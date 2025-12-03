"""Policy checker node: validates hierarchy and proposes fixes."""

from __future__ import annotations

from loguru import logger

from src.orchestrator.state import OrchState
from src.policy.rules import auto_fix_suggestions, check_hierarchy


def _parse_optimizer_price(text: str) -> float | None:
    """Extract the numeric price from optimizer output text."""
    import re

    m = re.search(r"Optimal Price:\s*\$?([0-9]+(?:\.[0-9]+)?)", text)
    if m:
        try:
            return float(m.group(1))
        except Exception:  # pragma: no cover
            return None
    return None


def policy_node(state: OrchState) -> dict:
    """Validate/repair price hierarchy (New > Exchange > Repair > USM).

    Inputs:
        - context.tier_prices (optional) → dict with keys new|exchange|repair|usm
        - outputs.optimizer (optional) → string, parsed to derive a baseline

    Output:
        - outputs.policy → { tier_prices, violations, suggestions, summary }
    """
    ctx_dict = state.get("context") or {}
    outputs = dict(state.get("outputs") or {})

    # Gather tier prices
    tier_prices: dict[str, float] | None = None
    tp_ctx = ctx_dict.get("tier_prices") if isinstance(ctx_dict, dict) else None
    if isinstance(tp_ctx, dict):
        # normalize keys
        tier_prices = {k.lower(): float(v) for k, v in tp_ctx.items() if k}

    if tier_prices is None:
        # Attempt to derive from optimizer output as a baseline
        opt_text = outputs.get("optimizer") if isinstance(outputs.get("optimizer"), str) else None
        base_price = _parse_optimizer_price(opt_text or "")
        if base_price is not None:
            tier_prices = {
                "new": base_price,
                "exchange": base_price * 0.95,
                "repair": base_price * 0.90,
                "usm": base_price * 0.85,
            }
        else:
            # If nothing is available, use a safe default to avoid false violations
            logger.warning("policy_node: no tier prices available; using defaults")
            tier_prices = {"new": 100.0, "exchange": 95.0, "repair": 90.0, "usm": 85.0}

    violations_objs = check_hierarchy(tier_prices)
    violations = [v.model_dump() for v in violations_objs]
    suggestions = [s.model_dump() for s in auto_fix_suggestions(tier_prices, violations_objs)]

    # Build simple summary
    if violations:
        summary = (
            "Policy Check: Violations detected in tier hierarchy. "
            f"Suggested fixes: {len(suggestions)}"
        )
    else:
        summary = "Policy Check: No hierarchy violations detected."

    outputs["policy"] = {
        "tier_prices": tier_prices,
        "violations": violations,
        "suggestions": suggestions,
        "summary": summary,
    }

    return {"outputs": outputs}
