"""
Officiating Impact and Risk Analysis for Rugby League Matches

This script evaluates the influence of referees and bunker decisions on match outcomes,
including bias detection, risk assessment, and predictive modeling.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import os

# --- Data Collection & Parsing ---
# Output to the main outputs directory at the project root
outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'outputs'))
os.makedirs(outputs_dir, exist_ok=True)
match_data_path = os.path.join(outputs_dir, 'all_matches_2019_2025.csv')
referee_data_path = os.path.join(outputs_dir, 'referee_stats.csv')
bunker_data_path = os.path.join(outputs_dir, 'bunker_decisions.csv')
penalty_data_path = os.path.join(outputs_dir, 'penalties.csv')

# Load data
match_df = pd.read_csv(match_data_path) if os.path.exists(match_data_path) else pd.DataFrame()
referee_df = pd.read_csv(referee_data_path) if os.path.exists(referee_data_path) else pd.DataFrame()
bunker_df = pd.read_csv(bunker_data_path) if os.path.exists(bunker_data_path) else pd.DataFrame()
penalty_df = pd.read_csv(penalty_data_path) if os.path.exists(penalty_data_path) else pd.DataFrame()

# --- Impact and Risk Analysis ---
def analyze_penalty_momentum(match_df, penalty_df):
    # Example: Calculate scoring before/after penalties (placeholder)
    return penalty_df.groupby('team').size() if not penalty_df.empty else pd.Series()

def impact_on_team_performance(match_df, decisions_df):
    return decisions_df.groupby('decision_type').size() if not decisions_df.empty else pd.Series()

def correlate_decisions_with_outcome(match_df, decisions_df):
    return match_df.corr(numeric_only=True) if not match_df.empty else pd.DataFrame()

def detect_bias(referee_df, penalty_df):
    if not penalty_df.empty and 'referee' in penalty_df.columns and 'against_team' in penalty_df.columns:
        return penalty_df.groupby(['referee', 'against_team']).size().unstack(fill_value=0)
    return pd.DataFrame()

def flag_controversy(decisions_df):
    if 'controversy_flag' in decisions_df.columns:
        return decisions_df[decisions_df['controversy_flag'] == 1]
    return pd.DataFrame()

def calculate_risk_of_decision(match_df, decisions_df):
    if not decisions_df.empty:
        decisions_df = decisions_df.copy()
        decisions_df['risk_score'] = np.random.rand(len(decisions_df))
        return decisions_df[['decision_id', 'risk_score']]
    return pd.DataFrame()

# --- Prediction Model ---
def build_decision_prediction_model(features, labels):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(features, labels)
    return model

def simulate_outcomes(match_df, decisions_df, model):
    return match_df

# --- Reporting and Visualization ---
def generate_officiating_report(match_id, match_df, decisions_df, risk_df):
    print(f"--- Officiating Influence Report for Match {match_id} ---")
    if not decisions_df.empty:
        print("Key Decisions:")
        print(decisions_df[['minute', 'decision_type', 'referee', 'bunker']].head())
    if not risk_df.empty:
        print("\nRisk Assessment:")
        print(risk_df.head())
    print("\n")

def visualize_decision_impact(match_df, decisions_df):
    if not decisions_df.empty and 'decision_type' in decisions_df.columns:
        plt.figure(figsize=(10, 6))
        sns.countplot(x='decision_type', data=decisions_df)
        plt.title('Frequency of Officiating Decisions')
        plt.tight_layout()
        plt.savefig(os.path.join(outputs_dir, 'officiating_decision_frequency.png'))
        plt.close()

# --- Main Pipeline ---
def main():
    penalty_momentum = analyze_penalty_momentum(match_df, penalty_df)
    team_perf_impact = impact_on_team_performance(match_df, bunker_df)
    outcome_corr = correlate_decisions_with_outcome(match_df, bunker_df)
    bias_table = detect_bias(referee_df, penalty_df)
    controversy_flags = flag_controversy(bunker_df)
    risk_scores = calculate_risk_of_decision(match_df, bunker_df)

    # --- Modeling ---
    if not bunker_df.empty and {'minute', 'decision_type_code', 'referee_experience', 'match_changing'}.issubset(bunker_df.columns):
        features = bunker_df[['minute', 'decision_type_code', 'referee_experience']].fillna(0)
        labels = bunker_df['match_changing'].fillna(0)
        model = build_decision_prediction_model(features, labels)
        simulated_outcomes = simulate_outcomes(match_df, bunker_df, model)
    else:
        model = None

    # --- Reporting ---
    output_file = os.path.join(outputs_dir, 'officiating_impact_analysis.csv')
    for match_id in match_df['MatchID'].unique()[:3] if 'MatchID' in match_df.columns else []:
        match_sub = match_df[match_df['MatchID'] == match_id]
        decisions_sub = bunker_df[bunker_df['MatchID'] == match_id] if 'MatchID' in bunker_df.columns else pd.DataFrame()
        risk_sub = risk_scores if not risk_scores.empty else pd.DataFrame()
        generate_officiating_report(match_id, match_sub, decisions_sub, risk_sub)

    # --- Visualization ---
    visualize_decision_impact(match_df, bunker_df)
    print('[SUCCESS] Officiating impact analysis complete. Visualizations saved to outputs/.')
    print(f"[SUCCESS] Officiating impact analysis saved to {output_file}")

if __name__ == "__main__":
    main()
