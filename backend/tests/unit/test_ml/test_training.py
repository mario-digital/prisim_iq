"""Tests for ML model training pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from src.ml.training import ModelMetrics, ModelTrainer, TrainingResult


@pytest.fixture
def sample_training_data() -> pd.DataFrame:
    """Create sample training data for tests."""
    np.random.seed(42)
    n_samples = 100

    return pd.DataFrame(
        {
            "number_of_riders": np.random.randint(10, 100, n_samples),
            "number_of_drivers": np.random.randint(5, 50, n_samples),
            "location_category": np.random.choice(
                ["Urban", "Suburban", "Rural"], n_samples
            ),
            "customer_loyalty_status": np.random.choice(
                ["Bronze", "Silver", "Gold", "Platinum"], n_samples
            ),
            "number_of_past_rides": np.random.randint(0, 100, n_samples),
            "average_ratings": np.random.uniform(1.0, 5.0, n_samples),
            "time_of_booking": np.random.choice(
                ["Morning", "Afternoon", "Evening", "Night"], n_samples
            ),
            "vehicle_type": np.random.choice(["Economy", "Premium"], n_samples),
            "expected_ride_duration": np.random.randint(5, 60, n_samples),
            "historical_cost_of_ride": np.random.uniform(10, 100, n_samples),
            "supply_demand_ratio": np.random.uniform(0.3, 3.0, n_samples),
            "segment": np.random.choice(["Segment_A", "Segment_B", "Segment_C"], n_samples),
            "price": np.random.uniform(10, 100, n_samples),
            "demand": np.random.uniform(0, 1, n_samples),
            "profit": np.random.uniform(0, 50, n_samples),
        }
    )


@pytest.fixture
def sample_test_data() -> pd.DataFrame:
    """Create sample test data for tests."""
    np.random.seed(123)
    n_samples = 30

    return pd.DataFrame(
        {
            "number_of_riders": np.random.randint(10, 100, n_samples),
            "number_of_drivers": np.random.randint(5, 50, n_samples),
            "location_category": np.random.choice(
                ["Urban", "Suburban", "Rural"], n_samples
            ),
            "customer_loyalty_status": np.random.choice(
                ["Bronze", "Silver", "Gold", "Platinum"], n_samples
            ),
            "number_of_past_rides": np.random.randint(0, 100, n_samples),
            "average_ratings": np.random.uniform(1.0, 5.0, n_samples),
            "time_of_booking": np.random.choice(
                ["Morning", "Afternoon", "Evening", "Night"], n_samples
            ),
            "vehicle_type": np.random.choice(["Economy", "Premium"], n_samples),
            "expected_ride_duration": np.random.randint(5, 60, n_samples),
            "historical_cost_of_ride": np.random.uniform(10, 100, n_samples),
            "supply_demand_ratio": np.random.uniform(0.3, 3.0, n_samples),
            "segment": np.random.choice(["Segment_A", "Segment_B", "Segment_C"], n_samples),
            "price": np.random.uniform(10, 100, n_samples),
            "demand": np.random.uniform(0, 1, n_samples),
            "profit": np.random.uniform(0, 50, n_samples),
        }
    )


class TestModelMetrics:
    """Tests for ModelMetrics dataclass."""

    def test_model_metrics_creation(self) -> None:
        """Test ModelMetrics can be created."""
        metrics = ModelMetrics(r2=0.85, mae=0.1, rmse=0.15)

        assert metrics.r2 == 0.85
        assert metrics.mae == 0.1
        assert metrics.rmse == 0.15

    def test_model_metrics_to_dict(self) -> None:
        """Test ModelMetrics to_dict conversion."""
        metrics = ModelMetrics(r2=0.85, mae=0.1, rmse=0.15)
        result = metrics.to_dict()

        assert result == {"r2": 0.85, "mae": 0.1, "rmse": 0.15}


class TestTrainingResult:
    """Tests for TrainingResult dataclass."""

    def test_training_result_creation(self) -> None:
        """Test TrainingResult can be created."""
        model = LinearRegression()
        metrics = ModelMetrics(r2=0.85, mae=0.1, rmse=0.15)

        result = TrainingResult(
            model_name="test_model",
            model=model,
            metrics=metrics,
        )

        assert result.model_name == "test_model"
        assert result.model is model
        assert result.metrics.r2 == 0.85
        assert result.best_params is None
        assert result.feature_importance is None


class TestModelTrainer:
    """Tests for ModelTrainer class."""

    def test_trainer_initialization(self, tmp_path: Path) -> None:
        """Test ModelTrainer can be initialized."""
        trainer = ModelTrainer(models_dir=tmp_path)

        assert trainer.models_dir == tmp_path
        assert trainer.models_dir.exists()
        assert trainer.encoders == {}
        assert trainer.results == {}

    @patch("src.ml.training.load_training_data")
    @patch("src.ml.training.load_test_data")
    def test_load_data(
        self,
        mock_load_test: MagicMock,
        mock_load_train: MagicMock,
        sample_training_data: pd.DataFrame,
        sample_test_data: pd.DataFrame,
        tmp_path: Path,
    ) -> None:
        """Test data loading and encoding."""
        mock_load_train.return_value = sample_training_data
        mock_load_test.return_value = sample_test_data

        trainer = ModelTrainer(models_dir=tmp_path)
        trainer.load_data()

        assert trainer._X_train is not None
        assert trainer._y_train is not None
        assert trainer._X_test is not None
        assert trainer._y_test is not None
        assert len(trainer.encoders) > 0
        assert len(trainer.feature_names) > 0

    @patch("src.ml.training.load_training_data")
    @patch("src.ml.training.load_test_data")
    def test_train_linear_regression(
        self,
        mock_load_test: MagicMock,
        mock_load_train: MagicMock,
        sample_training_data: pd.DataFrame,
        sample_test_data: pd.DataFrame,
        tmp_path: Path,
    ) -> None:
        """Test Linear Regression training."""
        mock_load_train.return_value = sample_training_data
        mock_load_test.return_value = sample_test_data

        trainer = ModelTrainer(models_dir=tmp_path)
        trainer.load_data()
        result = trainer.train_linear_regression()

        assert result.model_name == "linear_regression"
        assert isinstance(result.model, LinearRegression)
        assert result.metrics.r2 is not None
        assert result.metrics.mae is not None
        assert result.metrics.rmse is not None
        assert result.coefficients is not None
        assert "linear_regression" in trainer.results

    @patch("src.ml.training.load_training_data")
    @patch("src.ml.training.load_test_data")
    def test_train_decision_tree(
        self,
        mock_load_test: MagicMock,
        mock_load_train: MagicMock,
        sample_training_data: pd.DataFrame,
        sample_test_data: pd.DataFrame,
        tmp_path: Path,
    ) -> None:
        """Test Decision Tree training with GridSearchCV."""
        mock_load_train.return_value = sample_training_data
        mock_load_test.return_value = sample_test_data

        trainer = ModelTrainer(models_dir=tmp_path)
        trainer.load_data()
        result = trainer.train_decision_tree()

        assert result.model_name == "decision_tree"
        assert isinstance(result.model, DecisionTreeRegressor)
        assert result.best_params is not None
        assert "max_depth" in result.best_params
        assert result.feature_importance is not None
        assert "decision_tree" in trainer.results

    @patch("src.ml.training.load_training_data")
    @patch("src.ml.training.load_test_data")
    def test_train_xgboost(
        self,
        mock_load_test: MagicMock,
        mock_load_train: MagicMock,
        sample_training_data: pd.DataFrame,
        sample_test_data: pd.DataFrame,
        tmp_path: Path,
    ) -> None:
        """Test XGBoost training with GridSearchCV."""
        mock_load_train.return_value = sample_training_data
        mock_load_test.return_value = sample_test_data

        trainer = ModelTrainer(models_dir=tmp_path)
        trainer.load_data()
        result = trainer.train_xgboost()

        assert result.model_name == "xgboost"
        assert isinstance(result.model, XGBRegressor)
        assert result.best_params is not None
        assert "max_depth" in result.best_params
        assert "n_estimators" in result.best_params
        assert "learning_rate" in result.best_params
        assert result.feature_importance is not None
        assert "xgboost" in trainer.results

    @patch("src.ml.training.load_training_data")
    @patch("src.ml.training.load_test_data")
    def test_train_all(
        self,
        mock_load_test: MagicMock,
        mock_load_train: MagicMock,
        sample_training_data: pd.DataFrame,
        sample_test_data: pd.DataFrame,
        tmp_path: Path,
    ) -> None:
        """Test training all models."""
        mock_load_train.return_value = sample_training_data
        mock_load_test.return_value = sample_test_data

        trainer = ModelTrainer(models_dir=tmp_path)
        results = trainer.train_all()

        assert len(results) == 3
        assert "linear_regression" in results
        assert "decision_tree" in results
        assert "xgboost" in results

    @patch("src.ml.training.load_training_data")
    @patch("src.ml.training.load_test_data")
    def test_get_comparison_table(
        self,
        mock_load_test: MagicMock,
        mock_load_train: MagicMock,
        sample_training_data: pd.DataFrame,
        sample_test_data: pd.DataFrame,
        tmp_path: Path,
    ) -> None:
        """Test comparison table generation."""
        mock_load_train.return_value = sample_training_data
        mock_load_test.return_value = sample_test_data

        trainer = ModelTrainer(models_dir=tmp_path)
        trainer.train_all()
        table = trainer.get_comparison_table()

        assert isinstance(table, pd.DataFrame)
        assert "model" in table.columns
        assert "r2" in table.columns
        assert "mae" in table.columns
        assert "rmse" in table.columns
        assert len(table) == 3

    @patch("src.ml.training.load_training_data")
    @patch("src.ml.training.load_test_data")
    def test_save_models(
        self,
        mock_load_test: MagicMock,
        mock_load_train: MagicMock,
        sample_training_data: pd.DataFrame,
        sample_test_data: pd.DataFrame,
        tmp_path: Path,
    ) -> None:
        """Test model serialization."""
        mock_load_train.return_value = sample_training_data
        mock_load_test.return_value = sample_test_data

        trainer = ModelTrainer(models_dir=tmp_path)
        trainer.train_all()
        trainer.save_models()

        # Check model files exist
        assert (tmp_path / "linear_regression.joblib").exists()
        assert (tmp_path / "decision_tree.joblib").exists()
        assert (tmp_path / "xgboost.joblib").exists()
        assert (tmp_path / "encoders.joblib").exists()
        assert (tmp_path / "feature_info.json").exists()

    @patch("src.ml.training.load_training_data")
    @patch("src.ml.training.load_test_data")
    def test_save_metrics(
        self,
        mock_load_test: MagicMock,
        mock_load_train: MagicMock,
        sample_training_data: pd.DataFrame,
        sample_test_data: pd.DataFrame,
        tmp_path: Path,
    ) -> None:
        """Test metrics serialization."""
        mock_load_train.return_value = sample_training_data
        mock_load_test.return_value = sample_test_data

        trainer = ModelTrainer(models_dir=tmp_path)
        trainer.train_all()
        trainer.save_metrics()

        metrics_path = tmp_path / "metrics.json"
        assert metrics_path.exists()

    def test_train_without_loading_data_raises_error(self, tmp_path: Path) -> None:
        """Test that training without data raises RuntimeError."""
        trainer = ModelTrainer(models_dir=tmp_path)

        with pytest.raises(RuntimeError, match="Data not loaded"):
            trainer.train_linear_regression()

    def test_comparison_table_without_training_raises_error(
        self, tmp_path: Path
    ) -> None:
        """Test that getting comparison without training raises RuntimeError."""
        trainer = ModelTrainer(models_dir=tmp_path)

        with pytest.raises(RuntimeError, match="No models trained"):
            trainer.get_comparison_table()

    @patch("src.ml.training.load_training_data")
    @patch("src.ml.training.load_test_data")
    def test_predictions_in_valid_range(
        self,
        mock_load_test: MagicMock,
        mock_load_train: MagicMock,
        sample_training_data: pd.DataFrame,
        sample_test_data: pd.DataFrame,
        tmp_path: Path,
    ) -> None:
        """Test that model predictions are reasonable (not checking [0,1] clip)."""
        mock_load_train.return_value = sample_training_data
        mock_load_test.return_value = sample_test_data

        trainer = ModelTrainer(models_dir=tmp_path)
        trainer.train_all()

        # Get predictions from each model
        for name, result in trainer.results.items():
            predictions = result.model.predict(trainer._X_test)
            # Just check they're numeric and finite
            assert np.all(np.isfinite(predictions)), f"{name} has non-finite predictions"

