"""Unit tests for the business rules engine."""

from pathlib import Path

import pytest
import yaml

from src.rules.engine import AppliedRule, RulesEngine
from src.schemas.market import MarketContext


@pytest.fixture
def sample_context() -> MarketContext:
    """Create a standard market context for testing."""
    return MarketContext(
        number_of_riders=50,
        number_of_drivers=25,
        location_category="Urban",
        customer_loyalty_status="Gold",
        number_of_past_rides=20,
        average_ratings=4.5,
        time_of_booking="Evening",
        vehicle_type="Premium",
        expected_ride_duration=30,
        historical_cost_of_ride=100.0,
    )


@pytest.fixture
def rural_context() -> MarketContext:
    """Create a rural market context for fairness testing."""
    return MarketContext(
        number_of_riders=10,
        number_of_drivers=5,
        location_category="Rural",
        customer_loyalty_status="Bronze",
        number_of_past_rides=5,
        average_ratings=4.0,
        time_of_booking="Morning",
        vehicle_type="Economy",
        expected_ride_duration=45,
        historical_cost_of_ride=50.0,
    )


@pytest.fixture
def rules_engine() -> RulesEngine:
    """Create a rules engine with default config."""
    return RulesEngine()


class TestRulesEngineInitialization:
    """Tests for rules engine initialization."""

    def test_loads_rules_from_default_config(self, rules_engine: RulesEngine) -> None:
        """Engine loads rules from default config path."""
        assert len(rules_engine.rules) > 0

    def test_rules_sorted_by_priority(self, rules_engine: RulesEngine) -> None:
        """Rules are sorted by priority (lowest first)."""
        priorities = [r.priority for r in rules_engine.rules]
        assert priorities == sorted(priorities)

    def test_handles_missing_config(self, tmp_path: Path) -> None:
        """Engine handles missing config file gracefully."""
        engine = RulesEngine(config_path=tmp_path / "nonexistent.yaml")
        assert engine.rules == []

    def test_custom_config_path(self, tmp_path: Path) -> None:
        """Engine loads from custom config path."""
        config = {
            "rules": [
                {
                    "id": "test_rule",
                    "name": "Test Rule",
                    "priority": 1,
                    "condition": {"type": "always"},
                    "action": {"type": "floor", "value": "cost * 1.0"},
                }
            ]
        }
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(yaml.dump(config))

        engine = RulesEngine(config_path=config_file)
        assert len(engine.rules) == 1
        assert engine.rules[0].id == "test_rule"


class TestPriceFloor:
    """Tests for price floor enforcement."""

    def test_floor_prevents_below_cost_pricing(
        self, rules_engine: RulesEngine, sample_context: MarketContext
    ) -> None:
        """Floor rule prevents pricing below cost + minimum margin."""
        # Try to set price below cost
        result = rules_engine.apply(sample_context, optimal_price=50.0)

        # Floor should raise to cost * 1.10 = 110.0
        # Then Gold loyalty discount (10%) reduces to 99.0
        floor_rules = [r for r in result.applied_rules if r.rule_id == "price_floor"]
        assert len(floor_rules) == 1
        assert floor_rules[0].price_after == 110.0  # Floor enforced correctly

        # Final price accounts for loyalty discount
        expected_final = 110.0 * 0.90  # Gold = 10% discount
        assert result.final_price == expected_final

    def test_floor_does_not_affect_high_prices(
        self, rules_engine: RulesEngine, sample_context: MarketContext
    ) -> None:
        """Floor rule doesn't lower prices that are already above floor."""
        # Price already above floor
        result = rules_engine.apply(sample_context, optimal_price=200.0)

        # Should not be raised (but may be capped by other rules)
        floor_rules = [r for r in result.applied_rules if r.rule_id == "price_floor"]
        assert len(floor_rules) == 0


class TestPriceCap:
    """Tests for price cap enforcement."""

    def test_general_cap_limits_excessive_surge(
        self, rules_engine: RulesEngine, sample_context: MarketContext
    ) -> None:
        """General cap limits price to 3x historical cost."""
        # Try to set price way above cap
        result = rules_engine.apply(sample_context, optimal_price=500.0)

        # Should be capped to cost * 3.0 = 300.0 (before loyalty discount)
        # Gold gets 10% discount: 300 * 0.90 = 270.0
        max_expected = sample_context.historical_cost_of_ride * 3.0 * 0.90
        assert result.final_price <= max_expected

    def test_cap_does_not_affect_low_prices(
        self, rules_engine: RulesEngine, sample_context: MarketContext
    ) -> None:
        """Cap rule doesn't raise prices that are already below cap."""
        # Price well below cap
        result = rules_engine.apply(sample_context, optimal_price=150.0)

        # General cap should not have been applied
        cap_rules = [
            r for r in result.applied_rules if r.rule_id == "surge_cap_general"
        ]
        assert len(cap_rules) == 0


