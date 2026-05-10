from __future__ import annotations

from afos.core.logging import get_logger
from afos.core.settings import Settings

log = get_logger().bind(component="startup-validation")


def log_configuration_review(settings: Settings) -> None:
    """
    Non-blocking startup review: log misconfigurations that are risky in production.

    Does not raise — operators may intentionally run minimal configs locally.
    """
    if settings.env in ("staging", "prod"):
        if not settings.admin_reindex_token:
            log.warning(
                "admin_reindex_token_unset",
                message="ADMIN_REINDEX_TOKEN is empty; POST /v1/rag/rebuild will be disabled.",
            )
        if settings.resolved_llm_provider() == "openai" and not settings.openai_api_key:
            log.warning("openai_key_missing", message="OPENAI_API_KEY unset while LLM_PROVIDER implies OpenAI.")
        if settings.resolved_llm_provider() == "gemini" and not settings.gemini_api_key:
            log.warning("gemini_key_missing", message="GEMINI_API_KEY unset while LLM_PROVIDER implies Gemini.")

    has_llm = bool(settings.resolved_llm_api_key())
    db_scheme = ""
    if settings.database_url and "://" in settings.database_url:
        db_scheme = settings.database_url.split("://", 1)[0]

    log.info(
        "configuration_snapshot",
        env=settings.env,
        llm_provider=settings.resolved_llm_provider(),
        llm_configured=has_llm,
        llm_auto_failover=settings.llm_auto_failover,
        demo_soft_fallback=bool(settings.llm_rate_limit_fallback_reply),
        embedding_provider=settings.embedding_provider,
        database_scheme=db_scheme,
        dual_llm_ready=bool(settings.openai_api_key and settings.gemini_api_key),
    )
