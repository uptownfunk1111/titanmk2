"""
Player Injury Impact Analysis
- Tracks and analyzes player injuries during a match
- Evaluates impact on team performance and adjusts predictions
"""
import pandas as pd
import os

def analyze_injuries(injury_file, player_impact_file, output_file):
    injuries = pd.read_csv(injury_file)
    impact_scores = pd.read_csv(player_impact_file)
    # Ensure required columns exist
    if 'Player' not in injuries.columns or 'Player' not in impact_scores.columns:
        print("[ERROR] 'Player' column missing in input files.")
        return
    if 'ImpactScore' not in impact_scores.columns:
        print("[ERROR] 'ImpactScore' column missing in player impact file.")
        return
    # If Severity is missing, default to 1
    if 'Severity' not in injuries.columns:
        injuries['Severity'] = 1
    # Merge and calculate impact loss
    merged = injuries.merge(impact_scores[['Player', 'ImpactScore']], on='Player', how='left')
    merged['ImpactScore'] = merged['ImpactScore'].fillna(0)
    merged['ImpactLoss'] = merged['ImpactScore'] * merged['Severity']
    merged.to_csv(output_file, index=False)
    print(f"[SUCCESS] Injury impact analysis saved to {output_file}")
    # Print team summary
    if 'Team' in merged.columns:
        team_summary = merged.groupby('Team')['ImpactLoss'].sum().reset_index()
        print("[INFO] Team impact loss summary:")
        print(team_summary)
    else:
        print("[INFO] No 'Team' column found for team summary.")

if __name__ == "__main__":
    # Output to the main outputs directory at the project root
    outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'outputs'))
    os.makedirs(outputs_dir, exist_ok=True)
    injury_file = os.path.join(outputs_dir, 'injury_reports.csv')
    player_impact_file = os.path.join(outputs_dir, 'player_impact_scores_2019_2025.csv')
    output_file = os.path.join(outputs_dir, 'injury_impact_analysis.csv')
    analyze_injuries(injury_file, player_impact_file, output_file)
