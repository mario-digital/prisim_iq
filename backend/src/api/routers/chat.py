"""Chat endpoint router for PrismIQ agent interactions."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from src.agent.agent import PrismIQAgent, get_agent
from src.config import get_settings
from src.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chat"])


def get_agent_dependency() -> PrismIQAgent:
    """Dependency that provides the PrismIQ agent.

    Returns:
        PrismIQAgent instance.

    Raises:
        HTTPException: If OpenAI API key is not configured or agent fails to initialize.

    Note:
        Settings are cached via @lru_cache in get_settings(), so this check is
        efficient even when called repeatedly. We use HTTP 503 (Service Unavailable)
        rather than 401/403 because this is a server configuration issue, not a
        client authentication issue - the service cannot function without the key.
    """
    settings = get_settings()  # Cached via @lru_cache

    if not settings.openai_api_key:
        logger.error("OpenAI API key not configured")
        # 503: Service is unavailable due to missing configuration (not client auth)
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
    response_model=ChatResponse,
    summary="Chat with PrismIQ Agent",
    description="""
    Send a natural language message to the PrismIQ pricing copilot.

    The agent will:
    1. Analyze your query to determine which tools to use
    2. Execute relevant tools with the provided market context
    3. Generate a natural language response incorporating tool results

    **Available capabilities:**
    - Price optimization recommendations
    - Explanation of pricing decisions
    - Sensitivity analysis
    - Market segment classification
    - Dataset statistics
    - External context (weather, events)
    - Model documentation and evidence
    - Honeywell enterprise mapping

    **Example queries:**
    - "What's the optimal price for this context?"
    - "Why was this price recommended?"
    - "How stable is this recommendation?"
    - "What segment does this context belong to?"
    - "Tell me about the models used"
    """,
    responses={
        200: {"description": "Successful response from agent"},
        422: {"description": "Validation error - invalid input data"},
        503: {"description": "Chat service unavailable - API key not configured"},
    },
)
async def chat(
    request: ChatRequest,
    agent: AgentDep,
) -> ChatResponse:
    """Process a chat message and return agent response.

    Args:
        request: Chat request with message and market context.
        agent: Injected PrismIQ agent instance.

    Returns:
        ChatResponse with agent's message and metadata.
    """
    logger.info(
        f"Chat request: message='{request.message[:50]}...', "
        f"session_id={request.session_id}"
    )

    try:
        result = await agent.chat(
            message=request.message,
            context=request.context,
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
        # Return error in response rather than raising HTTPException
        # to maintain structured response format
        return ChatResponse(
            message=f"I encountered an error: {str(e)}",
            tools_used=[],
            context=request.context.model_dump(),
            error=str(e),
        )


@router.post(
    "/clear",
    summary="Clear Chat Memory",
    description="Clear the conversation memory for a fresh session.",
    responses={
        200: {"description": "Memory cleared successfully"},
        503: {"description": "Chat service unavailable"},
    },
)
async def clear_memory(agent: AgentDep) -> dict[str, str]:
    """Clear the agent's conversation memory.

    Args:
        agent: Injected PrismIQ agent instance.

    Returns:
        Success message.
    """
    agent.clear_memory()
    logger.info("Chat memory cleared")
    return {"status": "ok", "message": "Conversation memory cleared"}

