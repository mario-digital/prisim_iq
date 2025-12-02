#!/usr/bin/env python
"""Generate synthetic training data for ML price optimization.

This script generates labeled training data by:
1. Loading the original dynamic_pricing.xlsx dataset
2. For each row, generating demand at multiple price points
3. Calculating profit for each price-demand pair
4. Splitting into train/test sets (80/20) stratified by segment
5. Saving to parquet files

Usage:
    cd backend
    source .venv/bin/activate
    python scripts/generate_training_data.py --seed 42
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
from loguru import logger

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sklearn.model_selection import train_test_split

from src.ml.demand_simulator import DemandSimulator
from src.ml.preprocessor import load_dataset
from src.ml.segmenter import Segmenter
from src.schemas.market import MarketContext

# Type alias for loyalty status literals
LoyaltyStatus = Literal["Bronze", "Silver", "Gold", "Platinum"]

# Default paths
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = DATA_DIR / "processed"

# Price multipliers relative to historical cost (Option 2 from story)
PRICE_MULTIPLIERS = [0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0, 2.5]


def get_price_points(historical_cost: float) -> list[float]:
    """Generate price points relative to historical cost.

    Args:
        historical_cost: Baseline/reference price for the ride.

    Returns:
        List of 10 price points from 50% to 250% of historical cost.
    """
    return [historical_cost * m for m in PRICE_MULTIPLIERS]


# Mapping for loyalty status values in dataset to MarketContext Literal values
LOYALTY_STATUS_MAP: dict[str, LoyaltyStatus] = {
    "Regular": "Bronze",  # Map "Regular" to base tier
    "Bronze": "Bronze",
    "Silver": "Silver",
    "Gold": "Gold",
    "Platinum": "Platinum",
}


def row_to_market_context(row: pd.Series) -> MarketContext:
    """Convert a DataFrame row to MarketContext.

    Args:
        row: Single row from the dataset.

    Returns:
        MarketContext instance.
    """
    # Map loyalty status from dataset values to MarketContext allowed values
    raw_loyalty = str(row["Customer_Loyalty_Status"])
    loyalty_status: LoyaltyStatus = LOYALTY_STATUS_MAP.get(raw_loyalty, "Bronze")

    return MarketContext(
        number_of_riders=int(row["Number_of_Riders"]),
        number_of_drivers=int(row["Number_of_Drivers"]),
        location_category=row["Location_Category"],
        customer_loyalty_status=loyalty_status,
        number_of_past_rides=int(row["Number_of_Past_Rides"]),
        average_ratings=float(row["Average_Ratings"]),
        time_of_booking=row["Time_of_Booking"],
        vehicle_type=row["Vehicle_Type"],
        expected_ride_duration=int(row["Expected_Ride_Duration"]),
        historical_cost_of_ride=float(row["Historical_Cost_of_Ride"]),
    )


def generate_training_data(
    df: pd.DataFrame,
    simulator: DemandSimulator,
    segmenter: Segmenter,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate synthetic training data with demand labels.

    For each row in the original dataset, generates multiple price-demand pairs
    using the demand simulator. Adds segment labels and profit calculations.

    Args:
        df: Original dataset loaded via load_dataset().
        simulator: DemandSimulator instance for generating demand.
        segmenter: Trained Segmenter for assigning segment labels.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with expanded rows (original_rows × price_points).
    """
    np.random.seed(seed)
    logger.info(f"Generating training data with seed={seed}")
    logger.info(f"Original dataset: {len(df)} rows")
    logger.info(f"Price points per row: {len(PRICE_MULTIPLIERS)}")

    records = []
    total_rows = len(df)

    for row_num, (_, row) in enumerate(df.iterrows(), start=1):
        # Convert row to MarketContext
        context = row_to_market_context(row)

        # Get segment assignment
        segment_result = segmenter.classify(context)
        segment_name = segment_result.segment_name

        # Get historical cost for price point calculation
        historical_cost = float(row["Historical_Cost_of_Ride"])
        price_points = get_price_points(historical_cost)

        # Generate demand at each price point
        for price in price_points:
            demand = simulator.simulate_demand(context, price)

            # Calculate profit: (price - cost) * demand
            # Note: demand is probability [0,1], profit can be negative
            profit = (price - historical_cost) * demand

            records.append(
                {
                    # Original context features
                    "number_of_riders": context.number_of_riders,
                    "number_of_drivers": context.number_of_drivers,
                    "location_category": context.location_category,
                    "customer_loyalty_status": context.customer_loyalty_status,
                    "number_of_past_rides": context.number_of_past_rides,
                    "average_ratings": context.average_ratings,
                    "time_of_booking": context.time_of_booking,
                    "vehicle_type": context.vehicle_type,
                    "expected_ride_duration": context.expected_ride_duration,
                    "historical_cost_of_ride": historical_cost,
                    "supply_demand_ratio": context.supply_demand_ratio,
                    "segment": segment_name,
                    # Generated columns
                    "price": price,
                    "demand": demand,
                    "profit": profit,
                }
            )

        # Log progress every 100 rows
        if row_num % 100 == 0:
            logger.info(f"Processed {row_num}/{total_rows} rows")

    training_df = pd.DataFrame(records)
    logger.info(f"Generated {len(training_df)} training samples")

    return training_df


