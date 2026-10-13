"""Dataset generator based on empirical iDFlakies and FlakeFlagger distributions.

Produces realistic test execution trajectories across both deterministic
(stable pass, regression fail) and flaky (async wait, order-dependent, network) categories.
"""

import random
from typing import List, Tuple, Dict, Any
from .features import extract_features


def generate_flaky_dataset(num_samples: int = 1200, seed: int = 42) -> Tuple[List[Dict[str, float]], List[int]]:
    """Generates synthetic dataset aligned with iDFlakies failure characteristics.

    Returns:
        (X, y) where X is a list of feature dictionaries and y is binary label (1=flaky, 0=stable).
    """
    random.seed(seed)
    X = []
    y = []

    for i in range(num_samples):
        # 40% Flaky, 60% Deterministic (mirrors real CI test distributions)
        is_flaky = 1 if (i % 5 in (0, 1)) else 0
        num_runs = random.randint(8, 30)
        history = []

        if is_flaky:
            flake_type = random.choice(["async_wait", "order_dependent", "network_flake"])
            churn = random.randint(0, 5)  # Flaky tests fail with minimal/no code churn

            if flake_type == "async_wait":
                # High duration variance, intermittent timeouts
                for _ in range(num_runs):
                    duration = random.gauss(0.8, 0.4)
                    status = "failed" if (duration > 1.2 or random.random() < 0.25) else "passed"
                    history.append({"status": status, "duration": max(0.05, duration)})

            elif flake_type == "order_dependent":
                # Bursts of failures followed by passes
                for r_idx in range(num_runs):
                    duration = random.uniform(0.1, 0.3)
                    status = "failed" if (r_idx % 4 == 0) else "passed"
                    history.append({"status": status, "duration": duration})

            else:  # network_flake
                # Low duration variance, sporadic failures with high rerun-pass rate
                for _ in range(num_runs):
                    duration = random.uniform(0.15, 0.25)
                    status = "failed" if (random.random() < 0.20) else "passed"
                    history.append({"status": status, "duration": duration})

        else:
            # Deterministic test: either rock-solid pass or persistent failure
            is_broken = random.random() < 0.10
            churn = random.randint(10, 80) if is_broken else random.randint(0, 3)

            for _ in range(num_runs):
                duration = random.gauss(0.2, 0.03)
                status = "failed" if is_broken else "passed"
                history.append({"status": status, "duration": max(0.01, duration)})

        feats = extract_features(history, code_churn=churn)
        X.append(feats)
        y.append(is_flaky)

    return X, y
