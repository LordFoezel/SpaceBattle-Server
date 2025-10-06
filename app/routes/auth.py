from __future__ import annotations

from fastapi import APIRouter
from psycopg import errors

from app.core.auth import create_access_token
from app.core.errors import AppHttpStatus
from app.core.exceptions import AlreadyExistsError, UnauthorizedError
from app.core.openapi import with_errors
from app.core.security import verify_password
from app.models.auth import LoginRequest, RegisterRequest, TokenResponse
from app.models.users import UserRole
from app.repositories import users as users_repo
import logging
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=AppHttpStatus.OK,
    responses=with_errors(),
)
def login(payload: LoginRequest) -> TokenResponse:
    
    logging.info("login", payload)
    user = users_repo.get_one(where={"email": payload.email})
    
    if not user or not verify_password(payload.password, user.password_hash):
        raise UnauthorizedError("Invalid credentials")

    token = create_access_token(subject=user.id, role=user.role)
    return TokenResponse(access_token=token, user=user)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=AppHttpStatus.CREATED,
    responses=with_errors(),
)
def register(payload: RegisterRequest) -> TokenResponse:
    try:
        user = users_repo.create_with_password(
            name=payload.name,
            email=payload.email,
            password=payload.password,
            role=payload.role or UserRole.player,
        )
    except errors.UniqueViolation as exc:
        raise AlreadyExistsError("Email already registered") from exc

    token = create_access_token(subject=user.id, role=user.role)
    return TokenResponse(access_token=token, user=user)
