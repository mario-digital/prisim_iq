"""Evidence and Honeywell mapping response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# --- Model Card Schema (matching existing JSON structure) ---


class ModelHyperparameters(BaseModel):
    """Hyperparameters used in model training."""

    learning_rate: float | None = None
    max_depth: int | None = None
    n_estimators: int | None = None
    # Linear regression fields
    fit_intercept: bool | None = None
    normalize: bool | None = None


class ModelDetails(BaseModel):
    """Details about a trained model."""

    architecture: str = Field(description="Model architecture name")
    hyperparameters: ModelHyperparameters | dict[str, float | int | str | bool] = Field(
        description="Training hyperparameters"
    )
    training_date: str = Field(description="Date model was trained")
    framework: str = Field(description="ML framework used")
    input_features: list[str] = Field(description="Features used by the model")
    output: str = Field(description="Model output description")


class IntendedUse(BaseModel):
    """Intended use cases for the model."""

    primary_use: str = Field(description="Primary use case")
    users: list[str] = Field(description="Intended user groups")
    out_of_scope: list[str] = Field(description="Uses that are out of scope")


class TrainingData(BaseModel):
    """Information about training data."""

    dataset_name: str = Field(description="Name of training dataset")
    dataset_size: int = Field(description="Number of samples")
    features_used: list[str] = Field(description="Features in training data")
    target_variable: str = Field(description="Target variable name")
    train_test_split: str = Field(description="Train/test split description")


class ModelMetrics(BaseModel):
    """Model performance metrics."""

    r2_score: float = Field(description="R² coefficient of determination")
    mae: float = Field(description="Mean Absolute Error")
    rmse: float = Field(description="Root Mean Square Error")
    test_set_size: int = Field(description="Size of test set")


class EthicalConsiderations(BaseModel):
    """Ethical considerations for model use."""

    fairness_considerations: list[str] = Field(description="Fairness notes")
    privacy_considerations: list[str] = Field(description="Privacy notes")
    transparency_notes: list[str] = Field(description="Transparency notes")


class ModelCard(BaseModel):
    """Complete model card following ML model card standards."""

    model_name: str = Field(description="Name of the model")
    model_version: str = Field(description="Version string")
    generated_at: datetime = Field(description="When card was generated")
    model_details: ModelDetails = Field(description="Model architecture details")
    intended_use: IntendedUse = Field(description="Intended use cases")
    training_data: TrainingData = Field(description="Training data info")
    metrics: ModelMetrics = Field(description="Performance metrics")
    ethical_considerations: EthicalConsiderations = Field(description="Ethical notes")
    limitations: list[str] = Field(description="Known limitations")
    feature_importance: dict[str, float] | None = Field(
        default=None, description="Feature importance scores (None for linear models)"
    )
    coefficients: dict[str, float] | None = Field(
        default=None, description="Model coefficients (for linear models)"
    )


# --- Data Card Schema (matching existing JSON structure) ---


class DataFeature(BaseModel):
    """Description of a dataset feature."""

    name: str = Field(description="Feature name")
    dtype: str = Field(description="Data type")
    description: str = Field(description="Feature description")
    range_or_values: str = Field(description="Value range or categories")
    distribution: Literal["continuous", "categorical"] = Field(
        description="Distribution type"
    )


class DataSource(BaseModel):
    """Data source information."""

    origin: str = Field(description="Data origin")
    collection_date: str = Field(description="When data was collected")
    preprocessing_steps: list[str] = Field(description="Preprocessing applied")


class DataStatistics(BaseModel):
    """Dataset statistics."""

    row_count: int = Field(description="Number of rows")
    column_count: int = Field(description="Number of columns")
    missing_values: int = Field(description="Count of missing values")
    numeric_features: int = Field(description="Number of numeric features")
    categorical_features: int = Field(description="Number of categorical features")


class DataCard(BaseModel):
    """Data card documenting the training dataset."""

    dataset_name: str = Field(description="Name of the dataset")
    version: str = Field(description="Dataset version")
    generated_at: datetime = Field(description="When card was generated")
    source: DataSource = Field(description="Data source information")
    features: list[DataFeature] = Field(description="Feature descriptions")
    statistics: DataStatistics = Field(description="Dataset statistics")
    known_biases: list[str] = Field(description="Known biases in data")
    limitations: list[str] = Field(description="Dataset limitations")
    intended_use: str = Field(description="Intended use description")


# --- Methodology Documentation ---


class DocSection(BaseModel):
    """A section of documentation."""

    heading: str = Field(description="Section heading")
    content: str = Field(description="Section content (markdown)")
    subsections: list["DocSection"] | None = Field(
        default=None, description="Nested subsections"
    )


class MethodologyDoc(BaseModel):
    """Methodology documentation."""

    title: str = Field(description="Document title")
    sections: list[DocSection] = Field(description="Document sections")


# --- Evidence Response ---


class EvidenceResponse(BaseModel):
    """Complete evidence package for the Evidence tab."""

    model_cards: list[ModelCard] = Field(description="All model cards")
    data_card: DataCard = Field(description="Training data card")
    methodology: MethodologyDoc = Field(description="Methodology documentation")
    generated_at: datetime = Field(description="When evidence was compiled")
    cache_ttl_seconds: int = Field(
        default=86400, description="Cache TTL in seconds (24 hours)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "model_cards": [],
                    "data_card": {
                        "dataset_name": "Dynamic Pricing Dataset",
                        "version": "1.0.0",
                        "generated_at": "2024-12-02T10:00:00Z",
                        "source": {
                            "origin": "Kaggle",
                            "collection_date": "2024",
                            "preprocessing_steps": ["Loaded from Excel"],
                        },
                        "features": [],
                        "statistics": {
                            "row_count": 1000,
                            "column_count": 11,
                            "missing_values": 0,
                            "numeric_features": 7,
                            "categorical_features": 4,
                        },
                        "known_biases": [],
                        "limitations": [],
                        "intended_use": "Training demand prediction models",
                    },
                    "methodology": {
                        "title": "PrismIQ Methodology",
                        "sections": [],
                    },
                    "generated_at": "2024-12-02T10:00:00Z",
                    "cache_ttl_seconds": 86400,
                }
            ]
        }
    }


# --- Honeywell Mapping ---


class HoneywellMapping(BaseModel):
    """Single mapping from ride-sharing to Honeywell concept."""

    ride_sharing_concept: str = Field(description="Ride-sharing domain concept")
    honeywell_equivalent: str = Field(description="Honeywell enterprise equivalent")
    category: Literal["pricing", "demand", "supply", "customer"] = Field(
        description="Concept category"
    )
    rationale: str = Field(description="Why these concepts map")
    applicability: str = Field(description="How this applies to enterprise")


class HoneywellMappingResponse(BaseModel):
    """Complete Honeywell mapping response."""

    title: str = Field(description="Document title")
    description: str = Field(description="Overview description")
    mappings: list[HoneywellMapping] = Field(description="All concept mappings")
    business_context: str = Field(description="Business context explanation")
    rendered_markdown: str | None = Field(
        default=None, description="Markdown rendering (if format=markdown)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Ride-Sharing to Honeywell Enterprise Mapping",
                    "description": "How dynamic pricing concepts translate",
                    "mappings": [
                        {
                            "ride_sharing_concept": "Number of Riders",
                            "honeywell_equivalent": "Product Demand Forecast",
                            "category": "demand",
                            "rationale": "Both represent demand signals",
                            "applicability": "Any product with variable demand",
                        }
                    ],
                    "business_context": "ML-driven pricing applies to enterprise",
                    "rendered_markdown": None,
                }
            ]
        }
    }

