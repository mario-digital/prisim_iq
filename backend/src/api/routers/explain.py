"""Explain API router for decision explanation endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from src.schemas.explanation import ExplainRequest, PriceExplanation
from src.services.explanation_service import ExplanationService, get_explanation_service

router = APIRouter(prefix="/explain_decision", tags=["Explainability"])

# Type alias for dependency injection
ExplanationServiceDep = Annotated[ExplanationService, Depends(get_explanation_service)]


@router.post(
    "",
    response_model=PriceExplanation,
    summary="Explain price decision",
    description="""
    Generate a comprehensive explanation for a pricing recommendation.

    The endpoint provides:
    1. **Price Recommendation**: Optimal price with confidence and profit metrics
    2. **Feature Importance**: Local (SHAP) and global feature contributions
    3. **Decision Trace**: Step-by-step pipeline execution audit trail
    4. **Model Agreement**: Cross-model prediction comparison
    5. **Natural Language Summary**: Human-readable explanation

    This endpoint is designed for UI display of "why" information alongside
    pricing recommendations, enabling users to understand the factors
    driving the ML-based price optimization.

    **Performance Target**: < 2 seconds total response time
    """,
    responses={
        200: {
            "description": "Successful explanation generation",
            "content": {
                "application/json": {
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
                                "human_readable_description": "High-demand urban area during peak hours",
                                "confidence_level": "high",
                            },
                            "model_used": "xgboost",
                            "rules_applied": [],
                            "price_before_rules": 42.50,
                            "price_demand_curve": [],
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
                        "decision_trace": None,
                        "model_agreement": {
                            "models_compared": ["xgboost", "decision_tree", "linear_regression"],
                            "predictions": {
                                "xgboost": 0.72,
                                "decision_tree": 0.71,
                                "linear_regression": 0.69,
                            },
                            "max_deviation_percent": 3.5,
                            "is_agreement": True,
                            "status": "full_agreement",
                        },
                        "model_predictions": {
                            "xgboost": 0.72,
                            "decision_tree": 0.71,
                            "linear_regression": 0.69,
                        },
                        "natural_language_summary": "The recommended price of $42.50 is primarily driven by high demand-to-supply ratio (contributing 32% to the decision). This price is expected to generate $18.75 in profit, a 24.3% improvement over the baseline price.",
                        "key_factors": ["High demand", "Evening hours", "Premium vehicle"],
                        "explanation_time_ms": 450.5,
                        "timestamp": "2024-01-15T10:30:00Z",
                    }
                }
            },
        },
        422: {
            "description": "Validation error - invalid request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "value_error",
                                "loc": ["body", "context", "average_ratings"],
                                "msg": "Input should be greater than or equal to 1.0",
                                "input": 0.5,
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error during explanation generation",
                    }
                }
            },
        },
        503: {
            "description": "Service unavailable - models not loaded",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Explanation service not available. Please ensure models are trained.",
                    }
                }
            },
        },
    },
)
async def explain_decision(
    request: ExplainRequest,
    explanation_service: ExplanationServiceDep,
) -> PriceExplanation:
    """Generate comprehensive explanation for a pricing decision.

    Args:
        request: Explanation request with market context and options.
        explanation_service: Injected explanation service.

    Returns:
        Complete price explanation with all components.

    Raises:
        HTTPException: 503 if models not available, 500 for other errors.
    """
    logger.info(
        f"Explain decision request: "
        f"location={request.context.location_category}, "
        f"vehicle={request.context.vehicle_type}, "
        f"include_trace={request.include_trace}, "
        f"include_shap={request.include_shap}"
    )

    try:
        result = await explanation_service.explain(request)

        logger.info(
            f"Explanation generated: "
            f"price=${result.recommendation.recommended_price:.2f}, "
            f"factors={len(result.feature_importance)}, "
            f"time={result.explanation_time_ms:.1f}ms"
        )

        return result

    except FileNotFoundError as e:
        logger.error(f"Model files not found: {e}")
        raise HTTPException(
            status_code=503,
            detail="Explanation service not available. Please ensure models are trained.",
        ) from e

    except RuntimeError as e:
        logger.error(f"Runtime error during explanation: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        ) from e

    except Exception as e:
        logger.error(f"Unexpected error during explanation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during explanation generation",
        ) from e

