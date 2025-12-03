"""Unit tests for SSE event shape validation.

Validates that SSE events conform to the documented contract:
- Token events: {"token": str, "done": false}
- Tool call events: {"tool_call": str, "done": false}
- Final message events: {"message": str, "tools_used": list, "done": true}
- Error events: {"error": str, "done": true}
"""

import json
from typing import Any
from unittest.mock import MagicMock

import pytest


def validate_token_event(event: dict[str, Any]) -> None:
    """Validate a token SSE event."""
    assert "token" in event, "Token event must have 'token' field"
    assert isinstance(event["token"], str), "Token must be a string"
    assert "done" in event, "Token event must have 'done' field"
    assert event["done"] is False, "Token event 'done' must be False"


def validate_tool_call_event(event: dict[str, Any]) -> None:
    """Validate a tool call SSE event."""
    assert "tool_call" in event, "Tool call event must have 'tool_call' field"
    assert isinstance(event["tool_call"], str), "tool_call must be a string"
    assert "done" in event, "Tool call event must have 'done' field"
    assert event["done"] is False, "Tool call event 'done' must be False"


def validate_final_message_event(event: dict[str, Any]) -> None:
    """Validate a final message SSE event."""
    assert "message" in event, "Final event must have 'message' field"
    assert isinstance(event["message"], str), "message must be a string"
    assert "tools_used" in event, "Final event must have 'tools_used' field"
    assert isinstance(event["tools_used"], list), "tools_used must be a list"
    assert "done" in event, "Final event must have 'done' field"
    assert event["done"] is True, "Final event 'done' must be True"


def validate_error_event(event: dict[str, Any]) -> None:
    """Validate an error SSE event."""
    assert "error" in event, "Error event must have 'error' field"
    assert isinstance(event["error"], str), "error must be a string"
    assert "done" in event, "Error event must have 'done' field"
    assert event["done"] is True, "Error event 'done' must be True"


class TestSSEEventShapes:
    """Test that SSE events conform to the documented contract."""

    def test_token_event_shape(self) -> None:
        """Token events have correct shape."""
        event = {"token": "The ", "done": False}
        validate_token_event(event)

    def test_token_event_rejects_invalid(self) -> None:
        """Token events reject invalid shapes."""
        # Missing token field
        with pytest.raises(AssertionError):
            validate_token_event({"done": False})

        # Token is not string
        with pytest.raises(AssertionError):
            validate_token_event({"token": 123, "done": False})

        # done is True (should be False for tokens)
        with pytest.raises(AssertionError):
            validate_token_event({"token": "x", "done": True})

    def test_tool_call_event_shape(self) -> None:
        """Tool call events have correct shape."""
        event = {"tool_call": "optimize_price", "done": False}
        validate_tool_call_event(event)

    def test_tool_call_event_rejects_invalid(self) -> None:
        """Tool call events reject invalid shapes."""
        # Missing tool_call field
        with pytest.raises(AssertionError):
            validate_tool_call_event({"done": False})

        # tool_call is not string
        with pytest.raises(AssertionError):
            validate_tool_call_event({"tool_call": ["a", "b"], "done": False})

    def test_final_message_event_shape(self) -> None:
        """Final message events have correct shape."""
        event = {
            "message": "The optimal price is $94.50.",
            "tools_used": ["optimize_price"],
            "done": True,
        }
        validate_final_message_event(event)

    def test_final_message_event_empty_tools(self) -> None:
        """Final message events can have empty tools_used list."""
        event = {
            "message": "Hello, how can I help?",
            "tools_used": [],
            "done": True,
        }
        validate_final_message_event(event)

    def test_final_message_event_rejects_invalid(self) -> None:
        """Final message events reject invalid shapes."""
        # Missing message
        with pytest.raises(AssertionError):
            validate_final_message_event({"tools_used": [], "done": True})

        # Missing tools_used
        with pytest.raises(AssertionError):
            validate_final_message_event({"message": "x", "done": True})

        # done is False (should be True for final)
        with pytest.raises(AssertionError):
            validate_final_message_event(
                {"message": "x", "tools_used": [], "done": False}
            )

    def test_error_event_shape(self) -> None:
        """Error events have correct shape."""
        event = {"error": "Rate limit exceeded", "done": True}
        validate_error_event(event)

    def test_error_event_with_optional_fields(self) -> None:
        """Error events can have optional code and retryable fields."""
        event = {
            "error": "Rate limit exceeded",
            "done": True,
            "code": "rate_limit",
            "retryable": True,
        }
        validate_error_event(event)
        # Optional fields are allowed
        assert event.get("code") == "rate_limit"
        assert event.get("retryable") is True

    def test_error_event_rejects_invalid(self) -> None:
        """Error events reject invalid shapes."""
        # Missing error field
        with pytest.raises(AssertionError):
            validate_error_event({"done": True})

        # done is False (should be True for errors)
        with pytest.raises(AssertionError):
            validate_error_event({"error": "fail", "done": False})


def create_test_context():
    """Create a valid MarketContext for testing."""
    from src.schemas.market import MarketContext

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


