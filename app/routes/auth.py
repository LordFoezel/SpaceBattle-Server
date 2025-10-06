from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from psycopg import errors

from app.core.auth import create_access_token
from app.core.security import verify_password
from app.models.auth import LoginRequest, RegisterRequest, TokenResponse
from app.models.users import UserRole
from app.repositories import users as users_repo

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, responses={401: {"description": "Invalid credentials"}})
def login(payload: LoginRequest) -> TokenResponse:
    credentials = users_repo.get_credentials_by_email(payload.email)
    if not credentials or not verify_password(payload.password, credentials.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(subject=credentials.user.id, role=credentials.user.role)
    return TokenResponse(access_token=token, user=credentials.user)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User registered successfully"},
        409: {"description": "Email already registered"},
    },
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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from exc

    token = create_access_token(subject=user.id, role=user.role)
    return TokenResponse(access_token=token, user=user)
