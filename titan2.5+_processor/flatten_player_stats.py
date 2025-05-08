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
        print(f"[WARN] No valid PlayerStats in {stats_path}")
        continue
    for entry in player_stats:
        if str(year) not in entry:
            continue
        for round_data in entry[str(year)]:
            for round_key, matches in round_data.items():
                if not isinstance(matches, list):
                    continue
                for match_dict in matches:
                    if not isinstance(match_dict, dict):
                        continue
                    for game_key, player_data in match_dict.items():
                        for idx, player in enumerate(player_data):
                            row = {'Year': year, 'Round': round_key, 'MatchKey': game_key}
                            row.update(player)
                            all_rows.append(row)

if not all_rows:
    print("[FATAL] No player stats found for any year. Writing empty CSV with headers.")
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    default_columns = ['Year', 'Round', 'MatchKey', 'Name', 'Number', 'Position', 'Mins Played', 'Total Points']
    try:
        pd.DataFrame(columns=default_columns).to_csv(OUTPUT_CSV, index=False)
        pd.DataFrame(columns=default_columns).to_csv(OUTPUT_2025, index=False)
        print(f"[WARN] Wrote empty player stats CSV with headers to {OUTPUT_CSV} and {OUTPUT_2025}")
    except PermissionError as e:
        print(f"[ERROR] Permission denied when writing CSV: {e}")
    exit(0)

os.makedirs(OUTPUTS_DIR, exist_ok=True)
df = pd.DataFrame(all_rows)

# Clean all stat columns: replace '-', '', 'N/A', 'null' with 0, and convert to numeric
stat_cols = [col for col in df.columns if col not in ['Year', 'Round', 'MatchKey', 'Name', 'Number', 'Position', 'Team', 'Player', 'Opposition']]
df[stat_cols] = df[stat_cols].replace(['-', '', 'N/A', 'null'], 0)
for col in stat_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

try:
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"[SUCCESS] Flattened all player stats to {OUTPUT_CSV} ({len(df)} rows)")
except PermissionError as e:
    print(f"[ERROR] Permission denied when writing {OUTPUT_CSV}: {e}")

# After writing all_players_2019_2025.csv, also write player_stats_2025.csv for just 2025 data
if not df.empty:
    df_2025 = df[df['Year'] == 2025]
    if df_2025.empty:
        df.head(0).to_csv(OUTPUT_2025, index=False)
        print(f"[WARN] No player stats for 2025. Wrote empty CSV with headers to {OUTPUT_2025}")
    else:
        try:
            df_2025.to_csv(OUTPUT_2025, index=False)
            print(f"[SUCCESS] Wrote player stats for 2025 to {OUTPUT_2025} ({len(df_2025)} rows)")
        except PermissionError as e:
            print(f"[ERROR] Permission denied when writing {OUTPUT_2025}: {e}")
