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
import logging
from colorama import init, Fore, Style
init(autoreset=True)

log_path = 'outputs/player_impact_scores.log'
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def print_info(msg):
    print(Fore.CYAN + msg)
    logging.info(msg)

def print_success(msg):
    print(Fore.GREEN + msg)
    logging.info(msg)

def print_warn(msg):
    print(Fore.YELLOW + msg)
    logging.warning(msg)

def print_error(msg):
    print(Fore.RED + msg)
    logging.error(msg)

# CONFIGURABLE PATHS
# Always resolve relative to the project root, not CWD
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYER_STATS_PATH = os.path.join(PROJECT_ROOT, "titan2.5+_processor", "outputs", "all_players_2019_2025.csv")
MATCH_DATA_PATH = os.path.join(PROJECT_ROOT, "titan2.5+_processor", "outputs", "all_matches_2019_2025.csv")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "titan2.5+_processor", "outputs", "player_impact_scores_2019_2025.csv")

# 1. Load player stats and match outcomes
def load_data():
    print_info("[INFO] Loading player stats from: " + PLAYER_STATS_PATH)
    print_info("[INFO] Loading match data from: " + MATCH_DATA_PATH)
    player_stats = pd.read_csv(PLAYER_STATS_PATH)
    match_data = pd.read_csv(MATCH_DATA_PATH)
    print_info(f"[DEBUG] Player stats columns: {player_stats.columns.tolist()}")
    print_info(f"[DEBUG] Match data columns: {match_data.columns.tolist()}")
    # --- PATCH: Add Team column by extracting from MatchKey ---
    if 'Team' not in player_stats.columns:
        print_info("[DEBUG] 'Team' column not found in player_stats. Extracting from MatchKey...")
        def extract_team(row):
            mk = row['MatchKey']
            if '-v-' in mk:
                teams = mk.split('-v-')
                match_rows = player_stats[player_stats['MatchKey'] == mk]
                idx = match_rows.index.get_loc(row.name)
                if idx < 17:
                    team = teams[0].split('-')[-1]
                else:
                    team = teams[1]
                print_info(f"[TRACE] Assigning team '{team}' for player '{row['Name']}' in match '{mk}' (idx={idx})")
                return team
            return None
        player_stats['Team'] = player_stats.apply(extract_team, axis=1)
        print_info("[DEBUG] 'Team' column added to player_stats.")
    print_info(f"[INFO] Player stats loaded: {player_stats.shape}")
    print_info(f"[INFO] Match data loaded: {match_data.shape}")
    return player_stats, match_data

# 2. Feature engineering: aggregate player stats per team per match
def prepare_training_data(player_stats, match_data):
    print_info("[INFO] Aggregating player stats by team, year, round...")
    print_info(f"[DEBUG] player_stats dtypes before conversion:\n{player_stats.dtypes}")
    print_info(f"[DEBUG] player_stats head before conversion:\n{player_stats.head()}")
    # Convert all possible stat columns to numeric, handling commas and dashes
    for col in player_stats.columns:
        if col not in ['Year', 'Round', 'Team', 'Player', 'Number', 'Team_norm']:
            player_stats[col] = pd.to_numeric(player_stats[col].astype(str).str.replace(',', '').replace('-', ''), errors='coerce')
    print_info(f"[DEBUG] player_stats dtypes after conversion:\n{player_stats.dtypes}")
    print_info(f"[DEBUG] player_stats head after conversion:\n{player_stats.head()}")
    numeric_cols = player_stats.select_dtypes(include=[np.number]).columns.tolist()
    agg_cols = [col for col in numeric_cols if col not in ['Year', 'Round', 'Number']]
    print_info(f"[DEBUG] Aggregation columns: {agg_cols}")
    if not agg_cols:
        print_error("[ERROR] No numeric/stat columns found in player stats. Please check your data file.")
        exit(1)
    print_info(f"[DEBUG] Grouping by: ['Year', 'Round', 'Team']")
    team_stats = player_stats.groupby(['Year', 'Round', 'Team'])[agg_cols].sum().reset_index()
    print_info(f"[DEBUG] Aggregated team stats shape: {team_stats.shape}")
    print_info("[INFO] Merging team stats with match data (home/away)...")
    merged = match_data.merge(
        team_stats.add_prefix('Home_'),
        left_on=['Year', 'Round', 'HomeTeam'], right_on=['Home_Year', 'Home_Round', 'Home_Team'], how='left'
    )
    merged = merged.merge(
        team_stats.add_prefix('Away_'),
        left_on=['Year', 'Round', 'AwayTeam'], right_on=['Away_Year', 'Away_Round', 'Away_Team'], how='left'
    )
    merged['Margin'] = merged['HomeScore'] - merged['AwayScore']
    print_info(f"[INFO] Merged data shape: {merged.shape}")
    print_info(f"[DEBUG] Merged data columns: {merged.columns.tolist()}")
    return merged, agg_cols

