"""Feature importance service combining global and SHAP importance.

This module provides the main interface for generating complete feature
importance results with:
- Normalized values summing to 100%
- Ranked by absolute importance
- Plain-English descriptions
- Top 3 summary
"""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
from loguru import logger

from src.explainability.feature_importance import FeatureImportanceCalculator
from src.explainability.shap_explainer import ShapExplainer
from src.schemas.explainability import FeatureContribution, FeatureImportanceResult

ModelType = Literal["linear_regression", "decision_tree", "xgboost"]

# Feature display names mapping
FEATURE_DISPLAY_NAMES: dict[str, str] = {
    "number_of_riders": "Number of Riders",
    "number_of_drivers": "Number of Drivers",
    "location_category": "Location Category",
    "customer_loyalty_status": "Customer Loyalty",
    "number_of_past_rides": "Past Rides Count",
    "average_ratings": "Average Rating",
    "time_of_booking": "Time of Booking",
    "vehicle_type": "Vehicle Type",
    "expected_ride_duration": "Expected Duration",
    "historical_cost_of_ride": "Historical Cost",
    "supply_demand_ratio": "Supply/Demand Ratio",
    "segment": "Customer Segment",
    "price": "Price Point",
}

# Feature description templates based on direction and relative value
FEATURE_DESCRIPTIONS: dict[str, dict[str, str]] = {
    "supply_demand_ratio": {
        "positive": "High demand relative to available drivers",
        "negative": "Adequate driver supply for current demand",
    },
    "time_of_booking": {
        "positive": "Peak hours increase price sensitivity",
        "negative": "Off-peak hours reduce price impact",
    },
    "location_category": {
        "positive": "Urban location increases demand",
        "negative": "Rural/suburban location reduces demand",
    },
    "customer_loyalty_status": {
        "positive": "Loyalty status increases retention",
        "negative": "Lower loyalty reduces retention",
    },
    "number_of_riders": {
        "positive": "Higher rider demand in area",
        "negative": "Lower rider demand in area",
    },
    "number_of_drivers": {
        "positive": "More drivers available",
        "negative": "Fewer drivers available",
    },
    "number_of_past_rides": {
        "positive": "Frequent user with established behavior",
        "negative": "New or infrequent user",
    },
    "average_ratings": {
        "positive": "Higher ratings improve retention",
        "negative": "Lower ratings reduce retention",
    },
    "vehicle_type": {
        "positive": "Premium vehicle type",
        "negative": "Standard vehicle type",
    },
    "expected_ride_duration": {
        "positive": "Longer expected ride duration",
        "negative": "Shorter expected ride duration",
    },
    "historical_cost_of_ride": {
        "positive": "Higher historical cost baseline",
        "negative": "Lower historical cost baseline",
    },
    "segment": {
        "positive": "Premium customer segment",
        "negative": "Standard customer segment",
    },
    "price": {
        "positive": "Higher price point",
        "negative": "Lower price point",
    },
}


def _normalize_importance(
    raw_importance: dict[str, float],
) -> dict[str, tuple[float, str]]:
    """Normalize importance values to sum to 1.0 and determine direction.

    Args:
        raw_importance: Dictionary of feature names to raw importance/SHAP values.

    Returns:
        Dictionary mapping feature names to (normalized_value, direction).
        Values are absolute, normalized to sum to 1.0.
    """
    # Calculate total absolute value
    abs_values = {k: abs(v) for k, v in raw_importance.items()}
    total = sum(abs_values.values())

    if total == 0:
        # Edge case: all values are 0
        n_features = len(raw_importance)
        return dict.fromkeys(raw_importance, (1.0 / n_features, "positive"))

    # Normalize and track direction
    result = {}
    for name, raw_value in raw_importance.items():
        normalized = abs(raw_value) / total
        direction = "positive" if raw_value >= 0 else "negative"
        result[name] = (normalized, direction)

    return result


def _rank_contributions(
    normalized: dict[str, tuple[float, str]],
) -> list[tuple[str, float, str]]:
    """Sort contributions by absolute importance (descending).

    Args:
        normalized: Dictionary from _normalize_importance.

    Returns:
        List of (feature_name, importance, direction) tuples, sorted by importance.
    """
    items = [(name, imp, direction) for name, (imp, direction) in normalized.items()]
    items.sort(key=lambda x: x[1], reverse=True)
    return items


def _generate_description(
    feature_name: str,
    importance: float,
    direction: str,
) -> str:
    """Generate plain-English description for a feature contribution.

    Args:
        feature_name: Internal feature name.
        importance: Normalized importance (0-1).
        direction: "positive" or "negative".

    Returns:
        Human-readable description with percentage.
    """
    # Get template or use generic
    templates = FEATURE_DESCRIPTIONS.get(feature_name, {})
    base_description = templates.get(
        direction,
        f"{'Increases' if direction == 'positive' else 'Decreases'} prediction"
    )

    # Format percentage with sign
    pct = importance * 100
    sign = "+" if direction == "positive" else "-"

    return f"{base_description} ({sign}{pct:.0f}%)"


