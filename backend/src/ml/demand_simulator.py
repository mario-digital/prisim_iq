"""Behavioral demand simulator for ML training data generation.

Implements a log-linear demand model with behavioral economics principles:
- Price elasticity varies by segment (Premium less elastic than Economy)
- Reference pricing effects (anchoring to historical cost)
- Modifiers for time of day, loyalty tier, and supply/demand ratio
- External factors: weather, events, fuel prices (from n8n)
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from loguru import logger

if TYPE_CHECKING:
    from src.schemas.external import ExternalContext
    from src.schemas.market import MarketContext

# Default config path
_CONFIG_PATH = Path(__file__).parent / "config" / "elasticity.yaml"


class DemandSimulator:
    """Simulator for realistic price-demand relationships.

    Uses a log-linear demand model with segment-specific elasticity
    and behavioral modifiers (time, loyalty, supply/demand).
    """

    def __init__(self, config_path: Path | str | None = None) -> None:
        """Initialize the demand simulator.

        Args:
            config_path: Path to elasticity config YAML. Uses default if None.
        """
        self._config_path = Path(config_path) if config_path else _CONFIG_PATH
        self._config = self._load_config()
        logger.info(f"DemandSimulator initialized with config: {self._config_path}")

    def _load_config(self) -> dict:
        """Load elasticity configuration from YAML file.

        Returns:
            Configuration dictionary with elasticity and modifier parameters.

        Raises:
            FileNotFoundError: If config file doesn't exist.
            yaml.YAMLError: If config file is invalid YAML.
        """
        if not self._config_path.exists():
            logger.warning(f"Config file not found at {self._config_path}, using defaults")
            return self._get_default_config()

        with open(self._config_path) as f:
            config = yaml.safe_load(f)
            logger.debug(f"Loaded config: {config}")
            self._validate_config(config)
            return config

    def _validate_config(self, config: dict) -> None:
        """Validate configuration values and warn about potential issues.

        Args:
            config: Configuration dictionary to validate.

        Raises:
            ValueError: If elasticity values are positive (invalid).
        """
        # Valid keys for validation
        valid_locations = {"Urban", "Suburban", "Rural"}
        valid_periods = {"Peak", "Standard"}
        valid_vehicles = {"Premium", "Economy"}
        valid_times = {"Morning", "Afternoon", "Evening", "Night"}
        valid_loyalty = {"Bronze", "Silver", "Gold", "Platinum"}

        # Validate elasticity values and keys
        elasticity = config.get("elasticity", {})
        for key, value in elasticity.items():
            # Check elasticity is negative (law of demand)
            if value >= 0:
                raise ValueError(
                    f"Elasticity value for '{key}' must be negative (got {value}). "
                    "Positive elasticity violates the law of demand."
                )

            # Validate key format: {Location}_{Period}_{Vehicle}
            parts = key.split("_")
            if len(parts) != 3:
                logger.warning(
                    f"Elasticity key '{key}' does not match expected format "
                    "'{{Location}}_{{Period}}_{{Vehicle}}'"
                )
                continue

            location, period, vehicle = parts
            if location not in valid_locations:
                logger.warning(
                    f"Unknown location '{location}' in elasticity key '{key}'. "
                    f"Expected one of: {valid_locations}"
                )
            if period not in valid_periods:
                logger.warning(
                    f"Unknown period '{period}' in elasticity key '{key}'. "
                    f"Expected one of: {valid_periods}"
                )
            if vehicle not in valid_vehicles:
                logger.warning(
                    f"Unknown vehicle type '{vehicle}' in elasticity key '{key}'. "
                    f"Expected one of: {valid_vehicles}"
                )

        # Validate modifier keys
        modifiers = config.get("modifiers", {})

        time_mods = modifiers.get("time", {})
        for time_key in time_mods:
            if time_key not in valid_times:
                logger.warning(
                    f"Unknown time modifier key '{time_key}'. Expected one of: {valid_times}"
                )

        loyalty_mods = modifiers.get("loyalty", {})
        for loyalty_key in loyalty_mods:
            if loyalty_key not in valid_loyalty:
                logger.warning(
                    f"Unknown loyalty modifier key '{loyalty_key}'. "
                    f"Expected one of: {valid_loyalty}"
                )

    def _get_default_config(self) -> dict:
        """Return default elasticity configuration.

        Returns:
            Default configuration dictionary.
        """
        return {
            "elasticity": {
                "Urban_Peak_Premium": -0.7,
                "Urban_Peak_Economy": -1.0,
                "Urban_Standard_Premium": -0.8,
                "Urban_Standard_Economy": -1.2,
                "Suburban_Peak_Premium": -0.9,
                "Suburban_Peak_Economy": -1.1,
                "Suburban_Standard_Premium": -1.0,
                "Suburban_Standard_Economy": -1.3,
                "Rural_Peak_Premium": -1.0,
                "Rural_Peak_Economy": -1.2,
                "Rural_Standard_Premium": -1.1,
                "Rural_Standard_Economy": -1.5,
            },
            "modifiers": {
                "time": {
                    "Morning": 0.9,
                    "Afternoon": 0.85,
                    "Evening": 1.1,
                    "Night": 0.7,
                },
                "loyalty": {
                    "Bronze": 1.0,
                    "Silver": 1.05,
                    "Gold": 1.1,
                    "Platinum": 1.15,
                },
            },
            "reference_price_sensitivity": 0.3,
            "base_demand": 0.5,
        }

    def _get_elasticity_key(self, context: MarketContext) -> str:
        """Build elasticity lookup key from context.

        Args:
            context: Market context with location, time, and vehicle type.

        Returns:
            Key string like 'Urban_Peak_Premium'.
        """
        # Determine if peak time (Evening is peak, Morning is secondary peak)
        peak_times = {"Evening", "Morning"}
        period = "Peak" if context.time_of_booking in peak_times else "Standard"

        return f"{context.location_category}_{period}_{context.vehicle_type}"

    def _get_elasticity(
        self, context: MarketContext, elasticity_params: dict | None = None
    ) -> float:
        """Get elasticity value for the given context.

        Args:
            context: Market context for elasticity lookup.
            elasticity_params: Override parameters (optional).

        Returns:
            Elasticity coefficient (negative value).
        """
        # Allow direct elasticity override
        if elasticity_params and "elasticity" in elasticity_params:
            return float(elasticity_params["elasticity"])

        key = self._get_elasticity_key(context)
        elasticity_map = self._config.get("elasticity", {})

        # Fallback to a default if key not found
        default_elasticity = -1.0
        elasticity = elasticity_map.get(key, default_elasticity)

        logger.debug(f"Elasticity for {key}: {elasticity}")
        return elasticity

    def _calculate_supply_demand_modifier(self, context: MarketContext) -> float:
        """Calculate demand modifier based on supply/demand ratio.

        High supply (many drivers) -> higher demand modifier
        Low supply (few drivers) -> lower demand modifier

        Args:
            context: Market context with driver/rider counts.

        Returns:
            Modifier in range [0.5, 1.5].
        """
        ratio = context.supply_demand_ratio

        # Sigmoid-like transformation centered at ratio=1.0
        # ratio > 1 (more drivers than riders) -> modifier > 1
        # ratio < 1 (more riders than drivers) -> modifier < 1
        modifier = 0.5 + (1.0 / (1.0 + math.exp(-2 * (ratio - 1.0))))

        return max(0.5, min(1.5, modifier))

    def _calculate_time_modifier(self, time_of_booking: str) -> float:
        """Get time-of-day demand modifier.

        Args:
            time_of_booking: Time period (Morning/Afternoon/Evening/Night).

        Returns:
            Time modifier value.
        """
        time_modifiers = self._config.get("modifiers", {}).get("time", {})
        return time_modifiers.get(time_of_booking, 1.0)

    def _calculate_loyalty_modifier(self, loyalty_status: str) -> float:
        """Get loyalty tier demand modifier.

        Higher loyalty -> higher demand (more loyal = more likely to purchase).

        Args:
            loyalty_status: Customer loyalty tier.

        Returns:
            Loyalty modifier value.
        """
        loyalty_modifiers = self._config.get("modifiers", {}).get("loyalty", {})
        return loyalty_modifiers.get(loyalty_status, 1.0)

    def _calculate_segment_modifier(self, context: MarketContext) -> float:
        """Calculate segment-based demand modifier.

        Urban locations have higher base demand than rural.

        Args:
            context: Market context with location category.

        Returns:
            Segment modifier in range [0.7, 1.1].
        """
        segment_modifiers = {
            "Urban": 1.1,
            "Suburban": 0.95,
            "Rural": 0.8,
        }
        return segment_modifiers.get(context.location_category, 1.0)

    def _calculate_base_demand(self, context: MarketContext) -> float:
        """Calculate base demand from all modifiers.

        Args:
            context: Market context for modifier calculations.

        Returns:
            Base demand value (unbounded).
        """
        base = self._config.get("base_demand", 0.5)

        # Apply all modifiers
        supply_demand_mod = self._calculate_supply_demand_modifier(context)
        time_mod = self._calculate_time_modifier(context.time_of_booking)
        segment_mod = self._calculate_segment_modifier(context)
        loyalty_mod = self._calculate_loyalty_modifier(context.customer_loyalty_status)

        base_demand = base * supply_demand_mod * time_mod * segment_mod * loyalty_mod

        logger.debug(
            f"Base demand calculation: {base} * {supply_demand_mod:.3f} * "
            f"{time_mod:.3f} * {segment_mod:.3f} * {loyalty_mod:.3f} = {base_demand:.3f}"
        )

        return base_demand

    def _calculate_reference_price_effect(self, price: float, reference_price: float) -> float:
        """Calculate anchoring effect from price deviation.

        Larger deviations from reference price have greater demand impact.

        Args:
            price: Proposed price point.
            reference_price: Historical/reference price (anchor).

        Returns:
            Reference price effect multiplier.
        """
        if reference_price <= 0:
            return 1.0

        sensitivity = self._config.get("reference_price_sensitivity", 0.3)
        deviation = (price - reference_price) / reference_price

        # Negative deviation (price below reference) -> positive effect
        # Positive deviation (price above reference) -> negative effect
        effect = math.exp(-sensitivity * deviation)

        logger.debug(f"Reference price effect: deviation={deviation:.3f}, effect={effect:.3f}")

        return effect

    def simulate_demand(
        self,
        context: MarketContext,
        price: float,
        elasticity_params: dict | None = None,
        external_factors: ExternalContext | dict | None = None,
    ) -> float:
        """Simulate demand probability for given context and price.

        Uses a log-linear demand model:
            demand = base_demand * exp(elasticity * log(price / reference_price))

        Args:
            context: Market context with all features.
            price: Proposed price point.
            elasticity_params: Override default elasticity (optional).
            external_factors: ExternalContext from n8n or dict for legacy support.

        Returns:
            Demand probability in [0.0, 1.0].
        """
        if price <= 0:
            logger.warning(f"Invalid price {price}, returning 0.0 demand")
            return 0.0

        # Get reference price from context
        reference_price = context.historical_cost_of_ride
        if reference_price <= 0:
            reference_price = price  # Use current price as reference

        # Calculate base demand with all modifiers
        base_demand = self._calculate_base_demand(context)

        # Get segment-specific elasticity
        elasticity = self._get_elasticity(context, elasticity_params)

        # Log-linear demand model
        price_ratio = price / reference_price
        price_effect = math.exp(elasticity * math.log(price_ratio)) if price_ratio > 0 else 1.0

        # Apply reference pricing (anchoring) effect
        reference_effect = self._calculate_reference_price_effect(price, reference_price)

        # Apply external factors if provided
        external_multiplier = self._calculate_external_multiplier(external_factors)

        # Combine all effects
        demand = base_demand * price_effect * reference_effect * external_multiplier

        # Bound to [0.0, 1.0]
        bounded_demand = max(0.0, min(1.0, demand))

        logger.debug(
            f"Demand simulation: base={base_demand:.3f}, price_effect={price_effect:.3f}, "
            f"ref_effect={reference_effect:.3f}, external={external_multiplier:.3f}, "
            f"raw={demand:.3f}, bounded={bounded_demand:.3f}"
        )

        return bounded_demand

    def _calculate_external_multiplier(
        self, external_factors: ExternalContext | dict | None
    ) -> float:
        """Calculate demand multiplier from external factors.

        Supports both ExternalContext model (preferred) and legacy dict format.

        Args:
            external_factors: External factors from n8n or legacy dict.

        Returns:
            Combined multiplier from weather and events.
        """
        if external_factors is None:
            return 1.0

        external_multiplier = 1.0

        # Handle ExternalContext model (preferred)
        if hasattr(external_factors, "weather") and hasattr(external_factors, "events"):
            # ExternalContext model
            if external_factors.weather:
                external_multiplier *= external_factors.weather.demand_modifier
                logger.debug(
                    f"Weather modifier ({external_factors.weather.condition}): "
                    f"{external_factors.weather.demand_modifier:.3f}"
                )

            for event in external_factors.events:
                external_multiplier *= event.surge_modifier
                logger.debug(f"Event modifier ({event.name}): {event.surge_modifier:.3f}")
        else:
            # Legacy dict format for backwards compatibility
            weather_effects = {
                "sunny": 0.9,
                "cloudy": 1.0,
                "rainy": 1.2,
                "stormy": 1.3,
            }
            weather = external_factors.get("weather", "").lower()
            external_multiplier *= weather_effects.get(weather, 1.0)

            if external_factors.get("event_nearby", False):
                external_multiplier *= 1.15

        if external_multiplier != 1.0:
            logger.debug(f"External factors multiplier: {external_multiplier:.3f}")

        return external_multiplier


# Module-level convenience function
_default_simulator: DemandSimulator | None = None


def simulate_demand(
    context: MarketContext,
    price: float,
    elasticity_params: dict | None = None,
    external_factors: ExternalContext | dict | None = None,
) -> float:
    """Simulate demand probability for given context and price.

    Module-level convenience function using default simulator instance.

    Args:
        context: Market context with all features.
        price: Proposed price point.
        elasticity_params: Override default elasticity (optional).
        external_factors: ExternalContext from n8n or dict for legacy support.

    Returns:
        Demand probability in [0.0, 1.0].
    """
    global _default_simulator
    if _default_simulator is None:
        _default_simulator = DemandSimulator()

    return _default_simulator.simulate_demand(context, price, elasticity_params, external_factors)
