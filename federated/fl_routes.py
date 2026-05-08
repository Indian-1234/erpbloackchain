"""
Federated Learning — Flask Blueprint  (Steps 2 + 3, production-ready)

Routes:
  POST /fl/train/<hospital_id>  — doctor triggers local training
  POST /fl/aggregate            — FedAvg (auto-called when all hospitals trained)
  GET  /fl/predict              — disease-risk prediction for a patient
  GET  /fl/status               — current FL round status (JSON)
  POST /fl/reset                — reset round (demo / testing)
"""

import os, json, pickle, hashlib
import numpy as np
from datetime import datetime
from flask import Blueprint, request, jsonify

from federated.local_trainer import (
    generate_hospital_data, train_local_model,
    get_model_weights, set_model_weights, fedavg,
    hash_weights, build_update_metadata,
    FEATURE_NAMES, HOSPITAL_PROFILES,
)
from sklearn.model_selection import train_test_split

fl_bp = Blueprint("fl", __name__, url_prefix="/fl")

# ── Paths ──────────────────────────────────────────────────────────────────────
_HERE       = os.path.dirname(__file__)
BASE        = os.path.join(_HERE, "..", "data", "fl_models")
STATE_FILE  = os.path.join(BASE, "fl_state.json")
LOG_FILE    = os.path.join(BASE, "blockchain_log.json")
FL_CONTRACT = os.path.join(_HERE, "..", "data", "fl_contract.json")

HOSPITALS   = list(HOSPITAL_PROFILES.keys())


# ══════════════════════════════════════════════════════════════════════════════
# BLOCKCHAIN HELPER  (graceful fallback if Ganache / contract not available)
# ══════════════════════════════════════════════════════════════════════════════

def _get_fl_contract():
    """Return (web3, contract) or (None, None) if blockchain unavailable."""
    try:
        from web3 import Web3
        from web3.providers.rpc import HTTPProvider
        if not os.path.exists(FL_CONTRACT):
            return None, None
        with open(FL_CONTRACT) as f:
            info = json.load(f)
        w3 = Web3(HTTPProvider("http://127.0.0.1:7545"))
        if not w3.is_connected():
            return None, None
        contract = w3.eth.contract(address=info["address"], abi=info["abi"])
        w3.eth.default_account = w3.eth.accounts[0]
        return w3, contract
    except Exception:
        return None, None


def _chain_log_update(provider_hash: str, weight_hash: str, n_samples: int):
    w3, contract = _get_fl_contract()
    if contract:
        try:
            tx = contract.functions.logModelUpdate(
                provider_hash, weight_hash, n_samples
            ).transact()
            w3.eth.wait_for_transaction_receipt(tx)
            print(f"[FL Chain] logModelUpdate tx={tx.hex()[:16]}...")
            return tx.hex()
        except Exception as e:
            print(f"[FL Chain] logModelUpdate failed: {e}")
    return None


def _chain_set_global(global_hash: str):
    w3, contract = _get_fl_contract()
    if contract:
        try:
            tx = contract.functions.setGlobalModel(global_hash).transact()
            w3.eth.wait_for_transaction_receipt(tx)
            print(f"[FL Chain] setGlobalModel tx={tx.hex()[:16]}...")
            return tx.hex()
        except Exception as e:
            print(f"[FL Chain] setGlobalModel failed: {e}")
    return None


# ══════════════════════════════════════════════════════════════════════════════
# STATE + MODEL HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _ensure_base():
    os.makedirs(BASE, exist_ok=True)


def load_state() -> dict:
    _ensure_base()
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"round": 1, "trained": [], "aggregated": False, "last_aggregation": None}


def save_state(state: dict):
    _ensure_base()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def load_model(name: str):
    path = os.path.join(BASE, f"{name}.pkl")
    if not os.path.exists(path):
        return None, None
    with open(path, "rb") as f:
        obj = pickle.load(f)
    return obj["model"], obj["scaler"]


