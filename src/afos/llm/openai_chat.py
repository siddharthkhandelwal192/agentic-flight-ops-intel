from __future__ import annotations

import random
import time

from openai import OpenAI, OpenAIError

from afos.api.schemas.llm import ChatRoleMessage
from afos.core.logging import get_logger
from afos.llm.exceptions import LLMProviderError, LLMRateLimitError

log = get_logger().bind(component="llm-openai")


def _is_rate_limit_openai(exc: OpenAIError) -> bool:
    code = getattr(exc, "status_code", None)
    if code == 429:
        return True
    body = str(exc).lower()
    return "429" in body or "rate_limit" in body


def _backoff_seconds(attempt: int, base: float) -> float:
    return base * (2**attempt) + random.uniform(0, 0.35)


def generate_chat(
    *,
    api_key: str,
    base_url: str | None,
    model_name: str,
    messages: list[ChatRoleMessage],
    temperature: float,
    max_retries: int,
    request_timeout_seconds: float,
) -> tuple[str, str]:
    client = OpenAI(api_key=api_key, base_url=base_url)
    oa_msgs = [{"role": m.role, "content": m.content} for m in messages]
    last_exc: BaseException | None = None
    base_delay = 1.0
    for attempt in range(max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=oa_msgs,
                temperature=temperature,
                timeout=request_timeout_seconds,
            )
            choice = completion.choices[0].message.content or ""
            return choice.strip(), model_name
        except OpenAIError as exc:
            last_exc = exc
            if _is_rate_limit_openai(exc):
                log.warning(
                    "openai_rate_limited",
                    model=model_name,
                    attempt=attempt,
                    error_type=type(exc).__name__,
                )
                if attempt < max_retries:
                    time.sleep(_backoff_seconds(attempt, base_delay))
                    continue
                raise LLMRateLimitError(
                    "OpenAI rate limit exceeded after retries.",
                    retry_after_seconds=None,
                ) from exc
            log.error("openai_chat_failed", error_type=type(exc).__name__)
            raise LLMProviderError(str(exc)) from exc
    raise LLMProviderError(str(last_exc) if last_exc else "unknown")
