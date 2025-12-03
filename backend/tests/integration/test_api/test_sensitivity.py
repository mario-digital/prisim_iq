"""Integration tests for sensitivity analysis endpoint.

These tests run real sensitivity analysis with ProcessPoolExecutor,
which is slow in CI. Marked slow to skip in fast CI runs.
"""

import time

import pytest
from fastapi.testclient import TestClient

# Mark all tests in this module as slow
pytestmark = pytest.mark.slow


class TestSensitivityAnalysisEndpoint:
    """Tests for POST /api/v1/sensitivity_analysis endpoint."""

    def test_sensitivity_analysis_returns_valid_response(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test sensitivity_analysis endpoint returns expected structure."""
        response = client.post("/api/v1/sensitivity_analysis", json=valid_market_context)
        assert response.status_code == 200

        data = response.json()

        # Base reference (AC: 1)
        assert "base_context" in data
        assert "base_price" in data
        assert "base_profit" in data

        # Sensitivity arrays (AC: 2)
        assert "elasticity_sensitivity" in data
        assert "demand_sensitivity" in data
        assert "cost_sensitivity" in data

        # Confidence metrics (AC: 3)
        assert "confidence_band" in data
        assert "robustness_score" in data

        # Extremes
        assert "worst_case" in data
        assert "best_case" in data

        # Metadata
        assert "scenarios_calculated" in data
        assert "processing_time_ms" in data

    def test_elasticity_sensitivity_has_7_points(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test elasticity_sensitivity has 7 data points (AC: 2)."""
        response = client.post("/api/v1/sensitivity_analysis", json=valid_market_context)
        data = response.json()

        elasticity = data["elasticity_sensitivity"]
        assert isinstance(elasticity, list)
        assert len(elasticity) == 7, f"Expected 7 points, got {len(elasticity)}"

    def test_demand_sensitivity_has_5_points(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test demand_sensitivity has 5 data points (AC: 2)."""
        response = client.post("/api/v1/sensitivity_analysis", json=valid_market_context)
        data = response.json()

        demand = data["demand_sensitivity"]
        assert isinstance(demand, list)
        assert len(demand) == 5, f"Expected 5 points, got {len(demand)}"

    def test_cost_sensitivity_has_5_points(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test cost_sensitivity has 5 data points (AC: 2)."""
        response = client.post("/api/v1/sensitivity_analysis", json=valid_market_context)
        data = response.json()

        cost = data["cost_sensitivity"]
        assert isinstance(cost, list)
        assert len(cost) == 5, f"Expected 5 points, got {len(cost)}"

    def test_sensitivity_point_structure(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test sensitivity points have chart-ready structure (AC: 2)."""
        response = client.post("/api/v1/sensitivity_analysis", json=valid_market_context)
        data = response.json()

        # Check first point in elasticity_sensitivity
        point = data["elasticity_sensitivity"][0]
        assert "x" in point, "Missing 'x' coordinate"
        assert "y" in point, "Missing 'y' coordinate"
        assert "label" in point, "Missing 'label'"
        assert "profit" in point, "Missing 'profit'"
        assert "demand" in point, "Missing 'demand'"

        # Validate types
        assert isinstance(point["x"], (int, float))
        assert isinstance(point["y"], (int, float))
        assert isinstance(point["label"], str)
        assert isinstance(point["profit"], (int, float))
        assert isinstance(point["demand"], (int, float))

    def test_confidence_band_structure(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test confidence_band has correct structure (AC: 3)."""
        response = client.post("/api/v1/sensitivity_analysis", json=valid_market_context)
        data = response.json()

        band = data["confidence_band"]
        assert "min_price" in band
        assert "max_price" in band
        assert "price_range" in band
        assert "range_percent" in band

        # Validate logical constraints
        assert band["min_price"] <= band["max_price"]
        assert band["price_range"] >= 0
        assert band["price_range"] == band["max_price"] - band["min_price"]

    def test_robustness_score_in_valid_range(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test robustness_score is in [0, 100] range (AC: 3)."""
        response = client.post("/api/v1/sensitivity_analysis", json=valid_market_context)
        data = response.json()

        score = data["robustness_score"]
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100, f"Score {score} not in [0, 100]"

    def test_base_context_summary(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test base_context contains market context summary."""
        response = client.post("/api/v1/sensitivity_analysis", json=valid_market_context)
        data = response.json()

        context = data["base_context"]
        assert "location_category" in context
        assert "vehicle_type" in context
        assert "customer_loyalty_status" in context
        assert "time_of_booking" in context
        assert "supply_demand_ratio" in context

        # Validate values match input
        assert context["location_category"] == valid_market_context["location_category"]
        assert context["vehicle_type"] == valid_market_context["vehicle_type"]

    def test_worst_case_structure(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test worst_case has scenario summary structure."""
        response = client.post("/api/v1/sensitivity_analysis", json=valid_market_context)
        data = response.json()

        worst = data["worst_case"]
        assert "scenario_name" in worst
        assert "scenario_type" in worst
        assert "price" in worst
        assert "profit" in worst
        assert "description" in worst

    def test_best_case_structure(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test best_case has scenario summary structure."""
        response = client.post("/api/v1/sensitivity_analysis", json=valid_market_context)
        data = response.json()

        best = data["best_case"]
        assert "scenario_name" in best
        assert "scenario_type" in best
        assert "price" in best
        assert "profit" in best
        assert "description" in best

    def test_scenarios_calculated_count(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test scenarios_calculated is 17 (7 + 5 + 5)."""
        response = client.post("/api/v1/sensitivity_analysis", json=valid_market_context)
        data = response.json()

        # 7 elasticity + 5 demand + 5 cost = 17 total
        assert data["scenarios_calculated"] == 17


class TestSensitivityAnalysisPerformance:
    """Performance tests for sensitivity_analysis endpoint (AC: 4)."""

    def test_response_time_under_3_seconds(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test sensitivity analysis completes under 3 seconds (AC: 4).

        Uses ProcessPoolExecutor for true CPU parallelism, running all 17
        scenarios across multiple worker processes. Each process initializes
        its own models, bypassing Python's GIL.

        Typical performance: ~1.3s with 4+ CPU cores.
        """
        # Warm up - first call loads models in worker processes
        client.post("/api/v1/sensitivity_analysis", json=valid_market_context)

        # Measure actual performance
        start = time.perf_counter()
        response = client.post("/api/v1/sensitivity_analysis", json=valid_market_context)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 200
        # AC4: Response time < 3 seconds
        assert elapsed_ms < 3000, f"Response took {elapsed_ms:.2f}ms, expected < 3000ms"

    def test_processing_time_reported(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test processing_time_ms is included in response."""
        response = client.post("/api/v1/sensitivity_analysis", json=valid_market_context)
        data = response.json()

        assert "processing_time_ms" in data
        assert isinstance(data["processing_time_ms"], (int, float))
        assert data["processing_time_ms"] > 0


class TestSensitivityAnalysisValidation:
    """Tests for input validation on sensitivity_analysis endpoint."""

    def test_invalid_location_category(self, client: TestClient) -> None:
        """Test 422 returned for invalid location category."""
        invalid_context = {
            "number_of_riders": 50,
            "number_of_drivers": 25,
            "location_category": "InvalidLocation",
            "customer_loyalty_status": "Gold",
            "number_of_past_rides": 20,
            "average_ratings": 4.5,
            "time_of_booking": "Evening",
            "vehicle_type": "Premium",
            "expected_ride_duration": 30,
            "historical_cost_of_ride": 35.0,
        }

        response = client.post("/api/v1/sensitivity_analysis", json=invalid_context)
        assert response.status_code == 422

    def test_missing_required_field(self, client: TestClient) -> None:
        """Test 422 returned for missing required field."""
        incomplete_context = {
            "number_of_riders": 50,
            "number_of_drivers": 25,
        }

        response = client.post("/api/v1/sensitivity_analysis", json=incomplete_context)
        assert response.status_code == 422


class TestSensitivityAnalysisSwagger:
    """Tests for Swagger documentation (AC: 5)."""

    def test_openapi_schema_includes_endpoint(self, client: TestClient) -> None:
        """Test sensitivity_analysis endpoint is documented in OpenAPI schema."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        paths = schema.get("paths", {})

        assert "/api/v1/sensitivity_analysis" in paths
        assert "post" in paths["/api/v1/sensitivity_analysis"]

    def test_openapi_has_request_body_schema(self, client: TestClient) -> None:
        """Test OpenAPI includes request body schema."""
        response = client.get("/openapi.json")
        schema = response.json()

        endpoint = schema["paths"]["/api/v1/sensitivity_analysis"]["post"]
        assert "requestBody" in endpoint

    def test_openapi_has_response_schema(self, client: TestClient) -> None:
        """Test OpenAPI includes response schema."""
        response = client.get("/openapi.json")
        schema = response.json()

        endpoint = schema["paths"]["/api/v1/sensitivity_analysis"]["post"]
        assert "responses" in endpoint
        assert "200" in endpoint["responses"]

    def test_openapi_has_detailed_description(self, client: TestClient) -> None:
        """Test OpenAPI includes detailed description for chart integration."""
        response = client.get("/openapi.json")
        schema = response.json()

        endpoint = schema["paths"]["/api/v1/sensitivity_analysis"]["post"]
        assert "description" in endpoint
        # Should mention chart/Recharts
        description = endpoint["description"].lower()
        assert "chart" in description or "recharts" in description


class TestSensitivityAnalysisChartReadiness:
    """Tests for chart-ready response format."""

    def test_elasticity_points_have_sequential_modifiers(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test elasticity points span from 0.7 to 1.3."""
        response = client.post("/api/v1/sensitivity_analysis", json=valid_market_context)
        data = response.json()

        modifiers = [p["x"] for p in data["elasticity_sensitivity"]]

        # Should include base (1.0) and range from 0.7 to 1.3
        assert min(modifiers) == 0.7
        assert max(modifiers) == 1.3
        assert 1.0 in modifiers

    def test_labels_are_human_readable(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test labels are human-readable percentage strings."""
        response = client.post("/api/v1/sensitivity_analysis", json=valid_market_context)
        data = response.json()

        labels = [p["label"] for p in data["elasticity_sensitivity"]]

        # Should have Base and percentage labels
        assert "Base" in labels
        assert any("%" in label for label in labels)

    def test_worst_case_has_lower_profit_than_best_case(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test worst_case profit is less than best_case profit."""
        response = client.post("/api/v1/sensitivity_analysis", json=valid_market_context)
        data = response.json()

        assert data["worst_case"]["profit"] <= data["best_case"]["profit"]
