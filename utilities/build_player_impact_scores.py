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

# Diagnostics function
def diagnostics(df, name):
    print(f"\n[DIAG] {name}: shape={df.shape}")
    print(f"[DIAG] Columns: {list(df.columns)}")
    print(f"[DIAG] Missing values per column:\n{df.isnull().sum()}")
    for col in ['Year', 'Round', 'Team', 'HomeTeam', 'AwayTeam']:
        if col in df.columns:
            print(f"[DIAG] Unique {col}: {df[col].unique()[:10]}")
    print(f"[DIAG] Sample data:\n{df.head(3)}\n")

# 2. Feature engineering: aggregate player stats per team per match
def prepare_training_data(player_stats, match_data):
    # --- Fix: Robustly find the 'Team' column or infer from MatchKey ---
    team_col = None
    for col in player_stats.columns:
        if col.lower() == 'team':
            team_col = col
            break
    if team_col is None:
        # Try to find a close match (e.g., 'teamname', 'club', etc.)
        for col in player_stats.columns:
            if 'team' in col.lower():
                team_col = col
                print(f"[WARN] Using '{col}' as the team column.")
                break
    if team_col is None:
        # Try to infer team from MatchKey if possible
        if 'MatchKey' in player_stats.columns:
            # Attempt to parse team from MatchKey (format: 'TeamA vs TeamB', or similar)
            def infer_team(row):
                # If Name matches Home or Away team, assign accordingly (requires more context)
                # Here, just return None as placeholder
                return None
            print("[WARN] No 'Team' column found. Attempting to infer from 'MatchKey' (will set as 'Unknown' for now).")
            player_stats['Team'] = 'Unknown'  # Placeholder, user should update flattening to include team info
            team_col = 'Team'
        else:
            print("[ERROR] Could not find a 'Team' column in player stats. Available columns:")
            print(list(player_stats.columns))
            raise KeyError("No 'Team' column found in player stats CSV. Please check your data file and ensure a 'Team' column is present.")
    # Use the detected or created team_col
    player_stats['Team_norm'] = player_stats[team_col].apply(normalize_team_name)
    match_data['HomeTeam_norm'] = match_data['HomeTeam'].apply(normalize_team_name)
    match_data['AwayTeam_norm'] = match_data['AwayTeam'].apply(normalize_team_name)
    
    print("[DEBUG] player_stats dtypes:")
    print(player_stats.dtypes)
    print("[DEBUG] player_stats head:")
    print(player_stats.head())

    # Print unique Round values and counts for both match_data and player_stats before merging
    print("[DEBUG] Unique Round values in match_data:")
    print(match_data['Round'].value_counts(dropna=False).sort_index())
    print("[DEBUG] Unique Round values in player_stats:")
    print(player_stats['Round'].value_counts(dropna=False).sort_index())
    # Ensure both are int
    match_data['Round'] = match_data['Round'].fillna(-1).astype(int)
    player_stats['Round'] = player_stats['Round'].fillna(-1).astype(int)

    # Convert possible stat columns to numeric
    for col in player_stats.columns:
        if col not in ['Year', 'Round', 'Team', 'Player', 'Number', 'Team_norm', 'MatchKey', 'Name', 'Position']:
            player_stats[col] = pd.to_numeric(player_stats[col].str.replace(',', ''), errors='coerce') if player_stats[col].dtype == object else pd.to_numeric(player_stats[col], errors='coerce')

    # Only use numeric/stat columns for aggregation (exclude non-stats)
    non_stat_cols = ['Year', 'Round', 'Number', 'Team', 'Player', 'Team_norm', 'MatchKey', 'Name', 'Position']
    numeric_cols = player_stats.select_dtypes(include=[np.number]).columns.tolist()
    agg_cols = [col for col in numeric_cols if col not in non_stat_cols]
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
    # After merging, check for NaN in Round and print a warning/sample if found
    if merged['Round'].isna().any():
        print("[WARN] Some merged rows have NaN in 'Round' after merging. Sample:")
        print(merged[merged['Round'].isna()].head())
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
    try:
        impact_scores.to_csv(os.path.join(BASE_DIR, 'outputs', 'player_impact_scores_2019_2025.csv'), index=False)
        print(f"Saved player impact scores to {os.path.join(BASE_DIR, 'outputs', 'player_impact_scores_2019_2025.csv')}")
    except PermissionError as e:
        print(f"[ERROR] Permission denied when writing player_impact_scores_2019_2025.csv. Please close the file if it is open in Excel or another program and try again.")
        raise

if __name__ == "__main__":
    print("[START] Player Impact Score Builder (ML Model)")
    print("[INFO] This script loads player and match data, aggregates stats, trains a RandomForest ML model, and outputs player impact scores.")
    print("[INFO] Data sources: all_players_2019_2025.csv and all_matches_2019_2025.csv (searched in titan2.5+_processor/outputs and outputs/)")
    print("[INFO] Output: outputs/player_impact_scores_2019_2025.csv")
    player_stats, match_data = load_data()
    print("[STEP] Diagnostics on loaded player_stats:")
    diagnostics(player_stats, 'Loaded player_stats')
    print("[STEP] Diagnostics on loaded match_data:")
    diagnostics(match_data, 'Loaded match_data')
    # Print latest year and round for verification
    try:
        latest_year = int(player_stats['Year'].max())
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
    print("[STEP] Preparing training data (aggregating player stats by team/year/round and merging with match data)...")
    merged, agg_cols = prepare_training_data(player_stats, match_data)
    print("[STEP] Diagnostics on merged data:")
    diagnostics(merged, 'Merged match_data + team_stats')
    print("[STEP] Training RandomForestRegressor ML model to estimate team impact from player stats...")
    model, feature_cols = train_team_impact_model(merged, agg_cols)
    print("[STEP] Calculating player impact scores from model feature importances...")
    impact_scores = calculate_player_impact_scores(model, agg_cols)
    print("[STEP] Diagnostics on impact scores DataFrame:")
    diagnostics(impact_scores, 'Impact scores DataFrame')
    print("[STEP] Saving player impact scores to CSV...")
    save_impact_scores(impact_scores, OUTPUT_PATH)
    print("[COMPLETE] Player impact score build finished. Review outputs/player_impact_scores_2019_2025.csv for results.")
