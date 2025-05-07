import os
import json
import pandas as pd

def flatten_nrl_match_data(input_base_dir, output_csv_path, years=range(2019, 2026)):
    all_matches = []
    for year in years:
        json_path = os.path.join(input_base_dir, 'NRL', str(year), f'NRL_data_{year}.json')
        if not os.path.exists(json_path):
            print(f"[WARN] No match data file found for {year}: {json_path}")
            continue
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Structure: { "NRL": [ { "2019": [ { "1": [ {match1}, ... ] }, ... ] } ] }
        # Fix: handle both wrapped and unwrapped structures
        year_data = None
        if 'NRL' in data and isinstance(data['NRL'], list) and data['NRL'] and str(year) in data['NRL'][0]:
            year_data = data['NRL'][0][str(year)]
        elif str(year) in data:
            year_data = data[str(year)]
        else:
            print(f"[ERROR] Could not find year {year} in {json_path}")
            continue
        for round_block in year_data:
            for round_num, matches in round_block.items():
                for match in matches:
                    all_matches.append({
                        'Year': year,
                        'Round': int(round_num) if str(round_num).isdigit() else None,
                        'HomeTeam': match.get('Home', ''),
                        'HomeScore': match.get('Home_Score', match.get('HomeScore', '')),
                        'AwayTeam': match.get('Away', ''),
                        'AwayScore': match.get('Away_Score', match.get('AwayScore', '')),
                        'Venue': match.get('Venue', ''),
                        'Date': match.get('Date', ''),
                        'MatchCentreURL': match.get('Match_Centre_URL', match.get('MatchCentreURL', ''))
                    })
    if not all_matches:
        print("[FATAL] No matches found in any year. Exiting flattening.")
        return
    df = pd.DataFrame(all_matches)
    # Fix: Drop rows with missing or NaN Round
    df = df.dropna(subset=['Round'])
    df['Round'] = df['Round'].astype(int)
    print("[DEBUG] DataFrame info before saving:")
    print(df.info())
    print(df.head())
    df.to_csv(output_csv_path, index=False)
    print(f"[SUCCESS] Flattened all matches to {output_csv_path} ({len(df)} rows)")

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    output_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outputs', 'all_matches_2019_2025.csv'))
    flatten_nrl_match_data(base_dir, output_csv)
