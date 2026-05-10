from __future__ import annotations

import random
import time
import warnings
from typing import Any

with warnings.catch_warnings():
    warnings.simplefilter("ignore", FutureWarning)
    import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from afos.api.schemas.llm import ChatRoleMessage
from afos.core.logging import get_logger
from afos.llm.exceptions import LLMProviderError, LLMRateLimitError

log = get_logger().bind(component="llm-gemini-native")


def _split_system_and_contents(
    messages: list[ChatRoleMessage],
) -> tuple[str | None, list[dict[str, Any]]]:
    system_chunks: list[str] = []
    contents: list[dict] = []
    for m in messages:
        if m.role == "system":
            system_chunks.append(m.content)
        elif m.role == "user":
            contents.append({"role": "user", "parts": [m.content]})
        elif m.role == "assistant":
            contents.append({"role": "model", "parts": [m.content]})
    system_instruction = "\n\n".join(system_chunks).strip() or None
    return system_instruction, contents


def _extract_text(response: Any) -> str:
    direct = getattr(response, "text", None)
    if direct:
        return str(direct).strip()
    if not response.candidates:
        return ""
    parts: list[str] = []
    for cand in response.candidates:
        if not cand.content or not cand.content.parts:
            continue
        for p in cand.content.parts:
            if hasattr(p, "text") and p.text:
                parts.append(p.text)
    return "".join(parts).strip()


def _is_rate_limit(exc: BaseException) -> bool:
    if isinstance(exc, google_exceptions.ResourceExhausted):
        return True
    msg = str(exc).lower()
    return "429" in msg or "resource_exhausted" in msg or "quota" in msg


def _backoff_seconds(attempt: int, base: float) -> float:
    return base * (2**attempt) + random.uniform(0, 0.35)


def generate_chat(
    *,
    api_key: str,
    model_name: str,
    messages: list[ChatRoleMessage],
    temperature: float,
    max_retries: int,
    request_timeout_seconds: float,
    fallback_model: str | None,
) -> tuple[str, str]:
    """
    Native Gemini generateContent. Returns (reply_text, model_used).

    Retries on rate limits with exponential backoff; optional fallback model.
    """
    genai.configure(api_key=api_key)
    system_instruction, contents = _split_system_and_contents(messages)
    if not contents:
        raise LLMProviderError("No user/assistant messages to send to Gemini.")

    def _run(model: str) -> str:
        last_err: BaseException | None = None
        base_delay = 1.0
        for attempt in range(max_retries + 1):
            try:
                model_obj = genai.GenerativeModel(
                    model,
                    system_instruction=system_instruction,
                )
                # Single-string path avoids empty multi-turn edge cases
                if len(contents) == 1 and contents[0]["role"] == "user":
                    prompt = contents[0]["parts"][0]
                    resp = model_obj.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=temperature,
                        ),
                        request_options={"timeout": request_timeout_seconds},
                    )
                else:
                    resp = model_obj.generate_content(
                        contents,
                        generation_config=genai.types.GenerationConfig(
                            temperature=temperature,
                        ),
                        request_options={"timeout": request_timeout_seconds},
                    )
                text = _extract_text(resp)
                if text:
                    return text
                if resp.prompt_feedback and resp.prompt_feedback.block_reason:
                    br = resp.prompt_feedback.block_reason
                    label = getattr(br, "name", str(br))
                    raise LLMProviderError(f"Content blocked: {label}")
                return ""
            except LLMProviderError:
                raise
            except Exception as exc:  # noqa: BLE001 — map provider errors
                last_err = exc
                if _is_rate_limit(exc):
                    log.warning(
                        "gemini_rate_limited",
                        model=model,
                        attempt=attempt,
                        error_type=type(exc).__name__,
                    )
                    if attempt < max_retries:
                        time.sleep(_backoff_seconds(attempt, base_delay))
                        continue
                    ra = getattr(exc, "retry_after", None)
                    retry_after = float(ra) if ra is not None else None
                    raise LLMRateLimitError(
                        "Gemini rate limit or quota exceeded after retries.",
                        retry_after_seconds=retry_after,
                    ) from exc
                log.error(
                    "gemini_generate_failed",
                    model=model,
                    error_type=type(exc).__name__,
                )
                raise LLMProviderError(str(exc)) from exc
        raise LLMProviderError(str(last_err) if last_err else "unknown")

    try:
        out = _run(model_name)
        return out, model_name
    except LLMRateLimitError:
        if fallback_model and fallback_model != model_name:
            log.info("gemini_trying_fallback_model", fallback=fallback_model)
            try:
                out = _run(fallback_model)
                return out, fallback_model
            except LLMRateLimitError:
                raise
        raise
