"""
Structured JSON logging configuration.

Uses structlog for machine-parseable log output.
PII is scrubbed before any log record is emitted.
"""

from __future__ import annotations

import logging
import re
import sys
from contextvars import ContextVar

import structlog

# Context variables for request-scoped metadata
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
tenant_id_ctx: ContextVar[str | None] = ContextVar("tenant_id", default=None)
user_id_ctx: ContextVar[str | None] = ContextVar("user_id", default=None)

# Patterns that indicate PII — never allow these values through
_PII_KEYS = re.compile(
    r"(password|secret|token|authorization|cookie|"
    r"ssn|social_security|credit_card|card_number|"
    r"email|phone|address|date_of_birth)",
    re.IGNORECASE,
)

_PII_REPLACEMENT = "***REDACTED***"


def _scrub_pii(
    _logger: object,
    _method: str,
    event_dict: dict,
) -> dict:
    """Remove PII values from log event dictionaries."""
    for key in list(event_dict.keys()):
        if _PII_KEYS.search(str(key)):
            event_dict[key] = _PII_REPLACEMENT
    return event_dict


def _inject_context(
    _logger: object,
    _method: str,
    event_dict: dict,
) -> dict:
    """Inject request-scoped context into every log line."""
    ctx_request_id = request_id_ctx.get()
    ctx_tenant_id = tenant_id_ctx.get()
    ctx_user_id = user_id_ctx.get()

    if ctx_request_id:
        event_dict["request_id"] = ctx_request_id
    if ctx_tenant_id:
        event_dict["tenant_id"] = ctx_tenant_id
    if ctx_user_id:
        event_dict["user_id"] = ctx_user_id

    return event_dict


def configure_logging(log_level: str = "INFO") -> None:
    """Wire up structlog with JSON rendering and PII scrubbing."""

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            _inject_context,
            _scrub_pii,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Mirror structlog level to stdlib so filter_by_level works
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(numeric_level)

    # Single stream handler — JSON goes to stdout for container capture
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)
    root.handlers = [handler]


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a named, bound structlog logger."""
    return structlog.get_logger(name)
