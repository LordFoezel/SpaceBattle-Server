from fastapi import APIRouter

# importiere alle Router
from app.routes.database import router as database_router
from app.routes.system import router as system_router
from app.routes.health import router as health_router
from app.routes.users import router as users_router

api_router = APIRouter()
api_router.include_router(database_router)
api_router.include_router(system_router)
api_router.include_router(health_router)
api_router.include_router(users_router)