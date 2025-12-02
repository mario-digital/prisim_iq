"""K-Means market segmentation for PrismIQ.

This module implements market context segmentation using K-Means clustering.
It groups similar market conditions to enable segment-based pricing strategies.
"""

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from loguru import logger
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import LabelEncoder, StandardScaler

from src.schemas.market import MarketContext
from src.schemas.segment import SegmentResult

# Default model path
DEFAULT_MODEL_PATH = Path(__file__).parent.parent.parent / "data" / "models" / "segmenter.joblib"

# Features used for clustering
CLUSTERING_FEATURES = [
    "supply_demand_ratio",
    "time_of_booking_encoded",
    "location_category_encoded",
    "vehicle_type_encoded",
]

# Categorical columns that need encoding
CATEGORICAL_MAPPINGS = {
    "time_of_booking": ["Morning", "Afternoon", "Evening", "Night"],
    "location_category": ["Urban", "Suburban", "Rural"],
    "vehicle_type": ["Economy", "Premium"],
}


class Segmenter:
    """K-Means based market segmenter.

    Segments market contexts into distinct clusters for pricing strategy.
    Uses supply/demand ratio and categorical features (location, time, vehicle)
    to identify ~6 market segments.
    """

    def __init__(self, n_clusters: int = 6, random_state: int = 42) -> None:
        """Initialize the segmenter.

        Args:
            n_clusters: Number of clusters for K-Means. Default is 6.
            random_state: Random seed for reproducibility.
        """
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.kmeans: KMeans | None = None
        self.scaler: StandardScaler | None = None
        self.label_encoders: dict[str, LabelEncoder] = {}
        self.segment_labels: dict[int, str] = {}
        self.cluster_characteristics: dict[int, dict[str, float]] = {}
        self._is_fitted = False

    @property
    def is_fitted(self) -> bool:
        """Check if the segmenter has been trained."""
        return self._is_fitted

    def fit(self, data: pd.DataFrame) -> "Segmenter":
        """Train the segmenter on historical data.

        Args:
            data: DataFrame with columns: supply_demand_ratio, Time_of_Booking,
                  Location_Category, Vehicle_Type.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If required columns are missing.
        """
        logger.info(f"Fitting segmenter on {len(data)} samples with {self.n_clusters} clusters")

        # Prepare features
        X = self._prepare_features(data, fit_encoders=True)

        # Fit scaler
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Fit K-Means
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init=10,
        )
        self.kmeans.fit(X_scaled)

        # Generate segment labels based on cluster centroids
        self._generate_segment_labels(data, X_scaled)

        self._is_fitted = True
        logger.info(f"Segmenter fitted. Segment labels: {self.segment_labels}")
        return self

    def classify(self, context: MarketContext) -> SegmentResult:
        """Assign a market context to a segment.

        Args:
            context: Market context to classify.

        Returns:
            SegmentResult with segment name, cluster ID, characteristics,
            and centroid distance.

        Raises:
            RuntimeError: If segmenter has not been fitted.
        """
        if not self._is_fitted:
            raise RuntimeError("Segmenter must be fitted before classification")

        # Convert context to feature vector
        X = self._context_to_features(context)

        # Scale features
        X_scaled = self.scaler.transform(X)  # type: ignore

        # Predict cluster
        cluster_id = int(self.kmeans.predict(X_scaled)[0])  # type: ignore

        # Calculate distance to centroid
        centroid = self.kmeans.cluster_centers_[cluster_id]  # type: ignore
        distance = float(np.linalg.norm(X_scaled[0] - centroid))

        return SegmentResult(
            segment_name=self.segment_labels.get(cluster_id, f"Cluster_{cluster_id}"),
            cluster_id=cluster_id,
            characteristics=self.cluster_characteristics.get(cluster_id, {}),
            centroid_distance=round(distance, 4),
        )

    def save(self, path: Path | str | None = None) -> Path:
        """Save the trained segmenter to disk.

        Args:
            path: Output path. Defaults to data/models/segmenter.joblib.

        Returns:
            Path where model was saved.

        Raises:
            RuntimeError: If segmenter has not been fitted.
        """
        if not self._is_fitted:
            raise RuntimeError("Cannot save unfitted segmenter")

        save_path = Path(path) if path else DEFAULT_MODEL_PATH
        save_path.parent.mkdir(parents=True, exist_ok=True)

        model_data = {
            "n_clusters": self.n_clusters,
            "random_state": self.random_state,
            "kmeans": self.kmeans,
            "scaler": self.scaler,
            "label_encoders": self.label_encoders,
            "segment_labels": self.segment_labels,
            "cluster_characteristics": self.cluster_characteristics,
        }

        joblib.dump(model_data, save_path)
        logger.info(f"Segmenter saved to {save_path}")
        return save_path

    @classmethod
    def load(cls, path: Path | str | None = None) -> "Segmenter":
        """Load a trained segmenter from disk.

        Args:
            path: Model path. Defaults to data/models/segmenter.joblib.

        Returns:
            Loaded Segmenter instance.

        Raises:
            FileNotFoundError: If model file does not exist.
        """
        load_path = Path(path) if path else DEFAULT_MODEL_PATH

        if not load_path.exists():
            raise FileNotFoundError(f"Model not found: {load_path}")

        model_data = joblib.load(load_path)

        segmenter = cls(
            n_clusters=model_data["n_clusters"],
            random_state=model_data["random_state"],
        )
        segmenter.kmeans = model_data["kmeans"]
        segmenter.scaler = model_data["scaler"]
        segmenter.label_encoders = model_data["label_encoders"]
        segmenter.segment_labels = model_data["segment_labels"]
        segmenter.cluster_characteristics = model_data["cluster_characteristics"]
        segmenter._is_fitted = True

        logger.info(f"Segmenter loaded from {load_path}")
        return segmenter

    def _prepare_features(self, data: pd.DataFrame, fit_encoders: bool = False) -> np.ndarray:
        """Prepare feature matrix from raw data.

        Args:
            data: Input DataFrame.
            fit_encoders: If True, fit new label encoders.

        Returns:
            Feature matrix as numpy array.
        """
        features = []

        # Numeric feature: supply_demand_ratio
        supply_demand = data["supply_demand_ratio"].values
        # Replace inf with max finite value
        supply_demand = np.where(
            np.isinf(supply_demand),
            np.nanmax(supply_demand[np.isfinite(supply_demand)]),
            supply_demand,
        )
        features.append(supply_demand)

        # Encode categorical features
        for col, categories in CATEGORICAL_MAPPINGS.items():
            source_col = self._get_source_column(col, data)
            if fit_encoders:
                encoder = LabelEncoder()
                encoder.fit(categories)
                self.label_encoders[col] = encoder
            encoded = self.label_encoders[col].transform(data[source_col])
            features.append(encoded)

        return np.column_stack(features)

    def _get_source_column(self, feature_name: str, data: pd.DataFrame) -> str:
        """Map feature name to actual column name in DataFrame."""
        # Handle different column naming conventions
        col_mapping = {
            "time_of_booking": "Time_of_Booking",
            "location_category": "Location_Category",
            "vehicle_type": "Vehicle_Type",
        }
        mapped = col_mapping.get(feature_name, feature_name)
        if mapped in data.columns:
            return mapped
        # Fallback to original name
        if feature_name in data.columns:
            return feature_name
        raise ValueError(f"Column not found: {feature_name}")

    def _context_to_features(self, context: MarketContext) -> np.ndarray:
        """Convert MarketContext to feature vector."""
        features = [context.supply_demand_ratio]

        for col, _ in CATEGORICAL_MAPPINGS.items():
            value = getattr(context, col)
            encoded = self.label_encoders[col].transform([value])[0]
            features.append(encoded)

        return np.array([features])

    def _generate_segment_labels(self, data: pd.DataFrame, _X_scaled: np.ndarray) -> None:
        """Generate descriptive labels for each cluster based on centroids.

        Labels follow pattern: {Location}_{TimeProfile}_{VehicleType}
        """
        labels = self.kmeans.labels_  # type: ignore
        centroids = self.kmeans.cluster_centers_  # type: ignore

        for cluster_id in range(self.n_clusters):
            mask = labels == cluster_id
            cluster_data = data.iloc[mask]

            # Determine dominant characteristics
            location = cluster_data["Location_Category"].mode().iloc[0] if len(cluster_data) > 0 else "Unknown"
            time = cluster_data["Time_of_Booking"].mode().iloc[0] if len(cluster_data) > 0 else "Unknown"
            vehicle = cluster_data["Vehicle_Type"].mode().iloc[0] if len(cluster_data) > 0 else "Unknown"

            # Simplify time label
            time_profile = "Peak" if time in ["Morning", "Evening"] else "Standard"

            # Create label
            label = f"{location}_{time_profile}_{vehicle}"
            self.segment_labels[cluster_id] = label

            # Store characteristics
            avg_ratio = float(cluster_data["supply_demand_ratio"].replace([np.inf], np.nan).mean())
            self.cluster_characteristics[cluster_id] = {
                "avg_supply_demand_ratio": round(avg_ratio, 3) if not np.isnan(avg_ratio) else 0.0,
                "sample_count": int(mask.sum()),
                "centroid_norm": round(float(np.linalg.norm(centroids[cluster_id])), 3),
            }

    def get_segment_distribution(self) -> dict[str, Any]:
        """Get distribution of segments for reference.

        Returns:
            Dictionary with segment labels and their characteristics.
        """
        if not self._is_fitted:
            raise RuntimeError("Segmenter must be fitted first")

        return {
            "n_clusters": self.n_clusters,
            "segments": {
                self.segment_labels[i]: {
                    "cluster_id": i,
                    **self.cluster_characteristics[i],
                }
                for i in range(self.n_clusters)
            },
        }


