"""PrismIQ LangChain Agent module for intelligent chat interactions.

Implements a LangChain v1.1 tool-calling agent with streaming support.
"""

from src.agent.agent import PrismIQAgent, get_agent, reset_agent
from src.agent.streaming import sse_generator, sse_keepalive_generator
from src.agent.utils import run_sync, sanitize_error_message

__all__ = [
    "PrismIQAgent",
    "get_agent",
    "reset_agent",
    "run_sync",
    "sanitize_error_message",
    "sse_generator",
    "sse_keepalive_generator",
]
