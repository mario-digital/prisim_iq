"""Market context schema for pricing and segmentation."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field


class MarketContext(BaseModel):
    """Market context for segmentation and pricing optimization.

    This schema represents the input features used for K-Means clustering
    and segment classification based on the dynamic_pricing dataset.
    """

    number_of_riders: int = Field(
        ...,
        ge=1,
        le=100,
        description="Demand indicator - number of riders requesting rides",
    )
    number_of_drivers: int = Field(
        ...,
        ge=1,
        le=100,
        description="Supply indicator - number of available drivers",
    )
    location_category: Literal["Urban", "Suburban", "Rural"] = Field(
        ...,
        description="Geographic location category",
    )
    customer_loyalty_status: Literal["Bronze", "Silver", "Gold", "Platinum"] = Field(
        ...,
        description="Customer loyalty tier",
    )
    number_of_past_rides: int = Field(
        ...,
        ge=0,
        description="Customer's historical ride count",
    )
    average_ratings: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Average customer rating (1.0-5.0)",
    )
    time_of_booking: Literal["Morning", "Afternoon", "Evening", "Night"] = Field(
        ...,
        description="Time period of the booking",
    )
    vehicle_type: Literal["Economy", "Premium"] = Field(
        ...,
        description="Type of vehicle requested",
    )
    expected_ride_duration: int = Field(
        ...,
        ge=1,
        description="Expected ride duration in minutes",
    )
    historical_cost_of_ride: float = Field(
        ...,
        ge=0,
        description="Baseline/historical price for this route",
    )

    # Optional tier prices for policy checks (rideshare analog of catalog hierarchy)
    tier_prices: dict[str, float] | None = Field(
        default=None,
        description="Optional explicit tier prices (keys: new, exchange, repair, usm)",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def supply_demand_ratio(self) -> float:
        """Compute supply/demand ratio for segmentation."""
        return self.number_of_drivers / self.number_of_riders

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
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
            }
        },
    )
