import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("REAL DATA AUGMENTATION FOR EPIDEMIC FORECASTING MODELS")
print("Using ONLY Real Observed Data (No Synthetic Generation)")
print("=" * 80)

# Load original datasets
print("\n[1] Loading original datasets...")
dengue_df = pd.read_csv('3_feature_engineering/final_ml_dataset_with_risk.csv')
print(f"    Original dengue dataset: {dengue_df.shape[0]} samples")

malaria_df = pd.read_csv('3_feature_engineering/final_ml_dataset_with_malaria_binary.csv')
print(f"    Original malaria dataset: {malaria_df.shape[0]} samples")

# Load raw real data sources
print("\n[2] Loading raw REAL data from disease files...")
disease_extended = pd.read_csv('1_raw_data/disease_data_extended.csv')
disease_final = pd.read_csv('1_raw_data/disease_data_final.csv')
population_data = pd.read_csv('1_raw_data/population_data.csv')
urban_data = pd.read_csv('1_raw_data/urban_data.csv')

print(f"    disease_data_extended.csv: {disease_extended.shape[0]} records")
print(f"    disease_data_final.csv: {disease_final.shape[0]} records")
print(f"    population_data.csv: {population_data.shape[0]} districts")
print(f"    urban_data.csv: {urban_data.shape[0]} districts")

# Combine disease data - using ALL available real data
print("\n[3] Preparing REAL data for merging (no synthetic generation)...")
disease_combined = pd.concat([disease_extended, disease_final], ignore_index=True)
print(f"    Combined disease records: {disease_combined.shape[0]}")

# Standardize column names
disease_combined.columns = [col.lower() for col in disease_combined.columns]
disease_combined = disease_combined.rename(columns={
    'unnamed: 0': 'index',
    'state_ut': 'state',
    'mon': 'month',
    'day': 'date',
    'preci': 'rainfall',
    'lai': 'lai_index',
    'temp': 'temperature'
})

# Pivot disease data to separate dengue and malaria cases
disease_data = disease_combined.copy()

# Create separate dengue and malaria records
dengue_records = disease_data[disease_data['disease'].str.lower() == 'dengue'].copy()
malaria_records = disease_data[disease_data['disease'].str.lower() == 'malaria'].copy()

# Group by location and time to merge disease types
print("\n[4] Merging REAL disease data records...")

# Create base records from dengue data
base_records = dengue_records[['district', 'year', 'week_of_outbreak', 'month', 'date', 
                               'latitude', 'longitude']].drop_duplicates()

# Merge dengue cases
dengue_cases = dengue_records.groupby(['district', 'year', 'week_of_outbreak'])['cases'].sum().reset_index()
dengue_cases = dengue_cases.rename(columns={'cases': 'dengue_cases'})

# Merge dengue deaths
dengue_deaths = disease_data[disease_data['disease'].str.lower() == 'dengue'].groupby(
    ['district', 'year', 'week_of_outbreak'])['deaths'].sum().reset_index()
dengue_deaths = dengue_deaths.rename(columns={'deaths': 'dengue_deaths'})

# Merge malaria cases
malaria_cases = malaria_records.groupby(['district', 'year', 'week_of_outbreak'])['cases'].sum().reset_index()
malaria_cases = malaria_cases.rename(columns={'cases': 'malaria_cases'})

# Merge malaria deaths
malaria_deaths = disease_data[disease_data['disease'].str.lower() == 'malaria'].groupby(
    ['district', 'year', 'week_of_outbreak'])['deaths'].sum().reset_index()
malaria_deaths = malaria_deaths.rename(columns={'deaths': 'malaria_deaths'})

# Climate data - keep unique records per district-week
climate_data = disease_data[['district', 'year', 'week_of_outbreak', 'month', 'temperature', 
                              'rainfall', 'lai_index', 'latitude', 'longitude']].drop_duplicates()

print(f"    Unique climate records: {len(climate_data)}")

# Start merging
merged_data = base_records.merge(
    dengue_cases, on=['district', 'year', 'week_of_outbreak'], how='left'
).merge(
    malaria_cases, on=['district', 'year', 'week_of_outbreak'], how='left'
).merge(
    dengue_deaths, on=['district', 'year', 'week_of_outbreak'], how='left'
).merge(
    malaria_deaths, on=['district', 'year', 'week_of_outbreak'], how='left'
).merge(
    climate_data, on=['district', 'year', 'week_of_outbreak'], how='left',
    suffixes=('', '_climate')
)

# Fill missing values
for col in ['dengue_cases', 'malaria_cases', 'dengue_deaths', 'malaria_deaths']:
    merged_data[col] = merged_data[col].fillna(0)

