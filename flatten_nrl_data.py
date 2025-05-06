import os
import json
import pandas as pd

def flatten_all_nrl_fixtures(input_base_dir, output_csv_path, years=range(2019, 2026)):
    all_matches = []
    for year in years:
        json_path = os.path.join(input_base_dir, 'NRL', str(year), f'NRL_fixtures_{year}.json')
        if not os.path.exists(json_path):
            print(f"[WARN] No fixture file found for {year}: {json_path}")
            continue
        with open(json_path, 'r', encoding='utf-8') as f:
            matches = json.load(f)
        print(f"[INFO] Loaded {len(matches)} matches for {year}")
        for match in matches:
            # Flatten and standardize keys
            all_matches.append({
                'Year': year,
                'Round': match.get('roundNumber', match.get('round', '')),
                'HomeTeam': match.get('homeTeam', match.get('home', '')),
                'HomeScore': match.get('homeScore', match.get('home_score', '')),
                'AwayTeam': match.get('awayTeam', match.get('away', '')),
                'AwayScore': match.get('awayScore', match.get('away_score', '')),
                'Venue': match.get('venue', ''),
                'Date': match.get('date', match.get('gameDate', '')),
                'MatchCentreURL': match.get('matchCentreUrl', match.get('match_centre_url', ''))
            })
    if not all_matches:
        print("[FATAL] No matches found in any year. Exiting flattening.")
        return
    df = pd.DataFrame(all_matches)
    df.to_csv(output_csv_path, index=False)
    print(f"[SUCCESS] Flattened all matches to {output_csv_path} ({len(df)} rows)")

if __name__ == "__main__":
    # Always use titan2.5+_processor/outputs as the input/output base
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'titan2.5+_processor', 'outputs'))
    output_csv = os.path.abspath(os.path.join(base_dir, 'all_matches_2019_2025.csv'))
    flatten_all_nrl_fixtures(base_dir, output_csv)