def split_and_save(
    df: pd.DataFrame,
    output_dir: Path,
    test_size: float = 0.2,
    seed: int = 42,
) -> tuple[Path, Path]:
    """Split data into train/test sets and save to parquet.

    Uses stratified split by segment to ensure balanced representation.

    Args:
        df: Training data DataFrame.
        output_dir: Directory to save parquet files.
        test_size: Fraction of data for test set (default 0.2).
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (train_path, test_path).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Stratified split by segment
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=seed,
        stratify=df["segment"],
    )

    logger.info(f"Train set: {len(train_df)} samples")
    logger.info(f"Test set: {len(test_df)} samples")

    # Log segment distribution
    logger.info("Train segment distribution:")
    for segment, count in train_df["segment"].value_counts().items():
        logger.info(f"  {segment}: {count}")

    # Save to parquet
    train_path = output_dir / "training_data.parquet"
    test_path = output_dir / "test_data.parquet"

    train_df.to_parquet(train_path, index=False)
    test_df.to_parquet(test_path, index=False)

    logger.info(f"Training data saved to {train_path}")
    logger.info(f"Test data saved to {test_path}")

    return train_path, test_path


def main(seed: int = 42) -> None:
    """Main entry point for training data generation.

    Args:
        seed: Random seed for reproducibility.
    """
    logger.info("=" * 60)
    logger.info("Starting synthetic training data generation")
    logger.info("=" * 60)

    # Load original dataset
    logger.info("Loading original dataset...")
    df = load_dataset()

    # Initialize demand simulator
    logger.info("Initializing demand simulator...")
    simulator = DemandSimulator()

    # Load trained segmenter
    logger.info("Loading trained segmenter...")
    segmenter = Segmenter.load()

    # Generate training data
    training_df = generate_training_data(df, simulator, segmenter, seed=seed)

    # Log statistics
    logger.info("Dataset statistics:")
    logger.info(f"  Total samples: {len(training_df)}")
    logger.info(f"  Columns: {list(training_df.columns)}")
    logger.info(f"  Price range: ${training_df['price'].min():.2f} - ${training_df['price'].max():.2f}")
    logger.info(f"  Demand range: {training_df['demand'].min():.4f} - {training_df['demand'].max():.4f}")
    logger.info(f"  Profit range: ${training_df['profit'].min():.2f} - ${training_df['profit'].max():.2f}")
    logger.info(f"  Unique segments: {training_df['segment'].nunique()}")

    # Split and save
    train_path, test_path = split_and_save(training_df, OUTPUT_DIR, seed=seed)

    logger.info("=" * 60)
    logger.info("Training data generation complete!")
    logger.info(f"  Training file: {train_path}")
    logger.info(f"  Test file: {test_path}")
    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic training data")
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    args = parser.parse_args()

    main(seed=args.seed)

