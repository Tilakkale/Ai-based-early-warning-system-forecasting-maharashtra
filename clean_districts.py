import pandas as pd

print("=== STEP 1: CLEAN DISTRICT NAMES ===")

# Load original disease data
disease = pd.read_csv("1_raw_data/disease_data_original.csv")

# Basic cleaning
disease["district"] = disease["district"].str.strip()
disease["district"] = disease["district"].str.title()

# Fix known duplicate names
district_map = {
    "Sholapur": "Solapur",
    "Osmanabad (Maharashtra)": "Osmanabad",
    "Raigarh": "Raigad",
    "Mumbai Suburban ": "Mumbai Suburban"
}

disease["district"] = disease["district"].replace(district_map)

# Save intermediate cleaned file
disease.to_csv("1_raw_data/disease_cleaned.csv", index=False)

print("✅ District names cleaned!")
print("Total districts:", disease["district"].nunique())
print(sorted(disease["district"].unique()))
