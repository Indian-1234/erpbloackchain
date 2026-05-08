"""
Federated Learning - Local Trainer (Step 1 Proof of Concept)

Simulates 3 hospital nodes, each training a local disease-risk model
on their private EHR data. Then runs FedAvg to produce a global model.
No blockchain changes needed — fully standalone.

Run:  python federated/local_trainer.py
"""

import numpy as np
import json
import hashlib
import pickle
import os
from datetime import datetime

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "fl_models")


def _ensure_model_dir():
    os.makedirs(MODEL_DIR, exist_ok=True)


def save_model(name: str, model, scaler):
    _ensure_model_dir()
    path = os.path.join(MODEL_DIR, f"{name}.pkl")
    with open(path, "wb") as f:
        pickle.dump({"model": model, "scaler": scaler}, f)
    print(f"  Saved → {path}")
    return path


def save_metadata(log: list):
    _ensure_model_dir()
    path = os.path.join(MODEL_DIR, "blockchain_log.json")
    with open(path, "w") as f:
        json.dump(log, f, indent=2)
    print(f"  Saved → {path}")
    return path

# ── sklearn imports ───────────────────────────────────────────────────────────
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. SYNTHETIC EHR DATA GENERATOR  (mimics MIMIC-III feature structure)
# ═══════════════════════════════════════════════════════════════════════════════

FEATURE_NAMES = [
    "age", "systolic_bp", "diastolic_bp",
    "heart_rate", "glucose_level", "bmi",
    "cholesterol", "oxygen_saturation"
]

HOSPITAL_PROFILES = {
    "Hospital_A": {"bias": 0.55, "noise": 0.08, "n_patients": 120},  # older patients
    "Hospital_B": {"bias": 0.42, "noise": 0.12, "n_patients": 95},   # younger, mixed
    "Hospital_C": {"bias": 0.61, "noise": 0.06, "n_patients": 110},  # high-risk ward
}


def generate_hospital_data(hospital_name: str, seed: int):
    """
    Generate synthetic patient records for one hospital.
    Returns (X, y) where y=1 means high disease risk.
    """
    profile = HOSPITAL_PROFILES[hospital_name]
    rng = np.random.default_rng(seed)
    n = profile["n_patients"]
    bias = profile["bias"]

    age              = rng.normal(55,  15,  n).clip(18, 95)
    systolic_bp      = rng.normal(130, 20,  n).clip(80, 200)
    diastolic_bp     = rng.normal(82,  12,  n).clip(50, 130)
    heart_rate       = rng.normal(78,  14,  n).clip(45, 150)
    glucose          = rng.normal(108, 28,  n).clip(60, 300)
    bmi              = rng.normal(27,   5,  n).clip(15, 50)
    cholesterol      = rng.normal(200, 40,  n).clip(100, 350)
    oxygen_sat       = rng.normal(97,   2,  n).clip(85, 100)

    X = np.column_stack([
        age, systolic_bp, diastolic_bp,
        heart_rate, glucose, bmi,
        cholesterol, oxygen_sat
    ])

    # Risk label: high BP, high glucose, high age → higher risk
    risk_score = (
        0.35 * (age / 95) +
        0.25 * (systolic_bp / 200) +
        0.20 * (glucose / 300) +
        0.10 * (bmi / 50) +
        0.10 * (cholesterol / 350)
    ) + rng.normal(0, profile["noise"], n)

    y = (risk_score > bias).astype(int)
    return X, y


# ═══════════════════════════════════════════════════════════════════════════════
# 2. LOCAL MODEL TRAINING  (each hospital trains on its own data)
# ═══════════════════════════════════════════════════════════════════════════════

