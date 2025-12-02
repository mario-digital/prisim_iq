"""Data-related response schemas."""

from pydantic import BaseModel, Field


class PriceRange(BaseModel):
    """Price range statistics."""

    min: float = Field(description="Minimum price in dataset")
    max: float = Field(description="Maximum price in dataset")


class DataSummaryResponse(BaseModel):
    """Response model for dataset summary endpoint."""

    row_count: int = Field(description="Total number of rows in the dataset")
    column_count: int = Field(description="Total number of columns in the dataset")
    segments: list[str] = Field(description="List of customer loyalty segments")
    price_range: PriceRange = Field(description="Min/max price range")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "row_count": 10000,
                    "column_count": 11,
                    "segments": ["Silver", "Gold", "Regular"],
                    "price_range": {"min": 5.0, "max": 150.0},
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response model."""

    detail: str = Field(description="Error message")
    error_code: str | None = Field(default=None, description="Application error code")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": "Dataset not found",
                    "error_code": "DATA_NOT_FOUND",
                }
            ]
        }
    }

