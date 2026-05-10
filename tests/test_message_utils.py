from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage

from afos.agents.extraction import assistant_final_plain
from afos.agents.message_utils import last_human_plain_text


def test_last_human_plain_text_reads_newest_human() -> None:
    msgs = [
        HumanMessage(content="Earlier"),
        AIMessage(content="Hi"),
        HumanMessage(content="Final question"),
    ]
    assert last_human_plain_text(msgs) == "Final question"


def test_assistant_final_plain_skips_tool_planning_turns() -> None:
    tc_msg = AIMessage(
        content="",
        tool_calls=[{"type": "tool_call", "id": "call_1", "name": "noop", "args": {}}],
    )
    final = AIMessage(content="Readable answer.")
    msgs = [HumanMessage("Q"), tc_msg, final]
    ai = assistant_final_plain(msgs)
    assert ai is not None and ai.content == "Readable answer."
