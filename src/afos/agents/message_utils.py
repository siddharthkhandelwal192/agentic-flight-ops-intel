from __future__ import annotations

from typing import Iterable

from langchain_core.messages import BaseMessage, HumanMessage


def last_human_plain_text(messages: Iterable[BaseMessage]) -> str:
    """Best-effort plaintext for the newest human turn (vision blocks ignored)."""

    for msg in reversed(list(messages)):
        if not isinstance(msg, HumanMessage):
            continue
        content = msg.content
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            fragments: list[str] = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    fragments.append(str(block.get("text", "")))
            return "".join(fragments).strip()
    return ""
