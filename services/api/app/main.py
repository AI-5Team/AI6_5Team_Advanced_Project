from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import get_settings
from app.core.database import initialize_database
from app.services.runtime import ensure_demo_state


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    ensure_demo_state()
    yield


app = FastAPI(
    title="AI6_5Team Advanced Project API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

get_settings().storage_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=get_settings().storage_dir), name="media")


@app.exception_handler(HTTPException)
async def handle_http_exception(_: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": str(exc.detail), "message": str(exc.detail)}},
    )


@app.exception_handler(Exception)
async def handle_exception(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": str(exc)}},
    )

app.include_router(router)