def analyze_optimal_k(
    data: pd.DataFrame,
    k_range: range | None = None,
    random_state: int = 42,
) -> dict[str, Any]:
    """Analyze optimal number of clusters using elbow and silhouette methods.

    Args:
        data: DataFrame with clustering features.
        k_range: Range of k values to test. Defaults to 2-10.
        random_state: Random seed for reproducibility.

    Returns:
        Dictionary with analysis results including recommended k.

    Note:
        This function helps determine the optimal k value before fitting.
        Based on the expected segments (Location × Time × Vehicle), k=6 is expected.
    """
    if k_range is None:
        k_range = range(2, 11)

    logger.info(f"Analyzing optimal k in range {k_range}")

    # Create temporary segmenter to use feature preparation
    temp_segmenter = Segmenter(n_clusters=2, random_state=random_state)
    X = temp_segmenter._prepare_features(data, fit_encoders=True)

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Elbow method: compute inertia for each k
    inertias = []
    silhouette_scores = []

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(float(kmeans.inertia_))

        # Silhouette score (only valid for k >= 2)
        if k >= 2:
            score = silhouette_score(X_scaled, kmeans.labels_)
            silhouette_scores.append(float(score))
        else:
            silhouette_scores.append(0.0)

    # Find elbow point (simple second derivative method)
    elbow_k = _find_elbow(list(k_range), inertias)

    # Find best silhouette score
    best_silhouette_idx = int(np.argmax(silhouette_scores))
    best_silhouette_k = list(k_range)[best_silhouette_idx]

    # Recommend k (prefer silhouette, but validate with elbow)
    recommended_k = best_silhouette_k

    results = {
        "k_range": list(k_range),
        "inertias": inertias,
        "silhouette_scores": silhouette_scores,
        "elbow_k": elbow_k,
        "best_silhouette_k": best_silhouette_k,
        "best_silhouette_score": silhouette_scores[best_silhouette_idx],
        "recommended_k": recommended_k,
        "rationale": f"Based on silhouette analysis, k={recommended_k} provides the best cluster separation. "
                     f"Elbow method suggests k={elbow_k}. "
                     f"Expected ~6 segments based on Location × Time × Vehicle combinations.",
    }

    logger.info(f"Optimal k analysis complete. Recommended: k={recommended_k}")
    return results


