import React, { useState } from "react";
import "./App.css";

// page components
import Charts from "./components/Charts";
import Zones from "./components/Zones";
import DistrictPredictions from "./components/DistrictPredictions";
import MapView from "./components/MapView";
import Weather from "./components/Weather";

function App() {
  const [activePage, setActivePage] = useState("predict");

  return (
    <div className="App">
      <Navbar activePage={activePage} setActivePage={setActivePage} />
      <div className="dashboard-container">
        {activePage === "predict" && <PredictPage />}
        {activePage === "analytics" && <Charts />}
        {activePage === "zones" && <Zones />}
        {activePage === "districts" && <DistrictPredictions />}
        {activePage === "map" && <MapView />}
        {activePage === "weather" && <Weather />}
      </div>
    </div>
  );
}

// simple navigation bar
function Navbar({ activePage, setActivePage }) {
  const pages = [
    { key: "predict", label: "PREDICT" },
    { key: "analytics", label: "ANALYTICS" },
    { key: "zones", label: "ZONES" },
    { key: "districts", label: "DISTRICTS" },
    { key: "map", label: "MAP" },
    { key: "weather", label: "WEATHER" },
  ];
  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="nav-brand">Epidemic Forecasting</div>
        <div className="nav-menu">
          {pages.map((p) => (
            <div
              key={p.key}
              className={`nav-item ${activePage === p.key ? "active" : ""}`}
              onClick={() => setActivePage(p.key)}
            >
              {p.label}
            </div>
          ))}
        </div>
      </div>
    </nav>
  );
}

export default App;

