import os
from typing import List

DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

def get_allowed_origins() -> List[str]:
    """Collect CORS origins from environment variables."""
    explicit_origins = [
        os.getenv("REACT_APP_API_BASE_URL"),
        os.getenv("FRONTEND_URL"),
        os.getenv("CORS_ALLOWED_ORIGINS"),
    ]
    origins: List[str] = [o for o in explicit_origins if o]

    if not origins:
        origins.extend(DEFAULT_ALLOWED_ORIGINS)

    expanded: List[str] = []
    for origin in origins:
        expanded.extend([value.strip() for value in origin.split(",") if value.strip()])

    seen, unique = set(), []
    for origin in expanded:
        if origin not in seen:
            seen.add(origin)
            unique.append(origin)

    return unique or DEFAULT_ALLOWED_ORIGINS
