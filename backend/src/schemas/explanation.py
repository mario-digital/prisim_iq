"""Explanation schemas for explain_decision endpoint."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.explainability.decision_trace import DecisionTrace, ModelAgreement
from src.schemas.explainability import FeatureContribution
from src.schemas.market import MarketContext
from src.schemas.pricing import PricingResult


class ExplainRequest(BaseModel):
    """Request schema for the explain_decision endpoint.

    Attributes:
        context: Market conditions and customer profile for explanation.
        pricing_result_id: Optional reference to a previous pricing result.
        include_trace: Whether to include full decision trace (default: True).
        include_shap: Whether to include SHAP-based local importance (default: True).
    """

    context: MarketContext = Field(
        ...,
        description="Market conditions and customer profile",
    )
    pricing_result_id: str | None = Field(
        None,
        description="Optional reference to a previous pricing result for consistency",
    )
    include_trace: bool = Field(
        True,
        description="Include full decision trace in response",
    )
    include_shap: bool = Field(
        True,
        description="Include SHAP-based local feature importance",
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "context": {
                    "number_of_riders": 50,
                    "number_of_drivers": 25,
                    "location_category": "Urban",
                    "customer_loyalty_status": "Gold",
                    "number_of_past_rides": 20,
                    "average_ratings": 4.5,
                    "time_of_booking": "Evening",
                    "vehicle_type": "Premium",
                    "expected_ride_duration": 30,
                    "historical_cost_of_ride": 35.0,
                },
                "pricing_result_id": None,
                "include_trace": True,
                "include_shap": True,
            }
        },
    )


class PriceExplanation(BaseModel):
    """Complete price explanation response.

    Contains the pricing recommendation along with full explainability data
    including feature importance, decision trace, model agreement, and
    natural language summary.

    Attributes:
        recommendation: The pricing result (may be recalculated or referenced).
        feature_importance: Local (SHAP) feature contributions for this prediction.
        global_importance: Model-level feature importance.
        decision_trace: Step-by-step pipeline execution trace.
        model_agreement: Cross-model agreement analysis.
        model_predictions: Dictionary of all model predictions.
        natural_language_summary: Human-readable explanation of the recommendation.
        key_factors: Top factors driving the recommendation.
        explanation_time_ms: Time taken to generate explanation.
        timestamp: When the explanation was generated.
    """

    # Core recommendation
    recommendation: PricingResult = Field(
        ...,
        description="Complete pricing recommendation",
    )

    # Feature importance
    feature_importance: list[FeatureContribution] = Field(
        ...,
        description="Local SHAP-based feature contributions for this prediction",
    )
    global_importance: list[FeatureContribution] = Field(
        ...,
        description="Model-level global feature importance",
    )

    # Decision trace
    decision_trace: DecisionTrace | None = Field(
        None,
        description="Step-by-step decision pipeline trace",
    )

    # Model comparison
    model_agreement: ModelAgreement = Field(
        ...,
        description="Cross-model agreement analysis",
    )
    model_predictions: dict[str, float] = Field(
        ...,
        description="Predictions from all available models",
    )

    # Natural language
    natural_language_summary: str = Field(
        ...,
        description="Human-readable explanation of the pricing recommendation",
    )
    key_factors: list[str] = Field(
        ...,
        description="Top factors driving the recommendation (e.g., 'High demand', 'Evening peak')",
    )

    # Metadata
    explanation_time_ms: float = Field(
        ...,
        ge=0,
        description="Time taken to generate explanation in milliseconds",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when explanation was generated",
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "recommendation": {
                    "recommended_price": 42.50,
                    "confidence_score": 0.85,
                    "expected_demand": 0.72,
                    "expected_profit": 18.75,
                    "baseline_profit": 15.08,
                    "profit_uplift_percent": 24.3,
                    "segment": {
                        "segment_name": "Urban_Peak_Premium",
                        "cluster_id": 2,
                        "characteristics": {
                            "avg_supply_demand_ratio": 0.65,
                            "sample_count": 1250,
                        },
                        "centroid_distance": 0.45,
                        "human_readable_description": "High-demand urban area during peak hours with premium vehicle preference",
                        "confidence_level": "high",
                    },
                    "model_used": "xgboost",
                    "rules_applied": [],
                    "price_before_rules": 42.50,
                    "price_demand_curve": [
                        {"price": 30.0, "demand": 0.95, "profit": 0.0},
                        {"price": 35.0, "demand": 0.85, "profit": 4.25},
                        {"price": 40.0, "demand": 0.75, "profit": 7.50},
                    ],
                    "processing_time_ms": 245.5,
                    "timestamp": "2024-01-15T10:30:00Z",
                },
                "feature_importance": [
                    {
                        "feature_name": "supply_demand_ratio",
                        "display_name": "Supply/Demand Ratio",
                        "importance": 0.32,
                        "direction": "positive",
                        "description": "High demand relative to available drivers (+32%)",
                    },
                    {
                        "feature_name": "time_of_booking",
                        "display_name": "Time of Booking",
                        "importance": 0.24,
                        "direction": "positive",
                        "description": "Peak hours increase price sensitivity (+24%)",
                    },
                    {
                        "feature_name": "vehicle_type",
                        "display_name": "Vehicle Type",
                        "importance": 0.18,
                        "direction": "positive",
                        "description": "Premium vehicle type (+18%)",
                    },
                ],
                "global_importance": [
                    {
                        "feature_name": "supply_demand_ratio",
                        "display_name": "Supply/Demand Ratio",
                        "importance": 0.28,
                        "direction": "positive",
                        "description": "High demand relative to available drivers (+28%)",
                    },
                ],
                "decision_trace": {
                    "trace_id": "abc12345-6789-def0-1234-567890abcdef",
                    "request_timestamp": "2024-01-15T10:30:00Z",
                    "total_duration_ms": 450.5,
                    "steps": [
                        {
                            "step_name": "segment_classification",
                            "timestamp": "2024-01-15T10:30:00Z",
                            "duration_ms": 12.5,
                            "inputs": {"location": "Urban"},
                            "outputs": {"segment": "Urban_Peak_Premium"},
                            "status": "success",
                            "error_message": None,
                        }
                    ],
                    "model_agreement": {
                        "models_compared": ["xgboost", "decision_tree", "linear_regression"],
                        "predictions": {"xgboost": 0.72, "decision_tree": 0.71, "linear_regression": 0.69},
                        "max_deviation_percent": 3.5,
                        "is_agreement": True,
                        "status": "full_agreement",
                    },
                    "final_result": {"recommended_price": 42.50},
                },
                "model_agreement": {
                    "models_compared": ["xgboost", "decision_tree", "linear_regression"],
                    "predictions": {"xgboost": 0.72, "decision_tree": 0.71, "linear_regression": 0.69},
                    "max_deviation_percent": 3.5,
                    "is_agreement": True,
                    "status": "full_agreement",
                },
                "model_predictions": {"xgboost": 0.72, "decision_tree": 0.71, "linear_regression": 0.69},
                "natural_language_summary": "The recommended price of $42.50 is primarily driven by high demand-to-supply ratio (contributing 32% to the decision). Additional factors include evening peak hours and premium vehicle selection. This price is expected to generate $18.75 in profit, a 24.3% improvement over the baseline price.",
                "key_factors": ["High demand", "Evening peak", "Premium vehicle"],
                "explanation_time_ms": 450.5,
                "timestamp": "2024-01-15T10:30:00Z",
            }
        },
    )