def save_model_file(name: str, model, scaler):
    _ensure_base()
    with open(os.path.join(BASE, f"{name}.pkl"), "wb") as f:
        pickle.dump({"model": model, "scaler": scaler}, f)


def _append_log(entry: dict):
    _ensure_base()
    log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            log = json.load(f)
    log.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def _do_fedavg() -> dict:
    """Run FedAvg over all trained hospital models. Returns result dict."""
    local_weights = []
    sample_counts = []
    for i, h in enumerate(HOSPITALS):
        model, scaler = load_model(h)
        if model is None:
            raise RuntimeError(f"Model file missing for {h}")
        local_weights.append(get_model_weights(model))
        X, y = generate_hospital_data(h, seed=i * 100)
        X_train, _, _, _ = train_test_split(X, y, test_size=0.25, random_state=42)
        sample_counts.append(len(X_train))

    global_weights = fedavg(local_weights, sample_counts)
    global_hash    = hash_weights(global_weights)

    base_model, base_scaler = load_model(HOSPITALS[0])
    set_model_weights(base_model, global_weights)
    save_model_file("global_model", base_model, base_scaler)

    now = datetime.utcnow().isoformat() + "Z"
    chain_tx = _chain_set_global(global_hash)

    state = load_state()
    state["aggregated"]       = True
    state["last_aggregation"] = now
    save_state(state)

    return {
        "status":         "aggregated",
        "round":          state["round"],
        "hospitals":      HOSPITALS,
        "sample_counts":  dict(zip(HOSPITALS, sample_counts)),
        "global_hash":    global_hash[:32] + "...",
        "chain_tx":       chain_tx,
        "timestamp":      now,
    }


# ══════════════════════════════════════════════════════════════════════════════
# ROUTE 1 — POST /fl/train/<hospital_id>
# ══════════════════════════════════════════════════════════════════════════════

@fl_bp.route("/train/<hospital_id>", methods=["POST"])
def train(hospital_id: str):
    if hospital_id not in HOSPITALS:
        return jsonify({"error": f"Unknown hospital. Valid: {HOSPITALS}"}), 400

    state = load_state()
    if hospital_id in state["trained"]:
        return jsonify({
            "status":  "already_trained",
            "message": f"{hospital_id} already trained in round {state['round']}",
            "state":   state,
        })

    seed = HOSPITALS.index(hospital_id) * 100
    X, y = generate_hospital_data(hospital_id, seed=seed)
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.25, random_state=42)

    model, scaler = train_local_model(X_train, y_train)
    save_model_file(hospital_id, model, scaler)

    weights = get_model_weights(model)
    meta    = build_update_metadata(hospital_id, weights, len(X_train))

    # Log to blockchain (graceful fallback to JSON)
    provider_hash = hashlib.sha256(hospital_id.encode()).hexdigest()
    chain_tx      = _chain_log_update(provider_hash, meta["weight_hash"], len(X_train))
    meta["chain_tx"] = chain_tx
    _append_log(meta)

    state["trained"].append(hospital_id)
    save_state(state)

    remaining  = [h for h in HOSPITALS if h not in state["trained"]]
    all_done   = len(remaining) == 0

    result = {
        "status":             "trained",
        "hospital":           hospital_id,
        "samples":            len(X_train),
        "weight_hash":        meta["weight_hash"][:20] + "...",
        "chain_tx":           chain_tx,
        "round":              state["round"],
        "trained_so_far":     state["trained"],
        "remaining":          remaining,
        "ready_to_aggregate": all_done,
    }

    # Auto-aggregate when all hospitals have trained
    if all_done and not state.get("aggregated"):
        try:
            agg = _do_fedavg()
            result["auto_aggregated"] = True
            result["global_hash"]     = agg["global_hash"]
            result["agg_chain_tx"]    = agg["chain_tx"]
            result["message"]         = "All hospitals trained — FedAvg complete. Global model ready."
        except Exception as e:
            result["auto_aggregated"] = False
            result["message"]         = f"Training done but auto-aggregation failed: {e}"
    else:
        result["message"] = (
            "All hospitals done — call POST /fl/aggregate"
            if all_done else f"Waiting for: {', '.join(remaining)}"
        )

    return jsonify(result)


