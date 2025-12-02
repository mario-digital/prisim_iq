"""Tests for decision trace module."""

import time
from datetime import datetime

import pytest

from src.explainability.decision_trace import (
    DecisionTrace,
    DecisionTracer,
    ModelAgreement,
    TraceStep,
    calculate_model_agreement,
    format_trace_text,
)


class TestTraceStep:
    """Tests for TraceStep model."""

    def test_create_success_step(self) -> None:
        """Test creating a successful trace step."""
        step = TraceStep(
            step_name="segment_classification",
            timestamp=datetime.utcnow(),
            duration_ms=45.5,
            inputs={"context": "test"},
            outputs={"segment": "Urban_Peak_Premium"},
            status="success",
        )

        assert step.step_name == "segment_classification"
        assert step.duration_ms == 45.5
        assert step.status == "success"
        assert step.error_message is None

    def test_create_error_step(self) -> None:
        """Test creating an error trace step."""
        step = TraceStep(
            step_name="external_factors",
            timestamp=datetime.utcnow(),
            duration_ms=120.0,
            inputs={"location": "NYC"},
            outputs={},
            status="error",
            error_message="API timeout",
        )

        assert step.status == "error"
        assert step.error_message == "API timeout"
        assert step.outputs == {}

    def test_create_skipped_step(self) -> None:
        """Test creating a skipped trace step."""
        step = TraceStep(
            step_name="optional_step",
            timestamp=datetime.utcnow(),
            duration_ms=0.1,
            inputs={},
            outputs={},
            status="skipped",
        )

        assert step.status == "skipped"
        assert step.duration_ms >= 0


class TestModelAgreement:
    """Tests for ModelAgreement model."""

    def test_full_agreement(self) -> None:
        """Test full agreement when all models predict within 5%."""
        agreement = ModelAgreement(
            models_compared=["xgboost", "linear_regression", "decision_tree"],
            predictions={"xgboost": 42.50, "linear_regression": 42.00, "decision_tree": 43.00},
            max_deviation_percent=1.2,
            is_agreement=True,
            status="full_agreement",
        )

        assert agreement.is_agreement is True
        assert agreement.status == "full_agreement"
        assert len(agreement.models_compared) == 3

    def test_partial_agreement(self) -> None:
        """Test partial agreement when within 10% but over 5%."""
        agreement = ModelAgreement(
            models_compared=["xgboost", "linear_regression"],
            predictions={"xgboost": 45.00, "linear_regression": 42.00},
            max_deviation_percent=7.0,
            is_agreement=True,
            status="partial_agreement",
        )

        assert agreement.is_agreement is True
        assert agreement.status == "partial_agreement"

    def test_divergent(self) -> None:
        """Test divergent status when over 10% deviation."""
        agreement = ModelAgreement(
            models_compared=["xgboost", "linear_regression"],
            predictions={"xgboost": 50.00, "linear_regression": 35.00},
            max_deviation_percent=17.6,
            is_agreement=False,
            status="divergent",
        )

        assert agreement.is_agreement is False
        assert agreement.status == "divergent"


class TestCalculateModelAgreement:
    """Tests for calculate_model_agreement function."""

    def test_empty_predictions(self) -> None:
        """Test with no predictions."""
        result = calculate_model_agreement({})

        assert result.models_compared == []
        assert result.predictions == {}
        assert result.max_deviation_percent == 0.0
        assert result.is_agreement is True
        assert result.status == "full_agreement"

    def test_single_model(self) -> None:
        """Test with single model prediction."""
        result = calculate_model_agreement({"xgboost": 42.50})

        assert result.models_compared == ["xgboost"]
        assert result.max_deviation_percent == 0.0
        assert result.is_agreement is True
        assert result.status == "full_agreement"

    def test_full_agreement_calculation(self) -> None:
        """Test calculation produces full agreement."""
        # All within ~2% of mean ($42.50)
        predictions = {
            "xgboost": 42.50,
            "linear_regression": 42.00,
            "decision_tree": 43.00,
        }
        result = calculate_model_agreement(predictions)

        assert result.is_agreement is True
        assert result.status == "full_agreement"
        assert result.max_deviation_percent <= 5.0
        assert len(result.models_compared) == 3

    def test_partial_agreement_calculation(self) -> None:
        """Test calculation produces partial agreement (5-10%)."""
        # Mean is ~42.5, max deviation ~8.2%
        predictions = {
            "xgboost": 46.00,
            "linear_regression": 42.00,
            "decision_tree": 40.00,
        }
        result = calculate_model_agreement(predictions)

        assert 5.0 < result.max_deviation_percent <= 10.0
        assert result.is_agreement is True
        assert result.status == "partial_agreement"

    def test_divergent_calculation(self) -> None:
        """Test calculation produces divergent status (>10%)."""
        # Mean is ~40, max deviation >15%
        predictions = {
            "xgboost": 50.00,
            "linear_regression": 35.00,
            "decision_tree": 35.00,
        }
        result = calculate_model_agreement(predictions)

        assert result.max_deviation_percent > 10.0
        assert result.is_agreement is False
        assert result.status == "divergent"

    def test_predictions_rounded(self) -> None:
        """Test that predictions are rounded to 4 decimal places."""
        predictions = {"xgboost": 42.123456789}
        result = calculate_model_agreement(predictions)

        assert result.predictions["xgboost"] == 42.1235


