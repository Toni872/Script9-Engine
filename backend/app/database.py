"""Configuración de la base de datos asíncrona con SQLAlchemy."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos SQLAlchemy."""

    pass


engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia FastAPI para obtener sesión de BD."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
