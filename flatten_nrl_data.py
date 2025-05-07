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
        # Structure: { "NRL": [ { "2025": [ { "1": [ {match1}, {match2}, ... ] }, ... ] } ] }
        year_data = data.get('NRL', [])[0].get(str(year), [])
        for round_block in year_data:
            for round_num, matches in round_block.items():
                for match in matches:
                    all_matches.append({
                        'Year': year,
                        'Round': int(round_num),
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
    print("[DEBUG] DataFrame info before saving:")
    print(df.info())
    print(df.head())
    df.to_csv(output_csv_path, index=False)
    print(f"[SUCCESS] Flattened all matches to {output_csv_path} ({len(df)} rows)")

if __name__ == "__main__":
    # Use titan2.5+_processor/data as the input base, outputs as output base
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
    output_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs', 'all_matches_2019_2025.csv'))
    flatten_nrl_match_data(base_dir, output_csv)
