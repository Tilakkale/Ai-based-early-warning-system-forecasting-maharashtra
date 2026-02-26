import React, { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Popup,
  CircleMarker,
  GeoJSON,
} from "react-leaflet";
import L from "leaflet";
import axios from "axios";
import "./MapView.css";

// Fix default marker icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

function MapView() {
  const [predictions, setPredictions] = useState([]);
  const [geoJson, setGeoJson] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedMarker, setSelectedMarker] = useState(null);

  useEffect(() => {
    fetchPredictions();
    fetchGeoJson();
  }, []);

  const fetchPredictions = async () => {
    try {
      console.log("Fetching map predictions for Maharashtra...");
      const res = await axios.get("http://127.0.0.1:8000/district-predictions?state=Maharashtra", {
        timeout: 10000
      });
      console.log("Map predictions loaded:", res.data.predictions?.length || 0, "districts");
      const mhDistricts = res.data.predictions ? res.data.predictions.filter(d => !d.state || d.state === "Maharashtra") : [];
      setPredictions(mhDistricts);
      setLoading(false);
    } catch (err) {
      console.error("Map predictions error:", err.message);
      setLoading(false);
    }
  };

  const fetchGeoJson = async () => {
    try {
      // public geojson of Maharashtra districts (example URL)
      const url = "https://raw.githubusercontent.com/geohacker/india/master/india/district/maharashtra.geojson";
      const resp = await axios.get(url, { timeout: 15000 });
      setGeoJson(resp.data);
    } catch (err) {
      console.error("Failed to load Maharashtra geojson", err.message);
    }
  };

  const getRiskColor = (riskLevel) => {
    if (riskLevel === "high") return "#ef4444";
    if (riskLevel === "moderate") return "#eab308";
    return "#10b981";
  };

  const getRiskOpacity = (riskLevel) => {
    if (riskLevel === "high") return 0.8;
    if (riskLevel === "moderate") return 0.6;
    return 0.4;
  };

  if (loading) {
    return (
      <div className="map-container">
        <div className="map-loading">🗺️ Loading map...</div>
      </div>
    );
  }

  const centerLat =
    predictions.reduce((sum, p) => sum + p.lat, 0) / predictions.length || 20;
  const centerLng =
    predictions.reduce((sum, p) => sum + p.lng, 0) / predictions.length || 78;

  return (
    <div className="map-view-container">
      <h2 className="map-title">🗺️ Disease Risk Map</h2>
      <div className="map-legend">
        <div className="legend-item">
          <div
            className="legend-color"
            style={{ backgroundColor: "#10b981" }}
          ></div>
          <span>Safe/Silent Zones</span>
        </div>
        <div className="legend-item">
          <div
            className="legend-color"
            style={{ backgroundColor: "#eab308" }}
          ></div>
          <span>Moderate Risk Zones</span>
        </div>
        <div className="legend-item">
          <div
            className="legend-color"
            style={{ backgroundColor: "#ef4444" }}
          ></div>
          <span>High Risk Zones</span>
        </div>
      </div>

      <MapContainer
        center={[centerLat, centerLng]}
        zoom={6}
        className="map-container"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        {/* draw district boundaries if geoJson loaded */}
        {geoJson && (
          <GeoJSON
            data={geoJson}
            style={(feature) => {
              // match district name to prediction risk
              const name = feature.properties.district || feature.properties.NAME_2 || feature.properties.NAME;
              const pred = predictions.find(d => d.name && name && d.name.toLowerCase().includes(name.toLowerCase()));
              const level = pred ? pred.risk_level : "low";
              return {
                fillColor: getRiskColor(level),
                weight: 1,
                color: "#444",
                fillOpacity: getRiskOpacity(level),
              };
            }}
            onEachFeature={(feature, layer) => {
              const name = feature.properties.district || feature.properties.NAME_2 || feature.properties.NAME;
              layer.bindPopup(name);
            }}
          />
        )}
        {predictions.map((district) => (
          <CircleMarker
            key={district.name}
            center={[district.lat, district.lng]}
            radius={20}
            className={`risk-marker ${district.risk_level}`} // add class for animation
            fillColor={getRiskColor(district.risk_level)}
            fillOpacity={getRiskOpacity(district.risk_level)}
            color={getRiskColor(district.risk_level)}
            weight={2}
            onClick={() => setSelectedMarker(district)}
          >
            <Popup className="custom-popup">
              <div className="popup-content">
                <h4>{district.name}</h4>
                <p>
                  <strong>Risk Level:</strong> {district.risk_level}
                </p>
                <p>
                  <strong>🦟 Dengue:</strong>{" "}
                  {district.dengue_risk === 0
                    ? "Low"
                    : district.dengue_risk === 1
                    ? "Moderate"
                    : "High"}
                </p>
                <p>
                  <strong>🦗 Malaria:</strong>{" "}
                  {district.malaria_risk === 0
                    ? "Low"
                    : district.malaria_risk === 1
                    ? "Moderate"
                    : "High"}
                </p>
                <p>
                  <strong>🌡️ Temperature:</strong> {district.temperature}°C
                </p>
                <p>
                  <strong>💧 Humidity:</strong> {district.humidity}%
                </p>
                <p>
                  <strong>🌧️ Rainfall:</strong> {district.rainfall}mm
                </p>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>

      {selectedMarker && (
        <div className="marker-details">
          <button
            className="close-btn"
            onClick={() => setSelectedMarker(null)}
          >
            ✕
          </button>
          <h3>{selectedMarker.name}</h3>
          <div className="details-grid">
            <div className="detail-item">
              <span>Risk Level</span>
              <strong
                style={{
                  color: getRiskColor(selectedMarker.risk_level),
                }}
              >
                {selectedMarker.risk_level.toUpperCase()}
              </strong>
            </div>
            <div className="detail-item">
              <span>🦟 Dengue</span>
              <strong>
                {selectedMarker.dengue_risk === 0
                  ? "Low"
                  : selectedMarker.dengue_risk === 1
                  ? "Moderate"
                  : "High"}
              </strong>
            </div>
            <div className="detail-item">
              <span>🦗 Malaria</span>
              <strong>
                {selectedMarker.malaria_risk === 0
                  ? "Low"
                  : selectedMarker.malaria_risk === 1
                  ? "Moderate"
                  : "High"}
              </strong>
            </div>
            <div className="detail-item">
              <span>🌡️ Temperature</span>
              <strong>{selectedMarker.temperature}°C</strong>
            </div>
            <div className="detail-item">
              <span>💧 Humidity</span>
              <strong>{selectedMarker.humidity}%</strong>
            </div>
            <div className="detail-item">
              <span>🌧️ Rainfall</span>
              <strong>{selectedMarker.rainfall}mm</strong>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MapView;