class TestDecisionTracer:
    """Tests for DecisionTracer class."""

    def test_tracer_initialization(self) -> None:
        """Test tracer initializes with unique ID and timestamp."""
        tracer = DecisionTracer()

        assert tracer.trace_id is not None
        assert len(tracer.trace_id) == 36  # UUID format
        assert tracer.request_timestamp is not None
        assert tracer.steps == []
        assert tracer.model_agreement is None

    def test_add_step_manually(self) -> None:
        """Test manually adding a step."""
        tracer = DecisionTracer()

        tracer.add_step(
            step_name="input_validation",
            inputs={"context": "MarketContext(...)"},
            outputs={"valid": True},
            duration_ms=15.0,
            status="success",
        )

        assert len(tracer.steps) == 1
        assert tracer.steps[0].step_name == "input_validation"
        assert tracer.steps[0].duration_ms == 15.0
        assert tracer.steps[0].status == "success"

    def test_add_multiple_steps(self) -> None:
        """Test adding multiple steps in order."""
        tracer = DecisionTracer()

        step_names = ["input_validation", "segment_classification", "price_optimization"]
        for name in step_names:
            tracer.add_step(
                step_name=name,
                inputs={},
                outputs={},
                duration_ms=10.0,
                status="success",
            )

        assert len(tracer.steps) == 3
        assert [s.step_name for s in tracer.steps] == step_names

    def test_trace_step_decorator_success(self) -> None:
        """Test trace_step decorator captures successful execution."""
        tracer = DecisionTracer()

        @tracer.trace_step("test_step")
        def test_function(x: int, y: int) -> int:
            return x + y

        result = test_function(2, 3)

        assert result == 5
        assert len(tracer.steps) == 1
        assert tracer.steps[0].step_name == "test_step"
        assert tracer.steps[0].status == "success"
        assert tracer.steps[0].duration_ms > 0

    def test_trace_step_decorator_error(self) -> None:
        """Test trace_step decorator captures errors."""
        tracer = DecisionTracer()

        @tracer.trace_step("failing_step")
        def failing_function() -> None:
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_function()

        assert len(tracer.steps) == 1
        assert tracer.steps[0].status == "error"
        assert tracer.steps[0].error_message == "Test error"

    def test_set_model_agreement(self) -> None:
        """Test setting model agreement."""
        tracer = DecisionTracer()
        predictions = {"xgboost": 42.50, "linear_regression": 43.00}

        result = tracer.set_model_agreement(predictions)

        assert tracer.model_agreement is not None
        assert tracer.model_agreement == result
        assert result.is_agreement is True

    def test_finalize_creates_complete_trace(self) -> None:
        """Test finalize creates complete DecisionTrace."""
        tracer = DecisionTracer()

        # Add some steps
        tracer.add_step("step1", {}, {"result": "ok"}, 10.0, "success")
        tracer.add_step("step2", {}, {"result": "done"}, 20.0, "success")
        tracer.set_model_agreement({"xgboost": 42.50})

        # Finalize
        trace = tracer.finalize(
            final_result={"recommended_price": 42.50},
            log_to_file=False,
        )

        assert isinstance(trace, DecisionTrace)
        assert trace.trace_id == tracer.trace_id
        assert len(trace.steps) == 2
        assert trace.model_agreement is not None
        assert trace.final_result["recommended_price"] == 42.50
        assert trace.total_duration_ms > 0

    def test_finalize_with_timing(self) -> None:
        """Test finalize captures total duration."""
        tracer = DecisionTracer()

        # Simulate some work
        time.sleep(0.01)  # 10ms

        trace = tracer.finalize({"price": 42.50}, log_to_file=False)

        # Should be at least 10ms
        assert trace.total_duration_ms >= 10.0

    def test_duration_ms_positive(self) -> None:
        """Test all steps have positive duration."""
        tracer = DecisionTracer()

        @tracer.trace_step("fast_step")
        def fast_function() -> str:
            return "done"

        fast_function()

        assert tracer.steps[0].duration_ms >= 0


