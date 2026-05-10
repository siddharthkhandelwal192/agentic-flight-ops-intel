"""Provider-agnostic LLM chat completion (OpenAI + native Gemini)."""

from afos.llm.service import (
    LLMProviderError,
    LLMRateLimitError,
    CompleteChatOutcome,
    complete_chat_messages,
)

__all__ = [
    "LLMProviderError",
    "LLMRateLimitError",
    "CompleteChatOutcome",
    "complete_chat_messages",
]
