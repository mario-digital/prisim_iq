"""Sensitivity analysis result schemas."""

from typing import Literal

from pydantic import BaseModel, Field


class ScenarioResult(BaseModel):
    """Result from a single sensitivity scenario."""

    scenario_name: str = Field(..., description="Unique name for the scenario")
    scenario_type: Literal["elasticity", "demand", "cost"] = Field(
        ..., description="Type of sensitivity being tested"
    )
    modifier: float = Field(..., description="Multiplier applied (e.g., 0.9 for -10%)")
    optimal_price: float = Field(..., description="Optimal price under this scenario")
    expected_profit: float = Field(..., description="Expected profit at optimal price")
    expected_demand: float = Field(
        ..., ge=0, le=1, description="Expected demand at optimal price"
    )


class ConfidenceBand(BaseModel):
    """Price confidence band across all scenarios."""

    min_price: float = Field(..., description="Minimum optimal price across scenarios")
    max_price: float = Field(..., description="Maximum optimal price across scenarios")
    price_range: float = Field(..., description="Difference between max and min price")
    range_percent: float = Field(
        ..., description="Range as percentage of base price: (max-min)/base * 100"
    )


class SensitivityResult(BaseModel):
    """Complete sensitivity analysis result."""

    base_price: float = Field(..., description="Base optimal price (no modifiers)")
    base_profit: float = Field(..., description="Base expected profit (no modifiers)")

    elasticity_sensitivity: list[ScenarioResult] = Field(
        ..., description="Results for elasticity sensitivity scenarios"
    )
    demand_sensitivity: list[ScenarioResult] = Field(
        ..., description="Results for demand sensitivity scenarios"
    )
    cost_sensitivity: list[ScenarioResult] = Field(
        ..., description="Results for cost sensitivity scenarios"
    )

    confidence_band: ConfidenceBand = Field(
        ..., description="Price range across all scenarios"
    )
    worst_case: ScenarioResult = Field(
        ..., description="Scenario with lowest expected profit"
    )
    best_case: ScenarioResult = Field(
        ..., description="Scenario with highest expected profit"
    )
    robustness_score: float = Field(
        ..., ge=0, le=100, description="Score 0-100: higher = more robust (less variation)"
    )

    analysis_time_ms: float = Field(
        ..., ge=0, description="Total analysis time in milliseconds"
    )

