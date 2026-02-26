import React, { useState } from "react";
import axios from "axios";

function Dashboard() {
  const [result, setResult] = useState(null);

  const [form, setForm] = useState({
    temp_c: 30,
    rainfall: 120,
    humidity: 75,
    dengue_lag_1: 10,
    dengue_lag_2: 8,
    dengue_lag_3: 5,
    pop_density: 300
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: Number(e.target.value) });
  };

  const predict = async () => {
    const res = await axios.post(
      "http://127.0.0.1:8000/predict/dengue",
      form
    );
    setResult(res.data.dengue_risk);
  };

  return (
    <div style={{ padding: 40 }}>
      <h2>🦟 Dengue Risk Prediction</h2>

      {Object.keys(form).map((key) => (
        <div key={key}>
          <label>{key}</label>
          <input
            name={key}
            value={form[key]}
            onChange={handleChange}
            style={{ marginLeft: 10 }}
          />
        </div>
      ))}

      <button onClick={predict} style={{ marginTop: 20 }}>
        Predict Risk
      </button>

      {result !== null && (
        <h3>Predicted Risk Level: {result}</h3>
      )}
    </div>
  );
}

export default Dashboard;
