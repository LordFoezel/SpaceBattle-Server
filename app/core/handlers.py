# app/core/handlers.py
from fastapi import FastAPI
from app.core.exceptions import AppError
from app.core.errors import ErrorResponse
from starlette.responses import JSONResponse

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_, exc: AppError):
        # baue ein typisiertes ErrorResponse – landet sauber in den Responses
        payload = ErrorResponse(code=exc.code, message=str(exc), details=exc.details)
        return JSONResponse(status_code=int(exc.status), content=payload.model_dump())