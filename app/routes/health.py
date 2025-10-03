from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Container liveness check")
async def health() -> dict[str, str]:
    """Expose a lightweight endpoint useful for container health checks."""
    return {"status": "ok"}
