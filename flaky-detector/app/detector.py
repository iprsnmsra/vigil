from typing import List
from .models import TestResult, FlakynessScore

class BaselineDetector:
    def detect(self, results: List[TestResult]) -> float:
        """Calculates a simple flakiness score based on flip rate."""
        if not results:
            return 0.0
            
        flips = 0
        prev_status = None
        for result in results:
            if prev_status and prev_status != result.status:
                flips += 1
            prev_status = result.status
            
        flip_rate = flips / len(results) if len(results) > 1 else 0.0
        return min(flip_rate * 2.0, 1.0) # Scale up to 1.0

class MLDetector:
    """Placeholder for LightGBM model."""
    def detect(self, features: dict) -> float:
        # Phase 5: Implement LightGBM inference
        return 0.0

baseline_detector = BaselineDetector()
