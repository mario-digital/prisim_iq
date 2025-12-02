"""Explainability module for ML model interpretation.

This module provides tools for understanding model predictions through:
- Global feature importance (from model attributes)
- Local/per-prediction importance via SHAP values
- Human-readable explanations
- Decision trace for auditing pricing pipeline
"""

from src.explainability.decision_trace import (
    DecisionTrace,
    DecisionTracer,
    ModelAgreement,
    TraceStep,
    calculate_model_agreement,
    format_trace_text,
)
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
    # Decision trace
    "DecisionTrace",
    "DecisionTracer",
    "ModelAgreement",
    "TraceStep",
    "calculate_model_agreement",
    "format_trace_text",
    # Feature importance
    "FeatureImportanceCalculator",
    "get_global_importance",
    "FeatureImportanceService",
    "get_feature_importance",
    "ShapExplainer",
    "get_shap_importance",
]
