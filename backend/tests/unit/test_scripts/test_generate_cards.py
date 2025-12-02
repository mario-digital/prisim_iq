"""Tests for Model Cards and Data Cards generation.

Tests cover:
- Card schema validation
- JSON structure integrity
- Markdown rendering
- Card generation functions
"""

from __future__ import annotations

import json
from datetime import datetime

import pytest
from scripts.generate_cards import (
    DataCard,
    DatasetStatistics,
    DataSource,
    EthicalConsiderations,
    FeatureDescription,
    IntendedUse,
    ModelCard,
    ModelDetails,
    PerformanceMetrics,
    TrainingDataSummary,
    generate_data_card,
    generate_decision_tree_model_card,
    generate_linear_regression_model_card,
    generate_xgboost_model_card,
    load_eda_summary,
    load_feature_info,
    load_metrics,
    render_data_card_markdown,
    render_model_card_markdown,
)

# =============================================================================
# Schema Validation Tests
# =============================================================================


class TestModelCardSchema:
    """Tests for ModelCard Pydantic schema."""

    def test_model_card_required_fields(self) -> None:
        """Test that ModelCard requires all specified fields."""
        card = ModelCard(
            model_name="Test Model",
            model_version="1.0.0",
            generated_at="2024-01-01T00:00:00Z",
            model_details=ModelDetails(
                architecture="Test Architecture",
                hyperparameters={"param1": 10},
                training_date="2024-01-01",
                framework="test-framework 1.0",
                input_features=["feature1", "feature2"],
                output="test output",
            ),
            intended_use=IntendedUse(
                primary_use="Testing",
                users=["testers"],
                out_of_scope=["production"],
            ),
            training_data=TrainingDataSummary(
                dataset_name="Test Dataset",
                dataset_size=1000,
                features_used=["feature1", "feature2"],
                target_variable="target",
                train_test_split="80/20",
            ),
            metrics=PerformanceMetrics(
                r2_score=0.95,
                mae=0.05,
                rmse=0.07,
                test_set_size=200,
            ),
            ethical_considerations=EthicalConsiderations(
                fairness_considerations=["consideration1"],
                privacy_considerations=["consideration2"],
                transparency_notes=["note1"],
            ),
            limitations=["limitation1", "limitation2"],
        )

        assert card.model_name == "Test Model"
        assert card.model_version == "1.0.0"
        assert card.metrics.r2_score == 0.95
        assert len(card.limitations) == 2

    def test_model_card_optional_fields(self) -> None:
        """Test that feature_importance and coefficients are optional."""
        card = ModelCard(
            model_name="Test",
            model_version="1.0.0",
            generated_at="2024-01-01T00:00:00Z",
            model_details=ModelDetails(
                architecture="Test",
                hyperparameters={},
                training_date="2024-01-01",
                framework="test 1.0",
                input_features=["f1"],
                output="output",
            ),
            intended_use=IntendedUse(
                primary_use="Test",
                users=["user"],
                out_of_scope=["scope"],
            ),
            training_data=TrainingDataSummary(
                dataset_name="Test",
                dataset_size=100,
                features_used=["f1"],
                target_variable="target",
                train_test_split="80/20",
            ),
            metrics=PerformanceMetrics(
                r2_score=0.9,
                mae=0.1,
                rmse=0.12,
                test_set_size=20,
            ),
            ethical_considerations=EthicalConsiderations(
                fairness_considerations=[],
                privacy_considerations=[],
                transparency_notes=[],
            ),
            limitations=[],
        )

        assert card.feature_importance is None
        assert card.coefficients is None

    def test_model_card_with_feature_importance(self) -> None:
        """Test ModelCard with feature importance values."""
        card = ModelCard(
            model_name="Test",
            model_version="1.0.0",
            generated_at="2024-01-01T00:00:00Z",
            model_details=ModelDetails(
                architecture="Test",
                hyperparameters={},
                training_date="2024-01-01",
                framework="test 1.0",
                input_features=["f1", "f2"],
                output="output",
            ),
            intended_use=IntendedUse(
                primary_use="Test",
                users=["user"],
                out_of_scope=[],
            ),
            training_data=TrainingDataSummary(
                dataset_name="Test",
                dataset_size=100,
                features_used=["f1", "f2"],
                target_variable="target",
                train_test_split="80/20",
            ),
            metrics=PerformanceMetrics(
                r2_score=0.9,
                mae=0.1,
                rmse=0.12,
                test_set_size=20,
            ),
            ethical_considerations=EthicalConsiderations(
                fairness_considerations=[],
                privacy_considerations=[],
                transparency_notes=[],
            ),
            limitations=[],
            feature_importance={"f1": 0.7, "f2": 0.3},
        )

        assert card.feature_importance is not None
        assert card.feature_importance["f1"] == 0.7
        assert card.feature_importance["f2"] == 0.3


