"""Evidence and Honeywell mapping endpoints."""

import json
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Header, Query
from fastapi.responses import PlainTextResponse
from loguru import logger
from pydantic import ValidationError

from src.schemas.evidence import (
    DataCard,
    EvidenceResponse,
    HoneywellMappingResponse,
    MethodologyDoc,
    ModelCard,
)

router = APIRouter(tags=["Evidence"])

# Base path for data files
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
CARDS_DIR = DATA_DIR / "cards"
EVIDENCE_DIR = DATA_DIR / "evidence"


def _load_model_cards() -> list[ModelCard]:
    """Load all model cards from the cards directory.

    Auto-discovers all *_model_card.json files in the cards directory.
    This excludes data cards and other JSON files.
    """
    model_cards = []
    # Auto-discover model cards using naming convention
    card_files = sorted(CARDS_DIR.glob("*_model_card.json"))

    if not card_files:
        logger.warning(f"No model cards found in {CARDS_DIR}")
        return model_cards

    for filepath in card_files:
        try:
            with open(filepath) as f:
                data = json.load(f)
                model_cards.append(ModelCard.model_validate(data))
                logger.debug(f"Loaded model card: {filepath.name}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in model card {filepath.name}: {e}")
            # Skip corrupt files, continue loading others
        except ValidationError as e:
            logger.error(f"Invalid schema in model card {filepath.name}: {e}")
            # Skip files with wrong structure, continue loading others
        except Exception as e:
            logger.error(f"Error loading model card {filepath.name}: {e}")

    logger.info(f"Loaded {len(model_cards)} model cards")
    return model_cards


def _load_data_card() -> DataCard:
    """Load the data card."""
    filepath = CARDS_DIR / "dynamic_pricing_data_card.json"
    if not filepath.exists():
        logger.error(f"Required data card not found: {filepath}")
        raise FileNotFoundError(f"Data card not found: {filepath}")
    try:
        with open(filepath) as f:
            data = json.load(f)
            logger.debug(f"Loaded data card: {filepath.name}")
            return DataCard.model_validate(data)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in data card: {e}")
        raise ValueError(f"Data card contains invalid JSON: {e}") from e
    except ValidationError as e:
        logger.error(f"Invalid schema in data card: {e}")
        raise ValueError(f"Data card has invalid schema: {e}") from e


def _load_methodology() -> MethodologyDoc:
    """Load methodology documentation."""
    filepath = EVIDENCE_DIR / "methodology.json"
    if not filepath.exists():
        logger.error(f"Required methodology doc not found: {filepath}")
        raise FileNotFoundError(f"Methodology documentation not found: {filepath}")
    try:
        with open(filepath) as f:
            data = json.load(f)
            logger.debug(f"Loaded methodology: {filepath.name}")
            return MethodologyDoc.model_validate(data)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in methodology doc: {e}")
        raise ValueError(f"Methodology documentation contains invalid JSON: {e}") from e
    except ValidationError as e:
        logger.error(f"Invalid schema in methodology doc: {e}")
        raise ValueError(f"Methodology documentation has invalid schema: {e}") from e


def _load_honeywell_mapping() -> HoneywellMappingResponse:
    """Load and validate Honeywell mapping data."""
    filepath = EVIDENCE_DIR / "honeywell_mapping.json"
    if not filepath.exists():
        logger.error(f"Required Honeywell mapping not found: {filepath}")
        raise FileNotFoundError(f"Honeywell mapping not found: {filepath}")
    try:
        with open(filepath) as f:
            data = json.load(f)
            logger.debug(f"Loaded Honeywell mapping: {filepath.name}")
            return HoneywellMappingResponse.model_validate(data)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in Honeywell mapping: {e}")
        raise ValueError(f"Honeywell mapping contains invalid JSON: {e}") from e
    except ValidationError as e:
        logger.error(f"Invalid schema in Honeywell mapping: {e}")
        raise ValueError(f"Honeywell mapping has invalid schema: {e}") from e


@lru_cache(maxsize=1)
def get_cached_evidence() -> EvidenceResponse:
    """Load and cache evidence - regenerate on restart."""
    logger.info("Loading evidence data (will be cached)")
    return EvidenceResponse(
        model_cards=_load_model_cards(),
        data_card=_load_data_card(),
        methodology=_load_methodology(),
        generated_at=datetime.now(UTC),
        cache_ttl_seconds=86400,
    )


@lru_cache(maxsize=1)
def get_cached_honeywell_mapping() -> HoneywellMappingResponse:
    """Load and cache Honeywell mapping - regenerate on restart."""
    logger.info("Loading Honeywell mapping (will be cached)")
    return _load_honeywell_mapping()


