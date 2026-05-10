from __future__ import annotations

from typing import Iterable

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from afos.api.schemas.llm import ChatRoleMessage


def openapi_messages_to_lc(messages: Iterable[ChatRoleMessage]) -> list[BaseMessage]:
    lc: list[BaseMessage] = []
    for m in messages:
        if m.role == "system":
            lc.append(SystemMessage(content=m.content))
        elif m.role == "user":
            lc.append(HumanMessage(content=m.content))
        else:
            lc.append(AIMessage(content=m.content))
    return lc
