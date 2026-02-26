import React, { useEffect, useState } from "react";
import axios from "axios";
import "./Zones.css";

function Zones() {
  const [zones, setZones] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedZone, setSelectedZone] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [zonesRes, summaryRes] = await Promise.all([
        axios.get("http://127.0.0.1:8000/zones?state=Maharashtra", { timeout: 10000 }),
        axios.get("http://127.0.0.1:8000/maharashtra-summary", { timeout: 10000 }),
      ]);
      setZones(zonesRes.data);
      setSummary(summaryRes.data);
      setLoading(false);
    } catch (err) {
      console.error("Zones/summary error:", err.message);
      setError("Failed to load zone information. Is backend running?");
      setLoading(false);
    }
  };

  // pick a default zone (first high risk or first moderate or null)
  useEffect(() => {
    if (zones) {
      if (zones.high_risk_zones && zones.high_risk_zones.length > 0) {
        setSelectedZone(zones.high_risk_zones[0]);
      } else if (zones.moderate_risk_zones && zones.moderate_risk_zones.length > 0) {
        setSelectedZone(zones.moderate_risk_zones[0]);
      } else if (zones.silent_zones && zones.silent_zones.length > 0) {
        setSelectedZone(zones.silent_zones[0]);
      } else {
        setSelectedZone(null);
      }
    }
  }, [zones]);

  if (loading) {
    return <div className="zones-loading">⏳ Loading zones data...</div>;
  }

  if (error) {
    return <div className="zones-error">{error}</div>;
  }

  const renderList = (arr, label) => {
    if (!arr || arr.length === 0) {
      return <div className="zones-empty">No {label.toLowerCase()} currently.</div>;
    }
    return arr.map((z, idx) => (
      <div
        key={z.name + idx}
        className={`zone-card ${label.toLowerCase().replace(' ', '-')}`}
        onClick={() => setSelectedZone(z)}
      >
        <strong>{z.name}</strong> — {label === "High Risk Zones" ? "high" : label === "Moderate Risk Zones" ? "moderate" : "safe"}
        <div className="zone-metrics">
          <span>Temp: {z.temperature}°C</span>
          <span>Rain: {z.rainfall}mm</span>
          <span>Hum: {z.humidity}%</span>
        </div>
      </div>
    ));
  };

  return (
    <div className="zones-container">
      <h2 className="zones-title">⚠️ Maharashtra Zones</h2>

      {summary && (
        <div className="zones-summary">
          <strong>Maharashtra Current Cases:</strong> Dengue: {summary.total_dengue} • Malaria: {summary.total_malaria} • Last updated: {new Date(summary.last_updated).toLocaleString()}
        </div>
      )}

      {selectedZone && (
        <div className="zones-main">
          <h3>{selectedZone.name} — Main Metrics</h3>
          <div className="zones-main-details">
            <span>Risk: {selectedZone.risk_level}</span>
            <span>Temp: {selectedZone.temperature}°C</span>
            <span>Rain: {selectedZone.rainfall}mm</span>
            <span>Humidity: {selectedZone.humidity}%</span>
            <span>Last updated: {new Date(selectedZone.last_updated).toLocaleString()}</span>
          </div>
        </div>
      )}

      <div className="zones-section">
        <h4>🔥 High Risk Zones</h4>
        {renderList(zones.high_risk_zones, "High Risk Zones")}
      </div>

      <div className="zones-section">
        <h4>🟡 Moderate Zones</h4>
        {renderList(zones.moderate_risk_zones, "Moderate Risk Zones")}
      </div>

      <div className="zones-section">
        <h4>🟢 Silent Zones</h4>
        {renderList(zones.silent_zones, "Silent Zones")}
      </div>
    </div>
  );
}

export default Zones;
