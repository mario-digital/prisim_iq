"""Unit tests for feature importance service."""

import numpy as np
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from src.explainability.importance_service import (
    FeatureImportanceService,
    _generate_description,
    _normalize_importance,
    _rank_contributions,
    get_feature_importance,
)
from src.schemas.explainability import FeatureContribution, FeatureImportanceResult


@pytest.fixture
def sample_data():
    """Generate sample training data."""
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = 0.5 * X[:, 0] + 0.3 * X[:, 1] + 0.1 * X[:, 2] + np.random.randn(100) * 0.1
    feature_names = ["feature_a", "feature_b", "feature_c", "feature_d", "feature_e"]
    return X, y, feature_names


@pytest.fixture
def trained_xgboost(sample_data):
    """Train an XGBoost model."""
    X, y, _ = sample_data
    model = XGBRegressor(max_depth=3, n_estimators=10, random_state=42, verbosity=0)
    model.fit(X, y)
    return model


@pytest.fixture
def trained_linear_model(sample_data):
    """Train a Linear Regression model."""
    X, y, _ = sample_data
    model = LinearRegression()
    model.fit(X, y)
    return model


class TestNormalization:
    """Tests for normalization and ranking functions."""

    def test_normalize_importance_sums_to_one(self):
        """AC5: Normalized values must sum to 100%."""
        raw = {"a": 0.5, "b": 0.3, "c": 0.2}
        normalized = _normalize_importance(raw)

        total = sum(imp for imp, _ in normalized.values())
        assert abs(total - 1.0) < 0.01, f"Sum is {total}, expected 1.0"

    def test_normalize_handles_negative_values(self):
        """AC5: Handle negative coefficients correctly."""
        raw = {"a": -0.5, "b": 0.3, "c": 0.2}
        normalized = _normalize_importance(raw)

        # Should use absolute values for normalization
        total = sum(imp for imp, _ in normalized.values())
        assert abs(total - 1.0) < 0.01

        # Direction should be tracked
        assert normalized["a"][1] == "negative"
        assert normalized["b"][1] == "positive"
        assert normalized["c"][1] == "positive"

    def test_normalize_handles_all_zeros(self):
        """Edge case: all values are zero."""
        raw = {"a": 0.0, "b": 0.0, "c": 0.0}
        normalized = _normalize_importance(raw)

        total = sum(imp for imp, _ in normalized.values())
        assert abs(total - 1.0) < 0.01

    def test_rank_contributions_descending(self):
        """AC5: Sort by absolute importance (descending)."""
        normalized = {
            "low": (0.1, "positive"),
            "high": (0.6, "negative"),
            "mid": (0.3, "positive"),
        }
        ranked = _rank_contributions(normalized)

        assert ranked[0][0] == "high"
        assert ranked[1][0] == "mid"
        assert ranked[2][0] == "low"


class TestDescriptions:
    """Tests for description generation."""

    def test_description_includes_percentage(self):
        """AC6: Description should include percentage."""
        desc = _generate_description("supply_demand_ratio", 0.32, "positive")

        assert "32%" in desc or "+32%" in desc

    def test_description_includes_direction(self):
        """AC6: Include direction (positive/negative impact)."""
        pos_desc = _generate_description("supply_demand_ratio", 0.25, "positive")
        neg_desc = _generate_description("supply_demand_ratio", 0.25, "negative")

        assert "+" in pos_desc
        assert "-" in neg_desc

    def test_description_uses_feature_template(self):
        """Known features should use specific descriptions."""
        desc = _generate_description("supply_demand_ratio", 0.30, "positive")

        # Should use the template for supply_demand_ratio
        assert "demand" in desc.lower() or "driver" in desc.lower()


