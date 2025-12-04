"""Health check router."""

from datetime import UTC, datetime

from fastapi import APIRouter
from loguru import logger

from src.api.dependencies import SettingsDep
from src.schemas.health import HealthResponse, ModelInfo, ModelsStatusResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check API health status. Used for monitoring and load balancer health checks.",
)
async def health_check(settings: SettingsDep) -> HealthResponse:
    """Return current API health status."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now(UTC),
    )


@router.get(
    "/models/status",
    response_model=ModelsStatusResponse,
    summary="Models Status",
    description="Get status of all ML models including which are loaded and ready.",
)
async def models_status() -> ModelsStatusResponse:
    """Return current status of all ML models."""
    from src.ml.model_manager import get_model_manager

    try:
        model_manager = get_model_manager()
        
        # Ensure models are loaded (lazy load on first status check)
        if not model_manager._loaded:
            logger.info("Loading models for status check...")
            model_manager.load_models()
        
        # Get model info
        expected_models = ["linear_regression", "decision_tree", "xgboost"]
        models_info: list[ModelInfo] = []
        ready_count = 0
        
        for model_name in expected_models:
            is_loaded = model_name in model_manager.models
            if is_loaded:
                ready_count += 1
            
            # Determine model type
            model_type = "xgboost" if model_name == "xgboost" else "sklearn"
            
            models_info.append(ModelInfo(
                name=model_name,
                loaded=is_loaded,
                type=model_type,
            ))
        
        return ModelsStatusResponse(
            total=len(expected_models),
            ready=ready_count,
            models=models_info,
            timestamp=datetime.now(UTC),
        )
    except Exception as e:
        logger.error(f"Error getting models status: {e}")
        # Return degraded status on error
        return ModelsStatusResponse(
            total=3,
            ready=0,
            models=[],
            timestamp=datetime.now(UTC),
        )

