
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.databaseConnector import shutdown_connector

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    # await init_cache()
    yield
    # --- shutdown ---
    shutdown_connector()
    # await close_cache()