"""Unit tests for demand simulator module."""


import pytest

from src.ml.demand_simulator import DemandSimulator, simulate_demand
from src.schemas.market import MarketContext


@pytest.fixture
def base_context() -> MarketContext:
    """Create a base market context for testing."""
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
        historical_cost_of_ride=35.0,
    )


@pytest.fixture
def economy_context() -> MarketContext:
    """Create an economy segment context for testing."""
    return MarketContext(
        number_of_riders=50,
        number_of_drivers=25,
        location_category="Urban",
        customer_loyalty_status="Bronze",
        number_of_past_rides=5,
        average_ratings=4.0,
        time_of_booking="Afternoon",
        vehicle_type="Economy",
        expected_ride_duration=20,
        historical_cost_of_ride=20.0,
    )


@pytest.fixture
def simulator() -> DemandSimulator:
    """Create a demand simulator instance."""
    return DemandSimulator()


class TestDemandSimulator:
    """Tests for DemandSimulator class."""

    def test_simulator_initialization(self, simulator: DemandSimulator) -> None:
        """Test that simulator initializes with config."""
        assert simulator._config is not None
        assert "elasticity" in simulator._config
        assert "modifiers" in simulator._config

    def test_demand_decreases_with_price_increase(
        self, simulator: DemandSimulator, base_context: MarketContext
    ) -> None:
        """Test that demand decreases as price increases (negative elasticity)."""
        reference_price = base_context.historical_cost_of_ride

        # Test at multiple price points
        prices = [
            reference_price * 0.8,   # 20% below reference
            reference_price,          # At reference
            reference_price * 1.2,   # 20% above reference
            reference_price * 1.5,   # 50% above reference
        ]

        demands = [simulator.simulate_demand(base_context, p) for p in prices]

        # Verify demand is monotonically decreasing with price
        for i in range(len(demands) - 1):
            assert demands[i] > demands[i + 1], (
                f"Demand should decrease with price: "
                f"demand at {prices[i]:.2f} ({demands[i]:.4f}) should be > "
                f"demand at {prices[i+1]:.2f} ({demands[i+1]:.4f})"
            )

    def test_demand_bounded_zero_to_one(
        self, simulator: DemandSimulator, base_context: MarketContext
    ) -> None:
        """Test that demand values are bounded in [0.0, 1.0]."""
        # Test with very low price (should push demand up)
        very_low_price = base_context.historical_cost_of_ride * 0.1
        demand_low = simulator.simulate_demand(base_context, very_low_price)
        assert 0.0 <= demand_low <= 1.0, f"Demand {demand_low} out of bounds"

        # Test with very high price (should push demand down)
        very_high_price = base_context.historical_cost_of_ride * 10.0
        demand_high = simulator.simulate_demand(base_context, very_high_price)
        assert 0.0 <= demand_high <= 1.0, f"Demand {demand_high} out of bounds"

        # Test with reference price
        demand_ref = simulator.simulate_demand(
            base_context, base_context.historical_cost_of_ride
        )
        assert 0.0 <= demand_ref <= 1.0, f"Demand {demand_ref} out of bounds"

    def test_premium_less_elastic_than_economy(
        self,
        simulator: DemandSimulator,
        base_context: MarketContext,
        economy_context: MarketContext,
    ) -> None:
        """Test that Premium segment is less elastic than Economy."""
        # Calculate price increase percentage for both
        premium_base_price = base_context.historical_cost_of_ride
        economy_base_price = economy_context.historical_cost_of_ride

        # Increase price by 30%
        price_increase = 1.3

        # Premium demand at base and increased price
        premium_demand_base = simulator.simulate_demand(base_context, premium_base_price)
        premium_demand_high = simulator.simulate_demand(
            base_context, premium_base_price * price_increase
        )

        # Economy demand at base and increased price
        economy_demand_base = simulator.simulate_demand(economy_context, economy_base_price)
        economy_demand_high = simulator.simulate_demand(
            economy_context, economy_base_price * price_increase
        )

        # Calculate percentage drops
        premium_drop = (premium_demand_base - premium_demand_high) / premium_demand_base
        economy_drop = (economy_demand_base - economy_demand_high) / economy_demand_base

        # Economy should drop more (more elastic)
        assert economy_drop > premium_drop, (
            f"Economy should be more elastic (drop more): "
            f"economy_drop={economy_drop:.4f}, premium_drop={premium_drop:.4f}"
        )

    def test_reference_pricing_effect(
        self, simulator: DemandSimulator, base_context: MarketContext
    ) -> None:
        """Test that reference pricing (anchoring) affects demand."""
        reference_price = base_context.historical_cost_of_ride

        # Price below reference should have positive anchoring effect
        below_ref = simulator.simulate_demand(base_context, reference_price * 0.9)

        # Price at reference
        at_ref = simulator.simulate_demand(base_context, reference_price)

        # Price above reference should have negative anchoring effect
        above_ref = simulator.simulate_demand(base_context, reference_price * 1.1)

        # Verify ordering: below > at > above (including both elasticity and anchoring)
        assert below_ref > at_ref > above_ref, (
            f"Reference pricing not working: below={below_ref:.4f}, "
            f"at={at_ref:.4f}, above={above_ref:.4f}"
        )

    def test_invalid_price_returns_zero(
        self, simulator: DemandSimulator, base_context: MarketContext
    ) -> None:
        """Test that zero or negative prices return zero demand."""
        assert simulator.simulate_demand(base_context, 0.0) == 0.0
        assert simulator.simulate_demand(base_context, -10.0) == 0.0

    def test_time_of_day_modifier(
        self, simulator: DemandSimulator, base_context: MarketContext
    ) -> None:
        """Test that time of day affects demand."""
        price = base_context.historical_cost_of_ride

        # Create contexts for different times
        evening_context = base_context.model_copy(update={"time_of_booking": "Evening"})
        night_context = base_context.model_copy(update={"time_of_booking": "Night"})

        evening_demand = simulator.simulate_demand(evening_context, price)
        night_demand = simulator.simulate_demand(night_context, price)

        # Evening (peak) should have higher demand than Night
        assert evening_demand > night_demand, (
            f"Evening demand ({evening_demand:.4f}) should be > "
            f"Night demand ({night_demand:.4f})"
        )

    def test_loyalty_modifier(
        self, simulator: DemandSimulator, base_context: MarketContext
    ) -> None:
        """Test that loyalty tier affects demand."""
        price = base_context.historical_cost_of_ride

        # Create contexts for different loyalty tiers
        bronze_context = base_context.model_copy(
            update={"customer_loyalty_status": "Bronze"}
        )
        platinum_context = base_context.model_copy(
            update={"customer_loyalty_status": "Platinum"}
        )

        bronze_demand = simulator.simulate_demand(bronze_context, price)
        platinum_demand = simulator.simulate_demand(platinum_context, price)

        # Platinum should have higher demand than Bronze
        assert platinum_demand > bronze_demand, (
            f"Platinum demand ({platinum_demand:.4f}) should be > "
            f"Bronze demand ({bronze_demand:.4f})"
        )

    def test_supply_demand_ratio_modifier(self, simulator: DemandSimulator) -> None:
        """Test that supply/demand ratio affects demand."""
        base = MarketContext(
            number_of_riders=50,
            number_of_drivers=50,
            location_category="Urban",
            customer_loyalty_status="Gold",
            number_of_past_rides=20,
            average_ratings=4.5,
            time_of_booking="Evening",
            vehicle_type="Premium",
            expected_ride_duration=30,
            historical_cost_of_ride=35.0,
        )
        price = base.historical_cost_of_ride

        # High supply (more drivers than riders)
        high_supply = base.model_copy(
            update={"number_of_riders": 20, "number_of_drivers": 60}
        )

        # Low supply (more riders than drivers)
        low_supply = base.model_copy(
            update={"number_of_riders": 60, "number_of_drivers": 20}
        )

        high_supply_demand = simulator.simulate_demand(high_supply, price)
        low_supply_demand = simulator.simulate_demand(low_supply, price)

        # High supply should have higher demand (easier to get a ride)
        assert high_supply_demand > low_supply_demand, (
            f"High supply demand ({high_supply_demand:.4f}) should be > "
            f"Low supply demand ({low_supply_demand:.4f})"
        )

    def test_external_factors_weather(
        self, simulator: DemandSimulator, base_context: MarketContext
    ) -> None:
        """Test that external weather factors affect demand."""
        price = base_context.historical_cost_of_ride

        sunny_demand = simulator.simulate_demand(
            base_context, price, external_factors={"weather": "sunny"}
        )
        rainy_demand = simulator.simulate_demand(
            base_context, price, external_factors={"weather": "rainy"}
        )

        # Rainy weather should increase demand
        assert rainy_demand > sunny_demand, (
            f"Rainy demand ({rainy_demand:.4f}) should be > "
            f"Sunny demand ({sunny_demand:.4f})"
        )

    def test_external_factors_event(
        self, simulator: DemandSimulator, base_context: MarketContext
    ) -> None:
        """Test that nearby events increase demand."""
        price = base_context.historical_cost_of_ride

        no_event = simulator.simulate_demand(base_context, price)
        with_event = simulator.simulate_demand(
            base_context, price, external_factors={"event_nearby": True}
        )

        # Event should increase demand
        assert with_event > no_event, (
            f"Event demand ({with_event:.4f}) should be > "
            f"No event demand ({no_event:.4f})"
        )

    def test_elasticity_override(
        self, simulator: DemandSimulator, base_context: MarketContext
    ) -> None:
        """Test that elasticity can be overridden via params."""
        price = base_context.historical_cost_of_ride * 1.2  # 20% above reference

        # Default elasticity
        default_demand = simulator.simulate_demand(base_context, price)

        # Very inelastic (close to 0)
        inelastic_demand = simulator.simulate_demand(
            base_context, price, elasticity_params={"elasticity": -0.1}
        )

        # Very elastic (large negative)
        elastic_demand = simulator.simulate_demand(
            base_context, price, elasticity_params={"elasticity": -2.0}
        )

        # With price above reference:
        # - Inelastic should have higher demand (less sensitive to price)
        # - Elastic should have lower demand (more sensitive to price)
        assert inelastic_demand > default_demand > elastic_demand, (
            f"Elasticity override not working: "
            f"inelastic={inelastic_demand:.4f}, default={default_demand:.4f}, "
            f"elastic={elastic_demand:.4f}"
        )