class TestDataCardSchema:
    """Tests for DataCard Pydantic schema."""

    def test_data_card_required_fields(self) -> None:
        """Test that DataCard requires all specified fields."""
        card = DataCard(
            dataset_name="Test Dataset",
            version="1.0.0",
            generated_at="2024-01-01T00:00:00Z",
            source=DataSource(
                origin="Test Origin",
                collection_date="2024",
                preprocessing_steps=["step1", "step2"],
            ),
            features=[
                FeatureDescription(
                    name="feature1",
                    dtype="float64",
                    description="Test feature",
                    range_or_values="0.0 - 1.0",
                    distribution="continuous",
                )
            ],
            statistics=DatasetStatistics(
                row_count=1000,
                column_count=10,
                missing_values=0,
                numeric_features=7,
                categorical_features=3,
            ),
            known_biases=["bias1"],
            limitations=["limitation1"],
            intended_use="Testing purposes",
        )

        assert card.dataset_name == "Test Dataset"
        assert card.statistics.row_count == 1000
        assert len(card.features) == 1
        assert card.features[0].name == "feature1"


# =============================================================================
# JSON Structure Tests
# =============================================================================


class TestJSONStructure:
    """Tests for JSON serialization and structure."""

    def test_model_card_to_json(self) -> None:
        """Test ModelCard serializes to valid JSON."""
        card = ModelCard(
            model_name="Test Model",
            model_version="1.0.0",
            generated_at="2024-01-01T00:00:00Z",
            model_details=ModelDetails(
                architecture="Test",
                hyperparameters={"learning_rate": 0.1},
                training_date="2024-01-01",
                framework="test 1.0",
                input_features=["f1"],
                output="output",
            ),
            intended_use=IntendedUse(
                primary_use="Test",
                users=["user"],
                out_of_scope=[],
            ),
            training_data=TrainingDataSummary(
                dataset_name="Test",
                dataset_size=100,
                features_used=["f1"],
                target_variable="target",
                train_test_split="80/20",
            ),
            metrics=PerformanceMetrics(
                r2_score=0.9,
                mae=0.1,
                rmse=0.12,
                test_set_size=20,
            ),
            ethical_considerations=EthicalConsiderations(
                fairness_considerations=["fair"],
                privacy_considerations=["private"],
                transparency_notes=["transparent"],
            ),
            limitations=["limit1"],
        )

        # Serialize to JSON string
        json_str = card.model_dump_json()

        # Parse back and verify structure
        parsed = json.loads(json_str)

        assert "model_name" in parsed
        assert "model_details" in parsed
        assert "metrics" in parsed
        assert parsed["model_details"]["hyperparameters"]["learning_rate"] == 0.1

    def test_data_card_to_json(self) -> None:
        """Test DataCard serializes to valid JSON."""
        card = DataCard(
            dataset_name="Test",
            version="1.0.0",
            generated_at="2024-01-01T00:00:00Z",
            source=DataSource(
                origin="Test",
                collection_date="2024",
                preprocessing_steps=["step1"],
            ),
            features=[
                FeatureDescription(
                    name="f1",
                    dtype="int64",
                    description="Feature 1",
                    range_or_values="1 - 100",
                    distribution="continuous",
                )
            ],
            statistics=DatasetStatistics(
                row_count=100,
                column_count=5,
                missing_values=0,
                numeric_features=3,
                categorical_features=2,
            ),
            known_biases=[],
            limitations=[],
            intended_use="Testing",
        )

        json_str = card.model_dump_json()
        parsed = json.loads(json_str)

        assert "dataset_name" in parsed
        assert "features" in parsed
        assert "statistics" in parsed
        assert parsed["statistics"]["row_count"] == 100


