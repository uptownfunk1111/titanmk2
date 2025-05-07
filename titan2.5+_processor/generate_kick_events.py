"""
Generate a scaffolded kick_events.csv for NRL matches
- Uses available match and player data to create a base for kick event annotation
- Output: outputs/kick_events.csv
"""
import pandas as pd
import os
from datetime import datetime

# Paths
outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs'))
match_file = os.path.join(outputs_dir, 'all_matches_2019_2025.csv')
player_file = os.path.join(outputs_dir, 'all_players_2019_2025.csv')
kick_events_file = os.path.join(outputs_dir, 'kick_events.csv')

# Load data
matches = pd.read_csv(match_file)
players = pd.read_csv(player_file)

# Scaffold kick events: one row per match, per team, per half (for annotation)
kick_events = []
for idx, row in matches.iterrows():
    for team in [row['HomeTeam'], row['AwayTeam']]:
        for half in [1, 2]:
            kick_events.append({
                'MatchID': idx,
                'Date': row['Date'],
                'Venue': row['Venue'],
                'Team': team,
                'Opponent': row['AwayTeam'] if team == row['HomeTeam'] else row['HomeTeam'],
                'Half': half,
                'KickType': '',  # To be annotated: Bomb, Grubber, etc.
                'StartX': '',    # To be annotated
                'StartY': '',    # To be annotated
                'TargetX': '',   # To be annotated
                'TargetY': '',   # To be annotated
                'Outcome': '',   # To be annotated: DropOut, Try, etc.
                'Kicker': '',    # To be annotated
                'Pressure': '',  # To be annotated
                'Context': '',   # To be annotated (e.g., attacking/defending)
            })
kick_events_df = pd.DataFrame(kick_events)
kick_events_df.to_csv(kick_events_file, index=False)
print(f"[SUCCESS] Scaffolded kick_events.csv saved to {kick_events_file}")
