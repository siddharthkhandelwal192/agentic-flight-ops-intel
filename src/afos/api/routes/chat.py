from __future__ import annotations

from fastapi import APIRouter, HTTPException

from afos import __version__
from afos.api.routes.converters import openapi_messages_to_lc
from afos.api.schemas.llm import AgentInvokeRequest, AgentInvokeResponse, ChatCompletionRequest, ChatCompletionResponse
from afos.agents.graph import run_ops_graph
from afos.core.logging import get_logger
from afos.core.settings import get_settings
from afos.db.session import get_session_factory
from afos.llm import LLMProviderError, LLMRateLimitError, complete_chat_messages
from afos.llm.agent_errors import is_rate_limit_exception_chain

router = APIRouter(prefix="/llm", tags=["llm-chat"])
log = get_logger().bind(component="chat-routes")


def _rate_limit_http_exception(exc: LLMRateLimitError) -> HTTPException:
    headers: dict[str, str] = {}
    if exc.retry_after_seconds is not None:
        headers["Retry-After"] = str(max(1, int(exc.retry_after_seconds)))
    return HTTPException(
        status_code=429,
        detail="LLM rate limit or quota exceeded. Retry later or check Google AI / OpenAI quotas.",
        headers=headers,
    )


@router.post("/chat", response_model=ChatCompletionResponse)
def openai_compat_chat_completion(body: ChatCompletionRequest) -> ChatCompletionResponse:
    """Chat completion: OpenAI API or native Gemini (same JSON contract)."""

    s = get_settings()
    if not s.resolved_llm_api_key():
        raise HTTPException(
            status_code=503,
            detail="No LLM key configured. Set OPENAI_API_KEY or GEMINI_API_KEY.",
        )
    try:
        outcome = complete_chat_messages(body.messages, body.temperature, settings=s)
    except LLMRateLimitError as exc:
        log.warning(
            "llm_rate_limit",
            retry_after=exc.retry_after_seconds,
            provider=s.resolved_llm_provider(),
        )
        if s.llm_rate_limit_fallback_reply:
            return ChatCompletionResponse(
                reply=s.llm_rate_limit_fallback_reply.strip(),
                model=s.resolved_llm_model(),
                provider=s.resolved_llm_provider(),
            )
        raise _rate_limit_http_exception(exc) from exc
    except LLMProviderError as exc:
        log.warning("llm_provider_error", error=str(exc), provider=s.resolved_llm_provider())
        if s.llm_rate_limit_fallback_reply:
            return ChatCompletionResponse(
                reply=s.llm_rate_limit_fallback_reply.strip(),
                model=s.resolved_llm_model(),
                provider=s.resolved_llm_provider(),
            )
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatCompletionResponse(
        reply=outcome.reply,
        model=outcome.model,
        provider=outcome.provider,
        latency_ms=outcome.latency_ms,
        failover_used=outcome.failover_used,
    )


@router.post("/agents/operations", response_model=AgentInvokeResponse)
def airline_operations_supervisor_agent(body: AgentInvokeRequest) -> AgentInvokeResponse:
    """LangGraph supervisor → specialists (delay SQL tools + policy RAG + general OCC tone)."""

    s = get_settings()
    if not s.resolved_llm_api_key():
        raise HTTPException(
            status_code=503,
            detail="No LLM key configured. Set OPENAI_API_KEY or GEMINI_API_KEY.",
        )

    lc_messages = openapi_messages_to_lc(body.messages)
    SessionLocal = get_session_factory()
    db_session = SessionLocal()
    try:
        result = run_ops_graph(db_session, lc_messages)
    except LLMRateLimitError as exc:
        log.warning("ops_agent_rate_limit", retry_after=exc.retry_after_seconds)
        if s.llm_rate_limit_fallback_reply:
            return AgentInvokeResponse(
                intent=None,
                reply=s.llm_rate_limit_fallback_reply.strip(),
                model=s.resolved_llm_model(),
            )
        raise _rate_limit_http_exception(exc) from exc
    except LLMProviderError as exc:
        log.warning("ops_agent_provider_error", error=str(exc))
        if s.llm_rate_limit_fallback_reply:
            return AgentInvokeResponse(
                intent=None,
                reply=s.llm_rate_limit_fallback_reply.strip(),
                model=s.resolved_llm_model(),
            )
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except RuntimeError as exc:
        if s.llm_rate_limit_fallback_reply:
            log.warning("ops_agent_runtime_soft_fallback", error=str(exc))
            return AgentInvokeResponse(
                intent=None,
                reply=s.llm_rate_limit_fallback_reply.strip(),
                model=s.resolved_llm_model(),
            )
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        if is_rate_limit_exception_chain(exc):
            log.warning("ops_agent_rate_limit_chain", error_type=type(exc).__name__)
            if s.llm_rate_limit_fallback_reply:
                return AgentInvokeResponse(
                    intent=None,
                    reply=s.llm_rate_limit_fallback_reply.strip(),
                    model=s.resolved_llm_model(),
                )
            raise HTTPException(
                status_code=429,
                detail="LLM rate limit or quota exceeded during agent run.",
            ) from exc
        log.exception("ops_agent_failed", error_type=type(exc).__name__)
        raise HTTPException(status_code=502, detail="Agent execution failed.") from exc
    finally:
        db_session.close()

    return AgentInvokeResponse(
        intent=str(result["intent"]) if result.get("intent") is not None else None,
        reply=str(result["reply"]),
        model=s.resolved_llm_model(),
    )


@router.get("/version")
def llm_router_version():
    """Utility route for recruiter demos verifying deploy SHA / package version coupling."""

    s = get_settings()
    return {
        "api_version": __version__,
        "llm_provider": s.resolved_llm_provider(),
        "llm_model": s.resolved_llm_model(),
        "openapi_model_default": s.resolved_llm_model(),
    }
