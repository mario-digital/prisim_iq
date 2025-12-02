"""Segment result schema for classification output."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class SegmentResult(BaseModel):
    """Basic result of market context classification into a segment.

    Used internally by the Segmenter class.
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
    characteristics: dict[str, Any] = Field(
        default_factory=dict,
        description="Key characteristics of this segment (e.g., avg_surge, avg_demand_ratio)",
    )
    centroid_distance: float = Field(
        ...,
        ge=0,
        description="Distance from cluster centroid (lower = higher confidence)",
    )

    model_config = ConfigDict(extra="forbid")


class SegmentDetails(BaseModel):
    """Full segment classification response for API output.

    Extends SegmentResult with human-readable description and confidence level.
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
    characteristics: dict[str, Any] = Field(
        default_factory=dict,
        description="Key characteristics of this segment (e.g., avg_supply_demand_ratio, sample_count)",
    )
    centroid_distance: float = Field(
        ...,
        ge=0,
        description="Distance from cluster centroid (lower = more confident)",
    )
    human_readable_description: str = Field(
        ...,
        description="Human-friendly explanation of the segment",
    )
    confidence_level: Literal["high", "medium", "low"] = Field(
        ...,
        description="Confidence level based on centroid distance",
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "segment_name": "Urban_Peak_Premium",
                "cluster_id": 2,
                "characteristics": {
                    "avg_supply_demand_ratio": 0.65,
                    "sample_count": 1250,
                    "centroid_norm": 1.234,
                },
                "centroid_distance": 0.45,
                "human_readable_description": "High-demand urban area during peak hours with premium vehicle preference",
                "confidence_level": "high",
            }
        },
    )

