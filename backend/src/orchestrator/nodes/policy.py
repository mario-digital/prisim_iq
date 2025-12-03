"""Policy checker node: validates hierarchy and proposes fixes.

Note: This node relies on set_current_context for tool invocation context.
The current implementation is NOT fully concurrent-safe due to process-global
context. For concurrent async execution, tools should be refactored to accept
explicit context objects.
"""

from __future__ import annotations

import re

from loguru import logger

from src.orchestrator.state import OrchState
from src.policy.rules import auto_fix_suggestions, check_hierarchy

# Patterns for extracting price from optimizer output (tolerant to format variations)
_PRICE_PATTERNS = [
    r"Optimal Price:\s*\$?([0-9]+(?:\.[0-9]+)?)",  # "Optimal Price: $123.45"
    r"recommended price[:\s]+\$?([0-9]+(?:\.[0-9]+)?)",  # "recommended price: 123"
    r"price[:\s]+\$?([0-9]+(?:\.[0-9]+)?)",  # fallback: any "price: X"
]


def _parse_optimizer_price(text: str) -> float | None:
    """Extract the numeric price from optimizer output text.

    Tries multiple patterns in order of specificity to be tolerant of format changes.
    Expected format: "Optimal Price: $123.45" but also handles variations.
    """
    if not text:
        return None

    for pattern in _PRICE_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except (ValueError, TypeError):
                continue
    return None


def _safe_parse_tier_prices(raw: dict) -> tuple[dict[str, float], list[str]]:
    """Safely parse tier prices dict, handling non-numeric values.

    Returns:
        Tuple of (parsed_prices, errors) where errors lists any conversion failures.
    """
    parsed: dict[str, float] = {}
    errors: list[str] = []

    for k, v in raw.items():
        if not k:
            continue
        key = str(k).lower()
        try:
            parsed[key] = float(v)
        except (ValueError, TypeError) as e:
            errors.append(f"Invalid value for tier '{key}': {v!r} ({e})")

    return parsed, errors


def policy_node(state: OrchState) -> dict:
    """Validate/repair price hierarchy (New > Exchange > Repair > USM).

    Inputs:
        - context.tier_prices (optional) → dict with keys new|exchange|repair|usm
        - outputs.optimizer (optional) → string, parsed to derive a baseline

    Output:
        - outputs.policy → { tier_prices, violations, suggestions, summary, source }

    The 'source' field indicates where tier_prices came from:
        - "context": Provided explicitly in context.tier_prices
        - "optimizer": Derived from optimizer output
        - "default": Hardcoded fallback (validation may not reflect real prices)
    """
    ctx_dict = state.get("context") or {}
    outputs = dict(state.get("outputs") or {})

    # Gather tier prices with source tracking
    tier_prices: dict[str, float] | None = None
    source: str = "default"
    parse_errors: list[str] = []

    tp_ctx = ctx_dict.get("tier_prices") if isinstance(ctx_dict, dict) else None
    if isinstance(tp_ctx, dict):
        tier_prices, parse_errors = _safe_parse_tier_prices(tp_ctx)
        if parse_errors:
            logger.warning(f"policy_node: tier_prices parse errors: {parse_errors}")
        if tier_prices:
            source = "context"
            logger.debug(f"policy_node: using tier_prices from context: {tier_prices}")

    if tier_prices is None or not tier_prices:
        # Attempt to derive from optimizer output as a baseline
        opt_text = outputs.get("optimizer") if isinstance(outputs.get("optimizer"), str) else None
        base_price = _parse_optimizer_price(opt_text or "")
        if base_price is not None:
            tier_prices = {
                "new": base_price,
                "exchange": round(base_price * 0.95, 2),
                "repair": round(base_price * 0.90, 2),
                "usm": round(base_price * 0.85, 2),
            }
            source = "optimizer"
            logger.info(f"policy_node: derived tier_prices from optimizer (base={base_price})")
        else:
            # If nothing is available, use a safe default to avoid false violations
            logger.warning(
                "policy_node: no tier prices available from context or optimizer; "
                "using hardcoded defaults - validation may not reflect actual prices"
            )
            tier_prices = {"new": 100.0, "exchange": 95.0, "repair": 90.0, "usm": 85.0}
            source = "default"

    violations_objs = check_hierarchy(tier_prices)
    violations = [v.model_dump() for v in violations_objs]
    suggestions = [s.model_dump() for s in auto_fix_suggestions(tier_prices, violations_objs)]

    # Build summary with source awareness
    source_note = f" (prices source: {source})"
    if violations:
        summary = (
            f"Policy Check: Violations detected in tier hierarchy{source_note}. "
            f"Suggested fixes: {len(suggestions)}"
        )
    else:
        summary = f"Policy Check: No hierarchy violations detected{source_note}."

    outputs["policy"] = {
        "tier_prices": tier_prices,
        "violations": violations,
        "suggestions": suggestions,
        "summary": summary,
        "source": source,  # Downstream visibility into price origin
        "parse_errors": parse_errors if parse_errors else None,
    }

    return {"outputs": outputs}
