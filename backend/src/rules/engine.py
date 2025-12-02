"""Rules engine for applying business rules to optimized prices."""

import re
from pathlib import Path
from typing import Any, Literal

import yaml
from loguru import logger
from pydantic import BaseModel, Field

from src.schemas.market import MarketContext

# Strict pattern for cost expressions: "cost * <positive_number>"
COST_EXPRESSION_PATTERN = re.compile(r"^cost\s*\*\s*(\d+(?:\.\d+)?)$")


class AppliedRule(BaseModel):
    """Record of a single rule application."""

    rule_id: str = Field(..., description="Unique rule identifier")
    rule_name: str = Field(..., description="Human-readable rule name")
    price_before: float = Field(..., description="Price before rule application")
    price_after: float = Field(..., description="Price after rule application")
    impact: float = Field(..., description="Absolute price change")
    impact_percent: float = Field(..., description="Percentage price change")


class RulesResult(BaseModel):
    """Result of applying all business rules."""

    original_price: float = Field(..., description="Price before any rules")
    final_price: float = Field(..., description="Price after all rules applied")
    applied_rules: list[AppliedRule] = Field(
        default_factory=list, description="List of rules that were applied"
    )
    total_adjustment: float = Field(..., description="Total price adjustment")
    total_adjustment_percent: float = Field(
        ..., description="Total adjustment as percentage"
    )


class RuleCondition(BaseModel):
    """Condition that determines when a rule applies."""

    type: Literal["always", "field_match"] = Field(
        default="always", description="Condition type"
    )
    field: str | None = Field(default=None, description="Field to check")
    operator: Literal["equals", "not_equals", "in", "not_in"] | None = Field(
        default=None, description="Comparison operator"
    )
    value: Any = Field(default=None, description="Value to compare against")


class RuleAction(BaseModel):
    """Action to take when rule condition is met."""

    type: Literal["floor", "cap", "discount"] = Field(
        ..., description="Type of price adjustment"
    )
    value: str | None = Field(
        default=None, description="Expression for floor/cap (e.g., 'cost * 1.10')"
    )
    values: dict[str, float] | None = Field(
        default=None, description="Lookup table for discount by tier"
    )


class Rule(BaseModel):
    """Business rule definition."""

    id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Human-readable rule name")
    priority: int = Field(..., description="Execution priority (lower = earlier)")
    condition: RuleCondition = Field(..., description="When to apply the rule")
    action: RuleAction = Field(..., description="What adjustment to make")