class TestSSEGeneratorOutput:
    """Test that sse_generator produces valid events."""

    @pytest.mark.asyncio
    async def test_sse_generator_yields_valid_json(self) -> None:
        """SSE generator yields valid JSON data events."""
        # Create a mock agent that yields expected events
        mock_agent = MagicMock()

        async def mock_stream(*_args, **_kwargs):
            yield {"token": "Hello", "done": False}
            yield {"token": " world", "done": False}
            yield {"message": "Hello world", "tools_used": [], "done": True}

        mock_agent.stream_chat = mock_stream

        from src.agent.streaming import sse_generator

        context = create_test_context()

        events = []
        async for event in sse_generator(mock_agent, "test", context, "session"):
            events.append(event)

        assert len(events) == 3

        # Each event should have "data" key with JSON
        for event in events:
            assert "data" in event
            parsed = json.loads(event["data"])
            assert "done" in parsed

    @pytest.mark.asyncio
    async def test_sse_generator_token_events_valid(self) -> None:
        """SSE generator token events are valid."""
        mock_agent = MagicMock()

        async def mock_stream(*_args, **_kwargs):
            yield {"token": "Test", "done": False}
            yield {"message": "Test", "tools_used": [], "done": True}

        mock_agent.stream_chat = mock_stream

        from src.agent.streaming import sse_generator

        context = create_test_context()

        events = []
        async for event in sse_generator(mock_agent, "test", context, "session"):
            events.append(json.loads(event["data"]))

        # First event is token
        validate_token_event(events[0])

    @pytest.mark.asyncio
    async def test_sse_generator_tool_call_events_valid(self) -> None:
        """SSE generator tool call events are valid."""
        mock_agent = MagicMock()

        async def mock_stream(*_args, **_kwargs):
            yield {"tool_call": "optimize_price", "done": False}
            yield {"message": "Done", "tools_used": ["optimize_price"], "done": True}

        mock_agent.stream_chat = mock_stream

        from src.agent.streaming import sse_generator

        context = create_test_context()

        events = []
        async for event in sse_generator(mock_agent, "test", context, "session"):
            events.append(json.loads(event["data"]))

        # First event is tool call
        validate_tool_call_event(events[0])

    @pytest.mark.asyncio
    async def test_sse_generator_final_event_valid(self) -> None:
        """SSE generator final message events are valid."""
        mock_agent = MagicMock()

        async def mock_stream(*_args, **_kwargs):
            yield {"message": "Final answer", "tools_used": ["tool1"], "done": True}

        mock_agent.stream_chat = mock_stream

        from src.agent.streaming import sse_generator

        context = create_test_context()

        events = []
        async for event in sse_generator(mock_agent, "test", context, "session"):
            events.append(json.loads(event["data"]))

        validate_final_message_event(events[0])

    @pytest.mark.asyncio
    async def test_sse_generator_error_event_valid(self) -> None:
        """SSE generator handles errors and produces valid error events."""
        mock_agent = MagicMock()

        async def mock_stream(*_args, **_kwargs):
            raise RuntimeError("Test error")
            yield  # Make it a generator

        mock_agent.stream_chat = mock_stream

        from src.agent.streaming import sse_generator

        context = create_test_context()

        events = []
        async for event in sse_generator(mock_agent, "test", context, "session"):
            events.append(json.loads(event["data"]))

        assert len(events) == 1
        validate_error_event(events[0])


class TestSSEKeepaliveGenerator:
    """Test the keepalive generator variant."""

    @pytest.mark.asyncio
    async def test_keepalive_generator_yields_valid_events(self) -> None:
        """Keepalive generator yields valid events like standard generator."""
        mock_agent = MagicMock()

        async def mock_stream(*_args, **_kwargs):
            yield {"token": "Hi", "done": False}
            yield {"message": "Hi", "tools_used": [], "done": True}

        mock_agent.stream_chat = mock_stream

        from src.agent.streaming import sse_keepalive_generator

        context = create_test_context()

        events = []
        async for event in sse_keepalive_generator(
            mock_agent, "test", context, "session", keepalive_interval=15.0
        ):
            events.append(event)

        # Should have same events as standard generator
        assert len(events) == 2
        for event in events:
            assert "data" in event


class TestGoldenSamples:
    """Test against golden sample events from the story documentation."""

    def test_golden_token_event(self) -> None:
        """Golden sample: data: {"token":"The","done":false}"""
        raw = '{"token":"The","done":false}'
        event = json.loads(raw)
        validate_token_event(event)

    def test_golden_tool_call_event(self) -> None:
        """Golden sample: data: {"tool_call":"optimize_price","done":false}"""
        raw = '{"tool_call":"optimize_price","done":false}'
        event = json.loads(raw)
        validate_tool_call_event(event)

    def test_golden_final_event(self) -> None:
        """Golden sample: data: {"message":"The optimal price is $94.50.","tools_used":["optimize_price"],"done":true}"""
        raw = '{"message":"The optimal price is $94.50.","tools_used":["optimize_price"],"done":true}'
        event = json.loads(raw)
        validate_final_message_event(event)

    def test_golden_error_event(self) -> None:
        """Golden sample: data: {"error":"Rate limit exceeded","code":"rate_limit","retryable":true,"done":true}"""
        raw = '{"error":"Rate limit exceeded","code":"rate_limit","retryable":true,"done":true}'
        event = json.loads(raw)
        validate_error_event(event)

