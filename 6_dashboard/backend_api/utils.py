from datetime import datetime
import numpy as np
import sqlite3
import json
from pathlib import Path

# Simple in-memory store for real-time samples keyed by district name (kept for fallback)
real_time_store = {}

# DB path
DB_PATH = Path(__file__).parent / "data.db"


def _get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create samples table if it doesn't exist."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            payload TEXT NOT NULL,
            ts TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


# ensure DB exists on import
try:
    init_db()
except Exception:
    # if DB creation fails, fall back to in-memory store
    pass

def ingest_data(payload: dict):
    """Store incoming real-time payload for a district.

    Expected minimal payload: {"name": "DistrictName", "temp": float, "humidity": float, "rainfall": float, ...}
    """
    name = payload.get("name")
    if not name:
        raise ValueError("missing 'name' in payload")

    entry = payload.copy()
    entry["_ts"] = datetime.utcnow().isoformat()

    # store in sqlite
    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO samples (name, payload, ts) VALUES (?, ?, ?)",
            (name, json.dumps(entry), entry["_ts"]),
        )
        conn.commit()
        conn.close()
    except Exception:
        # fallback to in-memory
        real_time_store[name] = entry

    # also keep last-in-memory for quick access
    real_time_store[name] = entry
    return entry


def build_zone_from_sample(district: dict, sample: dict, dengue_model, malaria_model):
    # Prepare fallback/defaults
    temp = float(sample.get("temp", sample.get("temp_c", 25.0)))
    rainfall = float(sample.get("rainfall", 0.0))
    humidity = float(sample.get("humidity", 50.0))
    pop_density = float(sample.get("pop_density", district.get("population", 1000000) / 1000))
    risk_index = float(sample.get("risk_index", 2.5))

    dengue_lag_1 = float(sample.get("dengue_lag_1", 0))
    dengue_lag_2 = float(sample.get("dengue_lag_2", 0))
    dengue_lag_3 = float(sample.get("dengue_lag_3", 0))

    malaria_lag_1 = float(sample.get("malaria_lag_1", 0))
    malaria_lag_2 = float(sample.get("malaria_lag_2", 0))
    malaria_lag_3 = float(sample.get("malaria_lag_3", 0))

    # prepare dictionary for features
    data_dict = {
        "temp_c": temp,
        "rainfall": rainfall,
        "humidity": humidity,
        "risk_index": risk_index,
        "dengue_lag_1": dengue_lag_1,
        "dengue_lag_2": dengue_lag_2,
        "dengue_lag_3": dengue_lag_3,
        "malaria_lag_1": malaria_lag_1,
        "malaria_lag_2": malaria_lag_2,
        "malaria_lag_3": malaria_lag_3,
        "pop_density": pop_density,
        # allow extended fields (may or may not exist)
        "lai": float(sample.get("lai", 0)),
        "population": float(sample.get("population", district.get("population", 0))),
        "urban_percent": float(sample.get("urban_percent", 0)),
        "dengue_trend": float(sample.get("dengue_trend", 0)),
        "malaria_trend": float(sample.get("malaria_trend", 0)),
    }

    def make_vec(model, data):
        names = list(model.feature_names_in_) if hasattr(model, "feature_names_in_") else []
        vec = []
        for n in names:
            try:
                vec.append(float(data.get(n, 0)))
            except Exception:
                vec.append(0.0)
        return np.array([vec])

    try:
        dengue_risk = int(dengue_model.predict(make_vec(dengue_model, data_dict))[0])
    except Exception:
        dengue_risk = 0

    try:
        malaria_risk = int(malaria_model.predict(make_vec(malaria_model, data_dict))[0])
    except Exception:
        malaria_risk = 0

    max_risk = max(dengue_risk, malaria_risk)
    if max_risk == 2:
        risk_level = "high"
    elif max_risk == 1:
        risk_level = "moderate"
    else:
        risk_level = "low"

    zone = {
        "name": district.get("name"),
        "lat": district.get("lat"),
        "lng": district.get("lng"),
        "dengue_risk": dengue_risk,
        "malaria_risk": malaria_risk,
        "temperature": round(temp, 1),
        "rainfall": round(rainfall, 1),
        "humidity": round(humidity, 1),
        "risk_level": risk_level,
        "last_updated": sample.get("_ts") or datetime.utcnow().isoformat(),
    }

    return zone


def get_zones_from_realtime(districts, dengue_model, malaria_model):
    """Generate zones using real-time store when available, otherwise random-like defaults."""
    high = []
    moderate = []
    silent = []

    for district in districts:
        name = district.get("name")
        # try DB latest sample first
        sample = None
        try:
            conn = _get_conn()
            cur = conn.cursor()
            cur.execute("SELECT payload FROM samples WHERE name = ? ORDER BY id DESC LIMIT 1", (name,))
            row = cur.fetchone()
            conn.close()
            if row:
                sample = json.loads(row["payload"])
        except Exception:
            sample = None

        if sample is None:
            sample = real_time_store.get(name)
        if sample is None:
            # create a small default sample to feed the model
            sample = {
                "temp": 25 + (hash(name) % 10),
                "rainfall": 20 + (hash(name) % 100),
                "humidity": 50 + (hash(name) % 35),
                "pop_density": district.get("population", 1000000) / 1000,
            }

        zone = build_zone_from_sample(district, sample, dengue_model, malaria_model)

        if zone["risk_level"] == "high":
            high.append(zone)
        elif zone["risk_level"] == "moderate":
            moderate.append(zone)
        elif zone["risk_level"] == "low" and zone["dengue_risk"] == 0 and zone["malaria_risk"] == 0:
            silent.append(zone)

    return {"high_risk_zones": high, "moderate_risk_zones": moderate, "silent_zones": silent}
