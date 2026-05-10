from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Select, select, text
from sqlalchemy.orm import Session

from afos.api.deps import get_db
from afos.api.schemas.flight import FlightRead
from afos.core.settings import get_settings
from afos.db.models.flight import Flight

router = APIRouter(prefix="/ops", tags=["operations"])


@router.get("/ready")
def readiness(db: Session = Depends(get_db)) -> dict[str, object]:
    """Kubernetes-style readiness: DB must answer. Use with `/health` for liveness."""

    scalar = db.execute(text("SELECT 1")).scalar_one()
    s = get_settings()
    return {
        "status": "ready",
        "database": "ok",
        "scalar": scalar,
        "llm_configured": bool(s.resolved_llm_api_key()),
        "llm_provider": s.resolved_llm_provider(),
    }


@router.get("/llm-config")
def llm_configuration_probe() -> dict[str, object]:
    """Non-secret LLM configuration snapshot (safe for dashboards / ops UI badges)."""

    s = get_settings()
    primary = s.resolved_llm_provider()
    return {
        "llm_provider": primary,
        "openai_ready": bool(s.openai_api_key),
        "gemini_ready": bool(s.gemini_api_key),
        "llm_configured": bool(s.resolved_llm_api_key()),
        "llm_model": s.resolved_llm_model(),
        "embedding_provider": s.embedding_provider,
        "llm_auto_failover": s.llm_auto_failover,
        "rate_limit_fallback_configured": bool(s.llm_rate_limit_fallback_reply),
        "dual_provider_ready": bool(s.openai_api_key and s.gemini_api_key),
    }


@router.get("/db-health")
def database_health(db: Session = Depends(get_db)) -> dict[str, object]:
    """Basic connectivity probe (load balancers can use `/health`; this checks ORM wiring)."""

    scalar = db.execute(text("SELECT 1")).scalar_one()
    return {"status": "ok", "scalar": scalar}


@router.get("/flights", response_model=list[FlightRead])
def list_recent_flights(
    db: Session = Depends(get_db),
    limit: int = Query(25, ge=1, le=200),
    airline_code: Optional[str] = Query(None, description="Optional IATA airline code filter, e.g. UA."),
) -> list[Flight]:
    stmt: Select[Flight] = select(Flight).order_by(Flight.scheduled_departure_utc.desc())
    if airline_code:
        stmt = stmt.where(Flight.airline_code == airline_code.upper())
    stmt = stmt.limit(limit)

    rows = db.scalars(stmt).all()
    return list(rows)
