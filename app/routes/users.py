from __future__ import annotations

from fastapi import APIRouter, Response

from app.core.exceptions import NotFoundError
from app.core.openapi import with_errors
from app.core.errors import AppHttpStatus
from app.models.users import User, UserCreate, UserUpdate
from app.repositories import users as repo

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[User], responses=with_errors())
def list_users() -> list[User]:
    return repo.list_users()


@router.get("/{user_id}", response_model=User, responses=with_errors())
def get_user(user_id: int) -> User:
    user = repo.get_by_id(user_id)
    if not user:
        raise NotFoundError(f"User {user_id} not found")
    return user


@router.post("/", response_model=User, status_code=AppHttpStatus.CREATED, responses=with_errors())
def create_user(payload: UserCreate) -> User:
    return repo.create(payload)


@router.patch("/{user_id}", response_model=User, responses=with_errors())
def update_user(user_id: int, payload: UserUpdate) -> User:
    user = repo.update(user_id, payload)
    if not user:
        raise NotFoundError(f"User {user_id} not found")
    return user


@router.delete("/{user_id}", status_code=AppHttpStatus.NO_CONTENT, response_class=Response, responses=with_errors(exclude=[204]))
def delete_user(user_id: int) -> Response:
    affected = repo.delete(user_id)
    if affected == 0:
        raise NotFoundError(f"User {user_id} not found")
    return Response(status_code=AppHttpStatus.NO_CONTENT)