# 3. Train model to estimate team impact from player stats
def train_team_impact_model(merged, agg_cols):
    print_info("[INFO] Training RandomForestRegressor to estimate team impact...")
    feature_cols = [f'Home_{col}' for col in agg_cols] + [f'Away_{col}' for col in agg_cols]
    print_info(f"[DEBUG] Feature columns for training: {feature_cols[:5]} ... (total {len(feature_cols)})")
    X = merged[feature_cols].fillna(0)
    y = merged['Margin'].fillna(0)
    print_info(f"[DEBUG] Training features shape: {X.shape}")
    print_info(f"[DEBUG] Training target shape: {y.shape}")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print_info(f"[INFO] Training set size: {X_train.shape[0]}, Test set size: {X_test.shape[0]}")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    print_info("[INFO] Fitting model...")
    model.fit(X_train, y_train)
    print_info("[INFO] Model fit complete. Predicting on test set...")
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    print_info(f"[RESULT] Model R2 score: {r2:.3f}")
    return model, feature_cols

# 4. Calculate player impact scores (feature importances)
def calculate_player_impact_scores(model, agg_cols):
    print_info("[INFO] Calculating player impact scores from feature importances...")
    importances = model.feature_importances_
    n = len(agg_cols)
    print_info(f"[DEBUG] Number of stats/features: {n}")
    # Average home/away importances for each stat
    stat_importances = [(agg_cols[i], (importances[i] + importances[i+n])/2) for i in range(n)]
    impact_scores = pd.DataFrame(stat_importances, columns=['Stat', 'ImpactScore'])
    print_info("[INFO] Top 5 impact scores:")
    print_info(str(impact_scores.sort_values('ImpactScore', ascending=False).head()))
    return impact_scores

# 5. Save player impact scores to CSV
def save_impact_scores(impact_scores, output_path):
    print_info(f"[INFO] Saving impact scores to {output_path} ...")
    impact_scores.to_csv(output_path, index=False)
    print_success(f"[SUCCESS] Saved player impact scores to {output_path}")

if __name__ == "__main__":
    print_info("[START] Building player impact scores...")
    try:
        player_stats, match_data = load_data()
        if player_stats.empty or match_data.empty:
            print_warn("[WARN] One or more input files are empty. Exiting.")
            exit(1)
        merged, agg_cols = prepare_training_data(player_stats, match_data)
        if not agg_cols:
            print_warn("[WARN] No aggregate columns found in player stats. Exiting.")
            exit(1)
        model, feature_cols = train_team_impact_model(merged, agg_cols)
        impact_scores = calculate_player_impact_scores(model, agg_cols)
        save_impact_scores(impact_scores, OUTPUT_PATH)
        print_success("[COMPLETE] Player impact score build finished.")
        print_info("[SAMPLE OUTPUT]")
        print_info(str(impact_scores.head()))
    except Exception as e:
        print_error(f"[ERROR] Exception in player impact score build: {e}")
        exit(1)
