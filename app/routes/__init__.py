"""Application API routers."""

from .routers import api_router
from .database import router as database_router
from .health import router as health_router
from .system import router as system_router
from .auth import router as auth_router
from .users import router as users_router
from .mailer import router as mailer_router

__all__ = [
    "api_router",
    "database_router",
    "health_router",
    "auth_router",
    "system_router",
    "users_router",
    "mailer_router",
]
