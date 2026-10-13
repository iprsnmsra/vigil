"""Feature extraction for Flaky-Test detection.

Extracts statistical and historical features from test execution traces
matching the research methodologies of iDFlakies and FlakeFlagger.
"""

from typing import List, Dict, Any
import numpy as np


def extract_features(test_results: List[Any], code_churn: int = 0) -> Dict[str, float]:
    """Extracts ML features from a sequence of TestResult objects or dicts.

    Args:
        test_results: List of test results with 'status' and 'duration'.
        code_churn: Number of lines changed in recent commits touching this test.

    Returns:
        Dictionary of numerical feature values.
    """
    if not test_results:
        return {
            "total_runs": 0.0,
            "flip_rate": 0.0,
            "failure_rate": 0.0,
            "rerun_pass_rate": 0.0,
            "duration_mean": 0.0,
            "duration_std": 0.0,
            "code_churn": float(code_churn),
        }

    statuses = [r.status if hasattr(r, "status") else r.get("status", "passed") for r in test_results]
    durations = [r.duration if hasattr(r, "duration") else r.get("duration", 0.0) for r in test_results]

    total_runs = len(statuses)

    # 1. Flip Rate: count transitions between passed and failed
    flips = 0
    prev = None
    for s in statuses:
        if prev is not None and prev != s:
            flips += 1
        prev = s
    flip_rate = (flips / (total_runs - 1)) if total_runs > 1 else 0.0

    # 2. Failure Rate: count non-passed executions
    failures = sum(1 for s in statuses if s in ("failed", "error"))
    failure_rate = failures / total_runs

    # 3. Rerun Pass Rate: when a failed test is immediately followed by a pass
    rerun_passes = 0
    failed_prior = False
    for s in statuses:
        if failed_prior and s == "passed":
            rerun_passes += 1
            failed_prior = False
        elif s in ("failed", "error"):
            failed_prior = True
        else:
            failed_prior = False
    rerun_pass_rate = (rerun_passes / failures) if failures > 0 else 0.0

    # 4. Duration statistics
    d_mean = float(np.mean(durations)) if durations else 0.0
    d_std = float(np.std(durations)) if durations and len(durations) > 1 else 0.0

    return {
        "total_runs": float(total_runs),
        "flip_rate": round(float(flip_rate), 4),
        "failure_rate": round(float(failure_rate), 4),
        "rerun_pass_rate": round(float(rerun_pass_rate), 4),
        "duration_mean": round(d_mean, 4),
        "duration_std": round(d_std, 4),
        "code_churn": float(code_churn),
    }
