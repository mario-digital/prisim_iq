#!/usr/bin/env python
"""Generate Model Cards and Data Cards for PrismIQ.

This script generates standardized documentation for models and data:
1. Model Cards (Google Model Cards format) for each trained model
2. Data Card for the dynamic_pricing.xlsx dataset

Usage:
    cd backend
    source .venv/bin/activate
    python scripts/generate_cards.py
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
CARDS_DIR = DATA_DIR / "cards"
MODELS_DIR = DATA_DIR / "models"


# =============================================================================
# Model Card Schemas (Google Model Cards Format)
# =============================================================================


class ModelDetails(BaseModel):
    """Technical details about the model architecture and training."""

    architecture: str = Field(description="Model architecture type")
    hyperparameters: dict[str, Any] = Field(description="Model hyperparameters")
    training_date: str = Field(description="Date model was trained")
    framework: str = Field(description="ML framework and version")
    input_features: list[str] = Field(description="List of input feature names")
    output: str = Field(description="Model output description")


class IntendedUse(BaseModel):
    """Documentation of intended and out-of-scope uses."""

    primary_use: str = Field(description="Primary intended use case")
    users: list[str] = Field(description="Target user groups")
    out_of_scope: list[str] = Field(description="Uses that are out of scope")


class TrainingDataSummary(BaseModel):
    """Summary of the training data used."""

    dataset_name: str = Field(description="Name of the training dataset")
    dataset_size: int = Field(description="Number of training samples")
    features_used: list[str] = Field(description="Features used in training")
    target_variable: str = Field(description="Target variable name")
    train_test_split: str = Field(description="Train/test split ratio")


class PerformanceMetrics(BaseModel):
    """Model performance metrics on test set."""

    r2_score: float = Field(description="R-squared score")
    mae: float = Field(description="Mean Absolute Error")
    rmse: float = Field(description="Root Mean Squared Error")
    test_set_size: int = Field(description="Number of test samples")


class EthicalConsiderations(BaseModel):
    """Ethical considerations and responsible AI notes."""

    fairness_considerations: list[str] = Field(description="Fairness-related considerations")
    privacy_considerations: list[str] = Field(description="Privacy-related considerations")
    transparency_notes: list[str] = Field(description="Transparency and explainability notes")


class ModelCard(BaseModel):
    """Complete Model Card following Google Model Cards format.

    Reference: https://arxiv.org/abs/1810.03993
    """

    # Metadata
    model_name: str = Field(description="Human-readable model name")
    model_version: str = Field(description="Semantic version of the model")
    generated_at: str = Field(description="ISO timestamp when card was generated")

    # Sections
    model_details: ModelDetails = Field(description="Technical model details")
    intended_use: IntendedUse = Field(description="Intended use documentation")
    training_data: TrainingDataSummary = Field(description="Training data summary")
    metrics: PerformanceMetrics = Field(description="Performance metrics")
    ethical_considerations: EthicalConsiderations = Field(description="Ethical considerations")
    limitations: list[str] = Field(description="Known limitations")

    # PrismIQ-specific
    feature_importance: dict[str, float] | None = Field(
        default=None, description="Feature importance scores (if available)"
    )
    coefficients: dict[str, float] | None = Field(
        default=None, description="Model coefficients (for linear models)"
    )


# =============================================================================
# Data Card Schemas
# =============================================================================


class DataSource(BaseModel):
    """Information about data source and provenance."""

    origin: str = Field(description="Data origin/source")
    collection_date: str = Field(description="When data was collected")
    preprocessing_steps: list[str] = Field(description="Preprocessing steps applied")


class FeatureDescription(BaseModel):
    """Description of a single feature in the dataset."""

    name: str = Field(description="Feature name")
    dtype: str = Field(description="Data type")
    description: str = Field(description="Human-readable description")
    range_or_values: str = Field(description="Value range or categories")
    distribution: str = Field(description="Distribution type")


class DatasetStatistics(BaseModel):
    """Statistical summary of the dataset."""

    row_count: int = Field(description="Total number of rows")
    column_count: int = Field(description="Total number of columns")
    missing_values: int = Field(description="Total missing values")
    numeric_features: int = Field(description="Number of numeric features")
    categorical_features: int = Field(description="Number of categorical features")


class DataCard(BaseModel):
    """Data Card documenting dataset characteristics and quality.

    Based on Google Data Cards format for dataset documentation.
    """

    # Metadata
    dataset_name: str = Field(description="Dataset name")
    version: str = Field(description="Dataset version")
    generated_at: str = Field(description="ISO timestamp when card was generated")

    # Sections
    source: DataSource = Field(description="Data source information")
    features: list[FeatureDescription] = Field(description="Feature documentation")
    statistics: DatasetStatistics = Field(description="Dataset statistics")
    known_biases: list[str] = Field(description="Known biases in the data")
    limitations: list[str] = Field(description="Dataset limitations")
    intended_use: str = Field(description="Intended use for this dataset")


# =============================================================================
# Markdown Rendering Functions
# =============================================================================


def _format_dict_as_table(d: dict[str, Any], key_header: str = "Key", value_header: str = "Value") -> str:
    """Format a dictionary as a Markdown table."""
    if not d:
        return "*None*"

    lines = [f"| {key_header} | {value_header} |", "|---|---|"]
    for key, value in d.items():
        formatted_value = f"{value:.6f}" if isinstance(value, float) else str(value)
        lines.append(f"| {key} | {formatted_value} |")
    return "\n".join(lines)


def _format_list(items: list[str]) -> str:
    """Format a list as Markdown bullet points."""
    if not items:
        return "*None*"
    return "\n".join(f"- {item}" for item in items)


def render_model_card_markdown(card: ModelCard) -> str:
    """Render a ModelCard as Markdown documentation.

    Args:
        card: ModelCard instance to render.

    Returns:
        Formatted Markdown string.
    """
    sections = [
        f"# Model Card: {card.model_name}",
        "",
        f"**Version:** {card.model_version}  ",
        f"**Generated:** {card.generated_at}",
        "",
        "---",
        "",
        "## Model Details",
        "",
        f"- **Architecture:** {card.model_details.architecture}",
        f"- **Framework:** {card.model_details.framework}",
        f"- **Training Date:** {card.model_details.training_date}",
        f"- **Output:** {card.model_details.output}",
        "",
        "### Hyperparameters",
        "",
        _format_dict_as_table(card.model_details.hyperparameters, "Parameter", "Value"),
        "",
        "### Input Features",
        "",
        _format_list(card.model_details.input_features),
        "",
        "---",
        "",
        "## Intended Use",
        "",
        f"**Primary Use:** {card.intended_use.primary_use}",
        "",
        "**Target Users:**",
        "",
        _format_list(card.intended_use.users),
        "",
        "**Out of Scope:**",
        "",
        _format_list(card.intended_use.out_of_scope),
        "",
        "---",
        "",
        "## Training Data",
        "",
        f"- **Dataset:** {card.training_data.dataset_name}",
        f"- **Size:** {card.training_data.dataset_size:,} samples",
        f"- **Target Variable:** {card.training_data.target_variable}",
        f"- **Train/Test Split:** {card.training_data.train_test_split}",
        "",
        "---",
        "",
        "## Performance Metrics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| R² Score | {card.metrics.r2_score:.4f} |",
        f"| MAE | {card.metrics.mae:.4f} |",
        f"| RMSE | {card.metrics.rmse:.4f} |",
        f"| Test Set Size | {card.metrics.test_set_size:,} |",
        "",
    ]

    # Add feature importance if available
    if card.feature_importance:
        # Sort by importance descending
        sorted_importance = dict(
            sorted(card.feature_importance.items(), key=lambda x: x[1], reverse=True)
        )
        sections.extend(
            [
                "### Feature Importance",
                "",
                _format_dict_as_table(sorted_importance, "Feature", "Importance"),
                "",
            ]
        )

    # Add coefficients if available
    if card.coefficients:
        sections.extend(
            [
                "### Model Coefficients",
                "",
                _format_dict_as_table(card.coefficients, "Feature", "Coefficient"),
                "",
            ]
        )

    sections.extend(
        [
            "---",
            "",
            "## Ethical Considerations",
            "",
            "### Fairness",
            "",
            _format_list(card.ethical_considerations.fairness_considerations),
            "",
            "### Privacy",
            "",
            _format_list(card.ethical_considerations.privacy_considerations),
            "",
            "### Transparency",
            "",
            _format_list(card.ethical_considerations.transparency_notes),
            "",
            "---",
            "",
            "## Limitations",
            "",
            _format_list(card.limitations),
            "",
        ]
    )

    return "\n".join(sections)


def render_data_card_markdown(card: DataCard) -> str:
    """Render a DataCard as Markdown documentation.

    Args:
        card: DataCard instance to render.

    Returns:
        Formatted Markdown string.
    """
    sections = [
        f"# Data Card: {card.dataset_name}",
        "",
        f"**Version:** {card.version}  ",
        f"**Generated:** {card.generated_at}",
        "",
        "---",
        "",
        "## Data Source",
        "",
        f"- **Origin:** {card.source.origin}",
        f"- **Collection Date:** {card.source.collection_date}",
        "",
        "### Preprocessing Steps",
        "",
        _format_list(card.source.preprocessing_steps),
        "",
        "---",
        "",
        "## Dataset Statistics",
        "",
        f"- **Rows:** {card.statistics.row_count:,}",
        f"- **Columns:** {card.statistics.column_count}",
        f"- **Missing Values:** {card.statistics.missing_values}",
        f"- **Numeric Features:** {card.statistics.numeric_features}",
        f"- **Categorical Features:** {card.statistics.categorical_features}",
        "",
        "---",
        "",
        "## Features",
        "",
        "| Feature | Type | Description | Range/Values | Distribution |",
        "|---------|------|-------------|--------------|--------------|",
    ]

    for feature in card.features:
        sections.append(
            f"| {feature.name} | {feature.dtype} | {feature.description} | "
            f"{feature.range_or_values} | {feature.distribution} |"
        )

    sections.extend(
        [
            "",
            "---",
            "",
            "## Intended Use",
            "",
            card.intended_use,
            "",
            "---",
            "",
            "## Known Biases",
            "",
            _format_list(card.known_biases),
            "",
            "---",
            "",
            "## Limitations",
            "",
            _format_list(card.limitations),
            "",
        ]
    )

    return "\n".join(sections)


# =============================================================================
# Card Generation Functions
# =============================================================================


def load_metrics() -> dict[str, Any]:
    """Load model metrics from metrics.json."""
    metrics_path = MODELS_DIR / "metrics.json"
    with open(metrics_path) as f:
        return json.load(f)


def load_feature_info() -> dict[str, Any]:
    """Load feature info from feature_info.json."""
    feature_info_path = MODELS_DIR / "feature_info.json"
    with open(feature_info_path) as f:
        return json.load(f)


def load_eda_summary() -> dict[str, Any]:
    """Load EDA summary from eda_summary.json."""
    eda_path = DATA_DIR / "eda_summary.json"
    with open(eda_path) as f:
        return json.load(f)


def _get_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(UTC).isoformat()


def _get_common_ethical_considerations() -> EthicalConsiderations:
    """Return common ethical considerations for all models."""
    return EthicalConsiderations(
        fairness_considerations=[
            "Model may exhibit different performance across customer segments",
            "Price sensitivity varies by loyalty status - monitor for discriminatory outcomes",
            "Geographic location features could encode socioeconomic biases",
            "Regular fairness audits recommended across protected characteristics",
        ],
        privacy_considerations=[
            "Model trained on aggregated ride data without PII",
            "Individual customer IDs not used as features",
            "Predictions should not be used to identify individual customers",
        ],
        transparency_notes=[
            "SHAP values available for individual prediction explanations",
            "Feature importance scores documented in this card",
            "Decision traces logged for audit purposes",
            "Model predictions include confidence intervals",
        ],
    )


def _get_common_intended_use() -> IntendedUse:
    """Return common intended use for all models."""
    return IntendedUse(
        primary_use="Predict customer demand probability for dynamic ride pricing optimization",
        users=[
            "Pricing Analysts - reviewing and adjusting pricing strategies",
            "Data Scientists - model monitoring and improvement",
            "Product Managers - understanding demand patterns",
            "Business Stakeholders - revenue optimization decisions",
        ],
        out_of_scope=[
            "Real-time surge pricing without human oversight",
            "Individual customer targeting based on personal characteristics",
            "Price discrimination based on protected attributes",
            "Extrapolation to markets outside training data geography",
            "Predictions for vehicle types not in training data",
        ],
    )


def generate_xgboost_model_card(metrics: dict, feature_info: dict) -> ModelCard:
    """Generate Model Card for the XGBoost demand prediction model."""
    model_metrics = metrics["xgboost"]

    return ModelCard(
        model_name="XGBoost Demand Predictor",
        model_version="1.0.0",
        generated_at=_get_timestamp(),
        model_details=ModelDetails(
            architecture="XGBoost Gradient Boosting Regressor",
            hyperparameters=model_metrics["best_params"] or {},
            training_date="2024-12-01",
            framework="XGBoost 2.1 / scikit-learn 1.5",
            input_features=feature_info["feature_names"],
            output="Demand probability [0.0, 1.0] representing likelihood of ride acceptance at given price",
        ),
        intended_use=_get_common_intended_use(),
        training_data=TrainingDataSummary(
            dataset_name="PrismIQ Synthetic Training Data",
            dataset_size=8000,  # 80% of 1000 * 10 price points
            features_used=feature_info["feature_names"],
            target_variable="demand",
            train_test_split="80/20 stratified by segment",
        ),
        metrics=PerformanceMetrics(
            r2_score=model_metrics["metrics"]["r2"],
            mae=model_metrics["metrics"]["mae"],
            rmse=model_metrics["metrics"]["rmse"],
            test_set_size=2000,  # 20% of 10000
        ),
        ethical_considerations=_get_common_ethical_considerations(),
        limitations=[
            "Trained on synthetic demand data generated from elasticity curves",
            "Performance may degrade for extreme price points outside training range",
            "Assumes stable market conditions - may not generalize during special events",
            "Limited to vehicle types present in training data (Economy, Premium)",
            "Geographic scope limited to Urban, Suburban, and Rural location categories",
            "Temporal patterns based on time_of_booking buckets, not continuous time",
        ],
        feature_importance=model_metrics.get("feature_importance"),
        coefficients=None,
    )


def generate_decision_tree_model_card(metrics: dict, feature_info: dict) -> ModelCard:
    """Generate Model Card for the Decision Tree demand prediction model."""
    model_metrics = metrics["decision_tree"]

    return ModelCard(
        model_name="Decision Tree Demand Predictor",
        model_version="1.0.0",
        generated_at=_get_timestamp(),
        model_details=ModelDetails(
            architecture="Decision Tree Regressor",
            hyperparameters=model_metrics["best_params"] or {"max_depth": 10},
            training_date="2024-12-01",
            framework="scikit-learn 1.5",
            input_features=feature_info["feature_names"],
            output="Demand probability [0.0, 1.0] representing likelihood of ride acceptance at given price",
        ),
        intended_use=_get_common_intended_use(),
        training_data=TrainingDataSummary(
            dataset_name="PrismIQ Synthetic Training Data",
            dataset_size=8000,
            features_used=feature_info["feature_names"],
            target_variable="demand",
            train_test_split="80/20 stratified by segment",
        ),
        metrics=PerformanceMetrics(
            r2_score=model_metrics["metrics"]["r2"],
            mae=model_metrics["metrics"]["mae"],
            rmse=model_metrics["metrics"]["rmse"],
            test_set_size=2000,
        ),
        ethical_considerations=_get_common_ethical_considerations(),
        limitations=[
            "Lower accuracy than XGBoost ensemble (R² 0.90 vs 0.99)",
            "Prone to overfitting without depth constraints",
            "Sharp decision boundaries may not reflect smooth demand curves",
            "Less robust to outliers compared to ensemble methods",
            "Same data scope limitations as XGBoost model",
        ],
        feature_importance=model_metrics.get("feature_importance"),
        coefficients=None,
    )


def generate_linear_regression_model_card(metrics: dict, feature_info: dict) -> ModelCard:
    """Generate Model Card for the Linear Regression baseline model."""
    model_metrics = metrics["linear_regression"]

    return ModelCard(
        model_name="Linear Regression Baseline",
        model_version="1.0.0",
        generated_at=_get_timestamp(),
        model_details=ModelDetails(
            architecture="Ordinary Least Squares Linear Regression",
            hyperparameters={},
            training_date="2024-12-01",
            framework="scikit-learn 1.5",
            input_features=feature_info["feature_names"],
            output="Demand probability [0.0, 1.0] - may exceed bounds, clip in production",
        ),
        intended_use=IntendedUse(
            primary_use="Baseline model for comparison - NOT recommended for production use",
            users=[
                "Data Scientists - model comparison and benchmarking",
                "Researchers - understanding linear relationships in data",
            ],
            out_of_scope=[
                "Production demand prediction (use XGBoost instead)",
                "Any use case where accuracy is critical",
                "Real-time pricing decisions",
            ],
        ),
        training_data=TrainingDataSummary(
            dataset_name="PrismIQ Synthetic Training Data",
            dataset_size=8000,
            features_used=feature_info["feature_names"],
            target_variable="demand",
            train_test_split="80/20 stratified by segment",
        ),
        metrics=PerformanceMetrics(
            r2_score=model_metrics["metrics"]["r2"],
            mae=model_metrics["metrics"]["mae"],
            rmse=model_metrics["metrics"]["rmse"],
            test_set_size=2000,
        ),
        ethical_considerations=EthicalConsiderations(
            fairness_considerations=[
                "Linear assumptions may not capture non-linear fairness issues",
                "Coefficient interpretation enables bias detection",
            ],
            privacy_considerations=[
                "Same privacy considerations as other models",
            ],
            transparency_notes=[
                "Fully interpretable through coefficient analysis",
                "Each coefficient represents direct feature impact on demand",
                "Intercept represents baseline demand when all features are zero",
            ],
        ),
        limitations=[
            "Significantly lower accuracy than tree-based models (R² 0.58 vs 0.99)",
            "Assumes linear relationships - demand/price relationship is non-linear",
            "Predictions may exceed [0, 1] bounds - requires clipping",
            "Cannot capture feature interactions without manual engineering",
            "Provided as baseline only - not suitable for production",
        ],
        feature_importance=None,
        coefficients=model_metrics.get("coefficients"),
    )


def generate_data_card(eda_summary: dict) -> DataCard:
    """Generate Data Card for the dynamic_pricing.xlsx dataset."""
    # Build feature descriptions from EDA summary
    features: list[FeatureDescription] = []
    column_info = eda_summary["columns"]
    numeric_stats = eda_summary["numeric_stats"]
    categorical_dist = eda_summary["categorical_distributions"]

    feature_descriptions = {
        "Number_of_Riders": "Number of customers requesting rides in the area",
        "Number_of_Drivers": "Number of available drivers in the area",
        "Location_Category": "Type of geographic location",
        "Customer_Loyalty_Status": "Customer loyalty tier based on ride history",
        "Number_of_Past_Rides": "Total historical rides by the customer",
        "Average_Ratings": "Customer's average rating from drivers",
        "Time_of_Booking": "Time period when ride was booked",
        "Vehicle_Type": "Type of vehicle requested",
        "Expected_Ride_Duration": "Estimated trip duration in minutes",
        "Historical_Cost_of_Ride": "Historical average cost for similar rides",
        "supply_demand_ratio": "Ratio of available drivers to requesting riders",
    }

    for col_name, col_data in column_info.items():
        dtype = col_data["dtype"]

        # Determine range/values and distribution
        if col_name in numeric_stats:
            stats = numeric_stats[col_name]
            range_str = f"{stats['min']:.2f} - {stats['max']:.2f}"
            distribution = "continuous"
        elif col_name in categorical_dist:
            categories = list(categorical_dist[col_name].keys())
            range_str = ", ".join(categories)
            distribution = "categorical"
        else:
            range_str = "unknown"
            distribution = "unknown"

        features.append(
            FeatureDescription(
                name=col_name,
                dtype=dtype,
                description=feature_descriptions.get(col_name, "No description available"),
                range_or_values=range_str,
                distribution=distribution,
            )
        )

    # Count numeric vs categorical
    numeric_count = len(numeric_stats)
    categorical_count = len(categorical_dist)

    return DataCard(
        dataset_name="Dynamic Pricing Dataset",
        version="1.0.0",
        generated_at=_get_timestamp(),
        source=DataSource(
            origin="Kaggle Dynamic Pricing Dataset (synthetic)",
            collection_date="2024",
            preprocessing_steps=[
                "Loaded from Excel format (dynamic_pricing.xlsx)",
                "Computed supply_demand_ratio as Number_of_Drivers / Number_of_Riders",
                "Verified no missing values across all columns",
                "Validated data types and value ranges",
                "Generated segment labels using K-Means clustering",
            ],
        ),
        features=features,
        statistics=DatasetStatistics(
            row_count=eda_summary["row_count"],
            column_count=eda_summary["column_count"],
            missing_values=0,
            numeric_features=numeric_count,
            categorical_features=categorical_count,
        ),
        known_biases=[
            "Synthetic data may not reflect real-world demand patterns",
            "Premium vehicles overrepresented (52% vs 48% Economy)",
            "Geographic categories are simplified (Urban/Suburban/Rural only)",
            "Time of booking is bucketed, losing granular temporal patterns",
            "Customer loyalty distribution is relatively balanced, may not match reality",
            "No seasonal or weather-related features included",
        ],
        limitations=[
            "Sample size of 1,000 rows limits statistical power for rare scenarios",
            "No external validation against real ride-sharing data",
            "Synthetic nature means patterns may not generalize to production",
            "Missing features: weather, events, competitor pricing, traffic conditions",
            "No longitudinal data - cannot capture customer behavior over time",
            "Geographic scope is abstract, not tied to real locations",
        ],
        intended_use=(
            "Training and evaluation of demand prediction models for PrismIQ "
            "dynamic pricing demonstration. This dataset is intended for educational "
            "and prototyping purposes. Production systems should validate against "
            "real-world data before deployment."
        ),
    )


def save_card(card: BaseModel, filename: str) -> Path:
    """Save a card to JSON file.

    Args:
        card: Model card or data card to save.
        filename: Output filename (without path).

    Returns:
        Path to the saved file.
    """
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = CARDS_DIR / filename

    with open(output_path, "w") as f:
        json.dump(card.model_dump(), f, indent=2)

    return output_path


def main() -> None:
    """Generate all model cards and data card."""
    print("=" * 60)
    print("Generating Model Cards and Data Card")
    print("=" * 60)

    # Load data
    print("\nLoading metrics and EDA data...")
    metrics = load_metrics()
    feature_info = load_feature_info()
    eda_summary = load_eda_summary()

    # Generate model cards
    print("\nGenerating XGBoost Model Card...")
    xgboost_card = generate_xgboost_model_card(metrics, feature_info)
    xgboost_path = save_card(xgboost_card, "xgboost_model_card.json")
    print(f"  Saved: {xgboost_path}")

    print("\nGenerating Decision Tree Model Card...")
    dt_card = generate_decision_tree_model_card(metrics, feature_info)
    dt_path = save_card(dt_card, "decision_tree_model_card.json")
    print(f"  Saved: {dt_path}")

    print("\nGenerating Linear Regression Model Card...")
    lr_card = generate_linear_regression_model_card(metrics, feature_info)
    lr_path = save_card(lr_card, "linear_regression_model_card.json")
    print(f"  Saved: {lr_path}")

    # Generate data card
    print("\nGenerating Data Card...")
    data_card = generate_data_card(eda_summary)
    data_path = save_card(data_card, "dynamic_pricing_data_card.json")
    print(f"  Saved: {data_path}")

    # Generate markdown files
    print("\nGenerating Markdown documentation...")
    md_dir = CARDS_DIR / "markdown"
    md_dir.mkdir(exist_ok=True)

    # XGBoost markdown
    xgboost_md_path = md_dir / "xgboost_model_card.md"
    with open(xgboost_md_path, "w") as f:
        f.write(render_model_card_markdown(xgboost_card))
    print(f"  Saved: {xgboost_md_path}")

    # Decision Tree markdown
    dt_md_path = md_dir / "decision_tree_model_card.md"
    with open(dt_md_path, "w") as f:
        f.write(render_model_card_markdown(dt_card))
    print(f"  Saved: {dt_md_path}")

    # Linear Regression markdown
    lr_md_path = md_dir / "linear_regression_model_card.md"
    with open(lr_md_path, "w") as f:
        f.write(render_model_card_markdown(lr_card))
    print(f"  Saved: {lr_md_path}")

    # Data Card markdown
    data_md_path = md_dir / "dynamic_pricing_data_card.md"
    with open(data_md_path, "w") as f:
        f.write(render_data_card_markdown(data_card))
    print(f"  Saved: {data_md_path}")

    print("\n" + "=" * 60)
    print("Card generation complete!")
    print("=" * 60)
    print(f"\nJSON cards: {CARDS_DIR}")
    print(f"Markdown docs: {md_dir}")


if __name__ == "__main__":
    main()