class TestDecisionTrace:
    """Tests for DecisionTrace model."""

    def test_create_trace(self) -> None:
        """Test creating a complete trace."""
        trace = DecisionTrace(
            trace_id="abc-123-def",
            request_timestamp=datetime.utcnow(),
            total_duration_ms=1234.5,
            steps=[
                TraceStep(
                    step_name="step1",
                    timestamp=datetime.utcnow(),
                    duration_ms=100.0,
                    inputs={},
                    outputs={},
                    status="success",
                )
            ],
            model_agreement=ModelAgreement(
                models_compared=["xgboost"],
                predictions={"xgboost": 42.50},
                max_deviation_percent=0.0,
                is_agreement=True,
                status="full_agreement",
            ),
            final_result={"recommended_price": 42.50},
        )

        assert trace.trace_id == "abc-123-def"
        assert trace.total_duration_ms == 1234.5
        assert len(trace.steps) == 1
        assert trace.model_agreement is not None
        assert trace.final_result["recommended_price"] == 42.50

    def test_trace_json_serializable(self) -> None:
        """Test trace can be serialized to JSON."""
        tracer = DecisionTracer()
        tracer.add_step("test", {"input": 1}, {"output": 2}, 10.0, "success")
        tracer.set_model_agreement({"xgboost": 42.50})

        trace = tracer.finalize({"price": 42.50}, log_to_file=False)

        # Should not raise
        json_str = trace.model_dump_json()
        assert "trace_id" in json_str
        assert "steps" in json_str


class TestFormatTraceText:
    """Tests for format_trace_text function."""

    def test_basic_format(self) -> None:
        """Test basic text formatting."""
        trace = DecisionTrace(
            trace_id="abc-123-def-456-ghi",
            request_timestamp=datetime(2024, 12, 2, 10, 15, 30),
            total_duration_ms=1234.5,
            steps=[
                TraceStep(
                    step_name="input_validation",
                    timestamp=datetime.utcnow(),
                    duration_ms=15.0,
                    inputs={"context": "test"},
                    outputs={"result": "Valid"},
                    status="success",
                ),
                TraceStep(
                    step_name="segment_classification",
                    timestamp=datetime.utcnow(),
                    duration_ms=45.0,
                    inputs={},
                    outputs={"result": "Urban_Peak_Premium"},
                    status="success",
                ),
            ],
            model_agreement=ModelAgreement(
                models_compared=["xgboost", "linear_regression"],
                predictions={"xgboost": 42.50, "linear_regression": 43.10},
                max_deviation_percent=3.2,
                is_agreement=True,
                status="full_agreement",
            ),
            final_result={"recommended_price": 42.50},
        )

        text = format_trace_text(trace)

        # Check header
        assert "=== Decision Trace: abc-123-" in text
        assert "Total Duration: 1,234.5ms" in text

        # Check steps
        assert "Step 1: Input Validation" in text
        assert "15.0ms" in text
        assert "✓" in text

        # Check model agreement
        assert "Model Agreement: FULL" in text
        assert "max deviation 3.2%" in text
        assert "xgboost: $42.50" in text

        # Check final price
        assert "Final Price: $42.50" in text

    def test_format_with_error_step(self) -> None:
        """Test formatting includes error message."""
        trace = DecisionTrace(
            trace_id="test-trace",
            request_timestamp=datetime.utcnow(),
            total_duration_ms=100.0,
            steps=[
                TraceStep(
                    step_name="failing_step",
                    timestamp=datetime.utcnow(),
                    duration_ms=50.0,
                    inputs={},
                    outputs={},
                    status="error",
                    error_message="Something went wrong",
                ),
            ],
            final_result={},
        )

        text = format_trace_text(trace)

        assert "✗" in text
        assert "Error: Something went wrong" in text

    def test_format_divergent_agreement(self) -> None:
        """Test formatting shows divergent status."""
        trace = DecisionTrace(
            trace_id="test-trace",
            request_timestamp=datetime.utcnow(),
            total_duration_ms=100.0,
            steps=[],
            model_agreement=ModelAgreement(
                models_compared=["xgboost", "linear_regression"],
                predictions={"xgboost": 50.0, "linear_regression": 35.0},
                max_deviation_percent=17.6,
                is_agreement=False,
                status="divergent",
            ),
            final_result={"recommended_price": 42.50},
        )

        text = format_trace_text(trace)

        assert "Model Agreement: DIVERGENT" in text
        assert "17.6%" in text


