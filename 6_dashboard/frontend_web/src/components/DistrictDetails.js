import React, { useEffect, useState } from "react";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

function DistrictDetails({ name, onClose }) {
  const [samples, setSamples] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!name) return;
    (async () => {
      setLoading(true);
      try {
        const [histRes, fcRes] = await Promise.all([
          axios.get(`http://127.0.0.1:8000/district/${encodeURIComponent(name)}/history?limit=100`, { timeout: 10000 }),
          axios.get(`http://127.0.0.1:8000/forecast/${encodeURIComponent(name)}?periods=7`, { timeout: 10000 }),
        ]);
        const data = histRes.data.samples || [];
        const parsed = data.map(s => ({
          ts: s._ts,
          temp: s.temp || s.temp_c || null,
          humidity: s.humidity || null,
          rainfall: s.rainfall || null,
          payload: s,
        })).filter(x => x.ts).reverse();
        setSamples(parsed);
        setForecast(fcRes.data.forecast || []);
        setLoading(false);
      } catch (err) {
        setError("Failed to load history");
        setLoading(false);
      }
    })();
  }, [name]);

  // simple forecast: linear extrapolation of last two temps
  const forecastTemp = () => {
    if (samples.length < 2) return null;
    const a = samples[samples.length - 2].temp;
    const b = samples[samples.length - 1].temp;
    if (a == null || b == null) return null;
    const delta = b - a;
    return (b + delta).toFixed(1);
  };

  return (
    <div style={{ position: "fixed", left: 0, top: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 9999 }}>
      <div style={{ width: "90%", maxWidth: 900, background: "#0b1220", padding: 18, borderRadius: 8, color: "#e6eef6" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3 style={{ margin: 0 }}>{name} — Recent Data</h3>
          <div>
            <button onClick={onClose} style={{ padding: "6px 10px" }}>Close</button>
          </div>
        </div>

        {loading && <div style={{ marginTop: 12 }}>Loading history...</div>}
        {error && <div style={{ marginTop: 12, color: "#fca5a5" }}>{error}</div>}

        {!loading && samples.length === 0 && <div style={{ marginTop: 12 }}>No historical samples available for this district.</div>}

        {!loading && samples.length > 0 && (
          <div style={{ marginTop: 12 }}>
            <div style={{ height: 260 }}>
              <ResponsiveContainer>
                <LineChart data={samples}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="ts" tickFormatter={(t) => new Date(t).toLocaleTimeString()} />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="temp" stroke="#f59e0b" dot={false} name="Temperature (°C)" />
                  <Line type="monotone" dataKey="humidity" stroke="#3b82f6" dot={false} name="Humidity (%)" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div style={{ marginTop: 12, display: "flex", gap: 12 }}>
              <div style={{ padding: 10, border: "1px solid rgba(255,255,255,0.06)", borderRadius: 8 }}>
                <div style={{ fontSize: 12, color: "#9ca3af" }}>Last Temp (°C)</div>
                <div style={{ fontSize: 18 }}>{samples[samples.length-1].temp ?? "-"}</div>
              </div>
              <div style={{ padding: 10, border: "1px solid rgba(255,255,255,0.06)", borderRadius: 8 }}>
                <div style={{ fontSize: 12, color: "#9ca3af" }}>Last Humidity (%)</div>
                <div style={{ fontSize: 18 }}>{samples[samples.length-1].humidity ?? "-"}</div>
              </div>
              <div style={{ padding: 10, border: "1px solid rgba(255,255,255,0.06)", borderRadius: 8 }}>
                <div style={{ fontSize: 12, color: "#9ca3af" }}>Forecast Temp (next)</div>
                <div style={{ fontSize: 18 }}>{forecastTemp() ?? "-"}</div>
              </div>
            </div>

            {forecast && forecast.length > 0 && (
              <div style={{ marginTop: 18, height: 260 }}>
                <h4 style={{ marginBottom: 8 }}>7-Day Forecast</h4>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={forecast}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="date" tickFormatter={(d) => new Date(d).toLocaleDateString()} />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Line yAxisId="left" type="monotone" dataKey="temp_forecast" stroke="#f59e0b" strokeDasharray="5 5" name="Temperature Forecast (°C)" />
                    <Line yAxisId="right" type="monotone" dataKey="cases_forecast" stroke="#ef4444" strokeDasharray="5 5" name="Est. Cases" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            <div style={{ marginTop: 18 }}>
              <h4 style={{ marginBottom: 8 }}>Recent Samples</h4>
              <div style={{ maxHeight: 220, overflow: "auto", borderTop: "1px solid rgba(255,255,255,0.04)", paddingTop: 8 }}>
                {samples.slice().reverse().map((s, i) => (
                  <div key={i} style={{ padding: 8, borderBottom: "1px solid rgba(255,255,255,0.02)" }}>
                    <div style={{ fontSize: 12, color: "#9ca3af" }}>{new Date(s.ts).toLocaleString()}</div>
                    <div style={{ fontSize: 14 }}>Temp: {s.temp ?? "-"}°C • Humidity: {s.humidity ?? "-"}% • Rain: {s.rainfall ?? "-"}mm</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default DistrictDetails;
