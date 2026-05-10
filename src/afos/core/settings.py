from __future__ import annotations

from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration for the service.

    In production, values come from environment variables.
    In local development, values may also come from a `.env` file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Service
    env: Literal["local", "dev", "staging", "prod"] = Field(default="local", validation_alias="ENV")
    service_name: str = Field(default="afois-api", validation_alias="SERVICE_NAME")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    # API
    api_host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    # Comma-separated browser origins for CORS (Next.js dev server, deployed UI, etc.).
    cors_allowed_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        validation_alias="CORS_ALLOWED_ORIGINS",
    )
    cors_allow_localhost_regex: bool = Field(
        default=True,
        validation_alias="CORS_ALLOW_LOCALHOST_REGEX",
        description="Allow any http(s) localhost / 127.0.0.1 port via regex (disable in strict prod).",
    )

    # Database (PostgreSQL in production; SQLite default for frictionless local dev/tests)
    database_url: str = Field(
        default="sqlite:///./data/afois_local.db",
        validation_alias="DATABASE_URL",
    )

    # LLM provider routing: gemini/auto are friendliest for recruiter demos (`auto`: OpenAI if
    # key exists, otherwise Gemini — set `GEMINI_*` alone for Gemini-only setups).
    llm_provider: Literal["openai", "gemini", "auto"] = Field(
        default="auto",
        validation_alias="LLM_PROVIDER",
    )
    llm_auto_failover: bool = Field(
        default=False,
        validation_alias="LLM_AUTO_FAILOVER",
        description="Reserved for experimental dual-provider failover; keep false for simple demos.",
    )

    # OpenAI (chat + embeddings)
    openai_api_key: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", validation_alias="OPENAI_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        validation_alias="OPENAI_EMBEDDING_MODEL",
    )
    openai_base_url: Optional[str] = Field(
        default=None,
        validation_alias="OPENAI_BASE_URL",
        description="Optional gateway / Azure OpenAI-compatible base URL.",
    )

    # Gemini (native Generative Language API — not OpenAI-compatible).
    gemini_api_key: Optional[str] = Field(default=None, validation_alias="GEMINI_API_KEY")
    gemini_model: str = Field(
        default="gemini-1.5-flash-latest",
        validation_alias="GEMINI_MODEL",
    )
    gemini_fallback_model: Optional[str] = Field(
        default=None,
        validation_alias="GEMINI_FALLBACK_MODEL",
        description="Optional secondary model if primary hits quota (e.g. gemini-1.5-flash).",
    )
    embedding_provider: Literal["auto", "openai", "local"] = Field(
        default="auto",
        validation_alias="EMBEDDING_PROVIDER",
    )
    local_embedding_dimensions: int = Field(
        default=256,
        validation_alias="LOCAL_EMBEDDING_DIMENSIONS",
        ge=64,
        le=3072,
    )
    llm_request_timeout_seconds: float = Field(
        default=45.0,
        validation_alias="LLM_REQUEST_TIMEOUT_SECONDS",
        gt=1.0,
        le=300.0,
    )
    llm_max_retries: int = Field(default=2, validation_alias="LLM_MAX_RETRIES", ge=0, le=8)
    llm_rate_limit_fallback_reply: Optional[str] = Field(
        default=None,
        validation_alias="LLM_RATE_LIMIT_FALLBACK_REPLY",
        description="If set, return this text with 200 on hard rate limits instead of 429.",
    )

    # Vector store — Chroma (persistent directory; Compose mounts ./data/chroma)
    chroma_persist_directory: str = Field(
        default="./data/chroma_db",
        validation_alias="CHROMA_PERSIST_DIRECTORY",
    )
    chroma_collection_name: str = Field(
        default="afois_policy_docs",
        validation_alias="CHROMA_COLLECTION_NAME",
    )

    # LangSmith observability — env names follow LangSmith + LangChain compatibility
    langsmith_tracing: bool = Field(default=False, validation_alias="LANGSMITH_TRACING")
    langsmith_api_key: Optional[str] = Field(default=None, validation_alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="afois", validation_alias="LANGSMITH_PROJECT")
    langsmith_endpoint: str = Field(
        default="https://api.smith.langchain.com",
        validation_alias="LANGSMITH_ENDPOINT",
    )

    # Optional admin token for destructive / expensive routes (disabled if unset).
    admin_reindex_token: Optional[str] = Field(default=None, validation_alias="ADMIN_REINDEX_TOKEN")

    def resolved_llm_provider(self) -> Literal["openai", "gemini"]:
        if self.llm_provider == "openai":
            return "openai"
        if self.llm_provider == "gemini":
            return "gemini"
        return "openai" if self.openai_api_key else "gemini"

    def resolved_llm_api_key(self) -> Optional[str]:
        return self.openai_api_key if self.resolved_llm_provider() == "openai" else self.gemini_api_key

    def resolved_llm_model(self) -> str:
        return self.openai_model if self.resolved_llm_provider() == "openai" else self.gemini_model

    def resolved_llm_base_url(self) -> Optional[str]:
        """OpenAI/Azure base URL only; Gemini uses the native SDK."""
        return self.openai_base_url if self.resolved_llm_provider() == "openai" else None

    def cors_origin_list(self) -> list[str]:
        raw = [o.strip() for o in self.cors_allowed_origins.split(",")]
        return [o for o in raw if o]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    """Use in tests after changing env variables."""
    get_settings.cache_clear()


def configure_langsmith_env(settings: Optional[Settings] = None) -> None:
    """Set process env vars so LangSmith + LangChain pick up tracing (no-op if tracing off)."""
    import os

    s = settings or get_settings()
    if not s.langsmith_tracing or not s.langsmith_api_key:
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")
        return

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = s.langsmith_endpoint
    os.environ["LANGCHAIN_API_KEY"] = s.langsmith_api_key
    os.environ["LANGCHAIN_PROJECT"] = s.langsmith_project