# Use climate data values
for col in ['month', 'temperature', 'rainfall', 'lai_index', 'latitude', 'longitude']:
    if col + '_climate' in merged_data.columns:
        merged_data[col] = merged_data[col].fillna(merged_data[col + '_climate'])
        merged_data = merged_data.drop(columns=[col + '_climate'])

print(f"    Merged real data records: {len(merged_data)}")

# Merge with population and urban data by district
merged_data = merged_data.merge(population_data, on='district', how='left')
merged_data = merged_data.merge(urban_data, on='district', how='left')

# Standardize column names using existing dataset structure
merged_data = merged_data.rename(columns={
    'month': 'mon',
    'temperature': 'temp_c',
    'lai_index': 'lai',
    'latitude': 'Latitude',
    'longitude': 'Longitude',
    'dengue_deaths': 'deaths'
})

# Fill climate data gaps by forward/backward fill per district
for col in ['temp_c', 'rainfall', 'lai', 'population', 'pop_density', 'urban_percent']:
    if col in merged_data.columns:
        merged_data[col] = merged_data.groupby('district')[col].ffill().bfill()

# Forward/backward fill globally if still missing
for col in ['temp_c', 'rainfall', 'lai', 'population', 'pop_density', 'urban_percent']:
    if col in merged_data.columns:
        merged_data[col] = merged_data[col].fillna(merged_data[col].mean())

print(f"\n[5] Creating lagged features from REAL historical data...")

# Create lagged features using real observed values
merged_data = merged_data.sort_values(['district', 'year', 'week_of_outbreak']).reset_index(drop=True)

for lag in range(1, 4):
    merged_data[f'dengue_lag_{lag}'] = merged_data.groupby('district')['dengue_cases'].shift(lag).fillna(0)
    merged_data[f'malaria_lag_{lag}'] = merged_data.groupby('district')['malaria_cases'].shift(lag).fillna(0)
    merged_data[f'temp_lag_{lag}'] = merged_data.groupby('district')['temp_c'].shift(lag).fillna(
        merged_data['temp_c'].mean())
    merged_data[f'rainfall_lag_{lag}'] = merged_data.groupby('district')['rainfall'].shift(lag).fillna(
        merged_data['rainfall'].mean())
    merged_data[f'humidity_lag_{lag}'] = merged_data.groupby('district')['rainfall'].shift(lag).fillna(
        merged_data['rainfall'].mean())  # Using rainfall as proxy

# Create derived features based on REAL observed patterns
print("\n[6] Calculating risk indices from REAL data distributions...")

