from __future__ import annotations

from typing import Annotated, Literal, Sequence

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing_extensions import NotRequired, TypedDict

from afos.agents.extraction import assistant_final_plain
from afos.agents.message_utils import last_human_plain_text
from afos.agents.prompts import (
    DELAY_AGENT_SYSTEM,
    GENERAL_SYSTEM,
    POLICY_AGENT_SYSTEM,
    ROUTER_SYSTEM,
)
from afos.agents.tools_delay import build_delay_tools
from afos.agents.tools_policy import build_policy_tools
from afos.core.logging import get_logger
from afos.core.settings import get_settings
from afos.llm.langchain_chat import build_lc_chat_pair
from afos.rag.chroma_store import get_policy_chroma

log = get_logger().bind(component="ops-agent-graph")


class OpsAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    intent: NotRequired[str]


class RoutedIntent(BaseModel):
    intent: Literal["delay", "policy", "general"] = Field(
        description="Single specialist lane for OCC-style assistance."
    )


def _routing_gate(state: OpsAgentState) -> str:
    intent = state.get("intent") or "general"
    lut = {
        "delay": "delay_specialist",
        "policy": "policy_specialist",
        "general": "general_specialist",
    }
    return lut.get(intent, "general_specialist")


def build_ops_agent_graph(db_session: Session):  # -> CompiledGraph (langgraph runtime type)

    settings = get_settings()
    llm_router, specialist_llm = build_lc_chat_pair(settings)

    classifier = llm_router.with_structured_output(RoutedIntent)

    def classify_node(state: OpsAgentState):
        snippet = last_human_plain_text(state["messages"])
        if not snippet.strip():
            return {"intent": "general"}
        try:
            label = classifier.invoke(
                [
                    SystemMessage(content=ROUTER_SYSTEM),
                    HumanMessage(content=f"User question:\n{snippet}"),
                ]
            )
            intent = label.intent
        except Exception as exc:  # noqa: BLE001 — fallback lane for provider/tooling glitches
            log.warning(
                "intent_classification_failed",
                error_type=type(exc).__name__,
                snippet_preview=snippet[:120],
            )
            intent = "general"
        log.info("intent_classified", intent=intent, snippet_preview=snippet[:80])
        return {"intent": intent}

    delay_tools = build_delay_tools(db_session)
    policy_vector_store = get_policy_chroma()
    policy_tools = build_policy_tools(policy_vector_store)

    delay_agent = create_react_agent(specialist_llm, delay_tools)
    policy_agent = create_react_agent(specialist_llm, policy_tools)

    def delay_specialist(state: OpsAgentState):
        payload = [SystemMessage(content=DELAY_AGENT_SYSTEM)] + state["messages"]
        result = delay_agent.invoke({"messages": payload})
        trimmed = assistant_final_plain(result["messages"])
        reply = trimmed or AIMessage(content="No summarizable delay answer.")
        return {"messages": [reply]}

    def policy_specialist(state: OpsAgentState):
        payload = [SystemMessage(content=POLICY_AGENT_SYSTEM)] + state["messages"]
        result = policy_agent.invoke({"messages": payload})
        trimmed = assistant_final_plain(result["messages"])
        reply = trimmed or AIMessage(content="Unable to summarize policy excerpts.")
        return {"messages": [reply]}

    def general_specialist(state: OpsAgentState):
        answer = specialist_llm.invoke(
            [SystemMessage(content=GENERAL_SYSTEM)] + state["messages"]
        )
        return {"messages": [answer]}

    graph = StateGraph(OpsAgentState)
    graph.add_node("classify", classify_node)
    graph.add_node("delay_specialist", delay_specialist)
    graph.add_node("policy_specialist", policy_specialist)
    graph.add_node("general_specialist", general_specialist)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        _routing_gate,
        {
            "delay_specialist": "delay_specialist",
            "policy_specialist": "policy_specialist",
            "general_specialist": "general_specialist",
        },
    )
    graph.add_edge("delay_specialist", END)
    graph.add_edge("policy_specialist", END)
    graph.add_edge("general_specialist", END)

    return graph.compile()


def run_ops_graph(
    db_session: Session,
    messages: Sequence[AnyMessage],
) -> dict[str, str | None]:
    """Execute supervisor → specialist workflow and return assistant text + intent."""

    graph = build_ops_agent_graph(db_session)
    final_state = graph.invoke({"messages": list(messages)})
    tail = assistant_final_plain(final_state["messages"])
    reply_text = tail.content if tail else ""
    log.info(
        "ops_graph_completed",
        intent=final_state.get("intent"),
        reply_chars=len(reply_text),
    )
    return {
        "intent": final_state.get("intent"),
        "reply": reply_text,
    }
