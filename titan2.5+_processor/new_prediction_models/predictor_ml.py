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

# ==========================================================
# 2. DATA LOADING
# ----------------------------------------------------------
# Load match, player, and detailed match data.
matches = pd.read_csv(r'C:\Users\slangston1\TITAN\titan2.5+_processor\outputs\all_matches_2019_2025.csv')
try:
    players = pd.read_csv(r'C:\Users\slangston1\TITAN\titan2.5+_processor\outputs\all_players_2019_2025.csv')
except Exception:
    players = pd.DataFrame()
try:
    detailed_matches = pd.read_csv(r'C:\Users\slangston1\TITAN\titan2.5+_processor\outputs\all_detailed_matches_2019_2025.csv')
except Exception:
    detailed_matches = pd.DataFrame()

# Load player impact scores
impact_scores_path = os.path.abspath(r'C:\Users\slangston1\TITAN\outputs\player_impact_scores_2019_2025.csv')
if os.path.exists(impact_scores_path):
    impact_scores = pd.read_csv(impact_scores_path)
    impact_score_dict = dict(zip(impact_scores['Stat'], impact_scores['ImpactScore']))
else:
    impact_scores = None
    impact_score_dict = {}

# Load upcoming fixtures and team lists for prediction
fixtures_path = os.path.abspath(r'C:\Users\slangston1\TITAN\outputs\upcoming_fixtures_and_officials_2025_round10.csv')
if os.path.exists(fixtures_path):
    fixtures = pd.read_csv(fixtures_path)
else:
    fixtures = None

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
    locals()[df_name] = df

# ==========================================================
# 3. FEATURE ENGINEERING
# ----------------------------------------------------------
# Aggregate player stats, calculate recent form, margin, etc.
if not players.empty and 'Team' in players.columns and 'Year' in players.columns and 'Round' in players.columns:
    agg_cols = [col for col in players.columns if col not in ['Year', 'Round', 'Team', 'Player']]
    player_agg = players.groupby(['Year', 'Round', 'Team'])[agg_cols].sum().reset_index()
    # Merge for home and away teams
    matches = matches.merge(
        player_agg.rename(lambda x: f'Home_{x}' if x not in ['Year', 'Round', 'Team'] else x, axis=1),
        left_on=['Year', 'Round', 'HomeTeam'], right_on=['Year', 'Round', 'Team'], how='left'
    ).drop('Team', axis=1)
    matches = matches.merge(
        player_agg.rename(lambda x: f'Away_{x}' if x not in ['Year', 'Round', 'Team'] else x, axis=1),
        left_on=['Year', 'Round', 'AwayTeam'], right_on=['Year', 'Round', 'Team'], how='left', suffixes=('', '_away')
    ).drop('Team', axis=1)

matches['HomeWin'] = (matches['HomeScore'] > matches['AwayScore']).astype(int)
matches['Margin'] = matches['HomeScore'] - matches['AwayScore']
matches = matches.sort_values(['Year', 'Round'])
for team_col, score_col, new_col in [
    ('HomeTeam', 'HomeScore', 'Home_RecentForm'),
    ('AwayTeam', 'AwayScore', 'Away_RecentForm')
]:
    matches[new_col] = matches.groupby(team_col)[score_col].transform(lambda x: x.rolling(window=3, min_periods=1).mean())

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
matches['Upset_Risk'] = None
matches['Edge_Mismatch'] = None
matches['Betting_Line_Movement'] = None

# ==========================================================
# 6. MODEL TRAINING AND EVALUATION
# ----------------------------------------------------------
# Ensure 'HomeImpactScore' and 'AwayImpactScore' exist in matches
for col in ['HomeImpactScore', 'AwayImpactScore']:
    if col not in matches.columns:
        matches[col] = np.nan

# Dynamically set feature columns based on available columns
base_feature_cols = ['Home_RecentForm', 'Away_RecentForm', 'Margin']
impact_cols = [col for col in ['HomeImpactScore', 'AwayImpactScore'] if col in matches.columns]
feature_cols = base_feature_cols + impact_cols

model_data = matches.dropna(subset=feature_cols + ['HomeWin'])
if model_data.empty:
    print('No data available for training after filtering. Please check your input data and feature engineering steps.')
    exit()
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
predictions_df.to_csv('nrl_predictions_output.csv', index=False)
print('Predictions exported to nrl_predictions_output.csv')

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
