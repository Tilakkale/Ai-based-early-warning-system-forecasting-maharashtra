import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import random

print("=" * 80)
print("🔄 AUGMENTING DATASET FOR IMPROVED MODEL ACCURACY")
print("=" * 80)

# Load original dataset
df = pd.read_csv("3_feature_engineering/final_ml_dataset_with_risk.csv")
original_size = len(df)
print(f"\n✅ Original dataset size: {original_size} samples")
print(f"✅ Original dengue_risk distribution:\n{df['dengue_risk'].value_counts().sort_index()}")
print(f"✅ Original malaria_risk distribution:\n{df['malaria_risk'].value_counts().sort_index()}")

# Features for augmentation (exclude IDs and target variables)
numeric_cols = [
    'temp_c', 'rainfall', 'humidity', 'lai', 'pop_density', 'urban_percent',
    'risk_index', 'dengue_lag_1', 'dengue_lag_2', 'dengue_lag_3',
    'malaria_lag_1', 'malaria_lag_2', 'malaria_lag_3'
]

categorical_cols = ['district', 'year', 'week_of_outbreak', 'mon', 'season_code', 'Latitude', 'Longitude']

# ================================
# SYNTHETIC DATA GENERATION
# ================================

def augment_with_variations(df_in, augmentation_factor=3):
    """Create synthetic samples by adding small variations to existing samples."""
    
    augmented_samples = []
    
    # Group by target classes to create balanced augmentation
    for dengue_risk_val in df_in['dengue_risk'].unique():
        for malaria_risk_val in df_in['malaria_risk'].unique():
            subset = df_in[
                (df_in['dengue_risk'] == dengue_risk_val) & 
                (df_in['malaria_risk'] == malaria_risk_val)
            ]
            
            if len(subset) == 0:
                continue
                
            # For each sample in this class combination, create variations
            for idx, row in subset.iterrows():
                for _ in range(augmentation_factor):
                    new_row = row.copy()
                    
                    # Add small gaussian noise to numeric features
                    for col in numeric_cols:
                        if col in new_row:
                            # Add noise: 5-8% of column value or std dev
                            noise_std = abs(new_row[col]) * 0.05 + 0.01
                            noise = np.random.normal(0, noise_std)
                            new_row[col] = max(0, new_row[col] + noise)
                    
                    # Randomly modify week/month slightly
                    if 'week_of_outbreak' in new_row:
                        weeks = int(new_row['week_of_outbreak'].replace('st', '').replace('nd', '').replace('rd', '').replace('th', '').split()[0])
                        weeks = max(1, min(52, weeks + random.randint(-1, 1)))
                        week_str = ['st', 'nd', 'rd', 'th'][(weeks-1) % 4] if weeks <= 4 else 'th'
                        new_row['week_of_outbreak'] = f"{weeks}{week_str} week"
                    
                    augmented_samples.append(new_row)
    
    return pd.DataFrame(augmented_samples)

# ================================
# CREATE AUGMENTED DATASET
# ================================

print("\n📊 Creating augmented dataset with variations...")
augmented_data = augment_with_variations(df, augmentation_factor=3)

# Combine original + augmented
combined_df = pd.concat([df, augmented_data], ignore_index=True)

# Remove duplicates (very similar rows)
combined_df = combined_df.drop_duplicates(subset=numeric_cols, keep='first')

print(f"\n✅ Augmented dataset size: {len(combined_df)} samples")
print(f"   (Original: {original_size} + Augmented: {len(combined_df) - original_size})")

# ================================
# ADD SYNTHETIC HIGH-RISK SAMPLES
# ================================

print("\n📈 Adding synthetic high-risk samples for better class balance...")

high_risk_dengue = df[df['dengue_risk'] == 2]
high_risk_malaria = df[df['malaria_risk'] == 2]

synthetic_samples = []

# Generate synthetic high-risk dengue samples
if len(high_risk_dengue) > 0:
    for _ in range(min(30, len(high_risk_dengue) * 2)):
        template = high_risk_dengue.sample(1).iloc[0]
        new_sample = template.copy()
        
        # Increase disease-promoting factors
        new_sample['temp_c'] = min(1.0, template['temp_c'] + abs(np.random.normal(0.05, 0.03)))
        new_sample['rainfall'] = template['rainfall'] + abs(np.random.normal(0.1, 0.05))
        new_sample['humidity'] = min(1.0, template['humidity'] + abs(np.random.normal(0.08, 0.04)))
        new_sample['dengue_lag_1'] = template['dengue_lag_1'] + abs(np.random.normal(5, 2))
        new_sample['risk_index'] = min(3.0, template['risk_index'] + abs(np.random.normal(0.3, 0.15)))
        new_sample['dengue_cases'] = int(template['dengue_cases'] + abs(np.random.normal(20, 10)))
        new_sample['dengue_risk'] = 2  # High risk
        
        synthetic_samples.append(new_sample)

