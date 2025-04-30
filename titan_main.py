# titan_main.py

from titan_fetch import fetch_nrl_data
from titan_teamlist import fetch_team_lists
from titan_model import predict_tips
import pandas as pd
from datetime import datetime
import os

def ensure_output_folder():
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

def save_tips_to_excel(tips):
    df = pd.DataFrame(tips)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    timestamped_path = f"outputs/titan_tips_{now}.xlsx"
    latest_path = "outputs/titan_tips_latest.xlsx"
    
    df.to_excel(timestamped_path, index=False)
    df.to_excel(latest_path, index=False)
    
    print(f"✅ Tips saved to '{timestamped_path}' and 'titan_tips_latest.xlsx'.")

if __name__ == "__main__":
    print("TITAN: Starting tipping process...")
    ensure_output_folder()

    # Step 1: Fetch matchups
    print("Step 1: Fetching NRL match data...")
    matches = fetch_nrl_data()
    if not matches:
        print("⚠️ No matches found. Skipping prediction.")
    else:
        print(f"Fetched match data: {matches}")

        # Step 2: Fetch team lists
        print("Step 2: Fetching team lists...")
        team_lists = fetch_team_lists()
        if not team_lists:
            print("⚠️ Team lists could not be fetched. Proceeding without player data.")
        else:
            print(f"Fetched {len(team_lists)} player entries.")

        # Step 3: Predict tips
        print("Step 3: Predicting tips...")
        tips = predict_tips(matches, team_lists)

        # Step 4: Save to Excel
        print("Step 4: Saving tips to Excel...")
        save_tips_to_excel(tips)
        print("TITAN: Process complete.")
