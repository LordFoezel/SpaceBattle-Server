from __future__ import annotations

from typing import Any

from app.db.core import db, build_insert, build_select
from app.models.users import User, UserCreate, UserUpdate
from app.repositories.base import Repository

TABLE = "users"


def _user_factory(payload: dict[str, Any]) -> User:
    return User(**payload)


def _prepare_user_update(patch: UserUpdate) -> dict[str, Any]:
    data = patch.model_dump(exclude_unset=True)
    return {key: (value.value if hasattr(value, "value") else value) for key, value in data.items()}


_repo = Repository[User, UserUpdate](
    table=TABLE,
    model_factory=_user_factory,
    default_order_by="id ASC",
    prepare_update=_prepare_user_update,
)


def get_by_id(user_id: int) -> User | None:
    return _repo.get_by_id(user_id)


def get_by_email(email: str) -> User | None:
    sql, params = build_select(TABLE, where={"email": email}, limit=1)
    row = db.fetch_one(sql, params)
    return User(**row) if row else None


def list_users(
    where: dict[str, Any] | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[User]:
    return _repo.list(offset=offset, limit=limit, where=where)


def create(u: UserCreate) -> User:
    return _repo.insert(u)


def update(user_id: int, patch: UserUpdate) -> User | None:
    return _repo.update(user_id, patch)


def delete(user_id: int) -> int:
    return _repo.delete(user_id)
