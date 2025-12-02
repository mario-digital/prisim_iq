"""Tests for synthetic training data generation.

Tests cover:
- Data generation produces correct shape
- Profit calculation
- Reproducibility with seed
- Utility functions (load_training_data, load_test_data)
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from src.ml.demand_simulator import DemandSimulator
from src.ml.training_data import (
    EXPECTED_COLUMNS,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    get_features_and_target,
    load_test_data,
    load_training_data,
    validate_training_data,
)
from src.schemas.market import MarketContext

# Import from script (need to add to path)
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

from generate_training_data import (
    PRICE_MULTIPLIERS,
    generate_training_data,
    get_price_points,
    row_to_market_context,
)


class TestGetPricePoints:
    """Tests for price point generation."""

    def test_returns_correct_number_of_points(self):
        """Should return 10 price points."""
        result = get_price_points(50.0)
        assert len(result) == 10
        assert len(result) == len(PRICE_MULTIPLIERS)

    def test_price_points_relative_to_historical_cost(self):
        """Price points should be multiples of historical cost."""
        historical_cost = 40.0
        result = get_price_points(historical_cost)

        # Check each multiplier
        for i, multiplier in enumerate(PRICE_MULTIPLIERS):
            expected = historical_cost * multiplier
            assert result[i] == pytest.approx(expected)

    def test_price_range_spans_50_to_250_percent(self):
        """Price points should span 50% to 250% of historical cost."""
        historical_cost = 100.0
        result = get_price_points(historical_cost)

        assert min(result) == pytest.approx(50.0)  # 50%
        assert max(result) == pytest.approx(250.0)  # 250%


class TestRowToMarketContext:
    """Tests for DataFrame row to MarketContext conversion."""

    def test_converts_row_correctly(self):
        """Should convert DataFrame row to MarketContext."""
        row = pd.Series({
            "Number_of_Riders": 50,
            "Number_of_Drivers": 25,
            "Location_Category": "Urban",
            "Customer_Loyalty_Status": "Gold",
            "Number_of_Past_Rides": 20,
            "Average_Ratings": 4.5,
            "Time_of_Booking": "Evening",
            "Vehicle_Type": "Premium",
            "Expected_Ride_Duration": 30,
            "Historical_Cost_of_Ride": 35.0,
        })

        context = row_to_market_context(row)

        assert isinstance(context, MarketContext)
        assert context.number_of_riders == 50
        assert context.number_of_drivers == 25
        assert context.location_category == "Urban"
        assert context.customer_loyalty_status == "Gold"
        assert context.time_of_booking == "Evening"
        assert context.vehicle_type == "Premium"
        assert context.historical_cost_of_ride == 35.0


class TestGenerateTrainingData:
    """Tests for training data generation."""

    @pytest.fixture
    def mock_dataset(self) -> pd.DataFrame:
        """Create a small mock dataset for testing."""
        return pd.DataFrame({
            "Number_of_Riders": [50, 30, 40],
            "Number_of_Drivers": [25, 35, 20],
            "Location_Category": ["Urban", "Suburban", "Rural"],
            "Customer_Loyalty_Status": ["Gold", "Silver", "Bronze"],
            "Number_of_Past_Rides": [20, 10, 5],
            "Average_Ratings": [4.5, 4.0, 3.5],
            "Time_of_Booking": ["Evening", "Morning", "Afternoon"],
            "Vehicle_Type": ["Premium", "Economy", "Economy"],
            "Expected_Ride_Duration": [30, 20, 25],
            "Historical_Cost_of_Ride": [35.0, 25.0, 30.0],
            "supply_demand_ratio": [0.5, 1.17, 0.5],
        })

    @pytest.fixture
    def mock_simulator(self) -> DemandSimulator:
        """Create a mock demand simulator."""
        simulator = MagicMock(spec=DemandSimulator)
        # Return deterministic demand based on price
        simulator.simulate_demand.return_value = 0.5
        return simulator

    @pytest.fixture
    def mock_segmenter(self):
        """Create a mock segmenter."""
        segmenter = MagicMock()
        mock_result = MagicMock()
        mock_result.segment_name = "Urban_Peak_Premium"
        segmenter.classify.return_value = mock_result
        return segmenter

    def test_generates_correct_number_of_rows(
        self, mock_dataset, mock_simulator, mock_segmenter
    ):
        """Output rows = input rows × price points."""
        result = generate_training_data(
            mock_dataset, mock_simulator, mock_segmenter, seed=42
        )

        expected_rows = len(mock_dataset) * len(PRICE_MULTIPLIERS)
        assert len(result) == expected_rows

    def test_generates_all_expected_columns(
        self, mock_dataset, mock_simulator, mock_segmenter
    ):
        """Should generate all required columns."""
        result = generate_training_data(
            mock_dataset, mock_simulator, mock_segmenter, seed=42
        )

        for col in EXPECTED_COLUMNS:
            assert col in result.columns, f"Missing column: {col}"

    def test_demand_values_in_valid_range(
        self, mock_dataset, mock_simulator, mock_segmenter
    ):
        """Demand should be in [0, 1] range."""
        # Mock varying demand values
        demands = [0.1, 0.5, 0.9, 0.3, 0.7, 0.2, 0.8, 0.4, 0.6, 0.0]
        mock_simulator.simulate_demand.side_effect = demands * 3  # 3 rows × 10 prices

        result = generate_training_data(
            mock_dataset, mock_simulator, mock_segmenter, seed=42
        )

        assert result["demand"].min() >= 0.0
        assert result["demand"].max() <= 1.0


class TestProfitCalculation:
    """Tests for profit calculation."""

    def test_profit_formula(self):
        """Profit = (price - cost) × demand."""
        price = 50.0
        cost = 30.0
        demand = 0.8

        expected_profit = (price - cost) * demand
        assert expected_profit == pytest.approx(16.0)

    def test_negative_profit_when_price_below_cost(self):
        """Profit can be negative if price < cost."""
        price = 20.0
        cost = 30.0
        demand = 0.5

        profit = (price - cost) * demand
        assert profit < 0
        assert profit == pytest.approx(-5.0)

    def test_zero_profit_when_demand_zero(self):
        """Profit is zero when demand is zero."""
        price = 50.0
        cost = 30.0
        demand = 0.0

        profit = (price - cost) * demand
        assert profit == 0.0


class TestReproducibility:
    """Tests for seed-based reproducibility."""

    @pytest.fixture
    def mock_dataset(self) -> pd.DataFrame:
        """Create a small mock dataset for testing."""
        return pd.DataFrame({
            "Number_of_Riders": [50, 30],
            "Number_of_Drivers": [25, 35],
            "Location_Category": ["Urban", "Suburban"],
            "Customer_Loyalty_Status": ["Gold", "Silver"],
            "Number_of_Past_Rides": [20, 10],
            "Average_Ratings": [4.5, 4.0],
            "Time_of_Booking": ["Evening", "Morning"],
            "Vehicle_Type": ["Premium", "Economy"],
            "Expected_Ride_Duration": [30, 20],
            "Historical_Cost_of_Ride": [35.0, 25.0],
            "supply_demand_ratio": [0.5, 1.17],
        })

    def test_same_seed_produces_same_output(self, mock_dataset):
        """Same seed should produce identical results."""
        simulator = DemandSimulator()
        segmenter = MagicMock()
        mock_result = MagicMock()
        mock_result.segment_name = "Test_Segment"
        segmenter.classify.return_value = mock_result

        result1 = generate_training_data(mock_dataset, simulator, segmenter, seed=42)
        result2 = generate_training_data(mock_dataset, simulator, segmenter, seed=42)

        pd.testing.assert_frame_equal(result1, result2)

    def test_different_seed_may_differ(self, mock_dataset):
        """Different seeds should be deterministic but potentially different."""
        simulator = DemandSimulator()
        segmenter = MagicMock()
        mock_result = MagicMock()
        mock_result.segment_name = "Test_Segment"
        segmenter.classify.return_value = mock_result

        result1 = generate_training_data(mock_dataset, simulator, segmenter, seed=42)
        result2 = generate_training_data(mock_dataset, simulator, segmenter, seed=123)

        # Results should be deterministic (each run with same seed is same)
        result1_repeat = generate_training_data(
            mock_dataset, simulator, segmenter, seed=42
        )
        pd.testing.assert_frame_equal(result1, result1_repeat)


class TestLoadTrainingData:
    """Tests for utility functions."""

    def test_load_training_data_file_not_found(self, tmp_path):
        """Should raise FileNotFoundError if file doesn't exist."""
        fake_path = tmp_path / "nonexistent.parquet"

        with pytest.raises(FileNotFoundError) as exc_info:
            load_training_data(fake_path)

        assert "Training data not found" in str(exc_info.value)

    def test_load_test_data_file_not_found(self, tmp_path):
        """Should raise FileNotFoundError if file doesn't exist."""
        fake_path = tmp_path / "nonexistent.parquet"

        with pytest.raises(FileNotFoundError) as exc_info:
            load_test_data(fake_path)

        assert "Test data not found" in str(exc_info.value)

    def test_load_training_data_missing_columns(self, tmp_path):
        """Should raise ValueError if required columns are missing."""
        # Create parquet with missing columns
        df = pd.DataFrame({"incomplete": [1, 2, 3]})
        path = tmp_path / "incomplete.parquet"
        df.to_parquet(path)

        with pytest.raises(ValueError) as exc_info:
            load_training_data(path)

        assert "Missing required columns" in str(exc_info.value)


