"""State definitions for the LangGraph orchestrator (v1)."""

from __future__ import annotations

from typing import TypedDict


class OrchState(TypedDict, total=False):
    """Minimal orchestrator state for routing and outputs."""

    user_message: str
    context: dict
    route: str
    outputs: dict
    violations: list[dict]
