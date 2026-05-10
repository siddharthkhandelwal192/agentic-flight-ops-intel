from __future__ import annotations

from typing import Iterable

from langchain_core.messages import AIMessage


def _flatten_ai_content(raw: object) -> str | None:
    if raw is None:
        return None
    if isinstance(raw, str):
        return raw.strip() or None
    if isinstance(raw, list):
        parts: list[str] = []
        for block in raw:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(str(block.get("text", "")))
                elif "text" in block:
                    parts.append(str(block["text"]))
        joined = "".join(parts).strip()
        return joined or None
    return str(raw).strip() or None


def assistant_final_plain(messages: Iterable[object]) -> AIMessage | None:
    """Pick last plain assistant message (skip tool-planning turns)."""

    for msg in reversed(list(messages)):
        if not isinstance(msg, AIMessage):
            continue
        tool_calls = getattr(msg, "tool_calls", None) or []
        if tool_calls:
            continue
        text = _flatten_ai_content(getattr(msg, "content", None))
        if text:
            return AIMessage(content=text)
    return None
