"""Tests for health check endpoint."""

from fastapi.testclient import TestClient


def test_health_check_returns_healthy(client: TestClient) -> None:
    """Test that health endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_health_check_version_format(client: TestClient) -> None:
    """Test that health endpoint returns valid version format."""
    response = client.get("/health")
    data = response.json()
    # Version should be semantic versioning format
    assert data["version"] == "1.0.0"


def test_root_endpoint(client: TestClient) -> None:
    """Test that root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "PrismIQ"
    assert "version" in data
    assert data["docs"] == "/docs"

