from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import os
from pathlib import Path
from datetime import datetime, timedelta
from fastapi import HTTPException
import pandas as pd
import utils
import sqlite3
import json
import random

def simple_forecast(values, periods=7):
    """Simple exponential smoothing forecast.
    
    If fewer than 2 values, returns linear extension.
    """
    if not values or len(values) < 2:
        if not values:
            return [None] * periods
        return [values[0]] * periods
    
    alpha = 0.3
    last_val = values[-1]
    second_last = values[-2]
    trend = last_val - second_last
    
    forecast = []
    current = last_val
    for _ in range(periods):
        current = current + alpha * trend
        forecast.append(round(current, 1))
    return forecast

app = FastAPI(title="Epidemic Prediction API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models - use absolute path
model_dir = Path(__file__).parent / "models"
dengue_model = joblib.load(model_dir / "best_dengue_risk_model.pkl")
malaria_model = joblib.load(model_dir / "best_malaria_binary_risk_model.pkl")

# try loading encoder so we can return original labels
try:
    dengue_encoder = joblib.load(model_dir / "dengue_risk_encoder.pkl")
except Exception:
    dengue_encoder = None

# cache feature names for convenience (could change if models replaced at runtime)
dengue_feature_names = list(dengue_model.feature_names_in_) if hasattr(dengue_model, "feature_names_in_") else []
malaria_feature_names = list(malaria_model.feature_names_in_) if hasattr(malaria_model, "feature_names_in_") else []

class PredictionInput(BaseModel):
    # required weather and lags
    temp_c: float
    rainfall: float
    humidity: float

    # optional / extended features (defaults to 0 when not provided)
    pop_density: float = 0.0
    risk_index: float = 0.0
    lai: float = 0.0
    population: float = 0.0
    urban_percent: float = 0.0
    dengue_lag_1: float = 0.0
    dengue_lag_2: float = 0.0
    dengue_lag_3: float = 0.0
    malaria_lag_1: float = 0.0
    malaria_lag_2: float = 0.0
    malaria_lag_3: float = 0.0
    dengue_trend: float = 0.0
    malaria_trend: float = 0.0

# Sample district data
DISTRICTS = [
    {"name": "Mumbai", "lat": 19.0760, "lng": 72.8777, "population": 20961472, "state": "Maharashtra"},
    {"name": "Delhi", "lat": 28.7041, "lng": 77.1025, "population": 16753235, "state": "Delhi"},
    {"name": "Bangalore", "lat": 12.9716, "lng": 77.5946, "population": 9621008, "state": "Karnataka"},
    {"name": "Hyderabad", "lat": 17.3850, "lng": 78.4867, "population": 6809970, "state": "Telangana"},
    {"name": "Chennai", "lat": 13.0827, "lng": 80.2707, "population": 7088000, "state": "Tamil Nadu"},
    {"name": "Kolkata", "lat": 22.5726, "lng": 88.3639, "population": 14681900, "state": "West Bengal"},
    {"name": "Pune", "lat": 18.5204, "lng": 73.8567, "population": 6430400, "state": "Maharashtra"},
    {"name": "Ahmedabad", "lat": 23.0225, "lng": 72.5714, "population": 8450000, "state": "Gujarat"},
    {"name": "Wardha", "lat": 20.7450, "lng": 78.6026, "population": 148801, "state": "Maharashtra"},
]

@app.get("/")
def home():
    return {"message": "Epidemic Prediction API running"}

def _make_feature_vector(model, feature_names, data_dict):
    """Build a single-row numpy vector for `model` using the ordered
    `feature_names`. Missing keys are filled with 0.0 and values coerced to
    float.  This allows the API to work with both old and new models.
    """
    vect = []
    for fname in feature_names:
        # if data_dict has the field, use it; otherwise default to 0
        val = data_dict.get(fname, 0.0)
        try:
            vect.append(float(val))
        except Exception:
            vect.append(0.0)
    return np.array([vect])


@app.post("/predict")
def predict(data: PredictionInput):
    payload = data.model_dump()

    dengue_features = _make_feature_vector(dengue_model, dengue_feature_names, payload)
    malaria_features = _make_feature_vector(malaria_model, malaria_feature_names, payload)

    dengue_pred = dengue_model.predict(dengue_features)[0]
    malaria_pred = malaria_model.predict(malaria_features)[0]

    # Convert numpy types to Python native types for JSON serialization
    dengue_risk = int(dengue_pred)
    malaria_risk = int(malaria_pred)

    result = {"dengue_risk": dengue_risk, "malaria_risk": malaria_risk}
    if dengue_encoder is not None:
        try:
            dengue_label = dengue_encoder.inverse_transform([[dengue_pred]])[0][0]
            result["dengue_label"] = str(dengue_label)
        except Exception:
            pass
    return result

@app.get("/weather")
def get_weather(state: str = "Maharashtra"):
    """Get simulated real-time weather data for major cities or districts.

    By default returns weather only for districts in `Maharashtra`. A client
    can override using the `state` query parameter, e.g. `/weather?state=Delhi`.
    """
    # Build city/district weather from the DISTRICTS list filtered by state
    cities = []
    for d in DISTRICTS:
        if state and d.get("state", "").lower() != state.lower():
            continue
        cities.append({
            "name": d["name"],
            "temp": round(random.uniform(20, 36), 1),
            "humidity": round(random.uniform(40, 90), 1),
            "rainfall": round(random.uniform(0, 200), 1),
            "condition": random.choice(["Sunny", "Cloudy", "Rainy"]),
            "lat": d.get("lat"),
            "lng": d.get("lng")
        })

    # Fallback: if filter yields nothing, return a small default sample
    if not cities:
        cities = [
            {
                "name": "Mumbai",
                "temp": round(random.uniform(25, 35), 1),
                "humidity": round(random.uniform(60, 85), 1),
                "rainfall": round(random.uniform(0, 150), 1),
                "condition": random.choice(["Sunny", "Cloudy", "Rainy"])
            },
        ]

    return {"timestamp": datetime.now().isoformat(), "cities": cities}

@app.get("/districts")
def get_districts():
    """Get all districts with their metadata"""
    return {"districts": DISTRICTS}

@app.get("/district-predictions")
def get_district_predictions(state: str = None):
    """Get predictions for all districts, optionally filtered by `state`.

    If `state` is provided, only districts with matching `state` are returned.
    """
    predictions = []
    for district in DISTRICTS:
        if state and district.get("state", "").lower() != state.lower():
            continue

        temp = random.uniform(20, 35)
        rainfall = random.uniform(50, 200)
        humidity = random.uniform(55, 85)

        # build a dictionary of sample features, using sensible defaults
        sample = {
            "temp_c": temp,
            "rainfall": rainfall,
            "humidity": humidity,
            "risk_index": 2.5,
            "dengue_lag_1": 8,
            "dengue_lag_2": 6,
            "dengue_lag_3": 4,
            "malaria_lag_1": 3,
            "malaria_lag_2": 2,
            "malaria_lag_3": 1,
            "pop_density": district.get("population", 0) / 1000,
            # extended fields default to 0
            "lai": 0.0,
            "population": district.get("population", 0),
            "urban_percent": 0.0,
            "dengue_trend": 0.0,
            "malaria_trend": 0.0,
        }

        dengue_features = _make_feature_vector(dengue_model, dengue_feature_names, sample)
        malaria_features = _make_feature_vector(malaria_model, malaria_feature_names, sample)

        dengue_risk = int(dengue_model.predict(dengue_features)[0])
        malaria_risk = int(malaria_model.predict(malaria_features)[0])
        
        predictions.append({
            "name": district["name"],
            "lat": district["lat"],
            "lng": district["lng"],
            "state": district.get("state"),
            "dengue_risk": dengue_risk,
            "malaria_risk": malaria_risk,
            "temperature": round(temp, 1),
            "rainfall": round(rainfall, 1),
            "humidity": round(humidity, 1),
            "risk_level": "high" if max(dengue_risk, malaria_risk) == 2 else "moderate" if max(dengue_risk, malaria_risk) == 1 else "low"
        })
    
    return {"predictions": predictions}


@app.get("/zones")
def get_zones():
    """Return only High Risk and Silent zones based on latest real-time data when available."""
    state = None
    # allow query param handling by FastAPI: request state from query string
    from fastapi import Request
    # try to read state from query parameters when uvicorn calls
    try:
        request = Request(scope={})
    except Exception:
        request = None

    # Instead of using Request, accept optional query param via function arg would be better.
    # For now default to Maharashtra unless client provides explicit state via query param in URL.
    # We'll inspect environment variable 'DEFAULT_STATE' for override (not required)
    state = "Maharashtra"

    try:
        # use helper to build zones filtered by state
        districts_to_use = [d for d in DISTRICTS if d.get("state", "").lower() == state.lower()]
        zones = utils.get_zones_from_realtime(districts_to_use, dengue_model, malaria_model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    zones["last_updated"] = datetime.now().isoformat()
    return zones


@app.post("/ingest")
def ingest(payload: dict):
    """Ingest real-time data for a district. Minimal payload: {name, temp, humidity, rainfall, ...}.

    Stored in-memory for use by `/zones`. This is intentionally simple; persist to DB for production.
    """
    try:
        entry = utils.ingest_data(payload)
        return {"status": "ok", "entry": entry}
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to ingest data: " + str(e))


@app.get("/district/{name}/history")
def district_history(name: str, limit: int = 100):
    """Return recent ingested samples for a district (most recent first)."""
    db_path = Path(__file__).parent / "data.db"
    if not db_path.exists():
        return {"samples": []}

    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("SELECT payload, ts FROM samples WHERE name = ? ORDER BY id DESC LIMIT ?", (name, limit))
        rows = cur.fetchall()
        conn.close()
        samples = []
        for payload_text, ts in rows:
            try:
                obj = json.loads(payload_text)
            except Exception:
                obj = {"raw": payload_text}
            obj["_ts"] = ts
            samples.append(obj)
        return {"samples": samples}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics")
def get_analytics():
    """Get historical trends and analytics"""
    today = datetime.now()
    trend_data = []
    
    for i in range(30):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        trend_data.append({
            "date": date,
            "dengue_cases": random.randint(10, 150),
            "malaria_cases": random.randint(5, 80),
            "temp_avg": round(random.uniform(20, 35), 1),
            "rainfall": round(random.uniform(0, 200), 1)
        })
    
    return {
        "trend_data": sorted(trend_data, key=lambda x: x["date"]),
        "summary": {
            "total_dengue": sum(d["dengue_cases"] for d in trend_data),
            "total_malaria": sum(d["malaria_cases"] for d in trend_data),
            "avg_temperature": round(np.mean([d["temp_avg"] for d in trend_data]), 1),
            "total_rainfall": round(sum(d["rainfall"] for d in trend_data), 1)
        }
    }


@app.get("/metrics")
def get_metrics():
    """Return evaluation metrics read from the CSV file produced by the evaluation scripts."""
    metrics_path = Path(__file__).parent.parent / "5_evaluation" / "metrics.csv"
    if not metrics_path.exists():
        raise HTTPException(status_code=404, detail="Metrics file not found")
    try:
        df = pd.read_csv(metrics_path, index_col=0)
        return df.to_dict(orient="index")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load metrics: {e}")


@app.get("/maharashtra-summary")
def maharashtra_summary():
    """Return current (simulated) aggregate dengue and malaria case counts for Maharashtra districts."""
    preds = get_district_predictions(state="Maharashtra")["predictions"]
    # Simulate current case counts based on risk levels
    total_dengue = 0
    total_malaria = 0
    details = []
    for p in preds:
        # estimate cases: low->5-20, moderate->20-80, high->80-300
        if p["risk_level"] == "high":
            d_cases = random.randint(80, 300)
            m_cases = random.randint(40, 200)
        elif p["risk_level"] == "moderate":
            d_cases = random.randint(20, 80)
            m_cases = random.randint(10, 60)
        else:
            d_cases = random.randint(0, 20)
            m_cases = random.randint(0, 15)

        total_dengue += d_cases
        total_malaria += m_cases
        details.append({"name": p["name"], "dengue_cases": d_cases, "malaria_cases": m_cases, "risk_level": p["risk_level"]})

    return {"state": "Maharashtra", "total_dengue": total_dengue, "total_malaria": total_malaria, "details": details, "last_updated": datetime.now().isoformat()}

@app.get("/risk-summary")
def get_risk_summary():
    """Get overall risk summary"""
    predictions = get_district_predictions()["predictions"]
    
    high_risk = sum(1 for p in predictions if p["risk_level"] == "high")
    moderate_risk = sum(1 for p in predictions if p["risk_level"] == "moderate")
    low_risk = sum(1 for p in predictions if p["risk_level"] == "low")
    
    avg_dengue = round(np.mean([p["dengue_risk"] for p in predictions]), 1)
    avg_malaria = round(np.mean([p["malaria_risk"] for p in predictions]), 1)
    
    return {
        "high_risk_districts": high_risk,
        "moderate_risk_districts": moderate_risk,
        "low_risk_districts": low_risk,
        "average_dengue_risk": avg_dengue,
        "average_malaria_risk": avg_malaria,
        "last_updated": datetime.now().isoformat()
    }


@app.get("/forecast/{name}")
def forecast_district(name: str, periods: int = 7):
    """Forecast temperature and cases for next N days using stored history."""
    db_path = Path(__file__).parent / "data.db"
    if not db_path.exists():
        return {"forecast": []}

    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("SELECT payload FROM samples WHERE name = ? ORDER BY id ASC LIMIT 100", (name,))
        rows = cur.fetchall()
        conn.close()

        temps = []
        dates = []
        for payload_text, in rows:
            try:
                obj = json.loads(payload_text)
                t = obj.get("temp") or obj.get("temp_c")
                if t is not None:
                    temps.append(float(t))
                    dates.append(obj.get("_ts") or datetime.utcnow().isoformat())
            except Exception:
                pass

        temp_forecast = simple_forecast(temps, periods)

        forecast_data = []
        last_date = datetime.fromisoformat(dates[-1]) if dates else datetime.utcnow()
        for i, temp in enumerate(temp_forecast):
            future_date = last_date + timedelta(days=i + 1)
            forecast_data.append({
                "date": future_date.isoformat(),
                "temp_forecast": temp,
                "cases_forecast": max(0, 20 + (temp - 25) * 3) if temp else None
            })

        return {"forecast": forecast_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    # start uvicorn server when running directly
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
