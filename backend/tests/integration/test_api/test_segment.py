"""Integration tests for segment endpoint."""

import time

import pytest
from fastapi.testclient import TestClient


class TestSegmentEndpoint:
    """Tests for POST /api/v1/data/segment endpoint."""

    def test_segment_returns_valid_response(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test segment endpoint returns expected SegmentDetails structure."""
        response = client.post("/api/v1/data/segment", json=valid_market_context)
        assert response.status_code == 200

        data = response.json()
        assert "segment_name" in data
        assert "cluster_id" in data
        assert "characteristics" in data
        assert "centroid_distance" in data
        assert "human_readable_description" in data
        assert "confidence_level" in data

    def test_segment_name_format(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test segment name follows expected format."""
        response = client.post("/api/v1/data/segment", json=valid_market_context)
        data = response.json()

        # Segment name should be Location_TimeProfile_Vehicle format
        segment_name = data["segment_name"]
        assert isinstance(segment_name, str)
        parts = segment_name.split("_")
        assert len(parts) >= 2, f"Expected format Location_TimeProfile_Vehicle, got {segment_name}"

    def test_cluster_id_valid_range(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test cluster ID is in valid range (0-5 for 6 clusters)."""
        response = client.post("/api/v1/data/segment", json=valid_market_context)
        data = response.json()

        assert isinstance(data["cluster_id"], int)
        assert 0 <= data["cluster_id"] < 6

    def test_centroid_distance_positive(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test centroid distance is a positive float."""
        response = client.post("/api/v1/data/segment", json=valid_market_context)
        data = response.json()

        assert isinstance(data["centroid_distance"], float)
        assert data["centroid_distance"] >= 0

    def test_confidence_level_valid(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test confidence level is one of high/medium/low."""
        response = client.post("/api/v1/data/segment", json=valid_market_context)
        data = response.json()

        assert data["confidence_level"] in ["high", "medium", "low"]

    def test_human_readable_description_not_empty(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test human-readable description is present and meaningful."""
        response = client.post("/api/v1/data/segment", json=valid_market_context)
        data = response.json()

        description = data["human_readable_description"]
        assert isinstance(description, str)
        assert len(description) > 10  # Should be a sentence, not just a word

    def test_characteristics_structure(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test characteristics dict contains expected keys."""
        response = client.post("/api/v1/data/segment", json=valid_market_context)
        data = response.json()

        characteristics = data["characteristics"]
        assert isinstance(characteristics, dict)
        # Should have at least some characteristics
        assert len(characteristics) > 0


class TestSegmentValidation:
    """Tests for input validation on segment endpoint."""

    def test_invalid_location_category(self, client: TestClient) -> None:
        """Test 422 returned for invalid location category."""
        invalid_context = {
            "number_of_riders": 50,
            "number_of_drivers": 25,
            "location_category": "InvalidLocation",  # Invalid
            "customer_loyalty_status": "Gold",
            "number_of_past_rides": 20,
            "average_ratings": 4.5,
            "time_of_booking": "Evening",
            "vehicle_type": "Premium",
            "expected_ride_duration": 30,
            "historical_cost_of_ride": 35.0,
        }

        response = client.post("/api/v1/data/segment", json=invalid_context)
        assert response.status_code == 422

        detail = response.json()["detail"]
        assert any("location_category" in str(err) for err in detail)

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

        response = client.post("/api/v1/data/segment", json=invalid_context)
        assert response.status_code == 422

    def test_invalid_rating_range(self, client: TestClient) -> None:
        """Test 422 returned for rating out of range (1-5)."""
        invalid_context = {
            "number_of_riders": 50,
            "number_of_drivers": 25,
            "location_category": "Urban",
            "customer_loyalty_status": "Gold",
            "number_of_past_rides": 20,
            "average_ratings": 6.0,  # Max is 5.0
            "time_of_booking": "Evening",
            "vehicle_type": "Premium",
            "expected_ride_duration": 30,
            "historical_cost_of_ride": 35.0,
        }

        response = client.post("/api/v1/data/segment", json=invalid_context)
        assert response.status_code == 422

    def test_missing_required_field(self, client: TestClient) -> None:
        """Test 422 returned for missing required field."""
        incomplete_context = {
            "number_of_riders": 50,
            "number_of_drivers": 25,
            # Missing location_category and other required fields
        }

        response = client.post("/api/v1/data/segment", json=incomplete_context)
        assert response.status_code == 422

    def test_invalid_loyalty_status(self, client: TestClient) -> None:
        """Test 422 returned for invalid loyalty status."""
        invalid_context = {
            "number_of_riders": 50,
            "number_of_drivers": 25,
            "location_category": "Urban",
            "customer_loyalty_status": "Diamond",  # Not a valid tier
            "number_of_past_rides": 20,
            "average_ratings": 4.5,
            "time_of_booking": "Evening",
            "vehicle_type": "Premium",
            "expected_ride_duration": 30,
            "historical_cost_of_ride": 35.0,
        }

        response = client.post("/api/v1/data/segment", json=invalid_context)
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
            "extra_field": "should_fail",  # Extra field
        }

        response = client.post("/api/v1/data/segment", json=context_with_extra)
        assert response.status_code == 422


class TestSegmentPerformance:
    """Performance tests for segment endpoint."""

    def test_response_time_under_100ms(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test classification completes in < 100ms (AC: 6)."""
        # Warm up the model (first call may be slower due to loading)
        client.post("/api/v1/data/segment", json=valid_market_context)

        # Measure actual performance
        start = time.perf_counter()
        response = client.post("/api/v1/data/segment", json=valid_market_context)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 100, f"Response took {elapsed_ms:.2f}ms, expected < 100ms"

    def test_includes_timing_header(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test response includes X-Process-Time header."""
        response = client.post("/api/v1/data/segment", json=valid_market_context)
        assert "X-Process-Time" in response.headers


class TestSegmentConsistency:
    """Tests for segment classification consistency."""

    def test_same_input_same_output(
        self,
        client: TestClient,
        valid_market_context: dict,
    ) -> None:
        """Test same input always returns same segment."""
        response1 = client.post("/api/v1/data/segment", json=valid_market_context)
        response2 = client.post("/api/v1/data/segment", json=valid_market_context)

        data1 = response1.json()
        data2 = response2.json()

        assert data1["cluster_id"] == data2["cluster_id"]
        assert data1["segment_name"] == data2["segment_name"]
        assert data1["centroid_distance"] == pytest.approx(data2["centroid_distance"])

    def test_different_inputs_may_differ(self, client: TestClient) -> None:
        """Test different inputs can get different segments."""
        high_demand_context = {
            "number_of_riders": 100,
            "number_of_drivers": 20,  # Low supply ratio
            "location_category": "Urban",
            "customer_loyalty_status": "Platinum",
            "number_of_past_rides": 100,
            "average_ratings": 4.9,
            "time_of_booking": "Morning",
            "vehicle_type": "Premium",
            "expected_ride_duration": 45,
            "historical_cost_of_ride": 75.0,
        }

        low_demand_context = {
            "number_of_riders": 10,
            "number_of_drivers": 50,  # High supply ratio
            "location_category": "Rural",
            "customer_loyalty_status": "Bronze",
            "number_of_past_rides": 2,
            "average_ratings": 3.5,
            "time_of_booking": "Afternoon",
            "vehicle_type": "Economy",
            "expected_ride_duration": 15,
            "historical_cost_of_ride": 12.0,
        }

        response1 = client.post("/api/v1/data/segment", json=high_demand_context)
        response2 = client.post("/api/v1/data/segment", json=low_demand_context)

        # Both should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200

        # Results should have valid structure
        data1 = response1.json()
        data2 = response2.json()
        assert "segment_name" in data1
        assert "segment_name" in data2

