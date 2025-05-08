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
                        # --- Extract home/away teams from game_key ---
                        # Example game_key: '2025-1-Raiders-v-Warriors'
                        try:
                            parts = game_key.split('-')
                            # Find the index of 'v' (or 'vs')
                            v_idx = None
                            for i, p in enumerate(parts):
                                if p.lower() in ('v', 'vs'):
                                    v_idx = i
                                    break
                            if v_idx is not None and v_idx > 1 and v_idx < len(parts)-1:
                                home_team = '-'.join(parts[2:v_idx])
                                away_team = '-'.join(parts[v_idx+1:])
                            else:
                                home_team = ''
                                away_team = ''
                        except Exception as e:
                            print(f"[WARN] Could not parse teams from game_key '{game_key}': {e}")
                            home_team = ''
                            away_team = ''
                        # Assign team to each player: first N are home, next N are away
                        n_players = len(player_data)
                        # Heuristic: if 34 or 36, split in half; else, fallback to jersey number (1-17 home, 18+ away)
                        split_idx = n_players // 2 if n_players >= 30 else None
                        for idx, player in enumerate(player_data):
                            row = {'Year': year, 'Round': round_key, 'MatchKey': game_key}
                            row.update(player)
                            # Assign team
                            team = ''
                            if split_idx is not None:
                                team = home_team if idx < split_idx else away_team
                            else:
                                # Try to use jersey number if available
                                try:
                                    num = int(player.get('Number', 0))
                                    if 1 <= num <= 17:
                                        team = home_team
                                    elif num >= 18:
                                        team = away_team
                                    else:
                                        team = ''
                                except:
                                    team = ''
                            row['Team'] = team
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

# Convert Round to int, warn if not possible
try:
    df['Round'] = df['Round'].astype(int)
except Exception as e:
    print(f"[WARN] Could not convert all Round values to int: {e}")
    # Try to coerce, set errors to -1
    import numpy as np
    df['Round'] = pd.to_numeric(df['Round'], errors='coerce').fillna(-1).astype(int)

# Debug: print unique values and types for Round and Team
print("[DEBUG] Unique Round values and types in player stats:")
print(df['Round'].value_counts(dropna=False).sort_index())
print(f"[DEBUG] Team column unique values: {df['Team'].unique()}")

# Print sample of rows with missing/invalid Team or Round
invalid_rows = df[(df['Team'] == '') | (df['Round'] == -1)]
if not invalid_rows.empty:
    print("[WARN] Sample rows with missing/invalid Team or Round:")
    print(invalid_rows.head())

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
