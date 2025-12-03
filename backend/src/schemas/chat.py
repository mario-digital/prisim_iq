"""Pydantic schemas for chat endpoint."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from src.schemas.market import MarketContext


def _utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(UTC)


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User's natural language query",
    )
    context: MarketContext = Field(
        ...,
        description="Current market context for tool execution",
    )
    session_id: str | None = Field(
        default=None,
        description=(
            "Optional session ID for conversation continuity. "
            "⚠️ NOTE: Not currently used - all sessions share global memory. "
            "See agent.py TODO for per-session memory implementation."
        ),
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "What is the optimal price for this context?",
                "context": {
                    "number_of_riders": 50,
                    "number_of_drivers": 25,
                    "location_category": "Urban",
                    "customer_loyalty_status": "Gold",
                    "number_of_past_rides": 20,
                    "average_ratings": 4.5,
                    "time_of_booking": "Evening",
                    "vehicle_type": "Premium",
                    "expected_ride_duration": 30,
                    "historical_cost_of_ride": 35.0,
                },
                "session_id": "session-123",
            }
        }
    }


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    message: str = Field(
        ...,
        description="Agent's natural language response",
    )
    tools_used: list[str] = Field(
        default_factory=list,
        description="List of tools invoked to answer the query",
    )
    context: dict = Field(
        ...,
        description="Market context used for the response",
    )
    timestamp: datetime = Field(
        default_factory=_utc_now,
        description="Response timestamp (UTC)",
    )
    processing_time_ms: float | None = Field(
        default=None,
        description="Time taken to process the request in milliseconds",
    )
    error: str | None = Field(
        default=None,
        description="Error message if request failed",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "The optimal price for this context is $42.50 with high confidence...",
                "tools_used": ["optimize_price"],
                "context": {"number_of_riders": 50, "...": "..."},
                "timestamp": "2024-12-02T10:30:00Z",
                "processing_time_ms": 1250.5,
                "error": None,
            }
        }
    }

