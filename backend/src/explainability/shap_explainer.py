"""SHAP-based explainer for per-prediction feature importance.

This module provides local (per-prediction) explanations using SHAP values:
- TreeExplainer for XGBoost, Decision Tree, Random Forest
- LinearExplainer for Linear Regression
"""

from __future__ import annotations

from typing import Any, Literal

import numpy as np
import pandas as pd
import shap
from loguru import logger

ModelType = Literal["linear_regression", "decision_tree", "xgboost"]


class ShapExplainer:
    """SHAP-based explainer for local feature importance.

    Provides per-prediction SHAP values that explain how each feature
    contributed to a specific prediction, not just global importance.
    """

    def __init__(
        self,
        model: Any,
        model_type: ModelType,
        feature_names: list[str],
        background_data: np.ndarray | pd.DataFrame | None = None,
    ) -> None:
        """Initialize the SHAP explainer.

        Args:
            model: Trained scikit-learn compatible model.
            model_type: Type of model ('linear_regression', 'decision_tree', 'xgboost').
            feature_names: List of feature names matching model input.
            background_data: Background/training data for LinearExplainer.
                           Required for linear_regression, optional for tree models.
        """
        self.model = model
        self.model_type = model_type
        self.feature_names = feature_names
        self.background_data = background_data
        self._explainer: shap.Explainer | None = None

    def _get_explainer(self) -> shap.Explainer:
        """Get or initialize the appropriate SHAP explainer.

        Returns:
            SHAP explainer instance.

        Raises:
            ValueError: If background_data is required but not provided.
        """
        if self._explainer is not None:
            return self._explainer

        if self.model_type in ["xgboost", "decision_tree"]:
            logger.debug(f"Initializing TreeExplainer for {self.model_type}")
            self._explainer = shap.TreeExplainer(self.model)
        elif self.model_type == "linear_regression":
            if self.background_data is None:
                raise ValueError(
                    "background_data is required for LinearExplainer. "
                    "Provide training data samples for accurate explanations."
                )
            logger.debug("Initializing LinearExplainer for linear_regression")
            self._explainer = shap.LinearExplainer(self.model, self.background_data)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

        return self._explainer

    def explain(self, X: np.ndarray | pd.DataFrame) -> np.ndarray:
        """Calculate SHAP values for given input(s).

        Args:
            X: Input features (single sample or batch).
               Shape: (n_features,) for single sample or (n_samples, n_features).

        Returns:
            SHAP values with same shape as input.
            For single sample: shape (n_features,)
            For batch: shape (n_samples, n_features)
        """
        explainer = self._get_explainer()

        # Ensure 2D input
        X_2d = np.atleast_2d(X)
        if isinstance(X, pd.DataFrame):
            X_2d = X.values if len(X.shape) == 2 else X.values.reshape(1, -1)

        shap_values = explainer.shap_values(X_2d)

        # Handle different SHAP return formats
        if isinstance(shap_values, list):
            # Multi-output case - take first output
            shap_values = shap_values[0]

        # Return squeezed if single sample input
        if len(X_2d) == 1:
            shap_values = shap_values.squeeze()

        logger.debug(f"Calculated SHAP values with shape: {shap_values.shape}")

        return shap_values

    def explain_single(
        self, X: np.ndarray | pd.DataFrame
    ) -> dict[str, float]:
        """Calculate SHAP values for a single prediction as a dictionary.

        Args:
            X: Input features for single sample.
               Shape: (n_features,) or (1, n_features).

        Returns:
            Dictionary mapping feature names to SHAP values.
        """
        shap_values = self.explain(X)

        # Flatten if needed
        if shap_values.ndim > 1:
            shap_values = shap_values.flatten()

        return dict(zip(self.feature_names, shap_values.tolist(), strict=False))

    def get_expected_value(self) -> float:
        """Get the expected (base) value of the model.

        This is the average prediction that SHAP values are relative to.

        Returns:
            Expected value (base prediction).
        """
        explainer = self._get_explainer()

        expected = explainer.expected_value
        if isinstance(expected, np.ndarray):
            expected = expected[0]

        return float(expected)

    def explain_with_base(
        self, X: np.ndarray | pd.DataFrame
    ) -> tuple[dict[str, float], float]:
        """Calculate SHAP values along with base value.

        Args:
            X: Input features for single sample.

        Returns:
            Tuple of (shap_values_dict, expected_value).
        """
        shap_dict = self.explain_single(X)
        expected = self.get_expected_value()
        return shap_dict, expected


def get_shap_importance(
    model: Any,
    model_type: ModelType,
    feature_names: list[str],
    X: np.ndarray | pd.DataFrame,
    background_data: np.ndarray | pd.DataFrame | None = None,
) -> dict[str, float]:
    """Convenience function to get per-prediction SHAP importance.

    Args:
        model: Trained scikit-learn compatible model.
        model_type: Type of model.
        feature_names: List of feature names.
        X: Input features for single prediction.
        background_data: Background data for LinearExplainer.

    Returns:
        Dictionary mapping feature names to SHAP values.
    """
    explainer = ShapExplainer(
        model=model,
        model_type=model_type,
        feature_names=feature_names,
        background_data=background_data,
    )
    return explainer.explain_single(X)

