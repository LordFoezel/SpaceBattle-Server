from __future__ import annotations

import bcrypt

from app.util.token import extract_bearer_token
from fastapi import Request
from app.core.auth import get_current_user_role
from app.core.exceptions import ForbiddenError, UnauthorizedError

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    if not password:
        raise ValueError("Password must not be empty")
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    if not plain_password or not password_hash:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False

def check_role(request: Request, required: list[str]) -> bool:
    token = extract_bearer_token(request)
    if not token:
        return False
    role = get_current_user_role(token)
    if not role:
        return False
    if role in required: return True 
    return False

def check_role_route(request: Request, required: list[str]) -> None:
    token = extract_bearer_token(request)
    if not token:
        raise UnauthorizedError("Missing bearer token")
    role = get_current_user_role(token)
    if not role:
        raise ForbiddenError("Invalid or missing user role")
    if not role in required: 
        raise ForbiddenError("Insufficient permissions")


def require_roles(*roles: str):
    def dep(request: Request):
        token = extract_bearer_token(request)
        if not token:
            raise UnauthorizedError("Missing bearer token")
        role = get_current_user_role(token)  
        if not role or role not in roles:
            raise ForbiddenError("Insufficient permissions")     
    return dep
