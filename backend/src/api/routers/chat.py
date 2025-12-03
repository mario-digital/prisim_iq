"""Chat endpoint router for PrismIQ agent interactions with SSE streaming support."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sse_starlette.sse import EventSourceResponse

from src.agent.agent import PrismIQAgent, get_agent
from src.agent.streaming import sse_generator
from src.config import get_settings
from src.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chat"])


def get_agent_dependency() -> PrismIQAgent:
    """Dependency that provides the PrismIQ agent.

    Returns:
        PrismIQAgent instance.

    Raises:
        HTTPException: If OpenAI API key is not configured or agent fails to initialize.
    """
    settings = get_settings()

    if not settings.openai_api_key:
        logger.error("OpenAI API key not configured")
        raise HTTPException(
            status_code=503,
            detail="Chat service unavailable: OpenAI API key not configured. "
            "Set OPENAI_API_KEY environment variable.",
        )

    try:
        return get_agent()
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Chat service unavailable: {str(e)}",
        ) from e


AgentDep = Annotated[PrismIQAgent, Depends(get_agent_dependency)]


@router.post(
    "",
    summary="Chat with PrismIQ Agent",
    description="""
    Send a natural language message to the PrismIQ pricing copilot.

    ## Streaming Mode (Default)

    When `stream=true` (default), returns Server-Sent Events (SSE):
    - `Content-Type: text/event-stream`
    - Events are JSON objects with `token`, `tool_call`, `message`, or `error` fields
    - Stream ends with `{"done": true}`

    ## Non-Streaming Mode

    When `stream=false`, returns a single JSON response with the complete message.

    ## Capabilities

    The agent can:
    - Optimize prices with ML models
    - Explain pricing decisions with SHAP values
    - Run sensitivity analysis
    - Classify market segments
    - Provide dataset statistics
    - Fetch external context (weather, events)
    - Access model documentation

    ## Example Queries

    - "What's the optimal price for this context?"
    - "Why was this price recommended?"
    - "How stable is this recommendation?"
    - "What segment does this context belong to?"

    ## SSE Event Format

    ```
    data: {"token": "The ", "done": false}
    data: {"tool_call": "optimize_price", "done": false}
    data: {"token": "optimal price is $24.50", "done": false}
    data: {"message": "The optimal price is $24.50...", "tools_used": ["optimize_price"], "done": true}
    ```
    """,
    responses={
        200: {
            "description": "Successful response from agent",
            "content": {
                "text/event-stream": {
                    "example": 'data: {"token": "The ", "done": false}\n\ndata: {"message": "...", "done": true}\n\n'
                },
                "application/json": {
                    "example": {
                        "message": "The optimal price is $42.50...",
                        "tools_used": ["optimize_price"],
                        "context": {},
                        "timestamp": "2024-12-02T10:30:00Z",
                    }
                },
            },
        },
        422: {"description": "Validation error - invalid input data"},
        503: {"description": "Chat service unavailable - API key not configured"},
    },
)
async def chat(
    request: ChatRequest,
    agent: AgentDep,
    stream: bool = Query(
        True,
        description="Enable streaming response (SSE). Set to false for single JSON response.",
    ),
):
    """Process a chat message with optional streaming.

    Args:
        request: Chat request with message and market context.
        agent: Injected PrismIQ agent instance.
        stream: If True, return SSE stream. If False, return JSON.

    Returns:
        EventSourceResponse for streaming, or ChatResponse for non-streaming.
    """
    session_id = request.session_id or "default"

    logger.info(
        f"Chat request: message='{request.message[:50]}...', "
        f"session_id={session_id}, stream={stream}"
    )

    if stream:
        # Return SSE streaming response
        return EventSourceResponse(
            sse_generator(
                agent=agent,
                message=request.message,
                context=request.context,
                session_id=session_id,
            ),
            media_type="text/event-stream",
        )
    else:
        # Non-streaming fallback
        try:
            result = await agent.chat(
                message=request.message,
                context=request.context,
                session_id=session_id,
            )

            return ChatResponse(
                message=result["message"],
                tools_used=result.get("tools_used", []),
                context=result.get("context", request.context.model_dump()),
                processing_time_ms=result.get("processing_time_ms"),
                error=result.get("error"),
            )

        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            return ChatResponse(
                message=f"I encountered an error: {str(e)}",
                tools_used=[],
                context=request.context.model_dump(),
                error=str(e),
            )


@router.post(
    "/clear",
    summary="Clear Chat Memory",
    description="Clear the conversation memory for a session.",
    responses={
        200: {"description": "Memory cleared successfully"},
        503: {"description": "Chat service unavailable"},
    },
)
async def clear_memory(
    agent: AgentDep,
    session_id: str = Query(
        "default",
        description="Session ID to clear memory for",
    ),
) -> dict[str, str]:
    """Clear the agent's conversation memory for a session.

    Args:
        agent: Injected PrismIQ agent instance.
        session_id: Session ID to clear memory for.

    Returns:
        Success message.
    """
    agent.clear_memory(session_id)
    logger.info(f"Chat memory cleared for session: {session_id}")
    return {"status": "ok", "message": f"Conversation memory cleared for session: {session_id}"}
