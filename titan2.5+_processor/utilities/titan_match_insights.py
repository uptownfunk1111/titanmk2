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
    return "Left edge: Munster vs rookie edge"  # Placeholder

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
    return "Penalty swing risk"  # Placeholder

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
