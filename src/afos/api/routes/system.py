from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from afos import __version__
from afos.core.settings import get_settings


router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.service_name,
        "version": __version__,
        "time_utc": datetime.now(timezone.utc).isoformat(),
    }

