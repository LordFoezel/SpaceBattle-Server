from app.core.errors import ErrorResponse
from typing import Iterable, Mapping, Any

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

def with_errors(
    extra: Mapping[int, dict[str, Any]] | None = None,
    *,
    exclude: Iterable[int] = (),
) -> dict[int, dict[str, Any]]:
    """
    Kombiniert Standard-Error-Responses mit optionalen zusätzlichen.
    Falls `exclude` gesetzt ist, werden diese Statuscodes entfernt.
    """
    merged = dict(DEFAULT_ERROR_RESPONSES)

    if extra:
        merged.update(extra)

    for code in exclude:
        merged.pop(code, None)

    return merged