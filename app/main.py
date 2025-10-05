from __future__ import annotations

from fastapi import FastAPI
from app.core.logging import setup_logging
from app.core.handlers import register_exception_handlers
from app.routes import api_router
from app.config import API_TITLE, API_DESCRIPTION, API_VERSION
from app.core.middleware import register_middlewares

# Logging initialisieren
setup_logging("INFO")                

# define app
app = FastAPI(title=API_TITLE, description=API_DESCRIPTION, version=API_VERSION)

# register middleware
register_middlewares(app)

# register routes
app.include_router(api_router)

# register handlers
register_exception_handlers(app)