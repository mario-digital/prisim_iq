"""Sensitivity analysis API router for robustness testing endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from src.schemas.market import MarketContext
from src.schemas.sensitivity import (
    ConfidenceBand,
    MarketContextSummary,
    ScenarioResult,
    ScenarioSummary,
    SensitivityPoint,
    SensitivityResponse,
    SensitivityResult,
)
from src.services.sensitivity_service import SensitivityService, get_sensitivity_service

router = APIRouter(prefix="/sensitivity_analysis", tags=["Sensitivity Analysis"])

# Type alias for dependency injection
SensitivityServiceDep = Annotated[SensitivityService, Depends(get_sensitivity_service)]


def _modifier_to_label(modifier: float) -> str:
    """Convert modifier value to human-readable label.

    Args:
        modifier: Multiplier value (e.g., 0.8, 1.0, 1.2)

    Returns:
        Label string (e.g., "-20%", "Base", "+20%")
    """
    if modifier == 1.0:
        return "Base"
    percent = round((modifier - 1.0) * 100)
    if percent > 0:
        return f"+{percent}%"
    return f"{percent}%"


def _scenario_to_point(scenario: ScenarioResult) -> SensitivityPoint:
    """Convert ScenarioResult to chart-ready SensitivityPoint.

    Args:
        scenario: Internal scenario result.

    Returns:
        SensitivityPoint ready for Recharts consumption.
    """
    return SensitivityPoint(
        x=scenario.modifier,
        y=round(scenario.optimal_price, 2),
        label=_modifier_to_label(scenario.modifier),
        profit=round(scenario.expected_profit, 2),
        demand=round(scenario.expected_demand, 4),
    )


def _scenario_to_summary(scenario: ScenarioResult, base_price: float) -> ScenarioSummary:
    """Convert ScenarioResult to human-readable ScenarioSummary.

    Args:
        scenario: Internal scenario result.
        base_price: Base optimal price for comparison.

    Returns:
        ScenarioSummary with description for UI display.
    """
    if scenario.modifier == 1.0:
        description = f"Base case: optimal price is ${scenario.optimal_price:.2f}"
    elif scenario.modifier < 1.0:
        change = abs(round((scenario.modifier - 1.0) * 100))
        # Compare scenario price to base price to determine direction
        price_direction = "increases" if scenario.optimal_price > base_price else "decreases"
        description = (
            f"{change}% lower {scenario.scenario_type} "
            f"{price_direction} optimal price to ${scenario.optimal_price:.2f}"
        )
    else:
        change = round((scenario.modifier - 1.0) * 100)
        # Compare scenario price to base price to determine direction
        price_direction = "reduces" if scenario.optimal_price < base_price else "increases"
        description = (
            f"{change}% higher {scenario.scenario_type} "
            f"{price_direction} optimal price to ${scenario.optimal_price:.2f}"
        )

    return ScenarioSummary(
        scenario_name=scenario.scenario_name,
        scenario_type=scenario.scenario_type,
        price=round(scenario.optimal_price, 2),
        profit=round(scenario.expected_profit, 2),
        description=description,
    )


def _format_for_charts(
    result: SensitivityResult,
    context: MarketContext,
) -> SensitivityResponse:
    """Transform SensitivityResult to chart-ready SensitivityResponse.

    Args:
        result: Internal sensitivity analysis result.
        context: Original market context for summary.

    Returns:
        SensitivityResponse formatted for frontend charts.
    """
    # Create context summary
    base_context = MarketContextSummary(
        location_category=context.location_category,
        vehicle_type=context.vehicle_type,
        customer_loyalty_status=context.customer_loyalty_status,
        time_of_booking=context.time_of_booking,
        supply_demand_ratio=round(context.supply_demand_ratio, 4),
    )

    # Convert scenario results to chart points
    elasticity_points = [_scenario_to_point(s) for s in result.elasticity_sensitivity]
    demand_points = [_scenario_to_point(s) for s in result.demand_sensitivity]
    cost_points = [_scenario_to_point(s) for s in result.cost_sensitivity]

    # Calculate total scenarios
    total_scenarios = (
        len(result.elasticity_sensitivity)
        + len(result.demand_sensitivity)
        + len(result.cost_sensitivity)
    )

    return SensitivityResponse(
        base_context=base_context,
        base_price=round(result.base_price, 2),
        base_profit=round(result.base_profit, 2),
        elasticity_sensitivity=elasticity_points,
        demand_sensitivity=demand_points,
        cost_sensitivity=cost_points,
        confidence_band=ConfidenceBand(
            min_price=result.confidence_band.min_price,
            max_price=result.confidence_band.max_price,
            price_range=result.confidence_band.price_range,
            range_percent=result.confidence_band.range_percent,
        ),
        robustness_score=result.robustness_score,
        worst_case=_scenario_to_summary(result.worst_case, result.base_price),
        best_case=_scenario_to_summary(result.best_case, result.base_price),
        scenarios_calculated=total_scenarios,
        processing_time_ms=result.analysis_time_ms,
    )


@router.post(
    "",
    response_model=SensitivityResponse,
    summary="Run sensitivity analysis for price optimization",
    description="""
