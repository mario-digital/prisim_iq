"""Health check response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        description="Current health status of the API"
    )
    version: str = Field(description="API version string")
    timestamp: datetime = Field(description="Current server timestamp (UTC)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "healthy",
                    "version": "1.0.0",
                    "timestamp": "2024-12-02T10:30:00Z",
                }
            ]
        }
    }

