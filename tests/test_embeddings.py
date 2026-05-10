from __future__ import annotations

from afos.core.settings import clear_settings_cache
from afos.rag.embeddings import LocalDeterministicEmbeddings, get_embeddings, reset_embeddings_singleton


def test_local_embeddings_used_when_openai_key_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("EMBEDDING_PROVIDER", "auto")
    clear_settings_cache()
    reset_embeddings_singleton()

    try:
        embeddings = get_embeddings()
        assert isinstance(embeddings, LocalDeterministicEmbeddings)
        v = embeddings.embed_query("crew delay mitigation")
        assert len(v) > 0
    finally:
        reset_embeddings_singleton()
        clear_settings_cache()
