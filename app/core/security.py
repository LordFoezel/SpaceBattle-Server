from __future__ import annotations

import bcrypt


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
