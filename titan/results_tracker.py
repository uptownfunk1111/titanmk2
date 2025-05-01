# results_tracker.py

import pandas as pd
import os
from glob import glob

# Path to the tips folder
TIPS_FOLDER = "outputs"
LATEST_FILE = os.path.join(TIPS_FOLDER, "titan_tips_latest.xlsx")
RESULTS_FILE = os.path.join(TIPS_FOLDER, "actual_results.xlsx")

if not os.path.exists(RESULTS_FILE):
    print("❌ 'actual_results.xlsx' not found. Please create it with 'Home Team', 'Away Team', and 'Actual Winner' columns.")
    exit()

# Load predictions and actual results
tips_df = pd.read_excel(LATEST_FILE)
results_df = pd.read_excel(RESULTS_FILE)

# Standardise columns
tips_df.columns = [c.strip() for c in tips_df.columns]
results_df.columns = [c.strip() for c in results_df.columns]

# Merge on teams
merged = pd.merge(
    tips_df,
    results_df,
    how="inner",
    left_on=["Home_Team", "Away_Team"],
    right_on=["Home Team", "Away Team"]
)

merged["Correct"] = merged["Tip"] == merged["Actual Winner"]
correct_count = merged["Correct"].sum()
total_games = len(merged)

accuracy = round((correct_count / total_games) * 100, 2) if total_games > 0 else 0

print(f"\n📊 TITAN Accuracy Report")
print(f"------------------------")
print(f"✔️ {correct_count} correct out of {total_games} games")
print(f"🎯 Accuracy: {accuracy}%\n")

# Show breakdown
print(merged[["Home_Team", "Away_Team", "Tip", "Actual Winner", "Correct"]])