# =============================================================================
# Markdown Rendering Tests
# =============================================================================


class TestMarkdownRendering:
    """Tests for Markdown rendering functions."""

    def test_model_card_markdown_structure(self) -> None:
        """Test that ModelCard renders to valid Markdown with required sections."""
        card = ModelCard(
            model_name="Test Model",
            model_version="1.0.0",
            generated_at="2024-01-01T00:00:00Z",
            model_details=ModelDetails(
                architecture="Test Architecture",
                hyperparameters={"param1": 10},
                training_date="2024-01-01",
                framework="test 1.0",
                input_features=["f1", "f2"],
                output="output",
            ),
            intended_use=IntendedUse(
                primary_use="Testing",
                users=["testers"],
                out_of_scope=["production"],
            ),
            training_data=TrainingDataSummary(
                dataset_name="Test Dataset",
                dataset_size=1000,
                features_used=["f1", "f2"],
                target_variable="target",
                train_test_split="80/20",
            ),
            metrics=PerformanceMetrics(
                r2_score=0.95,
                mae=0.05,
                rmse=0.07,
                test_set_size=200,
            ),
            ethical_considerations=EthicalConsiderations(
                fairness_considerations=["fair"],
                privacy_considerations=["private"],
                transparency_notes=["transparent"],
            ),
            limitations=["limitation1"],
        )

        markdown = render_model_card_markdown(card)

        # Check required sections exist
        assert "# Model Card: Test Model" in markdown
        assert "## Model Details" in markdown
        assert "## Intended Use" in markdown
        assert "## Training Data" in markdown
        assert "## Performance Metrics" in markdown
        assert "## Ethical Considerations" in markdown
        assert "## Limitations" in markdown

        # Check metrics table
        assert "| R² Score | 0.9500 |" in markdown
        assert "| MAE | 0.0500 |" in markdown

    def test_model_card_markdown_with_feature_importance(self) -> None:
        """Test that feature importance is rendered when present."""
        card = ModelCard(
            model_name="Test",
            model_version="1.0.0",
            generated_at="2024-01-01T00:00:00Z",
            model_details=ModelDetails(
                architecture="Test",
                hyperparameters={},
                training_date="2024-01-01",
                framework="test 1.0",
                input_features=["f1"],
                output="output",
            ),
            intended_use=IntendedUse(
                primary_use="Test",
                users=["user"],
                out_of_scope=[],
            ),
            training_data=TrainingDataSummary(
                dataset_name="Test",
                dataset_size=100,
                features_used=["f1"],
                target_variable="target",
                train_test_split="80/20",
            ),
            metrics=PerformanceMetrics(
                r2_score=0.9,
                mae=0.1,
                rmse=0.12,
                test_set_size=20,
            ),
            ethical_considerations=EthicalConsiderations(
                fairness_considerations=[],
                privacy_considerations=[],
                transparency_notes=[],
            ),
            limitations=[],
            feature_importance={"f1": 0.8, "f2": 0.2},
        )

        markdown = render_model_card_markdown(card)

        assert "### Feature Importance" in markdown
        assert "f1" in markdown
        assert "f2" in markdown

    def test_model_card_markdown_with_coefficients(self) -> None:
        """Test that coefficients are rendered for linear models."""
        card = ModelCard(
            model_name="Linear Model",
            model_version="1.0.0",
            generated_at="2024-01-01T00:00:00Z",
            model_details=ModelDetails(
                architecture="Linear Regression",
                hyperparameters={},
                training_date="2024-01-01",
                framework="test 1.0",
                input_features=["f1"],
                output="output",
            ),
            intended_use=IntendedUse(
                primary_use="Test",
                users=["user"],
                out_of_scope=[],
            ),
            training_data=TrainingDataSummary(
                dataset_name="Test",
                dataset_size=100,
                features_used=["f1"],
                target_variable="target",
                train_test_split="80/20",
            ),
            metrics=PerformanceMetrics(
                r2_score=0.6,
                mae=0.15,
                rmse=0.18,
                test_set_size=20,
            ),
            ethical_considerations=EthicalConsiderations(
                fairness_considerations=[],
                privacy_considerations=[],
                transparency_notes=[],
            ),
            limitations=[],
            coefficients={"f1": 0.5, "intercept": 0.1},
        )

        markdown = render_model_card_markdown(card)

        assert "### Model Coefficients" in markdown
        assert "f1" in markdown
        assert "intercept" in markdown

    def test_data_card_markdown_structure(self) -> None:
        """Test that DataCard renders to valid Markdown with required sections."""
        card = DataCard(
            dataset_name="Test Dataset",
            version="1.0.0",
            generated_at="2024-01-01T00:00:00Z",
            source=DataSource(
                origin="Test Origin",
                collection_date="2024",
                preprocessing_steps=["step1", "step2"],
            ),
            features=[
                FeatureDescription(
                    name="feature1",
                    dtype="float64",
                    description="Test feature",
                    range_or_values="0.0 - 1.0",
                    distribution="continuous",
                )
            ],
            statistics=DatasetStatistics(
                row_count=1000,
                column_count=10,
                missing_values=0,
                numeric_features=7,
                categorical_features=3,
            ),
            known_biases=["bias1"],
            limitations=["limitation1"],
            intended_use="Testing purposes",
        )

        markdown = render_data_card_markdown(card)

        # Check required sections exist
        assert "# Data Card: Test Dataset" in markdown
        assert "## Data Source" in markdown
        assert "## Dataset Statistics" in markdown
        assert "## Features" in markdown
        assert "## Known Biases" in markdown
        assert "## Limitations" in markdown

        # Check statistics
        assert "**Rows:** 1,000" in markdown
        assert "**Columns:** 10" in markdown


