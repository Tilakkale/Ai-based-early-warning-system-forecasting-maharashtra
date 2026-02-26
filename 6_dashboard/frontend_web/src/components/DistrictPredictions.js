import React, { useEffect, useState } from "react";
import axios from "axios";
import "./DistrictPredictions.css";
import DistrictDetails from "./DistrictDetails";

function DistrictPredictions() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState("risk");
  const [selectedDistrict, setSelectedDistrict] = useState(null);
  const [showHigh, setShowHigh] = useState(true);
  const [showModerate, setShowModerate] = useState(true);
  const [showSilent, setShowSilent] = useState(true);

  useEffect(() => {
    fetchPredictions();
  }, []);

  const fetchPredictions = async () => {
    try {
      console.log("Fetching Maharashtra district predictions...");
      const res = await axios.get("http://127.0.0.1:8000/district-predictions?state=Maharashtra", {
        timeout: 10000
      });
      console.log("District predictions loaded:", res.data.predictions?.length || 0, "districts");
      const mhDistricts = res.data.predictions ? res.data.predictions.filter(d => !d.state || d.state === "Maharashtra") : [];
      setPredictions(mhDistricts);
      setLoading(false);
    } catch (err) {
      console.error("District predictions error:", err.message);
      setError("Failed to load Maharashtra districts. Backend may not be responding.");
      setLoading(false);
    }
  };

  const getSortedData = () => {
    const sorted = [...predictions];
    if (sortBy === "risk") {
      return sorted.sort((a, b) => {
        const riskOrder = { high: 0, moderate: 1, low: 2 };
        return riskOrder[a.risk_level] - riskOrder[b.risk_level];
      });
    } else if (sortBy === "name") {
      return sorted.sort((a, b) => a.name.localeCompare(b.name));
    } else if (sortBy === "temp") {
      return sorted.sort((a, b) => b.temperature - a.temperature);
    }
    return sorted;
  };

  if (loading) {
    return (
      <div className="district-loading">
        🔍 Loading district predictions...
      </div>
    );
  }

  if (error) {
    return <div className="district-error">{error}</div>;
  }

  const sortedData = getSortedData();
  const visibleData = sortedData.filter(d => (d.risk_level === 'high' && showHigh) || (d.risk_level === 'moderate' && showModerate) || (d.risk_level === 'low' && showSilent));

  return (
    <div className="district-container">
      <div className="district-header">
        <h2 className="district-title">🌏 Maharashtra Districts</h2>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <div className="sort-controls">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="sort-select"
            >
              <option value="risk">Sort by Risk Level</option>
              <option value="name">Sort by District Name</option>
              <option value="temp">Sort by Temperature</option>
            </select>
          </div>

          <div style={{ display: 'flex', gap: 12, alignItems: 'center', padding: '8px 12px', background: 'rgba(20, 184, 166, 0.1)', borderRadius: '8px' }}>
            <label style={{ fontSize: 13, display: 'flex', alignItems: 'center', gap: 4 }}>
              <input type="checkbox" checked={showHigh} onChange={e => setShowHigh(e.target.checked)} />
              <span>🔴 High Risk</span>
            </label>
            <label style={{ fontSize: 13, display: 'flex', alignItems: 'center', gap: 4 }}>
              <input type="checkbox" checked={showModerate} onChange={e => setShowModerate(e.target.checked)} />
              <span>🟡 Moderate</span>
            </label>
            <label style={{ fontSize: 13, display: 'flex', alignItems: 'center', gap: 4 }}>
              <input type="checkbox" checked={showSilent} onChange={e => setShowSilent(e.target.checked)} />
              <span>🟢 Safe/Silent</span>
            </label>
          </div>
        </div>
      </div>

      <div className="stats-overview">
        <div className="stat-item">
          <span className="stat-icon">📍</span>
          <span className="stat-text">Total Districts: {predictions.length}</span>
        </div>
        <div className="stat-item high">
          <span className="stat-icon">🔴</span>
          <span className="stat-text">
            High Risk: {predictions.filter((p) => p.risk_level === "high").length}
          </span>
        </div>
        <div className="stat-item moderate">
          <span className="stat-icon">🟡</span>
          <span className="stat-text">
            Moderate Risk: {predictions.filter((p) => p.risk_level === "moderate").length}
          </span>
        </div>
        <div className="stat-item safe">
          <span className="stat-icon">🟢</span>
          <span className="stat-text">
            Safe: {predictions.filter((p) => p.risk_level === "low").length}
          </span>
        </div>
      </div>

      <div className="district-grid">
        {visibleData.map((district, index) => (
          <div
            key={district.name}
            className={`district-card ${district.risk_level}`}
            style={{ animationDelay: `${index * 0.05}s` }}
          >
            <div className="card-header">
              <h3 className="district-name">{district.name}</h3>
              <div className={`risk-badge ${district.risk_level}`}>
                {district.risk_level === "high" && "🔴 HIGH RISK"}
                {district.risk_level === "moderate" && "🟡 MODERATE RISK"}
                {district.risk_level === "low" && "🟢 SAFE/SILENT"}
              </div>
            </div>

            <div className="card-metrics">
              <div className="metric-row">
                <div className="metric">
                  <span className="metric-label">🦟 Dengue Risk</span>
                  <span className="metric-value">
                    {district.dengue_risk === 0 && "Low"}
                    {district.dengue_risk === 1 && "Moderate"}
                    {district.dengue_risk === 2 && "High"}
                  </span>
                </div>
                <div className="metric">
                  <span className="metric-label">🦗 Malaria Risk</span>
                  <span className="metric-value">
                    {district.malaria_risk === 0 && "Low"}
                    {district.malaria_risk === 1 && "Moderate"}
                    {district.malaria_risk === 2 && "High"}
                  </span>
                </div>
              </div>

              <div className="metric-row">
                <div className="metric">
                  <span className="metric-label">🌡️ Temperature</span>
                  <span className="metric-value">{district.temperature}°C</span>
                </div>
                <div className="metric">
                  <span className="metric-label">💧 Humidity</span>
                  <span className="metric-value">{district.humidity}%</span>
                </div>
              </div>

              <div className="metric-row">
                <div className="metric">
                  <span className="metric-label">🌧️ Rainfall</span>
                  <span className="metric-value">{district.rainfall}mm</span>
                </div>
                <div className="metric">
                  <span className="metric-label">📍 Location</span>
                  <span className="metric-value">
                    {district.lat.toFixed(2)}, {district.lng.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>

            <div className="card-footer">
              <button className="action-btn" onClick={() => setSelectedDistrict(district.name)}>📊 View Details</button>
            </div>
          </div>
        ))}
      </div>
      {selectedDistrict && (
        <DistrictDetails name={selectedDistrict} onClose={() => setSelectedDistrict(null)} />
      )}
    </div>
  );
}

export default DistrictPredictions;
