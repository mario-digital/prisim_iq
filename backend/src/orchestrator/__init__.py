"""Orchestrator graph (LangGraph v1) for multi-agent workflow."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from src.orchestrator.nodes.explainer import explainer_node
from src.orchestrator.nodes.optimizer import optimizer_node
from src.orchestrator.nodes.policy import policy_node
from src.orchestrator.nodes.reporter import reporter_node
from src.orchestrator.nodes.router import router_node
from src.orchestrator.nodes.sensitivity import sensitivity_node
from src.orchestrator.state import OrchState


def build_graph(model: str | None = None):
    """Build and compile the orchestrator graph.

    Args:
        model: Optional model name for the reporter LLM.

    Returns:
        A compiled LangGraph app ready for `.ainvoke()` / `.astream_events()`.
    """
    graph = StateGraph(OrchState)

    # Register nodes
    graph.add_node("router", router_node)
    graph.add_node("optimizer", optimizer_node)
    graph.add_node("explainer", explainer_node)
    graph.add_node("sens", sensitivity_node)
    graph.add_node("policy", policy_node)
    # reporter node captures LLM streaming; wrap to pass model
    graph.add_node("reporter", lambda s: reporter_node(s, model=model))

    # Entry
    graph.set_entry_point("router")

    # Conditional routing from router
    def route_selector(state: OrchState) -> str:
        route = state.get("route") or "optimizer"
        return {
            "optimizer": "optimizer",
            "explainer": "explainer",
            "sensitivity": "sens",
            "policy": "policy",
            "reporter": "reporter",
            "end": END,
        }.get(route, "optimizer")

    graph.add_conditional_edges(
        "router",
        route_selector,
        {
            "optimizer": "optimizer",
            "explainer": "explainer",
            "sens": "sens",
            "policy": "policy",
            "reporter": "reporter",
            END: END,
        },
    )

    # After workers, go to reporter then end
    graph.add_edge("optimizer", "reporter")
    graph.add_edge("explainer", "reporter")
    graph.add_edge("sens", "reporter")
    graph.add_edge("policy", "reporter")
    graph.add_edge("reporter", END)

    return graph.compile()
