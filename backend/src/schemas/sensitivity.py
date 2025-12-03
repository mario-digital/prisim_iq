"""Sensitivity analysis result schemas."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ScenarioResult(BaseModel):
    """Result from a single sensitivity scenario."""

    scenario_name: str = Field(..., description="Unique name for the scenario")
    scenario_type: Literal["elasticity", "demand", "cost"] = Field(
        ..., description="Type of sensitivity being tested"
    )
    modifier: float = Field(..., description="Multiplier applied (e.g., 0.9 for -10%)")
    optimal_price: float = Field(..., description="Optimal price under this scenario")
    expected_profit: float = Field(..., description="Expected profit at optimal price")
    expected_demand: float = Field(..., ge=0, le=1, description="Expected demand at optimal price")


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

    confidence_band: ConfidenceBand = Field(..., description="Price range across all scenarios")
    worst_case: ScenarioResult = Field(..., description="Scenario with lowest expected profit")
    best_case: ScenarioResult = Field(..., description="Scenario with highest expected profit")
    robustness_score: float = Field(
        ..., ge=0, le=100, description="Score 0-100: higher = more robust (less variation)"
    )

    analysis_time_ms: float = Field(..., ge=0, description="Total analysis time in milliseconds")


# ============================================================================
# Chart-Ready Response Schemas (Story 3.6)
# ============================================================================


class SensitivityPoint(BaseModel):
    """Single data point for sensitivity charts (Recharts-ready).

    Example: {"x": 0.8, "y": 45.00, "label": "-20%", "profit": 20.50, "demand": 0.72}
    """

    x: float = Field(..., description="Modifier value (e.g., 0.8 for -20%)")
    y: float = Field(..., description="Resulting optimal price")
    label: str = Field(..., description="Human-readable label (e.g., '-20%', 'Base', '+20%')")
    profit: float = Field(..., description="Expected profit at this point")
    demand: float = Field(..., description="Expected demand at this point")


class MarketContextSummary(BaseModel):
    """Summary of the base market context for the analysis."""

    location_category: str = Field(..., description="Geographic location category")
    vehicle_type: str = Field(..., description="Vehicle type (Economy/Premium)")
    customer_loyalty_status: str = Field(..., description="Customer loyalty tier")
    time_of_booking: str = Field(..., description="Time period of booking")
    supply_demand_ratio: float = Field(..., description="Supply/demand ratio")


class ScenarioSummary(BaseModel):
    """Summary of worst/best case scenarios for display."""

    scenario_name: str = Field(..., description="Name of the scenario")
    scenario_type: str = Field(..., description="Type: elasticity, demand, or cost")
    price: float = Field(..., description="Optimal price under this scenario")
    profit: float = Field(..., description="Expected profit under this scenario")
    description: str = Field(..., description="Human-readable description of the scenario impact")


class SensitivityResponse(BaseModel):
    """Complete sensitivity analysis response formatted for frontend charts.

    This response is optimized for direct consumption by Recharts components.
    Each sensitivity array contains SensitivityPoint objects with x/y coordinates
    suitable for LineChart or AreaChart components.
    """

    # Base reference
    base_context: MarketContextSummary = Field(
        ..., description="Summary of the input market context"
    )
    base_price: float = Field(..., description="Base optimal price (no modifiers)")
    base_profit: float = Field(..., description="Base expected profit (no modifiers)")

    # Sensitivity arrays (Recharts-ready)
    elasticity_sensitivity: list[SensitivityPoint] = Field(
        ...,
        description="Elasticity sensitivity points for chart plotting (7 points)",
    )
    demand_sensitivity: list[SensitivityPoint] = Field(
        ...,
        description="Demand sensitivity points for chart plotting (5 points)",
    )
    cost_sensitivity: list[SensitivityPoint] = Field(
        ...,
        description="Cost sensitivity points for chart plotting (5 points)",
    )

    # Confidence metrics
    confidence_band: ConfidenceBand = Field(
        ..., description="Price confidence band across all scenarios"
    )
    robustness_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Score 0-100: higher = more robust (less price variation)",
    )

    # Extremes
    worst_case: ScenarioSummary = Field(..., description="Scenario with lowest expected profit")
    best_case: ScenarioSummary = Field(..., description="Scenario with highest expected profit")

    # Metadata
    scenarios_calculated: int = Field(..., description="Total number of scenarios analyzed")
    processing_time_ms: float = Field(
        ..., ge=0, description="Total processing time in milliseconds"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "base_context": {
                    "location_category": "Urban",
                    "vehicle_type": "Premium",
                    "customer_loyalty_status": "Gold",
                    "time_of_booking": "Evening",
                    "supply_demand_ratio": 0.5,
                },
                "base_price": 42.50,
                "base_profit": 18.75,
                "elasticity_sensitivity": [
                    {"x": 0.7, "y": 48.50, "label": "-30%", "profit": 22.10, "demand": 0.68},
                    {"x": 0.8, "y": 45.00, "label": "-20%", "profit": 20.50, "demand": 0.72},
                    {"x": 0.9, "y": 43.50, "label": "-10%", "profit": 19.20, "demand": 0.75},
                    {"x": 1.0, "y": 42.50, "label": "Base", "profit": 18.75, "demand": 0.78},
                    {"x": 1.1, "y": 40.50, "label": "+10%", "profit": 17.80, "demand": 0.82},
                    {"x": 1.2, "y": 38.50, "label": "+20%", "profit": 16.90, "demand": 0.85},
                    {"x": 1.3, "y": 36.50, "label": "+30%", "profit": 16.10, "demand": 0.88},
                ],
                "demand_sensitivity": [
                    {"x": 0.8, "y": 40.00, "label": "-20%", "profit": 16.00, "demand": 0.70},
                    {"x": 0.9, "y": 41.00, "label": "-10%", "profit": 17.20, "demand": 0.74},
                    {"x": 1.0, "y": 42.50, "label": "Base", "profit": 18.75, "demand": 0.78},
                    {"x": 1.1, "y": 44.00, "label": "+10%", "profit": 20.50, "demand": 0.82},
                    {"x": 1.2, "y": 45.50, "label": "+20%", "profit": 22.30, "demand": 0.85},
                ],
                "cost_sensitivity": [
                    {"x": 0.9, "y": 40.00, "label": "-10%", "profit": 21.50, "demand": 0.78},
                    {"x": 0.95, "y": 41.25, "label": "-5%", "profit": 20.10, "demand": 0.78},
                    {"x": 1.0, "y": 42.50, "label": "Base", "profit": 18.75, "demand": 0.78},
                    {"x": 1.05, "y": 43.75, "label": "+5%", "profit": 17.40, "demand": 0.78},
                    {"x": 1.1, "y": 45.00, "label": "+10%", "profit": 16.00, "demand": 0.78},
                ],
                "confidence_band": {
                    "min_price": 32.00,
                    "max_price": 52.00,
                    "price_range": 20.00,
                    "range_percent": 47.06,
                },
                "robustness_score": 53,
                "worst_case": {
                    "scenario_name": "elasticity_+30%",
                    "scenario_type": "elasticity",
                    "price": 36.50,
                    "profit": 16.10,
                    "description": "30% higher elasticity reduces optimal price to $36.50",
                },
                "best_case": {
                    "scenario_name": "elasticity_-30%",
                    "scenario_type": "elasticity",
                    "price": 48.50,
                    "profit": 22.10,
                    "description": "30% lower elasticity increases optimal price to $48.50",
                },
                "scenarios_calculated": 17,
                "processing_time_ms": 245.5,
            }
        }
    )
