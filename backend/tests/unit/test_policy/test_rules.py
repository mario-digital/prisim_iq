import math

from src.policy.rules import (
    auto_fix_suggestions,
    auto_fix_threshold_suggestions,
    check_all_policies,
    check_hierarchy,
    check_tier_thresholds,
)


def test_check_hierarchy_no_violations() -> None:
    prices = {"new": 100.0, "exchange": 95.0, "repair": 90.0, "usm": 85.0}
    v = check_hierarchy(prices)
    assert v == []


def test_check_hierarchy_detects_inversions() -> None:
    prices = {"new": 100.0, "exchange": 102.0, "repair": 90.0, "usm": 80.0}
    v = check_hierarchy(prices)
    # Should flag exchange >= new
    assert any(vi.type == "hierarchy_inversion" for vi in v)


def test_auto_fix_suggestions_proposes_decrease() -> None:
    prices = {"new": 100.0, "exchange": 102.0, "repair": 90.0, "usm": 80.0}
    v = check_hierarchy(prices)
    s = auto_fix_suggestions(prices, v)
    # Should suggest decreasing exchange below new
    assert any(sug.field == "exchange" and sug.action == "decrease" for sug in s)
    # New suggested value is slightly below new
    exchange_fix = next(sug for sug in s if sug.field == "exchange")
    assert exchange_fix.new_value < prices["new"]
    assert math.isclose(exchange_fix.new_value, prices["new"] - 0.01, rel_tol=0, abs_tol=1e-9)


# ============ Tier Threshold Tests ============


def test_check_tier_thresholds_no_violations() -> None:
    """Prices with >3% gaps pass threshold checks."""
    prices = {"new": 100.0, "exchange": 95.0, "repair": 90.0, "usm": 85.0}
    v = check_tier_thresholds(prices)
    assert v == []


def test_check_tier_thresholds_detects_insufficient_margin() -> None:
    """Prices with <3% gap between new and exchange should flag violation."""
    prices = {"new": 100.0, "exchange": 99.0, "repair": 90.0, "usm": 85.0}
    v = check_tier_thresholds(prices)
    assert len(v) == 1
    assert v[0].type == "insufficient_tier_margin"
    assert "new" in v[0].message
    assert "exchange" in v[0].message
    assert v[0].details is not None
    assert v[0].details["actual_gap_pct"] == 1.0  # 1%
    assert v[0].details["required_gap_pct"] == 3.0  # 3%


def test_check_tier_thresholds_multiple_violations() -> None:
    """Multiple insufficient margins detected."""
    prices = {"new": 100.0, "exchange": 99.5, "repair": 99.0, "usm": 98.5}
    v = check_tier_thresholds(prices)
    assert len(v) == 3  # All three gaps are < 3%


def test_check_tier_thresholds_segment_override_premium() -> None:
    """Premium segment requires 5% gap; 4% should fail."""
    prices = {"new": 100.0, "exchange": 96.0, "repair": 90.0, "usm": 85.0}
    # Default (3%): passes
    v_default = check_tier_thresholds(prices)
    assert len(v_default) == 0
    # Premium (5%): fails new→exchange (4% gap)
    v_premium = check_tier_thresholds(prices, segment="premium")
    assert len(v_premium) == 1
    assert "new" in v_premium[0].message


def test_check_tier_thresholds_segment_override_budget() -> None:
    """Budget segment requires only 2% gap."""
    prices = {"new": 100.0, "exchange": 98.5, "repair": 96.5, "usm": 94.5}
    # Default (3%): fails (1.5%, ~2%, ~2% gaps)
    v_default = check_tier_thresholds(prices)
    assert len(v_default) == 3
    # Budget (2%): new→exchange still fails (1.5% < 2%)
    # But exchange→repair (2.03%) and repair→usm (2.07%) pass
    v_budget = check_tier_thresholds(prices, segment="budget")
    # Only 1 violation (new→exchange at 1.5% < 2%)
    assert len(v_budget) == 1
    assert "new" in v_budget[0].message


def test_check_tier_thresholds_region_override_emea() -> None:
    """EMEA region requires 4% gap."""
    prices = {"new": 100.0, "exchange": 96.5, "repair": 92.5, "usm": 88.5}
    # Default (3%): passes (3.5%, 4.1%, 4.3% gaps)
    v_default = check_tier_thresholds(prices)
    assert len(v_default) == 0
    # EMEA (4%): new→exchange fails (3.5% < 4%)
    v_emea = check_tier_thresholds(prices, region="EMEA")
    assert len(v_emea) == 1


def test_check_tier_thresholds_custom_override() -> None:
    """Custom thresholds take highest priority."""
    prices = {"new": 100.0, "exchange": 95.0, "repair": 90.0, "usm": 85.0}
    # Default: passes (5% gaps)
    v_default = check_tier_thresholds(prices)
    assert len(v_default) == 0
    # Custom 10% threshold: fails
    v_custom = check_tier_thresholds(
        prices, custom_thresholds={"new_exchange": 0.10}
    )
    assert len(v_custom) == 1
    assert v_custom[0].details is not None
    assert v_custom[0].details["required_gap_pct"] == 10.0


def test_check_tier_thresholds_partial_prices() -> None:
    """Only available tiers are checked."""
    prices = {"new": 100.0, "exchange": 99.0}  # Missing repair/usm
    v = check_tier_thresholds(prices)
    assert len(v) == 1  # Only new→exchange checked
    assert "new" in v[0].message


def test_auto_fix_threshold_suggestions() -> None:
    """Suggestions propose decreasing lower tier to achieve margin."""
    prices = {"new": 100.0, "exchange": 99.0, "repair": 90.0, "usm": 85.0}
    v = check_tier_thresholds(prices)
    s = auto_fix_threshold_suggestions(prices, v)
    assert len(s) == 1
    assert s[0].field == "exchange"
    assert s[0].action == "decrease"
    # Should suggest ~96.99 to achieve 3% margin below 100
    assert s[0].new_value < 97.0
    assert s[0].new_value >= 96.0


def test_auto_fix_threshold_suggestions_with_segment() -> None:
    """Suggestions use segment-specific thresholds."""
    prices = {"new": 100.0, "exchange": 96.0, "repair": 90.0, "usm": 85.0}
    v = check_tier_thresholds(prices, segment="premium")
    s = auto_fix_threshold_suggestions(prices, v, segment="premium")
    assert len(s) == 1
    # Premium requires 5%, so suggested value should be < 95
    assert s[0].new_value < 95.0


def test_check_all_policies_combined() -> None:
    """check_all_policies combines hierarchy and threshold checks."""
    # This has a hierarchy inversion (exchange > new) AND threshold issues
    prices = {"new": 100.0, "exchange": 101.0, "repair": 100.5, "usm": 100.0}
    violations, suggestions = check_all_policies(prices)
    # Should have hierarchy violations
    assert any(v.type == "hierarchy_inversion" for v in violations)
    # Should have threshold violations
    assert any(v.type == "insufficient_tier_margin" for v in violations)
    # Should have suggestions for both
    assert len(suggestions) > 0


def test_check_all_policies_clean() -> None:
    """Clean prices pass all checks."""
    prices = {"new": 100.0, "exchange": 90.0, "repair": 80.0, "usm": 70.0}
    violations, suggestions = check_all_policies(prices)
    assert violations == []
    assert suggestions == []

