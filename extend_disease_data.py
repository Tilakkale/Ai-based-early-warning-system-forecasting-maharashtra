import pandas as pd

print("=== STEP 3: EXTEND DISEASE DATA ===")

# Load cleaned disease data and population data
disease = pd.read_csv("1_raw_data/disease_cleaned.csv")
pop = pd.read_csv("1_raw_data/population_data.csv")

# Clean population district names
pop["district"] = pop["district"].str.strip().str.title()

# Find missing districts
disease_districts = set(disease["district"].unique())
all_districts = set(pop["district"].unique())

missing = all_districts - disease_districts
print("Missing districts:", missing)

rows = []

# Use one sample row structure
sample_row = disease.iloc[0]

for district in missing:
    new_row = sample_row.copy()
    new_row["district"] = district
    new_row["Cases"] = 0
    new_row["Deaths"] = 0
    rows.append(new_row)

# Add missing districts
if rows:
    disease = pd.concat([disease, pd.DataFrame(rows)], ignore_index=True)

# Save FINAL dataset
disease.to_csv("1_raw_data/disease_data_final.csv", index=False)

print("✅ disease_data_final.csv created!")
print("Final district count:", disease["district"].nunique())
