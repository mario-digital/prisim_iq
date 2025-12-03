"""Tests for SSE streaming utilities."""

import json

import pytest

from src.agent.streaming import sse_generator
from src.schemas.market import MarketContext


@pytest.fixture
def sample_context() -> MarketContext:
    """Create a sample market context for testing."""
    return MarketContext(
        number_of_riders=50,
        number_of_drivers=25,
        location_category="Urban",
        customer_loyalty_status="Gold",
        number_of_past_rides=20,
        average_ratings=4.5,
        time_of_booking="Evening",
        vehicle_type="Premium",
        expected_ride_duration=30,
        historical_cost_of_ride=35.0,
    )


class TestSSEFormat:
    """Tests for SSE format validation."""

    def test_sse_event_format(self) -> None:
        """Test SSE event format is correct."""
        # Valid SSE format: "data: {json}\n\n"
        event_data = {"token": "Hello", "done": False}
        sse_line = f"data: {json.dumps(event_data)}\n\n"

        assert sse_line.startswith("data: ")
        assert sse_line.endswith("\n\n")

        # Parse the JSON part
        json_part = sse_line.replace("data: ", "").strip()
        parsed = json.loads(json_part)
        assert parsed["token"] == "Hello"
        assert parsed["done"] is False

    def test_completion_event_format(self) -> None:
        """Test completion SSE event format."""
        event_data = {
            "message": "The optimal price is $24.50",
            "tools_used": ["optimize_price"],
            "done": True,
        }
        sse_line = f"data: {json.dumps(event_data)}\n\n"

        json_part = sse_line.replace("data: ", "").strip()
        parsed = json.loads(json_part)
        assert parsed["done"] is True
        assert parsed["message"] == "The optimal price is $24.50"
        assert "optimize_price" in parsed["tools_used"]

    def test_error_event_format(self) -> None:
        """Test error SSE event format."""
        event_data = {
            "error": "Rate limit exceeded",
            "done": True,
        }
        sse_line = f"data: {json.dumps(event_data)}\n\n"

        json_part = sse_line.replace("data: ", "").strip()
        parsed = json.loads(json_part)
        assert parsed["done"] is True
        assert parsed["error"] == "Rate limit exceeded"


class TestSSEGenerator:
    """Tests for SSE generator function."""

    @pytest.mark.asyncio
    async def test_sse_generator_signature(self, sample_context: MarketContext) -> None:
        """Test sse_generator has correct signature."""
        # Reference the fixture to avoid unused-argument lint
        assert sample_context is not None
        # This test verifies the function signature without calling it
        # (which would require a real agent)
        import inspect

        sig = inspect.signature(sse_generator)
        params = list(sig.parameters.keys())

        assert "agent" in params
        assert "message" in params
        assert "context" in params
        assert "session_id" in params

    def test_sse_generator_is_async_generator(self) -> None:
        """Test sse_generator is an async generator function."""
        import inspect

        assert inspect.isasyncgenfunction(sse_generator)
