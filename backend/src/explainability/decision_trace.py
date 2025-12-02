"""Decision trace module for auditing pricing pipeline decisions.

This module provides step-by-step tracing of the pricing pipeline,
capturing inputs, outputs, timing, and model agreement information
for audit and explainability purposes.
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime
from functools import wraps
from pathlib import Path
from collections.abc import Callable
from typing import Any, Literal, TypeVar

from loguru import logger
from pydantic import BaseModel, Field

from src.config import get_settings

# Type variable for decorator return type preservation
F = TypeVar("F", bound=Callable[..., Any])


class TraceStep(BaseModel):
    """A single step in the decision trace.

    Attributes:
        step_name: Identifier for the pipeline step (e.g., "segment_classification").
        timestamp: When this step started.
        duration_ms: Time taken for this step in milliseconds.
        inputs: Dictionary of input values to this step.
        outputs: Dictionary of output values from this step.
        status: Whether the step succeeded, failed, or was skipped.
        error_message: Error details if status is "error".
    """

    step_name: str = Field(..., description="Pipeline step identifier")
    timestamp: datetime = Field(..., description="Step start timestamp")
    duration_ms: float = Field(..., ge=0, description="Step duration in milliseconds")
    inputs: dict[str, Any] = Field(default_factory=dict, description="Step inputs")
    outputs: dict[str, Any] = Field(default_factory=dict, description="Step outputs")
    status: Literal["success", "error", "skipped"] = Field(
        ..., description="Step completion status"
    )
    error_message: str | None = Field(None, description="Error message if failed")


class ModelAgreement(BaseModel):
    """Model agreement analysis across all prediction models.

    Attributes:
        models_compared: List of model names that were compared.
        predictions: Dictionary mapping model names to their predictions.
        max_deviation_percent: Maximum percentage deviation between models.
        is_agreement: True if all models agree within 10%.
        status: Agreement classification.
    """

    models_compared: list[str] = Field(..., description="Models used in comparison")
    predictions: dict[str, float] = Field(..., description="Model predictions mapping")
    max_deviation_percent: float = Field(
        ..., ge=0, description="Maximum deviation percentage"
    )
    is_agreement: bool = Field(..., description="Whether models agree within 10%")
    status: Literal["full_agreement", "partial_agreement", "divergent"] = Field(
        ..., description="Agreement status classification"
    )


class DecisionTrace(BaseModel):
    """Complete decision trace for a pricing request.

    Contains all steps, timing, model agreement, and final result
    for audit and explainability purposes.

    Attributes:
        trace_id: Unique identifier for this trace.
        request_timestamp: When the request was received.
        total_duration_ms: Total pipeline execution time.
        steps: List of all traced steps in order.
        model_agreement: Model agreement analysis results.
        final_result: The final pricing result.
    """

    trace_id: str = Field(..., description="Unique trace identifier")
    request_timestamp: datetime = Field(..., description="Request start timestamp")
    total_duration_ms: float = Field(..., ge=0, description="Total execution time in ms")
    steps: list[TraceStep] = Field(default_factory=list, description="Pipeline steps")
    model_agreement: ModelAgreement | None = Field(
        None, description="Model agreement analysis"
    )
    final_result: dict[str, Any] = Field(
        default_factory=dict, description="Final pricing result"
    )


class DecisionTracer:
    """Tracer for capturing decision pipeline steps.

    Usage:
        tracer = DecisionTracer()

        # Using decorator
        @tracer.trace_step("segment_classification")
        def classify_segment(context):
            ...

        # Using context manager style
        with tracer.record_step("external_factors", inputs={"location": "NYC"}):
            result = fetch_external_data()
        tracer.current_step.outputs = {"weather": "rainy"}

        # Get complete trace
        trace = tracer.finalize(final_result={"price": 42.50})
    """

    def __init__(self) -> None:
        """Initialize a new decision tracer."""
        self.trace_id = str(uuid.uuid4())
        self.request_timestamp = datetime.utcnow()
        self._start_time = time.perf_counter()
        self.steps: list[TraceStep] = []
        self.model_agreement: ModelAgreement | None = None

    def trace_step(self, step_name: str) -> Callable[[F], F]:
        """Decorator to trace a function as a pipeline step.

        Args:
            step_name: Name identifier for this step.

        Returns:
            Decorator function that wraps the target function with tracing.

        Example:
            @tracer.trace_step("segment_classification")
            def classify(context):
                return segment_name
        """

        def decorator(func: F) -> F:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                step_start = time.perf_counter()
                timestamp = datetime.utcnow()

                # Capture inputs (exclude self for methods)
                input_args = args[1:] if args and hasattr(args[0], "__dict__") else args
                inputs = {
                    "args": [_safe_serialize(a) for a in input_args],
                    "kwargs": {k: _safe_serialize(v) for k, v in kwargs.items()},
                }

                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.perf_counter() - step_start) * 1000

                    self.steps.append(
                        TraceStep(
                            step_name=step_name,
                            timestamp=timestamp,
                            duration_ms=round(duration_ms, 3),
                            inputs=inputs,
                            outputs={"result": _safe_serialize(result)},
                            status="success",
                        )
                    )
                    return result

                except Exception as e:
                    duration_ms = (time.perf_counter() - step_start) * 1000
                    self.steps.append(
                        TraceStep(
                            step_name=step_name,
                            timestamp=timestamp,
                            duration_ms=round(duration_ms, 3),
                            inputs=inputs,
                            outputs={},
                            status="error",
                            error_message=str(e),
                        )
                    )
                    raise

            return wrapper  # type: ignore[return-value]

        return decorator

    def add_step(
        self,
        step_name: str,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        duration_ms: float,
        status: Literal["success", "error", "skipped"] = "success",
        error_message: str | None = None,
    ) -> None:
        """Manually add a traced step.

        Args:
            step_name: Name identifier for this step.
            inputs: Dictionary of input values.
            outputs: Dictionary of output values.
            duration_ms: Step duration in milliseconds.
            status: Completion status.
            error_message: Error message if status is "error".
        """
        self.steps.append(
            TraceStep(
                step_name=step_name,
                timestamp=datetime.utcnow(),
                duration_ms=round(duration_ms, 3),
                inputs={k: _safe_serialize(v) for k, v in inputs.items()},
                outputs={k: _safe_serialize(v) for k, v in outputs.items()},
                status=status,
                error_message=error_message,
            )
        )

    def set_model_agreement(self, predictions: dict[str, float]) -> ModelAgreement:
        """Calculate and set model agreement from predictions.

        Args:
            predictions: Dictionary mapping model names to predicted values.

        Returns:
            ModelAgreement analysis result.
        """
        self.model_agreement = calculate_model_agreement(predictions)
        return self.model_agreement

    def finalize(
        self,
        final_result: dict[str, Any],
        log_to_file: bool | None = None,
    ) -> DecisionTrace:
        """Finalize the trace and optionally log to file.

        Args:
            final_result: The final pricing result dictionary.
            log_to_file: Whether to log trace to file. If None, uses config setting.

        Returns:
            Complete DecisionTrace object.
        """
        total_duration_ms = (time.perf_counter() - self._start_time) * 1000

        trace = DecisionTrace(
            trace_id=self.trace_id,
            request_timestamp=self.request_timestamp,
            total_duration_ms=round(total_duration_ms, 3),
            steps=self.steps,
            model_agreement=self.model_agreement,
            final_result={k: _safe_serialize(v) for k, v in final_result.items()},
        )

        # Optional file logging
        settings = get_settings()
        should_log = log_to_file if log_to_file is not None else settings.debug
        if should_log:
            _log_trace_to_file(trace)

        return trace


def calculate_model_agreement(predictions: dict[str, float]) -> ModelAgreement:
    """Calculate model agreement metrics from predictions.

    Agreement is defined as all models predicting within 10% of each other
    relative to the mean prediction.

    Args:
        predictions: Dictionary mapping model names to predicted values.

    Returns:
        ModelAgreement with deviation analysis.
    """
    if not predictions:
        return ModelAgreement(
            models_compared=[],
            predictions={},
            max_deviation_percent=0.0,
            is_agreement=True,
            status="full_agreement",
        )

    values = list(predictions.values())
    mean_value = sum(values) / len(values) if values else 0

    # Calculate max deviation as percentage from mean
    if mean_value > 0:
        deviations = [abs(v - mean_value) / mean_value * 100 for v in values]
        max_deviation = max(deviations) if deviations else 0.0
    else:
        max_deviation = 0.0

    # Agreement if all within 10% of mean
    is_agreement = max_deviation <= 10.0

    # Classify agreement status
    if max_deviation <= 5.0:
        status: Literal["full_agreement", "partial_agreement", "divergent"] = (
            "full_agreement"
        )
    elif max_deviation <= 10.0:
        status = "partial_agreement"
    else:
        status = "divergent"

    return ModelAgreement(
        models_compared=list(predictions.keys()),
        predictions={k: round(v, 4) for k, v in predictions.items()},
        max_deviation_percent=round(max_deviation, 2),
        is_agreement=is_agreement,
        status=status,
    )


def format_trace_text(trace: DecisionTrace) -> str:
    """Format decision trace as human-readable text.

    Args:
        trace: The decision trace to format.

    Returns:
        Formatted text representation of the trace.
    """
    lines = [
        f"=== Decision Trace: {trace.trace_id[:8]}... ===",
        f"Request Time: {trace.request_timestamp.isoformat()}Z",
        f"Total Duration: {trace.total_duration_ms:,.1f}ms",
        "",
    ]

    # Add each step
    for i, step in enumerate(trace.steps, 1):
        status_icon = {"success": "✓", "error": "✗", "skipped": "○"}.get(
            step.status, "?"
        )
        lines.append(f"Step {i}: {_format_step_name(step.step_name)} ({step.duration_ms:.1f}ms) {status_icon}")

        # Format inputs
        if step.inputs:
            input_str = _format_dict_short(step.inputs)
            lines.append(f"  Input: {input_str}")

        # Format outputs
        if step.outputs:
            output_str = _format_dict_short(step.outputs)
            lines.append(f"  Output: {output_str}")

        # Show error if present
        if step.error_message:
            lines.append(f"  Error: {step.error_message}")

        lines.append("")

    # Add model agreement section
    if trace.model_agreement:
        ma = trace.model_agreement
        status_display = {
            "full_agreement": "FULL",
            "partial_agreement": "PARTIAL",
            "divergent": "DIVERGENT",
        }.get(ma.status, ma.status.upper())

        lines.append(f"Model Agreement: {status_display} (max deviation {ma.max_deviation_percent:.1f}%)")

        for model, pred in ma.predictions.items():
            lines.append(f"  - {model}: ${pred:.2f}")

        lines.append("")

    # Add final result
    if trace.final_result:
        final_price = trace.final_result.get("recommended_price", "N/A")
        if isinstance(final_price, (int, float)):
            lines.append(f"Final Price: ${final_price:.2f}")
        else:
            lines.append(f"Final Price: {final_price}")

    return "\n".join(lines)


def _format_step_name(name: str) -> str:
    """Convert snake_case step name to Title Case."""
    return name.replace("_", " ").title()


def _format_dict_short(d: dict[str, Any], max_len: int = 100) -> str:
    """Format dictionary to short string representation."""
    if not d:
        return "{}"

    # For simple single-value results, show just the value
    if len(d) == 1 and "result" in d:
        val = d["result"]
        if isinstance(val, str) and len(val) <= max_len:
            return val
        return str(val)[:max_len] + "..." if len(str(val)) > max_len else str(val)

    # Otherwise show abbreviated dict
    parts = []
    for k, v in d.items():
        if k in ("args", "kwargs"):
            continue  # Skip decorator artifacts
        v_str = str(v)
        if len(v_str) > 50:
            v_str = v_str[:47] + "..."
        parts.append(f"{k}={v_str}")

    result = ", ".join(parts)
    if len(result) > max_len:
        result = result[: max_len - 3] + "..."
    return result


def _safe_serialize(obj: Any) -> Any:
    """Safely serialize an object for JSON storage.

    Args:
        obj: Object to serialize.

    Returns:
        JSON-serializable representation.
    """
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_safe_serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {str(k): _safe_serialize(v) for k, v in obj.items()}
    if hasattr(obj, "model_dump"):
        # Pydantic model
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return {k: _safe_serialize(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
    # Fallback to string representation
    return str(obj)


def _log_trace_to_file(trace: DecisionTrace) -> None:
    """Log trace to audit file.

    Args:
        trace: The decision trace to log.
    """
    try:
        # Create logs directory if needed
        log_dir = Path("logs/traces")
        log_dir.mkdir(parents=True, exist_ok=True)

        # Write trace to file
        log_file = log_dir / f"trace_{trace.trace_id}.json"
        log_file.write_text(trace.model_dump_json(indent=2))

        logger.debug(f"Trace logged to {log_file}")

    except Exception as e:
        logger.warning(f"Failed to log trace to file: {e}")

