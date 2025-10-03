# app/core/middleware.py
from __future__ import annotations

import uuid
from typing import Awaitable, Callable
from fastapi import Request, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.cors import get_allowed_origins  # <-- fix: kein "corse", kein "server."

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        req_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        request.state.request_id = req_id
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = req_id
        return response


def register_middlewares(app: FastAPI) -> None:
    # 1) Request-ID immer zuerst (damit alle späteren Logs die ID haben)
    app.add_middleware(RequestIdMiddleware)

    # 2) CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_allowed_origins(),
        allow_credentials=True,
        allow_methods=["*"],     # oder explizit: ["GET","POST","PUT","PATCH","DELETE","OPTIONS"]
        allow_headers=["*"],
        expose_headers=[REQUEST_ID_HEADER],  # damit der Client die Request-ID lesen darf
        max_age=600,             # optional: Cache für Preflight (in Sekunden)
    )
