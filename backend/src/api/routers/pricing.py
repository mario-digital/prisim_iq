"""Pricing API router for price optimization endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from src.schemas.market import MarketContext
from src.schemas.pricing import PricingResult
from src.services.pricing_service import PricingService, get_pricing_service

router = APIRouter(prefix="/optimize_price", tags=["Pricing"])

# Type alias for dependency injection
PricingServiceDep = Annotated[PricingService, Depends(get_pricing_service)]


@router.post(
    "",
    response_model=PricingResult,
    summary="Optimize price for market context",
    description="""
    Calculate the optimal price recommendation for a given market context.

    The endpoint orchestrates:
    1. **Segment Classification**: Assigns the context to a market segment using K-Means clustering
    2. **Price Optimization**: Runs grid search to find profit-maximizing price using ML demand prediction
    3. **Business Rules**: Applies floor, cap, and loyalty discount rules

    Returns a complete pricing recommendation with confidence scores, profit metrics,
    segment information, and applied business rules.
    """,
    responses={
        200: {
            "description": "Successful price optimization",
            "content": {
                "application/json": {
                    "example": {
                        "recommended_price": 42.50,
                        "confidence_score": 0.85,
                        "expected_demand": 0.72,
                        "expected_profit": 15.30,
                        "baseline_profit": 10.50,
                        "profit_uplift_percent": 45.71,
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
                        "rules_applied": [
                            {
                                "rule_id": "floor_minimum_margin",
                                "rule_name": "Minimum Margin Floor",
                                "price_before": 38.50,
                                "price_after": 42.50,
                                "impact": 4.00,
                                "impact_percent": 10.39,
                            }
                        ],
                        "price_before_rules": 38.50,
                        "price_demand_curve": [
                            {"price": 30.0, "demand": 0.95, "profit": 0.0},
                            {"price": 35.0, "demand": 0.85, "profit": 4.25},
                            {"price": 40.0, "demand": 0.75, "profit": 7.50},
                        ],
                        "processing_time_ms": 245.5,
                        "timestamp": "2024-01-15T10:30:00Z",
                    }
                }
            },
        },
        422: {
            "description": "Validation error - invalid market context",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "value_error",
                                "loc": ["body", "average_ratings"],
                                "msg": "Value error, Input should be greater than or equal to 1.0",
                                "input": 0.5,
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error - model or service failure",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error",
                        "error_code": "INTERNAL_ERROR",
                    }
                }
            },
        },
        503: {
            "description": "Service unavailable - models not loaded",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Pricing models not available. Please ensure models are trained.",
                    }
                }
            },
        },
    },
)
async def optimize_price(
    context: MarketContext,
    pricing_service: PricingServiceDep,
) -> PricingResult:
    """Optimize price for the given market context.

    Args:
        context: Market conditions and customer profile.
        pricing_service: Injected pricing service.

    Returns:
        Complete pricing result with recommendation and explanation.

    Raises:
        HTTPException: 503 if models not available, 500 for other errors.
    """
    logger.info(
        f"Optimize price request: "
        f"location={context.location_category}, "
        f"vehicle={context.vehicle_type}, "
        f"loyalty={context.customer_loyalty_status}"
    )

    try:
        result = await pricing_service.get_recommendation(context)
        logger.info(
            f"Price optimized: ${result.recommended_price:.2f}, "
            f"uplift={result.profit_uplift_percent:.1f}%, "
            f"time={result.processing_time_ms:.1f}ms"
        )
        return result

    except FileNotFoundError as e:
        logger.error(f"Model files not found: {e}")
        raise HTTPException(
            status_code=503,
            detail="Pricing models not available. Please ensure models are trained.",
        ) from e

    except RuntimeError as e:
        logger.error(f"Runtime error during optimization: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        ) from e

