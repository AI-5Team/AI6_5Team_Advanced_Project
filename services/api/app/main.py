from contextlib import asynccontextmanager
from urllib.parse import urlparse

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


_CSRF_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
# Paths called by external parties (webhooks, OAuth redirects) — exempt from CSRF check
_CSRF_EXEMPT_PREFIXES = ("/api/webhooks/",)


app = FastAPI(
    title="AI6_5Team Advanced Project API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def csrf_origin_check(request: Request, call_next):
    if request.method not in _CSRF_SAFE_METHODS:
        path = request.url.path
        if not any(path.startswith(prefix) for prefix in _CSRF_EXEMPT_PREFIXES):
            origin = request.headers.get("origin") or request.headers.get("referer")
            if origin:
                parsed = urlparse(origin)
                allowed_host = request.url.hostname or ""
                if parsed.hostname and parsed.hostname not in (allowed_host, "localhost", "127.0.0.1"):
                    return JSONResponse(
                        status_code=403,
                        content={"error": {"code": "CSRF_REJECTED", "message": "요청 출처가 허용되지 않습니다."}},
                    )
    return await call_next(request)


import os as _os
import re as _re

def _build_cors(env_val: str | None) -> dict:
    if env_val:
        return {"allow_origins": [o.strip() for o in env_val.split(",") if o.strip()]}
    # Dev default: allow any localhost/127.0.0.1 port
    return {"allow_origin_regex": r"https?://(localhost|127\.0\.0\.1)(:\d+)?$"}

_cors_kwargs = _build_cors(_os.getenv("APP_CORS_ORIGINS"))

app.add_middleware(
    CORSMiddleware,
    **_cors_kwargs,
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
