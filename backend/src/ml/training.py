"""ML model training pipeline for demand prediction.

This module provides the ModelTrainer class for training and evaluating
multiple ML models: Linear Regression, Decision Tree, and XGBoost.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from loguru import logger
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from src.ml.training_data import (
    CATEGORICAL_COLUMNS,
    TARGET_COLUMN,
    get_features_and_target,
    load_test_data,
    load_training_data,
)

# Default models directory
MODELS_DIR = Path(__file__).parent.parent.parent / "data" / "models"


@dataclass
class ModelMetrics:
    """Container for model evaluation metrics."""

    r2: float
    mae: float
    rmse: float

    def to_dict(self) -> dict[str, float]:
        """Convert metrics to dictionary."""
        return {
            "r2": self.r2,
            "mae": self.mae,
            "rmse": self.rmse,
        }


@dataclass
class TrainingResult:
    """Result of training a single model."""

    model_name: str
    model: Any
    metrics: ModelMetrics
    best_params: dict[str, Any] | None = None
    feature_importance: dict[str, float] | None = None
    coefficients: dict[str, float] | None = None


class ModelTrainer:
    """Trainer for demand prediction models.

    Trains and evaluates three model types:
    - Linear Regression (interpretable baseline)
    - Decision Tree (tuned with GridSearchCV)
    - XGBoost (production model with hyperparameter tuning)
    """

    def __init__(self, models_dir: Path | str | None = None) -> None:
        """Initialize the trainer.

        Args:
            models_dir: Directory to save trained models.
                       Defaults to backend/data/models/.
        """
        self.models_dir = Path(models_dir) if models_dir else MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Label encoders for categorical columns
        self.encoders: dict[str, LabelEncoder] = {}

        # Feature names after encoding
        self.feature_names: list[str] = []

        # Training results
        self.results: dict[str, TrainingResult] = {}

        # Data placeholders
        self._X_train: pd.DataFrame | None = None
        self._y_train: pd.Series | None = None
        self._X_test: pd.DataFrame | None = None
        self._y_test: pd.Series | None = None

    def load_data(self) -> None:
        """Load and preprocess training and test data."""
        logger.info("Loading training and test data...")

        train_df = load_training_data()
        test_df = load_test_data()

        X_train_raw, self._y_train = get_features_and_target(train_df)
        X_test_raw, self._y_test = get_features_and_target(test_df)

        logger.info(f"Training samples: {len(X_train_raw)}")
        logger.info(f"Test samples: {len(X_test_raw)}")

        # Encode categorical columns
        self._X_train = self._encode_features(X_train_raw, fit=True)
        self._X_test = self._encode_features(X_test_raw, fit=False)

        self.feature_names = list(self._X_train.columns)
        logger.info(f"Features after encoding: {len(self.feature_names)}")

    def _encode_features(self, df: pd.DataFrame, fit: bool = False) -> pd.DataFrame:
        """Encode categorical features using LabelEncoder.

        Args:
            df: DataFrame with features.
            fit: Whether to fit encoders (True for training, False for test).

        Returns:
            DataFrame with encoded features.
        """
        df_encoded = df.copy()

        for col in CATEGORICAL_COLUMNS:
            if col in df_encoded.columns:
                if fit:
                    encoder = LabelEncoder()
                    df_encoded[col] = encoder.fit_transform(df_encoded[col].astype(str))
                    self.encoders[col] = encoder
                else:
                    encoder = self.encoders[col]
                    # Handle unseen categories gracefully
                    df_encoded[col] = df_encoded[col].astype(str).map(
                        lambda x, enc=encoder: (
                            enc.transform([x])[0]
                            if x in enc.classes_
                            else -1
                        )
                    )

        return df_encoded

    def train_linear_regression(self) -> TrainingResult:
        """Train Linear Regression as interpretable baseline.

        Returns:
            TrainingResult with trained model and metrics.
        """
        if self._X_train is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")

        logger.info("Training Linear Regression...")

        model = LinearRegression()
        model.fit(self._X_train, self._y_train)

        # Evaluate
        y_pred = model.predict(self._X_test)
        metrics = self._calculate_metrics(self._y_test, y_pred)

        # Extract coefficients for interpretability
        coefficients = dict(zip(self.feature_names, model.coef_, strict=False))
        coefficients["intercept"] = model.intercept_

        result = TrainingResult(
            model_name="linear_regression",
            model=model,
            metrics=metrics,
            coefficients=coefficients,
        )

        self.results["linear_regression"] = result

        logger.info(
            f"Linear Regression - R²: {metrics.r2:.4f}, "
            f"MAE: {metrics.mae:.4f}, RMSE: {metrics.rmse:.4f}"
        )

        return result

    def train_decision_tree(self) -> TrainingResult:
        """Train Decision Tree with GridSearchCV for max_depth.

        Returns:
            TrainingResult with best model and metrics.
        """
        if self._X_train is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")

        logger.info("Training Decision Tree with GridSearchCV...")

        param_grid = {"max_depth": [3, 4, 5, 6, 7, 8, 9, 10]}

        grid_search = GridSearchCV(
            DecisionTreeRegressor(random_state=42),
            param_grid,
            cv=5,
            scoring="neg_mean_squared_error",
            n_jobs=-1,
        )

        grid_search.fit(self._X_train, self._y_train)

        best_model = grid_search.best_estimator_
        best_params = grid_search.best_params_

        logger.info(f"Best Decision Tree params: {best_params}")

        # Evaluate
        y_pred = best_model.predict(self._X_test)
        metrics = self._calculate_metrics(self._y_test, y_pred)

        # Feature importance
        feature_importance = dict(
            zip(self.feature_names, best_model.feature_importances_, strict=False)
        )

        result = TrainingResult(
            model_name="decision_tree",
            model=best_model,
            metrics=metrics,
            best_params=best_params,
            feature_importance=feature_importance,
        )

        self.results["decision_tree"] = result

        logger.info(
            f"Decision Tree - R²: {metrics.r2:.4f}, "
            f"MAE: {metrics.mae:.4f}, RMSE: {metrics.rmse:.4f}"
        )

        return result

    def train_xgboost(self) -> TrainingResult:
        """Train XGBoost with GridSearchCV for hyperparameters.

        Returns:
            TrainingResult with best model and metrics.
        """
        if self._X_train is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")

        logger.info("Training XGBoost with GridSearchCV...")

        param_grid = {
            "max_depth": [3, 5, 7],
            "n_estimators": [50, 100, 200],
            "learning_rate": [0.01, 0.1, 0.2],
        }

        grid_search = GridSearchCV(
            XGBRegressor(random_state=42, verbosity=0),
            param_grid,
            cv=5,
            scoring="neg_mean_squared_error",
            n_jobs=-1,
        )

        grid_search.fit(self._X_train, self._y_train)

        best_model = grid_search.best_estimator_
        best_params = grid_search.best_params_

        logger.info(f"Best XGBoost params: {best_params}")

        # Evaluate
        y_pred = best_model.predict(self._X_test)
        metrics = self._calculate_metrics(self._y_test, y_pred)

        # Feature importance
        feature_importance = dict(
            zip(self.feature_names, best_model.feature_importances_, strict=False)
        )

        result = TrainingResult(
            model_name="xgboost",
            model=best_model,
            metrics=metrics,
            best_params=best_params,
            feature_importance=feature_importance,
        )

        self.results["xgboost"] = result

        logger.info(
            f"XGBoost - R²: {metrics.r2:.4f}, "
            f"MAE: {metrics.mae:.4f}, RMSE: {metrics.rmse:.4f}"
        )

        return result

    def train_all(self) -> dict[str, TrainingResult]:
        """Train all models and return results.

        Returns:
            Dictionary mapping model names to their TrainingResults.
        """
        self.load_data()
        self.train_linear_regression()
        self.train_decision_tree()
        self.train_xgboost()
        return self.results

    def _calculate_metrics(
        self, y_true: pd.Series | np.ndarray, y_pred: np.ndarray
    ) -> ModelMetrics:
        """Calculate evaluation metrics.

        Args:
            y_true: True target values.
            y_pred: Predicted values.

        Returns:
            ModelMetrics with R², MAE, and RMSE.
        """
        return ModelMetrics(
            r2=float(r2_score(y_true, y_pred)),
            mae=float(mean_absolute_error(y_true, y_pred)),
            rmse=float(np.sqrt(mean_squared_error(y_true, y_pred))),
        )

    def get_comparison_table(self) -> pd.DataFrame:
        """Generate comparison table of all trained models.

        Returns:
            DataFrame with model comparison metrics.
        """
        if not self.results:
            raise RuntimeError("No models trained. Call train_all() first.")

        data = []
        for name, result in self.results.items():
            row = {
                "model": name,
                "r2": result.metrics.r2,
                "mae": result.metrics.mae,
                "rmse": result.metrics.rmse,
            }
            if result.best_params:
                row["best_params"] = str(result.best_params)
            data.append(row)

        df = pd.DataFrame(data)
        df = df.sort_values("r2", ascending=False)

        return df

    def log_comparison(self) -> None:
        """Log comparison table to console."""
        table = self.get_comparison_table()
        logger.info("Model Comparison:")
        logger.info(f"\n{table.to_string(index=False)}")

        # Find best model
        best_model = table.iloc[0]["model"]
        best_r2 = table.iloc[0]["r2"]
        logger.info(f"Best model: {best_model} with R² = {best_r2:.4f}")

    def save_models(self) -> None:
        """Serialize all trained models to joblib files."""
        if not self.results:
            raise RuntimeError("No models trained. Call train_all() first.")

        for name, result in self.results.items():
            model_path = self.models_dir / f"{name}.joblib"
            joblib.dump(result.model, model_path)
            logger.info(f"Saved {name} to {model_path}")

        # Save encoders for inference
        encoders_path = self.models_dir / "encoders.joblib"
        joblib.dump(self.encoders, encoders_path)
        logger.info(f"Saved encoders to {encoders_path}")

        # Save feature names
        feature_info = {
            "feature_names": self.feature_names,
            "categorical_columns": CATEGORICAL_COLUMNS,
            "target_column": TARGET_COLUMN,
        }
        feature_info_path = self.models_dir / "feature_info.json"
        with open(feature_info_path, "w") as f:
            json.dump(feature_info, f, indent=2)
        logger.info(f"Saved feature info to {feature_info_path}")

    def save_metrics(self) -> None:
        """Save metrics to JSON file."""
        if not self.results:
            raise RuntimeError("No models trained. Call train_all() first.")

        def convert_to_native(obj: Any) -> Any:
            """Convert numpy types to native Python types for JSON serialization."""
            if isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, np.floating | np.integer):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        metrics_data = {}
        for name, result in self.results.items():
            metrics_data[name] = {
                "metrics": result.metrics.to_dict(),
                "best_params": convert_to_native(result.best_params),
                "feature_importance": convert_to_native(result.feature_importance),
                "coefficients": convert_to_native(result.coefficients),
            }

        metrics_path = self.models_dir / "metrics.json"
        with open(metrics_path, "w") as f:
            json.dump(metrics_data, f, indent=2)
        logger.info(f"Saved metrics to {metrics_path}")


def train_models(models_dir: Path | str | None = None) -> ModelTrainer:
    """Convenience function to train all models.

    Args:
        models_dir: Directory to save models.

    Returns:
        Trained ModelTrainer instance.
    """
    trainer = ModelTrainer(models_dir=models_dir)
    trainer.train_all()
    trainer.log_comparison()
    trainer.save_models()
    trainer.save_metrics()
    return trainer


if __name__ == "__main__":
    train_models()

