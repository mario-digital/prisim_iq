"""Schemas for external data integration (n8n webhooks).

Defines data structures for:
- Fuel prices: Impact cost basis calculations
- Weather conditions: Impact demand modifiers
- Local events: Impact surge factors
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class FuelData(BaseModel):
    """Fuel price data from external source."""

    price_per_gallon: float = Field(..., description="Current fuel price per gallon")
    change_percent: float = Field(
        ..., description="Percent change vs yesterday (e.g., 2.5 for +2.5%)"
    )
    source: str = Field(default="n8n", description="Data source identifier")
    fetched_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="When data was fetched"
    )


class WeatherData(BaseModel):
    """Weather conditions from external source."""

    condition: Literal["sunny", "cloudy", "rainy", "snowy"] = Field(
        ..., description="Current weather condition"
    )
    temperature_f: float = Field(..., description="Temperature in Fahrenheit")
    demand_modifier: float = Field(
        ...,
        description="Demand multiplier (e.g., 1.15 for rainy = +15% demand)",
        ge=0.5,
        le=2.0,
    )
    source: str = Field(default="n8n", description="Data source identifier")
    fetched_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="When data was fetched"
    )


class EventData(BaseModel):
    """Local event data from external source."""

    name: str = Field(..., description="Event name")
    type: Literal["concert", "sports", "convention", "other"] = Field(
        ..., description="Event category"
    )
    venue: str = Field(..., description="Event venue/location")
    start_time: datetime = Field(..., description="Event start time")
    surge_modifier: float = Field(
        ...,
        description="Surge multiplier (e.g., 1.20 for +20% surge)",
        ge=1.0,
        le=2.0,
    )
    radius_miles: float = Field(default=5.0, description="Affected radius in miles", ge=0.0)


class ExternalContext(BaseModel):
    """Aggregated external context from all sources."""

    fuel: FuelData | None = Field(default=None, description="Current fuel price data")
    weather: WeatherData | None = Field(default=None, description="Current weather conditions")
    events: list[EventData] = Field(default_factory=list, description="Active local events")
    last_updated: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="When context was last refreshed"
    )

    def get_combined_event_modifier(self) -> float:
        """Calculate combined surge modifier from all active events.

        Returns:
            Combined multiplier (multiplicative, e.g., 1.20 * 1.25 = 1.50).
        """
        if not self.events:
            return 1.0
        modifier = 1.0
        for event in self.events:
            modifier *= event.surge_modifier
        return modifier


class ExternalContextResponse(BaseModel):
    """API response for external context endpoint."""

    context: ExternalContext = Field(..., description="Current external context")
    cache_status: dict[str, dict] = Field(
        ...,
        description="Cache freshness info per data type",
        examples=[
            {
                "fuel": {"age_seconds": 1800, "is_fresh": True},
                "weather": {"age_seconds": 900, "is_fresh": True},
                "events": {"age_seconds": 3600, "is_fresh": True},
            }
        ],
    )
    explanation: str = Field(..., description="Natural language summary of external factors")
