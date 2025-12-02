"""Market context schema for pricing and segmentation."""

from typing import Literal

from pydantic import BaseModel, Field


class MarketContext(BaseModel):
    """Market context for segmentation and pricing optimization.

    This schema represents the input features used for K-Means clustering
    and segment classification based on the dynamic_pricing dataset.
    """

    # Core segmentation features
    supply_demand_ratio: float = Field(
        ...,
        ge=0,
        description="Ratio of drivers to riders (Number_of_Drivers / Number_of_Riders)",
    )
    time_of_booking: Literal["Morning", "Afternoon", "Evening", "Night"] = Field(
        ...,
        description="Time period of the booking",
    )
    location_category: Literal["Urban", "Suburban", "Rural"] = Field(
        ...,
        description="Geographic location category",
    )
    vehicle_type: Literal["Economy", "Premium"] = Field(
        ...,
        description="Type of vehicle",
    )

    # Additional context (optional, for future use)
    number_of_riders: int | None = Field(
        default=None,
        ge=0,
        description="Number of riders requesting rides",
    )
    number_of_drivers: int | None = Field(
        default=None,
        ge=0,
        description="Number of available drivers",
    )
    customer_loyalty_status: Literal["Silver", "Gold", "Regular"] | None = Field(
        default=None,
        description="Customer loyalty tier",
    )
    number_of_past_rides: int | None = Field(
        default=None,
        ge=0,
        description="Customer's historical ride count",
    )
    average_ratings: float | None = Field(
        default=None,
        ge=0,
        le=5,
        description="Average customer rating",
    )
    expected_ride_duration: float | None = Field(
        default=None,
        ge=0,
        description="Expected duration in minutes",
    )
    historical_cost_of_ride: float | None = Field(
        default=None,
        ge=0,
        description="Historical average ride cost",
    )

    model_config = {"extra": "forbid"}

