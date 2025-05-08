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

# Fix the PLAYER_STATS_PATH and MATCH_DATA_PATH to use the correct outputs directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Try titan2.5+_processor/outputs first, then fallback to outputs/
POSSIBLE_OUTPUTS_DIRS = [
    os.path.join(BASE_DIR, 'titan2.5+_processor', 'outputs'),
    os.path.join(BASE_DIR, 'outputs'),
    os.path.join(BASE_DIR, 'titan2.5+_processor', '..', 'outputs'),
]
PLAYER_STATS_PATH = None
MATCH_DATA_PATH = None
for out_dir in POSSIBLE_OUTPUTS_DIRS:
    player_stats_candidate = os.path.join(out_dir, 'all_players_2019_2025.csv')
    match_data_candidate = os.path.join(out_dir, 'all_matches_2019_2025.csv')
    if os.path.exists(player_stats_candidate) and os.path.exists(match_data_candidate):
        PLAYER_STATS_PATH = player_stats_candidate
        MATCH_DATA_PATH = match_data_candidate
        break
if PLAYER_STATS_PATH is None or MATCH_DATA_PATH is None:
    raise FileNotFoundError("Could not find all_players_2019_2025.csv or all_matches_2019_2025.csv in expected outputs directories.")

OUTPUT_PATH = os.path.abspath("outputs/player_impact_scores_2019_2025.csv")

# 1. Load player stats and match outcomes
def load_data():
    player_stats = pd.read_csv(PLAYER_STATS_PATH)
    match_data = pd.read_csv(MATCH_DATA_PATH)
    return player_stats, match_data

# Normalize team names to reduce mismatches
def normalize_team_name(name):
    if pd.isna(name):
        return ''
    return str(name).strip().lower().replace(' ', '').replace('-', '').replace('.', '')

# 2. Feature engineering: aggregate player stats per team per match
def prepare_training_data(player_stats, match_data):
    # Normalize team names in both dataframes
    player_stats = player_stats.copy()
    match_data = match_data.copy()
    player_stats['Team_norm'] = player_stats['Team'].apply(normalize_team_name)
    match_data['HomeTeam_norm'] = match_data['HomeTeam'].apply(normalize_team_name)
    match_data['AwayTeam_norm'] = match_data['AwayTeam'].apply(normalize_team_name)
    
    print("[DEBUG] player_stats dtypes:")
    print(player_stats.dtypes)
    print("[DEBUG] player_stats head:")
    print(player_stats.head())

    # Convert possible stat columns to numeric
    for col in player_stats.columns:
        if col not in ['Year', 'Round', 'Team', 'Player', 'Number', 'Team_norm']:
            player_stats[col] = pd.to_numeric(player_stats[col].str.replace(',', ''), errors='coerce') if player_stats[col].dtype == object else pd.to_numeric(player_stats[col], errors='coerce')

    numeric_cols = player_stats.select_dtypes(include=[np.number]).columns.tolist()
    agg_cols = [col for col in numeric_cols if col not in ['Year', 'Round', 'Number']]
    print(f"[DEBUG] Aggregation columns: {agg_cols}")

    if not agg_cols:
        print("[ERROR] No numeric/stat columns found in player stats. Please check your data file.")
        exit(1)

    print(f"[DEBUG] Grouping by: ['Year', 'Round', 'Team_norm']")
    team_stats = player_stats.groupby(['Year', 'Round', 'Team_norm'])[agg_cols].sum().reset_index()
    print(f"[DEBUG] player_stats rows: {len(player_stats)}")
    print(f"[DEBUG] match_data rows: {len(match_data)}")
    print(f"[DEBUG] team_stats rows: {len(team_stats)}")
    # Merge with match data for home and away teams using normalized names
    merged = match_data.merge(
        team_stats.add_prefix('Home_'),
        left_on=['Year', 'Round', 'HomeTeam_norm'], right_on=['Home_Year', 'Home_Round', 'Home_Team_norm'], how='left'
    )
    merged = merged.merge(
        team_stats.add_prefix('Away_'),
        left_on=['Year', 'Round', 'AwayTeam_norm'], right_on=['Away_Year', 'Away_Round', 'Away_Team_norm'], how='left'
    )
    merged['Margin'] = merged['HomeScore'] - merged['AwayScore']
    print(f"[DEBUG] merged rows: {len(merged)}")
    print(f"[DEBUG] merged columns: {list(merged.columns)}")
    print(f"[DEBUG] NaNs in HomeScore: {merged['HomeScore'].isna().sum()} | AwayScore: {merged['AwayScore'].isna().sum()} | Margin: {merged['Margin'].isna().sum()}")
    # Remove rows with missing HomeScore, AwayScore, or Margin
    merged = merged.dropna(subset=["HomeScore", "AwayScore", "Margin"])
    print(f"[DEBUG] After dropping NaNs in HomeScore/AwayScore/Margin: {len(merged)} rows remain.")
    # Print a sample of rows that had NaNs before dropping (for diagnosis)
    nan_rows = match_data[(match_data['HomeScore'].isna()) | (match_data['AwayScore'].isna())]
    if not nan_rows.empty:
        print(f"[DEBUG] Sample rows in match_data with NaN HomeScore/AwayScore:\n{nan_rows.head(5)}")
    # Print a sample of rows that failed to merge player stats (for diagnosis)
    merged_nan_stats = merged[merged.isna().any(axis=1)]
    if not merged_nan_stats.empty:
        print(f"[DEBUG] Sample merged rows with remaining NaNs after merge (first 5):\n{merged_nan_stats.head(5)}")
    return merged, agg_cols

