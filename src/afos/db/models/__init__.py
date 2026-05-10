from __future__ import annotations

# Import models so Alembic and metadata.create_all see all tables.
from afos.db.models.delay_event import DelayEvent  # noqa: F401
from afos.db.models.flight import Flight  # noqa: F401
from afos.db.models.policy_document import PolicyDocument  # noqa: F401

__all__ = ["Flight", "DelayEvent", "PolicyDocument"]
