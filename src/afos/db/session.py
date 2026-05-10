from __future__ import annotations

from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from afos.core.settings import get_settings

_engine = None  # Lazily initialized SQLAlchemy Engine
_session_factory: Optional[sessionmaker[Session]] = None  # Bound sessionmaker


def _build_engine_url() -> str:
    return get_settings().database_url


def configure_engine(database_url: Optional[str] = None, *, reset: bool = False) -> None:
    """Create (or recreate) engine and Session factory. Called on first use or forced reset."""

    global _engine, _session_factory
    if reset and _engine is not None:
        _engine.dispose()
        _engine = None
        _session_factory = None

    if _engine is not None:
        return

    url = database_url or _build_engine_url()
    kwargs: dict[str, object] = {
        "pool_pre_ping": True,
        # SQLAlchemy 2.0 declarative mappings use future Engine/Sessions by default paths;
        # keep explicit compatibility with sessionmaker(bind=...)
        "future": True,
    }

    # SQLite defaults to scoped thread checking; FastAPI spans threads for sync defs.
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}

    _engine = create_engine(url, **kwargs)
    _session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=_engine,
        future=True,
    )


def get_engine():
    configure_engine()
    assert _engine is not None  # pragma: no cover — satisfied after configure
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    configure_engine()
    assert _session_factory is not None  # pragma: no cover
    return _session_factory


def dispose_engine() -> None:
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None
