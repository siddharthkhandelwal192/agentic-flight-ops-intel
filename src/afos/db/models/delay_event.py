from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from afos.db.base import Base

if TYPE_CHECKING:
    from afos.db.models.flight import Flight


class DelayEvent(Base):
    """
    Record of a delay attribution for audit, analytics, and agent reasoning.

    IATA/A4A-style lump reasons are flattened into operational categories here.
    """

    __tablename__ = "delay_events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    flight_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("flights.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    delay_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    reason_category: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="e.g. weather, atc, crew, maintenance, operational, airline, other",
    )
    reason_detail: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ata_chapter_hint: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)

    recorded_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    recorded_by_system: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)

    flight: Mapped["Flight"] = relationship(back_populates="delay_events")
