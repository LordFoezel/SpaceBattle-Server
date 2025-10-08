from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
import psycopg

from app.database import DatabaseConfigurationError, get_connector
from server.app.util.security import require_roles

router = APIRouter(prefix="/database", tags=["database"])


async def _fetch_table_names() -> list[str]:
    connector = get_connector()

    def _collect() -> list[str]:
        return list(connector.iter_user_tables())

    return await run_in_threadpool(_collect)


@router.get("/tables", summary="List database tables", dependencies=[Depends(require_roles("admin"))])
async def list_tables() -> dict[str, list[str]]:
    try:
        tables = await _fetch_table_names()
    except (DatabaseConfigurationError, psycopg.Error) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"tables": tables}
