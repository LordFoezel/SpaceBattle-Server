from __future__ import annotations

import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

API_TITLE = "SpaceBattle API"
API_DESCRIPTION = "Backend services for the SpaceBattle application."
DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]


def _get_allowed_origins() -> List[str]:
    """Collect CORS origins from environment variables."""
    explicit_origins = [
        os.getenv("REACT_APP_API_BASE_URL"),
        os.getenv("FRONTEND_URL"),
        os.getenv("CORS_ALLOWED_ORIGINS"),
    ]

    origins: List[str] = [origin for origin in explicit_origins if origin]

    if not origins:
        origins.extend(DEFAULT_ALLOWED_ORIGINS)

    # If the env var includes comma-separated list, split it out.
    expanded: List[str] = []
    for origin in origins:
        expanded.extend([value.strip() for value in origin.split(",") if value.strip()])

    # Ensure duplicates are removed while preserving order.
    seen = set()
    unique_origins: List[str] = []
    for origin in expanded:
        if origin not in seen:
            seen.add(origin)
            unique_origins.append(origin)

    return unique_origins or DEFAULT_ALLOWED_ORIGINS


app = FastAPI(title=API_TITLE, description=API_DESCRIPTION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="SpaceBattle welcome message")
async def read_root() -> dict[str, str]:
    """Return a simple greeting to confirm the API is reachable."""
    return {"message": "Welcome to the SpaceBattle API"}


@app.get("/health", summary="Container liveness check")
async def health() -> dict[str, str]:
    """Expose a lightweight endpoint useful for container health checks."""
    return {"status": "ok"}
