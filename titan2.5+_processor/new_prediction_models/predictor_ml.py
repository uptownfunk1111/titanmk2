"""
# TITAN 2.5+ NRL Prediction Model

A comprehensive machine learning pipeline for NRL match prediction, integrating:
- Historical match data
- Player and team statistics
- Contextual and real-time features
- Risk, betting, and tactical overlays

Author: Your Name
Date: 2025-05-05
"""

# ==========================================================
# 1. IMPORTS
# ----------------------------------------------------------
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import os
import sys  # Add this import for sys.exit
import time

print('--- TITAN 2.5+ NRL Prediction Model: Script Started ---')

# ==========================================================
# 2. DATA LOADING
# ----------------------------------------------------------
# Use the most up-to-date normalised data from the outputs directory
# Always resolve outputs_dir to the project root outputs/ directory for consistency
# This ensures the script works regardless of where it is run from
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
outputs_root = os.path.join(project_root, 'outputs')
t2p_outputs = os.path.join(project_root, 'titan2.5+_processor', 'outputs')

matches_path = os.path.join(outputs_root, 'normalised_all_matches_2019_2025.csv')
players_path = os.path.join(t2p_outputs, 'all_players_2019_2025.csv')
detailed_matches_path = os.path.join(t2p_outputs, 'all_detailed_matches_2019_2025.csv')
impact_scores_path = os.path.join(outputs_root, 'player_impact_scores_2019_2025.csv')
fixtures_path = os.path.join(outputs_root, 'upcoming_fixtures_and_officials_2025_round10.csv')
weather_impact_path = os.path.join(outputs_root, 'weather_impact_analysis.csv')

print('\n[DEBUG] --- STARTING TITAN 2.5+ NRL PREDICTION MODEL ---')
print(f'[DEBUG] Project root: {project_root}')
print(f'[DEBUG] Outputs root: {outputs_root}')
print(f'[DEBUG] Titan2.5+ outputs: {t2p_outputs}')

print('Loading data from:', outputs_root)
print('  matches_path:', matches_path)
print('  players_path:', players_path)
print('  detailed_matches_path:', detailed_matches_path)
print('  impact_scores_path:', impact_scores_path)
print('  fixtures_path:', fixtures_path)
print('  weather_impact_path:', weather_impact_path)

try:
    matches = pd.read_csv(matches_path)
    print(f'[DEBUG] Loaded matches from {matches_path}, shape: {matches.shape}')
    print(f'[DEBUG] Columns: {matches.columns.tolist()}')
    print(f'[DEBUG] Head:\n{matches.head()}')
    # --- FIX: Normalize column names to expected format ---
    col_map = {
        'year': 'Year',
        'round': 'Round',
        'hometeam': 'HomeTeam',
        'homescore': 'HomeScore',
        'awayteam': 'AwayTeam',
        'awayscore': 'AwayScore',
        'venue': 'Venue',
        'date': 'Date',
        'matchcentreurl': 'MatchCentreURL',
        'data_issues': 'data_issues',
    }
    matches.columns = [col_map.get(c.lower(), c) for c in matches.columns]
    print(f'[DEBUG] matches columns after normalization: {matches.columns.tolist()}')
    print(f'Loaded matches: {matches.shape}')
    print('[DEBUG] matches columns:', matches.columns.tolist())
    print('[DEBUG] matches head:')
    print(matches.head())
    expected_cols = {'Year', 'Round', 'HomeTeam', 'HomeScore', 'AwayTeam', 'AwayScore', 'Venue', 'Date', 'MatchCentreURL'}
    if not expected_cols.issubset(set(matches.columns)):
        print(f"[FATAL] Matches file '{matches_path}' does not contain expected columns. Found columns: {matches.columns.tolist()}")
        print("[HINT] Check the CSV header row and the script that generates this file.")
        sys.exit(1)
    if matches.empty:
        print(f"[FATAL] Matches file '{matches_path}' is empty. Please check your data extraction and flattening pipeline.")
        sys.exit(1)
