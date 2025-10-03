"""Application API routers."""

from .database import router as database_router
from .health import router as health_router
from .system import router as system_router
from .users import router as users_router

__all__ = ["database_router", "health_router", "system_router", "users_router"]
