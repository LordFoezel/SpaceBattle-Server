from fastapi import APIRouter, Depends
from app.util.security import require_roles

router = APIRouter()


@router.get("/health", summary="Container liveness check", dependencies=[Depends(require_roles("admin"))])
async def health() -> dict[str, str]:
    """Expose a lightweight endpoint useful for container health checks."""
    return {"status": "ok"}