except Exception as e:
    print(f'[ERROR] Failed to load matches: {e}')
    sys.exit()
try:
    players = pd.read_csv(players_path)
    print(f'[DEBUG] Loaded players from {players_path}, shape: {players.shape}')
    print(f'[DEBUG] Columns: {players.columns.tolist()}')
    print(f'[DEBUG] Head:\n{players.head()}')
except Exception as e:
    print(f'[ERROR] Failed to load players: {e}')
    players = pd.DataFrame()
try:
    detailed_matches = pd.read_csv(detailed_matches_path)
    print(f'[DEBUG] Loaded detailed_matches from {detailed_matches_path}, shape: {detailed_matches.shape}')
    print(f'[DEBUG] Columns: {detailed_matches.columns.tolist()}')
    print(f'[DEBUG] Head:\n{detailed_matches.head()}')
except Exception as e:
    print(f'[ERROR] Failed to load detailed_matches: {e}')
    detailed_matches = pd.DataFrame()

if os.path.exists(impact_scores_path):
    impact_scores = pd.read_csv(impact_scores_path)
    print(f'[DEBUG] Loaded impact_scores from {impact_scores_path}, shape: {impact_scores.shape}')
    print(f'[DEBUG] Columns: {impact_scores.columns.tolist()}')
    print(f'[DEBUG] Head:\n{impact_scores.head()}')
    impact_score_dict = dict(zip(impact_scores['Stat'], impact_scores['ImpactScore']))
else:
    print('[WARN] Impact scores file not found.')
    impact_scores = None
    impact_score_dict = {}

# Try reading fixtures with utf-8-sig, fallback to latin1 if UnicodeDecodeError
fixtures = None
try:
    fixtures = pd.read_csv(fixtures_path, encoding='utf-8-sig')
    print(f'[DEBUG] Loaded fixtures from {fixtures_path}, shape: {fixtures.shape}')
    print(f'[DEBUG] Columns: {fixtures.columns.tolist()}')
    print(f'[DEBUG] Head:\n{fixtures.head()}')
except UnicodeDecodeError:
    try:
        fixtures = pd.read_csv(fixtures_path, encoding='latin1')
        print(f'[DEBUG] Loaded fixtures (latin1) from {fixtures_path}, shape: {fixtures.shape}')
        print(f'[DEBUG] Columns: {fixtures.columns.tolist()}')
        print(f'[DEBUG] Head:\n{fixtures.head()}')
    except Exception as e:
        print(f'[ERROR] Fixtures file could not be loaded with utf-8-sig or latin1 encoding: {e}')
        fixtures = None
except Exception as e:
    print(f'[WARN] Fixtures file not loaded or not found: {fixtures_path}')
    fixtures = None

try:
    weather_impact = pd.read_csv(weather_impact_path)
    print(f'[DEBUG] Loaded weather impact from {weather_impact_path}, shape: {weather_impact.shape}')
    print(f'[DEBUG] Columns: {weather_impact.columns.tolist()}')
    print(f'[DEBUG] Head:\n{weather_impact.head()}')
except Exception as e:
    print(f'[WARN] Weather impact file not loaded or not found: {weather_impact_path}')
    weather_impact = pd.DataFrame()

# Ensure merge keys are of the same type and not nullable
for df_name in ['matches', 'players']:
    df = locals()[df_name]
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df = df.dropna(subset=['Year'])
        df['Year'] = df['Year'].astype(int)
    if 'Round' in df.columns:
        df['Round'] = pd.to_numeric(df['Round'], errors='coerce')
        df = df.dropna(subset=['Round'])
        df['Round'] = df['Round'].astype(int)
    if 'Team' in df.columns:
        df['Team'] = df['Team'].astype(str)
    if df_name == 'matches':
        matches = df
    elif df_name == 'players':
        players = df

