from fastapi import APIRouter


router = APIRouter(prefix="/system", tags=["system"])


@router.get("/", summary="SpaceBattle welcome message")
async def read_root() -> dict[str, str]:
    """Return a simple greeting to confirm the API is reachable."""
    return {"message": "Welcome to the SpaceBattle API"}