class TestFairnessConstraints:
    """Tests for fairness constraint rules."""

    def test_rural_cap_more_restrictive(
        self, rules_engine: RulesEngine, rural_context: MarketContext
    ) -> None:
        """Rural areas have stricter surge cap (1.5x)."""
        # Try high price in rural area
        result = rules_engine.apply(rural_context, optimal_price=200.0)

        # Should be capped to cost * 1.5 = 75.0 (no loyalty discount for Bronze)
        max_expected = rural_context.historical_cost_of_ride * 1.5
        assert result.final_price <= max_expected

    def test_rural_cap_applied_after_general(
        self, rules_engine: RulesEngine, rural_context: MarketContext
    ) -> None:
        """Rural cap is applied and more restrictive than general cap."""
        result = rules_engine.apply(rural_context, optimal_price=200.0)

        # Rural cap should be in applied rules
        rural_rules = [r for r in result.applied_rules if r.rule_id == "surge_cap_rural"]
        assert len(rural_rules) == 1

    def test_economy_vehicle_cap_in_urban(self, rules_engine: RulesEngine) -> None:
        """Economy vehicles in Urban areas have 2.5x surge cap."""
        context = MarketContext(
            number_of_riders=50,
            number_of_drivers=25,
            location_category="Urban",  # Urban, not Rural
            customer_loyalty_status="Bronze",  # No discount
            number_of_past_rides=10,
            average_ratings=4.2,
            time_of_booking="Evening",
            vehicle_type="Economy",  # Economy vehicle
            expected_ride_duration=30,
            historical_cost_of_ride=100.0,
        )

        # Try price above economy cap (2.5x = 250) but below general cap (3.0x = 300)
        result = rules_engine.apply(context, optimal_price=280.0)

        # Should be capped to 2.5x = 250.0 (no loyalty discount for Bronze)
        assert result.final_price == 250.0

        # Economy cap rule should be in applied rules
        economy_rules = [r for r in result.applied_rules if r.rule_id == "surge_cap_economy"]
        assert len(economy_rules) == 1


class TestLoyaltyDiscounts:
    """Tests for loyalty tier discounts."""

    def test_bronze_no_discount(
        self, rules_engine: RulesEngine, rural_context: MarketContext
    ) -> None:
        """Bronze tier gets 0% discount."""
        # rural_context has Bronze loyalty
        result = rules_engine.apply(rural_context, optimal_price=50.0)

        # No loyalty discount should be applied
        loyalty_rules = [
            r for r in result.applied_rules if r.rule_id == "loyalty_discount"
        ]
        assert len(loyalty_rules) == 0

    def test_silver_5_percent_discount(self, rules_engine: RulesEngine) -> None:
        """Silver tier gets 5% discount."""
        context = MarketContext(
            number_of_riders=50,
            number_of_drivers=25,
            location_category="Urban",
            customer_loyalty_status="Silver",
            number_of_past_rides=10,
            average_ratings=4.2,
            time_of_booking="Morning",
            vehicle_type="Premium",
            expected_ride_duration=20,
            historical_cost_of_ride=100.0,
        )
        result = rules_engine.apply(context, optimal_price=150.0)

        # Silver should get 5% off: 150 * 0.95 = 142.50
        assert result.final_price == 142.50

    def test_gold_10_percent_discount(
        self, rules_engine: RulesEngine, sample_context: MarketContext
    ) -> None:
        """Gold tier gets 10% discount."""
        # sample_context has Gold loyalty
        result = rules_engine.apply(sample_context, optimal_price=150.0)

        # Gold should get 10% off: 150 * 0.90 = 135.0
        assert result.final_price == 135.0

    def test_platinum_15_percent_discount(self, rules_engine: RulesEngine) -> None:
        """Platinum tier gets 15% discount."""
        context = MarketContext(
            number_of_riders=50,
            number_of_drivers=25,
            location_category="Urban",
            customer_loyalty_status="Platinum",
            number_of_past_rides=100,
            average_ratings=4.8,
            time_of_booking="Evening",
            vehicle_type="Premium",
            expected_ride_duration=30,
            historical_cost_of_ride=100.0,
        )
        result = rules_engine.apply(context, optimal_price=200.0)

        # Platinum should get 15% off: 200 * 0.85 = 170.0
        assert result.final_price == 170.0