# === TEAM NAME NORMALIZATION AND DIAGNOSTICS ===
def normalize_team_name(name):
    if pd.isna(name):
        return ''
    return str(name).strip().lower().replace(' ', '').replace('-', '').replace('.', '')

# Normalize team names in matches and players
print('[DEBUG] --- NORMALIZING TEAM NAMES ---')
for col in ['HomeTeam', 'AwayTeam', 'Team']:
    if col in matches.columns:
        matches[col + '_norm'] = matches[col].apply(normalize_team_name)
    if col in players.columns:
        players[col + '_norm'] = players[col].apply(normalize_team_name)

# Print diagnostics for merge keys
print('[DEBUG] --- MERGE KEY DIAGNOSTICS ---')
print(f'[DEBUG] matches Year dtype: {matches["Year"].dtype}, unique: {sorted(matches["Year"].unique())[:5]} ...')
print(f'[DEBUG] players Year dtype: {players["Year"].dtype}, unique: {sorted(players["Year"].unique())[:5]} ...')
print(f'[DEBUG] matches Round dtype: {matches["Round"].dtype}, unique: {sorted(matches["Round"].unique())[:5]} ...')
print(f'[DEBUG] players Round dtype: {players["Round"].dtype}, unique: {sorted(players["Round"].unique())[:5]} ...')
print(f'[DEBUG] matches HomeTeam_norm unique: {matches["HomeTeam_norm"].unique()[:5]} ...')
print(f'[DEBUG] players Team_norm unique: {players["Team_norm"].unique()[:5]} ...')

# Merge weather features into matches on Date and Venue if available
if not weather_impact.empty and 'Date' in matches.columns and 'Venue' in matches.columns:
    matches = matches.merge(
        weather_impact[['Date', 'Venue', 'Rain', 'WindSpeed', 'WindDirection', 'Temperature', 'Humidity', 'WeatherCondition', 'Pressure', 'CloudCover', 'DewPoint', 'UVIndex']],
        on=['Date', 'Venue'], how='left', suffixes=('', '_weather')
    )
    print('[INFO] Weather features merged into matches.')
    print('[DEBUG] matches columns after weather merge:', matches.columns.tolist())

# === LOAD AND MERGE ALL OVERLAY/ENHANCEMENT CSVs ===
# Define overlay files and merge keys
# All overlays are expected in the root outputs/ directory
overlay_files = {
    'lineup_impact': ('lineup_impact.csv', ['Year', 'Round', 'HomeTeam']),
    'kick_target_mapping': ('kick_target_mapping.csv', ['Year', 'Round', 'HomeTeam']),
    'officiating_impact': ('officiating_impact_analysis.csv', ['Year', 'Round']),
    'speculative': ('utilities/speculative_data_sweep.csv', ['Year', 'Round', 'HomeTeam']),
    'opponent_analysis': ('opponent_analysis.csv', ['Year', 'Round', 'HomeTeam']),
    'player_injury_impact': ('player_injury_impact.csv', ['Year', 'Round', 'HomeTeam']),
    'coach_impact_analysis': ('coach_impact_analysis.csv', ['Year', 'Round', 'HomeTeam']),
    'kick_events': ('kick_events.csv', ['Year', 'Round', 'HomeTeam']),  # Added kick events overlay
    # Add more overlays as needed
}

for overlay_name, (filename, merge_keys) in overlay_files.items():
    overlay_path = os.path.join(outputs_root, filename)
    if os.path.exists(overlay_path):
        print(f'[DEBUG] Attempting to merge overlay: {overlay_name} from {overlay_path}')
        try:
            overlay_df = pd.read_csv(overlay_path)
            print(f'[DEBUG] Overlay {overlay_name} shape: {overlay_df.shape}')
            print(f'[DEBUG] Overlay {overlay_name} columns: {overlay_df.columns.tolist()}')
            # Normalize merge keys if needed
            for key in merge_keys:
                if key in overlay_df.columns and key in matches.columns:
                    overlay_df[key] = overlay_df[key].astype(str)
                    matches[key] = matches[key].astype(str)
            # Merge overlay into matches
            matches = matches.merge(overlay_df, on=merge_keys, how='left', suffixes=('', f'_{overlay_name}'))
            print(f'[DEBUG] Overlay {overlay_name} merged. Matches shape: {matches.shape}')
        except Exception as e:
            print(f'[WARN] Failed to merge {overlay_name}: {e}')
    else:
        print(f'[INFO] Overlay file not found: {overlay_path}')

