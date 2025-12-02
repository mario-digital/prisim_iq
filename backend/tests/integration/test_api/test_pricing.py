"""Integration tests for pricing optimization endpoint."""

import time

from fastapi.testclient import TestClient


class TestOptimizePriceEndpoint:
    """Tests for POST /api/v1/optimize_price endpoint."""

    def test_optimize_price_returns_valid_response(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test optimize_price endpoint returns expected PricingResult structure."""
        response = client.post("/api/v1/optimize_price", json=valid_market_context)
        assert response.status_code == 200

        data = response.json()

        # Core recommendation fields (AC: 2)
        assert "recommended_price" in data
        assert "confidence_score" in data
        assert "expected_profit" in data
        assert "profit_uplift_percent" in data

        # Segment and model info (AC: 3)
        assert "segment" in data
        assert "model_used" in data

        # Business rules (AC: 4)
        assert "rules_applied" in data
        assert "price_before_rules" in data

        # Visualization data
        assert "price_demand_curve" in data

        # Metadata
        assert "processing_time_ms" in data
        assert "timestamp" in data

    def test_recommended_price_positive(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test recommended price is a positive number."""
        response = client.post("/api/v1/optimize_price", json=valid_market_context)
        data = response.json()

        assert isinstance(data["recommended_price"], (int, float))
        assert data["recommended_price"] > 0

    def test_confidence_score_in_range(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test confidence score is between 0 and 1."""
        response = client.post("/api/v1/optimize_price", json=valid_market_context)
        data = response.json()

        assert isinstance(data["confidence_score"], float)
        assert 0.0 <= data["confidence_score"] <= 1.0

    def test_expected_profit_and_uplift(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test profit metrics are present and valid."""
        response = client.post("/api/v1/optimize_price", json=valid_market_context)
        data = response.json()

        assert isinstance(data["expected_profit"], (int, float))
        assert isinstance(data["baseline_profit"], (int, float))
        assert isinstance(data["profit_uplift_percent"], (int, float))

    def test_segment_details_complete(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test segment information is complete (AC: 3)."""
        response = client.post("/api/v1/optimize_price", json=valid_market_context)
        data = response.json()

        segment = data["segment"]
        assert "segment_name" in segment
        assert "cluster_id" in segment
        assert "characteristics" in segment
        assert "centroid_distance" in segment
        assert "human_readable_description" in segment
        assert "confidence_level" in segment

    def test_model_used_is_xgboost(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test model used is xgboost (primary model)."""
        response = client.post("/api/v1/optimize_price", json=valid_market_context)
        data = response.json()

        assert data["model_used"] == "xgboost"

    def test_rules_applied_structure(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test rules_applied has correct structure (AC: 4)."""
        response = client.post("/api/v1/optimize_price", json=valid_market_context)
        data = response.json()

        rules_applied = data["rules_applied"]
        assert isinstance(rules_applied, list)

        # If rules were applied, check structure
        if len(rules_applied) > 0:
            rule = rules_applied[0]
            assert "rule_id" in rule
            assert "rule_name" in rule
            assert "price_before" in rule
            assert "price_after" in rule
            assert "impact" in rule
            assert "impact_percent" in rule

    def test_price_demand_curve_structure(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test price_demand_curve has correct structure."""
        response = client.post("/api/v1/optimize_price", json=valid_market_context)
        data = response.json()

        curve = data["price_demand_curve"]
        assert isinstance(curve, list)
        assert len(curve) > 0

        # Check first point structure
        point = curve[0]
        assert "price" in point
        assert "demand" in point
        assert "profit" in point


class TestOptimizePriceValidation:
    """Tests for input validation on optimize_price endpoint (AC: 6)."""

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

        response = client.post("/api/v1/optimize_price", json=invalid_context)
        assert response.status_code == 422

    def test_invalid_riders_range(self, client: TestClient) -> None:
        """Test 422 returned for riders out of range."""
        invalid_context = {
            "number_of_riders": 200,  # Max is 100
            "number_of_drivers": 25,
            "location_category": "Urban",
            "customer_loyalty_status": "Gold",
            "number_of_past_rides": 20,
            "average_ratings": 4.5,
            "time_of_booking": "Evening",
            "vehicle_type": "Premium",
            "expected_ride_duration": 30,
            "historical_cost_of_ride": 35.0,
        }

        response = client.post("/api/v1/optimize_price", json=invalid_context)
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

        response = client.post("/api/v1/optimize_price", json=invalid_context)
        assert response.status_code == 422

    def test_missing_required_field(self, client: TestClient) -> None:
        """Test 422 returned for missing required field."""
        incomplete_context = {
            "number_of_riders": 50,
            "number_of_drivers": 25,
            # Missing other required fields
        }

        response = client.post("/api/v1/optimize_price", json=incomplete_context)
        assert response.status_code == 422

    def test_extra_fields_rejected(self, client: TestClient) -> None:
        """Test 422 returned for extra fields (extra=forbid)."""
        context_with_extra = {
            "number_of_riders": 50,
            "number_of_drivers": 25,
            "location_category": "Urban",
            "customer_loyalty_status": "Gold",
            "number_of_past_rides": 20,
            "average_ratings": 4.5,
            "time_of_booking": "Evening",
            "vehicle_type": "Premium",
            "expected_ride_duration": 30,
            "historical_cost_of_ride": 35.0,
            "extra_field": "should_fail",
        }

        response = client.post("/api/v1/optimize_price", json=context_with_extra)
        assert response.status_code == 422


class TestOptimizePricePerformance:
    """Performance tests for optimize_price endpoint (AC: 5)."""

    def test_response_time_under_3_seconds(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test optimization completes in < 3 seconds (AC: 5)."""
        # Warm up - first call loads models
        client.post("/api/v1/optimize_price", json=valid_market_context)

        # Measure actual performance
        start = time.perf_counter()
        response = client.post("/api/v1/optimize_price", json=valid_market_context)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 3000, f"Response took {elapsed_ms:.2f}ms, expected < 3000ms"

    def test_processing_time_reported(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test processing_time_ms is included in response."""
        response = client.post("/api/v1/optimize_price", json=valid_market_context)
        data = response.json()

        assert "processing_time_ms" in data
        assert isinstance(data["processing_time_ms"], (int, float))
        assert data["processing_time_ms"] > 0

    def test_includes_timing_header(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test response includes X-Process-Time header."""
        response = client.post("/api/v1/optimize_price", json=valid_market_context)
        assert "X-Process-Time" in response.headers


class TestOptimizePriceConsistency:
    """Tests for price optimization consistency."""

    def test_same_input_similar_output(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test same input returns consistent recommendations."""
        response1 = client.post("/api/v1/optimize_price", json=valid_market_context)
        response2 = client.post("/api/v1/optimize_price", json=valid_market_context)

        data1 = response1.json()
        data2 = response2.json()

        # Same context should produce same price (deterministic)
        assert data1["recommended_price"] == data2["recommended_price"]
        assert data1["segment"]["segment_name"] == data2["segment"]["segment_name"]
        assert data1["model_used"] == data2["model_used"]

    def test_different_loyalty_different_price(self, client: TestClient) -> None:
        """Test different loyalty tiers may get different prices."""
        bronze_context = {
            "number_of_riders": 50,
            "number_of_drivers": 25,
            "location_category": "Urban",
            "customer_loyalty_status": "Bronze",
            "number_of_past_rides": 2,
            "average_ratings": 4.0,
            "time_of_booking": "Evening",
            "vehicle_type": "Premium",
            "expected_ride_duration": 30,
            "historical_cost_of_ride": 35.0,
        }

        platinum_context = {
            "number_of_riders": 50,
            "number_of_drivers": 25,
            "location_category": "Urban",
            "customer_loyalty_status": "Platinum",
            "number_of_past_rides": 100,
            "average_ratings": 4.9,
            "time_of_booking": "Evening",
            "vehicle_type": "Premium",
            "expected_ride_duration": 30,
            "historical_cost_of_ride": 35.0,
        }

        response_bronze = client.post("/api/v1/optimize_price", json=bronze_context)
        response_platinum = client.post("/api/v1/optimize_price", json=platinum_context)

        assert response_bronze.status_code == 200
        assert response_platinum.status_code == 200

        data_bronze = response_bronze.json()
        data_platinum = response_platinum.json()

        # Platinum should get a discount (lower or equal price)
        assert data_platinum["recommended_price"] <= data_bronze["recommended_price"]


class TestOptimizePriceSwagger:
    """Tests for Swagger documentation (AC: 7)."""

    def test_openapi_schema_includes_endpoint(self, client: TestClient) -> None:
        """Test optimize_price endpoint is documented in OpenAPI schema."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        paths = schema.get("paths", {})

        assert "/api/v1/optimize_price" in paths
        assert "post" in paths["/api/v1/optimize_price"]

    def test_openapi_has_request_body_schema(self, client: TestClient) -> None:
        """Test OpenAPI includes request body schema."""
        response = client.get("/openapi.json")
        schema = response.json()

        endpoint = schema["paths"]["/api/v1/optimize_price"]["post"]
        assert "requestBody" in endpoint

    def test_openapi_has_response_schema(self, client: TestClient) -> None:
        """Test OpenAPI includes response schema."""
        response = client.get("/openapi.json")
        schema = response.json()

        endpoint = schema["paths"]["/api/v1/optimize_price"]["post"]
        assert "responses" in endpoint
        assert "200" in endpoint["responses"]

