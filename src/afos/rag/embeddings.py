from __future__ import annotations

import hashlib
import math

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from afos.core.settings import get_settings


class LocalDeterministicEmbeddings(Embeddings):
    """
    Lightweight offline embedding fallback.

    Uses hashed token projections to create deterministic vectors so local RAG
    ingestion and similarity debugging work without external API credentials.
    """

    def __init__(self, dimensions: int = 256):
        self._dimensions = dimensions

    def _embed_text(self, text: str) -> list[float]:
        buckets = [0.0] * self._dimensions
        for raw_token in text.lower().split():
            token = raw_token.strip(".,;:!?()[]{}\"'")
            if not token:
                continue
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % self._dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            weight = 1.0 + (digest[5] / 255.0)
            buckets[idx] += sign * weight

        norm = math.sqrt(sum(v * v for v in buckets))
        if norm == 0:
            return buckets
        return [v / norm for v in buckets]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_text(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed_text(text)


_embeddings_singleton: Embeddings | None = None


def _should_use_local(provider: str, openai_api_key: str | None) -> bool:
    if provider == "local":
        return True
    if provider == "openai":
        return False
    return not openai_api_key


def get_embeddings() -> Embeddings:
    """Singleton embedding provider with local fallback for offline/local development."""

    global _embeddings_singleton
    s = get_settings()

    if _embeddings_singleton is None:
        if _should_use_local(s.embedding_provider, s.openai_api_key):
            _embeddings_singleton = LocalDeterministicEmbeddings(
                dimensions=s.local_embedding_dimensions
            )
        else:
            if not s.openai_api_key:
                raise RuntimeError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai.")
            _embeddings_singleton = OpenAIEmbeddings(
                model=s.openai_embedding_model,
                api_key=s.openai_api_key,
                base_url=s.openai_base_url,
            )

    return _embeddings_singleton


def reset_embeddings_singleton() -> None:
    """Reset cached embeddings client (primarily for tests)."""

    global _embeddings_singleton
    _embeddings_singleton = None
