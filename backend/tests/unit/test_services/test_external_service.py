"""Tests for external data integration service."""

from __future__ import annotations

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.schemas.external import (
    EventData,
    ExternalContext,
)
from src.services.external_service import (
    CACHE_TTL,
    EVENT_MODIFIERS,
    WEATHER_MODIFIERS,
    ExternalDataService,
    get_external_service,
)


@pytest.fixture
def temp_cache_dir() -> Path:
    """Create temporary cache directory for tests."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def external_service(temp_cache_dir: Path) -> ExternalDataService:
    """Create external data service with temp cache directory."""
    return ExternalDataService(cache_dir=temp_cache_dir)


class TestCacheConfiguration:
    """Tests for cache configuration constants."""

    def test_weather_ttl_is_30_minutes(self) -> None:
        """Verify weather cache TTL is 30 minutes (AC: 6)."""
        assert CACHE_TTL["weather"] == timedelta(minutes=30)

    def test_events_ttl_is_1_hour(self) -> None:
        """Verify events cache TTL is 1 hour (AC: 6)."""
        assert CACHE_TTL["events"] == timedelta(hours=1)

    def test_fuel_ttl_is_1_hour(self) -> None:
        """Verify fuel cache TTL is 1 hour (AC: 6)."""
        assert CACHE_TTL["fuel"] == timedelta(hours=1)


class TestWeatherModifiers:
    """Tests for weather condition to demand modifier mapping."""

    def test_sunny_modifier(self) -> None:
        """Sunny weather has baseline modifier."""
        assert WEATHER_MODIFIERS["sunny"] == 1.0

    def test_cloudy_modifier(self) -> None:
        """Cloudy weather has baseline modifier."""
        assert WEATHER_MODIFIERS["cloudy"] == 1.0

    def test_rainy_modifier(self) -> None:
        """Rainy weather increases demand by 15% (AC: 3)."""
        assert WEATHER_MODIFIERS["rainy"] == 1.15

    def test_snowy_modifier(self) -> None:
        """Snowy weather increases demand by 30% (AC: 3)."""
        assert WEATHER_MODIFIERS["snowy"] == 1.30


class TestEventModifiers:
    """Tests for event type to surge modifier mapping."""

    def test_concert_modifier(self) -> None:
        """Concert events add 20% surge (AC: 4)."""
        assert EVENT_MODIFIERS["concert"] == 1.20

    def test_sports_modifier(self) -> None:
        """Sports events add 25% surge (AC: 4)."""
        assert EVENT_MODIFIERS["sports"] == 1.25

    def test_convention_modifier(self) -> None:
        """Convention events add 15% surge (AC: 4)."""
        assert EVENT_MODIFIERS["convention"] == 1.15

    def test_other_modifier(self) -> None:
        """Other events add 10% surge."""
        assert EVENT_MODIFIERS["other"] == 1.10


class TestCaching:
    """Tests for caching layer functionality."""

    def test_cache_directory_created(self, temp_cache_dir: Path) -> None:
        """Cache directory is created on service init."""
        _service = ExternalDataService(cache_dir=temp_cache_dir / "new_cache")
        assert (temp_cache_dir / "new_cache").exists()

    def test_cache_miss_returns_none(self, external_service: ExternalDataService) -> None:
        """Cache miss returns None from internal read method."""
        result = external_service._read_cache("fuel")
        assert result is None

    def test_cache_write_and_read(self, external_service: ExternalDataService) -> None:
        """Cache can be written and read back."""
        test_data = {"price_per_gallon": 3.75, "change_percent": 2.5}
        external_service._write_cache("fuel", test_data)

        result = external_service._read_cache("fuel")
        assert result is not None
        assert result["price_per_gallon"] == 3.75
        assert result["change_percent"] == 2.5

    def test_cache_expiration(
        self, external_service: ExternalDataService, temp_cache_dir: Path
    ) -> None:
        """Expired cache returns None."""
        # Write cache with old timestamp
        cache_path = temp_cache_dir / "weather_cache.json"
        old_time = datetime.utcnow() - timedelta(hours=2)  # Expired
        cache_data = {
            "condition": "rainy",
            "temperature_f": 65.0,
            "demand_modifier": 1.15,
            "cached_at": old_time.isoformat(),
        }
        with open(cache_path, "w") as f:
            json.dump(cache_data, f)

        result = external_service._read_cache("weather")
        assert result is None  # Expired

    def test_cache_freshness_check(self, external_service: ExternalDataService) -> None:
        """Cache freshness check works correctly."""
        # No cache = not fresh
        assert not external_service._is_cache_fresh("fuel")

        # Write fresh cache
        external_service._write_cache("fuel", {"price_per_gallon": 3.50})
        assert external_service._is_cache_fresh("fuel")

    def test_cache_age_seconds(self, external_service: ExternalDataService) -> None:
        """Cache age is calculated correctly."""
        # No cache = None
        assert external_service._get_cache_age_seconds("fuel") is None

        # Write cache and check age
        external_service._write_cache("fuel", {"price_per_gallon": 3.50})
        age = external_service._get_cache_age_seconds("fuel")
        assert age is not None
        assert 0 <= age <= 2  # Should be very recent


class TestMockData:
    """Tests for mock/fallback data."""

    def test_mock_fuel_data(self, external_service: ExternalDataService) -> None:
        """Mock fuel data has neutral values."""
        mock = external_service._get_mock_fuel_data()
        assert mock.price_per_gallon == 3.50
        assert mock.change_percent == 0.0
        assert mock.source == "mock"

    def test_mock_weather_data(self, external_service: ExternalDataService) -> None:
        """Mock weather data is cloudy with 1.0 modifier (AC: fallback)."""
        mock = external_service._get_mock_weather_data()
        assert mock.condition == "cloudy"
        assert mock.demand_modifier == 1.0
        assert mock.source == "mock"

    def test_mock_events_data(self, external_service: ExternalDataService) -> None:
        """Mock events data is empty list (AC: fallback)."""
        mock = external_service._get_mock_events_data()
        assert mock == []


class TestWebhookHandlers:
    """Tests for webhook handlers that receive n8n data."""

    def test_fuel_webhook_handler(self, external_service: ExternalDataService) -> None:
        """Fuel webhook processes data correctly (AC: 2)."""
        data = {
            "price_per_gallon": 3.89,
            "change_percent": 3.5,
            "source": "test",
        }
        result = external_service.handle_fuel_webhook(data)

        assert result.price_per_gallon == 3.89
        assert result.change_percent == 3.5
        assert result.source == "test"

    def test_fuel_webhook_caches_data(self, external_service: ExternalDataService) -> None:
        """Fuel webhook caches received data."""
        data = {"price_per_gallon": 3.99, "change_percent": 5.0}
        external_service.handle_fuel_webhook(data)

        # Should be cached
        cached = external_service.get_fuel_data()
        assert cached.price_per_gallon == 3.99

    def test_weather_webhook_handler(self, external_service: ExternalDataService) -> None:
        """Weather webhook processes and calculates modifier (AC: 3)."""
        data = {"condition": "rainy", "temperature_f": 55.0}
        result = external_service.handle_weather_webhook(data)

        assert result.condition == "rainy"
        assert result.temperature_f == 55.0
        assert result.demand_modifier == 1.15  # Rainy = +15%

    def test_weather_webhook_unknown_condition_fallback(
        self, external_service: ExternalDataService
    ) -> None:
        """Unknown weather condition falls back to cloudy."""
        data = {"condition": "foggy", "temperature_f": 60.0}
        result = external_service.handle_weather_webhook(data)

        assert result.condition == "cloudy"
        assert result.demand_modifier == 1.0

    def test_events_webhook_handler(self, external_service: ExternalDataService) -> None:
        """Events webhook processes list of events (AC: 4)."""
        data = {
            "events": [
                {
                    "name": "Rock Concert",
                    "type": "concert",
                    "venue": "City Arena",
                    "start_time": "2024-12-15T19:00:00",
                },
                {
                    "name": "Football Game",
                    "type": "sports",
                    "venue": "Stadium",
                    "start_time": "2024-12-15T18:00:00",
                },
            ]
        }
        result = external_service.handle_events_webhook(data)

        assert len(result) == 2
        assert result[0].name == "Rock Concert"
        assert result[0].surge_modifier == 1.20  # Concert
        assert result[1].name == "Football Game"
        assert result[1].surge_modifier == 1.25  # Sports

    def test_events_webhook_empty_list(self, external_service: ExternalDataService) -> None:
        """Events webhook handles empty event list."""
        data = {"events": []}
        result = external_service.handle_events_webhook(data)
        assert result == []


class TestDataRetrieval:
    """Tests for data retrieval with caching and fallback."""

    def test_get_fuel_data_returns_mock_when_no_cache(
        self, external_service: ExternalDataService
    ) -> None:
        """Fuel data falls back to mock when no cache."""
        result = external_service.get_fuel_data()
        assert result.source == "mock"
        assert result.price_per_gallon == 3.50

    def test_get_weather_data_returns_mock_when_no_cache(
        self, external_service: ExternalDataService
    ) -> None:
        """Weather data falls back to mock when no cache."""
        result = external_service.get_weather_data()
        assert result.source == "mock"
        assert result.condition == "cloudy"

    def test_get_events_data_returns_empty_when_no_cache(
        self, external_service: ExternalDataService
    ) -> None:
        """Events data falls back to empty list when no cache."""
        result = external_service.get_events_data()
        assert result == []

    def test_get_external_context_aggregates_all_data(
        self, external_service: ExternalDataService
    ) -> None:
        """External context aggregates fuel, weather, and events (AC: 8)."""
        # Add some data
        external_service.handle_weather_webhook({"condition": "rainy", "temperature_f": 60.0})

        context = external_service.get_external_context()

        assert context.fuel is not None
        assert context.weather is not None
        assert context.weather.condition == "rainy"
        assert isinstance(context.events, list)


class TestExplanationGeneration:
    """Tests for natural language explanation generation."""

    def test_weather_explanation_rainy(self, external_service: ExternalDataService) -> None:
        """Rainy weather explanation mentions +15% demand (AC: 9)."""
        external_service.handle_weather_webhook({"condition": "rainy", "temperature_f": 65.0})
        context = external_service.get_external_context()
        explanation = external_service.generate_explanation(context)

        assert "rainy" in explanation.lower()
        assert "15%" in explanation

    def test_weather_explanation_snowy(self, external_service: ExternalDataService) -> None:
        """Snowy weather explanation mentions +30% demand (AC: 9)."""
        external_service.handle_weather_webhook({"condition": "snowy", "temperature_f": 32.0})
        context = external_service.get_external_context()
        explanation = external_service.generate_explanation(context)

        assert "snowy" in explanation.lower()
        assert "30%" in explanation

    def test_event_explanation(self, external_service: ExternalDataService) -> None:
        """Event explanation mentions surge factor (AC: 9)."""
        external_service.handle_events_webhook(
            {
                "events": [
                    {
                        "name": "Taylor Swift Concert",
                        "type": "concert",
                        "venue": "Arena",
                        "start_time": "2024-12-15T19:00:00",
                    }
                ]
            }
        )
        context = external_service.get_external_context()
        explanation = external_service.generate_explanation(context)

        assert "Taylor Swift Concert" in explanation
        assert "concert" in explanation.lower()
        assert "20%" in explanation

    def test_no_factors_explanation(self, external_service: ExternalDataService) -> None:
        """No significant factors returns neutral explanation."""
        # Mock data has neutral values
        context = external_service.get_external_context()
        explanation = external_service.generate_explanation(context)

        assert "no significant" in explanation.lower() or "cloudy" in explanation.lower()


class TestExternalContextResponse:
    """Tests for API response generation."""

    def test_response_includes_cache_status(self, external_service: ExternalDataService) -> None:
        """Response includes cache freshness info (AC: 8)."""
        response = external_service.get_external_context_response()

        assert "fuel" in response.cache_status
        assert "weather" in response.cache_status
        assert "events" in response.cache_status

        for status in response.cache_status.values():
            assert "age_seconds" in status
            assert "is_fresh" in status

    def test_response_includes_explanation(self, external_service: ExternalDataService) -> None:
        """Response includes natural language explanation (AC: 8)."""
        response = external_service.get_external_context_response()

        assert response.explanation is not None
        assert len(response.explanation) > 0


class TestExternalContextModel:
    """Tests for ExternalContext model functionality."""

    def test_combined_event_modifier_no_events(self) -> None:
        """Combined modifier is 1.0 with no events."""
        context = ExternalContext()
        assert context.get_combined_event_modifier() == 1.0

    def test_combined_event_modifier_single_event(self) -> None:
        """Combined modifier equals single event modifier."""
        context = ExternalContext(
            events=[
                EventData(
                    name="Concert",
                    type="concert",
                    venue="Arena",
                    start_time=datetime.utcnow(),
                    surge_modifier=1.20,
                )
            ]
        )
        assert context.get_combined_event_modifier() == 1.20

    def test_combined_event_modifier_multiple_events(self) -> None:
        """Combined modifier multiplies all event modifiers."""
        context = ExternalContext(
            events=[
                EventData(
                    name="Concert",
                    type="concert",
                    venue="Arena",
                    start_time=datetime.utcnow(),
                    surge_modifier=1.20,
                ),
                EventData(
                    name="Game",
                    type="sports",
                    venue="Stadium",
                    start_time=datetime.utcnow(),
                    surge_modifier=1.25,
                ),
            ]
        )
        # 1.20 * 1.25 = 1.50
        assert context.get_combined_event_modifier() == pytest.approx(1.50, rel=0.01)


class TestModuleSingleton:
    """Tests for module-level singleton."""

    def test_get_external_service_returns_singleton(self) -> None:
        """get_external_service returns same instance."""
        # Reset singleton for test
        import src.services.external_service as module

        module._service = None

        service1 = get_external_service()
        service2 = get_external_service()

        assert service1 is service2
