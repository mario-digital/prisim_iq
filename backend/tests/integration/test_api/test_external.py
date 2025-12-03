"""Integration tests for external data API endpoints."""

from fastapi.testclient import TestClient


def test_external_context_endpoint_exists(client: TestClient) -> None:
    """Test external context endpoint is accessible (AC: 8)."""
    response = client.get("/api/v1/external/context")
    assert response.status_code == 200


def test_external_context_returns_valid_structure(client: TestClient) -> None:
    """Test external context returns expected structure (AC: 8)."""
    response = client.get("/api/v1/external/context")
    data = response.json()

    assert "context" in data
    assert "cache_status" in data
    assert "explanation" in data

    # Context should have fuel, weather, events
    context = data["context"]
    assert "fuel" in context
    assert "weather" in context
    assert "events" in context
    assert "last_updated" in context


def test_external_context_cache_status_structure(client: TestClient) -> None:
    """Test cache status includes all data types (AC: 8)."""
    response = client.get("/api/v1/external/context")
    data = response.json()

    cache_status = data["cache_status"]
    assert "fuel" in cache_status
    assert "weather" in cache_status
    assert "events" in cache_status

    for status in cache_status.values():
        assert "age_seconds" in status
        assert "is_fresh" in status


def test_fuel_webhook_endpoint_exists(client: TestClient) -> None:
    """Test fuel webhook endpoint is accessible (AC: 5)."""
    payload = {"price_per_gallon": 3.75, "change_percent": 2.5}
    response = client.post("/api/v1/external/webhook/fuel", json=payload)
    assert response.status_code == 200


def test_fuel_webhook_returns_fuel_data(client: TestClient) -> None:
    """Test fuel webhook returns processed fuel data (AC: 2)."""
    payload = {"price_per_gallon": 3.89, "change_percent": 3.5, "source": "test"}
    response = client.post("/api/v1/external/webhook/fuel", json=payload)
    data = response.json()

    assert data["price_per_gallon"] == 3.89
    assert data["change_percent"] == 3.5
    assert data["source"] == "test"
    assert "fetched_at" in data


def test_weather_webhook_endpoint_exists(client: TestClient) -> None:
    """Test weather webhook endpoint is accessible (AC: 5)."""
    payload = {"condition": "rainy", "temperature_f": 65.0}
    response = client.post("/api/v1/external/webhook/weather", json=payload)
    assert response.status_code == 200


def test_weather_webhook_calculates_modifier(client: TestClient) -> None:
    """Test weather webhook calculates correct demand modifier (AC: 3)."""
    # Test rainy condition
    payload = {"condition": "rainy", "temperature_f": 65.0}
    response = client.post("/api/v1/external/webhook/weather", json=payload)
    data = response.json()

    assert data["condition"] == "rainy"
    assert data["demand_modifier"] == 1.15  # Rainy = +15%


def test_weather_webhook_snowy_modifier(client: TestClient) -> None:
    """Test snowy weather has +30% modifier (AC: 3)."""
    payload = {"condition": "snowy", "temperature_f": 28.0}
    response = client.post("/api/v1/external/webhook/weather", json=payload)
    data = response.json()

    assert data["condition"] == "snowy"
    assert data["demand_modifier"] == 1.30  # Snowy = +30%


def test_events_webhook_endpoint_exists(client: TestClient) -> None:
    """Test events webhook endpoint is accessible (AC: 5)."""
    payload = {"events": []}
    response = client.post("/api/v1/external/webhook/events", json=payload)
    assert response.status_code == 200


def test_events_webhook_processes_events(client: TestClient) -> None:
    """Test events webhook processes event list correctly (AC: 4)."""
    payload = {
        "events": [
            {
                "name": "Rock Concert",
                "type": "concert",
                "venue": "City Arena",
                "start_time": "2024-12-15T19:00:00",
            }
        ]
    }
    response = client.post("/api/v1/external/webhook/events", json=payload)
    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Rock Concert"
    assert data[0]["type"] == "concert"
    assert data[0]["surge_modifier"] == 1.20  # Concert = +20%


def test_events_webhook_sports_modifier(client: TestClient) -> None:
    """Test sports events have +25% surge (AC: 4)."""
    payload = {
        "events": [
            {
                "name": "Football Game",
                "type": "sports",
                "venue": "Stadium",
                "start_time": "2024-12-15T18:00:00",
            }
        ]
    }
    response = client.post("/api/v1/external/webhook/events", json=payload)
    data = response.json()

    assert data[0]["surge_modifier"] == 1.25  # Sports = +25%


def test_events_webhook_convention_modifier(client: TestClient) -> None:
    """Test convention events have +15% surge (AC: 4)."""
    payload = {
        "events": [
            {
                "name": "Tech Conference",
                "type": "convention",
                "venue": "Convention Center",
                "start_time": "2024-12-15T09:00:00",
            }
        ]
    }
    response = client.post("/api/v1/external/webhook/events", json=payload)
    data = response.json()

    assert data[0]["surge_modifier"] == 1.15  # Convention = +15%


def test_external_context_includes_timing_header(client: TestClient) -> None:
    """Test external context response includes timing header."""
    response = client.get("/api/v1/external/context")
    assert "X-Process-Time" in response.headers


def test_fuel_webhook_persists_to_context(client: TestClient) -> None:
    """Test fuel webhook data appears in external context."""
    # Post fuel data
    fuel_payload = {"price_per_gallon": 4.25, "change_percent": 5.0}
    client.post("/api/v1/external/webhook/fuel", json=fuel_payload)

    # Get context
    response = client.get("/api/v1/external/context")
    data = response.json()

    assert data["context"]["fuel"]["price_per_gallon"] == 4.25


def test_weather_webhook_persists_to_context(client: TestClient) -> None:
    """Test weather webhook data appears in external context."""
    # Post weather data
    weather_payload = {"condition": "snowy", "temperature_f": 30.0}
    client.post("/api/v1/external/webhook/weather", json=weather_payload)

    # Get context
    response = client.get("/api/v1/external/context")
    data = response.json()

    assert data["context"]["weather"]["condition"] == "snowy"
    assert data["context"]["weather"]["demand_modifier"] == 1.30


def test_external_context_explanation_populated(client: TestClient) -> None:
    """Test external context includes natural language explanation (AC: 9)."""
    # Add weather data for explanation
    weather_payload = {"condition": "rainy", "temperature_f": 60.0}
    client.post("/api/v1/external/webhook/weather", json=weather_payload)

    response = client.get("/api/v1/external/context")
    data = response.json()

    assert len(data["explanation"]) > 0
    assert "rainy" in data["explanation"].lower() or "weather" in data["explanation"].lower()