class TestFeatureImportanceService:
    """Tests for FeatureImportanceService class."""

    def test_global_importance_returns_result(self, trained_xgboost, sample_data):
        """Global importance should return FeatureImportanceResult."""
        _, _, feature_names = sample_data
        service = FeatureImportanceService(
            trained_xgboost, "xgboost", feature_names
        )

        result = service.get_global_importance()

        assert isinstance(result, FeatureImportanceResult)
        assert result.explanation_type == "global"
        assert result.model_used == "xgboost"

    def test_global_importance_sums_to_one(self, trained_xgboost, sample_data):
        """AC7: All importance values sum to 1.0."""
        _, _, feature_names = sample_data
        service = FeatureImportanceService(
            trained_xgboost, "xgboost", feature_names
        )

        result = service.get_global_importance()
        total = sum(c.importance for c in result.contributions)

        assert abs(total - 1.0) < 0.01, f"Sum is {total}, expected 1.0"

    def test_contributions_are_ranked(self, trained_xgboost, sample_data):
        """Contributions should be sorted by importance descending."""
        _, _, feature_names = sample_data
        service = FeatureImportanceService(
            trained_xgboost, "xgboost", feature_names
        )

        result = service.get_global_importance()
        importances = [c.importance for c in result.contributions]

        # Check sorted descending
        assert importances == sorted(importances, reverse=True)

    def test_top_3_have_descriptions(self, trained_xgboost, sample_data):
        """AC6: Top 3 features include plain-English descriptions."""
        _, _, feature_names = sample_data
        service = FeatureImportanceService(
            trained_xgboost, "xgboost", feature_names
        )

        result = service.get_global_importance()
        top_3 = result.contributions[:3]

        for c in top_3:
            assert c.description, f"Missing description for {c.feature_name}"
            assert len(c.description) > 5, "Description too short"
            assert "%" in c.description, "Description should include percentage"

    def test_top_3_summary_generated(self, trained_xgboost, sample_data):
        """top_3_summary should be a natural language string."""
        _, _, feature_names = sample_data
        service = FeatureImportanceService(
            trained_xgboost, "xgboost", feature_names
        )

        result = service.get_global_importance()

        assert result.top_3_summary
        assert "Price driven by:" in result.top_3_summary

    def test_local_importance_returns_shap_result(self, trained_xgboost, sample_data):
        """Local importance should return SHAP-based result."""
        X, _, feature_names = sample_data
        service = FeatureImportanceService(
            trained_xgboost, "xgboost", feature_names
        )

        result = service.get_local_importance(X[0])

        assert isinstance(result, FeatureImportanceResult)
        assert result.explanation_type == "local_shap"

    def test_local_importance_sums_to_one(self, trained_xgboost, sample_data):
        """AC7: SHAP values normalized to sum to 1.0."""
        X, _, feature_names = sample_data
        service = FeatureImportanceService(
            trained_xgboost, "xgboost", feature_names
        )

        result = service.get_local_importance(X[0])
        total = sum(c.importance for c in result.contributions)

        assert abs(total - 1.0) < 0.01, f"Sum is {total}, expected 1.0"

    def test_linear_regression_with_background(self, trained_linear_model, sample_data):
        """Linear regression should work with background data."""
        X, _, feature_names = sample_data
        service = FeatureImportanceService(
            trained_linear_model, "linear_regression", feature_names,
            background_data=X
        )

        # Global should work
        global_result = service.get_global_importance()
        assert len(global_result.contributions) == len(feature_names)

        # Local should work with background
        local_result = service.get_local_importance(X[0])
        assert len(local_result.contributions) == len(feature_names)


class TestConvenienceFunction:
    """Tests for get_feature_importance function."""

    def test_global_convenience_function(self, trained_xgboost, sample_data):
        """get_feature_importance with global type."""
        _, _, feature_names = sample_data

        result = get_feature_importance(
            trained_xgboost, "xgboost", feature_names,
            explanation_type="global"
        )

        assert result.explanation_type == "global"
        total = sum(c.importance for c in result.contributions)
        assert abs(total - 1.0) < 0.01

    def test_local_convenience_function(self, trained_xgboost, sample_data):
        """get_feature_importance with local_shap type."""
        X, _, feature_names = sample_data

        result = get_feature_importance(
            trained_xgboost, "xgboost", feature_names,
            X=X[0],
            explanation_type="local_shap"
        )

        assert result.explanation_type == "local_shap"
        total = sum(c.importance for c in result.contributions)
        assert abs(total - 1.0) < 0.01

    def test_local_requires_x(self, trained_xgboost, sample_data):
        """local_shap should raise error without X."""
        _, _, feature_names = sample_data

        with pytest.raises(ValueError, match="X is required"):
            get_feature_importance(
                trained_xgboost, "xgboost", feature_names,
                explanation_type="local_shap"
            )


class TestFeatureContributionSchema:
    """Tests for FeatureContribution schema."""

    def test_contribution_fields(self, trained_xgboost, sample_data):
        """FeatureContribution should have all required fields."""
        _, _, feature_names = sample_data
        service = FeatureImportanceService(
            trained_xgboost, "xgboost", feature_names
        )

        result = service.get_global_importance()
        contribution = result.contributions[0]

        assert hasattr(contribution, "feature_name")
        assert hasattr(contribution, "display_name")
        assert hasattr(contribution, "importance")
        assert hasattr(contribution, "direction")
        assert hasattr(contribution, "description")

    def test_importance_in_valid_range(self, trained_xgboost, sample_data):
        """Importance should be between 0 and 1."""
        _, _, feature_names = sample_data
        service = FeatureImportanceService(
            trained_xgboost, "xgboost", feature_names
        )

        result = service.get_global_importance()

        for c in result.contributions:
            assert 0 <= c.importance <= 1, f"{c.feature_name} has invalid importance"

    def test_direction_is_valid(self, trained_xgboost, sample_data):
        """Direction should be 'positive' or 'negative'."""
        _, _, feature_names = sample_data
        service = FeatureImportanceService(
            trained_xgboost, "xgboost", feature_names
        )

        result = service.get_global_importance()

        for c in result.contributions:
            assert c.direction in ["positive", "negative"]

