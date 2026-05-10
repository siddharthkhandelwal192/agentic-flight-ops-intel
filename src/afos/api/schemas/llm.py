from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChatRoleMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., max_length=32_000)


class ChatCompletionRequest(BaseModel):
    messages: list[ChatRoleMessage] = Field(..., min_length=1)
    temperature: float = Field(default=0.15, ge=0.0, le=2.0)


class ChatCompletionResponse(BaseModel):
    reply: str
    model: str
    provider: Optional[str] = Field(default=None, description="openai | gemini")
    latency_ms: Optional[float] = Field(default=None, description="End-to-end wall time estimate.")
    failover_used: bool = Field(default=False, description="Whether a secondary LLM responded after primary rate-limit.")


class AgentInvokeRequest(BaseModel):
    messages: list[ChatRoleMessage] = Field(..., min_length=1)


class AgentInvokeResponse(BaseModel):
    intent: Optional[str]
    reply: str
    model: str
