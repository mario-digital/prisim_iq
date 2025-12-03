"""Unit tests for evidence markdown rendering functions."""

from datetime import UTC, datetime

import pytest

from src.api.routers.evidence import (
    _render_evidence_markdown,
    _render_honeywell_markdown,
)
from src.schemas.evidence import (
    DataCard,
    DataFeature,
    DataSource,
    DataStatistics,
    DocSection,
    EthicalConsiderations,
    EvidenceResponse,
    HoneywellMapping,
    HoneywellMappingResponse,
    IntendedUse,
    MethodologyDoc,
    ModelCard,
    ModelDetails,
    ModelHyperparameters,
    ModelMetrics,
    TrainingData,
)


@pytest.fixture
def sample_model_card() -> ModelCard:
    """Create a sample model card for testing."""
    return ModelCard(
        model_name="Test Model",
        model_version="1.0.0",
        generated_at=datetime(2024, 1, 1, tzinfo=UTC),
        model_details=ModelDetails(
            architecture="XGBoost",
            hyperparameters=ModelHyperparameters(
                learning_rate=0.1,
                max_depth=6,
                n_estimators=100,
            ),
            training_date="2024-01-01",
            framework="scikit-learn",
            input_features=["feature1", "feature2"],
            output="price_prediction",
        ),
        intended_use=IntendedUse(
            primary_use="Price prediction",
            users=["Data Scientists"],
            out_of_scope=["Medical diagnosis"],
        ),
        training_data=TrainingData(
            dataset_name="Test Dataset",
            dataset_size=1000,
            features_used=["feature1", "feature2"],
            target_variable="price",
            train_test_split="80/20",
        ),
        metrics=ModelMetrics(
            r2_score=0.95,
            mae=1.5,
            rmse=2.0,
            test_set_size=200,
        ),
        ethical_considerations=EthicalConsiderations(
            fairness_considerations=["Equal treatment"],
            privacy_considerations=["No PII"],
            transparency_notes=["Model is explainable"],
        ),
        limitations=["Limited to certain conditions", "Requires clean data"],
        feature_importance={"feature1": 0.6, "feature2": 0.4},
    )


@pytest.fixture
def sample_data_card() -> DataCard:
    """Create a sample data card for testing."""
    return DataCard(
        dataset_name="Test Dataset",
        version="1.0.0",
        generated_at=datetime(2024, 1, 1, tzinfo=UTC),
        source=DataSource(
            origin="Internal",
            collection_date="2024-01-01",
            preprocessing_steps=["Normalization", "Feature scaling"],
        ),
        features=[
            DataFeature(
                name="price",
                dtype="float",
                description="Price value",
                range_or_values="10-100",
                distribution="continuous",
            )
        ],
        statistics=DataStatistics(
            row_count=1000,
            column_count=10,
            missing_values=0,
            numeric_features=8,
            categorical_features=2,
        ),
        known_biases=["Urban bias"],
        limitations=["Limited time range"],
        intended_use="Model training",
    )


@pytest.fixture
def sample_methodology() -> MethodologyDoc:
    """Create a sample methodology document for testing."""
    return MethodologyDoc(
        title="Test Methodology",
        sections=[
            DocSection(
                heading="Overview",
                content="This is the overview section.",
                subsections=[
                    DocSection(
                        heading="Details",
                        content="Detailed information here.",
                        subsections=None,
                    )
                ],
            ),
            DocSection(
                heading="Implementation",
                content="Implementation details.",
                subsections=None,
            ),
        ],
    )


@pytest.fixture
def sample_evidence_response(
    sample_model_card: ModelCard,
    sample_data_card: DataCard,
    sample_methodology: MethodologyDoc,
) -> EvidenceResponse:
    """Create a sample evidence response for testing."""
    return EvidenceResponse(
        model_cards=[sample_model_card],
        data_card=sample_data_card,
        methodology=sample_methodology,
        generated_at=datetime(2024, 1, 1, tzinfo=UTC),
        cache_ttl_seconds=86400,
    )


@pytest.fixture
def sample_honeywell_mapping() -> HoneywellMappingResponse:
    """Create a sample Honeywell mapping response for testing."""
    return HoneywellMappingResponse(
        title="Test Mapping",
        description="Test description",
        mappings=[
            HoneywellMapping(
                ride_sharing_concept="Riders",
                honeywell_equivalent="Demand Forecast",
                category="demand",
                rationale="Both represent demand",
                applicability="General",
            ),
            HoneywellMapping(
                ride_sharing_concept="Surge Pricing",
                honeywell_equivalent="Dynamic Pricing",
                category="pricing",
                rationale="Price adjustments",
                applicability="Energy sector",
            ),
        ],
        business_context="Enterprise pricing context.",
        rendered_markdown=None,
    )


