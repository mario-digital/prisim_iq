"""Explainability module for ML model interpretation.

This module provides tools for understanding model predictions through:
- Global feature importance (from model attributes)
- Local/per-prediction importance via SHAP values
- Human-readable explanations
"""

from src.explainability.feature_importance import (
    FeatureImportanceCalculator,
    get_global_importance,
)
from src.explainability.importance_service import (
    FeatureImportanceService,
    get_feature_importance,
)
from src.explainability.shap_explainer import (
    ShapExplainer,
    get_shap_importance,
)

__all__ = [
    "FeatureImportanceCalculator",
    "get_global_importance",
    "FeatureImportanceService",
    "get_feature_importance",
    "ShapExplainer",
    "get_shap_importance",
]