Perform sensitivity analysis on price optimization across multiple scenarios.

The endpoint tests how optimal price recommendations respond to changes in:
- **Elasticity**: Price sensitivity variations (±30% in 10% steps)
- **Demand**: Demand level changes (±20% in 10% steps)
- **Cost**: Cost basis variations (±10% in 5% steps)

Returns chart-ready arrays optimized for Recharts/LineChart components with:
- `x`: Modifier value (0.7 to 1.3)
- `y`: Resulting optimal price
- `label`: Human-readable label ("-30%" to "+30%")
- `profit`: Expected profit at this point
- `demand`: Expected demand at this point

Also provides confidence metrics:
    - `confidence_band`: Min/max price range across all scenarios
    - `robustness_score`: 0-100 score (higher = more stable pricing)
    - `worst_case` / `best_case`: Extreme scenarios with descriptions
    """,
    responses={
        200: {
            "description": "Successful sensitivity analysis",
        },
        422: {
            "description": "Validation error - invalid market context",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "value_error",
                                "loc": ["body", "average_ratings"],
                                "msg": "Input should be greater than or equal to 1.0",
                                "input": 0.5,
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error - model or service failure",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error",
                        "error_code": "INTERNAL_ERROR",
                    }
                }
            },
        },
        503: {
            "description": "Service unavailable - models not loaded",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Pricing models not available. Please ensure models are trained.",
                    }
                }
            },
        },
    },
)
async def sensitivity_analysis(
    context: MarketContext,
    sensitivity_service: SensitivityServiceDep,
) -> SensitivityResponse:
    """Run sensitivity analysis for the given market context.

    Executes price optimization under various scenarios (elasticity, demand, cost
    modifications) in parallel to assess pricing robustness.

    Args:
        context: Market conditions and customer profile.
        sensitivity_service: Injected sensitivity service.

    Returns:
        Chart-ready sensitivity analysis with confidence metrics.

    Raises:
        HTTPException: 503 if models not available, 500 for other errors.
    """
    logger.info(
        f"Sensitivity analysis request: "
        f"location={context.location_category}, "
        f"vehicle={context.vehicle_type}, "
        f"riders={context.number_of_riders}, "
        f"drivers={context.number_of_drivers}"
    )

    try:
        result = await sensitivity_service.run_sensitivity_analysis(context)
        response = _format_for_charts(result, context)

        logger.info(
            f"Sensitivity analysis complete: "
            f"base_price=${response.base_price:.2f}, "
            f"robustness={response.robustness_score:.1f}, "
            f"scenarios={response.scenarios_calculated}, "
            f"time={response.processing_time_ms:.1f}ms"
        )

        return response

    except FileNotFoundError as e:
        logger.error(f"Model files not found: {e}")
        raise HTTPException(
            status_code=503,
            detail="Pricing models not available. Please ensure models are trained.",
        ) from e

    except RuntimeError as e:
        logger.error(f"Runtime error during sensitivity analysis: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        ) from e
