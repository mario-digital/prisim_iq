"""Pricing service for orchestrating price optimization.

This service coordinates the Segmenter, ModelManager, PriceOptimizer,
and RulesEngine to produce complete pricing recommendations.
"""

from __future__ import annotations

import time
from datetime import datetime
from functools import lru_cache
from typing import Literal

from loguru import logger

from src.ml.model_manager import ModelManager, get_model_manager
from src.ml.price_optimizer import PriceOptimizer, get_price_optimizer
from src.ml.segmenter import Segmenter
from src.rules.engine import RulesEngine
from src.schemas.market import MarketContext
from src.schemas.pricing import PricingResult
from src.schemas.segment import SegmentDetails, SegmentResult


def _segment_result_to_details(result: SegmentResult) -> SegmentDetails:
    """Convert internal SegmentResult to API-facing SegmentDetails.

    Adds human-readable description and confidence level based on centroid distance.

    Args:
        result: Internal segment classification result.

    Returns:
        SegmentDetails with additional human-readable fields.
    """
    # Generate human-readable description from segment name
    parts = result.segment_name.split("_")
    if len(parts) >= 3:
        location, time_profile, vehicle = parts[0], parts[1], parts[2]
        description = (
            f"{location} area during {time_profile.lower()} hours "
            f"with {vehicle.lower()} vehicle preference"
        )
    else:
        description = f"Market segment: {result.segment_name}"

    # Determine confidence level based on centroid distance
    # Lower distance = higher confidence
    if result.centroid_distance < 1.0:
        confidence_level: Literal["high", "medium", "low"] = "high"
    elif result.centroid_distance < 2.0:
        confidence_level = "medium"
    else:
        confidence_level = "low"

    return SegmentDetails(
        segment_name=result.segment_name,
        cluster_id=result.cluster_id,
        characteristics=result.characteristics,
        centroid_distance=result.centroid_distance,
        human_readable_description=description,
        confidence_level=confidence_level,
    )


def _distance_to_confidence(centroid_distance: float) -> float:
    """Convert centroid distance to confidence score (0-1).

    Uses exponential decay: confidence = exp(-distance / scale).
    Lower distance = higher confidence.

    Args:
        centroid_distance: Distance from cluster centroid.

    Returns:
        Confidence score between 0.0 and 1.0.
    """
    import math

    # Scale factor: at distance=2, confidence ≈ 0.37
    scale = 2.0
    confidence = math.exp(-centroid_distance / scale)
    return round(min(max(confidence, 0.0), 1.0), 4)


class PricingService:
    """Service for orchestrating complete price optimization.

    Coordinates:
    1. Segmenter - Classifies market context into segments
    2. PriceOptimizer - Finds profit-maximizing price using ML
    3. RulesEngine - Applies business rules (floors, caps, discounts)
    """

    def __init__(
        self,
        segmenter: Segmenter,
        model_manager: ModelManager,
        optimizer: PriceOptimizer,
        rules_engine: RulesEngine,
        model_name: str = "xgboost",
    ) -> None:
        """Initialize the pricing service.

        Args:
            segmenter: Fitted Segmenter instance for classification.
            model_manager: ModelManager with loaded prediction models.
            optimizer: PriceOptimizer for finding optimal prices.
            rules_engine: RulesEngine for applying business rules.
            model_name: Name of ML model to use for predictions.
        """
        self._segmenter = segmenter
        self._model_manager = model_manager
        self._optimizer = optimizer
        self._rules_engine = rules_engine
        self._model_name = model_name

    async def get_recommendation(
        self,
        context: MarketContext,
    ) -> PricingResult:
        """Get complete pricing recommendation for market context.

        Orchestrates the full pricing pipeline:
        1. Classify segment
        2. Run price optimization
        3. Apply business rules
        4. Compile results

        Args:
            context: Market conditions and customer profile.

        Returns:
            Complete PricingResult with recommendation and explanation.

        Raises:
            RuntimeError: If segmenter is not fitted.
            FileNotFoundError: If model files are missing.
        """
        start_time = time.perf_counter()

        # 1. Classify segment
        logger.debug("Classifying market segment...")
        segment_result = self._segmenter.classify(context)
        segment_details = _segment_result_to_details(segment_result)
        segment_name = segment_result.segment_name

        logger.info(
            f"Segment classified: {segment_name} "
            f"(distance={segment_result.centroid_distance:.3f})"
        )

        # 2. Run price optimization
        logger.debug("Running price optimization...")
        optimization = self._optimizer.optimize(
            context=context,
            segment=segment_name,
            use_cache=True,
        )

        price_before_rules = optimization.optimal_price
        logger.info(
            f"ML optimization: ${price_before_rules:.2f}, "
            f"uplift={optimization.profit_uplift_percent:.1f}%"
        )

        # 3. Apply business rules
        logger.debug("Applying business rules...")
        rules_result = self._rules_engine.apply(
            context=context,
            optimal_price=price_before_rules,
        )

        logger.info(
            f"Rules applied: {len(rules_result.applied_rules)} rules, "
            f"adjustment={rules_result.total_adjustment_percent:+.1f}%"
        )

        # 4. Calculate final metrics
        end_time = time.perf_counter()
        processing_time_ms = (end_time - start_time) * 1000

        # Calculate confidence score from centroid distance
        confidence_score = _distance_to_confidence(segment_result.centroid_distance)

        # Compile result
        result = PricingResult(
            recommended_price=rules_result.final_price,
            confidence_score=confidence_score,
            expected_demand=optimization.expected_demand,
            expected_profit=optimization.expected_profit,
            baseline_profit=optimization.baseline_profit,
            profit_uplift_percent=optimization.profit_uplift_percent,
            segment=segment_details,
            model_used=self._model_name,
            rules_applied=rules_result.applied_rules,
            price_before_rules=price_before_rules,
            price_demand_curve=optimization.price_demand_curve,
            processing_time_ms=round(processing_time_ms, 2),
            timestamp=datetime.utcnow(),
        )

        logger.info(
            f"Pricing complete: ${result.recommended_price:.2f}, "
            f"confidence={result.confidence_score:.2f}, "
            f"time={processing_time_ms:.1f}ms"
        )

        return result


# Singleton instance
_pricing_service: PricingService | None = None


@lru_cache(maxsize=1)
def _load_segmenter() -> Segmenter:
    """Load segmenter model once and cache it."""
    logger.info("Loading segmenter for pricing service...")
    return Segmenter.load()


@lru_cache(maxsize=1)
def _load_rules_engine() -> RulesEngine:
    """Load rules engine once and cache it."""
    logger.info("Loading rules engine for pricing service...")
    return RulesEngine()


def get_pricing_service() -> PricingService:
    """Get or create singleton PricingService instance.

    Returns:
        PricingService instance with all dependencies loaded.

    Raises:
        FileNotFoundError: If model files are not found.
        RuntimeError: If models fail to load.
    """
    global _pricing_service

    if _pricing_service is None:
        logger.info("Initializing PricingService...")

        # Load dependencies
        segmenter = _load_segmenter()
        model_manager = get_model_manager()
        optimizer = get_price_optimizer(model_manager)
        rules_engine = _load_rules_engine()

        _pricing_service = PricingService(
            segmenter=segmenter,
            model_manager=model_manager,
            optimizer=optimizer,
            rules_engine=rules_engine,
            model_name="xgboost",
        )

        logger.info("PricingService initialized successfully")

    return _pricing_service

