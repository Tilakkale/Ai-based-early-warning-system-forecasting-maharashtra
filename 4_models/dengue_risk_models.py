import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, f1_score

print("Training Dengue Risk Models (RF + GB + ExtraTrees with Enhanced Tuning)")

# ===============================
# LOAD DATA
# ===============================
from pathlib import Path

# build absolute path to dataset relative to this script's parent directory
base_dir = Path(__file__).parent.parent
data_file = base_dir / "3_feature_engineering" / "final_ml_dataset_with_risk.csv"

df = pd.read_csv(data_file)


# ===============================
# STRONG FEATURES ONLY
# ===============================
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

X = df[FEATURES]
y = df["dengue_risk"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# ===============================
# MODELS
# ===============================
models = {
    "RandomForest": RandomForestClassifier(
        n_estimators=600,
        max_depth=14,
        min_samples_leaf=2,
        min_samples_split=3,
        max_features="sqrt",
        bootstrap=True,
        oob_score=True,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    ),
    "GradientBoosting": GradientBoostingClassifier(
        n_estimators=400,
        learning_rate=0.03,
        max_depth=5,
        min_samples_split=3,
        min_samples_leaf=2,
        subsample=0.92,
        max_features="sqrt",
        random_state=42
    ),
    "ExtraTrees": ExtraTreesClassifier(
        n_estimators=600,
        max_depth=14,
        min_samples_leaf=2,
        min_samples_split=3,
        max_features="sqrt",
        bootstrap=True,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
}

# ===============================
# TRAIN + EVALUATE
# ===============================
best_model = None
best_f1 = 0

for name, model in models.items():
    print(f"\n{name} RESULTS")

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # Cross-validation score
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1_weighted')

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    print("Accuracy:", round(acc, 3))
    print("Weighted F1:", round(f1, 3))
    print(f"Cross-validation F1: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    print(classification_report(y_test, y_pred))

    if f1 > best_f1:
        best_f1 = f1
        best_model = model
        best_name = name

# ===============================
# SAVE BEST MODEL
# ===============================
# ensure model directory path is relative to script location
model_dir = Path(__file__).parent / "saved_models"
model_dir.mkdir(exist_ok=True)
joblib.dump(best_model, model_dir / "best_dengue_risk_model.pkl")

print(f"\n✅ Best Dengue Risk Model: {best_name}")
print("Saved as best_dengue_risk_model.pkl")
