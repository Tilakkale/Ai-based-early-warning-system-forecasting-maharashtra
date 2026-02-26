import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

print("\n=== AI EPIDEMIC DATA PIPELINE STARTED ===")

# ======================================
# 1️⃣ LOAD DATASETS
# ======================================

disease = pd.read_csv("1_raw_data/disease_data_final.csv")
pop = pd.read_csv("1_raw_data/population_data.csv")
urban = pd.read_csv("1_raw_data/urban_data.csv")

print("Disease dataset shape:", disease.shape)

# ======================================
# 2️⃣ CLEAN DISTRICT NAMES
# ======================================

for df in [disease, pop, urban]:
    df["district"] = df["district"].astype(str).str.strip().str.title()

# ======================================
# 3️⃣ RENAME COLUMNS
# ======================================

disease = disease.rename(columns={
    "Cases": "cases",
    "Deaths": "deaths",
    "Temp": "temp_kelvin",
    "preci": "rainfall",
    "LAI": "lai",
    "Disease": "disease"
})

# ======================================
# 4️⃣ TEMPERATURE CONVERSION
# ======================================

disease["temp_c"] = disease["temp_kelvin"] - 273.15

# ======================================
# 5️⃣ HUMIDITY FEATURE (REALISTIC APPROX)
# ======================================

print("⚙️ Generating humidity feature...")

rain_norm = (disease["rainfall"] - disease["rainfall"].min()) / (disease["rainfall"].max() - disease["rainfall"].min() + 1e-6)
temp_norm = (disease["temp_c"] - disease["temp_c"].min()) / (disease["temp_c"].max() - disease["temp_c"].min() + 1e-6)

disease["humidity"] = (0.6 * rain_norm + 0.4 * (1 - temp_norm)) * 100
disease["humidity"] = disease["humidity"].fillna(disease["humidity"].mean())

print("✅ Humidity created!")

# ======================================
# 6️⃣ MERGE POPULATION & URBAN DATA
# ======================================

df = disease.merge(pop, on="district", how="left")
df = df.merge(urban, on="district", how="left")

df.to_csv("2_preprocessed_data/merged_dataset.csv", index=False)
print("✅ merged_dataset.csv created")

# ======================================
# 7️⃣ SEPARATE DENGUE & MALARIA
# ======================================

df["dengue_cases"] = np.where(df["disease"] == "Dengue", df["cases"], 0)
df["malaria_cases"] = np.where(df["disease"] == "Malaria", df["cases"], 0)

# ======================================
# 8️⃣ WEEKLY AGGREGATION
# ======================================

weekly = df.groupby(["district", "year", "week_of_outbreak"]).agg({
    "dengue_cases": "sum",
    "malaria_cases": "sum",
    "deaths": "sum",
    "temp_c": "mean",
    "rainfall": "mean",
    "humidity": "mean",
    "lai": "mean",
    "population": "first",
    "pop_density": "first",
    "urban_percent": "first",
    "Latitude": "first",
    "Longitude": "first",
    "mon": "first"
}).reset_index()

print("Weekly dataset shape:", weekly.shape)

# ======================================
# 9️⃣ HANDLE MISSING VALUES
# ======================================

weekly = weekly.sort_values(["district", "year", "week_of_outbreak"])

cols_to_fill = [
    "temp_c", "rainfall", "humidity", "lai",
    "population", "pop_density", "urban_percent",
    "Latitude", "Longitude", "mon"
]

for col in cols_to_fill:
    weekly[col] = weekly.groupby("district")[col].transform(lambda x: x.ffill().bfill())

# ======================================
# 🔟 SEASON FEATURE (NUMERIC - SAFE)
# ======================================

def season_code(month):
    if month in [12, 1, 2]:
        return 0  # Winter
    elif month in [3, 4, 5]:
        return 1  # Summer
    elif month in [6, 7, 8, 9]:
        return 2  # Monsoon
    else:
        return 3  # PostMonsoon

weekly["season_code"] = weekly["mon"].apply(season_code)

print("✅ Season feature added")

# ======================================
# 1️⃣1️⃣ LAG FEATURES (NO BUG VERSION)
# ======================================

weekly = weekly.sort_values(["district", "year", "week_of_outbreak"])

for lag in [1, 2, 3]:
    weekly[f"dengue_lag_{lag}"] = weekly.groupby("district")["dengue_cases"].shift(lag)
    weekly[f"malaria_lag_{lag}"] = weekly.groupby("district")["malaria_cases"].shift(lag)
    weekly[f"temp_lag_{lag}"] = weekly.groupby("district")["temp_c"].shift(lag)
    weekly[f"rainfall_lag_{lag}"] = weekly.groupby("district")["rainfall"].shift(lag)
    weekly[f"humidity_lag_{lag}"] = weekly.groupby("district")["humidity"].shift(lag)

weekly = weekly.dropna()

print("✅ Lag features created")

# ======================================
# 1️⃣2️⃣ EPIDEMIC RISK INDEX
# ======================================

weekly["risk_index"] = (
    0.35 * weekly["humidity"] +
    0.30 * weekly["rainfall"] +
    0.20 * weekly["temp_c"] +
    0.15 * weekly["pop_density"]
)

# ======================================
# 1️⃣3️⃣ NORMALIZATION
# ======================================

scaler = MinMaxScaler()

features_to_scale = [
    "temp_c", "rainfall", "humidity", "lai",
    "pop_density", "urban_percent", "risk_index",
    "temp_lag_1", "temp_lag_2", "temp_lag_3",
    "rainfall_lag_1", "rainfall_lag_2", "rainfall_lag_3",
    "humidity_lag_1", "humidity_lag_2", "humidity_lag_3"
]

weekly[features_to_scale] = scaler.fit_transform(weekly[features_to_scale])

# ======================================
# 1️⃣4️⃣ SAVE FINAL DATASET
# ======================================

weekly.to_csv("3_feature_engineering/final_ml_dataset.csv", index=False)

print("✅ FINAL ML DATASET CREATED!")
print("Final shape:", weekly.shape)
print("=== PIPELINE COMPLETED SUCCESSFULLY ===")

import pandas as pd

df = pd.read_csv("3_feature_engineering/final_ml_dataset.csv")

print(df.head())
print(df.columns)
print(df.describe())
print("Shape:", df.shape)
