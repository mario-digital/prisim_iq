"""Explanation service for generating comprehensive price explanations.

This module orchestrates the full explanation pipeline:
- Price recommendation (via TracedPricingService)
- Feature importance (global + local SHAP)
- Decision trace
- Model agreement
- Natural language generation
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import TYPE_CHECKING

import numpy as np
from loguru import logger

from src.explainability.decision_trace import ModelAgreement
from src.explainability.importance_service import FeatureImportanceService
from src.ml.model_manager import ModelManager, get_model_manager
from src.ml.price_optimizer import get_price_optimizer
from src.ml.segmenter import Segmenter
from src.rules.engine import RulesEngine
from src.schemas.explainability import FeatureContribution
from src.schemas.explanation import ExplainRequest, PriceExplanation
from src.schemas.pricing import PricingResult
from src.services.traced_pricing import TracedPricingService

if TYPE_CHECKING:
    from src.schemas.market import MarketContext


def generate_narrative(
    result: PricingResult,
    importance: list[FeatureContribution],
    _context: MarketContext,  # Reserved for future context-aware narratives
) -> str:
    """Generate human-readable explanation.

    Template-based, NOT LLM-generated (for speed).

    Args:
        result: The pricing result.
        importance: Ranked feature contributions.
        _context: Market context (reserved for future context-aware narratives).

    Returns:
        Natural language summary of the pricing recommendation.
    """
    top_factors = importance[:3]

    narrative = f"The recommended price of ${result.recommended_price:.2f} "

    # Add primary driver
    if top_factors:
        primary = top_factors[0]
        narrative += f"is primarily driven by {primary.description.lower()} "
        narrative += f"(contributing {primary.importance * 100:.0f}% to the decision). "

        # Add secondary factors
        if len(top_factors) > 1:
            secondary = [f.display_name.lower() for f in top_factors[1:]]
            narrative += f"Additional factors include {' and '.join(secondary)}. "
    else:
        narrative += "is based on the market conditions provided. "

    # Add profit context
    narrative += f"This price is expected to generate ${result.expected_profit:.2f} "
    narrative += f"in profit, a {result.profit_uplift_percent:.1f}% improvement "
    narrative += "over the baseline price."

    return narrative


def extract_key_factors(
    importance: list[FeatureContribution],
    context: MarketContext,
) -> list[str]:
    """Extract top key factors as short descriptions.

    Args:
        importance: Ranked feature contributions.
        context: Market context for contextual descriptions.

    Returns:
        List of short factor descriptions (e.g., "High demand", "Evening peak").
    """
    factor_mappings = {
        "supply_demand_ratio": lambda _: (
            "High demand" if context.supply_demand_ratio < 1.0 else "Balanced supply"
        ),
        "time_of_booking": lambda _: f"{context.time_of_booking} hours",
        "vehicle_type": lambda _: f"{context.vehicle_type} vehicle",
        "location_category": lambda _: f"{context.location_category} location",
        "customer_loyalty_status": lambda _: f"{context.customer_loyalty_status} loyalty",
        "number_of_riders": lambda _: (
            "High rider demand" if context.number_of_riders > 30 else "Normal demand"
        ),
        "number_of_drivers": lambda _: (
            "Low driver supply" if context.number_of_drivers < 20 else "Normal supply"
        ),
        "expected_ride_duration": lambda _: (
            f"{context.expected_ride_duration} min ride"
        ),
        "historical_cost_of_ride": lambda _: (
            f"${context.historical_cost_of_ride:.0f} baseline"
        ),
        "average_ratings": lambda _: f"{context.average_ratings:.1f}★ rating",
        "number_of_past_rides": lambda _: f"{context.number_of_past_rides} past rides",
    }

    key_factors = []
    for contrib in importance[:5]:  # Top 5 factors
        mapper = factor_mappings.get(contrib.feature_name)
        if mapper:
            key_factors.append(mapper(contrib))
        else:
            key_factors.append(contrib.display_name)

    return key_factors[:5]  # Ensure max 5


class ExplanationService:
    """Service for generating comprehensive price explanations.

    Orchestrates:
    - Price recommendation via TracedPricingService
    - Global and local feature importance
    - Decision trace
    - Model agreement analysis
    - Natural language summary generation
    """

    def __init__(
        self,
        traced_pricing: TracedPricingService,
        model_manager: ModelManager,
        feature_names: list[str],
    ) -> None:
        """Initialize the explanation service.

        Args:
            traced_pricing: Service for traced pricing recommendations.
            model_manager: Manager for ML models.
            feature_names: List of feature names for importance calculation.
        """
        self._traced_pricing = traced_pricing
        self._model_manager = model_manager
        self._feature_names = feature_names

    async def explain(
        self,
        request: ExplainRequest,
    ) -> PriceExplanation:
        """Generate a complete price explanation.

        Args:
            request: Explanation request with context and options.

        Returns:
            Complete PriceExplanation with all components.
        """
        start_time = time.perf_counter()
        context = request.context

        logger.info(
            f"Generating explanation: "
            f"location={context.location_category}, "
            f"vehicle={context.vehicle_type}, "
            f"include_trace={request.include_trace}, "
            f"include_shap={request.include_shap}"
        )

        # Step 1: Get pricing recommendation with trace
        result, trace = await self._traced_pricing.get_recommendation_with_trace(
            context=context,
            log_trace=False,
        )

        # Step 2: Calculate feature importance
        local_importance, global_importance = self._calculate_importance(
            context=context,
            result=result,
            include_shap=request.include_shap,
        )

        # Step 3: Get model predictions and calculate agreement
        # NOTE: Always recalculate agreement from fresh predictions to ensure consistency.
        # The trace may contain its own model_agreement (used for trace output), but the
        # top-level response agreement must match the current model_predictions to avoid
        # subtle inconsistencies if traces are cached or from different computation paths.
        model_predictions = self._model_manager.get_all_predictions(
            context=context,
            price=result.recommended_price,
            segment=result.segment.segment_name,
        )
        model_agreement = self._calculate_agreement(model_predictions)

        # Step 4: Generate natural language summary
        natural_language_summary = generate_narrative(
            result,
            local_importance if local_importance else global_importance,
            context,  # Passed positionally for underscore-prefixed parameter
        )

        # Step 5: Extract key factors
        key_factors = extract_key_factors(
            importance=local_importance if local_importance else global_importance,
            context=context,
        )

        # Calculate explanation time
        explanation_time_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            f"Explanation generated: "
            f"price=${result.recommended_price:.2f}, "
            f"factors={len(local_importance)}, "
            f"time={explanation_time_ms:.1f}ms"
        )

        return PriceExplanation(
            recommendation=result,
            feature_importance=local_importance,
            global_importance=global_importance,
            decision_trace=trace if request.include_trace else None,
            model_agreement=model_agreement,
            model_predictions={k: round(v, 4) for k, v in model_predictions.items()},
            natural_language_summary=natural_language_summary,
            key_factors=key_factors,
            explanation_time_ms=round(explanation_time_ms, 2),
            timestamp=datetime.utcnow(),
        )

    def _calculate_importance(
        self,
        context: MarketContext,
        result: PricingResult,
        include_shap: bool,
    ) -> tuple[list[FeatureContribution], list[FeatureContribution]]:
        """Calculate global and local feature importance.

        Args:
            context: Market context.
            result: Pricing result.
            include_shap: Whether to calculate SHAP importance.

        Returns:
            Tuple of (local_importance, global_importance).
        """
        # Ensure models are loaded
        self._model_manager._ensure_loaded()

        # Get the model
        model = self._model_manager.models.get(result.model_used)
        if model is None:
            logger.warning(f"Model {result.model_used} not found, using first available")
            model_name = next(iter(self._model_manager.models.keys()))
            model = self._model_manager.models[model_name]
        else:
            model_name = result.model_used

        # Build feature vector from context
        X = self._build_feature_vector(context, result)

        # Initialize importance service (no background data for speed)
        importance_service = FeatureImportanceService(
            model=model,
            model_type=model_name,  # type: ignore
            feature_names=self._feature_names,
            background_data=None,
        )

        # Get global importance
        global_result = importance_service.get_global_importance()
        global_importance = global_result.contributions

        # Get local SHAP importance if requested
        if include_shap:
            try:
                local_result = importance_service.get_local_importance(X)
                local_importance = local_result.contributions
            except Exception as e:
                logger.warning(f"SHAP calculation failed, using global: {e}")
                local_importance = global_importance
        else:
            local_importance = global_importance

        return local_importance, global_importance

    def _build_feature_vector(
        self,
        context: MarketContext,
        result: PricingResult,
    ) -> np.ndarray:
        """Build feature vector from context for model prediction.

        Args:
            context: Market context.
            result: Pricing result with price and segment.

        Returns:
            NumPy array of feature values.
        """
        # Use ModelManager's internal conversion method
        df = self._model_manager._context_to_features(
            context=context,
            price=result.recommended_price,
            segment=result.segment.segment_name,
        )
        return df.values

    def _calculate_agreement(
        self,
        predictions: dict[str, float],
    ) -> ModelAgreement:
        """Calculate model agreement from predictions.

        Args:
            predictions: Dictionary of model predictions.

        Returns:
            ModelAgreement analysis.
        """
        from src.explainability.decision_trace import calculate_model_agreement

        return calculate_model_agreement(predictions)


# Singleton instance
_explanation_service: ExplanationService | None = None


def get_explanation_service() -> ExplanationService:
    """Get or create singleton ExplanationService instance.

    Returns:
        ExplanationService instance with all dependencies loaded.
    """
    global _explanation_service

    if _explanation_service is None:
        logger.info("Initializing ExplanationService...")

        # Load dependencies
        segmenter = Segmenter.load()
        model_manager = get_model_manager()
        optimizer = get_price_optimizer(model_manager)
        rules_engine = RulesEngine()

        # Create traced pricing service
        traced_pricing = TracedPricingService(
            segmenter=segmenter,
            model_manager=model_manager,
            optimizer=optimizer,
            rules_engine=rules_engine,
            model_name="xgboost",
        )

        # Get feature names from model manager (ensure loaded first)
        model_manager._ensure_loaded()
        feature_names = model_manager.feature_names

        _explanation_service = ExplanationService(
            traced_pricing=traced_pricing,
            model_manager=model_manager,
            feature_names=feature_names,
        )

        logger.info("ExplanationService initialized successfully")

    return _explanation_service

