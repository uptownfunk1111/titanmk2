"""
Script to harvest and flatten player statistics for all years (2019-2025) into a single CSV.
- Loads all NRL_player_statistics_{year}.json files from data/NRL/{year}/
- Flattens and normalizes player stats into a single DataFrame
- Outputs all_players_2019_2025.csv in outputs/
"""
import os
import json
import pandas as pd

DATA_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'NRL'))
OUTPUTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs'))
OUTPUT_CSV = os.path.join(OUTPUTS_DIR, 'all_players_2019_2025.csv')
OUTPUT_2025 = os.path.join(OUTPUTS_DIR, 'player_stats_2025.csv')
YEARS = list(range(2019, 2026))

all_rows = []
for year in YEARS:
    stats_path = os.path.join(DATA_BASE, str(year), f'NRL_player_statistics_{year}.json')
    if not os.path.exists(stats_path):
        print(f"[WARN] Player stats file not found for {year}: {stats_path}")
        continue
    with open(stats_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    player_stats = data.get('PlayerStats', [])
    if not player_stats or not isinstance(player_stats, list):
        print(f"[WARN] No PlayerStats found for {year}")
        continue
    # The structure is: PlayerStats: [ {year: [ {round: [ {match_key: [player_dicts]} ] } ] } ]
    year_block = player_stats[0].get(str(year), [])
    for round_block in year_block:
        for round_num, matches in round_block.items():
            for match in matches:
                for match_key, players in match.items():
                    for player in players:
                        row = {'Year': year, 'Round': int(round_num), 'MatchKey': match_key}
                        row.update(player)
                        all_rows.append(row)

if not all_rows:
    print("[FATAL] No player stats found for any year. Writing empty CSV with headers.")
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    # Define a default header (customize as needed)
    default_columns = ['Year', 'Round', 'MatchKey', 'Name', 'Number', 'Position', 'Mins Played', 'Total Points']
    pd.DataFrame(columns=default_columns).to_csv(OUTPUT_CSV, index=False)
    pd.DataFrame(columns=default_columns).to_csv(OUTPUT_2025, index=False)
    print(f"[WARN] Wrote empty player stats CSV with headers to {OUTPUT_CSV} and {OUTPUT_2025}")
    exit(0)

os.makedirs(OUTPUTS_DIR, exist_ok=True)
df = pd.DataFrame(all_rows)
df.to_csv(OUTPUT_CSV, index=False)
print(f"[SUCCESS] Flattened all player stats to {OUTPUT_CSV} ({len(df)} rows)")

# After writing all_players_2019_2025.csv, also write player_stats_2025.csv for just 2025 data
if not df.empty:
    df_2025 = df[df['Year'] == 2025]
    if df_2025.empty:
        # Write only headers if no 2025 data
        df.head(0).to_csv(OUTPUT_2025, index=False)
        print(f"[WARN] No player stats for 2025. Wrote empty CSV with headers to {OUTPUT_2025}")
    else:
        df_2025.to_csv(OUTPUT_2025, index=False)
        print(f"[SUCCESS] Wrote player stats for 2025 to {OUTPUT_2025} ({len(df_2025)} rows)")
else:
    # If df is empty, already handled above
    pass
