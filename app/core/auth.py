from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, ValidationError

from app.models.users import User, UserRole
from app.repositories import users as users_repo

SECRET = os.getenv("JWT_SECRET", "dev-only-change-me")
ALGO = "HS256"
ACCESS_MIN = int(os.getenv("JWT_ACCESS_MIN", "15"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class TokenPayload(BaseModel):
    """Typed representation of the JWT payload used by the API."""

    sub: int
    role: UserRole
    iat: int
    exp: int


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGO])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


def verify_token(token: str) -> TokenPayload:
    """Decode a JWT and validate it against the expected payload schema."""

    raw = _decode_token(token)
    try:
        return TokenPayload.model_validate(raw)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed authentication token",
        ) from exc


def create_access_token(*, subject: int, role: UserRole, minutes: int = ACCESS_MIN) -> str:
    """Create a signed JWT containing the user's id and role."""

    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role.value,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def get_current_token(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    return verify_token(token)


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = verify_token(token)
    return payload.sub


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = verify_token(token)
    user = users_repo.get_by_id(payload.sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
