"""Router node that selects the next worker based on the user message."""

from __future__ import annotations

from typing import Literal

from loguru import logger

from src.orchestrator.state import OrchState

Route = Literal["optimizer", "explainer", "sensitivity", "policy", "reporter", "end"]


def router_node(state: OrchState) -> dict:
    """Decide which worker to run next based on simple heuristics.

    This is intentionally lightweight to keep latency low. We honor keywords
    in the user message; otherwise default to the optimizer path.
    """
    message = (state.get("user_message") or "").lower()
    route: Route

    if any(k in message for k in ["why", "explain", "drivers", "factors", "shap"]):
        route = "explainer"
    elif any(k in message for k in ["sensitivity", "robust", "what if", "band", "worst", "best"]):
        route = "sensitivity"
    elif any(k in message for k in ["policy", "hierarchy", "compliance", "far", "violation"]):
        route = "policy"
    elif any(k in message for k in ["summary", "report", "executive", "leadership"]):
        route = "reporter"
    else:
        # default: price optimization
        route = "optimizer"

    logger.debug("Orchestrator router selected route: {}", route)
    return {"route": route}

