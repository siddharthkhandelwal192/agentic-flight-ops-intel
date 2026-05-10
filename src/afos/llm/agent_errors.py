from __future__ import annotations

from google.api_core import exceptions as google_exceptions


def is_rate_limit_exception(exc: BaseException) -> bool:
    """Best-effort detection for quota / 429 style failures from agents."""
    if isinstance(exc, google_exceptions.ResourceExhausted):
        return True
    msg = str(exc).lower()
    name = type(exc).__name__.lower()
    return (
        "429" in msg
        or "resource_exhausted" in msg
        or "quota" in msg
        or ("rate" in name and "limit" in name)
    )


def is_rate_limit_exception_chain(exc: BaseException) -> bool:
    cur: BaseException | None = exc
    seen: set[int] = set()
    while cur is not None and id(cur) not in seen:
        seen.add(id(cur))
        if is_rate_limit_exception(cur):
            return True
        cur = cur.__cause__ or cur.__context__
    return False
