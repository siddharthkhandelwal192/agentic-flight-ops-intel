from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from afos.core.warnings_config import configure_third_party_warnings

configure_third_party_warnings()

from afos import __version__
from afos.api.error_handlers import register_exception_handlers
from afos.api.router import build_router
from afos.core.logging import configure_logging, get_logger
from afos.core.request_context import RequestContextMiddleware
from afos.core.startup_validation import log_configuration_review
from afos.core.settings import configure_langsmith_env, get_settings
from afos.db.session import dispose_engine


def create_app() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        configure_logging(level=settings.log_level)
        configure_langsmith_env(settings)
        log_configuration_review(settings)
        log = get_logger().bind(service=settings.service_name, env=settings.env, version=__version__)
        log.info("service_starting")
        try:
            yield
        finally:
            log.info("service_stopping")
            dispose_engine()

    app = FastAPI(
        title="Agentic Flight Operations Intelligence System",
        version=__version__,
        description=(
            "Enterprise-grade agentic AI backend for airline operations: "
            "delay analysis, policy Q&A, and retrieval-augmented decision support."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(RequestContextMiddleware)
    cors_origins = settings.cors_origin_list()
    cors_kwargs: dict[str, object] = {
        "allow_origins": cors_origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
    # Dev-friendly: any localhost / 127.0.0.1 port (covers Next dev, LAN IP typos, extra tools).
    if settings.cors_allow_localhost_regex:
        cors_kwargs["allow_origin_regex"] = (
            r"^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$"
        )
    app.add_middleware(CORSMiddleware, **cors_kwargs)
    register_exception_handlers(app)
    app.include_router(build_router())

    return app


app = create_app()

