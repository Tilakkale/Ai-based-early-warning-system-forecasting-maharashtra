"""
Retrain Dengue Risk Model with Augmented Real Data
Augmented dataset: 1763 samples (from 337 original)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
import pickle
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("RETRAINING DENGUE RISK MODEL WITH AUGMENTED REAL DATA")
print("=" * 80)

# Load augmented dataset
print("\n[1] Loading augmented real data...")
df = pd.read_csv('3_feature_engineering/final_ml_dataset_augmented.csv')
print(f"    Dataset size: {df.shape[0]} samples (was 337, now +{df.shape[0]-337})")
print(f"    Raw dengue risk distribution:\n{df['dengue_risk'].value_counts().sort_index()}")

# --- clean up risk labels --------------------------------------------------
# the augmented file may mix numeric (0/1/2) with strings ('Low','Medium','High').
# normalize everything to integers 0=Low,1=Medium,2=High before encoding.
mapping = {'Low': 0, 'Medium': 1, 'High': 2}

def normalize_label(x):
    try:
        # numeric strings or numbers
        return int(float(x))
    except Exception:
        return mapping.get(str(x).strip(), np.nan)

# apply mapping and drop any rows we still can't interpret
cleaned = df['dengue_risk'].apply(normalize_label)
if cleaned.isna().any():
    print("    Warning: some labels could not be normalized and will be dropped:",
          df.loc[cleaned.isna(), 'dengue_risk'].unique())
    df = df.loc[~cleaned.isna()].copy()
    cleaned = cleaned.loc[~cleaned.isna()]

df['dengue_risk'] = cleaned.astype(int)
print(f"    Normalized dengue risk distribution:\n{df['dengue_risk'].value_counts().sort_index()}")

# Prepare features
print("\n[2] Preparing features...")
feature_cols = ['temp_c', 'rainfall', 'humidity', 'lai', 'population', 'pop_density', 'urban_percent',
                'dengue_lag_1', 'dengue_lag_2', 'dengue_lag_3',
                'malaria_lag_1', 'malaria_lag_2', 'malaria_lag_3',
                'risk_index', 'dengue_trend', 'malaria_trend']

# Handle missing values
for col in feature_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

X = df[feature_cols].fillna(0)
y = df['dengue_risk']

# Encode target labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

print(f"    Features: {len(feature_cols)}")
print(f"    Samples: {len(X)}")
print(f"    Target classes: {len(le.classes_)} {list(le.classes_)}")

# Split data
print("\n[3] Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)
print(f"    Training: {len(X_train)} samples")
print(f"    Testing: {len(X_test)} samples")

# Train optimized model
print("\n[4] Training RandomForest model...")
model = RandomForestClassifier(
    n_estimators=800,           # Increased from 600
    max_depth=16,               # Balanced depth
    min_samples_split=5,
    min_samples_leaf=2,
    max_features='sqrt',
    class_weight='balanced',
    random_state=42,
    n_jobs=-1,
    oob_score=True,
    verbose=1
)

model.fit(X_train, y_train)
print("✓ Model training complete")

# Evaluate on test set
print("\n[5] Evaluating on test set...")
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted')
precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
try:
    roc_auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted')
except:
    roc_auc = 0

print(f"\n    TEST SET METRICS:")
print(f"    Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"    F1 Score:  {f1:.4f}")
print(f"    Precision: {precision:.4f}")
print(f"    Recall:    {recall:.4f}")
print(f"    ROC AUC:   {roc_auc:.4f}")

# Cross-validation
print("\n[6] Cross-validation (5-fold stratified)...")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy')
print(f"    CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print(f"    Fold scores: {[f'{s:.4f}' for s in cv_scores]}")

# Feature importance
print("\n[7] Feature importance (top 10):")
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.head(10).iterrows():
    print(f"    {row['feature']:25s} {row['importance']:.4f}")

# Save model
print("\n[8] Saving trained model...")
model_path = '4_models/saved_models/best_dengue_risk_model.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print(f"    ✓ Saved: {model_path}")

# Save encoder
encoder_path = '4_models/saved_models/dengue_risk_encoder.pkl'
with open(encoder_path, 'wb') as f:
    pickle.dump(le, f)
print(f"    ✓ Saved: {encoder_path}")

print("\n" + "=" * 80)
print("DENGUE RISK MODEL RETRAINING COMPLETE ✓")
print("=" * 80)
print(f"\nRESULTS SUMMARY:")
print(f"  Original dataset: 337 samples")
print(f"  Augmented dataset: {len(df)} samples (+{len(df)-337} real data)")
print(f"  Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"  CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print(f"  F1 Score: {f1:.4f}")
print(f"\n✓ Model saved and ready for deployment!")
