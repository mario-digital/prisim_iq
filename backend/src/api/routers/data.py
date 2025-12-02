"""Data endpoints router."""

import time
from typing import Literal

from fastapi import APIRouter, HTTPException
from loguru import logger

from src.api.dependencies import SegmenterDep
from src.ml.preprocessor import load_dataset
from src.schemas.data import DataSummaryResponse, PriceRange
from src.schemas.market import MarketContext
from src.schemas.segment import SegmentDetails

router = APIRouter(prefix="/data", tags=["Data"])


# Confidence thresholds based on centroid distance
# Lower distance = higher confidence
CONFIDENCE_THRESHOLDS = {
    "high": 1.0,    # distance <= 1.0
    "medium": 2.0,  # distance <= 2.0
    # distance > 2.0 = low
}


def _calculate_confidence_level(centroid_distance: float) -> Literal["high", "medium", "low"]:
    """Calculate confidence level based on centroid distance.

    Args:
        centroid_distance: Distance from cluster centroid.

    Returns:
        Confidence level: "high" if close, "medium" if moderate, "low" if far.
    """
    if centroid_distance <= CONFIDENCE_THRESHOLDS["high"]:
        return "high"
    elif centroid_distance <= CONFIDENCE_THRESHOLDS["medium"]:
        return "medium"
    return "low"


def _generate_segment_description(
    segment_name: str,
    characteristics: dict,
    context: MarketContext,
) -> str:
    """Generate human-readable description for a segment.

    Args:
        segment_name: Segment name (e.g., 'Urban_Peak_Premium').
        characteristics: Segment characteristics dict.
        context: Original market context for additional context.

    Returns:
        Human-friendly description of the segment.
    """
    # Parse segment name components
    parts = segment_name.split("_")

    # Build description components
    location_desc = {
        "Urban": "high-density urban area",
        "Suburban": "suburban neighborhood",
        "Rural": "rural location",
    }
    time_desc = {
        "Peak": "during peak hours",
        "Standard": "during off-peak hours",
    }
    vehicle_desc = {
        "Premium": "with premium vehicle preference",
        "Economy": "with economy vehicle preference",
    }

    # Extract components from segment name
    location = parts[0] if len(parts) > 0 else "Unknown"
    time_profile = parts[1] if len(parts) > 1 else "Standard"
    vehicle = parts[2] if len(parts) > 2 else "Economy"

    # Get demand indicator
    supply_demand = context.supply_demand_ratio
    if supply_demand < 0.5:
        demand_level = "High-demand"
    elif supply_demand < 1.0:
        demand_level = "Moderate-demand"
    else:
        demand_level = "Low-demand"

    # Build description
    location_text = location_desc.get(location, location)
    time_text = time_desc.get(time_profile, "")
    vehicle_text = vehicle_desc.get(vehicle, "")

    description = f"{demand_level} {location_text} {time_text} {vehicle_text}".strip()

    # Add characteristics info if available
    avg_ratio = characteristics.get("avg_supply_demand_ratio")
    if avg_ratio is not None:
        description += f". Typical supply/demand ratio: {avg_ratio:.2f}"

    return description


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


@router.post(
    "/segment",
    response_model=SegmentDetails,
    summary="Classify Market Segment",
    description="Submit a market context and receive its segment assignment with confidence indicator.",
    responses={
        422: {"description": "Validation error - invalid input data"},
        503: {"description": "Segmentation model not available"},
    },
)
async def classify_segment(
    context: MarketContext,
    segmenter: SegmenterDep,
) -> SegmentDetails:
    """Classify a market context into a pricing segment.

    Args:
        context: Market context with demand/supply indicators.
        segmenter: Injected segmenter model.

    Returns:
        SegmentDetails with segment name, cluster ID, characteristics,
        centroid distance, human-readable description, and confidence level.
    """
    start_time = time.perf_counter()

    # Classify the context
    result = segmenter.classify(context)

    # Calculate confidence level
    confidence_level = _calculate_confidence_level(result.centroid_distance)

    # Generate human-readable description
    description = _generate_segment_description(
        result.segment_name,
        result.characteristics,
        context,
    )

    # Log timing
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    logger.info(f"Segment classification completed in {elapsed_ms:.2f}ms")

    return SegmentDetails(
        segment_name=result.segment_name,
        cluster_id=result.cluster_id,
        characteristics=result.characteristics,
        centroid_distance=result.centroid_distance,
        human_readable_description=description,
        confidence_level=confidence_level,
    )

