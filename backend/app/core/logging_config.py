"""
Structured logging setup using structlog.

Configures both standard-library logging (for third-party libs) and
structlog-based structured logging for application code.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from app.core.config import get_settings

settings = get_settings()


def _drop_color_processor(
    _logger: Any, _method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Remove ANSI color codes from the event dict (useful for file output)."""
    for key in ("event",):
        value = event_dict.get(key)
        if isinstance(value, str):
            # Strip common ANSI escape sequences
            import re
            event_dict[key] = re.sub(r"\x1b\[[0-9;]*m", "", value)
    return event_dict


def setup_logging() -> None:
    """Configure structlog and stdlib logging for the application."""

    timestamper = structlog.processors.TimeStamper(fmt="iso")

    # Shared processors applied before renderer
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.APP_ENV == "production":
        # JSON output for log aggregation (ELK, Datadog, etc.)
        renderer = structlog.processors.JSONRenderer()
        processors = shared_processors + [_drop_color_processor, renderer]
        console_renderer = structlog.dev.ConsoleRenderer(colors=False)
    else:
        # Human-readable coloured console output
        renderer = structlog.dev.ConsoleRenderer(colors=True)
        processors = shared_processors + [renderer]
        console_renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard-library logging so third-party libraries play nicely
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Suppress noisy third-party loggers in non-DEBUG mode
    if log_level > logging.DEBUG:
        for noisy in (
            "httpx",
            "httpcore",
            "openai",
            "urllib3",
            "asyncio",
            "aiosqlite",
        ):
            logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger instance.

    Args:
        name: Logger name (usually __name__ of the calling module).

    Returns:
        A bound structlog logger.
    """
    return structlog.get_logger(name or __name__)
