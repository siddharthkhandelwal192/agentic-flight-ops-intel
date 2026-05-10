from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class RagRebuildResponse(BaseModel):
    indexed_chunks: int = Field(ge=0)


class RagSearchHit(BaseModel):
    metadata: dict[str, Any]
    snippet: str
    distance: Optional[float] = Field(
        default=None,
        description="Chroma L2 distance when available; lower is closer.",
    )


class RagSearchResponse(BaseModel):
    query: str
    hits: list[RagSearchHit]
