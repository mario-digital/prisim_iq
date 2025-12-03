"""External data integration service for n8n webhooks.

Manages external data from:
- Fuel prices: Impact cost basis calculations
- Weather conditions: Impact demand modifiers
- Local events: Impact surge factors

Features:
- File-based JSON caching with TTL per data type
- Automatic fallback to mock data when n8n unavailable
- Natural language explanation generation
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from loguru import logger

from src.schemas.external import (
    EventData,
    ExternalContext,
    ExternalContextResponse,
    FuelData,
    WeatherData,
)

# Cache configuration
CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "cache"
CACHE_FILES = {
    "fuel": "fuel_cache.json",
    "weather": "weather_cache.json",
    "events": "events_cache.json",
}
CACHE_TTL = {
    "fuel": timedelta(hours=1),
    "weather": timedelta(minutes=30),
    "events": timedelta(hours=1),
}

# Weather condition to demand modifier mapping
WEATHER_MODIFIERS = {
    "sunny": 1.0,
    "cloudy": 1.0,
    "rainy": 1.15,
    "snowy": 1.30,
}

# Event type to surge modifier mapping
EVENT_MODIFIERS = {
    "concert": 1.20,
    "sports": 1.25,
    "convention": 1.15,
    "other": 1.10,
}


class ExternalDataService:
    """Service for managing external data from n8n webhooks.

    Provides:
    - Webhook handlers for receiving external data
    - Caching layer with TTL
    - Fallback to mock data when n8n unavailable
    - Natural language explanations
    """

    def __init__(self, cache_dir: Path | None = None) -> None:
        """Initialize external data service.

        Args:
            cache_dir: Custom cache directory. Uses default if None.
        """
        self._cache_dir = cache_dir or CACHE_DIR
        self._ensure_cache_dir()
        logger.info(f"ExternalDataService initialized with cache dir: {self._cache_dir}")

    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, data_type: str) -> Path:
        """Get path to cache file for data type.

        Args:
            data_type: Type of data (fuel, weather, events).

        Returns:
            Path to cache file.
        """
        filename = CACHE_FILES.get(data_type, f"{data_type}_cache.json")
        return self._cache_dir / filename

    def _read_cache(self, data_type: str) -> dict[str, Any] | None:
        """Read cached data for a data type.

        Args:
            data_type: Type of data to read.

        Returns:
            Cached data dict or None if not found/expired.
        """
        cache_path = self._get_cache_path(data_type)
        if not cache_path.exists():
            logger.debug(f"No cache file for {data_type}")
            return None

        try:
            with open(cache_path) as f:
                data = json.load(f)

            # Check TTL
            cached_at = datetime.fromisoformat(data.get("cached_at", "1970-01-01"))
            ttl = CACHE_TTL.get(data_type, timedelta(hours=1))
            if datetime.utcnow() - cached_at > ttl:
                logger.debug(f"Cache expired for {data_type}")
                return None

            logger.debug(f"Cache hit for {data_type}")
            return data

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Invalid cache file for {data_type}: {e}")
            return None

    def _write_cache(self, data_type: str, data: dict[str, Any]) -> None:
        """Write data to cache.

        Args:
            data_type: Type of data to cache.
            data: Data to cache.
        """
        cache_path = self._get_cache_path(data_type)
        cache_data = {
            **data,
            "cached_at": datetime.utcnow().isoformat(),
        }
        try:
            with open(cache_path, "w") as f:
                json.dump(cache_data, f, indent=2, default=str)
            logger.debug(f"Cached {data_type} data")
        except OSError as e:
            logger.error(f"Failed to write cache for {data_type}: {e}")

    def _get_cache_age_seconds(self, data_type: str) -> int | None:
        """Get age of cached data in seconds.

        Args:
            data_type: Type of data.

        Returns:
            Age in seconds or None if no cache.
        """
        cache_path = self._get_cache_path(data_type)
        if not cache_path.exists():
            return None

        try:
            with open(cache_path) as f:
                data = json.load(f)
            cached_at = datetime.fromisoformat(data.get("cached_at", "1970-01-01"))
            return int((datetime.utcnow() - cached_at).total_seconds())
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def _is_cache_fresh(self, data_type: str) -> bool:
        """Check if cache is fresh (within TTL).

        Args:
            data_type: Type of data.

        Returns:
            True if cache is fresh.
        """
        age = self._get_cache_age_seconds(data_type)
        if age is None:
            return False
        ttl = CACHE_TTL.get(data_type, timedelta(hours=1))
        return age < ttl.total_seconds()

    # -------------------------------------------------------------------------
    # Mock Data (fallback when n8n unavailable)
    # -------------------------------------------------------------------------

    def _get_mock_fuel_data(self) -> FuelData:
        """Get mock fuel data for fallback.

        Returns:
            Neutral fuel data (no price adjustment).
        """
        return FuelData(
            price_per_gallon=3.50,
            change_percent=0.0,
            source="mock",
            fetched_at=datetime.utcnow(),
        )

    def _get_mock_weather_data(self) -> WeatherData:
        """Get mock weather data for fallback.

        Returns:
            Neutral weather data (cloudy, 1.0 modifier).
        """
        return WeatherData(
            condition="cloudy",
            temperature_f=70.0,
            demand_modifier=1.0,
            source="mock",
            fetched_at=datetime.utcnow(),
        )

    def _get_mock_events_data(self) -> list[EventData]:
        """Get mock events data for fallback.

        Returns:
            Empty list (no surge).
        """
        return []

    # -------------------------------------------------------------------------
    # Webhook Handlers (receive data from n8n)
    # -------------------------------------------------------------------------

    def handle_fuel_webhook(self, data: dict[str, Any]) -> FuelData:
        """Handle incoming fuel price data from n8n webhook.

        Args:
            data: Fuel data from webhook payload.

        Returns:
            Validated FuelData model.
        """
        fuel_data = FuelData(
            price_per_gallon=data.get("price_per_gallon", 3.50),
            change_percent=data.get("change_percent", 0.0),
            source=data.get("source", "n8n"),
            fetched_at=datetime.utcnow(),
        )
        self._write_cache("fuel", fuel_data.model_dump())
        logger.info(f"Received fuel data: ${fuel_data.price_per_gallon}/gal")
        return fuel_data

    def handle_weather_webhook(self, data: dict[str, Any]) -> WeatherData:
        """Handle incoming weather data from n8n webhook.

        Maps weather condition to demand modifier:
        - Sunny: 1.0 (baseline)
        - Cloudy: 1.0 (baseline)
        - Rainy: 1.15 (+15% demand)
        - Snowy: 1.30 (+30% demand)

        Args:
            data: Weather data from webhook payload.

        Returns:
            Validated WeatherData model.
        """
        condition = data.get("condition", "cloudy").lower()
        if condition not in WEATHER_MODIFIERS:
            logger.warning(f"Unknown weather condition: {condition}, using cloudy")
            condition = "cloudy"

        demand_modifier = WEATHER_MODIFIERS[condition]

        weather_data = WeatherData(
            condition=condition,  # type: ignore[arg-type]
            temperature_f=data.get("temperature_f", 70.0),
            demand_modifier=demand_modifier,
            source=data.get("source", "n8n"),
            fetched_at=datetime.utcnow(),
        )
        self._write_cache("weather", weather_data.model_dump())
        logger.info(f"Received weather data: {condition}, modifier={demand_modifier}")
        return weather_data

    def handle_events_webhook(self, data: dict[str, Any]) -> list[EventData]:
        """Handle incoming events data from n8n webhook.

        Maps event types to surge modifiers:
        - Concert: 1.20 (+20%)
        - Sports: 1.25 (+25%)
        - Convention: 1.15 (+15%)
        - Other: 1.10 (+10%)

        Args:
            data: Events data from webhook payload.

        Returns:
            List of validated EventData models.
        """
        events_list = data.get("events", [])
        events = []

        for event_data in events_list:
            event_type = event_data.get("type", "other").lower()
            if event_type not in EVENT_MODIFIERS:
                event_type = "other"

            surge_modifier = EVENT_MODIFIERS[event_type]

            # Parse start_time
            start_time_str = event_data.get("start_time")
            if isinstance(start_time_str, str):
                try:
                    start_time = datetime.fromisoformat(start_time_str)
                except ValueError:
                    start_time = datetime.utcnow()
            else:
                start_time = datetime.utcnow()

            event = EventData(
                name=event_data.get("name", "Unknown Event"),
                type=event_type,  # type: ignore[arg-type]
                venue=event_data.get("venue", "Unknown Venue"),
                start_time=start_time,
                surge_modifier=surge_modifier,
                radius_miles=event_data.get("radius_miles", 5.0),
            )
            events.append(event)

        self._write_cache("events", {"events": [e.model_dump() for e in events]})
        logger.info(f"Received {len(events)} events")
        return events

    # -------------------------------------------------------------------------
    # Data Retrieval (with caching and fallback)
    # -------------------------------------------------------------------------

    def get_fuel_data(self) -> FuelData:
        """Get current fuel data from cache or fallback to mock.

        Returns:
            FuelData from cache or mock.
        """
        cached = self._read_cache("fuel")
        if cached:
            # Remove cache metadata before parsing
            cached.pop("cached_at", None)
            return FuelData(**cached)
        return self._get_mock_fuel_data()

    def get_weather_data(self) -> WeatherData:
        """Get current weather data from cache or fallback to mock.

        Returns:
            WeatherData from cache or mock.
        """
        cached = self._read_cache("weather")
        if cached:
            cached.pop("cached_at", None)
            return WeatherData(**cached)
        return self._get_mock_weather_data()

    def get_events_data(self) -> list[EventData]:
        """Get current events data from cache or fallback to mock.

        Returns:
            List of EventData from cache or empty list.
        """
        cached = self._read_cache("events")
        if cached:
            events_list = cached.get("events", [])
            return [EventData(**e) for e in events_list]
        return self._get_mock_events_data()

    def get_external_context(self) -> ExternalContext:
        """Get complete external context from all sources.

        Returns:
            ExternalContext with fuel, weather, and events data.
        """
        return ExternalContext(
            fuel=self.get_fuel_data(),
            weather=self.get_weather_data(),
            events=self.get_events_data(),
            last_updated=datetime.utcnow(),
        )

    # -------------------------------------------------------------------------
    # Explanation Generation
    # -------------------------------------------------------------------------

    def generate_explanation(self, context: ExternalContext) -> str:
        """Generate natural language explanation of external factors.

        Args:
            context: External context to explain.

        Returns:
            Human-readable explanation string.
        """
        explanations = []

        # Weather explanation
        if context.weather:
            weather = context.weather
            if weather.condition == "rainy":
                explanations.append(
                    f"Current weather (rainy, {weather.temperature_f:.0f}°F) "
                    f"is increasing demand by {(weather.demand_modifier - 1) * 100:.0f}%"
                )
            elif weather.condition == "snowy":
                explanations.append(
                    f"Current weather (snowy, {weather.temperature_f:.0f}°F) "
                    f"is increasing demand by {(weather.demand_modifier - 1) * 100:.0f}%"
                )
            else:
                explanations.append(
                    f"Current weather ({weather.condition}, {weather.temperature_f:.0f}°F) "
                    "has no significant impact on demand"
                )

        # Fuel explanation
        if context.fuel:
            fuel = context.fuel
            if abs(fuel.change_percent) > 1:
                direction = "up" if fuel.change_percent > 0 else "down"
                explanations.append(
                    f"Fuel prices (${fuel.price_per_gallon:.2f}/gal) are "
                    f"{direction} {abs(fuel.change_percent):.1f}% from yesterday"
                )

        # Events explanation
        if context.events:
            for event in context.events:
                surge_pct = (event.surge_modifier - 1) * 100
                explanations.append(
                    f"Nearby {event.type} event ({event.name}) "
                    f"is adding {surge_pct:.0f}% surge factor"
                )

        if not explanations:
            return "No significant external factors affecting pricing"

        return ". ".join(explanations) + "."

    def get_external_context_response(self) -> ExternalContextResponse:
        """Get complete external context response for API.

        Returns:
            ExternalContextResponse with context, cache status, and explanation.
        """
        context = self.get_external_context()

        cache_status = {}
        for data_type in ["fuel", "weather", "events"]:
            age = self._get_cache_age_seconds(data_type)
            cache_status[data_type] = {
                "age_seconds": age,
                "is_fresh": self._is_cache_fresh(data_type),
            }

        explanation = self.generate_explanation(context)

        return ExternalContextResponse(
            context=context,
            cache_status=cache_status,
            explanation=explanation,
        )


# Module-level singleton
_service: ExternalDataService | None = None


def get_external_service() -> ExternalDataService:
    """Get or create the external data service singleton.

    Returns:
        ExternalDataService instance.
    """
    global _service
    if _service is None:
        _service = ExternalDataService()
    return _service
