"""Optimizer worker node: invokes price optimization tool."""

from __future__ import annotations

from loguru import logger

from src.orchestrator.state import OrchState


def optimizer_node(state: OrchState) -> dict:
    """Call the optimize_price tool with the current context and store output."""
    from src.agent.context import set_current_context
    from src.agent.tools.pricing_tools import optimize_price
    from src.schemas.market import MarketContext

    ctx_dict = state.get("context") or {}
    try:
        set_current_context(MarketContext(**ctx_dict))
    except Exception as e:  # pragma: no cover - defensive
        logger.warning("Failed to set context in optimizer_node: {}", e)

    try:
        text = optimize_price.invoke("current")
    except Exception as e:  # pragma: no cover - defensive
        logger.error("optimize_price invocation failed: {}", e)
        text = f"Error: {e}"

    outputs = dict(state.get("outputs") or {})
    outputs["optimizer"] = text
    return {"outputs": outputs}

