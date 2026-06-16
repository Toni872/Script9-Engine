"""Tests for request_id middleware — header uniqueness and context propagation."""

from unittest.mock import MagicMock
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.middleware.request_id import RequestIDMiddleware


class TestRequestIDMiddleware:
    """Verify X-Request-ID header is added to every response."""

    @pytest.mark.asyncio
    async def test_response_has_request_id_header(self) -> None:
        """Every response should include X-Request-ID with a valid UUID."""
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/test")

        assert "X-Request-ID" in response.headers
        # Should be a valid UUID
        request_id = response.headers["X-Request-ID"]
        UUID(request_id)  # Raises if not valid UUID

    @pytest.mark.asyncio
    async def test_request_ids_are_unique(self) -> None:
        """Each request should get a different UUID."""
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response1 = await client.get("/test")
            response2 = await client.get("/test")
            response3 = await client.get("/test")

        id1 = response1.headers["X-Request-ID"]
        id2 = response2.headers["X-Request-ID"]
        id3 = response3.headers["X-Request-ID"]

        assert id1 != id2
        assert id2 != id3
        assert id1 != id3

    @pytest.mark.asyncio
    async def test_request_id_stored_in_state(self) -> None:
        """The request_id should be accessible in request.state."""
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)
        captured_request_id: dict[str, str] = {}

        @app.get("/test")
        async def test_endpoint(request: MagicMock):
            captured_request_id["id"] = request.state.request_id
            return {"status": "ok"}

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/test")

        assert captured_request_id["id"] == response.headers["X-Request-ID"]