// component that renders prediction form/results
function PredictPage() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [form, setForm] = useState({
    temp_c: 30,
    rainfall: 120,
    humidity: 75,
    pop_density: 300,
    dengue_lag_1: 10,
    dengue_lag_2: 8,
    dengue_lag_3: 5,
    malaria_lag_1: 5,
    malaria_lag_2: 3,
    malaria_lag_3: 2,
    risk_index: 2.5,
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: Number(e.target.value) });
    setError(null);
  };

  const predict = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError("Failed to get prediction. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevel = (value) => {
    if (value === 0) return "safe";
    if (value === 1) return "moderate";
    return "high";
  };

  const getRiskLabel = (value) => {
    if (value === 0) return "✓ Safe";
    if (value === 1) return "⚠ Moderate Risk";
    return "✗ High Risk";
  };

  const formFields = [
    { key: "temp_c", label: "Temperature (°C)", min: 15, max: 40, step: 0.1 },
    { key: "rainfall", label: "Rainfall (mm)", min: 0, max: 500, step: 1 },
    { key: "humidity", label: "Humidity (%)", min: 0, max: 100, step: 0.1 },
    { key: "pop_density", label: "Population Density", min: 10, max: 1000, step: 1 },
    { key: "dengue_lag_1", label: "Dengue Cases (Lag 1)", min: 0, max: 100, step: 1 },
    { key: "dengue_lag_2", label: "Dengue Cases (Lag 2)", min: 0, max: 100, step: 1 },
    { key: "dengue_lag_3", label: "Dengue Cases (Lag 3)", min: 0, max: 100, step: 1 },
    { key: "malaria_lag_1", label: "Malaria Cases (Lag 1)", min: 0, max: 100, step: 1 },
  ];

  return (
    <>
      <h2 className="dashboard-title">🧠 Predict Disease Risk</h2>
      <div className="content-grid">
        <div className="form-card">
          <h3>📊 Environmental Parameters</h3>
          <div>
            {formFields.slice(0, 4).map((field) => (
              <div key={field.key} className="form-group">
                <label className="form-label">{field.label}</label>
                <input
                  type={field.step === 1 ? "range" : "range"}
                  name={field.key}
                  value={form[field.key]}
                  onChange={handleChange}
                  min={field.min}
                  max={field.max}
                  step={field.step}
                  className="form-input"
                />
                <div
                  style={{
                    marginTop: "8px",
                    fontSize: "0.9rem",
                    color: "var(--text-secondary)",
                  }}
                >
                  {form[field.key].toFixed(1)}
                </div>
              </div>
            ))}
          </div>

          <h3 style={{ marginTop: "30px" }}>📈 Disease History</h3>
          <div>
            {formFields.slice(4).map((field) => (
              <div key={field.key} className="form-group">
                <label className="form-label">{field.label}</label>
                <input
                  type="number"
                  name={field.key}
                  value={form[field.key]}
                  onChange={handleChange}
                  className="form-input"
                  min={field.min}
                  max={field.max}
                />
              </div>
            ))}
            <div className="form-group">
              <label className="form-label">Risk Index</label>
              <input
                type="number"
                name="risk_index"
                value={form.risk_index}
                onChange={handleChange}
                className="form-input"
                min="0"
                max="10"
                step="0.1"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Malaria Cases (Lag 2)</label>
              <input
                type="number"
                name="malaria_lag_2"
                value={form.malaria_lag_2}
                onChange={handleChange}
                className="form-input"
                min="0"
                max="100"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Malaria Cases (Lag 3)</label>
              <input
                type="number"
                name="malaria_lag_3"
                value={form.malaria_lag_3}
                onChange={handleChange}
                className="form-input"
                min="0"
                max="100"
              />
            </div>
          </div>

          <button
            onClick={predict}
            className="predict-button"
            disabled={loading}
          >
            {loading ? "⏳ Analyzing..." : "🎯 Predict Risk"}
          </button>

          {error && (
            <div
              style={{
                marginTop: "20px",
                padding: "15px",
                background: "rgba(239, 68, 68, 0.1)",
                border: "2px solid rgba(239, 68, 68, 0.5)",
                borderRadius: "10px",
                color: "#fca5a5",
                fontSize: "0.95rem",
              }}
            >
              {error}
            </div>
          )}
        </div>

        <div className="results-container">
          <h3 className="results-title">📋 Prediction Results</h3>
          {result ? (
            <div>
              <div
                className={`result-card ${getRiskLevel(result.dengue_risk)}`}
              >
                <div className="result-label">🦟 Dengue Risk</div>
                <div className="result-value">{getRiskLabel(result.dengue_risk)}</div>
                <div className="result-status">
                  {result.dengue_risk === 0 &&
                    "Disease transmission risk is minimal"}
                  {result.dengue_risk === 1 &&
                    "Moderate precautions recommended"}
                  {result.dengue_risk === 2 &&
                    "High alert - immediate action advised"}
                </div>
              </div>

              <div
                className={`result-card ${getRiskLevel(result.malaria_risk)}`}
              >
                <div className="result-label">🦗 Malaria Risk</div>
                <div className="result-value">{getRiskLabel(result.malaria_risk)}</div>
                <div className="result-status">
                  {result.malaria_risk === 0 &&
                    "Disease transmission risk is minimal"}
                  {result.malaria_risk === 1 &&
                    "Moderate precautions recommended"}
                  {result.malaria_risk === 2 &&
                    "High alert - immediate action advised"}
                </div>
              </div>

              <div
                style={{
                  marginTop: "30px",
                  padding: "20px",
                  background: "rgba(20, 184, 166, 0.05)",
                  border: "2px solid rgba(20, 184, 166, 0.3)",
                }}
              >
                <strong style={{ color: "var(--primary-light)" }}>
                  💡 Recommendation:
                </strong>
                <p style={{ marginTop: "10px", lineHeight: "1.6" }}>
                  Based on the current environmental conditions and disease
                  history, monitor the situation closely. Implement preventive
                  measures and maintain surveillance protocols.
                </p>
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">📡</div>
              <div className="empty-state-text">
                Configure parameters and click "Predict Risk" to generate forecasts
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
} 