def _find_elbow(k_values: list[int], inertias: list[float]) -> int:
    """Find elbow point using the kneedle algorithm (simplified).

    Uses the maximum distance from the line connecting first and last points.
    """
    if len(k_values) < 3:
        return k_values[0]

    # Normalize values to [0, 1]
    k_norm = np.array([(k - k_values[0]) / (k_values[-1] - k_values[0]) for k in k_values])
    inertia_norm = np.array([(i - min(inertias)) / (max(inertias) - min(inertias) + 1e-10) for i in inertias])

    # Line from first to last point
    line_vec = np.array([k_norm[-1] - k_norm[0], inertia_norm[-1] - inertia_norm[0]])
    line_len = np.linalg.norm(line_vec)

    if line_len < 1e-10:
        return k_values[0]

    line_unit = line_vec / line_len

    # Find point with maximum distance from line
    max_dist = 0
    elbow_idx = 0

    for i, (k, inertia) in enumerate(zip(k_norm, inertia_norm, strict=True)):
        point_vec = np.array([k - k_norm[0], inertia - inertia_norm[0]])
        proj_len = np.dot(point_vec, line_unit)
        proj = proj_len * line_unit
        dist = np.linalg.norm(point_vec - proj)

        if dist > max_dist:
            max_dist = dist
            elbow_idx = i

    return k_values[elbow_idx]

