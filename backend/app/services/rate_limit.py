"""Rate limiting via slowapi — IP-based limiter and decorator factory."""

from functools import wraps
from typing import Callable, TypeVar

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import Response

limiter = Limiter(key_func=get_remote_address)


def rate_limit(times: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
    """Decorator factory that applies a rate limit to a route handler.

    Usage::

        @router.post("/checkout")
        @limiter.limit("10/minute")  # from slowapi
        async def checkout(request: Request, ...):
            ...

    The decorator from slowapi returns a callable that wraps the endpoint.
    This factory exists to allow custom key_func injection later if needed.
    """
    return limiter.limit(times)


def rate_limit_exceeded_handler(request: Request, exc: Exception) -> Response:
    """Return JSON 429 when rate limit is exceeded."""
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
