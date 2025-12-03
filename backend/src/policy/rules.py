"""Policy rules and helpers for pricing hierarchy and constraints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Violation(BaseModel):
    """Represents a detected policy violation."""

    type: str
    message: str
    details: dict[str, float] | None = None


class Suggestion(BaseModel):
    """Represents an auto-fix suggestion for a violation."""

    action: str = Field(description="What to change (e.g., decrease, increase)")
    field: str = Field(description="Which tier/field to modify")
    new_value: float = Field(description="Suggested corrected value")
    reason: str


# Default tier thresholds: minimum percentage gap between adjacent tiers
# e.g., 0.03 means the higher tier must be at least 3% more than the lower tier
DEFAULT_TIER_THRESHOLDS: dict[str, float] = {
    "new_exchange": 0.03,      # New must be >= 3% above Exchange
    "exchange_repair": 0.03,   # Exchange must be >= 3% above Repair
    "repair_usm": 0.03,        # Repair must be >= 3% above USM
}

# Segment-specific threshold overrides (more aggressive margins for premium segments)
SEGMENT_THRESHOLD_OVERRIDES: dict[str, dict[str, float]] = {
    "premium": {
        "new_exchange": 0.05,
        "exchange_repair": 0.05,
        "repair_usm": 0.05,
    },
    "budget": {
        "new_exchange": 0.02,
        "exchange_repair": 0.02,
        "repair_usm": 0.02,
    },
}

# Region-specific threshold overrides
REGION_THRESHOLD_OVERRIDES: dict[str, dict[str, float]] = {
    "EMEA": {
        "new_exchange": 0.04,
        "exchange_repair": 0.04,
        "repair_usm": 0.04,
    },
    "APAC": {
        "new_exchange": 0.02,
        "exchange_repair": 0.02,
        "repair_usm": 0.02,
    },
}


def check_hierarchy(prices: dict[str, float]) -> list[Violation]:
    """Ensure New > Exchange > Repair > USM ordering.

    Args:
        prices: Mapping of price tiers, expected keys: new, exchange, repair, usm.

    Returns:
        List of violations (empty if none).
    """
    order = ["new", "exchange", "repair", "usm"]
    v: list[Violation] = []

    # Only evaluate known keys
    vals = {k: prices[k] for k in order if k in prices}
    for higher, lower in zip(order, order[1:], strict=False):
        if higher in vals and lower in vals and not (vals[higher] > vals[lower]):
                v.append(
                    Violation(
                        type="hierarchy_inversion",
                        message=f"Expected {higher} > {lower}, but got {vals[higher]:.2f} <= {vals[lower]:.2f}",
                        details={higher: vals[higher], lower: vals[lower]},
                    )
                )
    return v


def auto_fix_suggestions(prices: dict[str, float], violations: list[Violation]) -> list[Suggestion]:  # noqa: ARG001
    """Propose minimal changes to satisfy hierarchy.

    Strategy: Nudge lower tiers below the tier above by a small epsilon when violated.
    """
    order = ["new", "exchange", "repair", "usm"]
    vals = {k: prices.get(k) for k in order}
    suggestions: list[Suggestion] = []
    eps = 0.01

    for higher, lower in zip(order, order[1:], strict=False):
        hv = vals.get(higher)
        lv = vals.get(lower)
        if hv is None or lv is None:
            continue
        if lv >= hv:
            new_val = max(hv - eps, 0.0)
            suggestions.append(
                Suggestion(
                    action="decrease",
                    field=lower,
                    new_value=new_val,
                    reason=f"Ensure {higher} ({hv:.2f}) remains > {lower} (set to {new_val:.2f})",
                )
            )

    return suggestions


def _get_thresholds(
    segment: str | None = None,
    region: str | None = None,
    custom_thresholds: dict[str, float] | None = None,
) -> dict[str, float]:
    """Resolve effective thresholds based on segment/region overrides.

    Priority: custom_thresholds > segment > region > defaults
    """
    thresholds = DEFAULT_TIER_THRESHOLDS.copy()

    # Apply region overrides
    if region and region.upper() in REGION_THRESHOLD_OVERRIDES:
        thresholds.update(REGION_THRESHOLD_OVERRIDES[region.upper()])

    # Apply segment overrides (higher priority than region)
    if segment and segment.lower() in SEGMENT_THRESHOLD_OVERRIDES:
        thresholds.update(SEGMENT_THRESHOLD_OVERRIDES[segment.lower()])

    # Apply custom thresholds (highest priority)
    if custom_thresholds:
        thresholds.update(custom_thresholds)

    return thresholds


def check_tier_thresholds(
    prices: dict[str, float],
    segment: str | None = None,
    region: str | None = None,
    custom_thresholds: dict[str, float] | None = None,
) -> list[Violation]:
    """Validate minimum percentage gaps between price tiers.

    Ensures that higher tiers maintain sufficient margin above lower tiers
    to prevent illogical cross-tier inversions and maintain pricing integrity.

    Args:
        prices: Mapping of price tiers, expected keys: new, exchange, repair, usm.
        segment: Optional customer segment for threshold overrides (e.g., "premium", "budget").
        region: Optional region for threshold overrides (e.g., "EMEA", "APAC").
        custom_thresholds: Optional dict to override specific thresholds.
            Keys: "new_exchange", "exchange_repair", "repair_usm"
            Values: Minimum percentage gap (e.g., 0.05 = 5%)

    Returns:
        List of violations for insufficient tier margins.

    Example:
        >>> prices = {"new": 100.0, "exchange": 99.0, "repair": 90.0, "usm": 85.0}
        >>> violations = check_tier_thresholds(prices)
        >>> # Will flag new→exchange gap (1%) as below 3% threshold
    """
    order = ["new", "exchange", "repair", "usm"]
    violations: list[Violation] = []

    # Only evaluate known keys
    vals = {k: prices[k] for k in order if k in prices}

    # Get effective thresholds
    thresholds = _get_thresholds(segment, region, custom_thresholds)

    tier_pairs = [
        ("new", "exchange", "new_exchange"),
        ("exchange", "repair", "exchange_repair"),
        ("repair", "usm", "repair_usm"),
    ]

    for higher, lower, threshold_key in tier_pairs:
        if higher not in vals or lower not in vals:
            continue

        higher_price = vals[higher]
        lower_price = vals[lower]
        min_threshold = thresholds.get(threshold_key, 0.03)

        # Calculate actual gap as percentage of higher tier
        if higher_price <= 0:
            continue  # Avoid division by zero

        actual_gap = (higher_price - lower_price) / higher_price

        if actual_gap < min_threshold:
            violations.append(
                Violation(
                    type="insufficient_tier_margin",
                    message=(
                        f"Insufficient margin between {higher} (${higher_price:.2f}) and "
                        f"{lower} (${lower_price:.2f}): {actual_gap:.1%} < {min_threshold:.1%} required"
                    ),
                    details={
                        higher: higher_price,
                        lower: lower_price,
                        "actual_gap_pct": round(actual_gap * 100, 2),
                        "required_gap_pct": round(min_threshold * 100, 2),
                    },
                )
            )

    return violations


def auto_fix_threshold_suggestions(
    prices: dict[str, float],
    violations: list[Violation],  # noqa: ARG001
    segment: str | None = None,
    region: str | None = None,
    custom_thresholds: dict[str, float] | None = None,
) -> list[Suggestion]:
    """Propose fixes for threshold violations.

    Strategy: Decrease lower tier to achieve the required margin.
    """
    order = ["new", "exchange", "repair", "usm"]
    vals = {k: prices.get(k) for k in order}
    suggestions: list[Suggestion] = []

    thresholds = _get_thresholds(segment, region, custom_thresholds)

    tier_pairs = [
        ("new", "exchange", "new_exchange"),
        ("exchange", "repair", "exchange_repair"),
        ("repair", "usm", "repair_usm"),
    ]

    for higher, lower, threshold_key in tier_pairs:
        hv = vals.get(higher)
        lv = vals.get(lower)
        if hv is None or lv is None or hv <= 0:
            continue

        min_threshold = thresholds.get(threshold_key, 0.03)
        actual_gap = (hv - lv) / hv

        if actual_gap < min_threshold:
            # Calculate the required lower price to achieve threshold
            required_lower = hv * (1 - min_threshold)
            # Round down slightly to ensure compliance
            suggested_value = round(required_lower - 0.01, 2)
            suggested_value = max(suggested_value, 0.0)

            suggestions.append(
                Suggestion(
                    action="decrease",
                    field=lower,
                    new_value=suggested_value,
                    reason=(
                        f"Reduce {lower} from ${lv:.2f} to ${suggested_value:.2f} "
                        f"to achieve {min_threshold:.1%} margin below {higher} (${hv:.2f})"
                    ),
                )
            )

    return suggestions


def check_all_policies(
    prices: dict[str, float],
    segment: str | None = None,
    region: str | None = None,
    custom_thresholds: dict[str, float] | None = None,
) -> tuple[list[Violation], list[Suggestion]]:
    """Run all policy checks and return combined violations and suggestions.

    Combines:
    - Hierarchy checks (strict ordering)
    - Tier threshold checks (minimum margins)

    Args:
        prices: Mapping of price tiers.
        segment: Optional customer segment for threshold overrides.
        region: Optional region for threshold overrides.
        custom_thresholds: Optional custom threshold overrides.

    Returns:
        Tuple of (all_violations, all_suggestions).
    """
    # Run hierarchy check
    hierarchy_violations = check_hierarchy(prices)
    hierarchy_suggestions = auto_fix_suggestions(prices, hierarchy_violations)

    # Run threshold check
    threshold_violations = check_tier_thresholds(
        prices, segment, region, custom_thresholds
    )
    threshold_suggestions = auto_fix_threshold_suggestions(
        prices, threshold_violations, segment, region, custom_thresholds
    )

    all_violations = hierarchy_violations + threshold_violations
    all_suggestions = hierarchy_suggestions + threshold_suggestions

    return all_violations, all_suggestions

