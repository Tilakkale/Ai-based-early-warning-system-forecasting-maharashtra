import pandas as pd

print("=== STEP 2: CHECK MISSING DISTRICTS ===")

disease = pd.read_csv("1_raw_data/disease_cleaned.csv")
pop = pd.read_csv("1_raw_data/population_data.csv")

# Clean population district names
pop["district"] = pop["district"].str.strip().str.title()

disease_districts = set(disease["district"].unique())
all_districts = set(pop["district"].unique())

missing = all_districts - disease_districts

print("Missing districts:", missing)
print("Disease districts count:", len(disease_districts))
print("Population districts count:", len(all_districts))