# 3. Train model to estimate team impact from player stats
def train_team_impact_model(merged, agg_cols):
    feature_cols = [f'Home_{col}' for col in agg_cols] + [f'Away_{col}' for col in agg_cols]
    X = merged[feature_cols].fillna(0)
    X = X.infer_objects(copy=False)  # Fix FutureWarning for fillna downcasting
    y = merged['Margin'].fillna(0)
    print(f"[DEBUG] X shape: {X.shape}, y shape: {y.shape}")
    print(f"[DEBUG] NaNs in features: {X.isna().sum().sum()} | NaNs in target: {y.isna().sum()}")
    print(f"[DEBUG] Margin stats: min={y.min()}, max={y.max()}, mean={y.mean()}, std={y.std()}")
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
    impact_scores.to_csv(os.path.join(BASE_DIR, 'outputs', 'player_impact_scores_2019_2025.csv'), index=False)
    print(f"Saved player impact scores to {os.path.join(BASE_DIR, 'outputs', 'player_impact_scores_2019_2025.csv')}")

if __name__ == "__main__":
    player_stats, match_data = load_data()
    # Print latest year and round for verification
    try:
        latest_year = int(player_stats['Year'].max())
        # Only use non-NaN rounds for max
        rounds_this_year = player_stats[player_stats['Year'] == latest_year]['Round'].dropna()
        if not rounds_this_year.empty:
            latest_round = int(rounds_this_year.max())
            print(f"[INFO] Player stats include up to year {latest_year}, round {latest_round}.")
        else:
            print(f"[INFO] Player stats include up to year {latest_year}, but no valid round data found.")
        latest_year_m = int(match_data['Year'].max())
        rounds_this_year_m = match_data[match_data['Year'] == latest_year_m]['Round'].dropna()
        if not rounds_this_year_m.empty:
            latest_round_m = int(rounds_this_year_m.max())
            print(f"[INFO] Match data includes up to year {latest_year_m}, round {latest_round_m}.")
        else:
            print(f"[INFO] Match data includes up to year {latest_year_m}, but no valid round data found.")
    except Exception as e:
        print(f"[WARN] Could not determine latest year/round in data: {e}")
    merged, agg_cols = prepare_training_data(player_stats, match_data)
    model, feature_cols = train_team_impact_model(merged, agg_cols)
    impact_scores = calculate_player_impact_scores(model, agg_cols)
    save_impact_scores(impact_scores, OUTPUT_PATH)
