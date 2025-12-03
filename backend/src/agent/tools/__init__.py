"""LangChain tools for PrismIQ agent.

Uses LangChain v1.0+ @tool decorator pattern.
Tools are exported directly (not factory functions).
"""

from src.agent.tools.data_tools import (
    get_eda_summary,
    get_external_context,
    get_segment,
)
from src.agent.tools.doc_tools import (
    get_evidence,
    get_honeywell_mapping,
)
from src.agent.tools.pricing_tools import (
    explain_decision,
    optimize_price,
    sensitivity_analysis,
)

# All tools as a list for easy agent initialization
ALL_TOOLS = [
    optimize_price,
    explain_decision,
    sensitivity_analysis,
    get_segment,
    get_eda_summary,
    get_external_context,
    get_evidence,
    get_honeywell_mapping,
]

__all__ = [
    # Pricing tools
    "optimize_price",
    "explain_decision",
    "sensitivity_analysis",
    # Data tools
    "get_segment",
    "get_eda_summary",
    "get_external_context",
    # Documentation tools
    "get_evidence",
    "get_honeywell_mapping",
    # Convenience
    "ALL_TOOLS",
]
