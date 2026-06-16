"""Script9 Engine — FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import router as v1_router
from app.api.v1.router import webhook_router
from app.config import settings
from app.database import engine
from app.middleware.request_id import RequestIDMiddleware
from app.services.logging_service import configure_logging
from app.services.rate_limit import limiter, rate_limit_exceeded_handler

configure_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager — Alembic handles migrations; no create_all here."""
    yield
    await engine.dispose()


app = FastAPI(
    title="Script9 Engine API",
    version="0.1.0",
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost",  # Docker nginx
        "http://localhost:80",  # Docker nginx (explicit)
        "https://script9-engine.web.app",
        "https://script9-engine.firebaseapp.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestIDMiddleware)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.include_router(v1_router)
app.include_router(webhook_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return JSON error response with request_id for all unhandled exceptions."""
    import structlog

    request_id = getattr(request.state, "request_id", "unknown")
    logger.error("unhandled_exception", request_id=request_id, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "request_id": request_id},
    )