if 'officiating_impact' in overlay_files:
    print('[DEBUG] Officiating impact features available:', [col for col in matches.columns if 'officiating_impact' in col])

print('Data loading complete. Proceeding to feature engineering...')

# ==========================================================
# 3. FEATURE ENGINEERING
# ----------------------------------------------------------
# --- Detect player name column in players DataFrame ---
player_name_col = None
for col in ['Player', 'Name', 'player', 'name']:
    if col in players.columns:
        player_name_col = col
        break
if not player_name_col:
    print('[FATAL] Could not find a player name column in player stats. Columns found:', players.columns.tolist())
    sys.exit(1)

print('[DEBUG] --- FEATURE ENGINEERING ---')
print(f'[DEBUG] Player name column detected: {player_name_col}')

# Aggregate player stats, calculate recent form, margin, etc.
merge_successful = False
if not players.empty and 'Team_norm' in players.columns and 'Year' in players.columns and 'Round' in players.columns:
    print('[DEBUG] Aggregating player stats by team/year/round...')
    agg_cols = [col for col in players.columns if col not in ['Year', 'Round', 'Team', player_name_col, 'Team_norm']]
    print(f'[DEBUG] Aggregation columns: {agg_cols}')
    player_agg = players.groupby(['Year', 'Round', 'Team_norm'])[agg_cols].sum().reset_index()
    print(f'[DEBUG] player_agg shape: {player_agg.shape}')
    print(f'[DEBUG] player_agg head:\n{player_agg.head()}')
    # Merge for home and away teams using normalized keys
    matches_before_merge = matches.copy()
    print('[DEBUG] Merging player_agg for HomeTeam...')
    matches = matches.merge(
        player_agg.rename(lambda x: f'Home_{x}' if x not in ['Year', 'Round', 'Team_norm'] else x, axis=1),
        left_on=['Year', 'Round', 'HomeTeam_norm'], right_on=['Year', 'Round', 'Team_norm'], how='left'
    ).drop('Team_norm', axis=1)
    print('[DEBUG] Merging player_agg for AwayTeam...')
    matches = matches.merge(
        player_agg.rename(lambda x: f'Away_{x}' if x not in ['Year', 'Round', 'Team_norm'] else x, axis=1),
        left_on=['Year', 'Round', 'AwayTeam_norm'], right_on=['Year', 'Round', 'Team_norm'], how='left', suffixes=('', '_away')
    ).drop('Team_norm', axis=1)
    print(f'[DEBUG] matches shape after merge: {matches.shape}')
    print(f'[DEBUG] matches head after merge:\n{matches.head()}')
    if matches.shape[0] == 0:
        print('[ERROR] Merge resulted in empty matches DataFrame. Reverting to original matches data.')
        matches = matches_before_merge
    else:
        merge_successful = True

# Always perform feature engineering, even if merge fails
print('[DEBUG] --- RECENT FORM CALCULATION ---')
print(f'[DEBUG] Calculating rolling averages for Home_RecentForm and Away_RecentForm...')
matches = matches.sort_values(['Year', 'Round'])
for team_col, score_col, new_col in [
    ('HomeTeam', 'HomeScore', 'Home_RecentForm'),
    ('AwayTeam', 'AwayScore', 'Away_RecentForm')
]:
    matches[new_col] = matches.groupby(team_col)[score_col].transform(lambda x: x.rolling(window=3, min_periods=1).mean())

