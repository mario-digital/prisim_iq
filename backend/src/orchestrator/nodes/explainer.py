"""Explainer worker node: invokes explanation tool."""

from __future__ import annotations

from loguru import logger

from src.orchestrator.state import OrchState


def explainer_node(state: OrchState) -> dict:
    """Call the explain_decision tool with the current context and store output."""
    from src.agent.context import set_current_context
    from src.agent.tools.pricing_tools import explain_decision
    from src.schemas.market import MarketContext

    ctx_dict = state.get("context") or {}
    try:
        set_current_context(MarketContext(**ctx_dict))
    except Exception as e:  # pragma: no cover
        logger.warning("Failed to set context in explainer_node: {}", e)

    try:
        text = explain_decision.invoke("current")
    except Exception as e:  # pragma: no cover
        logger.error("explain_decision invocation failed: {}", e)
        text = f"Error: {e}"

    outputs = dict(state.get("outputs") or {})
    outputs["explainer"] = text
    return {"outputs": outputs}

