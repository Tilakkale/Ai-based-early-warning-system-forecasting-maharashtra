import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import axios from "axios";
import "./Charts.css";

function Charts() {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [riskSummary, setRiskSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      console.log("Fetching analytics data...");
      const analyticsRes = await axios.get(
        "http://127.0.0.1:8000/analytics",
        { timeout: 10000 }
      );
      console.log("Fetching risk summary...");
      const summaryRes = await axios.get(
        "http://127.0.0.1:8000/risk-summary",
        { timeout: 10000 }
      );
      setAnalyticsData(analyticsRes.data);
      setRiskSummary(summaryRes.data);
      setLoading(false);
    } catch (err) {
      console.error("Analytics error:", err.message);
      setError(err.response?.status === 500 
        ? "Backend error loading analytics" 
        : "Failed to load analytics data. Check if backend is running.");
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="charts-loading">📊 Loading analytics...</div>;
  }

  if (error) {
    return <div className="charts-error">{error}</div>;
  }

  return (
    <div className="charts-container">
      <h2 className="charts-title">📈 Disease Trends & Analytics</h2>

      {/* Risk Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card high-risk">
          <div className="card-value">{riskSummary.high_risk_districts}</div>
          <div className="card-label">High Risk Districts</div>
        </div>
        <div className="summary-card moderate-risk">
          <div className="card-value">{riskSummary.moderate_risk_districts}</div>
          <div className="card-label">Moderate Risk Districts</div>
        </div>
        <div className="summary-card low-risk">
          <div className="card-value">{riskSummary.low_risk_districts}</div>
          <div className="card-label">Safe Districts</div>
        </div>
        <div className="summary-card">
          <div className="card-value">{riskSummary.average_dengue_risk.toFixed(1)}</div>
          <div className="card-label">Avg Dengue Risk</div>
        </div>
        <div className="summary-card">
          <div className="card-value">{riskSummary.average_malaria_risk.toFixed(1)}</div>
          <div className="card-label">Avg Malaria Risk</div>
        </div>
      </div>

      {/* Trend Charts */}
      <div className="charts-grid">
        {/* Cases Trend */}
        <div className="chart-card">
          <h3>Disease Cases Trend (30 days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={analyticsData.trend_data}>
              <defs>
                <linearGradient id="colorDengue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorMalaria" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="date" stroke="#cbd5e1" />
              <YAxis stroke="#cbd5e1" />
              <Tooltip
                contentStyle={{
                  background: "rgba(30, 41, 59, 0.9)",
                  border: "1px solid #14b8a6",
                }}
              />
              <Area
                type="monotone"
                dataKey="dengue_cases"
                stroke="#f59e0b"
                fillOpacity={1}
                fill="url(#colorDengue)"
              />
              <Area
                type="monotone"
                dataKey="malaria_cases"
                stroke="#ef4444"
                fillOpacity={1}
                fill="url(#colorMalaria)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Temperature Trend */}
        <div className="chart-card">
          <h3>Temperature Trend (30 days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analyticsData.trend_data}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="date" stroke="#cbd5e1" />
              <YAxis stroke="#cbd5e1" />
              <Tooltip
                contentStyle={{
                  background: "rgba(30, 41, 59, 0.9)",
                  border: "1px solid #14b8a6",
                }}
              />
              <Line
                type="monotone"
                dataKey="temp_avg"
                stroke="#14b8a6"
                strokeWidth={2}
                dot={false}
                isAnimationActive
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Rainfall Bar Chart */}
        <div className="chart-card">
          <h3>Weekly Rainfall Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={analyticsData.trend_data.filter((_, i) => i % 7 === 0)}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="date" stroke="#cbd5e1" />
              <YAxis stroke="#cbd5e1" />
              <Tooltip
                contentStyle={{
                  background: "rgba(30, 41, 59, 0.9)",
                  border: "1px solid #14b8a6",
                }}
              />
              <Bar dataKey="rainfall" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Risk Distribution */}
        <div className="chart-card">
          <h3>Risk Level Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={[
                {
                  name: "Districts",
                  high: riskSummary.high_risk_districts,
                  moderate: riskSummary.moderate_risk_districts,
                  low: riskSummary.low_risk_districts,
                },
              ]}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="name" stroke="#cbd5e1" />
              <YAxis stroke="#cbd5e1" />
              <Tooltip
                contentStyle={{
                  background: "rgba(30, 41, 59, 0.9)",
                  border: "1px solid #14b8a6",
                }}
              />
              <Legend />
              <Bar dataKey="high" stackId="a" fill="#ef4444" />
              <Bar dataKey="moderate" stackId="a" fill="#eab308" />
              <Bar dataKey="low" stackId="a" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Statistics */}
      <div className="statistics-grid">
        <div className="stat-box">
          <span className="stat-label">Total Dengue Cases (30d):</span>
          <span className="stat-value">{analyticsData.summary.total_dengue}</span>
        </div>
        <div className="stat-box">
          <span className="stat-label">Total Malaria Cases (30d):</span>
          <span className="stat-value">{analyticsData.summary.total_malaria}</span>
        </div>
        <div className="stat-box">
          <span className="stat-label">Avg Temperature:</span>
          <span className="stat-value">{analyticsData.summary.avg_temperature}°C</span>
        </div>
        <div className="stat-box">
          <span className="stat-label">Total Rainfall (30d):</span>
          <span className="stat-value">{analyticsData.summary.total_rainfall}mm</span>
        </div>
      </div>
    </div>
  );
}

export default Charts;
