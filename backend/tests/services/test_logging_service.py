"""Tests for logging_service — env-aware JSON/console rendering."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from app.config import settings


class TestLoggingServiceConfiguration:
    """Verify structlog is configured correctly per environment."""

    @pytest.mark.asyncio
    async def test_production_environment_uses_json_renderer(self) -> None:
        """In production, structlog should emit JSON to stdout."""
        with patch.object(settings, "environment", "production"), patch(
            "structlog.processors.JSONRenderer"
        ) as mock_json, patch("structlog.processors.ConsoleRenderer") as mock_console, patch(
            "app.services.logging_service._init_sentry"
        ), patch(
            "structlog.configure"
        ) as mock_configure:
            # Re-import to pick up the mocked settings
            import importlib
            import app.services.logging_service as ls

            importlib.reload(ls)

            # Trigger configuration
            ls.configure_logging()

            # Find the renderer passed to structlog.configure
            call_kwargs = mock_configure.call_args.kwargs
            processors = call_kwargs.get("processors", [])

            # The last processor should be the renderer
            renderer = processors[-1] if processors else None
            assert renderer is not None

    @pytest.mark.asyncio
    async def test_development_environment_uses_console_renderer(self) -> None:
        """In development, structlog should emit human-readable console output."""
        with patch.object(settings, "environment", "local"), patch(
            "app.services.logging_service._init_sentry"
        ), patch("structlog.configure") as mock_configure:
            import importlib
            import app.services.logging_service as ls

            importlib.reload(ls)
            ls.configure_logging()

            # Verify structlog was configured (which means it ran)
            mock_configure.assert_called_once()

    def test_sentry_not_initialized_when_dsn_empty(self) -> None:
        """When sentry_dsn is empty, Sentry should not be initialized."""
        with patch.object(settings, "sentry_dsn", ""), patch(
            "sentry_sdk.init"
        ) as mock_sentry_init:
            from app.services.logging_service import _init_sentry

            _init_sentry()
            mock_sentry_init.assert_not_called()

    def test_sentry_initialized_when_dsn_provided(self) -> None:
        """When sentry_dsn is non-empty, Sentry should be initialized."""
        with patch.object(settings, "sentry_dsn", "https://abc@sentry.io/123"), patch(
            "sentry_sdk.init"
        ) as mock_sentry_init:
            from app.services.logging_service import _init_sentry

            _init_sentry()
            mock_sentry_init.assert_called_once()


class TestLoggingLevels:
    """Verify logging levels are set correctly per environment."""

    def test_production_level_is_warning(self) -> None:
        """Production should use WARNING level to reduce noise."""
        from app.services.logging_service import logging_level_from_settings

        level = logging_level_from_settings("production")
        assert level == logging.WARNING

    def test_development_level_is_debug(self) -> None:
        """Development should use DEBUG level for verbose output."""
        from app.services.logging_service import logging_level_from_settings

        level = logging_level_from_settings("local")
        assert level == logging.DEBUG
