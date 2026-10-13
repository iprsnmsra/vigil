import os
import logging
from typing import List, Dict, Any, Optional
from .models import TestResult

logger = logging.getLogger(__name__)


class BaselineDetector:
    def detect(self, results: List[TestResult]) -> float:
        """Calculates a simple flakiness score based on flip rate."""
        if not results:
            return 0.0

        flips = 0
        prev_status = None
        for result in results:
            status = result.status if hasattr(result, "status") else result.get("status")
            if prev_status and prev_status != status:
                flips += 1
            prev_status = status

        flip_rate = flips / len(results) if len(results) > 1 else 0.0
        return min(flip_rate * 2.0, 1.0)


class MLDetector:
    """Production ML Flakiness Detector utilizing trained LightGBM model."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), "..", "models", "flaky_detector_model.joblib"
        )
        self.model_artifact = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                import joblib
                self.model_artifact = joblib.load(self.model_path)
                logger.info(f"Loaded trained ML flakiness model from {self.model_path}")
            except Exception as e:
                logger.warning(f"Could not load ML model from {self.model_path}: {e}")

    def detect(self, features: Dict[str, float]) -> float:
        """Scores flakiness probability [0.0 - 1.0] from feature dictionary."""
        if not self.model_artifact:
            # Fallback to flip-rate heuristic
            flip = features.get("flip_rate", 0.0)
            return min(flip * 2.0, 1.0)

        try:
            import numpy as np
            clf = self.model_artifact["model"]
            feature_names = self.model_artifact["feature_names"]
            x = np.array([[features.get(f, 0.0) for f in feature_names]])
            prob = clf.predict_proba(x)[0, 1]
            return float(prob)
        except Exception as e:
            logger.error(f"Error executing ML inference: {e}")
            return float(features.get("flip_rate", 0.0))

    def detect_from_history(self, results: List[TestResult], code_churn: int = 0) -> float:
        """Extracts features from test history and runs ML inference."""
        try:
            from ml.features import extract_features
            features = extract_features(results, code_churn=code_churn)
            return self.detect(features)
        except ImportError:
            return baseline_detector.detect(results)


baseline_detector = BaselineDetector()
ml_detector = MLDetector()
