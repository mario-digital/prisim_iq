"""Segment result schema for classification output."""

from pydantic import BaseModel, Field


class SegmentResult(BaseModel):
    """Result of market context classification into a segment.

    Contains the segment assignment plus confidence/characteristics
    information for explainability.
    """

    segment_name: str = Field(
        ...,
        description="Descriptive name of the segment (e.g., 'Urban_Peak_Premium')",
    )
    cluster_id: int = Field(
        ...,
        ge=0,
        description="Numeric cluster ID from K-Means",
    )
    characteristics: dict[str, float] = Field(
        default_factory=dict,
        description="Key characteristics of this segment (e.g., avg_surge, avg_demand_ratio)",
    )
    centroid_distance: float = Field(
        ...,
        ge=0,
        description="Distance from cluster centroid (lower = higher confidence)",
    )

    model_config = {"extra": "forbid"}

