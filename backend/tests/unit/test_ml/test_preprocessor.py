"""Unit tests for preprocessor module."""

import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.ml.preprocessor import (
    CATEGORICAL_COLUMNS,
    EXPECTED_COLUMNS,
    export_eda_summary,
    get_basic_stats,
    get_descriptive_stats,
    get_eda_summary,
    get_feature_distributions,
    load_dataset,
)


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Create a sample DataFrame matching the expected schema."""
    return pd.DataFrame(
        {
            "Number_of_Riders": [10, 20, 30, 0, 15],
            "Number_of_Drivers": [5, 10, 15, 8, 12],
            "Location_Category": ["Urban", "Suburban", "Rural", "Urban", "Urban"],
            "Customer_Loyalty_Status": ["Gold", "Silver", "Bronze", "Platinum", "Gold"],
            "Number_of_Past_Rides": [50, 25, 10, 100, 75],
            "Average_Ratings": [4.5, 4.0, 3.5, 5.0, 4.2],
            "Time_of_Booking": ["Morning", "Afternoon", "Evening", "Night", "Morning"],
            "Vehicle_Type": ["Economy", "Premium", "Economy", "Premium", "Economy"],
            "Expected_Ride_Duration": [15, 30, 45, 20, 25],
            "Historical_Cost_of_Ride": [12.50, 25.00, 18.75, 35.00, 22.50],
        }
    )


@pytest.fixture
def sample_excel_file(sample_dataframe: pd.DataFrame, tmp_path: Path) -> Path:
    """Create a temporary Excel file with sample data."""
    file_path = tmp_path / "test_data.xlsx"
    sample_dataframe.to_excel(file_path, index=False)
    return file_path


class TestLoadDataset:
    """Tests for load_dataset function."""

    def test_load_dataset_success(self, sample_excel_file: Path) -> None:
        """Test successful dataset loading."""
        df = load_dataset(sample_excel_file)

        assert len(df) == 5
        assert "supply_demand_ratio" in df.columns
        # All expected columns plus derived column
        assert len(df.columns) == len(EXPECTED_COLUMNS) + 1

    def test_load_dataset_file_not_found(self, tmp_path: Path) -> None:
        """Test error when file does not exist."""
        with pytest.raises(FileNotFoundError):
            load_dataset(tmp_path / "nonexistent.xlsx")

    def test_load_dataset_missing_columns(self, tmp_path: Path) -> None:
        """Test error when required columns are missing."""
        df = pd.DataFrame({"invalid_column": [1, 2, 3]})
        file_path = tmp_path / "invalid.xlsx"
        df.to_excel(file_path, index=False)

        with pytest.raises(ValueError, match="Missing required columns"):
            load_dataset(file_path)

    def test_supply_demand_ratio_calculation(self, sample_excel_file: Path) -> None:
        """Test supply_demand_ratio is correctly calculated."""
        df = load_dataset(sample_excel_file)

        # Row 0: 5/10 = 0.5
        assert df.loc[0, "supply_demand_ratio"] == 0.5
        # Row 1: 10/20 = 0.5
        assert df.loc[1, "supply_demand_ratio"] == 0.5

    def test_supply_demand_ratio_division_by_zero(self, sample_excel_file: Path) -> None:
        """Test supply_demand_ratio handles zero riders."""
        df = load_dataset(sample_excel_file)

        # Row 3 has 0 riders, should be infinity
        assert np.isinf(df.loc[3, "supply_demand_ratio"])

    def test_load_real_dataset(self) -> None:
        """Test loading the actual dynamic_pricing.xlsx file."""
        # Use default path
        df = load_dataset()

        assert len(df) > 0
        assert "supply_demand_ratio" in df.columns
        for col in EXPECTED_COLUMNS:
            assert col in df.columns


class TestGetBasicStats:
    """Tests for get_basic_stats function."""

    def test_basic_stats_structure(self, sample_dataframe: pd.DataFrame) -> None:
        """Test basic stats returns expected structure."""
        # Add supply_demand_ratio as load_dataset would
        sample_dataframe["supply_demand_ratio"] = (
            sample_dataframe["Number_of_Drivers"] / sample_dataframe["Number_of_Riders"]
        )

        stats = get_basic_stats(sample_dataframe)

        assert "row_count" in stats
        assert "column_count" in stats
        assert "columns" in stats
        assert stats["row_count"] == 5
        assert stats["column_count"] == 11  # 10 original + 1 derived

    def test_column_info(self, sample_dataframe: pd.DataFrame) -> None:
        """Test per-column information is correct."""
        stats = get_basic_stats(sample_dataframe)

        assert "Number_of_Riders" in stats["columns"]
        riders_info = stats["columns"]["Number_of_Riders"]
        assert "dtype" in riders_info
        assert "missing_count" in riders_info
        assert "unique_count" in riders_info
        assert riders_info["missing_count"] == 0

    def test_missing_values_counted(self) -> None:
        """Test missing values are correctly counted."""
        df = pd.DataFrame(
            {
                "col_with_nulls": [1, None, 3, None, 5],
                "col_complete": [1, 2, 3, 4, 5],
            }
        )
        stats = get_basic_stats(df)

        assert stats["columns"]["col_with_nulls"]["missing_count"] == 2
        assert stats["columns"]["col_complete"]["missing_count"] == 0


class TestGetDescriptiveStats:
    """Tests for get_descriptive_stats function."""

    def test_descriptive_stats_structure(self, sample_dataframe: pd.DataFrame) -> None:
        """Test descriptive stats returns expected structure."""
        stats = get_descriptive_stats(sample_dataframe)

        # Should only contain numeric columns
        assert "Number_of_Riders" in stats
        assert "Location_Category" not in stats  # Categorical, not numeric

    def test_stats_values(self, sample_dataframe: pd.DataFrame) -> None:
        """Test statistical values are correct."""
        stats = get_descriptive_stats(sample_dataframe)

        riders_stats = stats["Number_of_Riders"]
        assert "mean" in riders_stats
        assert "std" in riders_stats
        assert "min" in riders_stats
        assert "max" in riders_stats
        assert "median" in riders_stats

        # Verify calculations: [10, 20, 30, 0, 15]
        assert riders_stats["min"] == 0.0
        assert riders_stats["max"] == 30.0
        assert riders_stats["mean"] == 15.0  # (10+20+30+0+15)/5

    def test_handles_infinite_values(self) -> None:
        """Test infinite values are excluded from statistics."""
        df = pd.DataFrame({"col": [1, 2, 3, np.inf, 5]})
        stats = get_descriptive_stats(df)

        # Should calculate stats from finite values only
        assert stats["col"]["mean"] == pytest.approx(2.75)  # (1+2+3+5)/4


class TestGetFeatureDistributions:
    """Tests for get_feature_distributions function."""

    def test_distributions_structure(self, sample_dataframe: pd.DataFrame) -> None:
        """Test feature distributions returns expected structure."""
        distributions = get_feature_distributions(sample_dataframe)

        for col in CATEGORICAL_COLUMNS:
            assert col in distributions

    def test_value_counts(self, sample_dataframe: pd.DataFrame) -> None:
        """Test value counts are correct."""
        distributions = get_feature_distributions(sample_dataframe)

        # Location_Category: Urban=3, Suburban=1, Rural=1
        assert distributions["Location_Category"]["Urban"] == 3
        assert distributions["Location_Category"]["Suburban"] == 1
        assert distributions["Location_Category"]["Rural"] == 1


class TestGetEdaSummary:
    """Tests for get_eda_summary function."""

    def test_eda_summary_structure(self, sample_dataframe: pd.DataFrame) -> None:
        """Test EDA summary contains all expected sections."""
        summary = get_eda_summary(sample_dataframe)

        assert "row_count" in summary
        assert "column_count" in summary
        assert "columns" in summary
        assert "numeric_stats" in summary
        assert "categorical_distributions" in summary

    def test_eda_summary_json_serializable(self, sample_dataframe: pd.DataFrame) -> None:
        """Test EDA summary can be serialized to JSON."""
        summary = get_eda_summary(sample_dataframe)

        # Should not raise
        json_str = json.dumps(summary)
        assert isinstance(json_str, str)

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["row_count"] == 5


class TestExportEdaSummary:
    """Tests for export_eda_summary function."""

    def test_export_creates_file(self, sample_dataframe: pd.DataFrame) -> None:
        """Test export creates JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_eda.json"
            result_path = export_eda_summary(sample_dataframe, output_path)

            assert result_path.exists()
            assert result_path == output_path

    def test_export_content(self, sample_dataframe: pd.DataFrame) -> None:
        """Test exported JSON content is valid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_eda.json"
            export_eda_summary(sample_dataframe, output_path)

            with open(output_path) as f:
                data = json.load(f)

            assert data["row_count"] == 5
            assert "columns" in data
            assert "numeric_stats" in data

