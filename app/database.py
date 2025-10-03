from __future__ import annotations

import os
from contextlib import contextmanager
from threading import Lock
from typing import Generator, Iterable

import psycopg
from psycopg_pool import ConnectionPool


class DatabaseConfigurationError(RuntimeError):
    pass


def _req(name: str) -> str:
    try:
        v = os.environ[name]
    except KeyError as exc:
        raise DatabaseConfigurationError(f"Missing required env var: {name}") from exc
    if not v.strip():
        raise DatabaseConfigurationError(f"Env var {name} must not be empty")
    return v


def _req_pos_int(name: str) -> int:
    raw = _req(name)
    try:
        val = int(raw)
    except ValueError as exc:
        raise DatabaseConfigurationError(f"{name} must be an integer, got {raw!r}") from exc
    if val < 1:
        raise DatabaseConfigurationError(f"{name} must be >= 1")
    return val


class DatabaseConnector:
    """Strict env-only config. Fails fast if anything is missing/wrong."""

    def __init__(self) -> None:
        dsn = _req("DATABASE_URL")
        min_size = _req_pos_int("DATABASE_MIN_POOL_SIZE")
        max_size = _req_pos_int("DATABASE_MAX_POOL_SIZE")
        if min_size > max_size:
            raise DatabaseConfigurationError("min_size cannot be greater than max_size")

        self._pool = ConnectionPool(
            conninfo=dsn,
            min_size=min_size,
            max_size=max_size,
            kwargs={"autocommit": True},
        )

    def close(self) -> None:
        self._pool.close()

    @contextmanager
    def connection(self) -> Generator[psycopg.Connection, None, None]:
        with self._pool.connection() as conn:  # type: ignore[assignment]
            yield conn

    def iter_user_tables(self) -> Iterable[str]:
        q = ("SELECT schemaname, tablename "
             "FROM pg_catalog.pg_tables "
             "WHERE schemaname NOT IN ('pg_catalog','information_schema') "
             "ORDER BY schemaname, tablename")
        with self.connection() as c, c.cursor() as cur:
            cur.execute(q)
            for s, t in cur.fetchall():
                yield t if s == "public" else f"{s}.{t}"


# Singleton – bleibt gleich:
_connector: DatabaseConnector | None = None
_lock = Lock()

def init_connector() -> DatabaseConnector:
    global _connector
    if _connector is None:
        with _lock:
            if _connector is None:
                _connector = DatabaseConnector()
    return _connector

def get_connector() -> DatabaseConnector:
    return _connector or init_connector()

def shutdown_connector() -> None:
    global _connector
    if _connector is not None:
        _connector.close()
        _connector = None
