"""Model Training and Evaluation Pipeline for Flaky-Test Detector.

Trains a LightGBM classifier on test execution feature traces, evaluates against
the baseline flip-rate rule, and serializes the trained model for production inference.
"""

import os
import sys
from typing import Dict, Any

# Ensure parent directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.dataset import generate_flaky_dataset


def train_and_evaluate(output_model_dir: str = "models") -> Dict[str, Any]:
    """Trains LightGBM classifier, calculates evaluation metrics, and saves the model."""
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    import joblib

    try:
        from lightgbm import LGBMClassifier
        model_cls = LGBMClassifier
        model_name = "LightGBM"
    except ImportError:
        from sklearn.ensemble import HistGradientBoostingClassifier
        model_cls = HistGradientBoostingClassifier
        model_name = "HistGradientBoosting"

    print("Generating iDFlakies empirical dataset (1,200 test cases)...")
    X_dicts, y = generate_flaky_dataset(num_samples=1200)

    feature_names = list(X_dicts[0].keys())
    X = np.array([[sample[k] for k in feature_names] for sample in X_dicts])
    y = np.array(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    print(f"Training set: {len(X_train)} samples, Test set: {len(X_test)} samples")

    # 1. Baseline Statistical Rule: Flag as flaky if flip_rate > 0.15
    flip_rate_idx = feature_names.index("flip_rate")
    y_pred_baseline = (X_test[:, flip_rate_idx] > 0.15).astype(int)

    base_acc = accuracy_score(y_test, y_pred_baseline)
    base_prec = precision_score(y_test, y_pred_baseline, zero_division=0)
    base_rec = recall_score(y_test, y_pred_baseline, zero_division=0)
    base_f1 = f1_score(y_test, y_pred_baseline, zero_division=0)

    # 2. Train ML Classifier
    if model_name == "LightGBM":
        clf = model_cls(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5,
            num_leaves=31,
            random_state=42,
            verbosity=-1,
        )
    else:
        clf = model_cls(max_iter=100, random_state=42)

    clf.fit(X_train, y_train)

    y_pred_ml = clf.predict(X_test)
    y_prob_ml = clf.predict_proba(X_test)[:, 1]

    ml_acc = accuracy_score(y_test, y_pred_ml)
    ml_prec = precision_score(y_test, y_pred_ml, zero_division=0)
    ml_rec = recall_score(y_test, y_pred_ml, zero_division=0)
    ml_f1 = f1_score(y_test, y_pred_ml, zero_division=0)
    ml_auc = roc_auc_score(y_test, y_prob_ml)

    # Save artifact
    os.makedirs(output_model_dir, exist_ok=True)
    model_artifact = {
        "model": clf,
        "feature_names": feature_names,
        "model_name": model_name,
        "metrics": {
            "accuracy": round(ml_acc, 4),
            "precision": round(ml_prec, 4),
            "recall": round(ml_rec, 4),
            "f1": round(ml_f1, 4),
            "roc_auc": round(ml_auc, 4),
        },
    }
    model_path = os.path.join(output_model_dir, "flaky_detector_model.joblib")
    joblib.dump(model_artifact, model_path)
    print(f"Model saved to: {model_path}")

    results = {
        "model_name": model_name,
        "baseline": {
            "accuracy": round(base_acc, 4),
            "precision": round(base_prec, 4),
            "recall": round(base_rec, 4),
            "f1": round(base_f1, 4),
        },
        "ml_model": {
            "accuracy": round(ml_acc, 4),
            "precision": round(ml_prec, 4),
            "recall": round(ml_rec, 4),
            "f1": round(ml_f1, 4),
            "roc_auc": round(ml_auc, 4),
        },
    }

    print("\n" + "=" * 50)
    print("FLAKY TEST DETECTOR EVALUATION BENCHMARK")
    print("=" * 50)
    print(f"{'Metric':<15} | {'Baseline (Rule)':<16} | {model_name:<16}")
    print("-" * 50)
    print(f"{'Accuracy':<15} | {base_acc:<16.4f} | {ml_acc:<16.4f}")
    print(f"{'Precision':<15} | {base_prec:<16.4f} | {ml_prec:<16.4f}")
    print(f"{'Recall':<15} | {base_rec:<16.4f} | {ml_rec:<16.4f}")
    print(f"{'F1 Score':<15} | {base_f1:<16.4f} | {ml_f1:<16.4f}")
    print("=" * 50)

    return results


if __name__ == "__main__":
    train_and_evaluate()
