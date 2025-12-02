"""Data loading and preprocessing utilities for PrismIQ.

This module handles loading the dynamic_pricing.xlsx dataset and provides
exploratory data analysis (EDA) functions.

Data Quality Notes:
- Dataset contains ride-sharing pricing data with 10 columns
- No missing values expected in source data
- supply_demand_ratio is derived: Number_of_Drivers / Number_of_Riders
- Division by zero handled by returning infinity for zero riders
"""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from loguru import logger

# Default data path relative to backend directory
DEFAULT_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "dynamic_pricing.xlsx"

# Expected columns in the dataset
EXPECTED_COLUMNS = [
    "Number_of_Riders",
    "Number_of_Drivers",
    "Location_Category",
    "Customer_Loyalty_Status",
    "Number_of_Past_Rides",
    "Average_Ratings",
    "Time_of_Booking",
    "Vehicle_Type",
    "Expected_Ride_Duration",
    "Historical_Cost_of_Ride",
]

# Categorical columns for distribution analysis
CATEGORICAL_COLUMNS = [
    "Location_Category",
    "Customer_Loyalty_Status",
    "Time_of_Booking",
    "Vehicle_Type",
]

# Numeric columns for statistical analysis
NUMERIC_COLUMNS = [
    "Number_of_Riders",
    "Number_of_Drivers",
    "Number_of_Past_Rides",
    "Average_Ratings",
    "Expected_Ride_Duration",
    "Historical_Cost_of_Ride",
]


def load_dataset(file_path: Path | str | None = None) -> pd.DataFrame:
    """Load the dynamic pricing dataset from Excel file.

    Args:
        file_path: Path to the Excel file. Defaults to backend/data/dynamic_pricing.xlsx.

    Returns:
        DataFrame containing the loaded dataset with supply_demand_ratio added.

    Raises:
        FileNotFoundError: If the Excel file does not exist.
        ValueError: If required columns are missing.
    """
    path = Path(file_path) if file_path else DEFAULT_DATA_PATH

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    logger.info(f"Loading dataset from {path}")
    df = pd.read_excel(path, engine="openpyxl")

    # Validate required columns
    missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Add derived feature: supply_demand_ratio
    # Handle division by zero: when riders = 0, ratio is infinity
    df["supply_demand_ratio"] = np.where(
        df["Number_of_Riders"] == 0,
        np.inf,
        df["Number_of_Drivers"] / df["Number_of_Riders"],
    )

    logger.info(f"Loaded {len(df)} rows with {len(df.columns)} columns")
    return df


def get_basic_stats(df: pd.DataFrame) -> dict[str, Any]:
    """Get basic statistics about the dataset.

    Args:
        df: The loaded DataFrame.

    Returns:
        Dictionary with row_count, column_count, and per-column info
        (dtype, missing_count, unique_count).
    """
    columns_info = {}
    for col in df.columns:
        columns_info[col] = {
            "dtype": str(df[col].dtype),
            "missing_count": int(df[col].isna().sum()),
            "unique_count": int(df[col].nunique()),
        }

    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": columns_info,
    }


def get_descriptive_stats(df: pd.DataFrame) -> dict[str, dict[str, float]]:
    """Get descriptive statistics for numeric columns.

    Args:
        df: The loaded DataFrame.

    Returns:
        Dictionary mapping column names to their statistics
        (mean, std, min, max, median, q25, q75).
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    stats = {}

    for col in numeric_cols:
        col_data = df[col].dropna()
        # Skip infinite values for statistics
        finite_data = col_data[np.isfinite(col_data)]

        if len(finite_data) == 0:
            stats[col] = {
                "mean": None,
                "std": None,
                "min": None,
                "max": None,
                "median": None,
                "q25": None,
                "q75": None,
            }
        else:
            stats[col] = {
                "mean": float(finite_data.mean()),
                "std": float(finite_data.std()),
                "min": float(finite_data.min()),
                "max": float(finite_data.max()),
                "median": float(finite_data.median()),
                "q25": float(finite_data.quantile(0.25)),
                "q75": float(finite_data.quantile(0.75)),
            }

    return stats


def get_feature_distributions(df: pd.DataFrame) -> dict[str, dict[str, int]]:
    """Get value counts for categorical columns.

    Args:
        df: The loaded DataFrame.

    Returns:
        Dictionary mapping categorical column names to their value counts.
    """
    distributions = {}

    for col in CATEGORICAL_COLUMNS:
        if col in df.columns:
            value_counts = df[col].value_counts()
            distributions[col] = {str(k): int(v) for k, v in value_counts.items()}

    return distributions


def get_eda_summary(df: pd.DataFrame) -> dict[str, Any]:
    """Generate complete EDA summary as JSON-serializable dictionary.

    Args:
        df: The loaded DataFrame.

    Returns:
        Complete EDA summary including basic stats, descriptive stats,
        and categorical distributions.
    """
    basic = get_basic_stats(df)

    return {
        "row_count": basic["row_count"],
        "column_count": basic["column_count"],
        "columns": basic["columns"],
        "numeric_stats": get_descriptive_stats(df),
        "categorical_distributions": get_feature_distributions(df),
    }


def export_eda_summary(df: pd.DataFrame, output_path: Path | str | None = None) -> Path:
    """Export EDA summary to JSON file.

    Args:
        df: The loaded DataFrame.
        output_path: Path for output JSON. Defaults to backend/data/eda_summary.json.

    Returns:
        Path to the created JSON file.
    """
    import json

    if output_path is None:
        output_path = DEFAULT_DATA_PATH.parent / "eda_summary.json"
    else:
        output_path = Path(output_path)

    summary = get_eda_summary(df)

    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"EDA summary exported to {output_path}")
    return output_path

