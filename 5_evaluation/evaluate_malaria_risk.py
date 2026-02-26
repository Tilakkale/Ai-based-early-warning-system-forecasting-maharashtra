import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
from pathlib import Path

print("Evaluating FINAL Malaria Risk Model...")

# =============================
# LOAD DATA
# =============================
df = pd.read_csv("3_feature_engineering/final_ml_dataset_with_risk.csv")

# =============================
# LOAD MODEL
# =============================
model = joblib.load(
    "4_models/saved_models/best_malaria_binary_risk_model.pkl"
)

# =============================
# USE TRAINED FEATURE ORDER
# =============================
FEATURES = model.feature_names_in_
print("Using trained features:", FEATURES)

X = df[FEATURES]

# Target selection
if "malaria_risk_binary" in df.columns:
    y = df["malaria_risk_binary"]
else:
    print("malaria_risk_binary not found, using malaria_risk")
    y = df["malaria_risk"]


# =============================
# PREDICTION
# =============================
y_pred = model.predict(X)

# =============================
# CLASSIFICATION REPORT
# =============================
report_text = classification_report(y, y_pred)

print("\nCLASSIFICATION REPORT")
print(report_text)

# Save TXT
with open(
    "5_evaluation/metrics/malaria_report.txt",
    "w"
) as f:
    f.write(report_text)

# Save CSV metrics
report_dict = classification_report(
    y, y_pred, output_dict=True
)
pd.DataFrame(report_dict).transpose().to_csv(
    "5_evaluation/metrics/malaria_report.csv"
)

# Append summary row to metrics.csv for dashboard use
from sklearn.metrics import accuracy_score

summary = {
    "dataset": "augmented",
    "model": "malaria_binary",
    "accuracy": accuracy_score(y, y_pred),
    "f1_score": report_dict.get("1", {}).get("f1-score", 0)
}
metrics_path = Path("5_evaluation/metrics.csv")
if metrics_path.exists():
    dfm = pd.read_csv(metrics_path, index_col=0)
else:
    dfm = pd.DataFrame()
# use model name as index
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
plt.title("Malaria Risk Confusion Matrix")
plt.colorbar()
plt.xlabel("Predicted")
plt.ylabel("Actual")

classes = ["Low", "Risk"]
plt.xticks(range(len(classes)), classes)
plt.yticks(range(len(classes)), classes)

for i in range(len(classes)):
    for j in range(len(classes)):
        plt.text(j, i, cm[i, j], ha="center", va="center")

plt.tight_layout()
plt.savefig("5_evaluation/plots/malaria_confusion.png")
plt.close()

print("Malaria evaluation completed.")
