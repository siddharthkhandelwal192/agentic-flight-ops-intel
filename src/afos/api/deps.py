from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from afos.db.session import get_session_factory


def get_db() -> Generator[Session, None, None]:
    """
    Yield a transactional SQLAlchemy session per request.

    FastAPI mounts sync dependencies in a worker threadpool; SQLite must allow
    cross-thread reuse (handled in configure_engine.connect_args).
    Callers perform ``db.commit()`` when mutating persisted state.
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
