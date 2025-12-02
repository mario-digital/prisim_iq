"""Data endpoints router."""

from fastapi import APIRouter, HTTPException

from src.ml.preprocessor import load_dataset
from src.schemas.data import DataSummaryResponse, PriceRange

router = APIRouter(prefix="/data", tags=["Data"])


@router.get(
    "/summary",
    response_model=DataSummaryResponse,
    summary="Dataset Summary",
    description="Get summary statistics about the loaded pricing dataset.",
    responses={
        500: {"description": "Dataset not found or failed to load"},
    },
)
async def get_data_summary() -> DataSummaryResponse:
    """Return summary statistics of the pricing dataset."""
    try:
        df = load_dataset()
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Dataset not found: {e}",
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Dataset validation failed: {e}",
        ) from e

    # Extract unique customer segments
    segments = sorted(df["Customer_Loyalty_Status"].unique().tolist())

    # Get price range from Historical_Cost_of_Ride
    price_range = PriceRange(
        min=float(df["Historical_Cost_of_Ride"].min()),
        max=float(df["Historical_Cost_of_Ride"].max()),
    )

    return DataSummaryResponse(
        row_count=len(df),
        column_count=len(df.columns),
        segments=segments,
        price_range=price_range,
    )

