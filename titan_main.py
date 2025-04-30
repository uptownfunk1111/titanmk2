# titan_main.py

import os
import pandas as pd
from titan_fetch import fetch_nrl_data
from titan_model import predict_tips
from titan_teamlist import fetch_team_lists

# Team Name Normalization (match tipping names to player team list names)
TEAM_NAME_FIXES = {
    "Sharks": "Cronulla-Sutherland Sharks",
    "Eels": "Parramatta Eels",
    "Roosters": "Sydney Roosters",
    "Dolphins": "The Dolphins",
    "Rabbitohs": "South Sydney Rabbitohs",
    "Knights": "Newcastle Knights",
    "Warriors": "New Zealand Warriors",
    "Cowboys": "North Queensland Cowboys",
    "Wests Tigers": "Wests Tigers",
    "Dragons": "St George Illawarra Dragons",
    "Titans": "Gold Coast Titans",
    "Bulldogs": "Canterbury-Bankstown Bulldogs",
    "Panthers": "Penrith Panthers",
    "Broncos": "Brisbane Broncos",
    "Storm": "Melbourne Storm",
    "Raiders": "Canberra Raiders"
}

def main():
    print("TITAN: Starting tipping process...")

    # Step 1: Fetch match data
    print("Step 1: Fetching NRL match data...")
    matches = fetch_nrl_data()
    if not matches:
        print("No match data fetched. Exiting.")
        return

    # Step 2: Fetch team lists
    print("Step 2: Fetching team lists...")
    team_lists = fetch_team_lists()
    if not team_lists:
        print("Warning: Team lists could not be fetched. Proceeding without player data.")

    # Step 3: Predict tips
    print("Step 3: Predicting tips...")
    predictions = predict_tips(matches)

    # Step 4: Build DataFrame of results
    df = pd.DataFrame(predictions)

    # Step 5: Attach player lineups (if available)
    if team_lists:
        home_lineups = []
        away_lineups = []

        for row in df.itertuples():
            home_team = getattr(row, "Home_Team")
            away_team = getattr(row, "Away_Team")

            # Normalize team names
            home_lookup = TEAM_NAME_FIXES.get(home_team, home_team)
            away_lookup = TEAM_NAME_FIXES.get(away_team, away_team)

            home_players = team_lists.get(home_lookup, [])
            away_players = team_lists.get(away_lookup, [])

            # Convert to readable strings
            home_lineup_str = ", ".join(f"{p['number']} {p['name']}" for p in home_players)
            away_lineup_str = ", ".join(f"{p['number']} {p['name']}" for p in away_players)

            home_lineups.append(home_lineup_str)
            away_lineups.append(away_lineup_str)

        df["Home Team Lineup"] = home_lineups
        df["Away Team Lineup"] = away_lineups

    # Step 6: Save to Excel
    output_folder = "outputs"
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "titan_tips.xlsx")

    print("Step 4: Saving tips to Excel...")
    df.to_excel(output_path, index=False)

    print(f"TITAN: Process complete. Tips saved to '{output_path}'.")

if __name__ == "__main__":
    main()
