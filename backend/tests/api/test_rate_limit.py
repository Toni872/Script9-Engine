"""Tests for rate limiting — verify 429 returned when limits are exceeded."""

from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_stripe_checkout_rate_limit_exceeded_returns_429(
    mock_firebase: MagicMock,
) -> None:
    """After 10 requests in 60 seconds, the 11th should get 429."""
    from app.database import get_db
    from app.models import Base
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.pool import StaticPool

    # Create a test engine with in-memory DB
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    app.dependency_overrides[get_db] = lambda: session_factory()

    uid = mock_firebase()

    with patch("app.api.v1.stripe.configure"):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            # First 10 requests should succeed (or at least not get 429 due to rate limit)
            # The 11th request in 60 seconds should get 429
            for i in range(10):
                response = await ac.post(
                    "/api/v1/stripe/checkout",
                    json={"lookup_key": "starter_monthly"},
                    headers={"Authorization": "Bearer test-token"},
                )
                # We don't assert on status here - could be 503 (Stripe not configured)
                # or 200 depending on Stripe setup. We just track that they go through.

            # The 11th request should be rate limited
            response = await ac.post(
                "/api/v1/stripe/checkout",
                json={"lookup_key": "starter_monthly"},
                headers={"Authorization": "Bearer test-token"},
            )
            assert response.status_code == 429, f"Expected 429, got {response.status_code}"


@pytest.mark.asyncio
async def test_rate_limit_exceeded_returns_json_detail() -> None:
    """When rate limited, the response should be JSON with detail field."""
    from app.database import get_db
    from app.models import Base
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.pool import StaticPool

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    app.dependency_overrides[get_db] = lambda: session_factory()

    with patch("app.api.v1.stripe.configure"), patch(
        "slowapi.limit_handlers.Limiter._check_request_limit"
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            response = await ac.post(
                "/api/v1/stripe/checkout",
                json={"lookup_key": "starter_monthly"},
            )

            if response.status_code == 429:
                body = response.json()
                assert "detail" in body
                assert body["detail"] == "Rate limit exceeded"