# Ensure HomeImpactScore and AwayImpactScore exist
if 'HomeImpactScore' not in matches.columns:
    matches['HomeImpactScore'] = np.nan
if 'AwayImpactScore' not in matches.columns:
    matches['AwayImpactScore'] = np.nan

print('[DEBUG] --- IMPACT SCORE CALCULATION ---')
# Function to calculate team impact score from player list
# Use detected player_name_col instead of hardcoded 'Player'
def get_team_impact_score(player_list_str, player_stats_df, impact_score_dict):
    if pd.isna(player_list_str):
        return 0.0
    players_list = [p.strip() for p in player_list_str.split(',') if p.strip()]
    total_score = 0.0
    for player in players_list:
        player_row = player_stats_df[player_stats_df[player_name_col] == player]
        if not player_row.empty:
            for stat, impact in impact_score_dict.items():
                if stat in player_row.columns:
                    total_score += player_row.iloc[0][stat] * impact
    return total_score

# Add HomeImpactScore and AwayImpactScore to fixtures if available
if fixtures is not None and impact_scores is not None and not players.empty:
    fixtures['HomeImpactScore'] = fixtures.apply(
        lambda row: get_team_impact_score(row['HomeTeamList'], players, impact_score_dict), axis=1)
    fixtures['AwayImpactScore'] = fixtures.apply(
        lambda row: get_team_impact_score(row['AwayTeamList'], players, impact_score_dict), axis=1)

# Add HomeImpactScore and AwayImpactScore to matches for model training
if impact_scores is not None and not players.empty:
    def get_team_impact_score_train(team, year, round_num, player_stats_df, impact_score_dict):
        team_players = player_stats_df[(player_stats_df['Team'] == team) & (player_stats_df['Year'] == year) & (player_stats_df['Round'] == round_num)][player_name_col]
        total_score = 0.0
        for player in team_players:
            player_row = player_stats_df[player_stats_df[player_name_col] == player]
            if not player_row.empty:
                for stat, impact in impact_score_dict.items():
                    if stat in player_row.columns:
                        total_score += player_row.iloc[0][stat] * impact
        return total_score
    matches['HomeImpactScore'] = matches.apply(
        lambda row: get_team_impact_score_train(row['HomeTeam'], row['Year'], row['Round'], players, impact_score_dict), axis=1)
    matches['AwayImpactScore'] = matches.apply(
        lambda row: get_team_impact_score_train(row['AwayTeam'], row['Year'], row['Round'], players, impact_score_dict), axis=1)

# === ADVANCED TEAM & PLAYER FEATURES (from player_stats_review.ipynb) ===
# Compute team-level attack/defense/halftime/second-half features
team_features = []
for team in matches['HomeTeam'].unique():
    team_matches = matches[(matches['HomeTeam'] == team) | (matches['AwayTeam'] == team)]
    # Only use matches where team played
    team_attack = pd.concat([
        team_matches[team_matches['HomeTeam'] == team]['HomeScore'],
        team_matches[team_matches['AwayTeam'] == team]['AwayScore']
    ])
    team_defense = pd.concat([
        team_matches[team_matches['HomeTeam'] == team]['AwayScore'],
        team_matches[team_matches['AwayTeam'] == team]['HomeScore']
    ])
    avg_attack = team_attack[team_attack != -1].mean()
    avg_defense = team_defense[team_defense != -1].mean()
    # Halftime/Second half (if available)
    if 'HomeHalftimeScore' in matches.columns and 'AwayHalftimeScore' in matches.columns:
        team_halftime_attack = pd.concat([
            team_matches[team_matches['HomeTeam'] == team]['HomeHalftimeScore'],
            team_matches[team_matches['AwayTeam'] == team]['AwayHalftimeScore']
        ])
        team_halftime_defense = pd.concat([
            team_matches[team_matches['HomeTeam'] == team]['AwayHalftimeScore'],
            team_matches[team_matches['AwayTeam'] == team]['HomeHalftimeScore']
        ])
        avg_halftime_attack = team_halftime_attack[team_halftime_attack != -1].mean()
        avg_halftime_defense = team_halftime_defense[team_halftime_defense != -1].mean()
        avg_secondhalf_attack = avg_attack - avg_halftime_attack
        avg_secondhalf_defense = avg_defense - avg_halftime_defense
    else:
        avg_halftime_attack = avg_halftime_defense = avg_secondhalf_attack = avg_secondhalf_defense = np.nan
    team_features.append({
        'Team': team,
        'AvgAttack': avg_attack,
        'AvgDefense': avg_defense,
        'AvgHalftimeAttack': avg_halftime_attack,
        'AvgHalftimeDefense': avg_halftime_defense,
        'AvgSecondHalfAttack': avg_secondhalf_attack,
        'AvgSecondHalfDefense': avg_secondhalf_defense
    })
