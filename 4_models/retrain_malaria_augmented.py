"""
Retrain Malaria Binary Risk Model with Augmented Real Data
Augmented dataset: 1763 samples (from 337 original)
Target: Reach 90-95% accuracy
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, confusion_matrix
import pickle
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("RETRAINING MALARIA BINARY RISK MODEL WITH AUGMENTED REAL DATA")
print("=" * 80)

# Load augmented dataset
print("\n[1] Loading augmented real data...")
df = pd.read_csv('3_feature_engineering/final_ml_dataset_augmented_malaria.csv')
print(f"    Dataset size: {df.shape[0]} samples (was 337, now +{df.shape[0]-337})")

# Create binary target if not present
if 'malaria_risk_binary' not in df.columns:
    df['malaria_risk_binary'] = (df['malaria_cases'] > df['malaria_cases'].quantile(0.5)).astype(int)

print(f"    Malaria risk distribution:\n{df['malaria_risk_binary'].value_counts().sort_index()}")

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
y = df['malaria_risk_binary'].astype(int)

print(f"    Features: {len(feature_cols)}")
print(f"    Samples: {len(X)}")
print(f"    Class distribution: {y.value_counts().to_dict()}")

# Split data
print("\n[3] Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"    Training: {len(X_train)} samples")
print(f"    Testing: {len(X_test)} samples")
print(f"    Train class distribution: {y_train.value_counts().to_dict()}")
print(f"    Test class distribution: {y_test.value_counts().to_dict()}")

# Train optimized binary classification model
print("\n[4] Training RandomForest binary classification model...")
model = RandomForestClassifier(
    n_estimators=1000,          # High number of trees for binary task
    max_depth=18,               # Allow deeper trees
    min_samples_split=3,        # Stricter split criteria
    min_samples_leaf=1,
    max_features='sqrt',
    class_weight='balanced_subsample',  # Better for imbalanced data
    random_state=42,
    n_jobs=-1,
    oob_score=True,
    verbose=1
)

model.fit(X_train, y_train)
print("Model training complete")
print(f"  OOB Score: {model.oob_score_:.4f}")

# Evaluate on test set
print("\n[5] Evaluating on test set...")
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
roc_auc = roc_auc_score(y_test, y_pred_proba[:, 1])

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)

print(f"\n    TEST SET METRICS:")
print(f"    Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"    F1 Score:  {f1:.4f}")
print(f"    Precision: {precision:.4f}")
print(f"    Recall:    {recall:.4f}")
print(f"    ROC AUC:   {roc_auc:.4f}")
print(f"\n    Confusion Matrix:")
print(f"    TN: {cm[0, 0]:4d}  FP: {cm[0, 1]:4d}")
print(f"    FN: {cm[1, 0]:4d}  TP: {cm[1, 1]:4d}")

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
model_path = '4_models/saved_models/best_malaria_binary_risk_model.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print(f"    [OK] Saved: {model_path}")

print("\n" + "=" * 80)
print("MALARIA BINARY RISK MODEL RETRAINING COMPLETE [OK]")
print("=" * 80)
print(f"\nRESULTS SUMMARY:")
print(f"  Original dataset: 337 samples")
print(f"  Augmented dataset: {len(df)} samples (+{len(df)-337} real data)")
print(f"  Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"  CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print(f"  Test F1 Score: {f1:.4f}")
print(f"  Test ROC AUC: {roc_auc:.4f}")

if accuracy >= 0.90:
    print(f"\n[SUCCESS] TARGET ACHIEVED! Accuracy {accuracy*100:.2f}% >= 90% [SUCCESS]")
    
print(f"\n[OK] Model saved and ready for deployment!")
