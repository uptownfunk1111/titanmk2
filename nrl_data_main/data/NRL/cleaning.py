import json
import pandas as pd

# Step 1: Load your stringified JSON
with open("combined_nrl_data.json", "r", encoding="utf-8") as f:
    raw_str = f.read()

# Step 2: Convert string to JSON object
data = json.loads(raw_str)

# Step 3: Traverse to extract all match dictionaries
all_matches = []

# Structure: NRL → 0 → [ {year: [ {round: [matches]} ] } ]
for entry in data['NRL']['0']:
    for year, rounds in entry.items():
        for round_data in rounds:
            for round_number, matches in round_data.items():
                for match in matches:
                    match['Year'] = year
                    match['RoundNumber'] = round_number
                    all_matches.append(match)

# Step 4: Create DataFrame
df = pd.DataFrame(all_matches)

# Check missing values
missing_summary = df.isnull().sum()

# Impute where needed
for col in df.columns:
    if df[col].dtype == 'object':
        df[col].fillna(df[col].mode()[0], inplace=True)
    else:
        df[col].fillna(df[col].median(), inplace=True)

# Optional: Save cleaned version
df.to_json("nrl_cleaned_2025.json", orient="records", lines=True)
