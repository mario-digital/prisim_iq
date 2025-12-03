"""Tests for agent context management."""

import pytest

from src.agent.context import clear_current_context, get_current_context, set_current_context
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


class TestContextManagement:
    """Tests for context variable management."""

    def test_set_and_get_context(self, sample_context: MarketContext) -> None:
        """Test setting and getting context."""
        set_current_context(sample_context)
        result = get_current_context()

        assert result == sample_context
        assert result.number_of_riders == 50
        assert result.location_category == "Urban"

        # Cleanup
        clear_current_context()

    def test_get_context_without_setting_raises(self) -> None:
        """Test getting context without setting raises RuntimeError."""
        clear_current_context()

        with pytest.raises(RuntimeError) as exc_info:
            get_current_context()

        assert "No market context available" in str(exc_info.value)

    def test_clear_context(self, sample_context: MarketContext) -> None:
        """Test clearing context."""
        set_current_context(sample_context)
        clear_current_context()

        with pytest.raises(RuntimeError):
            get_current_context()

    def test_context_can_be_overwritten(self, sample_context: MarketContext) -> None:
        """Test that context can be overwritten."""
        set_current_context(sample_context)

        new_context = MarketContext(
            number_of_riders=100,
            number_of_drivers=50,
            location_category="Suburban",
            customer_loyalty_status="Platinum",
            number_of_past_rides=100,
            average_ratings=4.9,
            time_of_booking="Morning",
            vehicle_type="Economy",
            expected_ride_duration=15,
            historical_cost_of_ride=20.0,
        )
        set_current_context(new_context)

        result = get_current_context()
        assert result.number_of_riders == 100
        assert result.location_category == "Suburban"

        # Cleanup
        clear_current_context()

