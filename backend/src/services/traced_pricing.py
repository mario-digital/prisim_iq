"""Traced pricing service for capturing complete decision pipeline.

This module wraps the PricingService with decision tracing to capture
every step of the pricing pipeline for audit and explainability.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from loguru import logger

from src.explainability.decision_trace import (
    DecisionTrace,
    DecisionTracer,
)
from src.ml.model_manager import ModelManager, get_model_manager
from src.ml.price_optimizer import PriceOptimizer, get_price_optimizer
from src.ml.segmenter import Segmenter
from src.rules.engine import RulesEngine
from src.schemas.market import MarketContext
from src.schemas.pricing import PricingResult
from src.schemas.segment import SegmentDetails, SegmentResult

if TYPE_CHECKING:
    from typing import Literal


def _segment_result_to_details(result: SegmentResult) -> SegmentDetails:
    """Convert internal SegmentResult to API-facing SegmentDetails."""
    parts = result.segment_name.split("_")
    if len(parts) >= 3:
        location, time_profile, vehicle = parts[0], parts[1], parts[2]
        description = (
            f"{location} area during {time_profile.lower()} hours "
            f"with {vehicle.lower()} vehicle preference"
        )
    else:
        description = f"Market segment: {result.segment_name}"

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
    """Convert centroid distance to confidence score (0-1)."""
    import math

    scale = 2.0
    confidence = math.exp(-centroid_distance / scale)
    return round(min(max(confidence, 0.0), 1.0), 4)


class TracedPricingService:
    """Pricing service with full decision tracing.

    Wraps the pricing pipeline with a DecisionTracer to capture
    every step: input validation, segmentation, external factors,
    model prediction, optimization, and rules application.
    """

    def __init__(
        self,
        segmenter: Segmenter,
        model_manager: ModelManager,
        optimizer: PriceOptimizer,
        rules_engine: RulesEngine,
        model_name: str = "xgboost",
    ) -> None:
        """Initialize the traced pricing service.

        Args:
            segmenter: Fitted Segmenter instance.
            model_manager: ModelManager with loaded models.
            optimizer: PriceOptimizer for finding optimal prices.
            rules_engine: RulesEngine for business rules.
            model_name: Primary model for optimization.
        """
        self._segmenter = segmenter
        self._model_manager = model_manager
        self._optimizer = optimizer
        self._rules_engine = rules_engine
        self._model_name = model_name

    async def get_recommendation_with_trace(
        self,
        context: MarketContext,
        log_trace: bool = False,
    ) -> tuple[PricingResult, DecisionTrace]:
        """Get pricing recommendation with complete decision trace.

        Orchestrates the full pipeline while capturing each step:
        1. Input validation
        2. Segment classification
        3. External factors (placeholder for n8n integration)
        4. Demand prediction (all models)
        5. Price optimization
        6. Rules application
        7. Explanation generation

        Args:
            context: Market conditions and customer profile.
            log_trace: Whether to log trace to audit file.

        Returns:
            Tuple of (PricingResult, DecisionTrace).
        """
        tracer = DecisionTracer()
        total_start = time.perf_counter()

        # Step 1: Input Validation
        step_start = time.perf_counter()
        try:
            # Pydantic already validated, but we trace the check
            context_dict = context.model_dump()
            tracer.add_step(
                step_name="input_validation",
                inputs={"context_fields": list(context_dict.keys())},
                outputs={"valid": True, "field_count": len(context_dict)},
                duration_ms=(time.perf_counter() - step_start) * 1000,
                status="success",
            )
        except Exception as e:
            tracer.add_step(
                step_name="input_validation",
                inputs={},
                outputs={},
                duration_ms=(time.perf_counter() - step_start) * 1000,
                status="error",
                error_message=str(e),
            )
            raise

        # Step 2: Segment Classification
        step_start = time.perf_counter()
        try:
            segment_result = self._segmenter.classify(context)
            segment_details = _segment_result_to_details(segment_result)
            segment_name = segment_result.segment_name

            tracer.add_step(
                step_name="segment_classification",
                inputs={
                    "location": context.location_category,
                    "vehicle": context.vehicle_type,
                    "time_of_booking": context.time_of_booking,
                },
                outputs={
                    "segment": segment_name,
                    "cluster_id": segment_result.cluster_id,
                    "confidence": segment_details.confidence_level,
                    "centroid_distance": round(segment_result.centroid_distance, 4),
                },
                duration_ms=(time.perf_counter() - step_start) * 1000,
                status="success",
            )
        except Exception as e:
            tracer.add_step(
                step_name="segment_classification",
                inputs={},
                outputs={},
                duration_ms=(time.perf_counter() - step_start) * 1000,
                status="error",
                error_message=str(e),
            )
            raise

        # Step 3: External Factors (placeholder for n8n integration)
        step_start = time.perf_counter()
        external_factors = {
            "weather": "normal",
            "events": "none",
            "fuel_price_index": 1.0,
        }
        tracer.add_step(
            step_name="external_factors",
            inputs={"location": context.location_category},
            outputs=external_factors,
            duration_ms=(time.perf_counter() - step_start) * 1000,
            status="success",
        )

        # Step 4: Demand Prediction (all models for agreement check)
        step_start = time.perf_counter()
        try:
            # Get baseline price for model comparison
            baseline_price = context.historical_cost_of_ride

            # Get predictions from all models
            all_predictions = self._model_manager.get_all_predictions(
                context=context,
                price=baseline_price,
                segment=segment_name,
            )

            tracer.add_step(
                step_name="demand_prediction",
                inputs={
                    "price": baseline_price,
                    "segment": segment_name,
                    "models": list(all_predictions.keys()),
                },
                outputs={
                    "predictions": {k: round(v, 4) for k, v in all_predictions.items()},
                    "primary_model": self._model_name,
                    "primary_prediction": round(
                        all_predictions.get(self._model_name, 0), 4
                    ),
                },
                duration_ms=(time.perf_counter() - step_start) * 1000,
                status="success",
            )

            # Calculate model agreement
            tracer.set_model_agreement(all_predictions)

        except Exception as e:
            tracer.add_step(
                step_name="demand_prediction",
                inputs={},
                outputs={},
                duration_ms=(time.perf_counter() - step_start) * 1000,
                status="error",
                error_message=str(e),
            )
            raise

        # Step 5: Price Optimization
        step_start = time.perf_counter()
        try:
            optimization = self._optimizer.optimize(
                context=context,
                segment=segment_name,
                use_cache=True,
            )
            price_before_rules = optimization.optimal_price

            tracer.add_step(
                step_name="price_optimization",
                inputs={
                    "segment": segment_name,
                    "baseline_price": context.historical_cost_of_ride,
                },
                outputs={
                    "optimal_price": round(price_before_rules, 2),
                    "expected_demand": round(optimization.expected_demand, 4),
                    "expected_profit": round(optimization.expected_profit, 2),
                    "profit_uplift_percent": round(
                        optimization.profit_uplift_percent, 2
                    ),
                },
                duration_ms=(time.perf_counter() - step_start) * 1000,
                status="success",
            )
        except Exception as e:
            tracer.add_step(
                step_name="price_optimization",
                inputs={},
                outputs={},
                duration_ms=(time.perf_counter() - step_start) * 1000,
                status="error",
                error_message=str(e),
            )
            raise

        # Step 6: Rules Application
        step_start = time.perf_counter()
        try:
            rules_result = self._rules_engine.apply(
                context=context,
                optimal_price=price_before_rules,
            )

            tracer.add_step(
                step_name="rules_application",
                inputs={
                    "price_before_rules": round(price_before_rules, 2),
                    "loyalty_status": context.customer_loyalty_status,
                },
                outputs={
                    "final_price": round(rules_result.final_price, 2),
                    "rules_applied": [r.rule_name for r in rules_result.applied_rules],
                    "rules_count": len(rules_result.applied_rules),
                    "total_adjustment_percent": round(
                        rules_result.total_adjustment_percent, 2
                    ),
                },
                duration_ms=(time.perf_counter() - step_start) * 1000,
                status="success",
            )
        except Exception as e:
            tracer.add_step(
                step_name="rules_application",
                inputs={},
                outputs={},
                duration_ms=(time.perf_counter() - step_start) * 1000,
                status="error",
                error_message=str(e),
            )
            raise

        # Step 7: Explanation Generation
        step_start = time.perf_counter()
        model_agreement = tracer.model_agreement
        explanation_summary = _generate_explanation_summary(
            segment_name=segment_name,
            price_before_rules=price_before_rules,
            final_price=rules_result.final_price,
            rules_applied=rules_result.applied_rules,
            model_agreement=model_agreement,
        )

        tracer.add_step(
            step_name="explanation_generation",
            inputs={"trace_id": tracer.trace_id},
            outputs={
                "summary": explanation_summary,
                "model_agreement_status": model_agreement.status
                if model_agreement
                else "unknown",
            },
            duration_ms=(time.perf_counter() - step_start) * 1000,
            status="success",
        )

        # Calculate final metrics
        processing_time_ms = (time.perf_counter() - total_start) * 1000
        confidence_score = _distance_to_confidence(segment_result.centroid_distance)

        # Create pricing result
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
            timestamp=datetime.now(UTC),
        )

        # Finalize trace
        trace = tracer.finalize(
            final_result={
                "recommended_price": result.recommended_price,
                "confidence_score": result.confidence_score,
                "segment": segment_name,
                "profit_uplift_percent": result.profit_uplift_percent,
            },
            log_to_file=log_trace,
        )

        logger.info(
            f"Traced pricing complete: ${result.recommended_price:.2f}, "
            f"trace_id={trace.trace_id[:8]}, "
            f"steps={len(trace.steps)}, "
            f"time={processing_time_ms:.1f}ms"
        )

        return result, trace


def _generate_explanation_summary(
    segment_name: str,
    price_before_rules: float,
    final_price: float,
    rules_applied: list,
    model_agreement: object | None,
) -> str:
    """Generate human-readable explanation summary."""
    parts = [f"Price optimized for {segment_name} segment."]

    if rules_applied:
        rule_names = [r.rule_name for r in rules_applied]
        parts.append(f"Applied {len(rules_applied)} rules: {', '.join(rule_names)}.")

    if price_before_rules != final_price:
        diff = final_price - price_before_rules
        direction = "increased" if diff > 0 else "decreased"
        parts.append(
            f"Price {direction} from ${price_before_rules:.2f} to ${final_price:.2f}."
        )

    if model_agreement and hasattr(model_agreement, "status"):
        if model_agreement.status == "full_agreement":
            parts.append("All prediction models agree on this pricing.")
        elif model_agreement.status == "divergent":
            parts.append("Note: Models show divergent predictions.")

    return " ".join(parts)


# Singleton instance
_traced_pricing_service: TracedPricingService | None = None


def get_traced_pricing_service() -> TracedPricingService:
    """Get or create singleton TracedPricingService instance.

    Returns:
        TracedPricingService instance with all dependencies loaded.
    """
    global _traced_pricing_service

    if _traced_pricing_service is None:
        logger.info("Initializing TracedPricingService...")

        segmenter = Segmenter.load()
        model_manager = get_model_manager()
        optimizer = get_price_optimizer(model_manager)
        rules_engine = RulesEngine()

        _traced_pricing_service = TracedPricingService(
            segmenter=segmenter,
            model_manager=model_manager,
            optimizer=optimizer,
            rules_engine=rules_engine,
            model_name="xgboost",
        )

        logger.info("TracedPricingService initialized successfully")

    return _traced_pricing_service

