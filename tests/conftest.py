from __future__ import annotations

from afos.core.warnings_config import configure_third_party_warnings

configure_third_party_warnings()

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from afos.db.base import Base
from afos.db import session as sm

# Register model tables on Base.metadata before create_all().
import afos.db.models  # noqa: F401


@pytest.fixture
def sqlite_memory_session(monkeypatch: pytest.MonkeyPatch):
    """Isolated SQLite in-memory DB; patches global session factory for one test."""

    sm.dispose_engine()
    # StaticPool ensures every Connection shares ONE in-memory database (SQLite
    # defaults to isolated :memory: per-connection, breaking FastAPI's threadpool).
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        future=True,
    )
    monkeypatch.setattr(sm, "_engine", engine)
    monkeypatch.setattr(sm, "_session_factory", SessionLocal)

    try:
        yield SessionLocal
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()
        sm.dispose_engine()
