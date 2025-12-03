"""PrismIQ LangChain Agent for intelligent pricing copilot interactions.

This module implements the main agent that orchestrates tool usage,
maintains conversation memory, and generates natural language responses.
"""

from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool

    from src.schemas.market import MarketContext


class PrismIQAgent:
    """LangChain-based agent for pricing copilot interactions.

    Orchestrates:
    - Tool selection based on user queries
    - Conversation memory for context continuity
    - Natural language response generation
    """

    def __init__(self, tools: list[BaseTool]) -> None:
        """Initialize the PrismIQ agent.

        Args:
            tools: List of LangChain tools available to the agent.
        """
        # Defer imports to avoid loading LangChain unless agent is used
        from langchain.agents import AgentExecutor, create_openai_functions_agent
        from langchain.memory import ConversationBufferMemory
        from langchain_openai import ChatOpenAI

        from src.agent.prompts import create_prompt
        from src.config import get_settings

        settings = get_settings()

        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=settings.openai_api_key,
        )

        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
        )

        self.tools = tools

        # Create the agent with tools and prompt
        prompt = create_prompt()
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt,
        )

        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
        )

        logger.info(
            f"PrismIQAgent initialized with {len(tools)} tools: "
            f"{[t.name for t in tools]}"
        )

    async def chat(
        self,
        message: str,
        context: MarketContext,
    ) -> dict:
        """Process a chat message and return agent response.

        Args:
            message: User's natural language query.
            context: Current market context for tool execution.

        Returns:
            Dictionary with response message, tools used, and metadata.
        """
        from src.agent.context import set_current_context

        start_time = datetime.now()

        # Store context for tools to access
        set_current_context(context)

        logger.info(f"Processing chat: '{message[:100]}...' with context")

        try:
            # Invoke the agent
            result = await self.executor.ainvoke({"input": message})

            # Extract tools used from intermediate steps
            tools_used = []
            if "intermediate_steps" in result:
                for step in result["intermediate_steps"]:
                    if hasattr(step, "__getitem__") and len(step) > 0:
                        action = step[0]
                        if hasattr(action, "tool"):
                            tools_used.append(action.tool)

            response = {
                "message": result.get("output", ""),
                "tools_used": tools_used,
                "context": context.model_dump(),
                "timestamp": datetime.now().isoformat(),
                "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
            }

            logger.info(
                f"Chat complete: tools_used={tools_used}, "
                f"time={response['processing_time_ms']:.1f}ms"
            )

            return response

        except Exception as e:
            logger.error(f"Agent chat error: {e}", exc_info=True)
            return {
                "message": f"I encountered an error processing your request: {str(e)}",
                "tools_used": [],
                "context": context.model_dump(),
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            }

    def clear_memory(self) -> None:
        """Clear conversation memory for a fresh session."""
        self.memory.clear()
        logger.info("Agent memory cleared")


# Singleton agent instance
_agent: PrismIQAgent | None = None


@lru_cache(maxsize=1)
def _create_tools() -> tuple:
    """Create and cache all tools for the agent.

    Returns tuple for hashability with lru_cache.
    """
    from src.agent.tools import (
        create_explain_decision_tool,
        create_get_eda_summary_tool,
        create_get_evidence_tool,
        create_get_external_context_tool,
        create_get_honeywell_mapping_tool,
        create_get_segment_tool,
        create_optimize_price_tool,
        create_sensitivity_tool,
    )

    logger.info("Creating agent tools...")

    tools = [
        create_optimize_price_tool(),
        create_explain_decision_tool(),
        create_sensitivity_tool(),
        create_get_segment_tool(),
        create_get_eda_summary_tool(),
        create_get_external_context_tool(),
        create_get_evidence_tool(),
        create_get_honeywell_mapping_tool(),
    ]

    logger.info(f"Created {len(tools)} tools")
    return tuple(tools)


def get_agent() -> PrismIQAgent:
    """Get or create singleton PrismIQAgent instance.

    Returns:
        PrismIQAgent instance with all tools configured.
    """
    global _agent

    if _agent is None:
        logger.info("Initializing PrismIQAgent...")
        tools = list(_create_tools())
        _agent = PrismIQAgent(tools=tools)
        logger.info("PrismIQAgent initialized successfully")

    return _agent

