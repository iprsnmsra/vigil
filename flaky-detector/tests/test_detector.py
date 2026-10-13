from app.detector import BaselineDetector
from app.models import TestResult

def test_baseline_detector():
    results = [
        TestResult(test_id="t1", name="t1", classname="c", status="passed", duration=0.1),
        TestResult(test_id="t1", name="t1", classname="c", status="failed", duration=0.1),
        TestResult(test_id="t1", name="t1", classname="c", status="passed", duration=0.1),
    ]
    
    detector = BaselineDetector()
    score = detector.detect(results)
    assert score > 0.0 # 2 flips in 3 runs