# ══════════════════════════════════════════════════════════════════════════════
# ROUTE 2 — POST /fl/aggregate
# ══════════════════════════════════════════════════════════════════════════════

@fl_bp.route("/aggregate", methods=["POST"])
def aggregate():
    state = load_state()
    if state.get("aggregated"):
        return jsonify({"status": "already_aggregated", "round": state["round"]})

    missing = [h for h in HOSPITALS if h not in state["trained"]]
    if missing:
        return jsonify({"status": "not_ready", "missing": missing}), 400

    try:
        result = _do_fedavg()
        result["message"] = "Global model updated via FedAvg. Use GET /fl/predict."
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# ROUTE 3 — GET/POST /fl/predict
# ══════════════════════════════════════════════════════════════════════════════

@fl_bp.route("/predict", methods=["GET", "POST"])
def predict():
    global_model, global_scaler = load_model("global_model")
    if global_model is None:
        return jsonify({"error": "Global model not ready. Wait for all hospitals to train."}), 404

    defaults = {
        "age": 45, "systolic_bp": 120, "diastolic_bp": 80,
        "heart_rate": 72, "glucose_level": 95, "bmi": 24,
        "cholesterol": 185, "oxygen_saturation": 98,
    }
    params = (
        request.get_json(silent=True) or {}
        if request.method == "POST"
        else request.args
    )
    values = {k: float(params.get(k, defaults[k])) for k in FEATURE_NAMES}

    X        = np.array([[values[k] for k in FEATURE_NAMES]])
    X_scaled = global_scaler.transform(X)
    pred     = int(global_model.predict(X_scaled)[0])
    prob     = float(global_model.predict_proba(X_scaled)[0][1])

    return jsonify({
        "prediction":     pred,
        "risk_label":     "HIGH RISK" if pred == 1 else "LOW RISK",
        "probability":    round(prob * 100, 1),
        "risk_color":     "#FF4D6D" if pred == 1 else "#00E5A0",
        "input_features": values,
        "model_version":  f"round_{load_state()['round']}",
    })


# ══════════════════════════════════════════════════════════════════════════════
# ROUTE 4 — GET /fl/status
# ══════════════════════════════════════════════════════════════════════════════

@fl_bp.route("/status", methods=["GET"])
def status():
    state   = load_state()
    log     = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            log = json.load(f)

    trained   = state.get("trained", [])
    remaining = [h for h in HOSPITALS if h not in trained]

    return jsonify({
        "round":               state["round"],
        "hospitals_total":     len(HOSPITALS),
        "hospitals_trained":   trained,
        "hospitals_remaining": remaining,
        "progress_pct":        round(len(trained) / len(HOSPITALS) * 100),
        "aggregated":          state.get("aggregated", False),
        "last_aggregation":    state.get("last_aggregation"),
        "global_model_ready":  os.path.exists(os.path.join(BASE, "global_model.pkl")),
        "blockchain_log":      log[-5:],
        "chain_available":     _get_fl_contract()[1] is not None,
    })


# ══════════════════════════════════════════════════════════════════════════════
# ROUTE 5 — POST /fl/reset
# ══════════════════════════════════════════════════════════════════════════════

@fl_bp.route("/reset", methods=["POST"])
def reset():
    cur_round = load_state().get("round", 1)
    save_state({"round": cur_round + 1, "trained": [], "aggregated": False, "last_aggregation": None})
    return jsonify({"status": "reset", "new_round": cur_round + 1})
