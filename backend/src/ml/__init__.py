"""Machine Learning module for PrismIQ pricing engine."""

from src.ml.demand_simulator import DemandSimulator, simulate_demand
from src.ml.model_manager import ModelManager, get_model_manager
from src.ml.preprocessor import (
    get_basic_stats,
    get_descriptive_stats,
    get_eda_summary,
    get_feature_distributions,
    load_dataset,
)
from src.ml.segmenter import Segmenter, analyze_optimal_k
from src.ml.training import ModelTrainer, train_models

__all__ = [
    "load_dataset",
    "get_basic_stats",
    "get_descriptive_stats",
    "get_feature_distributions",
    "get_eda_summary",
    "Segmenter",
    "analyze_optimal_k",
    "DemandSimulator",
    "simulate_demand",
    "ModelTrainer",
    "train_models",
    "ModelManager",
    "get_model_manager",
]

