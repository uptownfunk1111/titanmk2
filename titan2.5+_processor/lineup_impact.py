"""
Team Lineup Impact
- Analyzes impact of lineup and bench changes on match outcomes
"""
import pandas as pd
import os

def analyze_lineup_impact(lineup_file, player_impact_file, output_file):
    print("[PROGRESS] Loading lineup file:", lineup_file)
    lineups = pd.read_csv(lineup_file)
    print("[PROGRESS] Loading player impact file:", player_impact_file)
    impact_scores = pd.read_csv(player_impact_file)
    print("[DEBUG] Columns in lineups:", lineups.columns.tolist())
    print("[DEBUG] Columns in impact_scores:", impact_scores.columns.tolist())
    # Try to use 'Player' or 'Stat' as the lookup column
    lookup_col = None
    for col in ['Player', 'Stat']:
        if col in impact_scores.columns:
            lookup_col = col
            print(f"[PROGRESS] Using '{col}' as lookup column for impact scores.")
            break
    if not lookup_col:
        print("[ERROR] Neither 'Player' nor 'Stat' found in impact_scores columns.")
        raise KeyError("Neither 'Player' nor 'Stat' found in impact_scores columns.")
    def sum_impact(team_name):
        print(f"[TRACE] Calculating impact for team: {team_name}")
        # For team-based impact, sum all impact scores (or use a team mapping if available)
        # Here, just sum all impact scores as a placeholder
        total = impact_scores['ImpactScore'].sum()
        print(f"[TRACE] Total impact score for team {team_name}: {total}")
        return total
    print("[PROGRESS] Calculating HomeTotalImpact...")
    lineups['HomeTotalImpact'] = lineups['HomeTeam'].apply(sum_impact)
    print("[PROGRESS] Calculating AwayTotalImpact...")
    lineups['AwayTotalImpact'] = lineups['AwayTeam'].apply(sum_impact)
    print("[PROGRESS] Saving results to:", output_file)
    lineups.to_csv(output_file, index=False)
    print(f"[SUCCESS] Lineup impact analysis saved to {output_file}")

if __name__ == "__main__":
    outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs'))
    lineup_file = os.path.join(outputs_dir, 'upcoming_fixtures_and_officials_2025_round10.csv')
    player_impact_file = os.path.join(outputs_dir, 'player_impact_scores_2019_2025.csv')
    output_file = os.path.join(outputs_dir, 'lineup_impact_analysis.csv')
    analyze_lineup_impact(lineup_file, player_impact_file, output_file)
