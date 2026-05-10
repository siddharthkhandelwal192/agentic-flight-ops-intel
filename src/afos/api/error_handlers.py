from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from afos.core.logging import get_logger

log = get_logger().bind(component="http-errors")


def register_exception_handlers(app: FastAPI) -> None:
    """
    Extra handlers only where we add observability beyond FastAPI defaults.

    We intentionally do not register a catch-all Exception handler: it would
    intercept HTTPException and break normal 4xx/5xx semantics.
    """

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        log.warning(
            "request_validation_failed",
            path=request.url.path,
            errors=exc.errors(),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )
