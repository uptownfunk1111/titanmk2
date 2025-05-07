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

print('--- TITAN 2.5+ NRL Prediction Model: Script Started ---')

# ==========================================================
# 2. DATA LOADING
# ----------------------------------------------------------
# Use correct path for workspace compatibility
outputs_dir = os.path.join(os.path.dirname(__file__), '../outputs')
outputs_dir = os.path.abspath(outputs_dir)

# Ensure the outputs directory exists before writing output
if not os.path.exists(outputs_dir):
    os.makedirs(outputs_dir)

matches_path = os.path.join(outputs_dir, 'all_matches_2019_2025.csv')
players_path = os.path.join(outputs_dir, 'all_players_2019_2025.csv')
detailed_matches_path = os.path.join(outputs_dir, 'all_detailed_matches_2019_2025.csv')
impact_scores_path = os.path.join(outputs_dir, 'player_impact_scores_2019_2025.csv')
fixtures_path = os.path.join(outputs_dir, 'upcoming_fixtures_and_officials_2025_round10.csv')
weather_impact_path = os.path.join(outputs_dir, 'weather_impact_analysis.csv')

print('Loading data from:', outputs_dir)
print('  matches_path:', matches_path)
print('  players_path:', players_path)
print('  detailed_matches_path:', detailed_matches_path)
print('  impact_scores_path:', impact_scores_path)
print('  fixtures_path:', fixtures_path)
print('  weather_impact_path:', weather_impact_path)

try:
    matches = pd.read_csv(matches_path)
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
    print(f'Error loading matches: {e}')
    sys.exit()
try:
    players = pd.read_csv(players_path)
    print(f'Loaded players: {players.shape}')
except Exception as e:
    print(f'Error loading players: {e}')
    players = pd.DataFrame()
try:
    detailed_matches = pd.read_csv(detailed_matches_path)
    print(f'Loaded detailed_matches: {detailed_matches.shape}')
except Exception as e:
    print(f'Error loading detailed_matches: {e}')
    detailed_matches = pd.DataFrame()

if os.path.exists(impact_scores_path):
    impact_scores = pd.read_csv(impact_scores_path)
    impact_score_dict = dict(zip(impact_scores['Stat'], impact_scores['ImpactScore']))
    print(f'Loaded impact_scores: {impact_scores.shape}')
else:
    print('Impact scores file not found.')
    impact_scores = None
    impact_score_dict = {}

if os.path.exists(fixtures_path):
    fixtures = pd.read_csv(fixtures_path)
    print(f'Loaded fixtures: {fixtures.shape}')
else:
    print('Fixtures file not found.')
    fixtures = None

try:
    weather_impact = pd.read_csv(weather_impact_path)
    print(f'Loaded weather impact: {weather_impact.shape}')
    print('[DEBUG] weather_impact columns:', weather_impact.columns.tolist())
except Exception as e:
    print(f'Error loading weather impact: {e}')
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
for col in ['HomeTeam', 'AwayTeam', 'Team']:
    if col in matches.columns:
        matches[col + '_norm'] = matches[col].apply(normalize_team_name)
    if col in players.columns:
        players[col + '_norm'] = players[col].apply(normalize_team_name)

# Print diagnostics for merge keys
print('--- Merge Key Diagnostics ---')
print('matches Year dtype:', matches['Year'].dtype, 'unique:', sorted(matches['Year'].unique())[:5], '...')
print('players Year dtype:', players['Year'].dtype, 'unique:', sorted(players['Year'].unique())[:5], '...')
print('matches Round dtype:', matches['Round'].dtype, 'unique:', sorted(matches['Round'].unique())[:5], '...')
print('players Round dtype:', players['Round'].dtype, 'unique:', sorted(players['Round'].unique())[:5], '...')
print('matches HomeTeam_norm unique:', matches['HomeTeam_norm'].unique()[:5], '...')
print('players Team_norm unique:', players['Team_norm'].unique()[:5], '...')

# Merge weather features into matches on Date and Venue if available
if not weather_impact.empty and 'Date' in matches.columns and 'Venue' in matches.columns:
    matches = matches.merge(
        weather_impact[['Date', 'Venue', 'Rain', 'WindSpeed', 'WindDirection', 'Temperature', 'Humidity', 'WeatherCondition', 'Pressure', 'CloudCover', 'DewPoint', 'UVIndex']],
        on=['Date', 'Venue'], how='left', suffixes=('', '_weather')
    )
    print('[INFO] Weather features merged into matches.')
    print('[DEBUG] matches columns after weather merge:', matches.columns.tolist())

print('Data loading complete. Proceeding to feature engineering...')

# ==========================================================
# 3. FEATURE ENGINEERING
# ----------------------------------------------------------
# Aggregate player stats, calculate recent form, margin, etc.
merge_successful = False
if not players.empty and 'Team_norm' in players.columns and 'Year' in players.columns and 'Round' in players.columns:
    agg_cols = [col for col in players.columns if col not in ['Year', 'Round', 'Team', 'Player', 'Team_norm']]
    player_agg = players.groupby(['Year', 'Round', 'Team_norm'])[agg_cols].sum().reset_index()
    print('player_agg shape:', player_agg.shape)
    print('player_agg head:')
    print(player_agg.head())
    # Merge for home and away teams using normalized keys
    matches_before_merge = matches.copy()
    matches = matches.merge(
        player_agg.rename(lambda x: f'Home_{x}' if x not in ['Year', 'Round', 'Team_norm'] else x, axis=1),
        left_on=['Year', 'Round', 'HomeTeam_norm'], right_on=['Year', 'Round', 'Team_norm'], how='left'
    ).drop('Team_norm', axis=1)
    matches = matches.merge(
        player_agg.rename(lambda x: f'Away_{x}' if x not in ['Year', 'Round', 'Team_norm'] else x, axis=1),
        left_on=['Year', 'Round', 'AwayTeam_norm'], right_on=['Year', 'Round', 'Team_norm'], how='left', suffixes=('', '_away')
    ).drop('Team_norm', axis=1)
    print('matches shape after merge:', matches.shape)
    print('matches head after merge:')
    print(matches.head())
    if matches.shape[0] == 0:
        print('WARNING: Merge resulted in empty matches DataFrame. Reverting to original matches data.')
        matches = matches_before_merge
    else:
        merge_successful = True

# Always perform feature engineering, even if merge fails
matches['HomeWin'] = (matches['HomeScore'] > matches['AwayScore']).astype(int)
matches['Margin'] = matches['HomeScore'] - matches['AwayScore']
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

# Function to calculate team impact score from player list
def get_team_impact_score(player_list_str, player_stats_df, impact_score_dict):
    if pd.isna(player_list_str):
        return 0.0
    players = [p.strip() for p in player_list_str.split(',') if p.strip()]
    # For each player, sum their stats and multiply by stat impact
    total_score = 0.0
    for player in players:
        player_row = player_stats_df[player_stats_df['Player'] == player]
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
        # Get player list for this team/year/round
        team_players = player_stats_df[(player_stats_df['Team'] == team) & (player_stats_df['Year'] == year) & (player_stats_df['Round'] == round_num)]['Player']
        total_score = 0.0
        for player in team_players:
            player_row = player_stats_df[player_stats_df['Player'] == player]
            if not player_row.empty:
                for stat, impact in impact_score_dict.items():
                    if stat in player_row.columns:
                        total_score += player_row.iloc[0][stat] * impact
        return total_score
    matches['HomeImpactScore'] = matches.apply(
        lambda row: get_team_impact_score_train(row['HomeTeam'], row['Year'], row['Round'], players, impact_score_dict), axis=1)
    matches['AwayImpactScore'] = matches.apply(
        lambda row: get_team_impact_score_train(row['AwayTeam'], row['Year'], row['Round'], players, impact_score_dict), axis=1)

print('Feature engineering complete. matches shape:', matches.shape)

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
    kick_report_path = os.path.join(outputs_dir, 'kick_report_{}.csv'.format(pd.Timestamp.today().date()))
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
print('Beginning model training and evaluation...')

# Ensure 'HomeImpactScore' and 'AwayImpactScore' exist in matches
for col in ['HomeImpactScore', 'AwayImpactScore']:
    if col not in matches.columns:
        matches[col] = np.nan

# Dynamically set feature columns based on available columns
base_feature_cols = ['Home_RecentForm', 'Away_RecentForm', 'Margin']
impact_cols = [col for col in ['HomeImpactScore', 'AwayImpactScore'] if col in matches.columns]
weather_cols = [col for col in ['Rain', 'WindSpeed', 'WindDirection', 'Temperature', 'Humidity', 'Pressure', 'CloudCover', 'DewPoint', 'UVIndex'] if col in matches.columns]
feature_cols = base_feature_cols + impact_cols + weather_cols

model_data = matches.dropna(subset=feature_cols + ['HomeWin'])
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

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
print('\n' + '='*40)
print('MODEL PERFORMANCE')
print('='*40)
print('Accuracy:', accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))
print('Model training complete.')

# ==========================================================
# 7. PREDICTION OUTPUT WITH CONFIDENCE
# ----------------------------------------------------------
def predict_with_confidence(model, X):
    proba = model.predict_proba(X)
    predictions = model.predict(X)
    confidence = proba.max(axis=1)
    return predictions, confidence

print('\n' + '='*40)
print('SAMPLE PREDICTIONS')
print('='*40)
preds, confs = predict_with_confidence(clf, X_test)
for i, (pred, conf) in enumerate(zip(preds, confs)[:5]):
    print(f'Prediction: {"Home Win" if pred else "Away Win"}, Confidence: {conf:.2f}')

# When predicting for fixtures, use HomeImpactScore and AwayImpactScore if available
if fixtures is not None and 'HomeImpactScore' in fixtures.columns and 'AwayImpactScore' in fixtures.columns:
    for i, row in fixtures.iterrows():
        X_pred = pd.DataFrame([[row['Home_RecentForm'] if 'Home_RecentForm' in row else np.nan,
                               row['Away_RecentForm'] if 'Away_RecentForm' in row else np.nan,
                               0,  # margin unknown for future
                               row['HomeImpactScore'],
                               row['AwayImpactScore']]],
                             columns=feature_cols)
        pred, conf = predict_with_confidence(clf, X_pred)
        print(f"{row['HomeTeam']} vs {row['AwayTeam']}: Predicted winner: {row['HomeTeam'] if pred[0] == 1 else row['AwayTeam']}, Confidence: {conf[0]:.2f}")

print('Prediction output complete.')

# ==========================================================
# 8. EXPORTING PREDICTIONS AND ONGOING MODEL USE
# ----------------------------------------------------------
# Example: Export predictions for new matches to CSV
import pandas as pd

# Example: If you have a list of new matches to predict, e.g.:
wkd_matches = [
    ["Broncos", "Rabbitohs"],
    ["Sharks", "Bulldogs"],
    ["Panthers", "Eels"],
    ["Raiders", "Wests Tigers"],
    ["Cowboys", "Knights"],
    ["Storm", "Warriors"],
    ["Sea Eagles", "Roosters"],
    ["Dolphins", "Dragons"]
]

# You may need to define your teams list and a function to get features for new matches
teams = list(set(matches['HomeTeam']).union(set(matches['AwayTeam'])))

def get_recent_form(team, round_num, year):
    # Get last 3 games for the team before the given round/year
    team_matches = matches[((matches['HomeTeam'] == team) | (matches['AwayTeam'] == team)) &
                           (matches['Year'] == year) &
                           (matches['Round'] < round_num)]
    team_matches = team_matches.sort_values('Round', ascending=False).head(3)
    scores = []
    for _, row in team_matches.iterrows():
        if row['HomeTeam'] == team:
            scores.append(row['HomeScore'])
        else:
            scores.append(row['AwayScore'])
    return np.mean(scores) if scores else np.nan

results = []
for match in wkd_matches:
    home, away = match
    # Example: Use most recent year and round in your data
    year = matches['Year'].max()
    round_num = matches[matches['Year'] == year]['Round'].max() + 1
    home_recent = get_recent_form(home, round_num, year)
    away_recent = get_recent_form(away, round_num, year)
    margin = 0  # Unknown for future, set to 0 or use model
    # Prepare feature vector
    X_pred = pd.DataFrame([[home_recent, away_recent, margin]], columns=['Home_RecentForm', 'Away_RecentForm', 'Margin'])
    pred, conf = predict_with_confidence(clf, X_pred)
    results.append({
        'HomeTeam': home,
        'AwayTeam': away,
        'PredictedWinner': home if pred[0] == 1 else away,
        'Confidence': conf[0]
    })

predictions_df = pd.DataFrame(results)
# At the end, export predictions to outputs directory for consistency
output_predictions_path = os.path.join(outputs_dir, 'nrl_predictions_output.csv')
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

print('Script finished.')