def _render_evidence_markdown(evidence: EvidenceResponse) -> str:
    """Render evidence as markdown."""
    lines = ["# PrismIQ Evidence Documentation\n"]

    # Methodology
    lines.append(f"## {evidence.methodology.title}\n")
    for section in evidence.methodology.sections:
        lines.append(f"### {section.heading}\n")
        lines.append(f"{section.content}\n")
        if section.subsections:
            for sub in section.subsections:
                lines.append(f"#### {sub.heading}\n")
                lines.append(f"{sub.content}\n")

    # Model Cards
    lines.append("## Model Cards\n")
    for card in evidence.model_cards:
        lines.append(f"### {card.model_name} (v{card.model_version})\n")
        lines.append(f"**Architecture:** {card.model_details.architecture}\n")
        lines.append(f"**Primary Use:** {card.intended_use.primary_use}\n")
        lines.append(f"**Performance:** R²={card.metrics.r2_score:.4f}, ")
        lines.append(f"MAE={card.metrics.mae:.4f}, RMSE={card.metrics.rmse:.4f}\n")
        lines.append("\n**Limitations:**\n")
        for lim in card.limitations[:3]:  # First 3 limitations
            lines.append(f"- {lim}\n")
        lines.append("\n")

    # Data Card
    lines.append("## Data Card\n")
    lines.append(f"### {evidence.data_card.dataset_name} (v{evidence.data_card.version})\n")
    lines.append(f"**Source:** {evidence.data_card.source.origin}\n")
    stats = evidence.data_card.statistics
    lines.append(f"**Statistics:** {stats.row_count} rows, {stats.column_count} columns\n")
    lines.append(f"**Intended Use:** {evidence.data_card.intended_use}\n")

    lines.append(f"\n---\n*Generated: {evidence.generated_at.isoformat()}*\n")

    return "".join(lines)


def _render_honeywell_markdown(mapping: HoneywellMappingResponse) -> str:
    """Render Honeywell mapping as markdown."""
    lines = [f"# {mapping.title}\n"]
    lines.append(f"{mapping.description}\n\n")

    # Mapping table
    lines.append("| Ride-Sharing Concept | Honeywell Equivalent | Category | Rationale |\n")
    lines.append("|---------------------|---------------------|----------|----------|\n")
    for m in mapping.mappings:
        lines.append(
            f"| {m.ride_sharing_concept} | {m.honeywell_equivalent} | "
            f"{m.category} | {m.rationale} |\n"
        )

    lines.append(f"\n## Business Context\n\n{mapping.business_context}\n")

    return "".join(lines)


def _determine_format(
    format_param: str | None,
    accept_header: str | None,
) -> Literal["json", "markdown"]:
    """Determine output format from query param or Accept header."""
    # Query param takes precedence
    if format_param:
        return format_param

    # Check Accept header
    if accept_header:
        if "text/markdown" in accept_header:
            return "markdown"
        if "text/plain" in accept_header:
            return "markdown"

    return "json"


@router.get(
    "/evidence",
    response_model=EvidenceResponse,
    summary="Get Evidence Documentation",
    description="""
    Returns all model cards, data card, and methodology documentation.

    Supports multiple output formats:
    - JSON (default): Structured data for programmatic access
    - Markdown: Human-readable documentation

    Format can be specified via:
    - Query parameter: `?format=markdown`
    - Accept header: `Accept: text/markdown`

    Response is cached for 24 hours (86400 seconds).
    """,
    responses={
        200: {
            "description": "Evidence documentation",
            "content": {
                "application/json": {
                    "example": {
                        "model_cards": [],
                        "data_card": {},
                        "methodology": {},
                        "generated_at": "2024-12-02T10:00:00Z",
                        "cache_ttl_seconds": 86400,
                    }
                },
                "text/markdown": {"example": "# PrismIQ Evidence Documentation\n..."},
            },
        }
    },
)
async def get_evidence(
    format: Literal["json", "markdown"] | None = Query(
        default=None,
        description="Output format (json or markdown)",
    ),
    accept: str | None = Header(default=None, alias="Accept"),
) -> EvidenceResponse | PlainTextResponse:
    """
    Return all model cards, data card, and methodology documentation.

    The evidence package provides complete documentation for model transparency
    and regulatory compliance.
    """
    evidence = get_cached_evidence()
    output_format = _determine_format(format, accept)

    if output_format == "markdown":
        return PlainTextResponse(
            content=_render_evidence_markdown(evidence),
            media_type="text/markdown",
        )

    return evidence


@router.get(
    "/honeywell_mapping",
    response_model=HoneywellMappingResponse,
    summary="Get Honeywell Concept Mapping",
    description="""
    Returns the mapping between ride-sharing pricing concepts and
    Honeywell enterprise equivalents.

    This mapping demonstrates how dynamic pricing concepts validated
    in the ride-sharing domain translate to enterprise applications.

    Supports multiple output formats:
    - JSON (default): Structured data for programmatic access
    - Markdown: Human-readable table format

    Format can be specified via:
    - Query parameter: `?format=markdown`
    - Accept header: `Accept: text/markdown`
    """,
    responses={
        200: {
            "description": "Honeywell mapping documentation",
            "content": {
                "application/json": {
                    "example": {
                        "title": "Ride-Sharing to Honeywell Enterprise Mapping",
                        "mappings": [],
                        "business_context": "...",
                    }
                },
                "text/markdown": {"example": "# Ride-Sharing to Honeywell...\n..."},
            },
        }
    },
)
async def get_honeywell_mapping(
    format: Literal["json", "markdown"] | None = Query(
        default=None,
        description="Output format (json or markdown)",
    ),
    accept: str | None = Header(default=None, alias="Accept"),
) -> HoneywellMappingResponse | PlainTextResponse:
    """
    Return ride-sharing to Honeywell enterprise concept mapping.

    Provides business rationale for how pricing concepts translate
    to enterprise applications like HVAC, aerospace, and industrial products.
    """
    mapping = get_cached_honeywell_mapping()
    output_format = _determine_format(format, accept)

    if output_format == "markdown":
        rendered = _render_honeywell_markdown(mapping)
        return PlainTextResponse(
            content=rendered,
            media_type="text/markdown",
        )

    return mapping
