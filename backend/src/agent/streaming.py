"""Streaming SSE utilities for PrismIQ agent.

Provides async generators that convert agent stream events to SSE format.
"""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from src.agent.agent import PrismIQAgent
    from src.schemas.market import MarketContext


async def sse_generator(
    agent: PrismIQAgent,
    message: str,
    context: MarketContext,
    session_id: str = "default",
    plan: bool = False,
    model: str | None = None,
) -> AsyncGenerator[str, None]:
    """Convert agent stream to SSE format.

    Args:
        agent: PrismIQ agent instance.
        message: User's message to process.
        context: Market context for tool execution.
        session_id: Session ID for conversation memory.

    Yields:
        SSE-formatted strings: "data: {json}\n\n"

    SSE Event Format:
        data: {"token": "The ", "done": false}

        data: {"tool_call": "optimize_price", "done": false}

        data: {"message": "...", "tools_used": [...], "done": true}

        data: {"error": "...", "done": true}
    """
    try:
        async for event in agent.stream_chat(message, context, session_id, plan=plan, model=model):
            yield {"data": json.dumps(event)}
    except Exception as e:
        logger.error(f"SSE generator error: {e}", exc_info=True)
        error_event = {"error": str(e), "done": True}
        yield {"data": json.dumps(error_event)}


async def sse_keepalive_generator(
    agent: PrismIQAgent,
    message: str,
    context: MarketContext,
    session_id: str = "default",
    keepalive_interval: float = 15.0,
    plan: bool = False,
    model: str | None = None,
) -> AsyncGenerator[str, None]:
    """SSE generator with keepalive comments for connection health.

    Adds periodic keepalive comments to prevent connection timeouts.

    Args:
        agent: PrismIQ agent instance.
        message: User's message to process.
        context: Market context for tool execution.
        session_id: Session ID for conversation memory.
        keepalive_interval: Seconds between keepalive comments.

    Yields:
        SSE-formatted strings including keepalive comments.
    """
    import asyncio
    from datetime import UTC, datetime

    last_event_time = datetime.now(UTC)

    async def check_keepalive() -> str | None:
        """Check if keepalive is needed."""
        nonlocal last_event_time
        now = datetime.now(UTC)
        if (now - last_event_time).total_seconds() > keepalive_interval:
            last_event_time = now
            # SSE comment line to keep the connection alive
            return {"data": "{}"}
        return None

    try:
        async for event in agent.stream_chat(message, context, session_id, plan=plan, model=model):
            last_event_time = datetime.now(UTC)
            yield {"data": json.dumps(event)}

            # Check if done, no need for keepalive after completion
            if event.get("done"):
                break

    except asyncio.CancelledError:
        # Client disconnected
        logger.info(f"SSE stream cancelled for session: {session_id}")
        raise
    except Exception as e:
        logger.error(f"SSE generator error: {e}", exc_info=True)
        error_event = {"error": str(e), "done": True}
        yield {"data": json.dumps(error_event)}
