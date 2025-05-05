"""
Build Player Impact Scores using Machine Learning
- Uses all_players_2019_2025.csv and all_matches_2019_2025.csv
- Trains a regression model to estimate player impact
- Outputs a CSV with player names and impact scores
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import os

# CONFIGURABLE PATHS
PLAYER_STATS_PATH = os.path.abspath("titan2.5+_processor/outputs/all_players_2019_2025.csv")
MATCH_DATA_PATH = os.path.abspath("titan2.5+_processor/outputs/all_matches_2019_2025.csv")
OUTPUT_PATH = os.path.abspath("outputs/player_impact_scores_2019_2025.csv")

# 1. Load player stats and match outcomes
def load_data():
    player_stats = pd.read_csv(PLAYER_STATS_PATH)
    match_data = pd.read_csv(MATCH_DATA_PATH)
    return player_stats, match_data

# 2. Feature engineering: aggregate player stats per team per match
def prepare_training_data(player_stats, match_data):
    # Aggregate player stats for each team in each match
    agg_cols = [col for col in player_stats.columns if col not in ['Year', 'Round', 'Team', 'Player']]
    team_stats = player_stats.groupby(['Year', 'Round', 'Team'])[agg_cols].sum().reset_index()
    # Merge with match data for home and away teams
    merged = match_data.merge(
        team_stats.add_prefix('Home_'),
        left_on=['Year', 'Round', 'HomeTeam'], right_on=['Home_Year', 'Home_Round', 'Home_Team'], how='left'
    )
    merged = merged.merge(
        team_stats.add_prefix('Away_'),
        left_on=['Year', 'Round', 'AwayTeam'], right_on=['Away_Year', 'Away_Round', 'Away_Team'], how='left'
    )
    merged['Margin'] = merged['HomeScore'] - merged['AwayScore']
    return merged

# 3. Train model to estimate team impact from player stats
def train_team_impact_model(merged, agg_cols):
    feature_cols = [f'Home_{col}' for col in agg_cols] + [f'Away_{col}' for col in agg_cols]
    X = merged[feature_cols].fillna(0)
    y = merged['Margin'].fillna(0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(f"Model R2 score: {r2_score(y_test, y_pred):.3f}")
    return model, feature_cols

# 4. Calculate player impact scores (feature importances)
def calculate_player_impact_scores(model, agg_cols):
    importances = model.feature_importances_
    n = len(agg_cols)
    # Average home/away importances for each stat
    stat_importances = [(agg_cols[i], (importances[i] + importances[i+n])/2) for i in range(n)]
    impact_scores = pd.DataFrame(stat_importances, columns=['Stat', 'ImpactScore'])
    return impact_scores

# 5. Save player impact scores to CSV
def save_impact_scores(impact_scores, output_path):
    impact_scores.to_csv(output_path, index=False)
    print(f"Saved player impact scores to {output_path}")

if __name__ == "__main__":
    player_stats, match_data = load_data()
    agg_cols = [col for col in player_stats.columns if col not in ['Year', 'Round', 'Team', 'Player']]
    merged = prepare_training_data(player_stats, match_data)
    model, feature_cols = train_team_impact_model(merged, agg_cols)
    impact_scores = calculate_player_impact_scores(model, agg_cols)
    save_impact_scores(impact_scores, OUTPUT_PATH)
