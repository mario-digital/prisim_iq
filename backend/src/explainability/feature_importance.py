"""Feature importance calculation for demand prediction models.

This module extracts global feature importances from trained models:
- Random Forest/XGBoost/Decision Tree: feature_importances_ attribute
- Linear Regression: normalized coefficients
"""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
from loguru import logger

ModelType = Literal["linear_regression", "decision_tree", "xgboost"]


class FeatureImportanceCalculator:
    """Calculator for extracting feature importances from trained models.

    Supports three model types:
    - linear_regression: Extracts and normalizes coefficients
    - decision_tree: Uses feature_importances_ attribute
    - xgboost: Uses feature_importances_ attribute
    """

    def __init__(
        self,
        model: Any,
        model_type: ModelType,
        feature_names: list[str],
    ) -> None:
        """Initialize the importance calculator.

        Args:
            model: Trained scikit-learn compatible model.
            model_type: Type of model ('linear_regression', 'decision_tree', 'xgboost').
            feature_names: List of feature names matching model input.
        """
        self.model = model
        self.model_type = model_type
        self.feature_names = feature_names

    def get_global_importance(self) -> dict[str, float]:
        """Extract global feature importance from the model.

        For tree-based models (XGBoost, Decision Tree), uses feature_importances_.
        For Linear Regression, normalizes absolute coefficients to sum to 1.

        Returns:
            Dictionary mapping feature names to importance scores (sum to 1.0).
        """
        if self.model_type == "linear_regression":
            return self._get_linear_importance()
        else:
            return self._get_tree_importance()

    def _get_tree_importance(self) -> dict[str, float]:
        """Extract importance from tree-based models.

        Returns:
            Dictionary mapping feature names to importance scores.

        Raises:
            AttributeError: If model lacks feature_importances_.
        """
        if not hasattr(self.model, "feature_importances_"):
            raise AttributeError(
                f"Model type '{self.model_type}' does not have feature_importances_"
            )

        importances = self.model.feature_importances_

        # Ensure importances sum to 1.0 (they should already for sklearn)
        total = float(np.sum(importances))
        if total > 0:
            importances = importances / total

        importance_dict = dict(
            zip(self.feature_names, importances.tolist(), strict=False)
        )

        logger.debug(
            f"Extracted {len(importance_dict)} feature importances from {self.model_type}"
        )

        return importance_dict

    def _get_linear_importance(self) -> dict[str, float]:
        """Extract and normalize coefficients from Linear Regression.

        Uses absolute values of coefficients, normalized to sum to 1.0.

        Returns:
            Dictionary mapping feature names to normalized importance scores.

        Raises:
            AttributeError: If model lacks coef_ attribute.
        """
        if not hasattr(self.model, "coef_"):
            raise AttributeError("Linear model does not have coef_ attribute")

        coefficients = self.model.coef_

        # Use absolute values for importance magnitude
        abs_coef = np.abs(coefficients)

        # Normalize to sum to 1.0
        total = float(np.sum(abs_coef))
        if total > 0:
            normalized = abs_coef / total
        else:
            # Edge case: all coefficients are 0
            normalized = np.zeros_like(abs_coef)

        importance_dict = dict(
            zip(self.feature_names, normalized.tolist(), strict=False)
        )

        logger.debug(
            f"Extracted {len(importance_dict)} normalized coefficients from linear_regression"
        )

        return importance_dict

    def get_raw_coefficients(self) -> dict[str, float] | None:
        """Get raw coefficients for Linear Regression (with sign).

        Returns:
            Dictionary mapping feature names to raw coefficient values,
            or None if not a linear model.
        """
        if self.model_type != "linear_regression":
            return None

        if not hasattr(self.model, "coef_"):
            return None

        return dict(
            zip(self.feature_names, self.model.coef_.tolist(), strict=False)
        )


def get_global_importance(
    model: Any,
    model_type: ModelType,
    feature_names: list[str],
) -> dict[str, float]:
    """Convenience function to extract global feature importance.

    Args:
        model: Trained scikit-learn compatible model.
        model_type: Type of model ('linear_regression', 'decision_tree', 'xgboost').
        feature_names: List of feature names matching model input.

    Returns:
        Dictionary mapping feature names to importance scores (sum to 1.0).
    """
    calculator = FeatureImportanceCalculator(model, model_type, feature_names)
    return calculator.get_global_importance()

