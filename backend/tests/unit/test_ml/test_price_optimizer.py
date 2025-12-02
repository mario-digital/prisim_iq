"""Tests for ML price optimizer."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import joblib
import numpy as np
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from src.config import Settings
from src.ml.model_manager import ModelManager
from src.ml.price_optimizer import PriceOptimizer, get_price_optimizer
from src.ml.training_data import CATEGORICAL_COLUMNS, FEATURE_COLUMNS
from src.schemas.market import MarketContext
from src.schemas.optimization import OptimizationResult, PriceDemandPoint


@pytest.fixture
def sample_market_context() -> MarketContext:
    """Create sample market context for tests."""
    return MarketContext(
        number_of_riders=50,
        number_of_drivers=25,
        location_category="Urban",
        customer_loyalty_status="Gold",
        number_of_past_rides=20,
        average_ratings=4.5,
        time_of_booking="Evening",
        vehicle_type="Premium",
        expected_ride_duration=30,
        historical_cost_of_ride=35.0,
    )


@pytest.fixture
def trained_models_dir(tmp_path: Path) -> Path:
    """Create directory with mock trained models."""
    # Create mock encoders
    encoders = {}
    for col in CATEGORICAL_COLUMNS:
        encoder = LabelEncoder()
        if col == "location_category":
            encoder.fit(["Urban", "Suburban", "Rural"])
        elif col == "customer_loyalty_status":
            encoder.fit(["Bronze", "Silver", "Gold", "Platinum"])
        elif col == "time_of_booking":
            encoder.fit(["Morning", "Afternoon", "Evening", "Night"])
        elif col == "vehicle_type":
            encoder.fit(["Economy", "Premium"])
        elif col == "segment":
            encoder.fit(["Segment_A", "Segment_B", "Segment_C", "Unknown"])
        encoders[col] = encoder

    # Save encoders
    joblib.dump(encoders, tmp_path / "encoders.joblib")

    # Create and save mock models
    np.random.seed(42)
    n_features = len(FEATURE_COLUMNS)

    # Linear regression
    lr = LinearRegression()
    X_dummy = np.random.rand(100, n_features)
    y_dummy = np.random.rand(100)
    lr.fit(X_dummy, y_dummy)
    joblib.dump(lr, tmp_path / "linear_regression.joblib")

    # Decision tree
    dt = DecisionTreeRegressor(max_depth=3, random_state=42)
    dt.fit(X_dummy, y_dummy)
    joblib.dump(dt, tmp_path / "decision_tree.joblib")

    # XGBoost
    xgb = XGBRegressor(max_depth=3, n_estimators=10, random_state=42, verbosity=0)
    xgb.fit(X_dummy, y_dummy)
    joblib.dump(xgb, tmp_path / "xgboost.joblib")

    # Save feature info
    feature_info = {
        "feature_names": FEATURE_COLUMNS,
        "categorical_columns": CATEGORICAL_COLUMNS,
        "target_column": "demand",
    }
    with open(tmp_path / "feature_info.json", "w") as f:
        json.dump(feature_info, f)

    return tmp_path


@pytest.fixture
def model_manager(trained_models_dir: Path) -> ModelManager:
    """Create a loaded ModelManager."""
    manager = ModelManager(models_dir=trained_models_dir)
    manager.load_models()
    return manager


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with smaller price range for faster tests."""
    settings = Settings(
        price_min=10.0,
        price_max=100.0,
        price_step=1.0,
        optimization_cache_size=100,
    )
    return settings


