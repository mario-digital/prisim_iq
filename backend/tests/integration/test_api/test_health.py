"""Integration tests for health endpoint."""

from datetime import datetime

from fastapi.testclient import TestClient


def test_health_returns_healthy_status(client: TestClient) -> None:
    """Test health endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data


def test_health_timestamp_is_valid_iso_format(client: TestClient) -> None:
    """Test health endpoint returns valid ISO timestamp."""
    response = client.get("/health")
    data = response.json()

    # Should be parseable as datetime
    timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
    assert timestamp is not None


def test_health_includes_timing_header(client: TestClient) -> None:
    """Test health endpoint response includes X-Process-Time header."""
    response = client.get("/health")
    assert "X-Process-Time" in response.headers
    # Should be a valid float
    process_time = float(response.headers["X-Process-Time"])
    assert process_time >= 0