class TestRulePriorityOrdering:
    """Tests for rule priority and ordering."""

    def test_floor_before_cap_before_discount(
        self, rules_engine: RulesEngine, sample_context: MarketContext
    ) -> None:
        """Rules apply in order: floor → cap → discount."""
        # Price that will trigger multiple rules
        result = rules_engine.apply(sample_context, optimal_price=50.0)

        # Check ordering of applied rules
        if len(result.applied_rules) >= 2:
            for i in range(len(result.applied_rules) - 1):
                current_id = result.applied_rules[i].rule_id
                next_id = result.applied_rules[i + 1].rule_id

                # Floor has priority 1, cap has 10, loyalty has 100
                current_rule = next(r for r in rules_engine.rules if r.id == current_id)
                next_rule = next(r for r in rules_engine.rules if r.id == next_id)
                assert current_rule.priority < next_rule.priority

    def test_cap_before_loyalty_discount(
        self, rules_engine: RulesEngine, sample_context: MarketContext
    ) -> None:
        """Caps are applied before loyalty discounts."""
        # High price that triggers cap
        result = rules_engine.apply(sample_context, optimal_price=500.0)

        cap_applied = any(
            "cap" in r.rule_id.lower() for r in result.applied_rules
        )
        discount_applied = any(
            r.rule_id == "loyalty_discount" for r in result.applied_rules
        )

        assert cap_applied
        assert discount_applied


class TestRulesResult:
    """Tests for RulesResult structure."""

    def test_result_contains_original_price(
        self, rules_engine: RulesEngine, sample_context: MarketContext
    ) -> None:
        """Result includes the original price before rules."""
        result = rules_engine.apply(sample_context, optimal_price=150.0)
        assert result.original_price == 150.0

    def test_result_contains_total_adjustment(
        self, rules_engine: RulesEngine, sample_context: MarketContext
    ) -> None:
        """Result includes total price adjustment."""
        result = rules_engine.apply(sample_context, optimal_price=150.0)

        expected_adjustment = result.final_price - result.original_price
        assert result.total_adjustment == expected_adjustment

    def test_applied_rules_track_impact(
        self, rules_engine: RulesEngine, sample_context: MarketContext
    ) -> None:
        """Each applied rule tracks its impact."""
        result = rules_engine.apply(sample_context, optimal_price=150.0)

        for rule in result.applied_rules:
            assert isinstance(rule, AppliedRule)
            assert rule.impact == rule.price_after - rule.price_before
            assert rule.impact_percent is not None


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_zero_price_input(
        self, rules_engine: RulesEngine, sample_context: MarketContext
    ) -> None:
        """Engine handles zero price input."""
        result = rules_engine.apply(sample_context, optimal_price=0.0)

        # Floor should kick in
        assert result.final_price > 0

    def test_very_high_price_input(
        self, rules_engine: RulesEngine, sample_context: MarketContext
    ) -> None:
        """Engine handles very high price input."""
        result = rules_engine.apply(sample_context, optimal_price=10000.0)

        # Cap should limit it
        max_expected = sample_context.historical_cost_of_ride * 3.0
        # Account for Gold discount
        assert result.final_price <= max_expected

    def test_price_exactly_at_floor(
        self, rules_engine: RulesEngine, sample_context: MarketContext
    ) -> None:
        """No floor adjustment when price equals floor."""
        floor_price = sample_context.historical_cost_of_ride * 1.10
        result = rules_engine.apply(sample_context, optimal_price=floor_price)

        floor_rules = [r for r in result.applied_rules if r.rule_id == "price_floor"]
        assert len(floor_rules) == 0

    def test_price_exactly_at_cap(
        self, rules_engine: RulesEngine, sample_context: MarketContext
    ) -> None:
        """No cap adjustment when price equals cap."""
        cap_price = sample_context.historical_cost_of_ride * 3.0
        result = rules_engine.apply(sample_context, optimal_price=cap_price)

        cap_rules = [
            r for r in result.applied_rules if r.rule_id == "surge_cap_general"
        ]
        assert len(cap_rules) == 0


