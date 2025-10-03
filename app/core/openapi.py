# app/core/openapi.py
from app.core.errors import ErrorResponse
from typing import Mapping, Any

# Standard-Fehler, die viele Endpoints teilen
DEFAULT_ERROR_RESPONSES: Mapping[int, dict[str, Any]] = {
    400: {"model": ErrorResponse},
    401: {"model": ErrorResponse},
    403: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    409: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
    500: {"model": ErrorResponse},
}

def with_errors(extra: Mapping[int, dict[str, Any]] | None = None) -> dict[int, dict[str, Any]]:
    """Mische Standard-Fehler mit route-spezifischen (z. B. 201 hat eh keinen Body)."""
    merged = dict(DEFAULT_ERROR_RESPONSES)
    if extra:
        merged.update(extra)
    return merged
