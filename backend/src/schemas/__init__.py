"""Pydantic schemas for PrismIQ API."""

from src.schemas.chat import ChatRequest, ChatResponse
from src.schemas.data import DataSummaryResponse, ErrorResponse, PriceRange
from src.schemas.evidence import (
    DataCard,
    EvidenceResponse,
    HoneywellMapping,
    HoneywellMappingResponse,
    MethodologyDoc,
    ModelCard,
)
from src.schemas.explainability import FeatureContribution, FeatureImportanceResult
from src.schemas.explanation import ExplainRequest, PriceExplanation
from src.schemas.health import HealthResponse
from src.schemas.market import MarketContext
from src.schemas.optimization import OptimizationResult, PriceDemandPoint
from src.schemas.segment import SegmentDetails, SegmentResult
from src.schemas.sensitivity import (
    ConfidenceBand,
    ScenarioResult,
    SensitivityResult,
)

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "ConfidenceBand",
    "DataCard",
    "DataSummaryResponse",
    "ErrorResponse",
    "EvidenceResponse",
    "ExplainRequest",
    "FeatureContribution",
    "FeatureImportanceResult",
    "HealthResponse",
    "HoneywellMapping",
    "HoneywellMappingResponse",
    "MarketContext",
    "MethodologyDoc",
    "ModelCard",
    "OptimizationResult",
    "PriceDemandPoint",
    "PriceExplanation",
    "PriceRange",
    "ScenarioResult",
    "SegmentDetails",
    "SegmentResult",
    "SensitivityResult",
]
