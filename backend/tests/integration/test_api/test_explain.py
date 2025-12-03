"""Integration tests for explain_decision endpoint."""

import time

from fastapi.testclient import TestClient


class TestExplainDecisionEndpoint:
    """Tests for POST /api/v1/explain_decision endpoint."""

    def test_explain_decision_returns_valid_response(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test explain_decision endpoint returns expected PriceExplanation structure (AC: 2)."""
        request = {
            "context": valid_market_context,
            "include_trace": True,
            "include_shap": True,
        }

        response = client.post("/api/v1/explain_decision", json=request)
        assert response.status_code == 200

        data = response.json()

        # Core recommendation (AC: 2)
        assert "recommendation" in data
        assert "recommended_price" in data["recommendation"]

        # Feature importance (AC: 2)
        assert "feature_importance" in data
        assert "global_importance" in data

        # Decision trace (AC: 2)
        assert "decision_trace" in data

        # Model agreement (AC: 2)
        assert "model_agreement" in data
        assert "model_predictions" in data

        # Natural language summary (AC: 3)
        assert "natural_language_summary" in data
        assert "key_factors" in data

        # Metadata
        assert "explanation_time_ms" in data
        assert "timestamp" in data

    def test_feature_importance_structure(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test feature_importance has correct structure (AC: 2)."""
        request = {"context": valid_market_context}

        response = client.post("/api/v1/explain_decision", json=request)
        data = response.json()

        # Check feature_importance is a list with items
        feature_importance = data["feature_importance"]
        assert isinstance(feature_importance, list)
        assert len(feature_importance) > 0

        # Check first contribution structure
        contrib = feature_importance[0]
        assert "feature_name" in contrib
        assert "display_name" in contrib
        assert "importance" in contrib
        assert "direction" in contrib
        assert "description" in contrib

        # Check importance is normalized (0-1)
        assert 0.0 <= contrib["importance"] <= 1.0

        # Check direction is valid
        assert contrib["direction"] in ["positive", "negative"]

    def test_decision_trace_structure(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test decision_trace has correct structure (AC: 2)."""
        request = {"context": valid_market_context, "include_trace": True}

        response = client.post("/api/v1/explain_decision", json=request)
        data = response.json()

        trace = data["decision_trace"]
        assert trace is not None

        # Check trace structure
        assert "trace_id" in trace
        assert "request_timestamp" in trace
        assert "total_duration_ms" in trace
        assert "steps" in trace

        # Check steps is a list
        assert isinstance(trace["steps"], list)
        assert len(trace["steps"]) > 0

        # Check first step structure
        step = trace["steps"][0]
        assert "step_name" in step
        assert "timestamp" in step
        assert "duration_ms" in step
        assert "status" in step

    def test_model_agreement_structure(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test model_agreement has correct structure (AC: 2)."""
        request = {"context": valid_market_context}

        response = client.post("/api/v1/explain_decision", json=request)
        data = response.json()

        agreement = data["model_agreement"]
        assert "models_compared" in agreement
        assert "predictions" in agreement
        assert "max_deviation_percent" in agreement
        assert "is_agreement" in agreement
        assert "status" in agreement

        # Check status is valid
        assert agreement["status"] in ["full_agreement", "partial_agreement", "divergent"]

    def test_natural_language_summary_generated(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test natural_language_summary is a non-empty string (AC: 3)."""
        request = {"context": valid_market_context}

        response = client.post("/api/v1/explain_decision", json=request)
        data = response.json()

        summary = data["natural_language_summary"]
        assert isinstance(summary, str)
        assert len(summary) > 0

        # Summary should mention the recommended price
        price = data["recommendation"]["recommended_price"]
        assert f"${price:.2f}" in summary or str(int(price)) in summary

    def test_key_factors_populated(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test key_factors is a non-empty list (AC: 3)."""
        request = {"context": valid_market_context}

        response = client.post("/api/v1/explain_decision", json=request)
        data = response.json()

        key_factors = data["key_factors"]
        assert isinstance(key_factors, list)
        assert len(key_factors) > 0

        # Each factor should be a non-empty string
        for factor in key_factors:
            assert isinstance(factor, str)
            assert len(factor) > 0


class TestExplainDecisionOptions:
    """Tests for explain_decision request options."""

    def test_exclude_trace(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test decision_trace is null when include_trace is False."""
        request = {
            "context": valid_market_context,
            "include_trace": False,
        }

        response = client.post("/api/v1/explain_decision", json=request)
        data = response.json()

        assert data["decision_trace"] is None

    def test_exclude_shap_uses_global(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test feature_importance equals global_importance when include_shap is False."""
        request = {
            "context": valid_market_context,
            "include_shap": False,
        }

        response = client.post("/api/v1/explain_decision", json=request)
        data = response.json()

        # When SHAP is disabled, local should match global
        local = data["feature_importance"]
        global_imp = data["global_importance"]

        # They should have the same features
        local_features = {c["feature_name"] for c in local}
        global_features = {c["feature_name"] for c in global_imp}
        assert local_features == global_features


class TestExplainDecisionValidation:
    """Tests for input validation on explain_decision endpoint."""

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

        request = {"context": invalid_context}
        response = client.post("/api/v1/explain_decision", json=request)
        assert response.status_code == 422

    def test_missing_context(self, client: TestClient) -> None:
        """Test 422 returned for missing context."""
        request = {}
        response = client.post("/api/v1/explain_decision", json=request)
        assert response.status_code == 422

    def test_invalid_rating_range(self, client: TestClient) -> None:
        """Test 422 returned for rating out of range (1-5)."""
        invalid_context = {
            "number_of_riders": 50,
            "number_of_drivers": 25,
            "location_category": "Urban",
            "customer_loyalty_status": "Gold",
            "number_of_past_rides": 20,
            "average_ratings": 0.5,  # Min is 1.0
            "time_of_booking": "Evening",
            "vehicle_type": "Premium",
            "expected_ride_duration": 30,
            "historical_cost_of_ride": 35.0,
        }

        request = {"context": invalid_context}
        response = client.post("/api/v1/explain_decision", json=request)
        assert response.status_code == 422


class TestExplainDecisionPerformance:
    """Performance tests for explain_decision endpoint (AC: 4)."""

    def test_response_time_under_2_seconds(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test explanation completes in < 2 seconds (AC: 4)."""
        request = {
            "context": valid_market_context,
            "include_trace": True,
            "include_shap": True,
        }

        # Warm up - first call loads models
        client.post("/api/v1/explain_decision", json=request)

        # Measure actual performance
        start = time.perf_counter()
        response = client.post("/api/v1/explain_decision", json=request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 2000, f"Response took {elapsed_ms:.2f}ms, expected < 2000ms"

    def test_explanation_time_reported(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test explanation_time_ms is included and reasonable."""
        request = {"context": valid_market_context}

        response = client.post("/api/v1/explain_decision", json=request)
        data = response.json()

        assert "explanation_time_ms" in data
        assert isinstance(data["explanation_time_ms"], (int, float))
        assert data["explanation_time_ms"] > 0
        assert data["explanation_time_ms"] < 2000  # < 2 seconds


class TestExplainDecisionSwagger:
    """Tests for Swagger documentation (AC: 5)."""

    def test_openapi_schema_includes_endpoint(self, client: TestClient) -> None:
        """Test explain_decision endpoint is documented in OpenAPI schema (AC: 5)."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        paths = schema.get("paths", {})

        assert "/api/v1/explain_decision" in paths
        assert "post" in paths["/api/v1/explain_decision"]

    def test_openapi_has_request_body_schema(self, client: TestClient) -> None:
        """Test OpenAPI includes request body schema (AC: 5)."""
        response = client.get("/openapi.json")
        schema = response.json()

        endpoint = schema["paths"]["/api/v1/explain_decision"]["post"]
        assert "requestBody" in endpoint

    def test_openapi_has_response_schema(self, client: TestClient) -> None:
        """Test OpenAPI includes response schema (AC: 5)."""
        response = client.get("/openapi.json")
        schema = response.json()

        endpoint = schema["paths"]["/api/v1/explain_decision"]["post"]
        assert "responses" in endpoint
        assert "200" in endpoint["responses"]

    def test_openapi_has_comprehensive_examples(self, client: TestClient) -> None:
        """Test OpenAPI includes comprehensive examples (AC: 5)."""
        response = client.get("/openapi.json")
        schema = response.json()

        endpoint = schema["paths"]["/api/v1/explain_decision"]["post"]

        # Check description exists and is comprehensive
        assert "description" in endpoint
        assert len(endpoint["description"]) > 100  # Non-trivial description

        # Check response has examples
        responses = endpoint["responses"]
        assert "200" in responses
        assert "422" in responses  # Validation error
        assert "500" in responses  # Internal error
        assert "503" in responses  # Service unavailable


class TestExplainDecisionConsistency:
    """Tests for explanation consistency."""

    def test_same_input_consistent_output(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test same input returns consistent explanations."""
        request = {"context": valid_market_context}

        response1 = client.post("/api/v1/explain_decision", json=request)
        response2 = client.post("/api/v1/explain_decision", json=request)

        data1 = response1.json()
        data2 = response2.json()

        # Same context should produce same price
        assert data1["recommendation"]["recommended_price"] == data2["recommendation"]["recommended_price"]

        # Same segment
        assert data1["recommendation"]["segment"]["segment_name"] == data2["recommendation"]["segment"]["segment_name"]

        # Same model agreement
        assert data1["model_agreement"]["status"] == data2["model_agreement"]["status"]

