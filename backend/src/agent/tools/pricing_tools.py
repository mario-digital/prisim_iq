"""Pricing-related tools for the PrismIQ agent.

These tools provide access to price optimization, explanation, and sensitivity analysis.
Uses LangChain v1.0+ @tool decorator pattern.
"""

from __future__ import annotations

from langchain_core.tools import tool
from loguru import logger

from src.agent.utils import run_sync, sanitize_error_message


@tool
def optimize_price(query: str = "current") -> str:  # noqa: ARG001
    """Get the optimal price recommendation for the current market context.

    Use this when the user asks about pricing, optimal price, what price to set,
    or recommendations. Returns price, confidence, expected demand and profit.

    Args:
        query: Ignored - always uses current context.
    """
    from src.agent.context import get_current_context
    from src.services.pricing_service import get_pricing_service

    try:
        context = get_current_context()
        pricing_service = get_pricing_service()

        # Run async service in sync context
        result = run_sync(pricing_service.get_recommendation(context))

        # Format applied rules as names (result.rules_applied contains AppliedRule objects)
        rule_names = [r.rule_name for r in (result.rules_applied or [])]

        return (
            f"Optimal Price: ${result.recommended_price:.2f}\n"
            f"Confidence Score: {result.confidence_score:.2%}\n"
            f"Expected Demand: {result.expected_demand:.2f} rides\n"
            f"Expected Profit: ${result.expected_profit:.2f}\n"
            f"Profit Uplift: {result.profit_uplift_percent:.1f}%\n"
            f"Segment: {result.segment.segment_name}\n"
            f"Model Used: {result.model_used}\n"
            f"Rules Applied: {', '.join(rule_names) if rule_names else 'None'}"
        )

    except Exception as e:
        logger.error(f"optimize_price tool error: {e}")
        return f"Error getting price recommendation: {sanitize_error_message(e)}"


@tool
def explain_decision(query: str = "current") -> str:  # noqa: ARG001
    """Get detailed explanation of a pricing recommendation.

    Use this when the user asks 'why', wants to understand the factors,
    needs justification, or asks about feature importance.
    Returns natural language summary and top contributing factors.

    Args:
        query: Ignored - always uses current context.
    """
    from src.agent.context import get_current_context
    from src.schemas.explanation import ExplainRequest
    from src.services.explanation_service import get_explanation_service

    try:
        context = get_current_context()
        explanation_service = get_explanation_service()

        request = ExplainRequest(
            context=context,
            include_trace=False,
            include_shap=True,
        )

        # Run async service in sync context
        result = run_sync(explanation_service.explain(request))

        # Format top factors
        top_factors = result.feature_importance[:5]
        factors_text = "\n".join([
            f"  - {f.display_name}: {f.importance:.1%} ({f.direction})"
            for f in top_factors
        ])

        # Agreement formatting based on available fields
        agree = result.model_agreement
        status_map = {
            "full_agreement": "Full agreement",
            "partial_agreement": "Partial agreement",
            "divergent": "Divergent",
        }
        status_text = status_map.get(getattr(agree, "status", ""), "Agreement")
        max_dev = getattr(agree, "max_deviation_percent", None)
        agree_line = (
            f"Model Agreement: {status_text}"
            + (f" (max deviation: {max_dev:.1f}%)" if isinstance(max_dev, (int, float)) else "")
        )

        return (
            f"Price Recommendation: ${result.recommendation.recommended_price:.2f}\n\n"
            f"Summary: {result.natural_language_summary}\n\n"
            f"Top Contributing Factors:\n{factors_text}\n\n"
            f"Key Factors: {', '.join(result.key_factors)}\n\n"
            f"{agree_line}"
        )

    except Exception as e:
        logger.error(f"explain_decision tool error: {e}")
        return f"Error generating explanation: {sanitize_error_message(e)}"


@tool
def sensitivity_analysis(query: str = "current") -> str:  # noqa: ARG001
    """Analyze how price recommendation changes under different assumptions.

    Use this when the user asks about robustness, sensitivity, 'what if' scenarios,
    price stability, or how confident they can be in the recommendation.
    Tests elasticity, demand, and cost variations.

    Args:
        query: Ignored - always uses current context.
    """
    from src.agent.context import get_current_context
    from src.services.sensitivity_service import get_sensitivity_service

    try:
        context = get_current_context()
        sensitivity_service = get_sensitivity_service()

        # Run async service in sync context
        result = run_sync(sensitivity_service.run_sensitivity_analysis(context))

        return (
            f"Sensitivity Analysis Results:\n\n"
            f"Base Price: ${result.base_price:.2f}\n"
            f"Base Profit: ${result.base_profit:.2f}\n\n"
            f"Price Confidence Band:\n"
            f"  - Minimum: ${result.confidence_band.min_price:.2f}\n"
            f"  - Maximum: ${result.confidence_band.max_price:.2f}\n"
            f"  - Range: ${result.confidence_band.price_range:.2f} "
            f"({result.confidence_band.range_percent:.1f}%)\n\n"
            f"Best Case: ${result.best_case.optimal_price:.2f} "
            f"(profit: ${result.best_case.expected_profit:.2f})\n"
            f"Worst Case: ${result.worst_case.optimal_price:.2f} "
            f"(profit: ${result.worst_case.expected_profit:.2f})\n\n"
            f"Robustness Score: {result.robustness_score:.1f}/100\n"
            f"Analysis Time: {result.analysis_time_ms:.1f}ms"
        )

    except Exception as e:
        logger.error(f"sensitivity_analysis tool error: {e}")
        return f"Error running sensitivity analysis: {sanitize_error_message(e)}"