class TestPriceOptimizer:
    """Tests for PriceOptimizer class."""

    def test_optimizer_initialization(self, model_manager: ModelManager) -> None:
        """Test PriceOptimizer can be initialized."""
        optimizer = PriceOptimizer(model_manager=model_manager)

        assert optimizer._model_manager is model_manager
        assert optimizer._settings is not None
        assert optimizer._cache == {}

    def test_optimizer_with_custom_settings(
        self, model_manager: ModelManager, test_settings: Settings
    ) -> None:
        """Test PriceOptimizer with custom settings."""
        optimizer = PriceOptimizer(
            model_manager=model_manager,
            settings=test_settings,
        )

        assert optimizer._settings.price_min == 10.0
        assert optimizer._settings.price_max == 100.0
        assert optimizer._settings.price_step == 1.0

    def test_compute_profit_positive(self, model_manager: ModelManager) -> None:
        """Test profit computation returns positive value."""
        optimizer = PriceOptimizer(model_manager=model_manager)

        profit = optimizer._compute_profit(price=50.0, cost=30.0, demand=0.8)

        expected = (50.0 - 30.0) * 0.8  # = 16.0
        assert profit == expected

    def test_compute_profit_zero_demand(self, model_manager: ModelManager) -> None:
        """Test profit computation with zero demand."""
        optimizer = PriceOptimizer(model_manager=model_manager)

        profit = optimizer._compute_profit(price=50.0, cost=30.0, demand=0.0)

        assert profit == 0.0

    def test_compute_profit_below_cost(self, model_manager: ModelManager) -> None:
        """Test profit computation returns zero when price below cost."""
        optimizer = PriceOptimizer(model_manager=model_manager)

        profit = optimizer._compute_profit(price=25.0, cost=30.0, demand=0.8)

        assert profit == 0.0  # Should not be negative

    def test_optimize_returns_result(
        self,
        model_manager: ModelManager,
        test_settings: Settings,
        sample_market_context: MarketContext,
    ) -> None:
        """Test optimize returns OptimizationResult."""
        optimizer = PriceOptimizer(
            model_manager=model_manager,
            settings=test_settings,
        )

        result = optimizer.optimize(sample_market_context, use_cache=False)

        assert isinstance(result, OptimizationResult)
        assert result.optimal_price >= test_settings.price_min
        assert result.optimal_price <= test_settings.price_max
        assert result.expected_demand >= 0.0
        assert result.expected_demand <= 1.0
        assert result.expected_profit >= 0.0
        assert result.baseline_price == sample_market_context.historical_cost_of_ride
        assert isinstance(result.profit_uplift_percent, float)
        assert isinstance(result.price_demand_curve, list)
        assert result.optimization_time_ms >= 0.0

    def test_optimize_price_demand_curve(
        self,
        model_manager: ModelManager,
        test_settings: Settings,
        sample_market_context: MarketContext,
    ) -> None:
        """Test price-demand curve in result."""
        optimizer = PriceOptimizer(
            model_manager=model_manager,
            settings=test_settings,
        )

        result = optimizer.optimize(sample_market_context, use_cache=False)

        assert len(result.price_demand_curve) > 0
        for point in result.price_demand_curve:
            assert isinstance(point, PriceDemandPoint)
            assert point.price >= 0
            assert 0 <= point.demand <= 1
            assert isinstance(point.profit, float)

    def test_optimize_execution_time(
        self,
        sample_market_context: MarketContext,
    ) -> None:
        """Test optimization completes within 500ms (AC: 6).

        Uses a mock model manager to isolate algorithm performance from
        model inference time, ensuring consistent results across different
        CI environments.
        """
        # Use mock model for consistent, fast predictions across environments
        mock_manager = MagicMock(spec=ModelManager)
        mock_manager.predict.return_value = 0.5  # Fast constant response

        optimizer = PriceOptimizer(model_manager=mock_manager)

        result = optimizer.optimize(sample_market_context, use_cache=False)

        assert result.optimization_time_ms < 500, (
            f"Optimization took {result.optimization_time_ms}ms, exceeds 500ms limit"
        )

    def test_optimize_profit_uplift_calculation(
        self,
        model_manager: ModelManager,
        test_settings: Settings,
        sample_market_context: MarketContext,
    ) -> None:
        """Test profit uplift is calculated correctly."""
        optimizer = PriceOptimizer(
            model_manager=model_manager,
            settings=test_settings,
        )

        result = optimizer.optimize(sample_market_context, use_cache=False)

        # Verify uplift calculation if baseline_profit > 0
        if result.baseline_profit > 0:
            expected_uplift = (
                (result.expected_profit - result.baseline_profit) / result.baseline_profit
            ) * 100
            assert abs(result.profit_uplift_percent - expected_uplift) < 0.01

    def test_optimize_respects_cost_floor(
        self,
        model_manager: ModelManager,
        sample_market_context: MarketContext,
    ) -> None:
        """Test that optimal price is never below cost."""
        optimizer = PriceOptimizer(model_manager=model_manager)

        result = optimizer.optimize(sample_market_context, use_cache=False)

        # Optimal price should be at least the historical cost
        assert result.optimal_price >= sample_market_context.historical_cost_of_ride

    def test_optimize_with_segment(
        self,
        model_manager: ModelManager,
        test_settings: Settings,
        sample_market_context: MarketContext,
    ) -> None:
        """Test optimization with segment parameter."""
        optimizer = PriceOptimizer(
            model_manager=model_manager,
            settings=test_settings,
        )

        result = optimizer.optimize(
            sample_market_context,
            segment="Segment_A",
            use_cache=False,
        )

        assert isinstance(result, OptimizationResult)


