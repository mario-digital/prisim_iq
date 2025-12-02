"""Pytest configuration and fixtures for PrismIQ backend tests."""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.ml.preprocessor import load_dataset
from src.ml.segmenter import DEFAULT_MODEL_PATH, Segmenter


@pytest.fixture(scope="session", autouse=True)
def ensure_segmenter_model() -> None:
    """Ensure segmenter model exists before running tests.

    This fixture runs once per test session and trains the model
    if it doesn't exist.
    """
    if not DEFAULT_MODEL_PATH.exists():
        df = load_dataset()
        segmenter = Segmenter(n_clusters=6, random_state=42)
        segmenter.fit(df)
        segmenter.save(DEFAULT_MODEL_PATH)


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def valid_market_context() -> dict:
    """Create a valid market context request body."""
    return {
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
    }

