"""Integration tests for CORS configuration."""

from fastapi.testclient import TestClient


def test_cors_allows_localhost_origin(client: TestClient) -> None:
    """Test CORS allows requests from localhost:3000."""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    # OPTIONS request should succeed
    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"


def test_cors_headers_on_get_request(client: TestClient) -> None:
    """Test CORS headers are present on regular GET requests."""
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"


def test_cors_allows_credentials(client: TestClient) -> None:
    """Test CORS allows credentials."""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers["Access-Control-Allow-Credentials"] == "true"


def test_cors_allows_all_methods(client: TestClient) -> None:
    """Test CORS allows all HTTP methods."""
    for method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": method,
            },
        )
        assert response.status_code == 200

