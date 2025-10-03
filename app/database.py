from __future__ import annotations

import os
from contextlib import contextmanager
from threading import Lock
from typing import Generator, Iterable

import psycopg
from psycopg_pool import ConnectionPool

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

        # psycopg_pool manages connection lifecycle for us. autocommit ensures reads are immediate.
        self._pool = ConnectionPool(
            conninfo=self._dsn,
            min_size=resolved_min_size,
            max_size=resolved_max_size,
            kwargs={"autocommit": True},
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
