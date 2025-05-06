"""
Team Lineup Impact
- Analyzes impact of lineup and bench changes on match outcomes
"""
import pandas as pd
import os

def analyze_lineup_impact(lineup_file, player_impact_file, output_file):
    lineups = pd.read_csv(lineup_file)
    impact_scores = pd.read_csv(player_impact_file)
    # Placeholder: sum impact scores for each team lineup
    def sum_impact(teamlist_str):
        players = [p.strip() for p in str(teamlist_str).split(',') if p.strip()]
        return impact_scores[impact_scores['Player'].isin(players)]['ImpactScore'].sum()
    lineups['HomeTotalImpact'] = lineups['HomeTeamList'].apply(sum_impact)
    lineups['AwayTotalImpact'] = lineups['AwayTeamList'].apply(sum_impact)
    lineups.to_csv(output_file, index=False)
    print(f"[SUCCESS] Lineup impact analysis saved to {output_file}")

if __name__ == "__main__":
    outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs'))
    lineup_file = os.path.join(outputs_dir, 'upcoming_fixtures_and_officials_2025_round10.csv')
    player_impact_file = os.path.join(outputs_dir, 'player_impact_scores_2019_2025.csv')
    output_file = os.path.join(outputs_dir, 'lineup_impact_analysis.csv')
    analyze_lineup_impact(lineup_file, player_impact_file, output_file)
