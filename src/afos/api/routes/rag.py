from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from afos.api.deps import get_db
from afos.api.schemas.rag import RagRebuildResponse, RagSearchResponse
from afos.core.logging import get_logger
from afos.core.settings import get_settings
from afos.rag.chroma_store import get_policy_chroma, wipe_chroma_store
from afos.rag.ingestion import ingest_policies_session_to_chroma

router = APIRouter(prefix="/rag", tags=["rag-vector"])
log = get_logger().bind(component="rag-routes")


def _require_admin(x_admin_token: Optional[str] = Header(default=None)) -> None:
    s = get_settings()
    secret = s.admin_reindex_token
    if not secret:
        raise HTTPException(
            status_code=503,
            detail="ADMIN_REINDEX_TOKEN is not configured server-side.",
        )
    if not x_admin_token or x_admin_token != secret:
        raise HTTPException(status_code=403, detail="Missing or invalid X-Admin-Token header.")


@router.post("/rebuild", response_model=RagRebuildResponse)
def rebuild_policy_corpus(
    db: Session = Depends(get_db), _: None = Depends(_require_admin)
) -> RagRebuildResponse:
    """Wipe persisted Chroma + re-ingest Postgres `policy_documents` (destructive demo admin op)."""

    try:
        wipe_chroma_store()
        chroma_vs = get_policy_chroma()
        inserted = ingest_policies_session_to_chroma(db, chroma_vs)
    except Exception as exc:  # pragma: no cover - defensive for provider/store runtime failures
        log.exception("rag_rebuild_failed", error=str(exc))
        raise HTTPException(status_code=500, detail="Failed to rebuild policy corpus.") from exc
    log.info("rag_rebuild_completed", indexed_chunks=inserted)
    return RagRebuildResponse(indexed_chunks=inserted)


@router.get("/search", response_model=RagSearchResponse)
def debug_similarity(
    q: str = Query(..., description="Semantic search probe against policy corpus."),
    k: int = Query(8, ge=1, le=24),
):
    """Lightweight cosine-style similarity listing for debugging ingestion quality."""

    try:
        chroma_vs = get_policy_chroma()
        pairs = chroma_vs.similarity_search_with_score(q, k=k)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - depends on vector DB backend runtime behavior
        log.exception("rag_similarity_failed", error=str(exc))
        raise HTTPException(status_code=500, detail="Vector search failed.") from exc

    hits = []
    distances: list[float] = []
    for doc, dist in pairs:
        d = float(dist) if dist is not None else None
        if d is not None:
            distances.append(d)
        hits.append(
            {
                "metadata": doc.metadata,
                "snippet": doc.page_content[:750],
                "distance": d,
            }
        )
    log.info(
        "rag_similarity_completed",
        query=q,
        top_k=k,
        hit_count=len(hits),
        distances_preview=distances[:3],
        doc_codes=[h["metadata"].get("doc_code") for h in hits[:5]],
    )
    return RagSearchResponse(query=q, hits=hits)
