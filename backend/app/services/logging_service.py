"""Centralized structured logging with structlog + optional Sentry."""

import structlog

from app.config import settings


def configure_logging() -> None:
    """Configure structlog and optionally initialize Sentry.

    In production (environment == "production"), logs are JSON-structured
    for ingestion by log aggregators. In development, a console renderer
    with colors is used for readability.

    Sentry is initialized only when settings.sentry_dsn is non-empty,
    preventing errors in local/dev environments without a DSN.
    """
    import structlog
    import sys

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
            _get_renderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging_level_from_settings(settings.environment),
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=False,
    )

    _init_sentry()


def _get_renderer():  # type: ignore[no-untyped-def]
    """Return JSON renderer for production, console renderer for development."""
    if settings.environment == "production":
        return structlog.processors.JSONRenderer()
    return structlog.dev.ConsoleRenderer()


def logging_level_from_settings(environment: str) -> int:
    """Map environment string to logging level.

    Production uses WARNING to reduce noise; development uses DEBUG.
    """
    import logging

    if environment == "production":
        return logging.WARNING
    return logging.DEBUG


def _init_sentry() -> None:
    """Conditionally initialize Sentry when DSN is configured."""
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    if not settings.sentry_dsn:
        return

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[
            FastApiIntegration(),
            StarletteIntegration(),
        ],
        environment=settings.environment,
        send_default_pii=False,
    )
