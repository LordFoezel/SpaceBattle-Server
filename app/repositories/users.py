from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.models.users import User, UserCreate, UserRole, UserUpdate
from app.repositories.base import Repository
from app.database.core import db
from app.core.security import hash_password

TABLE = "users"


def _user_factory(payload: dict[str, Any]) -> User:
    return User(**payload)


def _prepare_user_update(patch: UserUpdate) -> dict[str, Any]:
    data = patch.model_dump(exclude_unset=True)
    return {key: (value.value if hasattr(value, "value") else value) for key, value in data.items()}


def _prepare_user_insert(payload: UserCreate) -> dict[str, Any]:
    data = payload.model_dump(exclude_unset=True)
    return {key: (value.value if hasattr(value, "value") else value) for key, value in data.items()}


_repo = Repository[User, UserUpdate, UserCreate](
    table=TABLE,
    model_factory=_user_factory,
    default_order_by="id ASC",
    prepare_update=_prepare_user_update,
    prepare_insert=_prepare_user_insert,
)


def get_by_id(user_id: int) -> User | None:
    return _repo.get_by_id(user_id)


def get_one(where: dict[str, Any]) -> User | None:
    return _repo.get_one(where=where)


def list_users(
    where: dict[str, Any] | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[User]:
    return _repo.list(offset=offset, limit=limit, where=where)


def create(payload: UserCreate) -> User:
    created = _repo.insert(payload, returning="*")
    if isinstance(created, User):
        return created
    if isinstance(created, dict):
        return _user_factory(created)
    raise RuntimeError("Repository returned no data for created user")


def update(user_id: int, patch: UserUpdate) -> User | None:
    return _repo.update(user_id, patch)


def delete(user_id: int) -> int:
    return _repo.delete(user_id)


def get_by_email(email: str) -> User | None:
    return get_one({"email": email})


@dataclass
class UserCredentials:
    user: User
    password_hash: str


def get_credentials_by_email(email: str) -> UserCredentials | None:
    row = db.fetch_one("SELECT * FROM users WHERE email = %s LIMIT 1", [email])
    if not row:
        return None

    password_hash = row.get("password_hash")
    user_payload = {k: v for k, v in row.items() if k != "password_hash"}
    user = _user_factory(user_payload)
    if not password_hash:
        return None
    return UserCredentials(user=user, password_hash=password_hash)


def create_with_password(*, name: str, email: str, password: str, role: UserRole = UserRole.player) -> User:
    payload = UserCreate(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=role,
    )
    return create(payload)
