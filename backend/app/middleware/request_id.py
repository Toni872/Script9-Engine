"""Request ID middleware that generates a UUID per request and attaches it to logs."""

import uuid
from typing import TYPE_CHECKING

from fastapi import BaseHTTPMiddleware, Request, Response

if TYPE_CHECKING:
    pass


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that injects a unique X-Request-ID header into every response.

    Generates a UUID for each incoming request, stores it in
    ``request.state.request_id`` for downstream access, and adds it
    to the response headers.
    """

    async def dispatch(self, request: Request, call_next: type) -> Response:  # type: ignore[type-arg]
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        import structlog

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