class TestIntegration:
    """Integration tests for the complete tracing flow."""

    def test_complete_pipeline_trace(self) -> None:
        """Test tracing a complete pipeline simulation."""
        tracer = DecisionTracer()

        # Simulate pipeline steps
        tracer.add_step(
            "input_validation",
            inputs={"context": "MarketContext(location=Urban, ...)"},
            outputs={"valid": True},
            duration_ms=15.0,
        )

        tracer.add_step(
            "segment_classification",
            inputs={"features": [0.5, 0.3, 0.8]},
            outputs={"segment": "Urban_Peak_Premium", "confidence": 0.92},
            duration_ms=45.0,
        )

        tracer.add_step(
            "external_factors",
            inputs={"location": "NYC"},
            outputs={"weather": "rainy", "events": "none"},
            duration_ms=120.0,
        )

        tracer.add_step(
            "demand_prediction",
            inputs={"segment": "Urban_Peak_Premium", "price": 42.50},
            outputs={"demand": 0.72},
            duration_ms=25.0,
        )

        tracer.add_step(
            "price_optimization",
            inputs={"demand_curve": "..."},
            outputs={"optimal_price": 42.50, "profit_uplift": 8.5},
            duration_ms=150.0,
        )

        tracer.add_step(
            "rules_application",
            inputs={"price": 42.50, "context": "..."},
            outputs={"final_price": 42.50, "rules_applied": 2},
            duration_ms=10.0,
        )

        tracer.add_step(
            "explanation_generation",
            inputs={"trace": "..."},
            outputs={"explanation": "Price optimized for urban peak demand"},
            duration_ms=5.0,
        )

        # Set model agreement
        tracer.set_model_agreement({
            "xgboost": 42.50,
            "linear_regression": 43.10,
            "decision_tree": 41.80,
        })

        # Finalize
        trace = tracer.finalize(
            {"recommended_price": 42.50, "confidence": 0.92},
            log_to_file=False,
        )

        # Verify all 7 steps captured (AC: 1)
        assert len(trace.steps) == 7

        # Verify all steps have positive duration (AC: 2)
        for step in trace.steps:
            assert step.duration_ms > 0
            assert step.timestamp is not None

        # Verify model agreement (AC: 4)
        assert trace.model_agreement is not None
        assert trace.model_agreement.is_agreement is True

        # Verify JSON export (AC: 3)
        json_output = trace.model_dump_json()
        assert "trace_id" in json_output
        assert "steps" in json_output

        # Verify text export (AC: 3)
        text_output = format_trace_text(trace)
        assert "Decision Trace" in text_output
        assert "Step 1:" in text_output
        assert "Step 7:" in text_output

    def test_all_seven_pipeline_steps(self) -> None:
        """Test that exactly 7 pipeline steps can be captured per requirements."""
        expected_steps = [
            "input_validation",
            "segment_classification",
            "external_factors",
            "demand_prediction",
            "price_optimization",
            "rules_application",
            "explanation_generation",
        ]

        tracer = DecisionTracer()

        for step in expected_steps:
            tracer.add_step(step, {}, {}, 10.0)

        assert len(tracer.steps) == 7
        assert [s.step_name for s in tracer.steps] == expected_steps