team_features_df = pd.DataFrame(team_features)
# Merge team features into matches for home and away teams
matches = matches.merge(team_features_df.add_prefix('Home_'), left_on='HomeTeam', right_on='Home_Team', how='left')
matches = matches.merge(team_features_df.add_prefix('Away_'), left_on='AwayTeam', right_on='Away_Team', how='left')

print('Feature engineering complete. matches shape:', matches.shape)

# === TRY SCORER MODEL INTEGRATION ===
try:
    from utilities import try_scorer_model
    print('[DEBUG] Running try scorer feature engineering...')
    try_scorer_players = try_scorer_model.load_player_data(year=2025, total_rounds=8)
    try_scorer_df = try_scorer_model.try_scorer_features(try_scorer_players, ["Name", "Tries", "Tackle Efficiency"])
    try_scorer_output = os.path.join(outputs_root, 'try_scorer_features_2025.csv')
    try_scorer_model.save_try_scorer_features(try_scorer_df, try_scorer_output)
    print(f'[DEBUG] Try scorer features exported to {try_scorer_output}')
except Exception as e:
    print(f'[WARN] Try scorer model step failed: {e}')

# ==========================================================
# 4. CONTEXTUAL FEATURES (PLACEHOLDERS)
# ----------------------------------------------------------
def fetch_weather(match_date, venue):
    return {'temperature': None, 'wind_speed': None}
def fetch_injuries_and_lineups(match_date, teams):
    return {'injuries': None, 'lineups': None}
def fetch_referee_impact(referee_name):
    return {'penalties_per_game': None, 'bias_metric': None}
def fetch_coaching_tactics(team, date):
    return {'style': None, 'recent_changes': None}

# ==========================================================
# 5. BETTING, RISK, AND TACTICAL LAYERING PLACEHOLDERS
# ----------------------------------------------------------
# Edge Mismatch Calculation
# Example: Use kick target mapping or player stats to flag edge mismatches
try:
    kick_report_path = os.path.join(outputs_root, 'kick_report_{}.csv'.format(pd.Timestamp.today().date()))
    if os.path.exists(kick_report_path):
        kick_df = pd.read_csv(kick_report_path)
        # Example: flag matches where a team targets a weak edge of the opponent
        # (This is a placeholder. Replace with your own logic as needed)
        edge_mismatch_flags = []
        for idx, row in matches.iterrows():
            home = row['HomeTeam'] if 'HomeTeam' in row else ''
            away = row['AwayTeam'] if 'AwayTeam' in row else ''
            # Example: if home team has more successful kicks to left edge, flag as left edge mismatch
            left_kicks = kick_df[(kick_df['Team'] == home) & (kick_df['TargetZone'] == '0-20m')].shape[0]
            right_kicks = kick_df[(kick_df['Team'] == home) & (kick_df['TargetZone'] == '40m+')].shape[0]
            if left_kicks > right_kicks + 2:
                edge = 'left'
            elif right_kicks > left_kicks + 2:
                edge = 'right'
            else:
                edge = ''
            edge_mismatch_flags.append(edge)
        matches['Edge_Mismatch'] = edge_mismatch_flags
    else:
        matches['Edge_Mismatch'] = None
