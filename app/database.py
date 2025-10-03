from __future__ import annotations

import os
from contextlib import contextmanager
from queue import Empty, LifoQueue
from threading import Lock
from typing import Generator, Iterable

import psycopg

DATABASE_URL_ENV = "DATABASE_URL"
MIN_POOL_SIZE_ENV = "DATABASE_MIN_POOL_SIZE"
MAX_POOL_SIZE_ENV = "DATABASE_MAX_POOL_SIZE"
DEFAULT_MIN_POOL_SIZE = 1
DEFAULT_MAX_POOL_SIZE = 5


class DatabaseConfigurationError(RuntimeError):
    """Raised when the database connector is misconfigured."""


def _resolve_pool_size(value: int | None, env_var: str, default: int) -> int:
    """Resolve an explicit or environment-provided pool size."""
    if value is not None:
        return value

    raw_value = os.getenv(env_var)
    if raw_value is None or raw_value.strip() == "":
        return default

    try:
        parsed = int(raw_value)
    except ValueError as exc:
        raise DatabaseConfigurationError(
            f"Invalid value for {env_var}: expected an integer, got {raw_value!r}."
        ) from exc

    if parsed < 1:
        raise DatabaseConfigurationError(
            f"Invalid value for {env_var}: must be a positive integer."
        )

    return parsed


class _ConnectionPool:
    """Small LIFO connection pool to avoid requiring psycopg_pool."""

    def __init__(self, conninfo: str, *, min_size: int, max_size: int, autocommit: bool) -> None:
        if min_size < 1:
            raise DatabaseConfigurationError("Pool size must be at least 1")
        if max_size < min_size:
            raise DatabaseConfigurationError("Pool max_size must not be smaller than min_size")

        self._conninfo = conninfo
        self._autocommit = autocommit
        self._max_size = max_size
        self._pool: LifoQueue[psycopg.Connection] = LifoQueue(maxsize=max_size)
        self._lock = Lock()
        self._total_connections = 0

        for _ in range(min_size):
            self._pool.put(self._new_connection())
            self._total_connections += 1

    def _new_connection(self) -> psycopg.Connection:
        return psycopg.connect(self._conninfo, autocommit=self._autocommit)

    def _get_connection(self) -> psycopg.Connection:
        try:
            conn = self._pool.get_nowait()
        except Empty:
            with self._lock:
                if self._total_connections < self._max_size:
                    conn = self._new_connection()
                    self._total_connections += 1
                else:
                    conn = self._pool.get()

        if conn.closed:
            return self._new_connection()

        return conn

    def _return_connection(self, conn: psycopg.Connection) -> None:
        if conn.closed:
            with self._lock:
                self._total_connections = max(0, self._total_connections - 1)
            return

        try:
            self._pool.put_nowait(conn)
        except Exception:
            conn.close()

    @contextmanager
    def connection(self) -> Generator[psycopg.Connection, None, None]:
        conn = self._get_connection()
        try:
            yield conn
        finally:
            self._return_connection(conn)

    def close(self) -> None:
        while not self._pool.empty():
            conn = self._pool.get_nowait()
            conn.close()
        with self._lock:
            self._total_connections = 0


class DatabaseConnector:
    """Thin wrapper around a psycopg connection pool for PostgreSQL access."""

    def __init__(
        self,
        dsn: str | None = None,
        *,
        min_size: int | None = None,
        max_size: int | None = None,
    ) -> None:
        self._dsn = dsn or os.getenv(DATABASE_URL_ENV)
        if not self._dsn:
            raise DatabaseConfigurationError(
                "Database connection string missing. Set the DATABASE_URL environment variable."
            )

        resolved_min_size = _resolve_pool_size(
            min_size,
            MIN_POOL_SIZE_ENV,
            DEFAULT_MIN_POOL_SIZE,
        )
        resolved_max_size = _resolve_pool_size(
            max_size,
            MAX_POOL_SIZE_ENV,
            DEFAULT_MAX_POOL_SIZE,
        )

        if resolved_min_size > resolved_max_size:
            raise DatabaseConfigurationError(
                "Database pool misconfigured: min_size cannot be greater than max_size."
            )

        # LIFO pooling keeps hot connections ready without requiring psycopg_pool.
        self._pool = _ConnectionPool(
            self._dsn,
            min_size=resolved_min_size,
            max_size=resolved_max_size,
            autocommit=True,
        )

    def close(self) -> None:
        """Close the underlying connection pool."""
        self._pool.close()

    @contextmanager
    def connection(self) -> Generator[psycopg.Connection, None, None]:
        """Provide a pooled connection as a context manager."""
        with self._pool.connection() as conn:  # type: ignore[assignment]
            yield conn

    def iter_user_tables(self) -> Iterable[str]:
        """Yield user-defined tables in the database as fully-qualified names."""
        query = (
            "SELECT schemaname, tablename "
            "FROM pg_catalog.pg_tables "
            "WHERE schemaname NOT IN ('pg_catalog', 'information_schema') "
            "ORDER BY schemaname, tablename"
        )

        with self.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                for schemaname, tablename in cursor.fetchall():
                    if schemaname == "public":
                        yield tablename
                    else:
                        yield f"{schemaname}.{tablename}"


_connector: DatabaseConnector | None = None
_connector_lock = Lock()


def init_connector() -> DatabaseConnector:
    """Initialise the global connector if needed and return it."""
    global _connector

    if _connector is None:
        with _connector_lock:
            if _connector is None:
                _connector = DatabaseConnector()

    return _connector


def get_connector() -> DatabaseConnector:
    """Return the global connector, ensuring it has been initialised."""
    connector = _connector or init_connector()
    return connector


def shutdown_connector() -> None:
    """Tear down the connector if it exists."""
    global _connector

    if _connector is not None:
        _connector.close()
        _connector = None
