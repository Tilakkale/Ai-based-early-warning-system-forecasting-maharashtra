import pandas as pd
import numpy as np

print("=== Creating MALARIA BINARY RISK LABELS (DISTRICT-AWARE) ===")

df = pd.read_csv("3_feature_engineering/final_ml_dataset.csv")

df = df.sort_values(["district", "year", "week_of_outbreak"])

# --- district-wise thresholds ---
def label_group(g):
    case_thr = g["malaria_cases"].quantile(0.80)
    lag_thr  = g["malaria_lag_1"].quantile(0.80)
    risk_thr = g["risk_index"].quantile(0.75)

    def label(row):
        # STRICT AND (not OR)
        if (
            row["malaria_cases"] >= case_thr and
            row["malaria_lag_1"] >= lag_thr and
            row["risk_index"] >= risk_thr
        ):
            return 1   # AT RISK
        return 0       # LOW RISK

    g["malaria_risk_binary"] = g.apply(label, axis=1)
    return g

df = df.groupby("district", group_keys=False).apply(label_group)

# ---- HARD CHECK ----
print("\nClass distribution:")

print(df["malaria_risk_binary"].value_counts())

assert df["malaria_risk_binary"].nunique() == 2, \
    "❌ Still only one class — check data!"

df.to_csv(
    "3_feature_engineering/final_ml_dataset_with_malaria_binary.csv",
    index=False
)

print("✅ Malaria binary risk labels created CORRECTLY!")
