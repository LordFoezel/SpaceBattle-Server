from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterable, Iterator

import psycopg
from psycopg.rows import dict_row

from app.databaseConnector import get_connector


class Db:
    """Thin convenience wrapper around psycopg with pooling helpers."""

    @contextmanager
    def _conn(self) -> Iterator[psycopg.Connection]:
        with get_connector().connection() as conn:
            yield conn

    @contextmanager
    def transaction(self) -> Iterator[psycopg.Connection]:
        """Provide an explicit transaction while autocommit is on in the pool."""
        with self._conn() as conn:
            with conn.transaction():
                yield conn

    def fetch_all(self, sql: str, params: Iterable[Any] | None = None) -> list[dict]:
        with self._conn() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params or [])
            return list(cur.fetchall())

    def fetch_one(self, sql: str, params: Iterable[Any] | None = None) -> dict | None:
        with self._conn() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params or [])
            return cur.fetchone()

    def execute(self, sql: str, params: Iterable[Any] | None = None) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(sql, params or [])
            return cur.rowcount

    def executemany(self, sql: str, seq_params: Iterable[Iterable[Any]]) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.executemany(sql, seq_params)
            return cur.rowcount


db = Db()


def build_insert(table: str, data: dict[str, Any], returning: str | None = None) -> tuple[str, list[Any]]:
    cols = list(data.keys())
    vals = list(data.values())
    placeholders = ", ".join(["%s"] * len(cols))
    sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
    if returning:
        sql += f" RETURNING {returning}"
    return sql, vals


def build_update(table: str, data: dict[str, Any], where: dict[str, Any]) -> tuple[str, list[Any]]:
    set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
    where_clause = " AND ".join([f"{k} = %s" for k in where.keys()])
    params = list(data.values()) + list(where.values())
    sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    return sql, params


def build_delete(table: str, where: dict[str, Any]) -> tuple[str, list[Any]]:
    where_clause = " AND ".join([f"{k} = %s" for k in where.keys()])
    params = list(where.values())
    sql = f"DELETE FROM {table} WHERE {where_clause}"
    return sql, params


def build_select(
    table: str,
    columns: list[str] | str = "*",
    where: dict[str, Any] | None = None,
    order_by: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> tuple[str, list[Any]]:
    cols = columns if isinstance(columns, str) else ", ".join(columns)
    sql = f"SELECT {cols} FROM {table}"
    params: list[Any] = []
    if where:
        sql += " WHERE " + " AND ".join([f"{k} = %s" for k in where.keys()])
        params.extend(where.values())
    if order_by:
        sql += f" ORDER BY {order_by}"
    if limit is not None:
        sql += " LIMIT %s"
        params.append(limit)
    if offset is not None:
        sql += " OFFSET %s"
        params.append(offset)
    return sql, params