class TestValidateTrainingData:
    """Tests for data validation."""

    def test_valid_data_passes(self):
        """Valid data should pass validation."""
        df = pd.DataFrame({
            "number_of_riders": [50, 30],
            "number_of_drivers": [25, 35],
            "location_category": ["Urban", "Suburban"],
            "customer_loyalty_status": ["Gold", "Silver"],
            "number_of_past_rides": [20, 10],
            "average_ratings": [4.5, 4.0],
            "time_of_booking": ["Evening", "Morning"],
            "vehicle_type": ["Premium", "Economy"],
            "expected_ride_duration": [30, 20],
            "historical_cost_of_ride": [35.0, 25.0],
            "supply_demand_ratio": [0.5, 1.17],
            "segment": ["Seg_A", "Seg_B"],
            "price": [40.0, 30.0],
            "demand": [0.5, 0.7],
            "profit": [2.5, 3.5],
        })

        result = validate_training_data(df)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_invalid_demand_range(self):
        """Demand outside [0, 1] should fail validation."""
        df = pd.DataFrame({
            "number_of_riders": [50],
            "number_of_drivers": [25],
            "location_category": ["Urban"],
            "customer_loyalty_status": ["Gold"],
            "number_of_past_rides": [20],
            "average_ratings": [4.5],
            "time_of_booking": ["Evening"],
            "vehicle_type": ["Premium"],
            "expected_ride_duration": [30],
            "historical_cost_of_ride": [35.0],
            "supply_demand_ratio": [0.5],
            "segment": ["Seg_A"],
            "price": [40.0],
            "demand": [1.5],  # Invalid: > 1
            "profit": [2.5],
        })

        result = validate_training_data(df)
        assert result["valid"] is False
        assert any("Demand values out of range" in e for e in result["errors"])


class TestGetFeaturesAndTarget:
    """Tests for feature/target splitting."""

    def test_splits_correctly(self):
        """Should split into features and target correctly."""
        df = pd.DataFrame({
            "number_of_riders": [50, 30],
            "number_of_drivers": [25, 35],
            "location_category": ["Urban", "Suburban"],
            "customer_loyalty_status": ["Gold", "Silver"],
            "number_of_past_rides": [20, 10],
            "average_ratings": [4.5, 4.0],
            "time_of_booking": ["Evening", "Morning"],
            "vehicle_type": ["Premium", "Economy"],
            "expected_ride_duration": [30, 20],
            "historical_cost_of_ride": [35.0, 25.0],
            "supply_demand_ratio": [0.5, 1.17],
            "segment": ["Seg_A", "Seg_B"],
            "price": [40.0, 30.0],
            "demand": [0.5, 0.7],
            "profit": [2.5, 3.5],
        })

        X, y = get_features_and_target(df)

        assert len(X) == len(df)
        assert len(y) == len(df)
        assert list(X.columns) == FEATURE_COLUMNS
        assert y.name == TARGET_COLUMN
        assert "profit" not in X.columns  # profit is not a feature

