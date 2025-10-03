from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar

from app.db.core import db, build_delete, build_insert, build_select, build_update

ModelT = TypeVar("ModelT")
UpdateModelT = TypeVar("UpdateModelT")


class Repository(Generic[ModelT, UpdateModelT]):
    """Generic helper encapsulating common CRUD helpers for simple tables."""

    def __init__(
        self,
        table: str,
        model_factory: Callable[[dict[str, Any]], ModelT],
        *,
        default_order_by: str | None = None,
        prepare_update: Callable[[UpdateModelT], dict[str, Any]] | None = None,
    ) -> None:
        self._table = table
        self._to_model = model_factory
        self._default_order_by = default_order_by
        self._prepare_update = prepare_update or self._default_prepare_update

    def _default_prepare_update(self, patch: UpdateModelT) -> dict[str, Any]:
        if patch is None:
            return {}

        if hasattr(patch, "model_dump"):
            raw = patch.model_dump(exclude_unset=True)  # type: ignore[call-arg]
        elif isinstance(patch, dict):
            raw = {k: v for k, v in patch.items() if v is not None}
        else:
            raise TypeError("Unsupported patch payload for repository update")

        prepared: dict[str, Any] = {}
        for key, value in raw.items():
            prepared[key] = value.value if hasattr(value, "value") else value
        return prepared

    def _prepare_insert(self, payload: Any) -> dict[str, Any]:
        if payload is None:
            return {}

        if hasattr(payload, "model_dump"):
            raw = payload.model_dump(exclude_none=True)  # type: ignore[call-arg]
        elif isinstance(payload, dict):
            raw = {k: v for k, v in payload.items() if v is not None}
        else:
            raise TypeError("Unsupported payload for repository insert")

        prepared: dict[str, Any] = {}
        for key, value in raw.items():
            prepared[key] = value.value if hasattr(value, "value") else value
        return prepared

    def get_by_id(self, entity_id: int) -> ModelT | None:
        sql, params = build_select(self._table, where={"id": entity_id}, limit=1)
        row = db.fetch_one(sql, params)
        return self._to_model(row) if row else None

    def list(
        self,
        limit: int | None = None,
        offset: int | None = None,
        *,
        order_by: str | None = None,
        where: dict[str, Any] | None = None,
    ) -> list[ModelT]:
        sql, params = build_select(
            self._table,
            where=where,
            order_by=order_by or self._default_order_by,
            limit=limit,
            offset=offset,
        )
        rows = db.fetch_all(sql, params)
        return [self._to_model(row) for row in rows]

    def insert(self, payload: Any, *, returning: str | None = "id") -> ModelT | dict[str, Any] | None:
        data = self._prepare_insert(payload)
        if not data:
            raise ValueError("Insert payload resulted in no columns")

        sql, params = build_insert(self._table, data, returning=returning)
        if returning:
            row = db.fetch_one(sql, params)
            if not row:
                return None
            if returning.strip() == "*":
                return self._to_model(row)
            if "id" in row:
                entity = self.get_by_id(row["id"])
                return entity if entity is not None else row
            return row

        db.execute(sql, params)
        return None

    def update(self, entity_id: int, patch: UpdateModelT) -> ModelT | None:
        data = self._prepare_update(patch)
        if not data:
            return self.get_by_id(entity_id)

        sql, params = build_update(self._table, data, where={"id": entity_id})
        db.execute(sql, params)
        return self.get_by_id(entity_id)

    def delete(self, entity_id: int) -> int:
        sql, params = build_delete(self._table, where={"id": entity_id})
        return db.execute(sql, params)
