"""
Opponent Analysis and Adaptation
- Analyzes opponent strategies and historical performance
"""
import pandas as pd
import os

def main():
    # Locate the outputs directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.abspath(os.path.join(base_dir, '..', 'outputs'))
    matches_path = os.path.join(outputs_dir, 'normalised_all_matches_2019_2025.csv')
    if not os.path.exists(matches_path):
        print(f"[ERROR] Could not find {matches_path}")
        return
    df = pd.read_csv(matches_path)
    # Example: Calculate opponent win rates and average margin for each team per round
    features = []
    for year in sorted(df['year'].unique()):
        for round_num in sorted(df[df['year'] == year]['round'].unique()):
            round_matches = df[(df['year'] == year) & (df['round'] < round_num)]
            for team in pd.concat([df['hometeam'], df['awayteam']]).unique():
                team_matches = round_matches[(round_matches['hometeam'] == team) | (round_matches['awayteam'] == team)]
                if len(team_matches) == 0:
                    continue
                win_count = ((team_matches['hometeam'] == team) & (team_matches['homescore'] > team_matches['awayscore'])).sum() + \
                           ((team_matches['awayteam'] == team) & (team_matches['awayscore'] > team_matches['homescore'])).sum()
                total_games = len(team_matches)
                avg_margin = team_matches.apply(lambda row: row['homescore'] - row['awayscore'] if row['hometeam'] == team else row['awayscore'] - row['homescore'], axis=1).mean()
                features.append({
                    'Year': year,
                    'Round': round_num,
                    'HomeTeam': team,
                    'Opponent_WinRate': win_count / total_games,
                    'Opponent_AvgMargin': avg_margin
                })
    features_df = pd.DataFrame(features)
    out_path = os.path.join(outputs_dir, 'opponent_analysis.csv')
    features_df.to_csv(out_path, index=False)
    print(f"[INFO] Opponent analysis features saved to {out_path}")

if __name__ == "__main__":
    main()
