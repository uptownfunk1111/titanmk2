"""
TITAN Match Insights Generator
Generates a CSV with detailed match insights for each upcoming NRL fixture, including model tips, probabilities, tactical overlays, and contextual features.
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime

# Paths (update as needed)
FIXTURES_PATH = os.path.abspath('outputs/upcoming_fixtures_and_officials_2025_round10.csv')
IMPACT_SCORES_PATH = os.path.abspath('outputs/player_impact_scores_2019_2025.csv')
PLAYER_STATS_PATH = os.path.abspath('titan2.5+_processor/outputs/all_players_2019_2025.csv')
PREDICTIONS_PATH = os.path.abspath('nrl_predictions_output.csv')
OUTPUT_PATH = os.path.abspath('outputs/titan_match_insights_round10.csv')

# Load data
def load_data():
    fixtures = pd.read_csv(FIXTURES_PATH)
    impact_scores = pd.read_csv(IMPACT_SCORES_PATH) if os.path.exists(IMPACT_SCORES_PATH) else None
    player_stats = pd.read_csv(PLAYER_STATS_PATH)
    predictions = pd.read_csv(PREDICTIONS_PATH) if os.path.exists(PREDICTIONS_PATH) else None
    return fixtures, impact_scores, player_stats, predictions

# Placeholder tactical/contextual functions
def get_edge_mismatch(row):
    # Try to pull from kick report if available
    try:
        kick_report_path = os.path.abspath(f'outputs/kick_report_{datetime.now().date()}.csv')
        if os.path.exists(kick_report_path):
            kick_df = pd.read_csv(kick_report_path)
            left_kicks = kick_df[(kick_df['Team'] == row['HomeTeam']) & (kick_df['TargetZone'] == '0-20m')].shape[0]
            right_kicks = kick_df[(kick_df['Team'] == row['HomeTeam']) & (kick_df['TargetZone'] == '40m+')].shape[0]
            if left_kicks > right_kicks + 2:
                return 'Left edge mismatch'
            elif right_kicks > left_kicks + 2:
                return 'Right edge mismatch'
    except Exception as e:
        print(f"[WARN] Could not load edge mismatch: {e}")
    return ''

def get_ktm(row):
    return "Bomb threat, short-side grubber risk"  # Placeholder

def get_back3_pressure(row):
    return "High risk for Home, moderate for Away"  # Placeholder

def get_momentum_trend(row):
    return np.random.choice(["Surging", "Fading", "Volatile", "Grinding wins"])  # Placeholder

def get_coach_impact(row):
    return "Bellamy structured control"  # Placeholder

def get_lineup_integrity(row):
    return "✅ Fully confirmed"  # Placeholder

def get_ref_bunker_risk(row):
    # Try to pull from referee risk report if available
    try:
        ref_risk_path = os.path.abspath('outputs/referee_risk_report.csv')
        if os.path.exists(ref_risk_path):
            ref_risk_df = pd.read_csv(ref_risk_path)
            ref_row = ref_risk_df[(ref_risk_df['Match'].str.contains(row['HomeTeam'], case=False, na=False)) & (ref_risk_df['Match'].str.contains(row['AwayTeam'], case=False, na=False))]
            if not ref_row.empty:
                return f"{ref_row.iloc[0].get('Referee','')} ({ref_row.iloc[0].get('RiskTier','')})"
    except Exception as e:
        print(f"[WARN] Could not load referee risk: {e}")
    return ''

def get_weather_impact(row):
    return "Dry track"  # Placeholder

def get_upset_risk(row):
    return np.random.choice(["Low", "Medium", "High"])  # Placeholder

def get_speculative_overlay(row):
    return "No major leaks"  # Placeholder

def get_final_confidence(row):
    return round(np.random.uniform(7, 10), 1)  # Placeholder

def get_score_prediction(row):
    return "Storm 26–18"  # Placeholder

def get_key_matchup(row):
    return "Papenhuyzen vs Savage counter-attack"  # Placeholder

# Main generator
def generate_match_insights():
    fixtures, impact_scores, player_stats, predictions = load_data()
    insights = []
    for i, row in fixtures.iterrows():
        match_fixture = f"{row['HomeTeam']} vs {row['AwayTeam']}"
        venue_time = f"{row['Venue']}, {row['Date']}" if 'Venue' in row and 'Date' in row else ''
        # Model tip and win probability
        if predictions is not None:
            pred_row = predictions[(predictions['HomeTeam'] == row['HomeTeam']) & (predictions['AwayTeam'] == row['AwayTeam'])]
            if not pred_row.empty:
                model_tip = pred_row.iloc[0]['PredictedWinner']
                ml_win_prob = f"{int(pred_row.iloc[0]['Confidence']*100)}% – {100-int(pred_row.iloc[0]['Confidence']*100)}%"
            else:
                model_tip = ''
                ml_win_prob = ''
        else:
            model_tip = ''
            ml_win_prob = ''
        insights.append({
            "Match Fixture": match_fixture,
            "Venue & Time": venue_time,
            "Model Tip": model_tip,
            "ML Win Probability": ml_win_prob,
            "Edge Mismatch": get_edge_mismatch(row),
            "Kick Target Mapping (KTM)": get_ktm(row),
            "Back 3 Pressure Analysis": get_back3_pressure(row),
            "Momentum Trend": get_momentum_trend(row),
            "Coach Impact (Model)": get_coach_impact(row),
            "Line-up Integrity Check": get_lineup_integrity(row),
            "Referee Assigned": row['Referee'] if 'Referee' in row else '',
            "Ref/Bunker Risk": get_ref_bunker_risk(row),
            "Weather Impact": get_weather_impact(row),
            "Upset Risk Score": get_upset_risk(row),
            "Speculative Overlay": get_speculative_overlay(row),
            "Final Confidence Rating": get_final_confidence(row),
            "User Tip (if different)": '',
            "Score Prediction (optional)": get_score_prediction(row),
            "Key Matchup to Watch": get_key_matchup(row)
        })
    df = pd.DataFrame(insights)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Match insights exported to {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_match_insights()
