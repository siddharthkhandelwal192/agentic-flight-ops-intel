#!/usr/bin/env python
"""Offline helper: wipe + ingest policy_documents → Chroma (mirrors `/v1/rag/rebuild`).

Usage:
  export PYTHONPATH=src
  export DATABASE_URL=sqlite:///./data/afois_local.db
  python scripts/sync_chroma_policies.py [--no-wipe]
"""

from __future__ import annotations

import argparse

from afos.db.session import get_session_factory
from afos.rag.chroma_store import get_policy_chroma, wipe_chroma_store
from afos.rag.ingestion import ingest_policies_session_to_chroma


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-wipe",
        action="store_true",
        help="Append without wiping (may duplicate embeddings if run repeatedly).",
    )
    args = parser.parse_args()

    SessionLocal = get_session_factory()
    if not args.no_wipe:
        wipe_chroma_store()
    chroma_vs = get_policy_chroma()

    db = SessionLocal()
    try:
        inserted = ingest_policies_session_to_chroma(db, chroma_vs)
    finally:
        db.close()

    print(f"Ingest complete: chunks={inserted}")


if __name__ == "__main__":
    main()
