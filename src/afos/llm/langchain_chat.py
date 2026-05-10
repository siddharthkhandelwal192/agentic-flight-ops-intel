from __future__ import annotations

from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from afos.core.settings import Settings


def build_lc_chat_pair(settings: Settings) -> tuple[Any, Any]:
    """
    LangChain chat models for LangGraph (router + specialist share config).

    Gemini uses native Google GenAI integration (not OpenAI-compatible HTTP).
    """
    if settings.resolved_llm_provider() == "gemini":
        key = settings.gemini_api_key
        if not key:
            raise RuntimeError("No LLM key configured. Set GEMINI_API_KEY.")
        model = settings.gemini_model
        common = {
            "model": model,
            "google_api_key": key,
            "timeout": float(settings.llm_request_timeout_seconds),
            "max_retries": settings.llm_max_retries,
        }
        llm_router = ChatGoogleGenerativeAI(temperature=0, **common)
        specialist_llm = ChatGoogleGenerativeAI(temperature=0.1, **common)
        return llm_router, specialist_llm

    key = settings.openai_api_key
    if not key:
        raise RuntimeError("No LLM key configured. Set OPENAI_API_KEY.")
    common: dict[str, Any] = {
        "model": settings.openai_model,
        "openai_api_key": key,
        "timeout": settings.llm_request_timeout_seconds,
        "max_retries": settings.llm_max_retries,
    }
    if settings.openai_base_url:
        common["openai_api_base"] = settings.openai_base_url
    llm_router = ChatOpenAI(temperature=0, **common)
    specialist_llm = ChatOpenAI(temperature=0.1, **common)
    return llm_router, specialist_llm
