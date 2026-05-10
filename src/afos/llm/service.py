from __future__ import annotations

import time
from typing import Literal

from afos.api.schemas.llm import ChatRoleMessage
from afos.core.logging import get_logger
from afos.core.settings import Settings, get_settings
from afos.llm import gemini_native, openai_chat
from afos.llm.exceptions import LLMProviderError, LLMRateLimitError

log = get_logger().bind(component="llm-service")

__all__ = ["LLMProviderError", "LLMRateLimitError", "complete_chat_messages", "CompleteChatOutcome"]


class CompleteChatOutcome:
    """Chat completion envelope (timing + resolved provider labels for `/v1/llm/chat`)."""

    __slots__ = ("reply", "model", "provider", "latency_ms", "failover_used")

    def __init__(
        self,
        reply: str,
        model: str,
        *,
        provider: Literal["openai", "gemini"],
        latency_ms: float,
        failover_used: bool = False,
    ) -> None:
        self.reply = reply
        self.model = model
        self.provider = provider
        self.latency_ms = latency_ms
        self.failover_used = failover_used


def complete_chat_messages(
    messages: list[ChatRoleMessage],
    temperature: float,
    settings: Settings | None = None,
) -> CompleteChatOutcome:
    """
    Provider-agnostic chat completion via the configured primary provider (`LLM_PROVIDER` /
    resolved auto rule). Keeps demos predictable: single provider path — no secondary hop.
    LangGraph agents resolve their own LangChain pairs separately.
    """

    s = settings or get_settings()
    if not messages:
        raise LLMProviderError("messages must not be empty")

    primary: Literal["openai", "gemini"] = s.resolved_llm_provider()

    started = time.perf_counter()

    if primary == "openai":
        key = s.openai_api_key
        if not key:
            raise LLMProviderError("OPENAI_API_KEY is not configured.")
        reply, model = openai_chat.generate_chat(
            api_key=key,
            base_url=s.openai_base_url,
            model_name=s.openai_model,
            messages=messages,
            temperature=temperature,
            max_retries=s.llm_max_retries,
            request_timeout_seconds=s.llm_request_timeout_seconds,
        )
    else:
        key = s.gemini_api_key
        if not key:
            raise LLMProviderError("GEMINI_API_KEY is not configured.")
        reply, model = gemini_native.generate_chat(
            api_key=key,
            model_name=s.gemini_model,
            messages=messages,
            temperature=temperature,
            max_retries=s.llm_max_retries,
            request_timeout_seconds=s.llm_request_timeout_seconds,
            fallback_model=s.gemini_fallback_model,
        )

    elapsed_ms = round((time.perf_counter() - started) * 1000.0, 2)
    log.info(
        "llm_chat_completed",
        provider=primary,
        model=model,
        latency_ms=elapsed_ms,
    )
    return CompleteChatOutcome(reply, model, provider=primary, latency_ms=elapsed_ms, failover_used=False)
