"""Sensitivity worker node: invokes sensitivity analysis tool."""

from __future__ import annotations

from loguru import logger

from src.orchestrator.state import OrchState


def sensitivity_node(state: OrchState) -> dict:
    """Call the sensitivity_analysis tool with the current context and store output."""
    from src.agent.context import set_current_context
    from src.agent.tools.pricing_tools import sensitivity_analysis
    from src.schemas.market import MarketContext

    ctx_dict = state.get("context") or {}
    try:
        set_current_context(MarketContext(**ctx_dict))
    except Exception as e:  # pragma: no cover
        logger.warning("Failed to set context in sensitivity_node: {}", e)

    try:
        text = sensitivity_analysis.invoke("current")
    except Exception as e:  # pragma: no cover
        logger.error("sensitivity_analysis invocation failed: {}", e)
        text = f"Error: {e}"

    outputs = dict(state.get("outputs") or {})
    outputs["sensitivity"] = text
    return {"outputs": outputs}