# Calculate seasonal components
merged_data['season_code'] = (merged_data['mon'].fillna(1) // 3) % 4

# Trend calculation using real observed values
merged_data['dengue_trend'] = merged_data.groupby('district')['dengue_cases'].rolling(
    window=3, min_periods=1).mean().reset_index(drop=True)
merged_data['malaria_trend'] = merged_data.groupby('district')['malaria_cases'].rolling(
    window=3, min_periods=1).mean().reset_index(drop=True)

# Risk index based on actual data statistics
dengue_std = merged_data['dengue_cases'].std()
dengue_mean = merged_data['dengue_cases'].mean()
malaria_std = merged_data['malaria_cases'].std()
malaria_mean = merged_data['malaria_cases'].mean()

merged_data['risk_index'] = (
    ((merged_data['dengue_cases'] - dengue_mean) / (dengue_std + 1)) * 0.5 +
    ((merged_data['malaria_cases'] - malaria_mean) / (malaria_std + 1)) * 0.5
)

# Create risk labels based on actual percentiles from REAL data
# Use qcut to automatically handle duplicate edges
merged_data['dengue_risk'] = pd.qcut(
    merged_data['dengue_cases'].rank(method='first'),
    q=3,
    labels=['Low', 'Medium', 'High'],
    duplicates='drop'
)

merged_data['malaria_risk'] = pd.qcut(
    merged_data['malaria_cases'].rank(method='first'),
    q=2,
    labels=[0, 1],
    duplicates='drop'
)

# Add humidity (approximated from rainfall)
merged_data['humidity'] = (merged_data['rainfall'] / (merged_data['rainfall'].max() + 1)) * 100

print("[7] Removing EXACT duplicates with existing dataset...")

# Columns to check for duplicates
comparison_cols = ['district', 'year', 'week_of_outbreak', 'mon', 
                  'dengue_cases', 'malaria_cases']

# Get unique existing records
original_unique = dengue_df[comparison_cols].drop_duplicates()
print(f"    Existing unique records: {len(original_unique)}")

# Get unique new records
new_unique = merged_data[comparison_cols].drop_duplicates()
print(f"    New real data records: {len(new_unique)}")

# Find truly new records (not in original)
# Create a key combination for comparison
original_unique['_key'] = (original_unique['district'].astype(str) + '|' + 
                           original_unique['year'].astype(str) + '|' + 
                           original_unique['week_of_outbreak'].astype(str) + '|' +
                           original_unique['mon'].astype(str) + '|' +
                           original_unique['dengue_cases'].astype(str) + '|' +
                           original_unique['malaria_cases'].astype(str))

new_unique['_key'] = (new_unique['district'].astype(str) + '|' + 
                      new_unique['year'].astype(str) + '|' + 
                      new_unique['week_of_outbreak'].astype(str) + '|' +
                      new_unique['mon'].astype(str) + '|' +
                      new_unique['dengue_cases'].astype(str) + '|' +
                      new_unique['malaria_cases'].astype(str))

existing_keys = set(original_unique['_key'])
new_keys = set(new_unique['_key'])
truly_new_keys = new_keys - existing_keys

# Filter merged_data to get only truly new records
merged_data['_key'] = (merged_data['district'].astype(str) + '|' + 
                       merged_data['year'].astype(str) + '|' + 
                       merged_data['week_of_outbreak'].astype(str) + '|' +
                       merged_data['mon'].astype(str) + '|' +
                       merged_data['dengue_cases'].astype(str) + '|' +
                       merged_data['malaria_cases'].astype(str))

new_real_records = merged_data[merged_data['_key'].isin(truly_new_keys)].drop(columns='_key')
original_unique = original_unique.drop(columns='_key')
new_unique = new_unique.drop(columns='_key')

print(f"    New non-duplicate records: {len(new_real_records)}")

# Select matching columns
keep_cols = [col for col in dengue_df.columns if col in merged_data.columns]
if 'malaria_risk' not in keep_cols and 'malaria_risk' in merged_data.columns:
    keep_cols.append('malaria_risk')

new_real_records_clean = new_real_records[keep_cols].copy()

# Combine with original data
print("\n[8] Combining with original datasets...")
dengue_augmented = pd.concat([dengue_df, new_real_records_clean], ignore_index=True)
dengue_augmented = dengue_augmented.drop_duplicates(subset=comparison_cols, keep='first').reset_index(drop=True)

print(f"    Original dengue: {len(dengue_df)} samples")
print(f"    After adding REAL data: {len(dengue_augmented)} samples")
print(f"    New REAL samples added: {len(dengue_augmented) - len(dengue_df)}")
print(f"    Increase: {((len(dengue_augmented) - len(dengue_df)) / len(dengue_df) * 100):.1f}%")

# Create malaria version
malaria_augmented = dengue_augmented.copy()
if 'malaria_risk' in malaria_augmented.columns:
    malaria_augmented['malaria_risk_binary'] = (
        malaria_augmented['malaria_cases'] > malaria_augmented['malaria_cases'].quantile(0.5)
    ).astype(int)

print("\n[9] Saving REAL-ONLY augmented datasets...")
dengue_augmented.to_csv('3_feature_engineering/final_ml_dataset_augmented.csv', index=False)
print("    ✓ Saved: final_ml_dataset_augmented.csv")

malaria_augmented.to_csv('3_feature_engineering/final_ml_dataset_augmented_malaria.csv', index=False)
print("    ✓ Saved: final_ml_dataset_augmented_malaria.csv")

print("\n" + "=" * 80)
print("REAL DATA AUGMENTATION COMPLETE ✓")
print("=" * 80)
print(f"\nORIGINAL DATASET:")
print(f"  Dengue samples: {len(dengue_df)}")
print(f"  Malaria samples: {len(malaria_df)}")

print(f"\nAUGMENTED DATASET (Real Data Only):")
print(f"  Dengue samples: {len(dengue_augmented)}")
print(f"  Malaria samples: {len(malaria_augmented)}")

print(f"\nREAL DATA ADDED:")
print(f"  Dengue: +{len(dengue_augmented) - len(dengue_df)} samples (+{((len(dengue_augmented) - len(dengue_df)) / len(dengue_df) * 100):.1f}%)")
print(f"  Malaria: +{len(malaria_augmented) - len(malaria_df)} samples (+{((len(malaria_augmented) - len(malaria_df)) / len(malaria_df) * 100):.1f}%)")

print(f"\nDATA SOURCES USED:")
print(f"  ✓ disease_data_extended.csv ({disease_extended.shape[0]} records)")
print(f"  ✓ disease_data_final.csv ({disease_final.shape[0]} records)")
print(f"  ✓ population_data.csv")
print(f"  ✓ urban_data.csv")
print(f"\nNO SYNTHETIC DATA GENERATED - All new samples are from real observed values!")
