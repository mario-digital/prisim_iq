"""Model manager for serving trained demand prediction models.

This module provides the ModelManager class for loading and serving
ML models at runtime for demand prediction.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

import joblib
import numpy as np
import pandas as pd
from loguru import logger
from sklearn.preprocessing import LabelEncoder

from src.ml.training_data import CATEGORICAL_COLUMNS, FEATURE_COLUMNS
from src.schemas.market import MarketContext

# Default models directory
MODELS_DIR = Path(__file__).parent.parent.parent / "data" / "models"

# Available model types
ModelName = Literal["linear_regression", "decision_tree", "xgboost"]


class ModelManager:
    """Manager for loading and serving trained demand prediction models.

    Loads models from disk and provides prediction interface for
    MarketContext objects at various price points.
    """

    def __init__(self, models_dir: Path | str | None = None) -> None:
        """Initialize the model manager.

        Args:
            models_dir: Directory containing trained models.
                       Defaults to backend/data/models/.
        """
        self.models_dir = Path(models_dir) if models_dir else MODELS_DIR
        self.models: dict[str, Any] = {}
        self.encoders: dict[str, LabelEncoder] = {}
        self.feature_names: list[str] = []
        self._loaded = False

    def load_models(self) -> None:
        """Load all trained models from disk."""
        if self._loaded:
            logger.debug("Models already loaded, skipping reload")
            return

        logger.info(f"Loading models from {self.models_dir}")

        # Load feature info
        feature_info_path = self.models_dir / "feature_info.json"
        if feature_info_path.exists():
            with open(feature_info_path) as f:
                feature_info = json.load(f)
                self.feature_names = feature_info["feature_names"]
        else:
            logger.warning("Feature info not found, using default feature columns")
            self.feature_names = FEATURE_COLUMNS

        # Load encoders
        encoders_path = self.models_dir / "encoders.joblib"
        if encoders_path.exists():
            self.encoders = joblib.load(encoders_path)
            logger.info(f"Loaded {len(self.encoders)} encoders")
        else:
            logger.warning("Encoders not found, categorical encoding may fail")

        # Load models
        model_names: list[ModelName] = ["linear_regression", "decision_tree", "xgboost"]
        for name in model_names:
            model_path = self.models_dir / f"{name}.joblib"
            if model_path.exists():
                self.models[name] = joblib.load(model_path)
                logger.info(f"Loaded model: {name}")
            else:
                logger.warning(f"Model not found: {model_path}")

        if not self.models:
            raise RuntimeError(f"No models found in {self.models_dir}")

        self._loaded = True
        logger.info(f"Loaded {len(self.models)} models: {list(self.models.keys())}")

    def _ensure_loaded(self) -> None:
        """Ensure models are loaded before prediction."""
        if not self._loaded:
            self.load_models()

    def _context_to_features(
        self, context: MarketContext, price: float, segment: str | None = None
    ) -> pd.DataFrame:
        """Convert MarketContext and price to feature DataFrame.

        Args:
            context: Market context for prediction.
            price: Price point to evaluate.
            segment: Optional customer segment. If None, uses 'Unknown'.

        Returns:
            DataFrame with encoded features ready for prediction.
        """
        # Build raw feature dict from context
        features = {
            "number_of_riders": context.number_of_riders,
            "number_of_drivers": context.number_of_drivers,
            "location_category": context.location_category,
            "customer_loyalty_status": context.customer_loyalty_status,
            "number_of_past_rides": context.number_of_past_rides,
            "average_ratings": context.average_ratings,
            "time_of_booking": context.time_of_booking,
            "vehicle_type": context.vehicle_type,
            "expected_ride_duration": context.expected_ride_duration,
            "historical_cost_of_ride": context.historical_cost_of_ride,
            "supply_demand_ratio": context.supply_demand_ratio,
            "segment": segment or "Unknown",
            "price": price,
        }

        df = pd.DataFrame([features])

        # Encode categorical columns
        for col in CATEGORICAL_COLUMNS:
            if col in df.columns and col in self.encoders:
                encoder = self.encoders[col]
                value = str(df[col].iloc[0])
                if value in encoder.classes_:
                    df[col] = encoder.transform([value])[0]
                else:
                    # Handle unseen category with -1
                    logger.warning(f"Unseen category '{value}' for column '{col}'")
                    df[col] = -1

        # Ensure column order matches training
        df = df[FEATURE_COLUMNS]

        return df

    def predict(
        self,
        context: MarketContext,
        price: float,
        model_name: ModelName = "xgboost",
        segment: str | None = None,
    ) -> float:
        """Predict demand for context at given price.

        Args:
            context: Market context for prediction.
            price: Price point to evaluate.
            model_name: Name of model to use. Defaults to 'xgboost'.
            segment: Optional customer segment.

        Returns:
            Predicted demand as a float in [0, 1].

        Raises:
            ValueError: If model_name is not available.
        """
        self._ensure_loaded()

        if model_name not in self.models:
            available = list(self.models.keys())
            raise ValueError(
                f"Model '{model_name}' not available. Available: {available}"
            )

        features = self._context_to_features(context, price, segment)
        model = self.models[model_name]

        prediction = model.predict(features)[0]

        # Clip to valid demand range [0, 1]
        prediction = float(np.clip(prediction, 0.0, 1.0))

        return prediction

    def get_all_predictions(
        self,
        context: MarketContext,
        price: float,
        segment: str | None = None,
    ) -> dict[str, float]:
        """Get predictions from all available models.

        Useful for model comparison and ensemble approaches.

        Args:
            context: Market context for prediction.
            price: Price point to evaluate.
            segment: Optional customer segment.

        Returns:
            Dictionary mapping model names to predicted demands.
        """
        self._ensure_loaded()

        predictions = {}
        for model_name in self.models:
            predictions[model_name] = self.predict(
                context, price, model_name=model_name, segment=segment  # type: ignore[arg-type]
            )

        return predictions

    def predict_demand_curve(
        self,
        context: MarketContext,
        prices: list[float],
        model_name: ModelName = "xgboost",
        segment: str | None = None,
    ) -> list[dict[str, float]]:
        """Predict demand at multiple price points.

        Useful for generating demand curves for optimization.

        Args:
            context: Market context for predictions.
            prices: List of price points to evaluate.
            model_name: Name of model to use.
            segment: Optional customer segment.

        Returns:
            List of dicts with 'price' and 'demand' keys.
        """
        self._ensure_loaded()

        results = []
        for price in prices:
            demand = self.predict(context, price, model_name=model_name, segment=segment)
            results.append({"price": price, "demand": demand})

        return results

    def get_available_models(self) -> list[str]:
        """Get list of available model names.

        Returns:
            List of loaded model names.
        """
        self._ensure_loaded()
        return list(self.models.keys())

    def get_model_info(self, model_name: ModelName) -> dict[str, Any]:
        """Get information about a specific model.

        Args:
            model_name: Name of the model.

        Returns:
            Dictionary with model information.
        """
        self._ensure_loaded()

        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not available")

        model = self.models[model_name]

        info: dict[str, Any] = {
            "name": model_name,
            "type": type(model).__name__,
            "feature_count": len(self.feature_names),
            "feature_names": self.feature_names,
        }

        # Add model-specific info
        if hasattr(model, "feature_importances_"):
            importance = dict(
                zip(self.feature_names, model.feature_importances_, strict=False)
            )
            # Sort by importance
            info["feature_importance"] = dict(
                sorted(importance.items(), key=lambda x: x[1], reverse=True)
            )
        elif hasattr(model, "coef_"):
            coef = dict(zip(self.feature_names, model.coef_, strict=False))
            info["coefficients"] = coef
            if hasattr(model, "intercept_"):
                info["intercept"] = model.intercept_

        return info


# Singleton instance for app-wide use
_model_manager: ModelManager | None = None


def get_model_manager(models_dir: Path | str | None = None) -> ModelManager:
    """Get or create singleton ModelManager instance.

    Args:
        models_dir: Optional models directory override.

    Returns:
        ModelManager instance.
    """
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager(models_dir=models_dir)
    return _model_manager

