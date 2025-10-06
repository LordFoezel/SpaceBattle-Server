from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.models.users import User, UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User
