"""Health check router."""

from datetime import UTC, datetime

from fastapi import APIRouter

from src.api.dependencies import SettingsDep
from src.schemas.health import HealthResponse

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

