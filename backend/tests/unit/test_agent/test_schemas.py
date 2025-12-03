"""Tests for chat schemas including streaming events."""

from datetime import datetime

import pytest

from src.schemas.chat import ChatRequest, ChatResponse, ChatStreamEvent
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


class TestChatRequest:
    """Tests for ChatRequest schema."""

    def test_valid_chat_request(self, sample_context: MarketContext) -> None:
        """Test creating a valid ChatRequest."""
        request = ChatRequest(
            message="What is the optimal price?",
            context=sample_context,
        )

        assert request.message == "What is the optimal price?"
        assert request.context == sample_context
        assert request.session_id is None

    def test_chat_request_with_session_id(self, sample_context: MarketContext) -> None:
        """Test ChatRequest with session ID."""
        request = ChatRequest(
            message="Test message",
            context=sample_context,
            session_id="session-123",
        )

        assert request.session_id == "session-123"

    def test_chat_request_empty_message_fails(self, sample_context: MarketContext) -> None:
        """Test ChatRequest with empty message fails validation."""
        with pytest.raises(ValueError):
            ChatRequest(
                message="",
                context=sample_context,
            )

    def test_chat_request_message_max_length(self, sample_context: MarketContext) -> None:
        """Test ChatRequest message max length validation."""
        # Message at max length should work
        long_message = "x" * 4000
        request = ChatRequest(
            message=long_message,
            context=sample_context,
        )
        assert len(request.message) == 4000

        # Message over max length should fail
        with pytest.raises(ValueError):
            ChatRequest(
                message="x" * 4001,
                context=sample_context,
            )


class TestChatResponse:
    """Tests for ChatResponse schema."""

    def test_valid_chat_response(self) -> None:
        """Test creating a valid ChatResponse."""
        response = ChatResponse(
            message="The optimal price is $42.50",
            tools_used=["optimize_price"],
            context={"number_of_riders": 50},
        )

        assert response.message == "The optimal price is $42.50"
        assert response.tools_used == ["optimize_price"]
        assert response.error is None

    def test_chat_response_with_error(self) -> None:
        """Test ChatResponse with error."""
        response = ChatResponse(
            message="An error occurred",
            tools_used=[],
            context={},
            error="Connection failed",
        )

        assert response.error == "Connection failed"

    def test_chat_response_timestamp(self) -> None:
        """Test ChatResponse has timestamp."""
        response = ChatResponse(
            message="Test",
            tools_used=[],
            context={},
        )

        assert isinstance(response.timestamp, datetime)

    def test_chat_response_processing_time(self) -> None:
        """Test ChatResponse with processing time."""
        response = ChatResponse(
            message="Test",
            tools_used=[],
            context={},
            processing_time_ms=125.5,
        )

        assert response.processing_time_ms == 125.5

    def test_chat_response_multiple_tools(self) -> None:
        """Test ChatResponse with multiple tools used."""
        response = ChatResponse(
            message="Price is $42.50 because...",
            tools_used=["optimize_price", "explain_decision"],
            context={},
        )

        assert len(response.tools_used) == 2
        assert "optimize_price" in response.tools_used
        assert "explain_decision" in response.tools_used


class TestChatStreamEvent:
    """Tests for ChatStreamEvent schema (SSE streaming)."""

    def test_token_event(self) -> None:
        """Test creating a token stream event."""
        event = ChatStreamEvent(
            token="The ",
            done=False,
        )

        assert event.token == "The "
        assert event.done is False
        assert event.message is None
        assert event.tool_call is None
        assert event.error is None

    def test_tool_call_event(self) -> None:
        """Test creating a tool call stream event."""
        event = ChatStreamEvent(
            tool_call="optimize_price",
            done=False,
        )

        assert event.tool_call == "optimize_price"
        assert event.done is False
        assert event.token is None

    def test_completion_event(self) -> None:
        """Test creating a completion stream event."""
        event = ChatStreamEvent(
            message="The optimal price is $24.50",
            tools_used=["optimize_price"],
            done=True,
        )

        assert event.message == "The optimal price is $24.50"
        assert event.tools_used == ["optimize_price"]
        assert event.done is True
        assert event.error is None

    def test_error_event(self) -> None:
        """Test creating an error stream event."""
        event = ChatStreamEvent(
            error="Rate limit exceeded",
            done=True,
        )

        assert event.error == "Rate limit exceeded"
        assert event.done is True
        assert event.message is None

    def test_default_done_is_false(self) -> None:
        """Test that done defaults to False."""
        event = ChatStreamEvent()
        assert event.done is False

    def test_stream_event_serialization(self) -> None:
        """Test stream event can be serialized to JSON."""
        event = ChatStreamEvent(
            token="Hello",
            done=False,
        )

        # Should serialize without error
        json_data = event.model_dump_json()
        assert "token" in json_data
        assert "Hello" in json_data

    def test_completion_event_with_multiple_tools(self) -> None:
        """Test completion event with multiple tools."""
        event = ChatStreamEvent(
            message="Based on the analysis...",
            tools_used=["optimize_price", "explain_decision", "sensitivity_analysis"],
            done=True,
        )

        assert len(event.tools_used) == 3
        assert "optimize_price" in event.tools_used
