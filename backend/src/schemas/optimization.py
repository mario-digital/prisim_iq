"""Optimization result schemas for price optimization."""

from pydantic import BaseModel, Field


class PriceDemandPoint(BaseModel):
    """A single point on the price-demand curve."""

    price: float = Field(..., description="Price point")
    demand: float = Field(..., ge=0, le=1, description="Predicted demand at this price")
    profit: float = Field(..., description="Expected profit at this price")


class OptimizationResult(BaseModel):
    """Result from price optimization."""

    optimal_price: float = Field(..., description="Profit-maximizing price")
    expected_demand: float = Field(
        ..., ge=0, le=1, description="Expected demand at optimal price"
    )
    expected_profit: float = Field(..., description="Expected profit at optimal price")
    baseline_price: float = Field(..., description="Historical/baseline price")
    baseline_profit: float = Field(..., description="Profit at baseline price")
    profit_uplift_percent: float = Field(
        ..., description="Percentage improvement over baseline: (optimal - baseline) / baseline * 100"
    )
    price_demand_curve: list[PriceDemandPoint] = Field(
        ..., description="Sample points for visualization"
    )
    optimization_time_ms: float = Field(
        ..., ge=0, description="Time taken to optimize in milliseconds"
    )

