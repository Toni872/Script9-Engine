"""Fixtures compartidas para los tests de Script9 Engine."""

from collections.abc import AsyncGenerator
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.models import Base

# Base de datos en memoria para tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def engine_test():  # type: ignore[misc]
    """Motor SQLite async para la sesión de tests."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine_test) -> AsyncGenerator[AsyncSession, None]:  # type: ignore[misc]
    """Sesión de BD aislada por test (rollback al finalizar)."""
    session_factory = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:  # type: ignore[misc]
    """Cliente HTTP con BD de test inyectada."""
    from app.main import app

    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def mock_firebase() -> MagicMock:
    """Mock de firebase_admin.auth.verify_id_token."""
    with patch("app.api.v1.auth.firebase_auth.verify_id_token") as mock_verify:
        mock_verify.return_value = {
            "uid": "test-firebase-uid-123",
            "email": "test@example.com",
            "name": "Test User",
        }
        yield mock_verify
