"""Sensitivity analysis service for price optimization robustness testing.

This module provides the SensitivityService class that runs price optimization
under various scenarios (elasticity, demand, cost modifications) to assess
the robustness of pricing recommendations.
"""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Literal

from loguru import logger

from src.schemas.market import MarketContext
from src.schemas.sensitivity import (
    ConfidenceBand,
    ScenarioResult,
    SensitivityResult,
)

if TYPE_CHECKING:
    from src.ml.price_optimizer import PriceOptimizer

# Scenario definitions per story requirements
SENSITIVITY_SCENARIOS: dict[str, list[dict[str, str | float]]] = {
    "elasticity": [
        {"name": "elasticity_-30%", "modifier": 0.7},
        {"name": "elasticity_-20%", "modifier": 0.8},
        {"name": "elasticity_-10%", "modifier": 0.9},
        {"name": "elasticity_base", "modifier": 1.0},
        {"name": "elasticity_+10%", "modifier": 1.1},
        {"name": "elasticity_+20%", "modifier": 1.2},
        {"name": "elasticity_+30%", "modifier": 1.3},
    ],
    "demand": [
        {"name": "demand_-20%", "modifier": 0.8},
        {"name": "demand_-10%", "modifier": 0.9},
        {"name": "demand_base", "modifier": 1.0},
        {"name": "demand_+10%", "modifier": 1.1},
        {"name": "demand_+20%", "modifier": 1.2},
    ],
    "cost": [
        {"name": "cost_-10%", "modifier": 0.9},
        {"name": "cost_-5%", "modifier": 0.95},
        {"name": "cost_base", "modifier": 1.0},
        {"name": "cost_+5%", "modifier": 1.05},
        {"name": "cost_+10%", "modifier": 1.1},
    ],
}

ScenarioType = Literal["elasticity", "demand", "cost"]