# Generate synthetic high-risk malaria samples
if len(high_risk_malaria) > 0:
    for _ in range(min(30, len(high_risk_malaria) * 2)):
        template = high_risk_malaria.sample(1).iloc[0]
        new_sample = template.copy()
        
        # Increase malaria-promoting factors
        new_sample['temp_c'] = min(1.0, template['temp_c'] + abs(np.random.normal(0.03, 0.02)))
        new_sample['rainfall'] = template['rainfall'] + abs(np.random.normal(0.15, 0.08))
        new_sample['humidity'] = min(1.0, template['humidity'] + abs(np.random.normal(0.1, 0.05)))
        new_sample['malaria_lag_1'] = template['malaria_lag_1'] + abs(np.random.normal(4, 2))
        new_sample['malaria_cases'] = int(template['malaria_cases'] + abs(np.random.normal(15, 8)))
        new_sample['malaria_risk'] = 2  # High risk
        
        synthetic_samples.append(new_sample)

if synthetic_samples:
    synthetic_df = pd.DataFrame(synthetic_samples)
    combined_df = pd.concat([combined_df, synthetic_df], ignore_index=True)
    print(f"✅ Added {len(synthetic_df)} synthetic high-risk samples")

# ================================
# SAVE AUGMENTED DATASET
# ================================

final_df = combined_df.reset_index(drop=True)
final_df.to_csv("3_feature_engineering/final_ml_dataset_augmented.csv", index=False)

print(f"\n✅ FINAL AUGMENTED DATASET:")
print(f"   Total samples: {len(final_df)}")
print(f"   Growth: {len(final_df) - original_size} new samples (+{((len(final_df) - original_size) / original_size * 100):.1f}%)")
print(f"\n✅ DENGUE RISK DISTRIBUTION:")
print(final_df['dengue_risk'].value_counts().sort_index())
print(f"\n✅ MALARIA RISK DISTRIBUTION:")
print(final_df['malaria_risk'].value_counts().sort_index())

# Also create augmented version of malaria binary
print("\n" + "=" * 80)
print("Creating MALARIA BINARY datasets...")
print("=" * 80)

# Load malaria binary dataset
malaria_binary_df = pd.read_csv("3_feature_engineering/final_ml_dataset_with_malaria_binary.csv")
original_malaria_size = len(malaria_binary_df)

malaria_augmented = augment_with_variations(malaria_binary_df, augmentation_factor=4)
malaria_combined = pd.concat([malaria_binary_df, malaria_augmented], ignore_index=True)
malaria_combined = malaria_combined.drop_duplicates(subset=numeric_cols, keep='first')

# Add synthetic high-risk malaria samples
high_risk_ops = malaria_combined[malaria_combined['malaria_risk_binary'] == 1]
if len(high_risk_ops) > 0:
    for _ in range(25):
        template = high_risk_ops.sample(1).iloc[0]
        new_sample = template.copy()
        new_sample['temp_c'] = min(1.0, template['temp_c'] + abs(np.random.normal(0.04, 0.02)))
        new_sample['rainfall'] = template['rainfall'] + abs(np.random.normal(0.12, 0.06))
        new_sample['humidity'] = min(1.0, template['humidity'] + abs(np.random.normal(0.08, 0.04)))
        new_sample['malaria_cases'] = int(template['malaria_cases'] + abs(np.random.normal(10, 5)))
        new_sample['malaria_risk_binary'] = 1
        malaria_combined = pd.concat([malaria_combined, pd.DataFrame([new_sample])], ignore_index=True)

malaria_combined = malaria_combined.reset_index(drop=True)
malaria_combined.to_csv("3_feature_engineering/final_ml_dataset_augmented_malaria.csv", index=False)

print(f"✅ Original malaria binary dataset: {original_malaria_size}")
print(f"✅ Final augmented malaria dataset: {len(malaria_combined)}")
print(f"✅ Growth: {len(malaria_combined) - original_malaria_size} new samples")
print(f"\n✅ MALARIA BINARY DISTRIBUTION:")
print(malaria_combined['malaria_risk_binary'].value_counts().sort_index())

print("\n" + "=" * 80)
print("✅ DATA AUGMENTATION COMPLETE!")
print("=" * 80)
print("Files created:")
print("  📄 3_feature_engineering/final_ml_dataset_augmented.csv")
print("  📄 3_feature_engineering/final_ml_dataset_augmented_malaria.csv")
print("\nReady for model retraining with expanded dataset!")
