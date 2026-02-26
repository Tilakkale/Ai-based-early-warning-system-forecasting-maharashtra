import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression

print("🦠 Training FINAL Malaria Binary Risk Models...")

# Load dataset
df = pd.read_csv("3_feature_engineering/final_ml_dataset_with_malaria_binary.csv")

# FEATURES (keep clean & meaningful)
FEATURES = [
    "temp_c", "rainfall", "humidity",
    "malaria_lag_1", "malaria_lag_2", "malaria_lag_3",
    "risk_index", "pop_density"
]

X = df[FEATURES]
y = df["malaria_risk_binary"]  # MUST EXIST

# Train-test split (stratified!)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

models = {
    "RandomForest": RandomForestClassifier(
        n_estimators=800,
        max_depth=15,
        min_samples_leaf=2,
        min_samples_split=4,
        class_weight="balanced",
        random_state=42,
        oob_score=True
    ),
    "ExtraTrees": ExtraTreesClassifier(
        n_estimators=800,
        max_depth=15,
        min_samples_leaf=2,
        min_samples_split=4,
        class_weight="balanced",
        random_state=42
    ),
    "LogisticRegression": LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        C=0.1
    )
}

best_model = None
best_f1 = 0

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    print(f"\n{name} RESULTS")
    print("Accuracy:", round(acc, 3))
    print("Weighted F1:", round(f1, 3))
    print(classification_report(y_test, y_pred))

    if f1 > best_f1:
        best_f1 = f1
        best_model = model

# Save best model
joblib.dump(best_model, "4_models/saved_models/best_malaria_binary_risk_model.pkl")
print("\n✅ Best Malaria Binary Risk Model Saved!")
