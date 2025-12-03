"""Thread-local context storage for agent tool execution.

This module provides a thread-safe way to store and retrieve the current
MarketContext that tools need to access during agent execution.
"""

from __future__ import annotations

import contextvars
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.schemas.market import MarketContext

# Context variable for storing current market context
_current_context: contextvars.ContextVar[MarketContext | None] = contextvars.ContextVar(
    "current_context",
    default=None,
)


def set_current_context(context: MarketContext) -> None:
    """Set the current market context for tool execution.

    Args:
        context: MarketContext to make available to tools.
    """
    _current_context.set(context)


def get_current_context() -> MarketContext:
    """Get the current market context for tool execution.

    Returns:
        The current MarketContext.

    Raises:
        RuntimeError: If no context has been set.
    """
    context = _current_context.get()
    if context is None:
        raise RuntimeError(
            "No market context available. "
            "Ensure set_current_context() is called before tool execution."
        )
    return context


def clear_current_context() -> None:
    """Clear the current market context."""
    _current_context.set(None)

