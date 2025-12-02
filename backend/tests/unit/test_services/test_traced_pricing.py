"""Tests for traced pricing service."""

import pytest

from src.explainability.decision_trace import DecisionTrace, format_trace_text
from src.ml.model_manager import get_model_manager
from src.ml.price_optimizer import get_price_optimizer
from src.ml.segmenter import Segmenter
from src.rules.engine import RulesEngine
from src.schemas.market import MarketContext
from src.schemas.pricing import PricingResult
from src.services.traced_pricing import TracedPricingService


@pytest.fixture
def market_context() -> MarketContext:
    """Create a test market context."""
    return MarketContext(
        number_of_riders=100,
        number_of_drivers=80,
        location_category="Urban",
        customer_loyalty_status="Silver",
        number_of_past_rides=15,
        average_ratings=4.5,
        time_of_booking="Morning",
        vehicle_type="Premium",
        expected_ride_duration=25,
        historical_cost_of_ride=35.0,
    )


@pytest.fixture
def traced_pricing_service() -> TracedPricingService:
    """Create a traced pricing service with real models."""
    segmenter = Segmenter.load()
    model_manager = get_model_manager()
    optimizer = get_price_optimizer(model_manager)
    rules_engine = RulesEngine()

    return TracedPricingService(
        segmenter=segmenter,
        model_manager=model_manager,
        optimizer=optimizer,
        rules_engine=rules_engine,
        model_name="xgboost",
    )


