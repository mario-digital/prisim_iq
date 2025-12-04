"""Pricing result schemas for price optimization API responses."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from src.rules.engine import AppliedRule
from src.schemas.optimization import PriceDemandPoint
from src.schemas.segment import SegmentDetails


class PricingResult(BaseModel):
    """Complete pricing recommendation result from optimization endpoint.

    Contains the recommended price, confidence metrics, profit analysis,
    segment classification, applied business rules, and visualization data.
    """

    # Core recommendation
    recommended_price: float = Field(
        ...,
        ge=0,
        description="Final recommended price after ML optimization and business rules",
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score based on segment centroid distance (0.0-1.0, higher is better)",
    )

    # Demand and profit metrics
    expected_demand: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Predicted demand at recommended price (0.0-1.0)",
    )
    expected_profit: float = Field(
        ...,
        description="Expected profit at recommended price",
    )
    baseline_profit: float = Field(
        ...,
        description="Profit at historical/baseline price",
    )
    profit_uplift_percent: float = Field(
        ...,
        description="Percentage improvement over baseline: (optimal - baseline) / baseline * 100",
    )

    # Segment information
    segment: SegmentDetails = Field(
        ...,
        description="Market segment classification with characteristics",
    )

    # Model information
    model_used: str = Field(
        ...,
        description="Name of ML model used for demand prediction (e.g., 'xgboost')",
    )

    # Business rules applied
    rules_applied: list[AppliedRule] = Field(
        default_factory=list,
        description="List of business rules that modified the price",
    )
    price_before_rules: float = Field(
        ...,
        ge=0,
        description="ML-optimized price before business rule adjustments",
    )

    # Visualization data
    price_demand_curve: list[PriceDemandPoint] = Field(
        default_factory=list,
        description="Sample points for price-demand curve visualization",
    )

    # Metadata
    processing_time_ms: float = Field(
        ...,
        ge=0,
        description="Total processing time in milliseconds",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp of the optimization (ISO 8601 UTC)",
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "recommended_price": 42.50,
                "confidence_score": 0.85,
                "expected_demand": 0.72,
                "expected_profit": 15.30,
                "baseline_profit": 10.50,
                "profit_uplift_percent": 45.71,
                "segment": {
                    "segment_name": "Urban_Peak_Premium",
                    "cluster_id": 2,
                    "characteristics": {
                        "avg_supply_demand_ratio": 0.65,
                        "sample_count": 1250,
                        "centroid_norm": 1.234,
                    },
                    "centroid_distance": 0.45,
                    "human_readable_description": "High-demand urban area during peak hours with premium vehicle preference",
                    "confidence_level": "high",
                },
                "model_used": "xgboost",
                "rules_applied": [
                    {
                        "rule_id": "floor_minimum_margin",
                        "rule_name": "Minimum Margin Floor",
                        "price_before": 38.50,
                        "price_after": 42.50,
                        "impact": 4.00,
                        "impact_percent": 10.39,
                    }
                ],
                "price_before_rules": 38.50,
                "price_demand_curve": [
                    {"price": 30.0, "demand": 0.95, "profit": 0.0},
                    {"price": 35.0, "demand": 0.85, "profit": 4.25},
                    {"price": 40.0, "demand": 0.75, "profit": 7.50},
                    {"price": 45.0, "demand": 0.65, "profit": 9.75},
                    {"price": 50.0, "demand": 0.55, "profit": 11.00},
                ],
                "processing_time_ms": 245.5,
                "timestamp": "2024-01-15T10:30:00Z",
            }
        },
    )