class TestModuleLevelFunction:
    """Tests for module-level simulate_demand function."""

    def test_simulate_demand_function(self, base_context: MarketContext) -> None:
        """Test the module-level convenience function."""
        demand = simulate_demand(base_context, base_context.historical_cost_of_ride)
        assert 0.0 <= demand <= 1.0

    def test_simulate_demand_with_params(self, base_context: MarketContext) -> None:
        """Test module function with optional parameters."""
        demand = simulate_demand(
            base_context,
            base_context.historical_cost_of_ride,
            elasticity_params={"elasticity": -0.5},
            external_factors={"weather": "sunny"},
        )
        assert 0.0 <= demand <= 1.0


class TestElasticityKeys:
    """Tests for elasticity key generation."""

    def test_elasticity_key_peak_times(self, simulator: DemandSimulator) -> None:
        """Test that Evening and Morning are treated as peak times."""
        base = MarketContext(
            number_of_riders=50,
            number_of_drivers=25,
            location_category="Urban",
            customer_loyalty_status="Gold",
            number_of_past_rides=20,
            average_ratings=4.5,
            time_of_booking="Evening",
            vehicle_type="Premium",
            expected_ride_duration=30,
            historical_cost_of_ride=35.0,
        )

        evening_key = simulator._get_elasticity_key(base)
        assert "Peak" in evening_key

        morning_context = base.model_copy(update={"time_of_booking": "Morning"})
        morning_key = simulator._get_elasticity_key(morning_context)
        assert "Peak" in morning_key

    def test_elasticity_key_standard_times(self, simulator: DemandSimulator) -> None:
        """Test that Afternoon and Night are treated as standard times."""
        base = MarketContext(
            number_of_riders=50,
            number_of_drivers=25,
            location_category="Urban",
            customer_loyalty_status="Gold",
            number_of_past_rides=20,
            average_ratings=4.5,
            time_of_booking="Afternoon",
            vehicle_type="Economy",
            expected_ride_duration=30,
            historical_cost_of_ride=35.0,
        )

        afternoon_key = simulator._get_elasticity_key(base)
        assert "Standard" in afternoon_key

        night_context = base.model_copy(update={"time_of_booking": "Night"})
        night_key = simulator._get_elasticity_key(night_context)
        assert "Standard" in night_key

    def test_elasticity_key_format(self, simulator: DemandSimulator) -> None:
        """Test elasticity key format is correct."""
        context = MarketContext(
            number_of_riders=50,
            number_of_drivers=25,
            location_category="Suburban",
            customer_loyalty_status="Gold",
            number_of_past_rides=20,
            average_ratings=4.5,
            time_of_booking="Night",
            vehicle_type="Economy",
            expected_ride_duration=30,
            historical_cost_of_ride=35.0,
        )

        key = simulator._get_elasticity_key(context)
        assert key == "Suburban_Standard_Economy"

