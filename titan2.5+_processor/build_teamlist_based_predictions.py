"""
Build Teamlist-Based Predictions for Upcoming NRL Round
- Loads latest team lists (from fetch_upcoming_teamlists.py output)
- Loads per-player impact scores (from build_player_impact_scores.py output)
- Sums impact scores for each named team
- Predicts winner and margin based on team impact difference
- Outputs predictions and allows for 'what-if' analysis
"""
import os
import json
import pandas as pd
from datetime import datetime

# CONFIGURABLE PATHS
TEAMLISTS_PATH = os.path.abspath("titan2.5+_processor/outputs/NRL_teamlists_{}.json".format(datetime.now().date()))
IMPACT_SCORES_PATH = os.path.abspath("titan2.5+_processor/outputs/player_impact_scores_2019_2025.csv")
OUTPUT_PATH = os.path.abspath("titan2.5+_processor/outputs/teamlist_predictions_{}.csv".format(datetime.now().date()))

# 1. Load team lists and impact scores
print(f"[INFO] Loading team lists from: {TEAMLISTS_PATH}")
print(f"[INFO] Loading player impact scores from: {IMPACT_SCORES_PATH}")
with open(TEAMLISTS_PATH, "r", encoding="utf-8") as f:
    teamlists = json.load(f)["matches"]
impact_scores = pd.read_csv(IMPACT_SCORES_PATH)
impact_scores = impact_scores.set_index("Stat")

# 2. Helper: Calculate team impact score for a list of players
# (Assumes player stats are not yet per-player, so uses stat importances as a proxy)
def calc_team_impact(team_list):
    # If you have per-player impact, replace this logic
    # For now, sum the stat importances for all players (proxy)
    total = 0.0
    for player in team_list:
        # Optionally, use player name to look up a per-player score
        # For now, sum all stat importances as a proxy
        total += impact_scores["ImpactScore"].sum()
    return total

# Helper: Normalize team names for comparison and lookup
def normalize_team_name(name):
    if not isinstance(name, str):
        return ''
    return name.strip().lower().replace(' ', '').replace('-', '').replace('.', '')

# 3. For each match, calculate team impact and predict winner
results = []
for i in range(0, len(teamlists), 2):
    try:
        match1 = teamlists[i]
        match2 = teamlists[i+1] if i+1 < len(teamlists) else None
        home_team = normalize_team_name(match1["matchup"].split(" v ")[0])
        away_team = normalize_team_name(match1["matchup"].split(" v ")[-1])
        home_list = match1["team_list"]
        away_list = match2["team_list"] if match2 else []
        home_score = calc_team_impact(home_list)
        away_score = calc_team_impact(away_list)
        margin = home_score - away_score
        winner = home_team if margin > 0 else away_team
        results.append({
            "HomeTeam": home_team,
            "AwayTeam": away_team,
            "HomeImpact": home_score,
            "AwayImpact": away_score,
            "PredictedMargin": margin,
            "PredictedWinner": winner
        })
    except Exception as e:
        print(f"[WARN] Failed to process match: {e}")

# 4. Output predictions
pred_df = pd.DataFrame(results)
pred_df.to_csv(OUTPUT_PATH, index=False)
print(f"[SUCCESS] Saved teamlist-based predictions to {OUTPUT_PATH}")

# 5. What-if analysis (optional):
# To analyze the effect of a player swap, modify the team_list for a match and rerun calc_team_impact.
# This can be extended as needed for interactive or batch what-if scenarios.
