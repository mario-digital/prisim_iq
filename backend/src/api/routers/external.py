"""External data integration router.

Provides:
- Webhook endpoints for n8n to push data
- GET endpoint for current external context
"""

from typing import Any

from fastapi import APIRouter
from loguru import logger

from src.schemas.external import (
    EventData,
    ExternalContextResponse,
    FuelData,
    WeatherData,
)
from src.services.external_service import get_external_service

router = APIRouter(prefix="/external", tags=["External Data"])


@router.get(
    "/context",
    response_model=ExternalContextResponse,
    summary="Get External Context",
    description=(
        "Returns current external factors affecting pricing: "
        "fuel prices, weather conditions, and local events. "
        "Includes cache freshness information and natural language explanation."
    ),
)
async def get_external_context() -> ExternalContextResponse:
    """Get current external context with cache status and explanation."""
    service = get_external_service()
    return service.get_external_context_response()


@router.post(
    "/webhook/fuel",
    response_model=FuelData,
    summary="Fuel Price Webhook",
    description=(
        "Receive fuel price updates from n8n. "
        "Expected payload: {price_per_gallon: float, change_percent: float, source?: string}"
    ),
)
async def webhook_fuel(data: dict[str, Any]) -> FuelData:
    """Handle fuel price webhook from n8n.

    Args:
        data: Fuel price data from n8n workflow.

    Returns:
        Validated FuelData model.
    """
    logger.info(f"Received fuel webhook: {data}")
    service = get_external_service()
    return service.handle_fuel_webhook(data)


@router.post(
    "/webhook/weather",
    response_model=WeatherData,
    summary="Weather Webhook",
    description=(
        "Receive weather condition updates from n8n. "
        "Expected payload: {condition: sunny|cloudy|rainy|snowy, temperature_f: float}"
    ),
)
async def webhook_weather(data: dict[str, Any]) -> WeatherData:
    """Handle weather data webhook from n8n.

    Args:
        data: Weather data from n8n workflow.

    Returns:
        Validated WeatherData model with calculated demand modifier.
    """
    logger.info(f"Received weather webhook: {data}")
    service = get_external_service()
    return service.handle_weather_webhook(data)


@router.post(
    "/webhook/events",
    response_model=list[EventData],
    summary="Events Webhook",
    description=(
        "Receive local events data from n8n. "
        "Expected payload: {events: [{name, type, venue, start_time, radius_miles?}]}"
    ),
)
async def webhook_events(data: dict[str, Any]) -> list[EventData]:
    """Handle events data webhook from n8n.

    Args:
        data: Events data from n8n workflow.

    Returns:
        List of validated EventData models with calculated surge modifiers.
    """
    logger.info(f"Received events webhook: {data}")
    service = get_external_service()
    return service.handle_events_webhook(data)
