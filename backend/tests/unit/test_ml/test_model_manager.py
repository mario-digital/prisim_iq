"""Tests for ML model manager."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from src.ml.model_manager import ModelManager, get_model_manager
from src.ml.training_data import CATEGORICAL_COLUMNS, FEATURE_COLUMNS
from src.schemas.market import MarketContext


@pytest.fixture
def sample_market_context() -> MarketContext:
    """Create sample market context for tests."""
    return MarketContext(
        number_of_riders=50,
        number_of_drivers=25,
        location_category="Urban",
        customer_loyalty_status="Gold",
        number_of_past_rides=20,
        average_ratings=4.5,
        time_of_booking="Evening",
        vehicle_type="Premium",
        expected_ride_duration=30,
        historical_cost_of_ride=35.0,
    )


@pytest.fixture
def trained_models_dir(tmp_path: Path) -> Path:
    """Create directory with mock trained models."""
    # Create mock encoders
    encoders = {}
    for col in CATEGORICAL_COLUMNS:
        encoder = LabelEncoder()
        if col == "location_category":
            encoder.fit(["Urban", "Suburban", "Rural"])
        elif col == "customer_loyalty_status":
            encoder.fit(["Bronze", "Silver", "Gold", "Platinum"])
        elif col == "time_of_booking":
            encoder.fit(["Morning", "Afternoon", "Evening", "Night"])
        elif col == "vehicle_type":
            encoder.fit(["Economy", "Premium"])
        elif col == "segment":
            encoder.fit(["Segment_A", "Segment_B", "Segment_C", "Unknown"])
        encoders[col] = encoder

    # Save encoders
    joblib.dump(encoders, tmp_path / "encoders.joblib")

    # Create and save mock models
    # Simple models that return reasonable values
    np.random.seed(42)
    n_features = len(FEATURE_COLUMNS)

    # Linear regression
    lr = LinearRegression()
    X_dummy = np.random.rand(100, n_features)
    y_dummy = np.random.rand(100)
    lr.fit(X_dummy, y_dummy)
    joblib.dump(lr, tmp_path / "linear_regression.joblib")

    # Decision tree
    dt = DecisionTreeRegressor(max_depth=3, random_state=42)
    dt.fit(X_dummy, y_dummy)
    joblib.dump(dt, tmp_path / "decision_tree.joblib")

    # XGBoost
    xgb = XGBRegressor(max_depth=3, n_estimators=10, random_state=42, verbosity=0)
    xgb.fit(X_dummy, y_dummy)
    joblib.dump(xgb, tmp_path / "xgboost.joblib")

    # Save feature info
    feature_info = {
        "feature_names": FEATURE_COLUMNS,
        "categorical_columns": CATEGORICAL_COLUMNS,
        "target_column": "demand",
    }
    with open(tmp_path / "feature_info.json", "w") as f:
        json.dump(feature_info, f)

    return tmp_path


class TestModelManager:
    """Tests for ModelManager class."""

    def test_manager_initialization(self, tmp_path: Path) -> None:
        """Test ModelManager can be initialized."""
        manager = ModelManager(models_dir=tmp_path)

        assert manager.models_dir == tmp_path
        assert manager.models == {}
        assert manager.encoders == {}
        assert manager._loaded is False

    def test_load_models(self, trained_models_dir: Path) -> None:
        """Test loading models from disk."""
        manager = ModelManager(models_dir=trained_models_dir)
        manager.load_models()

        assert manager._loaded is True
        assert len(manager.models) == 3
        assert "linear_regression" in manager.models
        assert "decision_tree" in manager.models
        assert "xgboost" in manager.models
        assert len(manager.encoders) > 0
        assert len(manager.feature_names) > 0

    def test_load_models_missing_dir(self, tmp_path: Path) -> None:
        """Test loading from empty directory raises error."""
        manager = ModelManager(models_dir=tmp_path)

        with pytest.raises(RuntimeError, match="No models found"):
            manager.load_models()

    def test_predict_default_model(
        self,
        trained_models_dir: Path,
        sample_market_context: MarketContext,
    ) -> None:
        """Test prediction with default XGBoost model."""
        manager = ModelManager(models_dir=trained_models_dir)
        manager.load_models()

        prediction = manager.predict(
            sample_market_context,
            price=35.0,
            segment="Segment_A",
        )

        assert isinstance(prediction, float)
        assert 0.0 <= prediction <= 1.0

    def test_predict_specific_model(
        self,
        trained_models_dir: Path,
        sample_market_context: MarketContext,
    ) -> None:
        """Test prediction with specific model."""
        manager = ModelManager(models_dir=trained_models_dir)
        manager.load_models()

        for model_name in ["linear_regression", "decision_tree", "xgboost"]:
            prediction = manager.predict(
                sample_market_context,
                price=35.0,
                model_name=model_name,  # type: ignore[arg-type]
                segment="Segment_A",
            )

            assert isinstance(prediction, float)
            assert 0.0 <= prediction <= 1.0, f"{model_name} prediction out of range"

    def test_predict_invalid_model(
        self,
        trained_models_dir: Path,
        sample_market_context: MarketContext,
    ) -> None:
        """Test prediction with invalid model raises error."""
        manager = ModelManager(models_dir=trained_models_dir)
        manager.load_models()

        with pytest.raises(ValueError, match="not available"):
            manager.predict(
                sample_market_context,
                price=35.0,
                model_name="invalid_model",  # type: ignore[arg-type]
            )

    def test_predict_auto_loads_models(
        self,
        trained_models_dir: Path,
        sample_market_context: MarketContext,
    ) -> None:
        """Test predict auto-loads models if not loaded."""
        manager = ModelManager(models_dir=trained_models_dir)
        assert manager._loaded is False

        prediction = manager.predict(
            sample_market_context,
            price=35.0,
            segment="Segment_A",
        )

        assert manager._loaded is True
        assert isinstance(prediction, float)

    def test_get_all_predictions(
        self,
        trained_models_dir: Path,
        sample_market_context: MarketContext,
    ) -> None:
        """Test getting predictions from all models."""
        manager = ModelManager(models_dir=trained_models_dir)
        manager.load_models()

        predictions = manager.get_all_predictions(
            sample_market_context,
            price=35.0,
            segment="Segment_A",
        )

        assert isinstance(predictions, dict)
        assert len(predictions) == 3
        assert "linear_regression" in predictions
        assert "decision_tree" in predictions
        assert "xgboost" in predictions

        for model_name, pred in predictions.items():
            assert isinstance(pred, float)
            assert 0.0 <= pred <= 1.0, f"{model_name} prediction out of range"

    def test_predict_demand_curve(
        self,
        trained_models_dir: Path,
        sample_market_context: MarketContext,
    ) -> None:
        """Test generating demand curve at multiple prices."""
        manager = ModelManager(models_dir=trained_models_dir)
        manager.load_models()

        prices = [20.0, 30.0, 40.0, 50.0]
        curve = manager.predict_demand_curve(
            sample_market_context,
            prices=prices,
            segment="Segment_A",
        )

        assert len(curve) == len(prices)
        for i, point in enumerate(curve):
            assert "price" in point
            assert "demand" in point
            assert point["price"] == prices[i]
            assert 0.0 <= point["demand"] <= 1.0

    def test_get_available_models(self, trained_models_dir: Path) -> None:
        """Test getting list of available models."""
        manager = ModelManager(models_dir=trained_models_dir)
        manager.load_models()

        available = manager.get_available_models()

        assert isinstance(available, list)
        assert len(available) == 3
        assert set(available) == {"linear_regression", "decision_tree", "xgboost"}

    def test_get_model_info_xgboost(self, trained_models_dir: Path) -> None:
        """Test getting XGBoost model info."""
        manager = ModelManager(models_dir=trained_models_dir)
        manager.load_models()

        info = manager.get_model_info("xgboost")

        assert info["name"] == "xgboost"
        assert info["type"] == "XGBRegressor"
        assert "feature_count" in info
        assert "feature_names" in info
        assert "feature_importance" in info

    def test_get_model_info_linear_regression(self, trained_models_dir: Path) -> None:
        """Test getting Linear Regression model info."""
        manager = ModelManager(models_dir=trained_models_dir)
        manager.load_models()

        info = manager.get_model_info("linear_regression")

        assert info["name"] == "linear_regression"
        assert info["type"] == "LinearRegression"
        assert "coefficients" in info
        assert "intercept" in info

    def test_get_model_info_invalid(self, trained_models_dir: Path) -> None:
        """Test getting info for invalid model raises error."""
        manager = ModelManager(models_dir=trained_models_dir)
        manager.load_models()

        with pytest.raises(ValueError, match="not available"):
            manager.get_model_info("invalid_model")  # type: ignore[arg-type]

    def test_unseen_category_handling(
        self,
        trained_models_dir: Path,
    ) -> None:
        """Test handling of unseen categorical values."""
        manager = ModelManager(models_dir=trained_models_dir)
        manager.load_models()

        # Create context with unusual values (within valid types)
        context = MarketContext(
            number_of_riders=50,
            number_of_drivers=25,
            location_category="Urban",
            customer_loyalty_status="Gold",
            number_of_past_rides=20,
            average_ratings=4.5,
            time_of_booking="Evening",
            vehicle_type="Premium",
            expected_ride_duration=30,
            historical_cost_of_ride=35.0,
        )

        # With unknown segment - should handle gracefully
        prediction = manager.predict(
            context,
            price=35.0,
            segment="NewSegment",  # Unseen segment
        )

        # Should still return a valid prediction
        assert isinstance(prediction, float)


class TestGetModelManager:
    """Tests for get_model_manager singleton function."""

    def test_singleton_behavior(self, trained_models_dir: Path) -> None:
        """Test that get_model_manager returns singleton."""
        # Reset singleton
        import src.ml.model_manager as mm

        mm._model_manager = None

        manager1 = get_model_manager(models_dir=trained_models_dir)
        manager2 = get_model_manager()

        assert manager1 is manager2

        # Cleanup
        mm._model_manager = None

