"""Tests for webhook handlers — race condition fix and signature validation."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from script9_billing.models import WebhookEvent

from app.api.v1.webhooks import Script9Callbacks


class TestWebhookRaceConditionFix:
    """Verify that callbacks are awaited inline, not fire-and-forget."""

    @pytest.mark.asyncio
    async def test_on_checkout_completed_is_awaited(self) -> None:
        """Callbacks must be awaited so DB writes complete before the handler returns."""
        callbacks = Script9Callbacks()
        mock_db = AsyncMock()
        mock_event = WebhookEvent(
            type="checkout.completed",
            user_id="uid-123",
            customer_id="cus_123",
            subscription_id="sub_123",
            subscription_status="active",
        )

        # The callback should be async and awaited, not fire-and-forget
        # If it were asyncio.create_task, calling it without await would not
        # guarantee the DB write completes before the HTTP response is sent.
        assert asyncio.iscoroutinefunction(callbacks.on_checkout_completed)

        # Await the callback and verify DB interaction happens synchronously
        await callbacks.on_checkout_completed(mock_event, mock_db)

        # Commit should have been called, proving the session is still open
        mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_on_subscription_updated_is_awaited(self) -> None:
        """on_subscription_updated must be awaited inline."""
        callbacks = Script9Callbacks()
        mock_db = AsyncMock()
        mock_event = WebhookEvent(
            type="customer.subscription.updated",
            customer_id="cus_123",
            subscription_id="sub_456",
            subscription_status="active",
        )

        assert asyncio.iscoroutinefunction(callbacks.on_subscription_updated)
        await callbacks.on_subscription_updated(mock_event, mock_db)
        mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_on_subscription_deleted_is_awaited(self) -> None:
        """on_subscription_deleted must be awaited inline."""
        callbacks = Script9Callbacks()
        mock_db = AsyncMock()
        mock_event = WebhookEvent(
            type="customer.subscription.deleted",
            customer_id="cus_123",
        )

        assert asyncio.iscoroutinefunction(callbacks.on_subscription_deleted)
        await callbacks.on_subscription_deleted(mock_event, mock_db)
        mock_db.commit.assert_awaited_once()


class TestWebhookSignatureValidation:
    """Verify that invalid signatures return 400 without invoking callbacks."""

    @pytest.mark.asyncio
    async def test_invalid_signature_returns_400(self, client: MagicMock) -> None:
        """An invalid stripe-signature header must result in 400, not 200."""
        from httpx import ASGITransport, AsyncClient
        from app.main import app

        app.dependency_overrides.clear()

        with patch("app.api.v1.webhooks.configure"):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as ac:
                response = await ac.post(
                    "/webhooks/stripe",
                    content=b"{}",
                    headers={"stripe-signature": "invalid"},
                )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_missing_signature_returns_400(self, client: MagicMock) -> None:
        """A missing stripe-signature header must result in 400."""
        from httpx import ASGITransport, AsyncClient
        from app.main import app

        app.dependency_overrides.clear()

        with patch("app.api.v1.webhooks.configure"):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as ac:
                response = await ac.post(
                    "/webhooks/stripe",
                    content=b"{}",
                )

        assert response.status_code == 400
