import os
import re
from typing import List, Set

DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

_ENV_KEYS = (
    "CORS_ALLOWED_ORIGINS",
    "FRONTEND_URL",
)


def _split_origins(raw: str) -> List[str]:
    """Split comma or whitespace separated values into clean origins."""
    tokens = re.split(r"[\s,]+", raw.strip())
    return [token for token in tokens if token]


def get_allowed_origins() -> List[str]:
    """Collect CORS origins from environment variables or fall back to defaults."""
    configured: List[str] = []
    for key in _ENV_KEYS:
        raw = os.getenv(key)
        if raw:
            configured.extend(_split_origins(raw))

    if not configured:
        configured.extend(DEFAULT_ALLOWED_ORIGINS)

    seen: Set[str] = set()
    unique: List[str] = []
    for origin in configured:
        if origin not in seen:
            seen.add(origin)
            unique.append(origin)

    return unique