class TestRenderEvidenceMarkdown:
    """Tests for _render_evidence_markdown function."""

    def test_returns_string(self, sample_evidence_response: EvidenceResponse) -> None:
        """Test that render returns a string."""
        result = _render_evidence_markdown(sample_evidence_response)
        assert isinstance(result, str)

    def test_contains_main_heading(
        self, sample_evidence_response: EvidenceResponse
    ) -> None:
        """Test that output contains main heading."""
        result = _render_evidence_markdown(sample_evidence_response)
        assert "# PrismIQ Evidence Documentation" in result

    def test_contains_methodology_title(
        self, sample_evidence_response: EvidenceResponse
    ) -> None:
        """Test that output contains methodology title."""
        result = _render_evidence_markdown(sample_evidence_response)
        assert "## Test Methodology" in result

    def test_contains_methodology_sections(
        self, sample_evidence_response: EvidenceResponse
    ) -> None:
        """Test that output contains methodology sections."""
        result = _render_evidence_markdown(sample_evidence_response)
        assert "### Overview" in result
        assert "### Implementation" in result

    def test_contains_methodology_subsections(
        self, sample_evidence_response: EvidenceResponse
    ) -> None:
        """Test that output contains methodology subsections."""
        result = _render_evidence_markdown(sample_evidence_response)
        assert "#### Details" in result

    def test_contains_model_cards_section(
        self, sample_evidence_response: EvidenceResponse
    ) -> None:
        """Test that output contains model cards section."""
        result = _render_evidence_markdown(sample_evidence_response)
        assert "## Model Cards" in result

    def test_contains_model_card_details(
        self, sample_evidence_response: EvidenceResponse
    ) -> None:
        """Test that output contains model card details."""
        result = _render_evidence_markdown(sample_evidence_response)
        assert "### Test Model (v1.0.0)" in result
        assert "**Architecture:** XGBoost" in result
        assert "**Primary Use:** Price prediction" in result
        assert "R²=0.9500" in result

    def test_contains_model_limitations(
        self, sample_evidence_response: EvidenceResponse
    ) -> None:
        """Test that output contains model limitations."""
        result = _render_evidence_markdown(sample_evidence_response)
        assert "**Limitations:**" in result
        assert "- Limited to certain conditions" in result

    def test_contains_data_card_section(
        self, sample_evidence_response: EvidenceResponse
    ) -> None:
        """Test that output contains data card section."""
        result = _render_evidence_markdown(sample_evidence_response)
        assert "## Data Card" in result

    def test_contains_data_card_details(
        self, sample_evidence_response: EvidenceResponse
    ) -> None:
        """Test that output contains data card details."""
        result = _render_evidence_markdown(sample_evidence_response)
        assert "### Test Dataset (v1.0.0)" in result
        assert "**Source:** Internal" in result
        assert "1000 rows" in result
        assert "10 columns" in result

    def test_contains_timestamp(
        self, sample_evidence_response: EvidenceResponse
    ) -> None:
        """Test that output contains generated timestamp."""
        result = _render_evidence_markdown(sample_evidence_response)
        assert "*Generated:" in result


class TestRenderHoneywellMarkdown:
    """Tests for _render_honeywell_markdown function."""

    def test_returns_string(self, sample_honeywell_mapping: HoneywellMappingResponse) -> None:
        """Test that render returns a string."""
        result = _render_honeywell_markdown(sample_honeywell_mapping)
        assert isinstance(result, str)

    def test_contains_title(
        self, sample_honeywell_mapping: HoneywellMappingResponse
    ) -> None:
        """Test that output contains title."""
        result = _render_honeywell_markdown(sample_honeywell_mapping)
        assert "# Test Mapping" in result

    def test_contains_description(
        self, sample_honeywell_mapping: HoneywellMappingResponse
    ) -> None:
        """Test that output contains description."""
        result = _render_honeywell_markdown(sample_honeywell_mapping)
        assert "Test description" in result

    def test_contains_table_header(
        self, sample_honeywell_mapping: HoneywellMappingResponse
    ) -> None:
        """Test that output contains markdown table header."""
        result = _render_honeywell_markdown(sample_honeywell_mapping)
        assert "| Ride-Sharing Concept | Honeywell Equivalent | Category | Rationale |" in result
        assert "|---------------------|---------------------|----------|----------|" in result

    def test_contains_mapping_rows(
        self, sample_honeywell_mapping: HoneywellMappingResponse
    ) -> None:
        """Test that output contains mapping data rows."""
        result = _render_honeywell_markdown(sample_honeywell_mapping)
        assert "| Riders | Demand Forecast | demand | Both represent demand |" in result
        assert "| Surge Pricing | Dynamic Pricing | pricing | Price adjustments |" in result

    def test_contains_business_context_section(
        self, sample_honeywell_mapping: HoneywellMappingResponse
    ) -> None:
        """Test that output contains business context section."""
        result = _render_honeywell_markdown(sample_honeywell_mapping)
        assert "## Business Context" in result
        assert "Enterprise pricing context." in result

    def test_empty_mappings_produces_valid_markdown(self) -> None:
        """Test that empty mappings still produces valid markdown structure."""
        empty_mapping = HoneywellMappingResponse(
            title="Empty Mapping",
            description="No mappings yet",
            mappings=[],
            business_context="Context here.",
            rendered_markdown=None,
        )
        result = _render_honeywell_markdown(empty_mapping)
        assert "# Empty Mapping" in result
        assert "| Ride-Sharing Concept |" in result
        assert "## Business Context" in result

