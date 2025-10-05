from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    admin = "admin"
    player = "player"


class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    verified: bool
    blocked: bool
    role: UserRole
    created_at: datetime


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password_hash: str
    role: UserRole = UserRole.player


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password_hash: str | None = None
    verified: bool | None = None
    blocked: bool | None = None
    role: UserRole | None = None
