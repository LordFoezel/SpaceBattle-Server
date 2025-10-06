from __future__ import annotations

from fastapi import APIRouter
from psycopg import errors

from app.core.auth import create_access_token
from app.core.errors import AppHttpStatus
from app.core.exceptions import AlreadyExistsError, UnauthorizedError, UserNotValidatedError, UserBlockedError
from app.core.openapi import with_errors
from app.core.security import hash_password, verify_password
from app.models.auth import LoginRequest, RegisterRequest, TokenResponse, VerifyRequest
from app.models.users import UserCreate
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
    user = users_repo.get_one(where={"email": payload.email})
    if not user or not verify_password(payload.password, user.password_hash):
        raise UnauthorizedError("Invalid credentials")
    if not user.verified:
        raise UserNotValidatedError("User account is not verified")
    if user.blocked:
        raise UserBlockedError("User account is blocked")
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
        user = users_repo.create(UserCreate(
            name=payload.name,
            email=payload.email,
            password_hash=payload.password,
            # password_hash=hash_password(payload.password),
        ))
    except errors.UniqueViolation as exc:
        raise AlreadyExistsError("Email already registered") from exc

    token = create_access_token(subject=user.id, role=user.role)
    return TokenResponse(access_token=token, user=user)


@router.post(
    "/verify",
    response_model=TokenResponse,
    status_code=AppHttpStatus.OK,
    responses=with_errors(),
)
def register(payload: VerifyRequest) -> TokenResponse:
    try:
        user = users_repo.create_with_password(
            name=payload.id,
        )
    except errors.UniqueViolation as exc:
        raise AlreadyExistsError("Email already registered") from exc

    token = create_access_token(subject=user.id, role=user.role)
    return TokenResponse(access_token=token, user=user)
