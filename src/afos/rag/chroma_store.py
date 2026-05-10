from __future__ import annotations

from pathlib import Path
from typing import Optional

from langchain_chroma import Chroma

from afos.core.settings import Settings, get_settings
from afos.rag.embeddings import get_embeddings

_chroma_singleton: Optional[Chroma] = None


def ensure_chroma_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def reset_chroma_singleton() -> None:
    global _chroma_singleton
    _chroma_singleton = None


def get_policy_chroma(settings: Settings | None = None) -> Chroma:
    """
    Persisted LangChain × Chroma store for airline policy corpus (RAG layer).

    Re-opened lazily once per process; call `reset_chroma_singleton()` after wipes.
    """
    global _chroma_singleton

    if _chroma_singleton is not None:
        return _chroma_singleton

    s = settings or get_settings()
    ensure_chroma_dir(s.chroma_persist_directory)
    embeddings = get_embeddings()

    _chroma_singleton = Chroma(
        persist_directory=s.chroma_persist_directory,
        collection_name=s.chroma_collection_name,
        embedding_function=embeddings,
    )
    return _chroma_singleton


def wipe_chroma_store(settings: Settings | None = None) -> None:
    """Remove on-disk chroma persistence (destructive admin action).

    On Docker volume mounts, deleting the mount root itself can raise EBUSY;
    we clear *contents* and keep the directory.
    """

    reset_chroma_singleton()
    s = settings or get_settings()
    chroma_root = Path(s.chroma_persist_directory).resolve()
    if chroma_root.exists():
        import shutil

        for child in chroma_root.iterdir():
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                try:
                    child.unlink()
                except OSError:
                    pass
    ensure_chroma_dir(s.chroma_persist_directory)
