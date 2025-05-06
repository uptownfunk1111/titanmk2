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
    # Placeholder: join on Player, calculate team impact loss
    merged = injuries.merge(impact_scores, on='Player', how='left')
    merged['ImpactLoss'] = merged['ImpactScore'] * merged.get('Severity', 1)
    merged.to_csv(output_file, index=False)
    print(f"[SUCCESS] Injury impact analysis saved to {output_file}")

if __name__ == "__main__":
    outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs'))
    injury_file = os.path.join(outputs_dir, 'injury_reports.csv')
    player_impact_file = os.path.join(outputs_dir, 'player_impact_scores_2019_2025.csv')
    output_file = os.path.join(outputs_dir, 'injury_impact_analysis.csv')
    analyze_injuries(injury_file, player_impact_file, output_file)
