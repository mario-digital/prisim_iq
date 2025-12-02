"""Price optimizer for finding profit-maximizing prices.

This module provides the PriceOptimizer class that uses grid search
to find the optimal price point that maximizes profit given predicted demand.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import TYPE_CHECKING

import numpy as np
from loguru import logger

from src.config import Settings, get_settings
from src.schemas.market import MarketContext
from src.schemas.optimization import OptimizationResult, PriceDemandPoint

if TYPE_CHECKING:
    from src.ml.model_manager import ModelManager


class PriceOptimizer:
    """Optimizer for finding profit-maximizing prices.

    Uses grid search over price range to find the price that maximizes
    profit = (price - cost) * predicted_demand(price).
    """

    def __init__(
        self,
        model_manager: ModelManager,
        settings: Settings | None = None,
    ) -> None:
        """Initialize the price optimizer.

        Args:
            model_manager: ModelManager instance for demand predictions.
            settings: Application settings. Defaults to global settings.
        """
        self._model_manager = model_manager
        self._settings = settings or get_settings()
        self._cache: dict[str, OptimizationResult] = {}

    def _compute_profit(self, price: float, cost: float, demand: float) -> float:
        """Compute profit for a given price, cost, and demand.

        Args:
            price: Selling price.
            cost: Cost/baseline price.
            demand: Predicted demand (0-1).

        Returns:
            Profit value. Returns 0 if profit would be negative.
        """
        profit = (price - cost) * demand
        return max(profit, 0.0)

    def _hash_context(self, context: MarketContext) -> str:
        """Create a hash key for caching based on context.

        Args:
            context: Market context to hash.

        Returns:
            Hash string for cache key.
        """
        # Convert context to JSON for consistent hashing
        context_dict = context.model_dump()
        context_json = json.dumps(context_dict, sort_keys=True)
        return hashlib.md5(context_json.encode()).hexdigest()

    def optimize(
        self,
        context: MarketContext,
        segment: str | None = None,
        use_cache: bool = True,
    ) -> OptimizationResult:
        """Find the profit-maximizing price for a given context.

        Uses grid search at price_step increments within configured bounds.

        Args:
            context: Market context for optimization.
            segment: Optional customer segment for prediction.
            use_cache: Whether to use cached results. Defaults to True.

        Returns:
            OptimizationResult with optimal price and metrics.
        """
        # Check cache
        cache_key = f"{self._hash_context(context)}_{segment or 'None'}"
        if use_cache and cache_key in self._cache:
            logger.debug(f"Cache hit for context hash: {cache_key[:8]}...")
            return self._cache[cache_key]

        start_time = time.perf_counter()

        cost = context.historical_cost_of_ride
        price_min = max(self._settings.price_min, cost)  # Don't go below cost
        price_max = self._settings.price_max
        price_step = self._settings.price_step

        # Generate price range
        prices = np.arange(price_min, price_max + price_step, price_step)

        best_profit = -float("inf")
        best_price = cost
        best_demand = 0.0

        # Track all results for curve
        all_results: list[tuple[float, float, float]] = []

        # Grid search
        for price in prices:
            demand = self._model_manager.predict(
                context=context,
                price=float(price),
                segment=segment,
            )
            profit = self._compute_profit(float(price), cost, demand)
            all_results.append((float(price), demand, profit))

            if profit > best_profit:
                best_profit = profit
                best_price = float(price)
                best_demand = demand

        # Calculate baseline
        baseline_demand = self._model_manager.predict(
            context=context,
            price=cost,
            segment=segment,
        )
        baseline_profit = self._compute_profit(cost, cost, baseline_demand)

        # Calculate uplift
        if baseline_profit > 0:
            profit_uplift_percent = ((best_profit - baseline_profit) / baseline_profit) * 100
        else:
            profit_uplift_percent = 100.0 if best_profit > 0 else 0.0

        # Build price-demand curve (sample points for visualization)
        curve_points = self._sample_curve_points(all_results)

        end_time = time.perf_counter()
        optimization_time_ms = (end_time - start_time) * 1000

        result = OptimizationResult(
            optimal_price=round(best_price, 2),
            expected_demand=round(best_demand, 4),
            expected_profit=round(best_profit, 2),
            baseline_price=round(cost, 2),
            baseline_profit=round(baseline_profit, 2),
            profit_uplift_percent=round(profit_uplift_percent, 2),
            price_demand_curve=curve_points,
            optimization_time_ms=round(optimization_time_ms, 2),
        )

        # Update cache
        if use_cache:
            self._update_cache(cache_key, result)

        logger.info(
            f"Optimization complete: price=${result.optimal_price:.2f}, "
            f"profit=${result.expected_profit:.2f}, "
            f"uplift={result.profit_uplift_percent:.1f}%, "
            f"time={result.optimization_time_ms:.1f}ms"
        )

        return result

    def _sample_curve_points(
        self, all_results: list[tuple[float, float, float]], num_points: int = 20
    ) -> list[PriceDemandPoint]:
        """Sample points from full results for visualization curve.

        Args:
            all_results: Full list of (price, demand, profit) tuples.
            num_points: Number of points to sample.

        Returns:
            List of PriceDemandPoint for visualization.
        """
        if len(all_results) <= num_points:
            indices = range(len(all_results))
        else:
            # Evenly sample across the range
            indices = np.linspace(0, len(all_results) - 1, num_points, dtype=int)

        return [
            PriceDemandPoint(
                price=round(all_results[i][0], 2),
                demand=round(all_results[i][1], 4),
                profit=round(all_results[i][2], 2),
            )
            for i in indices
        ]

    def _update_cache(self, key: str, result: OptimizationResult) -> None:
        """Update cache with LRU eviction.

        Args:
            key: Cache key.
            result: Result to cache.
        """
        max_size = self._settings.optimization_cache_size

        # Simple LRU: if at capacity, remove oldest
        if len(self._cache) >= max_size:
            # Remove first item (oldest in dict order for Python 3.7+)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        self._cache[key] = result

    def clear_cache(self) -> None:
        """Clear the optimization cache."""
        self._cache.clear()
        logger.info("Optimization cache cleared")

    def get_cache_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats.
        """
        return {
            "size": len(self._cache),
            "max_size": self._settings.optimization_cache_size,
        }


# Singleton instance
_price_optimizer: PriceOptimizer | None = None


def get_price_optimizer(model_manager: ModelManager | None = None) -> PriceOptimizer:
    """Get or create singleton PriceOptimizer instance.

    Args:
        model_manager: ModelManager instance. Required on first call.

    Returns:
        PriceOptimizer instance.

    Raises:
        ValueError: If model_manager not provided on first call.
    """
    global _price_optimizer
    if _price_optimizer is None:
        if model_manager is None:
            from src.ml.model_manager import get_model_manager
            model_manager = get_model_manager()
        _price_optimizer = PriceOptimizer(model_manager=model_manager)
    return _price_optimizer