class TestTracedPricingService:
    """Tests for TracedPricingService."""

    @pytest.mark.asyncio
    async def test_get_recommendation_returns_result_and_trace(
        self,
        traced_pricing_service: TracedPricingService,
        market_context: MarketContext,
    ) -> None:
        """Test that recommendation returns both result and trace."""
        result, trace = await traced_pricing_service.get_recommendation_with_trace(
            market_context,
            log_trace=False,
        )

        assert isinstance(result, PricingResult)
        assert isinstance(trace, DecisionTrace)

    @pytest.mark.asyncio
    async def test_trace_has_seven_steps(
        self,
        traced_pricing_service: TracedPricingService,
        market_context: MarketContext,
    ) -> None:
        """Test trace captures all 7 pipeline steps (AC: 1)."""
        _, trace = await traced_pricing_service.get_recommendation_with_trace(
            market_context,
            log_trace=False,
        )

        # Should have exactly 7 steps
        assert len(trace.steps) == 7

        # Verify step names
        expected_steps = [
            "input_validation",
            "segment_classification",
            "external_factors",
            "demand_prediction",
            "price_optimization",
            "rules_application",
            "explanation_generation",
        ]
        actual_steps = [s.step_name for s in trace.steps]
        assert actual_steps == expected_steps

    @pytest.mark.asyncio
    async def test_all_steps_have_timing(
        self,
        traced_pricing_service: TracedPricingService,
        market_context: MarketContext,
    ) -> None:
        """Test all steps have timestamp and duration (AC: 2)."""
        _, trace = await traced_pricing_service.get_recommendation_with_trace(
            market_context,
            log_trace=False,
        )

        for step in trace.steps:
            assert step.timestamp is not None
            assert step.duration_ms >= 0

    @pytest.mark.asyncio
    async def test_all_steps_have_inputs_outputs(
        self,
        traced_pricing_service: TracedPricingService,
        market_context: MarketContext,
    ) -> None:
        """Test all steps have input and output values (AC: 2)."""
        _, trace = await traced_pricing_service.get_recommendation_with_trace(
            market_context,
            log_trace=False,
        )

        for step in trace.steps:
            # All successful steps should have inputs and outputs
            if step.status == "success":
                assert step.inputs is not None
                assert step.outputs is not None

    @pytest.mark.asyncio
    async def test_trace_has_model_agreement(
        self,
        traced_pricing_service: TracedPricingService,
        market_context: MarketContext,
    ) -> None:
        """Test trace includes model agreement analysis (AC: 4)."""
        _, trace = await traced_pricing_service.get_recommendation_with_trace(
            market_context,
            log_trace=False,
        )

        assert trace.model_agreement is not None
        assert len(trace.model_agreement.models_compared) >= 2
        assert trace.model_agreement.max_deviation_percent >= 0
        assert trace.model_agreement.status in [
            "full_agreement",
            "partial_agreement",
            "divergent",
        ]

    @pytest.mark.asyncio
    async def test_trace_exportable_as_json(
        self,
        traced_pricing_service: TracedPricingService,
        market_context: MarketContext,
    ) -> None:
        """Test trace can be exported as JSON (AC: 3)."""
        _, trace = await traced_pricing_service.get_recommendation_with_trace(
            market_context,
            log_trace=False,
        )

        # Should not raise
        json_str = trace.model_dump_json()

        assert "trace_id" in json_str
        assert "steps" in json_str
        assert "model_agreement" in json_str
        assert "final_result" in json_str

    @pytest.mark.asyncio
    async def test_trace_exportable_as_text(
        self,
        traced_pricing_service: TracedPricingService,
        market_context: MarketContext,
    ) -> None:
        """Test trace can be exported as formatted text (AC: 3)."""
        _, trace = await traced_pricing_service.get_recommendation_with_trace(
            market_context,
            log_trace=False,
        )

        text = format_trace_text(trace)

        # Check text format includes key elements
        assert "Decision Trace:" in text
        assert "Step 1:" in text
        assert "Step 7:" in text
        assert "Model Agreement:" in text
        assert "Final Price:" in text

    @pytest.mark.asyncio
    async def test_trace_total_duration(
        self,
        traced_pricing_service: TracedPricingService,
        market_context: MarketContext,
    ) -> None:
        """Test trace has total duration."""
        _, trace = await traced_pricing_service.get_recommendation_with_trace(
            market_context,
            log_trace=False,
        )

        assert trace.total_duration_ms > 0
        # Sum of step durations should be <= total (may be less due to overhead)
        step_total = sum(s.duration_ms for s in trace.steps)
        assert step_total <= trace.total_duration_ms + 10  # Allow small margin

    @pytest.mark.asyncio
    async def test_result_matches_trace(
        self,
        traced_pricing_service: TracedPricingService,
        market_context: MarketContext,
    ) -> None:
        """Test pricing result matches trace final_result."""
        result, trace = await traced_pricing_service.get_recommendation_with_trace(
            market_context,
            log_trace=False,
        )

        assert trace.final_result["recommended_price"] == result.recommended_price
        assert trace.final_result["confidence_score"] == result.confidence_score

    @pytest.mark.asyncio
    async def test_segment_step_captures_details(
        self,
        traced_pricing_service: TracedPricingService,
        market_context: MarketContext,
    ) -> None:
        """Test segment classification step captures key details."""
        _, trace = await traced_pricing_service.get_recommendation_with_trace(
            market_context,
            log_trace=False,
        )

        segment_step = next(
            s for s in trace.steps if s.step_name == "segment_classification"
        )

        assert "location" in segment_step.inputs
        assert "segment" in segment_step.outputs
        assert "confidence" in segment_step.outputs

    @pytest.mark.asyncio
    async def test_optimization_step_captures_details(
        self,
        traced_pricing_service: TracedPricingService,
        market_context: MarketContext,
    ) -> None:
        """Test price optimization step captures key details."""
        _, trace = await traced_pricing_service.get_recommendation_with_trace(
            market_context,
            log_trace=False,
        )

        opt_step = next(
            s for s in trace.steps if s.step_name == "price_optimization"
        )

        assert "optimal_price" in opt_step.outputs
        assert "expected_demand" in opt_step.outputs
        assert "profit_uplift_percent" in opt_step.outputs

    @pytest.mark.asyncio
    async def test_rules_step_captures_applied_rules(
        self,
        traced_pricing_service: TracedPricingService,
        market_context: MarketContext,
    ) -> None:
        """Test rules application step captures applied rules."""
        _, trace = await traced_pricing_service.get_recommendation_with_trace(
            market_context,
            log_trace=False,
        )

        rules_step = next(
            s for s in trace.steps if s.step_name == "rules_application"
        )

        assert "final_price" in rules_step.outputs
        assert "rules_applied" in rules_step.outputs
        assert "rules_count" in rules_step.outputs

    @pytest.mark.asyncio
    async def test_all_steps_successful(
        self,
        traced_pricing_service: TracedPricingService,
        market_context: MarketContext,
    ) -> None:
        """Test all steps complete successfully for valid input."""
        _, trace = await traced_pricing_service.get_recommendation_with_trace(
            market_context,
            log_trace=False,
        )

        for step in trace.steps:
            assert step.status == "success", f"Step {step.step_name} failed"
            assert step.error_message is None