class RulesEngine:
    """Engine for applying business rules to optimized prices.

    Loads rules from a YAML configuration file and applies them in priority order.
    Rules can enforce price floors, caps, and loyalty discounts.
    """

    def __init__(self, config_path: str | Path | None = None) -> None:
        """Initialize rules engine with configuration.

        Args:
            config_path: Path to rules YAML config. Defaults to src/rules/config.yaml.
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        else:
            config_path = Path(config_path)

        self.config_path = config_path
        self.rules = self._load_rules()
        logger.info(f"Loaded {len(self.rules)} business rules from {config_path}")

    def _load_rules(self) -> list[Rule]:
        """Load and parse rules from YAML configuration."""
        if not self.config_path.exists():
            logger.warning(f"Rules config not found: {self.config_path}")
            return []

        with open(self.config_path) as f:
            config = yaml.safe_load(f)

        rules_data = config.get("rules", [])
        rules = [Rule(**rule_data) for rule_data in rules_data]

        # Sort by priority (lower number = higher priority = runs first)
        rules.sort(key=lambda r: r.priority)
        return rules

    # Valid fields that can be used in rule conditions
    VALID_CONTEXT_FIELDS = frozenset(MarketContext.model_fields.keys())

    def _evaluate_condition(
        self, condition: RuleCondition, context: MarketContext, rule_id: str = ""
    ) -> bool:
        """Check if a rule condition is satisfied.

        Args:
            condition: The condition to evaluate.
            context: Market context with field values.
            rule_id: Rule identifier for logging purposes.

        Returns:
            True if condition is met, False otherwise.
        """
        if condition.type == "always":
            return True

        if condition.type == "field_match" and condition.field:
            # Validate field exists on MarketContext
            if condition.field not in self.VALID_CONTEXT_FIELDS:
                logger.error(
                    f"Rule '{rule_id}': Invalid field '{condition.field}' in condition. "
                    f"Valid fields: {sorted(self.VALID_CONTEXT_FIELDS)}"
                )
                return False

            field_value = getattr(context, condition.field, None)
            if field_value is None:
                logger.warning(
                    f"Rule '{rule_id}': Field '{condition.field}' is None in context"
                )
                return False

            if condition.operator == "equals":
                return field_value == condition.value
            elif condition.operator == "not_equals":
                return field_value != condition.value
            elif condition.operator == "in":
                return field_value in condition.value
            elif condition.operator == "not_in":
                return field_value not in condition.value

        return False

    def _calculate_value(self, expression: str, cost: float) -> float:
        """Evaluate a price expression with strict validation.

        Args:
            expression: Expression like 'cost * 1.10' or 'cost * 3.0'.
            cost: The historical cost value to use.

        Returns:
            Calculated price value.

        Raises:
            ValueError: If expression format is invalid.
        """
        expression = expression.strip()

        # Try strict "cost * multiplier" pattern first
        match = COST_EXPRESSION_PATTERN.match(expression)
        if match:
            multiplier = float(match.group(1))
            if multiplier <= 0:
                logger.error(f"Invalid multiplier (must be positive): {expression}")
                raise ValueError(f"Invalid multiplier in expression: {expression}")
            return cost * multiplier

        # Try direct float conversion as fallback (for literal values)
        try:
            value = float(expression)
            if value < 0:
                logger.error(f"Negative value not allowed: {expression}")
                raise ValueError(f"Negative value in expression: {expression}")
            return value
        except ValueError:
            logger.error(
                f"Invalid expression format: '{expression}'. "
                f"Expected 'cost * <number>' or a literal number."
            )
            raise ValueError(
                f"Cannot parse expression: '{expression}'. "
                f"Supported formats: 'cost * <number>' or literal number."
            )

    def _apply_action(
        self,
        action: RuleAction,
        current_price: float,
        context: MarketContext,
    ) -> float:
        """Apply a rule action to modify the price.

        Args:
            action: The action to apply.
            current_price: Current price before this action.
            context: Market context for lookups.

        Returns:
            Modified price after action.
        """
        cost = context.historical_cost_of_ride

        if action.type == "floor" and action.value:
            floor_value = self._calculate_value(action.value, cost)
            return max(current_price, floor_value)

        elif action.type == "cap" and action.value:
            cap_value = self._calculate_value(action.value, cost)
            return min(current_price, cap_value)

        elif action.type == "discount" and action.values:
            loyalty_tier = context.customer_loyalty_status
            if loyalty_tier not in action.values:
                logger.warning(
                    f"Loyalty tier '{loyalty_tier}' not found in discount config. "
                    f"Available tiers: {list(action.values.keys())}. Defaulting to 0% discount."
                )
            discount_rate = action.values.get(loyalty_tier, 0.0)
            return current_price * (1 - discount_rate)

        return current_price

    def apply(self, context: MarketContext, optimal_price: float) -> RulesResult:
        """Apply all business rules to an optimized price.

        Rules are applied in priority order. Each rule's impact is tracked.

        Args:
            context: Market context for rule evaluation.
            optimal_price: The ML-optimized price before business rules.

        Returns:
            RulesResult with final price and applied rule details.
        """
        current_price = optimal_price
        applied_rules: list[AppliedRule] = []

        for rule in self.rules:
            if not self._evaluate_condition(rule.condition, context, rule.id):
                continue

            price_before = current_price
            current_price = self._apply_action(rule.action, current_price, context)

            # Only record if price actually changed
            if price_before != current_price:
                impact = current_price - price_before
                impact_percent = (impact / price_before) * 100 if price_before else 0.0

                applied_rules.append(
                    AppliedRule(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        price_before=round(price_before, 2),
                        price_after=round(current_price, 2),
                        impact=round(impact, 2),
                        impact_percent=round(impact_percent, 2),
                    )
                )

                logger.debug(
                    f"Applied rule '{rule.name}': ${price_before:.2f} → ${current_price:.2f} "
                    f"({impact_percent:+.1f}%)"
                )

        total_adjustment = current_price - optimal_price
        total_adjustment_percent = (
            (total_adjustment / optimal_price) * 100 if optimal_price else 0.0
        )

        return RulesResult(
            original_price=round(optimal_price, 2),
            final_price=round(current_price, 2),
            applied_rules=applied_rules,
            total_adjustment=round(total_adjustment, 2),
            total_adjustment_percent=round(total_adjustment_percent, 2),
        )

