import os
import pandas as pd
from utilities.load_match_data import load_match_data
from utilities.load_player_stats_custom import load_player_stats_custom
from utilities.load_detailed_match_data import load_detailed_match_data
from utilities.merge_all import merge_all

# CONFIGURATION
BASE_PATH = "./nrl_fixed"
OUTPUT_PATH = "./outputs"
YEARS = list(range(2019, 2026))

os.makedirs(OUTPUT_PATH, exist_ok=True)
match_dfs, player_dfs, detailed_dfs = [], [], []

# LOAD FILES
for year in YEARS:
    print(f"Loading {year}...")
    folder = os.path.join(BASE_PATH, str(year))

    match_file = os.path.join(folder, f"NRL_data_{year}.json")
    player_file = os.path.join(folder, f"NRL_player_statistics_{year}.json")
    detailed_file = os.path.join(folder, f"NRL_detailed_match_data_{year}.json")

    if os.path.exists(match_file):
        match_dfs.append(load_match_data(match_file, year))
    else:
        print(f"Missing: {match_file}")

    if os.path.exists(player_file):
        player_dfs.append(load_player_stats_custom(player_file, year))
    else:
        print(f"Missing: {player_file}")

    if os.path.exists(detailed_file):
        detailed_dfs.append(load_detailed_match_data(detailed_file))
    else:
        print(f"Missing: {detailed_file}")

# COMBINE AND MERGE
print("Combining datasets...")
match_df = pd.concat(match_dfs, ignore_index=True)
player_df = pd.concat(player_dfs, ignore_index=True)
detailed_df = pd.concat(detailed_dfs, ignore_index=True)

# Handle missing columns and merge
final_df = merge_all(match_df, player_df, detailed_df)

# EXPORT
final_df.to_csv(f"{OUTPUT_PATH}/titan_ml_dataset.csv", index=False)
final_df.to_json(f"{OUTPUT_PATH}/titan_ml_dataset.json", orient="records", indent=2)
final_df.to_parquet(f"{OUTPUT_PATH}/titan_ml_dataset.parquet", index=False)

print("All datasets saved to /outputs/")