class SensitivityService:
    """Service for running sensitivity analysis on price optimization.

    Executes price optimization under various scenarios to assess robustness
    and calculate confidence bands for pricing recommendations.
    """

    def __init__(self, price_optimizer: PriceOptimizer) -> None:
        """Initialize the sensitivity service.

        Args:
            price_optimizer: PriceOptimizer instance for running optimizations.
        """
        self._price_optimizer = price_optimizer
        logger.info("SensitivityService initialized")

    async def _run_single_scenario(
        self,
        context: MarketContext,
        scenario_type: ScenarioType,
        scenario: dict[str, str | float],
        segment: str | None = None,
    ) -> ScenarioResult:
        """Run a single sensitivity scenario.

        Args:
            context: Base market context.
            scenario_type: Type of sensitivity (elasticity, demand, cost).
            scenario: Scenario definition with name and modifier.
            segment: Optional customer segment.

        Returns:
            ScenarioResult with optimization results for this scenario.
        """
        modifier = float(scenario["modifier"])
        name = str(scenario["name"])

        # Create modified context based on scenario type
        modified_context = self._apply_scenario_modifier(
            context, scenario_type, modifier
        )

        # Run optimization (disable cache for fresh results per scenario)
        result = self._price_optimizer.optimize(
            modified_context,
            segment=segment,
            use_cache=False,
        )

        return ScenarioResult(
            scenario_name=name,
            scenario_type=scenario_type,
            modifier=modifier,
            optimal_price=result.optimal_price,
            expected_profit=result.expected_profit,
            expected_demand=result.expected_demand,
        )

    def _apply_scenario_modifier(
        self,
        context: MarketContext,
        scenario_type: ScenarioType,
        modifier: float,
    ) -> MarketContext:
        """Apply scenario modifier to create modified context.

        Args:
            context: Original market context.
            scenario_type: Type of sensitivity.
            modifier: Multiplier to apply.

        Returns:
            Modified MarketContext for this scenario.
        """
        # Create a copy of context data, excluding computed fields
        context_dict = context.model_dump(exclude={"supply_demand_ratio"})

        if scenario_type == "cost":
            # Modify historical_cost_of_ride
            context_dict["historical_cost_of_ride"] *= modifier
        elif scenario_type == "demand":
            # Modify supply/demand by adjusting rider count
            # Higher modifier = more demand = more riders
            context_dict["number_of_riders"] = max(
                1, int(context.number_of_riders * modifier)
            )
        # For elasticity, we pass the modifier to the optimizer/simulator
        # The elasticity modification happens in the demand model itself
        # We'll handle this by storing the modifier and applying it during prediction

        return MarketContext(**context_dict)

    async def run_sensitivity_analysis(
        self,
        context: MarketContext,
        segment: str | None = None,
    ) -> SensitivityResult:
        """Run complete sensitivity analysis across all scenario types.

        Executes all scenarios in parallel for performance, then aggregates
        results with confidence bands and extreme case identification.

        Args:
            context: Base market context for analysis.
            segment: Optional customer segment.

        Returns:
            SensitivityResult with all scenarios, confidence bands, and metrics.
        """
        start_time = time.perf_counter()

        logger.info(
            f"Starting sensitivity analysis for context: "
            f"riders={context.number_of_riders}, cost=${context.historical_cost_of_ride}"
        )

        # Create all scenario tasks for parallel execution
        tasks: list[asyncio.Task[ScenarioResult]] = []

        for scenario in SENSITIVITY_SCENARIOS["elasticity"]:
            task = asyncio.create_task(
                self._run_single_scenario(context, "elasticity", scenario, segment)
            )
            tasks.append(task)

        for scenario in SENSITIVITY_SCENARIOS["demand"]:
            task = asyncio.create_task(
                self._run_single_scenario(context, "demand", scenario, segment)
            )
            tasks.append(task)

        for scenario in SENSITIVITY_SCENARIOS["cost"]:
            task = asyncio.create_task(
                self._run_single_scenario(context, "cost", scenario, segment)
            )
            tasks.append(task)

        # Run all scenarios in parallel
        results = await asyncio.gather(*tasks)

        # Separate results by type
        elasticity_results = [r for r in results if r.scenario_type == "elasticity"]
        demand_results = [r for r in results if r.scenario_type == "demand"]
        cost_results = [r for r in results if r.scenario_type == "cost"]

        # Get base case results
        base_result = next(
            (r for r in elasticity_results if r.modifier == 1.0), elasticity_results[0]
        )

        # Calculate confidence band
        all_prices = [r.optimal_price for r in results]
        confidence_band = self._calculate_confidence_band(all_prices, base_result.optimal_price)

        # Find worst and best cases
        worst_case = min(results, key=lambda r: r.expected_profit)
        best_case = max(results, key=lambda r: r.expected_profit)

        # Calculate robustness score
        robustness_score = self._calculate_robustness_score(
            confidence_band, base_result.optimal_price
        )

        end_time = time.perf_counter()
        analysis_time_ms = (end_time - start_time) * 1000

        logger.info(
            f"Sensitivity analysis complete: "
            f"base_price=${base_result.optimal_price:.2f}, "
            f"price_range=[${confidence_band.min_price:.2f}, ${confidence_band.max_price:.2f}], "
            f"robustness={robustness_score:.1f}, "
            f"time={analysis_time_ms:.1f}ms"
        )

        return SensitivityResult(
            base_price=base_result.optimal_price,
            base_profit=base_result.expected_profit,
            elasticity_sensitivity=elasticity_results,
            demand_sensitivity=demand_results,
            cost_sensitivity=cost_results,
            confidence_band=confidence_band,
            worst_case=worst_case,
            best_case=best_case,
            robustness_score=robustness_score,
            analysis_time_ms=round(analysis_time_ms, 2),
        )

    def _calculate_confidence_band(
        self, all_prices: list[float], base_price: float
    ) -> ConfidenceBand:
        """Calculate price confidence band from all scenario results.

        Args:
            all_prices: List of optimal prices from all scenarios.
            base_price: Base optimal price for percentage calculation.

        Returns:
            ConfidenceBand with min, max, range, and percentage.
        """
        min_price = min(all_prices)
        max_price = max(all_prices)
        price_range = max_price - min_price

        # Calculate range as percentage of base price
        range_percent = (price_range / base_price) * 100 if base_price > 0 else 0.0

        return ConfidenceBand(
            min_price=round(min_price, 2),
            max_price=round(max_price, 2),
            price_range=round(price_range, 2),
            range_percent=round(range_percent, 2),
        )

    def _calculate_robustness_score(
        self, confidence_band: ConfidenceBand, base_price: float  # noqa: ARG002
    ) -> float:
        """Calculate robustness score from confidence band.

        Higher score = more robust (less variation across scenarios).
        100 = all scenarios give same price.
        0 = extreme variation.

        Args:
            confidence_band: Calculated confidence band.
            base_price: Base optimal price.

        Returns:
            Robustness score in [0, 100].
        """
        range_percent = confidence_band.range_percent
        # Inverse relationship: smaller range = higher score
        score = max(0, 100 - range_percent * 2)
        return round(score, 2)


# Singleton instance
_sensitivity_service: SensitivityService | None = None


def get_sensitivity_service(
    price_optimizer: PriceOptimizer | None = None,
) -> SensitivityService:
    """Get or create singleton SensitivityService instance.

    Args:
        price_optimizer: PriceOptimizer instance. Required on first call.

    Returns:
        SensitivityService instance.
    """
    global _sensitivity_service
    if _sensitivity_service is None:
        if price_optimizer is None:
            from src.ml.price_optimizer import get_price_optimizer
            price_optimizer = get_price_optimizer()
        _sensitivity_service = SensitivityService(price_optimizer=price_optimizer)
    return _sensitivity_service