except Exception as e:
    print(f"[WARN] Edge mismatch calculation failed: {e}")
    matches['Edge_Mismatch'] = None

matches['Upset_Risk'] = None
matches['Betting_Line_Movement'] = None

# ==========================================================
# 6. MODEL TRAINING AND EVALUATION
# ----------------------------------------------------------
print('[DEBUG] --- MODEL TRAINING AND EVALUATION ---')

# === DATA LEAKAGE GUARD: Only use pre-match features for training ===
# Remove post-match columns from feature_cols
post_match_cols = ['HomeScore', 'AwayScore', 'Margin', 'HomeWin']
base_feature_cols = [col for col in ['Home_RecentForm', 'Away_RecentForm'] if col in matches.columns]
impact_cols = [col for col in ['HomeImpactScore', 'AwayImpactScore'] if col in matches.columns]
weather_cols = [col for col in ['Rain', 'WindSpeed', 'WindDirection', 'Temperature', 'Humidity', 'Pressure', 'CloudCover', 'DewPoint', 'UVIndex'] if col in matches.columns]
overlay_feature_cols = []
for overlay_name, (filename, _) in overlay_files.items():
    overlay_cols = [col for col in matches.columns if overlay_name in col and col not in base_feature_cols + impact_cols + weather_cols + post_match_cols]
    overlay_feature_cols.extend(overlay_cols)
feature_cols = base_feature_cols + impact_cols + weather_cols + overlay_feature_cols

# Remove any post-match columns from matches if present
matches = matches.drop(columns=[col for col in post_match_cols if col in matches.columns], errors='ignore')

model_data = matches.dropna(subset=feature_cols)
if model_data.empty:
    print('No data available for training after filtering. Please check your input data and feature engineering steps.')
    print('Debug info:')
    print('  matches columns:', matches.columns.tolist())
    print('  feature_cols:', feature_cols)
    print('  matches head:')
    print(matches.head())
    sys.exit()
X = model_data[feature_cols]
y = model_data['HomeWin']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f'[DEBUG] Feature columns used for training: {feature_cols}')
print(f'[DEBUG] Training data shape: {X_train.shape}, Test data shape: {X_test.shape}')
print(f'[DEBUG] Sample X_train:\n{X_train.head()}')
print(f'[DEBUG] Sample y_train:\n{y_train.head()}')

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
print('\n' + '='*40)
print('MODEL PERFORMANCE')
print('='*40)
print('Accuracy:', accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))
print(f'[DEBUG] Model feature importances: {clf.feature_importances_}')
print('Model training complete.')

# ==========================================================
# 7. PREDICTION OUTPUT WITH CONFIDENCE
# ----------------------------------------------------------
def predict_with_confidence(model, X):
    proba = model.predict_proba(X)
    predictions = model.predict(X)
    confidence = proba.max(axis=1)
    return predictions, confidence

def print_progress(msg, delay=1.5):
    print(msg, flush=True)
    time.sleep(delay)

# --- Helper: Generate upcoming matchups if not defined ---
if 'wkd_matches' not in globals():
    # Example: Use the last round's teams to generate matchups for the next round
    latest_year = matches['Year'].max()
    latest_round = matches[matches['Year'] == latest_year]['Round'].max()
    last_round_matches = matches[(matches['Year'] == latest_year) & (matches['Round'] == latest_round)]
    wkd_matches = list(zip(last_round_matches['HomeTeam'], last_round_matches['AwayTeam']))
    print(f'[DEBUG] wkd_matches auto-generated: {wkd_matches}')

