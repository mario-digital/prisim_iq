"""PrismIQ LangChain Agent for intelligent pricing copilot interactions.

This module implements the main agent using LangChain v1.1
`create_tool_calling_agent` + `AgentExecutor` with streaming support and
session-scoped chat history.

Architecture (v1 patterns):
    - Tool-calling agent via `create_tool_calling_agent`
    - `AgentExecutor` to run tools and produce an `output` string
    - Per-session chat history passed as `chat_history` (Runnable pattern)
    - Streaming via `astream_events(version="v1")` for SSE
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import suppress
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from loguru import logger

from src.agent.utils import sanitize_error_message

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool

    from src.schemas.market import MarketContext


class PrismIQAgent:
    """LangChain v1 agent for pricing copilot interactions with streaming.

    Orchestrates:
    - Tool selection via a tool-calling agent runnable
    - Conversation memory per session using in-memory chat history
    - Streaming token/tool events for SSE responses
    """

    def __init__(self, tools: list[BaseTool]) -> None:
        """Initialize the PrismIQ agent with LangChain v1.1.

        Args:
            tools: List of LangChain tools available to the agent.
        """
        # Defer imports to avoid loading LangChain unless agent is used
        from langchain.agents import create_agent
        from langchain_core.messages import SystemMessage
        from langchain_openai import ChatOpenAI

        from src.agent.prompts import SYSTEM_PROMPT
        from src.config import get_settings

        settings = get_settings()

        # v1: Use langchain-openai ChatOpenAI (tool calling capable model)
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=settings.openai_api_key,
            streaming=True,
        )

        self.tools = tools

        # Build tool-calling agent runnable
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=SystemMessage(content=SYSTEM_PROMPT),
        )

        # Simple in-memory per-session chat history as list of (role, content) tuples
        # Roles: "user" | "assistant"
        self._history: dict[str, list[tuple[str, str]]] = {}

        logger.info(
            f"PrismIQAgent initialized with {len(tools)} tools: "
            f"{[t.name for t in tools]}"
        )

    async def chat(
        self,
        message: str,
        context: MarketContext,
        session_id: str = "default",
    ) -> dict[str, Any]:
        """Process a chat message and return agent response (non-streaming).

        Args:
            message: User's natural language query.
            context: Current market context for tool execution.
            session_id: Session ID for conversation memory.

        Returns:
            Dictionary with response message, tools used, and metadata.
        """
        from src.agent.context import set_current_context

        start_time = datetime.now(UTC)

        # Store context for tools to access
        set_current_context(context)

        logger.info(f"Processing chat: '{message[:100]}...' session={session_id}")

        try:
            # Retrieve history and build message list for the agent
            history = self._history.get(session_id, [])
            messages = history + [("user", message)]

            # Invoke the agent runnable with message list
            result = await self.agent.ainvoke({"messages": messages})

            # Extract response and (optionally) tools used
            final_message = result["messages"][-1].content
            tools_used: list[str] = []

            # Update history with user and assistant turns
            history = messages + [("assistant", final_message)]
            self._history[session_id] = history  # type: ignore[assignment]

            end_time = datetime.now(UTC)

            response = {
                "message": final_message,
                "tools_used": tools_used,
                "context": context.model_dump(),
                "processing_time_ms": (end_time - start_time).total_seconds() * 1000,
            }

            logger.info(
                f"Chat complete: tools_used={tools_used}, "
                f"time={response['processing_time_ms']:.1f}ms"
            )

            return response

        except Exception as e:
            logger.error(f"Agent chat error: {e}", exc_info=True)
            user_message = sanitize_error_message(e)
            return {
                "message": f"I encountered an error processing your request. {user_message}",
                "tools_used": [],
                "context": context.model_dump(),
                "error": user_message,
            }

    async def stream_chat(
        self,
        message: str,
        context: MarketContext,
        session_id: str = "default",
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream chat response with token-by-token output for SSE.

        Args:
            message: User's natural language query.
            context: Current market context for tool execution.
            session_id: Session ID for conversation memory.

        Yields:
            Event dictionaries for SSE streaming:
            - {"token": "...", "done": False} for tokens
            - {"tool_call": "tool_name", "done": False} for tool invocations
            - {"message": "...", "tools_used": [...], "done": True} for completion
            - {"error": "...", "done": True} for errors
        """
        from src.agent.context import set_current_context

        # Store context for tools to access
        set_current_context(context)

        logger.info(f"Streaming chat: '{message[:100]}...' session={session_id}")

        tools_used: list[str] = []
        token_buffer = ""
        extracted_text: str | None = None
        last_tool_output: str | None = None

        try:
            # Helper to robustly extract text from various LC event payload shapes
            def _extract_text(obj: Any) -> str | None:
                if obj is None:
                    return None
                if isinstance(obj, str):
                    return obj if obj.strip() else None
                if isinstance(obj, dict):
                    # Prefer common text-bearing keys first
                    for key in (
                        "content",
                        "text",
                        "output_text",
                        "message",
                        "result",
                        "output",
                    ):
                        if key in obj:
                            val = _extract_text(obj.get(key))
                            if val:
                                return val
                    # Fallback: search nested dict values
                    for v in obj.values():
                        val = _extract_text(v)
                        if val:
                            return val
                    return None
                if isinstance(obj, list):
                    for el in obj:
                        val = _extract_text(el)
                        if val:
                            return val
                    return None
                # Try common attributes on message/chunk-like objects
                with suppress(Exception):
                    if hasattr(obj, "content"):
                        val = obj.content  # type: ignore[attr-defined]
                        if isinstance(val, str) and val.strip():
                            return val
                    if hasattr(obj, "text"):
                        val = obj.text  # type: ignore[attr-defined]
                        if isinstance(val, str) and val.strip():
                            return val
                # Last resort: string representation if non-empty
                try:
                    s = str(obj)
                    return s if isinstance(s, str) and s.strip() else None
                except Exception:
                    return None

            # Clean up incremental token artifacts from model streaming
            def _clean_token(token: str, prev_tail: str) -> str:
                t = token
                # Collapse 4+ asterisks to 2 (avoid duplicated bold markers)
                while "****" in t:
                    t = t.replace("****", "**")
                # If previous buffer already ends with '**' and token starts with '**', drop leading '**'
                if prev_tail.endswith("**") and t.startswith("**"):
                    t = t[2:]
                # Normalize whitespace chunks
                if t.strip() == "":
                    return t
                return t

            # Retrieve history and build message list
            history = self._history.get(session_id, [])
            messages = history + [("user", message)]

            # Stream normalized v1 events from the agent runnable
            async for event in self.agent.astream_events(
                {"messages": messages}, version="v1"
            ):
                etype = event.get("event")
                with suppress(Exception):
                    logger.debug(
                        "LC event {} name={} data_keys={}",
                        etype,
                        event.get("name"),
                        list(event.get("data", {}).keys()),
                    )

                # Token events (generic + chat-specific)
                if etype == "on_llm_new_token":
                    token = event.get("data", {}).get("token", "")
                    if token:
                        token = _clean_token(token, token_buffer[-2:] if len(token_buffer) >= 2 else token_buffer)
                        token_buffer += token
                        yield {"token": token, "done": False}

                if etype == "on_chat_model_stream":
                    # Only emit actual text tokens; ignore tool-call metadata chunks
                    chunk = event.get("data", {}).get("chunk")
                    token = None
                    with suppress(Exception):
                        # Many LC chunks expose `.content` when actual text streams
                        if hasattr(chunk, "content"):
                            val = chunk.content  # type: ignore[attr-defined]
                            if isinstance(val, str) and val.strip():
                                token = val
                    if token:
                        token = _clean_token(token, token_buffer[-2:] if len(token_buffer) >= 2 else token_buffer)
                        token_buffer += token
                        yield {"token": token, "done": False}

                # Tool call starts
                if etype == "on_tool_start":
                    name = event.get("name") or event.get("data", {}).get("name")
                    if name and name not in tools_used:
                        tools_used.append(str(name))
                        yield {"tool_call": str(name), "done": False}

                # Tool completed; capture output as a fallback if no tokens are streamed
                if etype == "on_tool_end":
                    d = event.get("data", {})
                    # Shapes: {output: str|dict|list} or {result: str|dict}
                    out = d.get("output") or d.get("result") or d.get("output_str")
                    text = _extract_text(out)
                    if text:
                        last_tool_output = text
                        with suppress(Exception):
                            logger.info(
                                "Captured tool output (len={})",
                                len(last_tool_output),
                            )

                # Some models/tools may not stream tokens; capture final text on llm end
                if etype in ("on_llm_end", "on_chat_model_end") and not token_buffer:
                    data = event.get("data", {})
                    text = _extract_text(data.get("output")) or data.get("output_text")
                    if not text:
                        gens = data.get("generations") or []
                        text = _extract_text(gens)
                    if text:
                        extracted_text = text
                        with suppress(Exception):
                            logger.info("Captured LLM end text (len={})", len(extracted_text))

                # Chain end may carry the final structured output; try to extract
                if etype == "on_chain_end" and not token_buffer and not extracted_text:
                    data = event.get("data", {})
                    text = _extract_text(data.get("output"))
                    if text:
                        extracted_text = text
                        with suppress(Exception):
                            logger.info("Captured chain end text (len={})", len(extracted_text))

            # Update history for this session (user + assistant)
            # Assemble and normalize final message
            final_message = (
                token_buffer
                if token_buffer
                else (last_tool_output or extracted_text or "")
            )
            if final_message:
                import re
                # Collapse repeating spaces/tabs within lines
                final_message = re.sub(r"[ \t]{2,}", " ", final_message)
                # Trim spaces before punctuation
                final_message = re.sub(r"\s+([.,;:!?])", r"\1", final_message)
                # Collapse 3+ newlines to maximum of 2
                final_message = re.sub(r"\n{3,}", "\n\n", final_message)
                # Strip trailing spaces on lines
                final_message = re.sub(r"[ \t]+\n", "\n", final_message)
                # Final trim
                final_message = final_message.strip()
            history = messages + [("assistant", final_message)]
            self._history[session_id] = history  # type: ignore[assignment]

            # Final completion event
            # final_message is already resolved from tokens → tool → llm/chain
            yield {
                "message": final_message,
                "tools_used": tools_used,
                "done": True,
            }

            logger.info(f"Stream complete: tools_used={tools_used}")

        except Exception as e:
            logger.error(f"Stream chat error: {e}", exc_info=True)
            error_message = sanitize_error_message(e)
            yield {"error": error_message, "done": True}

    def _extract_tools_used(self, _: dict) -> list[str]:
        """Placeholder for extracting tools from non-stream results (optional)."""
        # AgentExecutor returns only {"output": ...} by default; tool inspection would
        # require callbacks/logging. We rely on streaming path for tool reporting.
        return []

    def clear_memory(self, session_id: str = "default") -> None:
        """Clear conversation memory for a session.

        Note: This clears the per-session chat history maintained by this agent.
        """
        try:
            if session_id in self._history:
                del self._history[session_id]
            logger.info(f"Cleared memory for session: {session_id}")
        except Exception as e:
            logger.warning(f"Could not clear memory: {e}")


# Singleton agent instance
_agent: PrismIQAgent | None = None


def get_agent() -> PrismIQAgent:
    """Get or create singleton PrismIQAgent instance.

    Returns:
        PrismIQAgent instance with all tools configured.
    """
    global _agent

    if _agent is None:
        logger.info("Initializing PrismIQAgent...")
        from src.agent.tools import ALL_TOOLS

        _agent = PrismIQAgent(tools=ALL_TOOLS)
        logger.info("PrismIQAgent initialized successfully")

    return _agent


def reset_agent() -> None:
    """Reset the singleton agent instance.

    Useful for testing or when configuration changes.
    """
    global _agent
    _agent = None
    logger.info("Agent instance reset")
