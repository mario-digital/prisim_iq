"""Unit tests for feature importance calculation."""

import numpy as np
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from src.explainability.feature_importance import (
    FeatureImportanceCalculator,
    get_global_importance,
)


@pytest.fixture
def sample_data():
    """Generate sample training data."""
    np.random.seed(42)
    X = np.random.randn(100, 5)
    # Create target with known feature importance pattern
    y = 0.5 * X[:, 0] + 0.3 * X[:, 1] + 0.1 * X[:, 2] + np.random.randn(100) * 0.1
    feature_names = ["feature_a", "feature_b", "feature_c", "feature_d", "feature_e"]
    return X, y, feature_names


@pytest.fixture
def trained_linear_model(sample_data):
    """Train a Linear Regression model."""
    X, y, _ = sample_data
    model = LinearRegression()
    model.fit(X, y)
    return model


@pytest.fixture
def trained_decision_tree(sample_data):
    """Train a Decision Tree model."""
    X, y, _ = sample_data
    model = DecisionTreeRegressor(max_depth=5, random_state=42)
    model.fit(X, y)
    return model


@pytest.fixture
def trained_xgboost(sample_data):
    """Train an XGBoost model."""
    X, y, _ = sample_data
    model = XGBRegressor(max_depth=3, n_estimators=10, random_state=42, verbosity=0)
    model.fit(X, y)
    return model


class TestFeatureImportanceCalculator:
    """Tests for FeatureImportanceCalculator class."""

    def test_linear_regression_importance_sums_to_one(
        self, trained_linear_model, sample_data
    ):
        """AC7: Linear regression importances must sum to 1.0."""
        _, _, feature_names = sample_data
        calculator = FeatureImportanceCalculator(
            trained_linear_model, "linear_regression", feature_names
        )
        importance = calculator.get_global_importance()

        # Sum of all importances should be 1.0 (within tolerance)
        total = sum(importance.values())
        assert abs(total - 1.0) < 0.01, f"Importances sum to {total}, expected 1.0"

    def test_decision_tree_importance_sums_to_one(
        self, trained_decision_tree, sample_data
    ):
        """AC7: Decision tree importances must sum to 1.0."""
        _, _, feature_names = sample_data
        calculator = FeatureImportanceCalculator(
            trained_decision_tree, "decision_tree", feature_names
        )
        importance = calculator.get_global_importance()

        # Sum of all importances should be 1.0 (within tolerance)
        total = sum(importance.values())
        assert abs(total - 1.0) < 0.01, f"Importances sum to {total}, expected 1.0"

    def test_xgboost_importance_sums_to_one(self, trained_xgboost, sample_data):
        """AC7: XGBoost importances must sum to 1.0."""
        _, _, feature_names = sample_data
        calculator = FeatureImportanceCalculator(
            trained_xgboost, "xgboost", feature_names
        )
        importance = calculator.get_global_importance()

        # Sum of all importances should be 1.0 (within tolerance)
        total = sum(importance.values())
        assert abs(total - 1.0) < 0.01, f"Importances sum to {total}, expected 1.0"

    def test_importance_dict_has_all_features(self, trained_xgboost, sample_data):
        """Importance dict should contain all feature names."""
        _, _, feature_names = sample_data
        calculator = FeatureImportanceCalculator(
            trained_xgboost, "xgboost", feature_names
        )
        importance = calculator.get_global_importance()

        assert len(importance) == len(feature_names)
        for name in feature_names:
            assert name in importance

    def test_all_importance_values_non_negative(self, trained_xgboost, sample_data):
        """All importance values should be non-negative."""
        _, _, feature_names = sample_data
        calculator = FeatureImportanceCalculator(
            trained_xgboost, "xgboost", feature_names
        )
        importance = calculator.get_global_importance()

        for name, value in importance.items():
            assert value >= 0, f"Feature {name} has negative importance: {value}"

    def test_linear_raw_coefficients(self, trained_linear_model, sample_data):
        """Linear model should provide raw coefficients with sign."""
        _, _, feature_names = sample_data
        calculator = FeatureImportanceCalculator(
            trained_linear_model, "linear_regression", feature_names
        )
        raw_coef = calculator.get_raw_coefficients()

        assert raw_coef is not None
        assert len(raw_coef) == len(feature_names)

    def test_tree_model_no_raw_coefficients(self, trained_decision_tree, sample_data):
        """Tree models should return None for raw_coefficients."""
        _, _, feature_names = sample_data
        calculator = FeatureImportanceCalculator(
            trained_decision_tree, "decision_tree", feature_names
        )
        raw_coef = calculator.get_raw_coefficients()

        assert raw_coef is None


class TestGetGlobalImportance:
    """Tests for get_global_importance convenience function."""

    def test_convenience_function_works(self, trained_xgboost, sample_data):
        """get_global_importance should return valid importance dict."""
        _, _, feature_names = sample_data
        importance = get_global_importance(trained_xgboost, "xgboost", feature_names)

        assert isinstance(importance, dict)
        total = sum(importance.values())
        assert abs(total - 1.0) < 0.01

    def test_importance_extraction_all_model_types(self, sample_data):
        """Test importance extraction works for all three model types."""
        X, y, feature_names = sample_data

        models = {
            "linear_regression": LinearRegression().fit(X, y),
            "decision_tree": DecisionTreeRegressor(max_depth=5, random_state=42).fit(
                X, y
            ),
            "xgboost": XGBRegressor(
                max_depth=3, n_estimators=10, random_state=42, verbosity=0
            ).fit(X, y),
        }

        for model_type, model in models.items():
            importance = get_global_importance(model, model_type, feature_names)

            # AC7: Verify sum to 1.0
            total = sum(importance.values())
            assert abs(total - 1.0) < 0.01, (
                f"{model_type}: Importances sum to {total}, expected 1.0"
            )

            # All features present
            assert len(importance) == len(feature_names)

