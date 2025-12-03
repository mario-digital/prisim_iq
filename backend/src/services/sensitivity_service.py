"""Sensitivity analysis service for price optimization robustness testing.

This module provides the SensitivityService class that runs price optimization
under various scenarios (elasticity, demand, cost modifications) to assess
the robustness of pricing recommendations.

Uses ProcessPoolExecutor for true CPU parallelism by running optimizations
in separate processes, bypassing Python's GIL.
"""

from __future__ import annotations

import asyncio
import os
import time
from concurrent.futures import ProcessPoolExecutor
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


# ============================================================================
# Module-level worker function for ProcessPoolExecutor
# ============================================================================

# Process-local optimizer instance (initialized once per worker process)
_process_optimizer: PriceOptimizer | None = None


def _get_process_optimizer() -> PriceOptimizer:
    """Get or initialize process-local PriceOptimizer.

    Each worker process initializes its own optimizer and models.
    This is cached per-process to avoid reloading models for each task.
    """
    global _process_optimizer
    if _process_optimizer is None:
        from src.ml.model_manager import get_model_manager
        from src.ml.price_optimizer import PriceOptimizer

        model_manager = get_model_manager()
        _process_optimizer = PriceOptimizer(model_manager=model_manager)
    return _process_optimizer


def _run_scenario_in_process(
    context_dict: dict,
    scenario_type: str,
    scenario_name: str,
    modifier: float,
    segment: str | None,
) -> dict:
    """Run a single scenario in a worker process.

    This is a module-level function that can be pickled and sent to
    worker processes via ProcessPoolExecutor.

    Args:
        context_dict: Market context as dictionary (for pickling).
        scenario_type: Type of sensitivity (elasticity, demand, cost).
        scenario_name: Name of the scenario.
        modifier: Multiplier to apply.
        segment: Optional customer segment.

    Returns:
        Dictionary with scenario results (for pickling back).
    """
    # Remove computed field if present (can't be passed to model constructor)
    context_dict = {k: v for k, v in context_dict.items() if k != "supply_demand_ratio"}

    # Apply scenario modifier directly to dict before creating context
    if scenario_type == "cost":
        context_dict["historical_cost_of_ride"] *= modifier
    elif scenario_type == "demand":
        context_dict["number_of_riders"] = max(1, int(context_dict["number_of_riders"] * modifier))

    # Reconstruct MarketContext from modified dict
    modified_context = MarketContext(**context_dict)

    # Get process-local optimizer and run
    optimizer = _get_process_optimizer()
    result = optimizer.optimize(modified_context, segment=segment, use_cache=False)

    return {
        "scenario_name": scenario_name,
        "scenario_type": scenario_type,
        "modifier": modifier,
        "optimal_price": result.optimal_price,
        "expected_profit": result.expected_profit,
        "expected_demand": result.expected_demand,
    }


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

    Uses ProcessPoolExecutor for true CPU parallelism by running optimizations
    in separate processes, bypassing Python's GIL.
    """

    # Default number of worker processes (CPU count, minimum 4)
    DEFAULT_MAX_WORKERS = max(4, os.cpu_count() or 4)

    def __init__(
        self,
        price_optimizer: PriceOptimizer,  # noqa: ARG002 - kept for API compatibility
        max_workers: int | None = None,
    ) -> None:
        """Initialize the sensitivity service.

        Args:
            price_optimizer: PriceOptimizer instance (kept for API compatibility;
                           worker processes initialize their own optimizers).
            max_workers: Maximum worker processes for parallel execution.
                         Defaults to max(4, CPU count).
        """
        self._max_workers = max_workers or self.DEFAULT_MAX_WORKERS
        # ProcessPoolExecutor for true parallelism (bypasses GIL)
        self._executor = ProcessPoolExecutor(max_workers=self._max_workers)
        logger.info(f"SensitivityService initialized with {self._max_workers} worker processes")

    def __del__(self) -> None:
        """Cleanup executor on deletion."""
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=False)

    async def _run_single_scenario(
        self,
        context: MarketContext,
        scenario_type: ScenarioType,
        scenario: dict[str, str | float],
        segment: str | None = None,
    ) -> ScenarioResult:
        """Run a single sensitivity scenario in a worker process.

        Submits the scenario to ProcessPoolExecutor for true parallel execution.

        Args:
            context: Base market context.
            scenario_type: Type of sensitivity (elasticity, demand, cost).
            scenario: Scenario definition with name and modifier.
            segment: Optional customer segment.

        Returns:
            ScenarioResult with optimization results for this scenario.
        """
        loop = asyncio.get_running_loop()

        # Convert to dict for pickling across process boundary
        context_dict = context.model_dump()

        # Submit to process pool
        result_dict = await loop.run_in_executor(
            self._executor,
            _run_scenario_in_process,
            context_dict,
            scenario_type,
            str(scenario["name"]),
            float(scenario["modifier"]),
            segment,
        )

        return ScenarioResult(**result_dict)

    async def run_sensitivity_analysis(
        self,
        context: MarketContext,
        segment: str | None = None,
    ) -> SensitivityResult:
        """Run complete sensitivity analysis across all scenario types.

        Executes all 17 scenarios (7 elasticity + 5 demand + 5 cost) in parallel
        using ProcessPoolExecutor for true CPU parallelism. Each worker process
        initializes its own models and runs optimizations independently.

        Target performance: < 3 seconds for all scenarios.

        Args:
            context: Base market context for analysis.
            segment: Optional customer segment.

        Returns:
            SensitivityResult with all scenarios, confidence bands, and metrics.
        """
        start_time = time.perf_counter()

        logger.info(
            f"Starting sensitivity analysis for context: "
            f"riders={context.number_of_riders}, cost=${context.historical_cost_of_ride}, "
            f"workers={self._max_workers}"
        )

        # Create all scenario coroutines for parallel execution via thread pool
        coroutines = []

        for scenario in SENSITIVITY_SCENARIOS["elasticity"]:
            coroutines.append(self._run_single_scenario(context, "elasticity", scenario, segment))

        for scenario in SENSITIVITY_SCENARIOS["demand"]:
            coroutines.append(self._run_single_scenario(context, "demand", scenario, segment))

        for scenario in SENSITIVITY_SCENARIOS["cost"]:
            coroutines.append(self._run_single_scenario(context, "cost", scenario, segment))

        # Run all scenarios in parallel via thread pool
        results = await asyncio.gather(*coroutines)

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
        self,
        confidence_band: ConfidenceBand,
        base_price: float,  # noqa: ARG002
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


def get_sensitivity_service() -> SensitivityService:
    """Get or create singleton SensitivityService instance.

    Returns:
        SensitivityService instance with PriceOptimizer dependency.

    Raises:
        FileNotFoundError: If model files are not found.
        RuntimeError: If models fail to load.
    """
    global _sensitivity_service
    if _sensitivity_service is None:
        from src.ml.price_optimizer import get_price_optimizer

        price_optimizer = get_price_optimizer()
        _sensitivity_service = SensitivityService(price_optimizer=price_optimizer)
    return _sensitivity_service