def _generate_top_3_summary(contributions: list[FeatureContribution]) -> str:
    """Generate natural language summary of top 3 features.

    Args:
        contributions: Sorted list of feature contributions.

    Returns:
        Summary string like "Price driven by: factor1, factor2, factor3".
    """
    top_3 = contributions[:3]
    parts = [c.description for c in top_3]
    return f"Price driven by: {', '.join(parts)}"


class FeatureImportanceService:
    """Service for generating complete feature importance results.

    Combines global importance and SHAP values with normalization,
    ranking, and description generation.
    """

    def __init__(
        self,
        model: Any,
        model_type: ModelType,
        feature_names: list[str],
        background_data: np.ndarray | None = None,
    ) -> None:
        """Initialize the importance service.

        Args:
            model: Trained model.
            model_type: Type of model.
            feature_names: List of feature names.
            background_data: Training data for SHAP LinearExplainer.
        """
        self.model = model
        self.model_type = model_type
        self.feature_names = feature_names
        self.background_data = background_data

        # Initialize calculators
        self._global_calculator = FeatureImportanceCalculator(
            model, model_type, feature_names
        )
        self._shap_explainer: ShapExplainer | None = None

    def _get_shap_explainer(self) -> ShapExplainer:
        """Lazy initialization of SHAP explainer."""
        if self._shap_explainer is None:
            self._shap_explainer = ShapExplainer(
                self.model,
                self.model_type,
                self.feature_names,
                self.background_data,
            )
        return self._shap_explainer

    def _build_contributions(
        self,
        raw_importance: dict[str, float],
    ) -> list[FeatureContribution]:
        """Build list of FeatureContribution from raw importance values.

        Args:
            raw_importance: Raw importance/SHAP values.

        Returns:
            Ranked list of FeatureContribution objects.
        """
        # Normalize to sum to 1.0
        normalized = _normalize_importance(raw_importance)

        # Rank by importance
        ranked = _rank_contributions(normalized)

        # Build contribution objects
        contributions = []
        for name, importance, direction in ranked:
            display_name = FEATURE_DISPLAY_NAMES.get(name, name.replace("_", " ").title())
            description = _generate_description(name, importance, direction)

            contributions.append(
                FeatureContribution(
                    feature_name=name,
                    display_name=display_name,
                    importance=importance,
                    direction=direction,
                    description=description,
                )
            )

        return contributions

    def get_global_importance(self) -> FeatureImportanceResult:
        """Get global feature importance from model attributes.

        Returns:
            Complete FeatureImportanceResult with ranked contributions.
        """
        logger.debug(f"Calculating global importance for {self.model_type}")

        # Get raw importance
        raw_importance = self._global_calculator.get_global_importance()

        # For linear regression, get signed coefficients for direction
        if self.model_type == "linear_regression":
            raw_coef = self._global_calculator.get_raw_coefficients()
            if raw_coef:
                # Use raw coefficients to determine direction
                for name in raw_importance:
                    if name in raw_coef and raw_coef[name] < 0:
                        # Keep magnitude from normalized, sign from raw
                        raw_importance[name] = -raw_importance[name]

        contributions = self._build_contributions(raw_importance)
        summary = _generate_top_3_summary(contributions)

        return FeatureImportanceResult(
            contributions=contributions,
            model_used=self.model_type,
            explanation_type="global",
            top_3_summary=summary,
        )

    def get_local_importance(
        self,
        X: np.ndarray,
    ) -> FeatureImportanceResult:
        """Get per-prediction SHAP importance.

        Args:
            X: Input features for single prediction.

        Returns:
            Complete FeatureImportanceResult with SHAP-based contributions.
        """
        logger.debug(f"Calculating SHAP importance for {self.model_type}")

        explainer = self._get_shap_explainer()
        shap_values = explainer.explain_single(X)

        contributions = self._build_contributions(shap_values)
        summary = _generate_top_3_summary(contributions)

        return FeatureImportanceResult(
            contributions=contributions,
            model_used=self.model_type,
            explanation_type="local_shap",
            top_3_summary=summary,
        )


def get_feature_importance(
    model: Any,
    model_type: ModelType,
    feature_names: list[str],
    X: np.ndarray | None = None,
    background_data: np.ndarray | None = None,
    explanation_type: Literal["global", "local_shap"] = "global",
) -> FeatureImportanceResult:
    """Convenience function to get feature importance.

    Args:
        model: Trained model.
        model_type: Type of model.
        feature_names: List of feature names.
        X: Input features (required for local_shap).
        background_data: Training data for SHAP LinearExplainer.
        explanation_type: "global" or "local_shap".

    Returns:
        Complete FeatureImportanceResult.

    Raises:
        ValueError: If X is required but not provided.
    """
    service = FeatureImportanceService(
        model, model_type, feature_names, background_data
    )

    if explanation_type == "global":
        return service.get_global_importance()
    else:
        if X is None:
            raise ValueError("X is required for local_shap explanation")
        return service.get_local_importance(X)

