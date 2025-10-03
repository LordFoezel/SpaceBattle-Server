from __future__ import annotations
from fastapi import APIRouter
from app.models.users import User, UserCreate, UserUpdate
from app.repositories import users as repo
from app.core.errors import AppHttpStatus
from app.core.exceptions import NotFoundError
from app.core.openapi import with_errors

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[User], responses=with_errors())
def list_users():
    return repo.list_users()


@router.get("/", response_model=list[User], responses=with_errors())
def get_user(user_id: int):
    u = repo.get_by_id(user_id)
    if not u:
        raise NotFoundError(f"User {user_id} not found")
    return u

@router.post("/", response_model=User, status_code=AppHttpStatus.CREATED, responses=with_errors())
def create_user(payload: UserCreate):
    u = repo.create(payload)
    return u

@router.patch("/{user_id}", response_model=User, responses=with_errors())
def update_user(user_id: int, payload: UserUpdate):
    u = repo.update(user_id, payload)
    if not u:
        raise NotFoundError(f"User {user_id} not found")
    return u

@router.delete("/{user_id}", status_code=AppHttpStatus.NO_CONTENT, responses=with_errors())
def delete_user(user_id: int):
    affected = repo.delete(user_id)
    if affected == 0:
        raise NotFoundError(f"User {user_id} not found")
