import React, { useEffect, useState } from "react";
import axios from "axios";
import "./Weather.css";

function Weather() {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchWeather();
    const interval = setInterval(fetchWeather, 300000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, []);

  const fetchWeather = async () => {
    try {
      console.log("Fetching weather data...");
      const res = await axios.get("http://127.0.0.1:8000/weather", {
        timeout: 10000
      });
      console.log("Weather data loaded");
      setWeather(res.data);
      setLoading(false);
    } catch (err) {
      console.error("Weather error:", err.message);
      setError(err.response?.status === 500 
        ? "Backend error loading weather" 
        : "Failed to load weather data. Check if backend is running.");
      setLoading(false);
    }
  };

  const getWeatherIcon = (condition) => {
    if (condition === "Sunny") return "☀️";
    if (condition === "Cloudy") return "☁️";
    if (condition === "Rainy") return "🌧️";
    return "🌡️";
  };

  if (loading) {
    return <div className="weather-loading">🌤️ Loading weather data...</div>;
  }

  if (error) {
    return <div className="weather-error">{error}</div>;
  }

  return (
    <div className="weather-container">
      <div className="weather-header">
        <h2 className="weather-title">🌦️ Real-time Weather Data</h2>
        <p className="weather-updated">
          Last updated: {new Date(weather.timestamp).toLocaleTimeString()}
        </p>
      </div>

      <div className="weather-grid">
        {weather.cities.slice(0, 3).map((city, index) => (
          <div
            key={city.name}
            className="weather-card"
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <div className="weather-icon">
              {getWeatherIcon(city.condition)}
            </div>

            <div className="city-name">{city.name}</div>

            <div className="weather-condition">{city.condition}</div>

            <div className="weather-metrics">
              <div className="weather-metric">
                <span className="metric-label">Temperature</span>
                <div className="metric-value">{city.temp}°C</div>
              </div>

              <div className="weather-metric">
                <span className="metric-label">Humidity</span>
                <div className="metric-value">{city.humidity}%</div>
              </div>

              <div className="weather-metric">
                <span className="metric-label">Rainfall</span>
                <div className="metric-value">{city.rainfall}mm</div>
              </div>
            </div>

            <div className="risk-indicator">
              {city.temp > 30 && city.humidity > 70 && (
                <div className="risk-badge high">⚠️ High Risk Conditions</div>
              )}
              {(city.temp > 25 || city.humidity > 65) && city.temp <= 30 && (
                <div className="risk-badge moderate">📌 Moderate Conditions</div>
              )}
              {city.temp <= 25 && city.humidity <= 65 && (
                <div className="risk-badge safe">✓ Favorable Conditions</div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="weather-insights">
        <h3>💡 Weather Insights</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <span className="insight-icon">🌡️</span>
            <span className="insight-text">
              High temperatures combined with humidity increase disease
              transmission risk for dengue and malaria
            </span>
          </div>
          <div className="insight-card">
            <span className="insight-icon">🌧️</span>
            <span className="insight-text">
              Rainfall creates breeding grounds for mosquitoes, increasing
              disease potential
            </span>
          </div>
          <div className="insight-card">
            <span className="insight-icon">💧</span>
            <span className="insight-text">
              High humidity (&gt;70%) accelerates virus development in vectors
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Weather;