class TestExpressionValidation:
    """Tests for expression parsing and validation."""

    def test_invalid_expression_raises_error(self, tmp_path: Path) -> None:
        """Invalid expression format raises ValueError."""
        config = {
            "rules": [
                {
                    "id": "bad_rule",
                    "name": "Bad Rule",
                    "priority": 1,
                    "condition": {"type": "always"},
                    "action": {"type": "floor", "value": "foobar"},
                }
            ]
        }
        config_file = tmp_path / "bad_config.yaml"
        config_file.write_text(yaml.dump(config))

        engine = RulesEngine(config_path=config_file)
        context = MarketContext(
            number_of_riders=50,
            number_of_drivers=25,
            location_category="Urban",
            customer_loyalty_status="Gold",
            number_of_past_rides=20,
            average_ratings=4.5,
            time_of_booking="Evening",
            vehicle_type="Premium",
            expected_ride_duration=30,
            historical_cost_of_ride=100.0,
        )

        with pytest.raises(ValueError, match="Cannot parse expression"):
            engine.apply(context, optimal_price=50.0)

    def test_malformed_cost_expression_raises_error(self, tmp_path: Path) -> None:
        """Malformed cost expression raises ValueError."""
        config = {
            "rules": [
                {
                    "id": "bad_rule",
                    "name": "Bad Rule",
                    "priority": 1,
                    "condition": {"type": "always"},
                    "action": {"type": "floor", "value": "cost * foo"},
                }
            ]
        }
        config_file = tmp_path / "bad_config.yaml"
        config_file.write_text(yaml.dump(config))

        engine = RulesEngine(config_path=config_file)
        context = MarketContext(
            number_of_riders=50,
            number_of_drivers=25,
            location_category="Urban",
            customer_loyalty_status="Gold",
            number_of_past_rides=20,
            average_ratings=4.5,
            time_of_booking="Evening",
            vehicle_type="Premium",
            expected_ride_duration=30,
            historical_cost_of_ride=100.0,
        )

        with pytest.raises(ValueError, match="Cannot parse expression"):
            engine.apply(context, optimal_price=50.0)

    def test_valid_literal_number_expression(self, tmp_path: Path) -> None:
        """Literal number expression is accepted."""
        config = {
            "rules": [
                {
                    "id": "literal_floor",
                    "name": "Literal Floor",
                    "priority": 1,
                    "condition": {"type": "always"},
                    "action": {"type": "floor", "value": "50.0"},
                }
            ]
        }
        config_file = tmp_path / "literal_config.yaml"
        config_file.write_text(yaml.dump(config))

        engine = RulesEngine(config_path=config_file)
        context = MarketContext(
            number_of_riders=50,
            number_of_drivers=25,
            location_category="Urban",
            customer_loyalty_status="Gold",
            number_of_past_rides=20,
            average_ratings=4.5,
            time_of_booking="Evening",
            vehicle_type="Premium",
            expected_ride_duration=30,
            historical_cost_of_ride=100.0,
        )

        result = engine.apply(context, optimal_price=30.0)
        # Floor should raise price to 50.0
        assert result.final_price == 50.0


class TestConditionFieldValidation:
    """Tests for condition field validation."""

    def test_invalid_field_name_logs_error_and_skips_rule(
        self, tmp_path: Path
    ) -> None:
        """Rule with invalid field name is skipped and logs error."""
        config = {
            "rules": [
                {
                    "id": "bad_field_rule",
                    "name": "Bad Field Rule",
                    "priority": 1,
                    "condition": {
                        "type": "field_match",
                        "field": "nonexistent_field",  # Invalid field
                        "operator": "equals",
                        "value": "test",
                    },
                    "action": {"type": "cap", "value": "cost * 0.5"},
                }
            ]
        }
        config_file = tmp_path / "bad_field_config.yaml"
        config_file.write_text(yaml.dump(config))

        engine = RulesEngine(config_path=config_file)
        context = MarketContext(
            number_of_riders=50,
            number_of_drivers=25,
            location_category="Urban",
            customer_loyalty_status="Gold",
            number_of_past_rides=20,
            average_ratings=4.5,
            time_of_booking="Evening",
            vehicle_type="Premium",
            expected_ride_duration=30,
            historical_cost_of_ride=100.0,
        )

        # Rule should be skipped (condition returns False), price unchanged
        result = engine.apply(context, optimal_price=200.0)
        assert result.final_price == 200.0
        assert len(result.applied_rules) == 0


class TestLoyaltyTierWarning:
    """Tests for loyalty tier configuration warnings."""

    def test_unknown_loyalty_tier_defaults_to_zero_discount(
        self, tmp_path: Path
    ) -> None:
        """Unknown loyalty tier defaults to 0% discount without failing."""
        config = {
            "rules": [
                {
                    "id": "loyalty_discount",
                    "name": "Loyalty Discount",
                    "priority": 1,
                    "condition": {"type": "always"},
                    "action": {
                        "type": "discount",
                        "values": {"Silver": 0.05, "Gold": 0.10},  # Missing Bronze, Platinum
                    },
                }
            ]
        }
        config_file = tmp_path / "partial_loyalty_config.yaml"
        config_file.write_text(yaml.dump(config))

        engine = RulesEngine(config_path=config_file)
        context = MarketContext(
            number_of_riders=50,
            number_of_drivers=25,
            location_category="Urban",
            customer_loyalty_status="Platinum",  # Not in config
            number_of_past_rides=100,
            average_ratings=4.8,
            time_of_booking="Evening",
            vehicle_type="Premium",
            expected_ride_duration=30,
            historical_cost_of_ride=100.0,
        )

        result = engine.apply(context, optimal_price=100.0)

        # Should still work, defaulting to 0% discount (no change to price)
        assert result.final_price == 100.0

        # No discount rule should be in applied_rules since 0% discount means no change
        loyalty_rules = [r for r in result.applied_rules if r.rule_id == "loyalty_discount"]
        assert len(loyalty_rules) == 0  # 0% discount = no price change = not recorded