# =============================================================================
# Card Generation Tests (Integration)
# =============================================================================


class TestCardGeneration:
    """Integration tests for card generation functions."""

    @pytest.fixture
    def metrics(self) -> dict:
        """Load actual metrics fixture."""
        return load_metrics()

    @pytest.fixture
    def feature_info(self) -> dict:
        """Load actual feature info fixture."""
        return load_feature_info()

    @pytest.fixture
    def eda_summary(self) -> dict:
        """Load actual EDA summary fixture."""
        return load_eda_summary()

    def test_generate_xgboost_model_card(self, metrics: dict, feature_info: dict) -> None:
        """Test XGBoost model card generation with real data."""
        card = generate_xgboost_model_card(metrics, feature_info)

        assert card.model_name == "XGBoost Demand Predictor"
        assert card.model_version == "1.0.0"
        assert card.model_details.architecture == "XGBoost Gradient Boosting Regressor"
        assert card.metrics.r2_score == pytest.approx(0.986, rel=0.01)
        assert card.feature_importance is not None
        assert len(card.feature_importance) > 0
        assert card.coefficients is None

    def test_generate_decision_tree_model_card(self, metrics: dict, feature_info: dict) -> None:
        """Test Decision Tree model card generation with real data."""
        card = generate_decision_tree_model_card(metrics, feature_info)

        assert card.model_name == "Decision Tree Demand Predictor"
        assert card.model_details.architecture == "Decision Tree Regressor"
        assert card.metrics.r2_score == pytest.approx(0.899, rel=0.01)
        assert card.feature_importance is not None
        assert card.model_details.hyperparameters.get("max_depth") == 10

    def test_generate_linear_regression_model_card(self, metrics: dict, feature_info: dict) -> None:
        """Test Linear Regression model card generation with real data."""
        card = generate_linear_regression_model_card(metrics, feature_info)

        assert card.model_name == "Linear Regression Baseline"
        assert card.model_details.architecture == "Ordinary Least Squares Linear Regression"
        assert card.metrics.r2_score == pytest.approx(0.576, rel=0.01)
        assert card.coefficients is not None
        assert "intercept" in card.coefficients
        assert card.feature_importance is None

    def test_generate_data_card(self, eda_summary: dict) -> None:
        """Test Data Card generation with real EDA summary."""
        card = generate_data_card(eda_summary)

        assert card.dataset_name == "Dynamic Pricing Dataset"
        assert card.version == "1.0.0"
        assert card.statistics.row_count == 1000
        assert card.statistics.column_count == 11
        assert card.statistics.missing_values == 0
        assert len(card.features) == 11  # All columns from EDA
        assert len(card.known_biases) > 0
        assert len(card.limitations) > 0

    def test_generated_cards_have_valid_timestamps(
        self, metrics: dict, feature_info: dict, eda_summary: dict
    ) -> None:
        """Test that all generated cards have valid ISO timestamps."""
        xgboost_card = generate_xgboost_model_card(metrics, feature_info)
        dt_card = generate_decision_tree_model_card(metrics, feature_info)
        lr_card = generate_linear_regression_model_card(metrics, feature_info)
        data_card = generate_data_card(eda_summary)

        for card in [xgboost_card, dt_card, lr_card, data_card]:
            # Should parse without error
            timestamp = card.generated_at
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            assert parsed is not None

    def test_xgboost_card_markdown_renders(self, metrics: dict, feature_info: dict) -> None:
        """Test that XGBoost card renders to Markdown without error."""
        card = generate_xgboost_model_card(metrics, feature_info)
        markdown = render_model_card_markdown(card)

        assert "XGBoost Demand Predictor" in markdown
        assert "XGBoost Gradient Boosting Regressor" in markdown
        assert "### Feature Importance" in markdown

    def test_data_card_markdown_renders(self, eda_summary: dict) -> None:
        """Test that Data Card renders to Markdown without error."""
        card = generate_data_card(eda_summary)
        markdown = render_data_card_markdown(card)

        assert "Dynamic Pricing Dataset" in markdown
        assert "Number_of_Riders" in markdown
        assert "## Known Biases" in markdown


# =============================================================================
# File Loading Tests
# =============================================================================


class TestDataLoading:
    """Tests for data loading functions."""

    def test_load_metrics(self) -> None:
        """Test that metrics.json loads correctly."""
        metrics = load_metrics()

        assert "xgboost" in metrics
        assert "decision_tree" in metrics
        assert "linear_regression" in metrics
        assert "metrics" in metrics["xgboost"]
        assert "r2" in metrics["xgboost"]["metrics"]

    def test_load_feature_info(self) -> None:
        """Test that feature_info.json loads correctly."""
        feature_info = load_feature_info()

        assert "feature_names" in feature_info
        assert "categorical_columns" in feature_info
        assert "target_column" in feature_info
        assert feature_info["target_column"] == "demand"

    def test_load_eda_summary(self) -> None:
        """Test that eda_summary.json loads correctly."""
        eda = load_eda_summary()

        assert "row_count" in eda
        assert "column_count" in eda
        assert "columns" in eda
        assert "numeric_stats" in eda
        assert "categorical_distributions" in eda

