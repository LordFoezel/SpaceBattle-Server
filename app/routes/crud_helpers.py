from __future__ import annotations

from typing import Any, Callable, Iterable, Mapping

from fastapi import Request, Response

from app.core.errors import AppHttpStatus
from app.core.exceptions import NotFoundError


def _parse_bool(raw: str) -> bool:
    return str(raw).strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def _coerce(raw: str, caster: Callable[[str], Any] | type | None, key: str) -> Any:
    if caster is None:
        # Heuristics: id -> int, booleans by name, else str
        if key.lower() in {"verified", "blocked", "active", "enabled"}:
            return _parse_bool(raw)
        if key.lower().endswith("_id") or key.lower() == "id":
            return int(raw)
        return raw

    if caster is bool:
        return _parse_bool(raw)
    if caster is int:
        return int(raw)
    if caster is float:
        return float(raw)
    if caster is str:
        return raw
    # custom callable/enum
    return caster(raw)  # type: ignore[misc]


def build_where_from_request(
    request: Request,
    allowed_filters: Iterable[str] | Mapping[str, Callable[[str], Any] | type],
) -> dict[str, Any]:
    qp = request.query_params
    parsers: Mapping[str, Callable[[str], Any] | type]
    if isinstance(allowed_filters, Mapping):
        parsers = allowed_filters
    else:
        parsers = {name: None for name in allowed_filters}  # type: ignore[assignment]

    where: dict[str, Any] = {}
    for key, caster in parsers.items():
        if key in qp:
            values = qp.getlist(key)
            if not values:
                continue
            raw = values[0]
            try:
                where[key] = _coerce(raw, caster, key)
            except Exception:
                # skip invalid value
                continue
    # Optional JSON "where" support: if present, merge but do not override explicit keys
    if "where" in qp:
        try:
            import json

            obj = json.loads(qp["where"])  # type: ignore[index]
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k not in where and k in parsers:
                        where[k] = v
        except Exception:
            pass

    return where


def sanitize_order_by(order_by: str | None, allowed_columns: Iterable[str]) -> str | None:
    if not order_by:
        return None
    allowed = set(allowed_columns)
    ob = order_by.strip()
    ob_lower = ob.lower()
    direction = None
    col = ob
    if ob_lower.endswith(" desc"):
        direction = "DESC"
        col = ob[:-5].strip()
    elif ob_lower.endswith(" asc"):
        direction = "ASC"
        col = ob[:-4].strip()
    if col in allowed:
        return f"{col} {direction}".strip() if direction else col
    return None


# Factories returning FastAPI handlers

def make_list_route(
    list_func: Callable[..., list[Any]],
    *,
    allowed_filters: Iterable[str] | Mapping[str, Callable[[str], Any] | type],
    allowed_order_cols: Iterable[str],
) -> Callable[[Request, int | None, int | None, str | None], list[Any]]:
    def route(
        request: Request,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> list[Any]:
        where = build_where_from_request(request, allowed_filters)
        ob = sanitize_order_by(order_by, allowed_order_cols)
        return list_func(where=where or None, limit=limit, offset=offset, order_by=ob)

    return route


def make_get_route(get_by_id_func: Callable[[int], Any]) -> Callable[[int], Any]:
    def route(entity_id: int) -> Any:
        entity = get_by_id_func(entity_id)
        if not entity:
            raise NotFoundError(f"Entity {entity_id} not found")
        return entity

    return route


def make_create_route(create_func: Callable[[Any], Any], model_create: type) -> Callable[[Any], Any]:
    def route(payload: model_create):  # type: ignore[valid-type]
        return create_func(payload)

    return route


def make_update_route(update_func: Callable[[int, Any], Any], model_update: type) -> Callable[[int, Any], Any]:
    def route(entity_id: int, payload: model_update):  # type: ignore[valid-type]
        entity = update_func(entity_id, payload)
        if not entity:
            raise NotFoundError(f"Entity {entity_id} not found")
        return entity

    return route


def make_delete_route(delete_func: Callable[[int], int]) -> Callable[[int], Response]:
    def route(entity_id: int) -> Response:
        affected = delete_func(entity_id)
        if affected == 0:
            raise NotFoundError(f"Entity {entity_id} not found")
        return Response(status_code=AppHttpStatus.NO_CONTENT)

    return route

