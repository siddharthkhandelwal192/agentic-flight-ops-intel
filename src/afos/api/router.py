from __future__ import annotations

from fastapi import APIRouter

from afos.api.routes import chat, operations, rag, system


def build_router() -> APIRouter:
    router = APIRouter()
    router.include_router(system.router)
    router.include_router(operations.router, prefix="/v1")
    router.include_router(chat.router, prefix="/v1")
    router.include_router(rag.router, prefix="/v1")
    return router

