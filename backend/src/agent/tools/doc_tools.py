"""Documentation tools for the PrismIQ agent.

These tools provide access to evidence documentation and Honeywell mapping.
"""

from __future__ import annotations

from langchain_core.tools import Tool
from loguru import logger


def create_get_evidence_tool() -> Tool:
    """Create the get_evidence tool for model and methodology documentation.

    Returns:
        LangChain Tool that returns evidence documentation.
    """

    def get_evidence(_input: str) -> str:
        """Get model cards and methodology documentation."""
        from src.api.routers.evidence import get_cached_evidence

        try:
            evidence = get_cached_evidence()

            # Format model cards summary
            model_cards_text = ""
            for card in evidence.model_cards:
                model_cards_text += (
                    f"\n{card.model_name} (v{card.model_version}):\n"
                    f"  - Architecture: {card.model_details.architecture}\n"
                    f"  - Primary Use: {card.intended_use.primary_use}\n"
                    f"  - R² Score: {card.metrics.r2_score:.4f}\n"
                    f"  - MAE: {card.metrics.mae:.4f}\n"
                    f"  - RMSE: {card.metrics.rmse:.4f}\n"
                )

            # Format methodology summary
            methodology_text = f"{evidence.methodology.title}\n"
            for section in evidence.methodology.sections[:3]:  # First 3 sections
                methodology_text += f"  - {section.heading}\n"

            # Format data card summary
            data_card = evidence.data_card
            data_card_text = (
                f"Dataset: {data_card.dataset_name} (v{data_card.version})\n"
                f"  - Source: {data_card.source.origin}\n"
                f"  - Records: {data_card.statistics.row_count:,}\n"
                f"  - Features: {data_card.statistics.column_count}\n"
                f"  - Intended Use: {data_card.intended_use}"
            )

            return (
                f"PrismIQ Evidence Documentation\n"
                f"{'='*40}\n\n"
                f"Model Cards:{model_cards_text}\n"
                f"Methodology Overview:\n{methodology_text}\n"
                f"Data Card:\n{data_card_text}\n\n"
                f"Generated: {evidence.generated_at.isoformat()}"
            )

        except FileNotFoundError as e:
            return f"Error: Evidence documentation not found: {str(e)}"
        except Exception as e:
            logger.error(f"get_evidence tool error: {e}")
            return f"Error loading evidence documentation: {str(e)}"

    return Tool(
        name="get_evidence",
        description=(
            "Get model cards, data card, and methodology documentation. "
            "Use this when the user asks about the models, how they work, "
            "methodology, data provenance, model performance metrics, "
            "or documentation. Returns model architecture, metrics, and data sources."
        ),
        func=get_evidence,
    )


def create_get_honeywell_mapping_tool() -> Tool:
    """Create the get_honeywell_mapping tool for enterprise concept mapping.

    Returns:
        LangChain Tool that returns Honeywell enterprise mapping.
    """

    def get_honeywell_mapping(_input: str) -> str:
        """Get ride-sharing to Honeywell enterprise concept mapping."""
        from src.api.routers.evidence import get_cached_honeywell_mapping

        try:
            mapping = get_cached_honeywell_mapping()

            # Format mappings
            mappings_text = ""
            for m in mapping.mappings:
                mappings_text += (
                    f"\n{m.ride_sharing_concept} → {m.honeywell_equivalent}\n"
                    f"  Category: {m.category}\n"
                    f"  Rationale: {m.rationale}\n"
                )

            return (
                f"{mapping.title}\n"
                f"{'='*50}\n\n"
                f"{mapping.description}\n\n"
                f"Concept Mappings:{mappings_text}\n"
                f"Business Context:\n{mapping.business_context}"
            )

        except FileNotFoundError as e:
            return f"Error: Honeywell mapping not found: {str(e)}"
        except Exception as e:
            logger.error(f"get_honeywell_mapping tool error: {e}")
            return f"Error loading Honeywell mapping: {str(e)}"

    return Tool(
        name="get_honeywell_mapping",
        description=(
            "Get the mapping between ride-sharing pricing concepts and "
            "Honeywell enterprise equivalents. Use this when the user asks about "
            "enterprise applications, Honeywell, how concepts translate to business, "
            "or industrial pricing applications. Returns concept mappings with rationale."
        ),
        func=get_honeywell_mapping,
    )

