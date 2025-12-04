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


class ModelInfo(BaseModel):
    """Information about a single ML model."""

    name: str = Field(description="Model name/identifier")
    loaded: bool = Field(description="Whether the model is loaded in memory")
    type: str = Field(description="Model type (e.g., xgboost, linear_regression)")


class ModelsStatusResponse(BaseModel):
    """Response model for models status endpoint."""

    total: int = Field(description="Total number of models")
    ready: int = Field(description="Number of models loaded and ready")
    models: list[ModelInfo] = Field(description="Details for each model")
    timestamp: datetime = Field(description="Current server timestamp (UTC)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total": 3,
                    "ready": 3,
                    "models": [
                        {"name": "xgboost", "loaded": True, "type": "xgboost"},
                        {"name": "linear_regression", "loaded": True, "type": "sklearn"},
                        {"name": "decision_tree", "loaded": True, "type": "sklearn"},
                    ],
                    "timestamp": "2024-12-02T10:30:00Z",
                }
            ]
        }
    }

