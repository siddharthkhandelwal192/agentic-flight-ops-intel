from __future__ import annotations

from datetime import timezone

import sqlalchemy as sa
from langchain_core.tools import tool
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from afos.db.models.delay_event import DelayEvent
from afos.db.models.flight import Flight


def build_delay_tools(db: Session):
    """Read-only LangChain tools bound to the current request-scoped SQLAlchemy Session."""

    @tool
    def list_delayed_flights(limit: int = 20) -> str:
        """Fetch flights currently marked delayed (relational OCC snapshot).

        `limit` clamps between 1 and 100.
        """
        cap = max(1, min(limit, 100))

        stmt: Select = (
            select(
                Flight.flight_number,
                Flight.airline_code,
                Flight.origin_iata,
                Flight.destination_iata,
                Flight.status,
                Flight.aircraft_tail,
                Flight.scheduled_departure_utc,
                Flight.actual_departure_utc,
            )
            .where(Flight.status == "delayed")
            .order_by(Flight.scheduled_departure_utc.desc())
            .limit(cap)
        )

        rows = db.execute(stmt).all()
        if not rows:
            return "No flights with status=delayed."
        lines = []
        for r in rows:
            sd = r.scheduled_departure_utc.isoformat() if r.scheduled_departure_utc else None
            ad = r.actual_departure_utc.isoformat() if r.actual_departure_utc else None
            lines.append(
                f"{r.airline_code}{r.flight_number} {r.origin_iata}-{r.destination_iata} "
                f"tail={r.aircraft_tail or '—'} sched_dep_utc={sd} actual_dep_utc={ad}"
            )
        return "\n".join(lines)

    @tool
    def analyze_recent_delay_events(limit: int = 35) -> str:
        """Return chronological delay attribution rows with joined flight identifiers.

        `limit` clamps between 1 and 250.
        """

        cap = max(1, min(limit, 250))
        stmt = (
            select(
                Flight.flight_number,
                DelayEvent.delay_minutes,
                DelayEvent.reason_category,
                DelayEvent.reason_detail,
                DelayEvent.recorded_at_utc,
            )
            .join(DelayEvent, DelayEvent.flight_id == Flight.id)
            .order_by(DelayEvent.recorded_at_utc.desc())
            .limit(cap)
        )

        rows = db.execute(stmt).all()
        if not rows:
            return "No delay attribution rows recorded."
        lines = []
        for r in rows:
            recorded = r.recorded_at_utc
            if recorded and recorded.tzinfo is None:
                recorded = recorded.replace(tzinfo=timezone.utc)
            ts = recorded.isoformat() if recorded else "—"
            detail = r.reason_detail or ""
            lines.append(
                f"{r.flight_number}|{r.delay_minutes}m|{r.reason_category}|"
                f"{detail}|recorded={ts}"
            )
        return "\n".join(lines)

    @tool
    def delay_statistics_snapshot() -> str:
        """Aggregate delay durations grouped by attribution category for OCC KPI narrative."""

        stmt = (
            select(
                DelayEvent.reason_category,
                func.avg(DelayEvent.delay_minutes).label("avg_delay"),
                func.count(DelayEvent.id).label("cases"),
            )
            .group_by(DelayEvent.reason_category)
            .order_by(sa.desc("cases"))
        )
        rows = db.execute(stmt).all()
        if not rows:
            return "No delays available for aggregation."
        parts = []
        for r in rows:
            avg = float(r.avg_delay or 0.0)
            parts.append(f"{r.reason_category}: n={r.cases} avg_delay_min={avg:.2f}")
        return "\n".join(parts)

    @tool
    def flights_touching_station(iata: str, limit: int = 35) -> str:
        """List flights departing or arriving at a station (IATA).

        `limit` clamps between 1 and 120.
        """

        cap = max(1, min(limit, 120))
        raw = iata.upper().strip()
        if len(raw) < 3 or len(raw) > 4 or not raw.isalpha():
            return "Invalid IATA station code (use 3–4 letters, e.g. ORD)."
        iata_upper = raw
        stmt = (
            select(
                Flight.flight_number,
                Flight.origin_iata,
                Flight.destination_iata,
                Flight.status,
                Flight.scheduled_departure_utc,
            )
            .where(
                sa.or_(
                    Flight.origin_iata == iata_upper,
                    Flight.destination_iata == iata_upper,
                )
            )
            .order_by(Flight.scheduled_departure_utc.desc())
            .limit(cap)
        )

        rows = db.execute(stmt).all()
        if not rows:
            return f"No flights found for station {iata_upper}."
        return "\n".join(
            (
                f"{r.flight_number}: {r.origin_iata}-{r.destination_iata} status={r.status} "
                f"dep_utc={r.scheduled_departure_utc.isoformat() if r.scheduled_departure_utc else '—'}"
            )
            for r in rows
        )

    return [list_delayed_flights, analyze_recent_delay_events, delay_statistics_snapshot, flights_touching_station]