class TestPriceOptimizerCaching:
    """Tests for PriceOptimizer caching behavior."""

    def test_cache_hit(
        self,
        model_manager: ModelManager,
        test_settings: Settings,
        sample_market_context: MarketContext,
    ) -> None:
        """Test that identical contexts return cached results."""
        optimizer = PriceOptimizer(
            model_manager=model_manager,
            settings=test_settings,
        )

        # First call - should populate cache
        result1 = optimizer.optimize(sample_market_context, use_cache=True)

        # Second call - should hit cache
        result2 = optimizer.optimize(sample_market_context, use_cache=True)

        # Results should be identical
        assert result1.optimal_price == result2.optimal_price
        assert result1.expected_profit == result2.expected_profit

        # Cache should have one entry
        assert len(optimizer._cache) == 1

    def test_cache_miss_different_context(
        self,
        model_manager: ModelManager,
        test_settings: Settings,
    ) -> None:
        """Test that different contexts don't share cache."""
        optimizer = PriceOptimizer(
            model_manager=model_manager,
            settings=test_settings,
        )

        context1 = MarketContext(
            number_of_riders=50,
            number_of_drivers=25,
            location_category="Urban",
            customer_loyalty_status="Gold",
            number_of_past_rides=20,
            average_ratings=4.5,
            time_of_booking="Evening",
            vehicle_type="Premium",
            expected_ride_duration=30,
            historical_cost_of_ride=35.0,
        )

        context2 = MarketContext(
            number_of_riders=100,  # Different
            number_of_drivers=25,
            location_category="Urban",
            customer_loyalty_status="Gold",
            number_of_past_rides=20,
            average_ratings=4.5,
            time_of_booking="Evening",
            vehicle_type="Premium",
            expected_ride_duration=30,
            historical_cost_of_ride=35.0,
        )

        optimizer.optimize(context1, use_cache=True)
        optimizer.optimize(context2, use_cache=True)

        # Cache should have two entries
        assert len(optimizer._cache) == 2

    def test_cache_disabled(
        self,
        model_manager: ModelManager,
        test_settings: Settings,
        sample_market_context: MarketContext,
    ) -> None:
        """Test that cache can be disabled."""
        optimizer = PriceOptimizer(
            model_manager=model_manager,
            settings=test_settings,
        )

        optimizer.optimize(sample_market_context, use_cache=False)
        optimizer.optimize(sample_market_context, use_cache=False)

        # Cache should be empty when disabled
        assert len(optimizer._cache) == 0

    def test_cache_eviction(
        self,
        model_manager: ModelManager,
    ) -> None:
        """Test LRU cache eviction."""
        settings = Settings(
            price_min=10.0,
            price_max=50.0,
            price_step=5.0,
            optimization_cache_size=2,  # Very small cache
        )
        optimizer = PriceOptimizer(
            model_manager=model_manager,
            settings=settings,
        )

        # Create 3 different contexts
        contexts = []
        for riders in [50, 60, 70]:
            contexts.append(
                MarketContext(
                    number_of_riders=riders,
                    number_of_drivers=25,
                    location_category="Urban",
                    customer_loyalty_status="Gold",
                    number_of_past_rides=20,
                    average_ratings=4.5,
                    time_of_booking="Evening",
                    vehicle_type="Premium",
                    expected_ride_duration=30,
                    historical_cost_of_ride=35.0,
                )
            )

        # Fill and overflow cache
        for ctx in contexts:
            optimizer.optimize(ctx, use_cache=True)

        # Cache should be at max size (oldest evicted)
        assert len(optimizer._cache) == 2

    def test_clear_cache(
        self,
        model_manager: ModelManager,
        test_settings: Settings,
        sample_market_context: MarketContext,
    ) -> None:
        """Test cache clearing."""
        optimizer = PriceOptimizer(
            model_manager=model_manager,
            settings=test_settings,
        )

        optimizer.optimize(sample_market_context, use_cache=True)
        assert len(optimizer._cache) == 1

        optimizer.clear_cache()
        assert len(optimizer._cache) == 0

    def test_get_cache_stats(
        self,
        model_manager: ModelManager,
        test_settings: Settings,
        sample_market_context: MarketContext,
    ) -> None:
        """Test cache statistics."""
        optimizer = PriceOptimizer(
            model_manager=model_manager,
            settings=test_settings,
        )

        optimizer.optimize(sample_market_context, use_cache=True)
        stats = optimizer.get_cache_stats()

        assert stats["size"] == 1
        assert stats["max_size"] == test_settings.optimization_cache_size


