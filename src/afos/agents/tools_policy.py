from __future__ import annotations

from langchain_chroma import Chroma
from langchain_core.tools import tool


def build_policy_tools(vector_store: Chroma):
    """RAG-backed policy retrieval bounded to embeddings + corpus metadata."""

    @tool
    def search_station_policies(query: str, k: int = 6) -> str:
        """Search airline operational policy excerpts (crew, vouchers, irregular ops manuals).

        Returns top excerpt snippets with citations.
        """

        kk = max(1, min(k, 12))
        snippets = vector_store.similarity_search(query, k=kk)
        if not snippets:
            return (
                "No corpus matches (run POST /v1/rag/rebuild after seeding Postgres policies "
                "or run scripts/sync_chroma_policies.py to refresh the vector corpus)."
            )
        lines = []
        for doc in snippets:
            meta = doc.metadata or {}
            doc_code = meta.get("doc_code", "?")
            title = meta.get("title", "?")
            section = meta.get("section_ref") or ""
            lines.append(f"[{doc_code}] {title} {section}\n{doc.page_content}\n---")
        return "\n".join(lines)

    return [search_station_policies]
