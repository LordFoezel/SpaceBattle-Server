# app/models/users.py
from __future__ import annotations
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
    created_at: str  # oder datetime, falls du willst

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password_hash: str  # Hash kommt aus deiner App (bcrypt/argon2)
    role: UserRole = UserRole.player

class UserUpdate(BaseModel):
    name: str | None = None
    verified: bool | None = None
    blocked: bool | None = None
    role: UserRole | None = None
