from __future__ import annotations

import hashlib
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from afos.core.logging import get_logger
from afos.db.models.policy_document import PolicyDocument

log = get_logger().bind(component="rag-ingestion")


def _chunk_fingerprint(policy_id: Any, start_index: int | None, chunk_index: int, text: str) -> str:
    raw = f"{policy_id}:{start_index}:{chunk_index}:{text[:200]}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def ingest_policies_session_to_chroma(
    db_session: Session,
    vector_store: Chroma,
    *,
    chunk_size: int = 900,
    chunk_overlap: int = 120,
) -> int:
    """
    Embed `policy_documents.body_text` into Chroma chunks with traceable metadata.

    Uses hierarchical separators for policy prose, preserves start_index per chunk,
    and assigns stable chunk fingerprints as Chroma IDs to reduce accidental duplicates
    on re-ingest (when not wiping the store).

    Returns total chunk count appended.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
        separators=["\n\n## ", "\n\n", "\n", ". ", " ", ""],
    )

    policies = db_session.scalars(select(PolicyDocument).order_by(PolicyDocument.effective_from.asc())).all()
    chunks: list[Document] = []
    chunk_ids: list[str] = []

    for doc in policies:
        text = (doc.body_text or "").strip()
        if not text:
            continue

        parent_meta: dict[str, Any] = {
            "policy_id": str(doc.id),
            "doc_code": doc.doc_code,
            "title": doc.title,
            "section_ref": doc.section_ref or "",
            "source_attribution": f"{doc.doc_code}"
            + (f" §{doc.section_ref}" if doc.section_ref else ""),
        }
        base = Document(page_content=text, metadata=parent_meta.copy())
        splits = splitter.split_documents([base])

        for i, split in enumerate(splits):
            body = (split.page_content or "").strip()
            if not body:
                continue
            start_idx = split.metadata.get("start_index")
            meta = {
                **parent_meta,
                "chunk_index": i,
                "start_index": start_idx if start_idx is not None else -1,
            }
            page = f"[{doc.doc_code}] {doc.title}\n{body}"
            cid = _chunk_fingerprint(doc.id, start_idx, i, body)
            chunks.append(Document(page_content=page, metadata=meta))
            chunk_ids.append(cid)

    if not chunks:
        log.info("policy_ingestion_no_chunks", policy_count=len(policies))
        return 0

    vector_store.add_documents(chunks, ids=chunk_ids)
    log.info(
        "policy_ingestion_complete",
        policy_count=len(policies),
        chunk_count=len(chunks),
        unique_ids=len(set(chunk_ids)),
    )
    return len(chunks)
