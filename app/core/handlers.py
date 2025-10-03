# app/core/handlers.py
import logging
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from app.core.exceptions import AppError
from app.core.errors import ErrorResponse

logger = logging.getLogger("spacebattle.api")

def _build_context(request: Request, exc: AppError) -> dict:
    # alles, was beim Debug hilft – ohne Secrets!
    return {
        "request_id": getattr(request.state, "request_id", None),
        "path": request.url.path,
        "method": request.method,
        "status": int(exc.status),
        "code": str(exc.code),
    }

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        ctx = _build_context(request, exc)
        # 5xx laut loggen, 4xx eher informativ
        if int(exc.status) >= 500:
            logger.exception("Unhandled server error", extra=ctx)
        else:
            logger.info("Handled app error", extra=ctx)

        payload = ErrorResponse(code=exc.code, message=str(exc), details=exc.details)
        return JSONResponse(status_code=int(exc.status), content=payload.model_dump())
