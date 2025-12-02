"""Unit tests for segmenter module."""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.ml.preprocessor import load_dataset
from src.ml.segmenter import Segmenter, analyze_optimal_k
from src.schemas.market import MarketContext
from src.schemas.segment import SegmentResult


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Create a sample DataFrame for clustering tests."""
    np.random.seed(42)
    n_samples = 100

    locations = ["Urban", "Suburban", "Rural"]
    times = ["Morning", "Afternoon", "Evening", "Night"]
    vehicles = ["Economy", "Premium"]

    return pd.DataFrame(
        {
            "Number_of_Riders": np.random.randint(5, 50, n_samples),
            "Number_of_Drivers": np.random.randint(3, 30, n_samples),
            "Location_Category": np.random.choice(locations, n_samples),
            "Customer_Loyalty_Status": np.random.choice(["Gold", "Silver", "Regular"], n_samples),
            "Number_of_Past_Rides": np.random.randint(1, 100, n_samples),
            "Average_Ratings": np.random.uniform(3.0, 5.0, n_samples),
            "Time_of_Booking": np.random.choice(times, n_samples),
            "Vehicle_Type": np.random.choice(vehicles, n_samples),
            "Expected_Ride_Duration": np.random.randint(10, 60, n_samples),
            "Historical_Cost_of_Ride": np.random.uniform(10, 50, n_samples),
            "supply_demand_ratio": np.random.uniform(0.3, 2.0, n_samples),
        }
    )


@pytest.fixture
def fitted_segmenter(sample_dataframe: pd.DataFrame) -> Segmenter:
    """Create a fitted segmenter for tests."""
    segmenter = Segmenter(n_clusters=4, random_state=42)
    segmenter.fit(sample_dataframe)
    return segmenter


@pytest.fixture
def sample_context() -> MarketContext:
    """Create a sample market context for classification."""
    return MarketContext(
        number_of_riders=50,
        number_of_drivers=40,
        location_category="Urban",
        customer_loyalty_status="Gold",
        number_of_past_rides=20,
        average_ratings=4.5,
        time_of_booking="Morning",
        vehicle_type="Premium",
        expected_ride_duration=30,
        historical_cost_of_ride=35.0,
    )


class TestSegmenterInit:
    """Tests for Segmenter initialization."""

    def test_default_init(self) -> None:
        """Test default initialization values."""
        segmenter = Segmenter()

        assert segmenter.n_clusters == 6
        assert segmenter.random_state == 42
        assert not segmenter.is_fitted

    def test_custom_init(self) -> None:
        """Test custom initialization values."""
        segmenter = Segmenter(n_clusters=4, random_state=123)

        assert segmenter.n_clusters == 4
        assert segmenter.random_state == 123


class TestSegmenterFit:
    """Tests for Segmenter.fit() method."""

    def test_fit_success(self, sample_dataframe: pd.DataFrame) -> None:
        """Test successful fitting."""
        segmenter = Segmenter(n_clusters=4, random_state=42)
        result = segmenter.fit(sample_dataframe)

        assert segmenter.is_fitted
        assert result is segmenter  # Method chaining
        assert segmenter.kmeans is not None
        assert segmenter.scaler is not None

    def test_fit_creates_segment_labels(self, sample_dataframe: pd.DataFrame) -> None:
        """Test fitting creates segment labels."""
        segmenter = Segmenter(n_clusters=4, random_state=42)
        segmenter.fit(sample_dataframe)

        assert len(segmenter.segment_labels) == 4
        for label in segmenter.segment_labels.values():
            assert isinstance(label, str)
            assert "_" in label  # Format: Location_TimeProfile_Vehicle

    def test_fit_creates_cluster_characteristics(self, sample_dataframe: pd.DataFrame) -> None:
        """Test fitting creates cluster characteristics."""
        segmenter = Segmenter(n_clusters=4, random_state=42)
        segmenter.fit(sample_dataframe)

        assert len(segmenter.cluster_characteristics) == 4
        for char in segmenter.cluster_characteristics.values():
            assert "avg_supply_demand_ratio" in char
            assert "sample_count" in char

    def test_fit_with_real_data(self) -> None:
        """Test fitting with real dataset."""
        df = load_dataset()
        segmenter = Segmenter(n_clusters=6, random_state=42)
        segmenter.fit(df)

        assert segmenter.is_fitted
        assert len(segmenter.segment_labels) == 6


class TestSegmenterClassify:
    """Tests for Segmenter.classify() method."""

    def test_classify_returns_segment_result(
        self,
        fitted_segmenter: Segmenter,
        sample_context: MarketContext,
    ) -> None:
        """Test classification returns SegmentResult."""
        result = fitted_segmenter.classify(sample_context)

        assert isinstance(result, SegmentResult)
        assert isinstance(result.segment_name, str)
        assert isinstance(result.cluster_id, int)
        assert isinstance(result.centroid_distance, float)

    def test_classify_valid_cluster_id(
        self,
        fitted_segmenter: Segmenter,
        sample_context: MarketContext,
    ) -> None:
        """Test classification returns valid cluster ID."""
        result = fitted_segmenter.classify(sample_context)

        assert 0 <= result.cluster_id < fitted_segmenter.n_clusters

    def test_classify_centroid_distance_positive(
        self,
        fitted_segmenter: Segmenter,
        sample_context: MarketContext,
    ) -> None:
        """Test centroid distance is positive."""
        result = fitted_segmenter.classify(sample_context)

        assert result.centroid_distance >= 0

    def test_classify_unfitted_raises(self, sample_context: MarketContext) -> None:
        """Test classification on unfitted segmenter raises error."""
        segmenter = Segmenter()

        with pytest.raises(RuntimeError, match="must be fitted"):
            segmenter.classify(sample_context)

    def test_classify_different_contexts(self, fitted_segmenter: Segmenter) -> None:
        """Test different contexts may get different segments."""
        context1 = MarketContext(
            number_of_riders=100,
            number_of_drivers=30,  # Low supply = 0.3 ratio
            location_category="Urban",
            customer_loyalty_status="Gold",
            number_of_past_rides=50,
            average_ratings=4.8,
            time_of_booking="Morning",
            vehicle_type="Premium",
            expected_ride_duration=25,
            historical_cost_of_ride=45.0,
        )
        context2 = MarketContext(
            number_of_riders=10,
            number_of_drivers=20,  # High supply = 2.0 ratio
            location_category="Rural",
            customer_loyalty_status="Bronze",
            number_of_past_rides=5,
            average_ratings=3.5,
            time_of_booking="Night",
            vehicle_type="Economy",
            expected_ride_duration=15,
            historical_cost_of_ride=15.0,
        )

        result1 = fitted_segmenter.classify(context1)
        result2 = fitted_segmenter.classify(context2)

        # Different contexts should have different characteristics
        # (may or may not be different clusters depending on data)
        assert result1.segment_name is not None
        assert result2.segment_name is not None

    def test_classify_consistency(
        self,
        fitted_segmenter: Segmenter,
        sample_context: MarketContext,
    ) -> None:
        """Test same context always gets same segment."""
        result1 = fitted_segmenter.classify(sample_context)
        result2 = fitted_segmenter.classify(sample_context)

        assert result1.cluster_id == result2.cluster_id
        assert result1.segment_name == result2.segment_name
        assert result1.centroid_distance == result2.centroid_distance


class TestSegmenterPersistence:
    """Tests for Segmenter save/load functionality."""

    def test_save_creates_file(self, fitted_segmenter: Segmenter) -> None:
        """Test save creates model file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "segmenter.joblib"
            result_path = fitted_segmenter.save(save_path)

            assert result_path.exists()
            assert result_path == save_path

    def test_save_unfitted_raises(self) -> None:
        """Test saving unfitted segmenter raises error."""
        segmenter = Segmenter()

        with pytest.raises(RuntimeError, match="Cannot save unfitted"):
            segmenter.save()

    def test_load_success(self, fitted_segmenter: Segmenter) -> None:
        """Test successful model loading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "segmenter.joblib"
            fitted_segmenter.save(save_path)

            loaded = Segmenter.load(save_path)

            assert loaded.is_fitted
            assert loaded.n_clusters == fitted_segmenter.n_clusters
            assert loaded.segment_labels == fitted_segmenter.segment_labels

    def test_load_not_found(self) -> None:
        """Test load with nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            Segmenter.load("/nonexistent/path/model.joblib")

    def test_load_classify_consistency(
        self,
        fitted_segmenter: Segmenter,
        sample_context: MarketContext,
    ) -> None:
        """Test loaded model gives same classification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "segmenter.joblib"
            fitted_segmenter.save(save_path)

            original_result = fitted_segmenter.classify(sample_context)

            loaded = Segmenter.load(save_path)
            loaded_result = loaded.classify(sample_context)

            assert original_result.cluster_id == loaded_result.cluster_id
            assert original_result.segment_name == loaded_result.segment_name
            assert original_result.centroid_distance == pytest.approx(
                loaded_result.centroid_distance
            )


class TestSegmentDistribution:
    """Tests for get_segment_distribution method."""

    def test_distribution_structure(self, fitted_segmenter: Segmenter) -> None:
        """Test segment distribution structure."""
        distribution = fitted_segmenter.get_segment_distribution()

        assert "n_clusters" in distribution
        assert "segments" in distribution
        assert distribution["n_clusters"] == fitted_segmenter.n_clusters
        assert len(distribution["segments"]) == fitted_segmenter.n_clusters

    def test_distribution_segment_info(self, fitted_segmenter: Segmenter) -> None:
        """Test segment info in distribution."""
        distribution = fitted_segmenter.get_segment_distribution()

        for _segment_name, info in distribution["segments"].items():
            assert "cluster_id" in info
            assert "avg_supply_demand_ratio" in info
            assert "sample_count" in info

    def test_distribution_unfitted_raises(self) -> None:
        """Test distribution on unfitted segmenter raises error."""
        segmenter = Segmenter()

        with pytest.raises(RuntimeError, match="must be fitted"):
            segmenter.get_segment_distribution()


class TestAnalyzeOptimalK:
    """Tests for analyze_optimal_k function."""

    def test_analyze_returns_structure(self, sample_dataframe: pd.DataFrame) -> None:
        """Test analysis returns expected structure."""
        result = analyze_optimal_k(sample_dataframe, k_range=range(2, 6))

        assert "k_range" in result
        assert "inertias" in result
        assert "silhouette_scores" in result
        assert "elbow_k" in result
        assert "best_silhouette_k" in result
        assert "recommended_k" in result
        assert "rationale" in result

    def test_analyze_inertias_decrease(self, sample_dataframe: pd.DataFrame) -> None:
        """Test inertias generally decrease with more clusters."""
        result = analyze_optimal_k(sample_dataframe, k_range=range(2, 6))

        inertias = result["inertias"]
        # Inertia should generally decrease (or stay same) with more clusters
        assert inertias[0] >= inertias[-1]

    def test_analyze_silhouette_valid_range(self, sample_dataframe: pd.DataFrame) -> None:
        """Test silhouette scores are in valid range [-1, 1]."""
        result = analyze_optimal_k(sample_dataframe, k_range=range(2, 6))

        for score in result["silhouette_scores"]:
            assert -1 <= score <= 1

    def test_analyze_recommended_k_in_range(self, sample_dataframe: pd.DataFrame) -> None:
        """Test recommended k is within tested range."""
        k_range = range(2, 6)
        result = analyze_optimal_k(sample_dataframe, k_range=k_range)

        assert result["recommended_k"] in k_range

    def test_analyze_with_real_data(self) -> None:
        """Test analysis with real dataset."""
        df = load_dataset()
        result = analyze_optimal_k(df, k_range=range(3, 8))

        assert result["recommended_k"] >= 3
        assert result["recommended_k"] <= 7
        assert len(result["inertias"]) == 5

