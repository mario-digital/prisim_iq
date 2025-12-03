"""Utility functions for the PrismIQ agent.

This module provides helpers for running async code in sync contexts
and sanitizing error messages.

Known Limitations:
    - run_sync() uses ThreadPoolExecutor when event loop is running, which
      may have performance implications in high-throughput scenarios.
    - For Python 3.12+, asyncio APIs are evolving; monitor for changes.

Future Improvements (TODO):
    - Consider using nest_asyncio for cleaner nested loop handling
    - Evaluate fully async tool execution when LangChain supports it
    - Profile ThreadPoolExecutor overhead in production workloads
"""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any, TypeVar

from loguru import logger

T = TypeVar("T")


def run_sync(coro: Coroutine[Any, Any, T]) -> T:
    """Run an async coroutine in a sync context safely.

    This function handles the case where an event loop may or may not
    already be running. It's designed to work in various contexts:
    - Standard Python scripts (no event loop)
    - Jupyter notebooks (event loop running)
    - FastAPI/Uvicorn (event loop may be running)

    Args:
        coro: The coroutine to execute.

    Returns:
        The result of the coroutine.

    Note:
        For Python 3.10+, this uses asyncio.run() when no loop is running,
        which is the recommended approach. When a loop is already running,
        it creates a new loop in a thread-safe manner using ThreadPoolExecutor.

    Warning:
        The ThreadPoolExecutor fallback introduces a thread context switch
        which may have performance implications. For high-throughput scenarios,
        consider:
        1. Using nest_asyncio library for cleaner nested loop handling
        2. Refactoring to fully async execution path
        3. Ensuring tools are called from non-async context when possible

    TODO:
        - Evaluate nest_asyncio as alternative for nested event loops
        - Monitor Python 3.12+ asyncio changes for compatibility
        - Consider async tool support when LangChain adds it
    """
    try:
        # Check if there's already a running event loop
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop - use asyncio.run() (Python 3.7+ recommended approach)
        return asyncio.run(coro)

    # Loop is already running - we need an alternative approach
    # This can happen in Jupyter, some test frameworks, or nested async contexts
    #
    # WARNING: This uses ThreadPoolExecutor which has overhead. For production
    # high-throughput scenarios, consider nest_asyncio or fully async execution.
    import concurrent.futures

    logger.debug("Event loop already running, using thread executor")

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, coro)
        return future.result()


def sanitize_error_message(error: Exception) -> str:
    """Sanitize an error message for user-facing responses.

    Removes potentially sensitive information like file paths,
    stack traces, and internal error details.

    Args:
        error: The exception to sanitize.

    Returns:
        A user-friendly error message.
    """
    error_str = str(error)

    # Map known internal errors to user-friendly messages
    error_mappings = {
        "No market context available": "Please provide market context to analyze.",
        "FileNotFoundError": "Required data or model file not found.",
        "ConnectionError": "Unable to connect to required service.",
        "TimeoutError": "The request timed out. Please try again.",
        "ValidationError": "Invalid input data provided.",
    }

    for pattern, friendly_message in error_mappings.items():
        if pattern in error_str:
            return friendly_message

    # For unrecognized errors, return a generic message
    # Log the full error for debugging
    error_type = type(error).__name__

    # Return type-based generic messages
    if "permission" in error_str.lower() or "access" in error_str.lower():
        return "Access denied to required resource."
    if "connect" in error_str.lower() or "network" in error_str.lower():
        return "Network connectivity issue encountered."
    if "timeout" in error_str.lower():
        return "Operation timed out. Please try again."

    # Default: return the error type without internal details
    return f"An error occurred ({error_type}). Please try again or contact support."
