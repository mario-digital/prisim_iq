"""Explainability schemas for feature importance results."""

from typing import Literal

from pydantic import BaseModel, Field


class FeatureContribution(BaseModel):
    """A single feature's contribution to a prediction.

    Attributes:
        feature_name: Internal feature name (e.g., "supply_demand_ratio").
        display_name: Human-readable name (e.g., "Supply/Demand Ratio").
        importance: Normalized importance value (0.0 to 1.0, sums to 1.0 across all).
        direction: Whether this feature pushes prediction up or down.
        description: Plain-English explanation (e.g., "High demand-to-supply ratio (+32%)").
    """

    feature_name: str = Field(..., description="Internal feature identifier")
    display_name: str = Field(..., description="Human-readable feature name")
    importance: float = Field(
        ..., ge=0, le=1, description="Normalized importance (0-1)"
    )
    direction: Literal["positive", "negative"] = Field(
        ..., description="Impact direction on prediction"
    )
    description: str = Field(..., description="Plain-English explanation")


class FeatureImportanceResult(BaseModel):
    """Complete feature importance result for a prediction.

    Contains ranked list of feature contributions with optional summary.

    Attributes:
        contributions: Ranked list of feature contributions (highest first).
        model_used: Name of the model that generated predictions.
        explanation_type: Whether this is global or local (SHAP) importance.
        top_3_summary: Natural language summary of top 3 factors.
    """

    contributions: list[FeatureContribution] = Field(
        ..., description="Ranked feature contributions"
    )
    model_used: str = Field(..., description="Model name used for prediction")
    explanation_type: Literal["global", "local_shap"] = Field(
        ..., description="Type of explanation"
    )
    top_3_summary: str = Field(..., description="Natural language summary of top factors")

