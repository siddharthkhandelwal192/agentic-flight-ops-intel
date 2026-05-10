from __future__ import annotations

import logging
import sys
from typing import Any

import structlog


def _timestamper(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    # ISO8601 UTC timestamps are easy to grep and consistent across systems.
    event_dict.setdefault("ts", structlog.processors.TimeStamper(fmt="iso", utc=True)({}, "", {}))
    return event_dict


def configure_logging(*, level: str) -> None:
    """
    Configure stdlib logging + structlog for JSON-ish structured logs.

    Why this matters:
    - In production, logs are your primary debugging tool.
    - Structured logs are machine-queryable (Datadog/Splunk/CloudWatch).
    """
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level.upper())
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    root.addHandler(handler)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            _timestamper,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level.upper(), logging.INFO)),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger() -> structlog.stdlib.BoundLogger:
    return structlog.get_logger()

