import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
from pathlib import Path

print("🦟 Evaluating FINAL Dengue Risk Model...")

# Create folders if not exist
Path("5_evaluation/plots").mkdir(parents=True, exist_ok=True)
Path("5_evaluation/metrics").mkdir(parents=True, exist_ok=True)

# =============================
# LOAD DATA & MODEL
# =============================
df = pd.read_csv("3_feature_engineering/final_ml_dataset_with_risk.csv")

model = joblib.load(
    "4_models/saved_models/best_dengue_risk_model.pkl"
)

# use feature names saved in the trained model if available
if hasattr(model, "feature_names_in_"):
    FEATURES = list(model.feature_names_in_)
    print("Using trained features:", FEATURES)
else:
    FEATURES = [
        "temp_c",
        "rainfall",
        "humidity",
        "risk_index",
        "dengue_lag_1",
        "dengue_lag_2",
        "dengue_lag_3",
        "pop_density"
    ]
    print("Model has no feature_names_in_; using default list")

X = df[FEATURES]
if "dengue_risk" not in df.columns:
    raise ValueError("dengue_risk column not found in dataset")
y = df["dengue_risk"]

# =============================
# PREDICTION
# =============================
y_pred = model.predict(X)

# =============================
# REPORT
# =============================
report_text = classification_report(y, y_pred)
print("\n📊 CLASSIFICATION REPORT")
print(report_text)

# Save TXT
with open(
    "5_evaluation/metrics/dengue_report.txt",
    "w"
) as f:
    f.write(report_text)

# Save CSV
report_dict = classification_report(
    y, y_pred, output_dict=True
)
pd.DataFrame(report_dict).transpose().to_csv(
    "5_evaluation/metrics/dengue_report.csv"
)

# Append summary row to metrics.csv for dashboard use
from sklearn.metrics import accuracy_score

summary = {
    "dataset": "augmented",
    "model": "dengue_risk",
    "accuracy": accuracy_score(y, y_pred),
    "f1_score": report_dict.get("accuracy", 0)
}
metrics_path = Path("5_evaluation/metrics.csv")
if metrics_path.exists():
    try:
        dfm = pd.read_csv(metrics_path, index_col=0)
    except pd.errors.EmptyDataError:
        dfm = pd.DataFrame()
else:
    dfm = pd.DataFrame()
row = pd.DataFrame([summary], index=[summary["model"]])
dfm = dfm.drop(labels=[summary["model"]], errors="ignore")
dfm = pd.concat([dfm, row])
dfm.to_csv(metrics_path)

# =============================
# CONFUSION MATRIX
# =============================
cm = confusion_matrix(y, y_pred)

plt.figure(figsize=(6, 5))
plt.imshow(cm, cmap="Blues")
plt.title("Dengue Risk Confusion Matrix")
plt.colorbar()
plt.xlabel("Predicted")
plt.ylabel("Actual")

classes = ["Low", "Medium", "High"]
plt.xticks(range(3), classes)
plt.yticks(range(3), classes)

for i in range(3):
    for j in range(3):
        plt.text(j, i, cm[i, j], ha="center", va="center")

plt.tight_layout()
plt.savefig("5_evaluation/plots/dengue_confusion.png")
plt.close()

print("✅ Dengue evaluation completed.")
