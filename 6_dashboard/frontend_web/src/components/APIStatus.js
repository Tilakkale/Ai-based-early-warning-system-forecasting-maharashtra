import React, { useEffect, useState } from "react";
import axios from "axios";
import "./APIStatus.css";

function APIStatus() {
  const [status, setStatus] = useState({
    backend: null,
    endpoints: {},
    loading: true,
  });

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkStatus = async () => {
    const endpoints = {
      "Health Check": "/",
      "Get Weather": "/weather",
      "Get Districts": "/districts",
      "Get District Predictions": "/district-predictions",
      "Get Analytics": "/analytics",
      "Get Risk Summary": "/risk-summary",
    };

    const newStatus = {
      backend: null,
      endpoints: {},
      loading: false,
    };

    try {
      // Test backend connection
      const backendTest = await axios.get("http://127.0.0.1:8000/", {
        timeout: 5000,
      });
      newStatus.backend = "✅ Connected";

      // Test each endpoint
      for (const [name, endpoint] of Object.entries(endpoints)) {
        try {
          await axios.get(`http://127.0.0.1:8000${endpoint}`, {
            timeout: 5000,
          });
          newStatus.endpoints[name] = "✅ Working";
        } catch (err) {
          newStatus.endpoints[name] =
            err.code === "ECONNABORTED"
              ? "⏱️ Timeout"
              : "❌ Error: " + (err.response?.status || err.code);
        }
      }
    } catch (err) {
      newStatus.backend = "❌ Cannot connect to backend";
    }

    setStatus(newStatus);
  };

  return (
    <div className="api-status-container">
      <h2>🔧 API Diagnostics</h2>

      <div className="status-card">
        <h3>Backend Connection</h3>
        <div className={`status-item ${status.backend?.includes("✅") ? "success" : "error"}`}>
          {status.backend || "Checking..."}
        </div>
        {status.backend?.includes("❌") && (
          <div className="error-message">
            <strong>⚠️ Backend is not running!</strong>
            <p>Make sure to start the backend server:</p>
            <code>cd 6_dashboard/backend_api</code>
            <code>python -m uvicorn app:app --reload</code>
          </div>
        )}
      </div>

      <div className="status-card">
        <h3>API Endpoints</h3>
        <div className="endpoints-grid">
          {Object.entries(status.endpoints).map(([name, statusText]) => (
            <div
              key={name}
              className={`endpoint-item ${statusText?.includes("✅") ? "success" : "error"}`}
            >
              <div className="endpoint-name">{name}</div>
              <div className="endpoint-status">{statusText || "Checking..."}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="status-card info">
        <h3>📝 Frontend Information</h3>
        <div className="info-item">
          <span>Frontend URL:</span>
          <code>http://localhost:3000</code>
        </div>
        <div className="info-item">
          <span>Backend URL:</span>
          <code>http://127.0.0.1:8000</code>
        </div>
        <div className="info-item">
          <span>API Docs:</span>
          <code>http://127.0.0.1:8000/docs</code>
        </div>
      </div>

      <div className="status-card">
        <h3>🔍 Troubleshooting</h3>
        <ul className="troubleshooting-list">
          <li>
            <strong>Backend not responding?</strong> Check terminal where backend
            is running for errors
          </li>
          <li>
            <strong>CORS errors?</strong> Make sure backend has CORS middleware
            enabled
          </li>
          <li>
            <strong>Timeout errors?</strong> Backend may be slow - try refreshing
          </li>
          <li>
            <strong>404 errors?</strong> Check API endpoint URLs in code
          </li>
          <li>
            <strong>Network errors?</strong> Ensure backend is running on
            127.0.0.1:8000
          </li>
        </ul>
      </div>

      <button onClick={checkStatus} className="refresh-btn">
        🔄 Refresh Status
      </button>
    </div>
  );
}

export default APIStatus;
