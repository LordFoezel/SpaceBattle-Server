from __future__ import annotations

from fastapi import APIRouter, Response, Request, Depends

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.openapi import with_errors
from app.core.errors import AppHttpStatus
from app.models.users import User, UserCreate, UserUpdate
from app.repositories import users as repo
from app.core.auth import get_current_user_role
from app.util.security import check_role_route, require_roles
from app.routes.crud_helpers import (
    make_list_route,
    make_get_route,
    make_create_route,
    make_update_route,
    make_delete_route,
)

router = APIRouter(prefix="/users", tags=["users"])


allowed_filters = {
    "id": int,
    "name": str,
    "email": str,
    "role": str,
    "verified": bool,
    "blocked": bool,
}

allowed_order_cols = {"id", "name", "email", "created_at", "role", "verified", "blocked"}

list_users_handler = make_list_route(
    repo.list_users,
    allowed_filters=allowed_filters,
    allowed_order_cols=allowed_order_cols,
)

@router.get("/", response_model=list[User], responses=with_errors())
def list_users(
    request: Request,
    limit: int | None = None,
    offset: int | None = None,
    order_by: str | None = None,
) -> list[User]:
    return list_users_handler(request, limit, offset, order_by)


get_user_handler = make_get_route(repo.get_by_id)

@router.get("/{user_id}", response_model=User, responses=with_errors())
def get_user(user_id: int) -> User:
    return get_user_handler(user_id)


create_user_handler = make_create_route(repo.create, UserCreate)

@router.post("/", response_model=User, status_code=AppHttpStatus.CREATED, responses=with_errors())
def create_user(payload: UserCreate) -> User:
    return create_user_handler(payload)


update_user_handler = make_update_route(repo.update, UserUpdate)

@router.patch("/{user_id}", response_model=User, responses=with_errors())
def update_user(user_id: int, payload: UserUpdate) -> User:
    return update_user_handler(user_id, payload)


delete_user_handler = make_delete_route(repo.delete)

@router.delete("/{user_id}", status_code=AppHttpStatus.NO_CONTENT, response_class=Response, responses=with_errors(exclude=[204]),  dependencies=[Depends(require_roles("admin"))])
def delete_user(user_id: int) -> Response:
    return delete_user_handler(user_id)
