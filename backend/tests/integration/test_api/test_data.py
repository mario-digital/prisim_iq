"""Integration tests for data endpoints."""

from fastapi.testclient import TestClient


def test_data_summary_returns_valid_response(client: TestClient) -> None:
    """Test data summary endpoint returns expected structure."""
    response = client.get("/api/v1/data/summary")
    assert response.status_code == 200

    data = response.json()
    assert "row_count" in data
    assert "column_count" in data
    assert "segments" in data
    assert "price_range" in data


def test_data_summary_row_count_is_positive(client: TestClient) -> None:
    """Test data summary returns positive row count."""
    response = client.get("/api/v1/data/summary")
    data = response.json()
    assert data["row_count"] > 0


def test_data_summary_has_segments(client: TestClient) -> None:
    """Test data summary returns list of segments."""
    response = client.get("/api/v1/data/summary")
    data = response.json()

    segments = data["segments"]
    assert isinstance(segments, list)
    assert len(segments) > 0
    # All segments should be strings
    assert all(isinstance(s, str) for s in segments)


def test_data_summary_price_range_valid(client: TestClient) -> None:
    """Test data summary returns valid price range."""
    response = client.get("/api/v1/data/summary")
    data = response.json()

    price_range = data["price_range"]
    assert "min" in price_range
    assert "max" in price_range
    assert price_range["min"] < price_range["max"]
    assert price_range["min"] >= 0


def test_data_summary_includes_timing_header(client: TestClient) -> None:
    """Test data summary response includes X-Process-Time header."""
    response = client.get("/api/v1/data/summary")
    assert "X-Process-Time" in response.headers

