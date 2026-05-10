from __future__ import annotations


class LLMProviderError(Exception):
    """Upstream LLM failure after retries."""


class LLMRateLimitError(LLMProviderError):
    """Quota or rate limit exhausted (Gemini / OpenAI)."""

    def __init__(self, message: str, *, retry_after_seconds: float | None = None):
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds
