"""Unit tests for SHAP explainer."""

import numpy as np
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from src.explainability.shap_explainer import (
    ShapExplainer,
    get_shap_importance,
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


class TestShapExplainer:
    """Tests for ShapExplainer class."""

    def test_xgboost_shap_values_calculated(self, trained_xgboost, sample_data):
        """AC4: SHAP values should be calculated for XGBoost."""
        X, _, feature_names = sample_data
        explainer = ShapExplainer(
            trained_xgboost, "xgboost", feature_names
        )

        # Get SHAP values for first sample
        shap_values = explainer.explain(X[0])

        # Should return values for all features
        assert len(shap_values) == len(feature_names)
        # All values should be finite
        assert np.all(np.isfinite(shap_values))

    def test_decision_tree_shap_values_calculated(
        self, trained_decision_tree, sample_data
    ):
        """AC4: SHAP values should be calculated for Decision Tree."""
        X, _, feature_names = sample_data
        explainer = ShapExplainer(
            trained_decision_tree, "decision_tree", feature_names
        )

        shap_values = explainer.explain(X[0])

        assert len(shap_values) == len(feature_names)
        assert np.all(np.isfinite(shap_values))

    def test_linear_regression_shap_values_calculated(
        self, trained_linear_model, sample_data
    ):
        """AC4: SHAP values should be calculated for Linear Regression."""
        X, _, feature_names = sample_data
        explainer = ShapExplainer(
            trained_linear_model,
            "linear_regression",
            feature_names,
            background_data=X,  # Required for LinearExplainer
        )

        shap_values = explainer.explain(X[0])

        assert len(shap_values) == len(feature_names)
        assert np.all(np.isfinite(shap_values))

    def test_linear_explainer_requires_background_data(
        self, trained_linear_model, sample_data
    ):
        """LinearExplainer should raise error without background data."""
        X, _, feature_names = sample_data
        explainer = ShapExplainer(
            trained_linear_model,
            "linear_regression",
            feature_names,
            background_data=None,  # Missing!
        )

        with pytest.raises(ValueError, match="background_data is required"):
            explainer.explain(X[0])

    def test_explain_single_returns_dict(self, trained_xgboost, sample_data):
        """explain_single should return dict mapping feature names to values."""
        X, _, feature_names = sample_data
        explainer = ShapExplainer(trained_xgboost, "xgboost", feature_names)

        result = explainer.explain_single(X[0])

        assert isinstance(result, dict)
        assert len(result) == len(feature_names)
        for name in feature_names:
            assert name in result
            assert isinstance(result[name], float)

    def test_batch_shap_values(self, trained_xgboost, sample_data):
        """SHAP values should work for batch inputs."""
        X, _, feature_names = sample_data
        explainer = ShapExplainer(trained_xgboost, "xgboost", feature_names)

        # Explain multiple samples
        shap_values = explainer.explain(X[:5])

        assert shap_values.shape == (5, len(feature_names))
        assert np.all(np.isfinite(shap_values))

    def test_expected_value_returned(self, trained_xgboost, sample_data):
        """get_expected_value should return the base prediction."""
        X, _, feature_names = sample_data
        explainer = ShapExplainer(trained_xgboost, "xgboost", feature_names)

        # Initialize explainer by making a prediction
        _ = explainer.explain(X[0])

        expected = explainer.get_expected_value()

        assert isinstance(expected, float)
        assert np.isfinite(expected)

    def test_explain_with_base(self, trained_xgboost, sample_data):
        """explain_with_base should return both SHAP dict and base value."""
        X, _, feature_names = sample_data
        explainer = ShapExplainer(trained_xgboost, "xgboost", feature_names)

        shap_dict, base_value = explainer.explain_with_base(X[0])

        assert isinstance(shap_dict, dict)
        assert len(shap_dict) == len(feature_names)
        assert isinstance(base_value, float)


class TestGetShapImportance:
    """Tests for get_shap_importance convenience function."""

    def test_convenience_function_works(self, trained_xgboost, sample_data):
        """get_shap_importance should return valid SHAP dict."""
        X, _, feature_names = sample_data

        result = get_shap_importance(
            trained_xgboost, "xgboost", feature_names, X[0]
        )

        assert isinstance(result, dict)
        assert len(result) == len(feature_names)

    def test_shap_calculated_all_model_types(self, sample_data):
        """AC4: SHAP values should be calculated for each model type."""
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
            # Linear needs background data
            bg_data = X if model_type == "linear_regression" else None

            result = get_shap_importance(
                model, model_type, feature_names, X[0], background_data=bg_data
            )

            # Verify SHAP values calculated
            assert isinstance(result, dict), f"{model_type}: Expected dict"
            assert len(result) == len(feature_names), f"{model_type}: Wrong feature count"

            # All values should be finite
            for name, value in result.items():
                assert np.isfinite(value), f"{model_type}: {name} has non-finite value"