# --- Helper: Calculate recent form for a team ---
def get_recent_form(team, round_num, year, window=3):
    # Use only matches before the given round in the given year
    team_matches = matches[(matches['Year'] == year) & (matches['Round'] < round_num) & ((matches['HomeTeam'] == team) | (matches['AwayTeam'] == team))]
    if team_matches.empty:
        return np.nan
    # Use HomeScore if team is home, AwayScore if away
    scores = []
    for _, row in team_matches.tail(window).iterrows():
        if row['HomeTeam'] == team:
            scores.append(row['HomeScore'])
        else:
            scores.append(row['AwayScore'])
    return np.mean(scores) if scores else np.nan

if __name__ == "__main__":
    print_progress("[PREDICTOR] Initialising prediction model...", 2)
    print_progress("[PREDICTOR] Loading normalised data...", 2)
    print_progress("[PREDICTOR] Running feature engineering...", 2)
    print_progress("[PREDICTOR] Running model inference...", 3)
    print_progress("[PREDICTOR] Saving predictions to outputs...", 2)
    print_progress("[PREDICTOR] Prediction step complete!", 1)

print('\n' + '='*40)
print('SAMPLE PREDICTIONS')
print('='*40)
preds, confs = predict_with_confidence(clf, X_test)
for i, (pred, conf) in enumerate(zip(preds, confs)[:5]):
    print(f'Prediction: {"Home Win" if pred else "Away Win"}, Confidence: {conf:.2f}')

# When predicting for fixtures, use only pre-match features
if fixtures is not None and 'HomeImpactScore' in fixtures.columns and 'AwayImpactScore' in fixtures.columns:
    for i, row in fixtures.iterrows():
        X_pred = pd.DataFrame([[row['Home_RecentForm'] if 'Home_RecentForm' in row else np.nan,
                               row['Away_RecentForm'] if 'Away_RecentForm' in row else np.nan,
                               row['HomeImpactScore'],
                               row['AwayImpactScore']]],
                             columns=feature_cols)
        pred, conf = predict_with_confidence(clf, X_pred)
        print(f"{row['HomeTeam']} vs {row['AwayTeam']}: Predicted winner: {row['HomeTeam'] if pred[0] == 1 else row['AwayTeam']}, Confidence: {conf[0]:.2f}")

# When predicting for new matches, use only pre-match features
results = []
for match in wkd_matches:
    home, away = match
    year = matches['Year'].max()
    round_num = matches[matches['Year'] == year]['Round'].max() + 1
    home_recent = get_recent_form(home, round_num, year)
    away_recent = get_recent_form(away, round_num, year)
    # Prepare feature vector with only pre-match features
    X_pred = pd.DataFrame([[home_recent, away_recent]], columns=base_feature_cols)
    pred, conf = predict_with_confidence(clf, X_pred)
    results.append({
        'HomeTeam': home,
        'AwayTeam': away,
        'PredictedWinner': home if pred[0] == 1 else away,
        'Confidence': conf[0]
    })

predictions_df = pd.DataFrame(results)
# At the end, export predictions to outputs directory for consistency
output_predictions_path = os.path.join(outputs_root, 'nrl_predictions_output.csv')
print('[DEBUG] --- EXPORTING PREDICTIONS ---')
print(f'[DEBUG] Predictions DataFrame:\n{predictions_df.head()}')
print(f'[DEBUG] Exporting predictions to {output_predictions_path}')
predictions_df.to_csv(output_predictions_path, index=False)
print(f'Predictions exported to {output_predictions_path}')

# ==========================================================
# 9. ONGOING USE WITH NEW DATA
# ----------------------------------------------------------
# To use this script on an ongoing basis:
# 1. Update your data files (CSV, etc.) with the latest matches and player stats.
# 2. Rerun the script from the top. The feature extraction, model training, and prediction steps will automatically use the new data.
# 3. Export new predictions as shown above.
# 4. (Optional) Save and reload your trained model to avoid retraining each time.

# Example for saving/loading model (if using joblib or pickle):
# import joblib
# joblib.dump(clf, 'nrl_titan_model.joblib')
# clf = joblib.load('nrl_titan_model.joblib')

print('[DEBUG] --- SCRIPT FINISHED ---')
print('Script finished.')
