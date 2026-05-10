"""
Suppress or downgrade noisy third-party warnings that clutter production logs.

These are environment / upstream deprecation notices, not application bugs.
Call `configure_third_party_warnings()` once at process startup (before heavy imports if possible).
"""

from __future__ import annotations

import warnings


def configure_third_party_warnings() -> None:
    try:
        from langchain_core._api.deprecation import LangChainPendingDeprecationWarning
    except ImportError:
        LangChainPendingDeprecationWarning = DeprecationWarning  # type: ignore[misc, assignment]

    warnings.filterwarnings("ignore", category=LangChainPendingDeprecationWarning)
    try:
        from urllib3.exceptions import NotOpenSSLWarning

        warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
    except ImportError:
        warnings.filterwarnings(
            "ignore",
            message=r".*urllib3 v2 only supports OpenSSL.*",
        )
    # Google is migrating google.generativeai → google.genai; we still use the stable SDK path.
    warnings.filterwarnings(
        "ignore",
        message=r".*google\.generativeai.*",
        category=FutureWarning,
    )
    warnings.filterwarnings(
        "ignore",
        message=r".*All support for the `google\.generativeai` package has ended.*",
        category=FutureWarning,
    )
    warnings.filterwarnings(
        "ignore",
        message=r".*Python version 3\.9 past its end of life.*",
        category=FutureWarning,
    )
    warnings.filterwarnings(
        "ignore",
        message=r".*non-supported Python version \(3\.9.*google\.api_core.*",
        category=FutureWarning,
    )
