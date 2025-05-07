"""
This script generates 'This Week's Tips' for the upcoming NRL round using:
- Latest team lists
- Player impact scores
- Official/fixture data
- (Optionally) weather, coach, and referee risk overlays

Outputs a table with:
- Home/Away teams
- Recommended tip
- % chance of win
- Confidence (high/medium/low)
- Chance of upset
- Referee risk
- Edge mismatches
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime
import subprocess
import argparse

# --- CONFIG ---
outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs'))
teamlists_path = os.path.join(outputs_dir, f'NRL_teamlists_{datetime.now().date()}.json')
impact_scores_path = os.path.join(outputs_dir, 'player_impact_scores_2019_2025.csv')
fixtures_path = os.path.join(outputs_dir, f'upcoming_fixtures_and_officials_{datetime.now().year}_round10.csv')
model_path = os.path.join(outputs_dir, 'nrl_titan_model.joblib')

# --- LOAD DATA ---
print(f"[INFO] Loading team lists: {teamlists_path}")
print(f"[INFO] Loading impact scores: {impact_scores_path}")
print(f"[INFO] Loading fixtures: {fixtures_path}")
try:
    import json
    with open(teamlists_path, 'r', encoding='utf-8') as f:
        teamlists = json.load(f)['matches']
except Exception as e:
    print(f"[FATAL] Could not load team lists: {e}")
    teamlists = []
try:
    impact_scores = pd.read_csv(impact_scores_path)
    impact_score_dict = dict(zip(impact_scores['Stat'], impact_scores['ImpactScore']))
except Exception as e:
    print(f"[FATAL] Could not load impact scores: {e}")
    impact_score_dict = {}
try:
    fixtures = pd.read_csv(fixtures_path)
except Exception as e:
    print(f"[FATAL] Could not load fixtures: {e}")
    fixtures = pd.DataFrame()

# --- LOAD TRAINED MODEL ---
try:
    import joblib
    clf = joblib.load(model_path)
    print(f"[INFO] Loaded trained model from {model_path}")
except Exception as e:
    print(f"[WARN] Could not load trained model: {e}")
    clf = None

# --- CALCULATE TEAM IMPACT SCORES ---
def calc_team_impact(team_list, impact_score_dict):
    # Placeholder: sum all stat importances for each player (proxy)
    if not team_list:
        return 0.0
    return len(team_list) * sum(impact_score_dict.values())

# --- GENERATE TIPS TABLE ---
results = []
for i in range(0, len(teamlists), 2):
    try:
        match1 = teamlists[i]
        match2 = teamlists[i+1] if i+1 < len(teamlists) else None
        home_team = match1['matchup'].split(' v ')[0]
        away_team = match1['matchup'].split(' v ')[-1]
        home_list = match1['team_list']
        away_list = match2['team_list'] if match2 else []
        home_impact = calc_team_impact(home_list, impact_score_dict)
        away_impact = calc_team_impact(away_list, impact_score_dict)
        margin = home_impact - away_impact
        win_prob = 0.5 + np.tanh(margin/100) * 0.5  # crude proxy
        confidence = 'high' if abs(margin) > 50 else 'medium' if abs(margin) > 20 else 'low'
        upset_chance = 1 - win_prob if win_prob > 0.5 else win_prob
        # Referee risk and edge mismatch overlays
        referee = ''
        risk = ''
        edge = ''
        # Try to pull from officiating and kick mapping outputs if available
        try:
            ref_risk_path = os.path.join(outputs_dir, 'referee_risk_report.csv')
            if os.path.exists(ref_risk_path):
                ref_risk_df = pd.read_csv(ref_risk_path)
                ref_row = ref_risk_df[(ref_risk_df['Match'].str.contains(home_team, case=False, na=False)) & (ref_risk_df['Match'].str.contains(away_team, case=False, na=False))]
                if not ref_row.empty:
                    referee = ref_row.iloc[0].get('Referee', '')
                    risk = ref_row.iloc[0].get('RiskTier', '')
        except Exception as e:
            print(f"[WARN] Could not load referee risk: {e}")
        try:
            kick_report_path = os.path.join(outputs_dir, f'kick_report_{datetime.now().date()}.csv')
            if os.path.exists(kick_report_path):
                kick_df = pd.read_csv(kick_report_path)
                left_kicks = kick_df[(kick_df['Team'] == home_team) & (kick_df['TargetZone'] == '0-20m')].shape[0]
                right_kicks = kick_df[(kick_df['Team'] == home_team) & (kick_df['TargetZone'] == '40m+')].shape[0]
                if left_kicks > right_kicks + 2:
                    edge = 'left'
                elif right_kicks > left_kicks + 2:
                    edge = 'right'
                else:
                    edge = ''
        except Exception as e:
            print(f"[WARN] Could not load edge mismatch: {e}")
        results.append({
            'HomeTeam': home_team,
            'AwayTeam': away_team,
            'RecommendedTip': home_team if margin > 0 else away_team,
            'WinChance': round(win_prob*100, 1),
            'Confidence': confidence,
            'UpsetChance': round(upset_chance*100, 1),
            'Referee': referee,
            'RefereeRisk': risk,
            'EdgeMismatch': edge
        })
    except Exception as e:
        print(f"[WARN] Failed to process match: {e}")

tips_df = pd.DataFrame(results)
output_path = os.path.join(outputs_dir, f'this_weeks_tips_{datetime.now().date()}.csv')
tips_df.to_csv(output_path, index=False)
print(f"[SUCCESS] This week's tips saved to {output_path}")
print(tips_df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--speculative', action='store_true', help='Run speculative data sweep after tips')
    args = parser.parse_args()
    if args.speculative:
        print("[INFO] Running speculative data sweep...")
        subprocess.run([sys.executable, "speculative_data_sweep.py"])