def train_local_model(X_train, y_train):
    """Train a LogisticRegression on one hospital's local data."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    model = LogisticRegression(max_iter=500, random_state=42)
    model.fit(X_scaled, y_train)
    return model, scaler


def get_model_weights(model):
    """Extract weights (coef + intercept) as a flat numpy array."""
    return np.concatenate([model.coef_.flatten(), model.intercept_])


def set_model_weights(model, weights):
    """Restore model weights from a flat array."""
    n_features = len(FEATURE_NAMES)
    model.coef_ = weights[:n_features].reshape(1, -1)
    model.intercept_ = weights[n_features:]
    return model


# ═══════════════════════════════════════════════════════════════════════════════
# 3. FEDERATED AVERAGING  (FedAvg — McMahan et al. 2017)
# ═══════════════════════════════════════════════════════════════════════════════

def fedavg(local_weights: list[np.ndarray], sample_counts: list[int]) -> np.ndarray:
    """
    Weighted average of model weights, proportional to dataset size.
    This is the core FedAvg algorithm from the paper.
    """
    total = sum(sample_counts)
    aggregated = np.zeros_like(local_weights[0])
    for weights, count in zip(local_weights, sample_counts):
        aggregated += weights * (count / total)
    return aggregated


# ═══════════════════════════════════════════════════════════════════════════════
# 4. BLOCKCHAIN METADATA LOGGER  (simulates on-chain logging — Step 2 preview)
# ═══════════════════════════════════════════════════════════════════════════════

def hash_weights(weights: np.ndarray) -> str:
    """SHA-256 hash of model weights — this is what goes on-chain, not the weights."""
    return hashlib.sha256(weights.tobytes()).hexdigest()


def build_update_metadata(hospital: str, weights: np.ndarray, n_samples: int) -> dict:
    """Simulates the blockchain log entry a smart contract would record."""
    return {
        "provider":    hospital,
        "weight_hash": hash_weights(weights),
        "n_samples":   n_samples,
        "timestamp":   datetime.utcnow().isoformat() + "Z",
        "round":       1,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 5. EVALUATION
# ═══════════════════════════════════════════════════════════════════════════════

def evaluate_model(model, scaler, X_test, y_test, label: str):
    X_scaled = scaler.transform(X_test)
    y_pred = model.predict(X_scaled)
    print(f"\n{'─'*55}")
    print(f"  {label}")
    print(f"{'─'*55}")
    print(f"  Accuracy  : {accuracy_score(y_test, y_pred):.4f}")
    print(f"  Precision : {precision_score(y_test, y_pred, zero_division=0):.4f}")
    print(f"  Recall    : {recall_score(y_test, y_pred, zero_division=0):.4f}")
    print(f"  F1 Score  : {f1_score(y_test, y_pred, zero_division=0):.4f}")
    return accuracy_score(y_test, y_pred)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. MAIN FEDERATED LEARNING LOOP
# ═══════════════════════════════════════════════════════════════════════════════

def run_federated_learning():
    print("\n" + "═"*55)
    print("  FEDERATED LEARNING — PROOF OF CONCEPT")
    print("  EHR Blockchain System  |  Step 1: Local Trainer")
    print("═"*55)

    # ── Generate data for each hospital ──────────────────────────────────────
    hospitals = list(HOSPITAL_PROFILES.keys())
    hospital_datasets = {}
    for i, h in enumerate(hospitals):
        X, y = generate_hospital_data(h, seed=i * 100)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42
        )
        hospital_datasets[h] = {
            "X_train": X_train, "X_test": X_test,
            "y_train": y_train, "y_test": y_test,
        }
        pos = int(y.sum())
        print(f"\n  {h}: {len(X)} patients  |  "
              f"High-risk: {pos} ({100*pos/len(X):.0f}%)")

    # ── Round 0: Each hospital trains its local model ─────────────────────────
    print("\n\n  ROUND 1 — LOCAL TRAINING (data never leaves hospital)")
    print("  " + "─"*50)

    local_models   = {}
    local_scalers  = {}
    local_weights  = []
    sample_counts  = []
    blockchain_log = []

    for h in hospitals:
        d = hospital_datasets[h]
        model, scaler = train_local_model(d["X_train"], d["y_train"])
        local_models[h]  = model
        local_scalers[h] = scaler
        w = get_model_weights(model)
        local_weights.append(w)
        sample_counts.append(len(d["X_train"]))

        # Simulate what goes on-chain (hash only, not weights)
        meta = build_update_metadata(h, w, len(d["X_train"]))
        blockchain_log.append(meta)
        print(f"  {h}: trained on {len(d['X_train'])} records  |  "
              f"weight_hash: {meta['weight_hash'][:16]}...")

    # ── Evaluate each local model independently ────────────────────────────────
    print("\n\n  LOCAL MODEL PERFORMANCE (before federation)")
    all_X_test = np.vstack([hospital_datasets[h]["X_test"] for h in hospitals])
    all_y_test = np.concatenate([hospital_datasets[h]["y_test"] for h in hospitals])

    local_accs = []
    for h in hospitals:
        acc = evaluate_model(
            local_models[h], local_scalers[h],
            all_X_test, all_y_test,
            f"Local model — {h}"
        )
        local_accs.append(acc)

    # ── FedAvg aggregation ────────────────────────────────────────────────────
    print("\n\n  FEDAVG AGGREGATION (blockchain-orchestrated)")
    print("  " + "─"*50)
    global_weights = fedavg(local_weights, sample_counts)
    print(f"  Aggregated {len(hospitals)} model updates")
    print(f"  Global weight hash: {hash_weights(global_weights)[:32]}...")

    # Build global model (clone first hospital's model, set averaged weights)
    global_model  = LogisticRegression(max_iter=500, random_state=42)
    global_scaler = local_scalers[hospitals[0]]

    # Need to fit briefly so sklearn initialises internal state, then override
    d0 = hospital_datasets[hospitals[0]]
    X0_scaled = global_scaler.transform(d0["X_train"])
    global_model.fit(X0_scaled, d0["y_train"])  # minimal fit to init structure
    global_model = set_model_weights(global_model, global_weights)

    # ── Evaluate global model ─────────────────────────────────────────────────
    global_acc = evaluate_model(
        global_model, global_scaler,
        all_X_test, all_y_test,
        "GLOBAL MODEL (after FedAvg)"
    )

    # ── Summary report ────────────────────────────────────────────────────────
    avg_local = np.mean(local_accs)
    print("\n\n" + "═"*55)
    print("  SUMMARY")
    print("═"*55)
    print(f"  Avg local accuracy  : {avg_local:.4f}")
    print(f"  Global accuracy     : {global_acc:.4f}")
    improvement = (global_acc - avg_local) * 100
    symbol = "↑" if improvement >= 0 else "↓"
    print(f"  Change after FedAvg : {symbol}{abs(improvement):.2f}%")

    print("\n  Simulated blockchain log (what would be stored on-chain):")
    for entry in blockchain_log:
        print(f"    {entry['provider']:12s} | samples={entry['n_samples']:4d} "
              f"| hash={entry['weight_hash'][:20]}... | {entry['timestamp']}")

    # ── Persist models to disk ────────────────────────────────────────────────
    print("\n\n  SAVING MODELS TO DISK")
    print("  " + "─"*50)
    for h in hospitals:
        save_model(h, local_models[h], local_scalers[h])
    save_model("global_model", global_model, global_scaler)
    save_metadata(blockchain_log)

    print("\n  ✓  AI LAYER PROOF COMPLETE")
    print("  ✓  Raw patient data never left each hospital node")
    print("  ✓  Only weight hashes logged on blockchain (not model weights)")
    print("  ✓  FedAvg produced a global model across 3 hospitals")
    print("═"*55 + "\n")

    return {
        "global_model":    global_model,
        "global_scaler":   global_scaler,
        "local_models":    local_models,
        "blockchain_log":  blockchain_log,
        "global_accuracy": global_acc,
        "avg_local_accuracy": avg_local,
    }


if __name__ == "__main__":
    run_federated_learning()
