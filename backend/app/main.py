"""Script9 Engine — FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.api.v1.router import webhook_router
from app.config import settings
from app.database import engine
from app.models import Base


from collections.abc import AsyncGenerator

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Intenta crear tablas al iniciar. No falla si la DB no está disponible."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"[WARN] No se pudo conectar a la base de datos: {e}")
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

app.include_router(v1_router)
app.include_router(webhook_router)