class TestPriceOptimizerKnownOptimal:
    """Tests verifying optimizer finds known optimal prices."""

    def test_finds_optimal_with_mock_model(self) -> None:
        """Test optimizer finds known optimal with controlled demand function.

        AC: 7 - Verify optimizer finds known optimal on synthetic data.
        """
        # Create a mock model manager with predictable demand curve
        # demand(price) = max(0, 1 - 0.02 * price)
        # For cost=30, profit = (p - 30) * (1 - 0.02p) = p - 0.02p^2 - 30 + 0.6p = -0.02p^2 + 1.6p - 30
        # d/dp = -0.04p + 1.6 = 0 => p = 40 is optimal
        mock_manager = MagicMock(spec=ModelManager)

        def mock_predict(*, context, price, segment=None):  # noqa: ARG001
            # Linear demand: 1 at price=0, 0 at price=50
            return max(0.0, min(1.0, 1 - 0.02 * price))

        mock_manager.predict.side_effect = mock_predict

        settings = Settings(
            price_min=30.0,  # Start at cost
            price_max=60.0,
            price_step=0.5,
            optimization_cache_size=100,
        )

        optimizer = PriceOptimizer(
            model_manager=mock_manager,
            settings=settings,
        )

        context = MarketContext(
            number_of_riders=50,
            number_of_drivers=25,
            location_category="Urban",
            customer_loyalty_status="Gold",
            number_of_past_rides=20,
            average_ratings=4.5,
            time_of_booking="Evening",
            vehicle_type="Premium",
            expected_ride_duration=30,
            historical_cost_of_ride=30.0,  # cost = 30
        )

        result = optimizer.optimize(context, use_cache=False)

        # Optimal should be around $40 (within grid step tolerance)
        assert 39.0 <= result.optimal_price <= 41.0, (
            f"Expected optimal ~40, got {result.optimal_price}"
        )

        # Verify demand at optimal (expected: 1 - 0.02 * 40 = 0.2)
        assert abs(result.expected_demand - 0.2) < 0.05

        # Verify profit at optimal: (40 - 30) * 0.2 = 2.0
        assert abs(result.expected_profit - 2.0) < 0.5


class TestGetPriceOptimizer:
    """Tests for get_price_optimizer singleton function."""

    def test_creates_optimizer(self, model_manager: ModelManager) -> None:
        """Test that get_price_optimizer creates an optimizer."""
        # Reset singleton
        import src.ml.price_optimizer as po

        po._price_optimizer = None

        optimizer = get_price_optimizer(model_manager=model_manager)

        assert isinstance(optimizer, PriceOptimizer)

        # Cleanup
        po._price_optimizer = None

    def test_singleton_behavior(self, model_manager: ModelManager) -> None:
        """Test that get_price_optimizer returns singleton."""
        # Reset singleton
        import src.ml.price_optimizer as po

        po._price_optimizer = None

        optimizer1 = get_price_optimizer(model_manager=model_manager)
        optimizer2 = get_price_optimizer()

        assert optimizer1 is optimizer2

        # Cleanup
        po._price_optimizer = None

