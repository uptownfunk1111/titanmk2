import os
import json
import pandas as pd

def flatten_nrl_match_data(input_base_dir, output_csv_path, years=range(2019, 2026)):
    all_matches = []
    data_issues = []
    for year in years:
        json_path = os.path.join(input_base_dir, 'NRL', str(year), f'NRL_data_{year}.json')
        if not os.path.exists(json_path):
            print(f"[WARN] No match data file found for {year}: {json_path}")
            continue
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Structure: { "NRL": [ { "2025": [ { "1": [ {match1}, {match2}, ... ] }, ... ] } ] }
        year_data = data.get('NRL', [])[0].get(str(year), [])
        # DEBUG: Print the round keys for the first year/season found
        if year_data:
            print(f"[DEBUG] Year {year} round keys: {[list(rb.keys()) for rb in year_data]}")
        for round_block in year_data:
            # Print the raw round_block for debugging
            print(f"[DEBUG] Raw round_block for year {year}: {json.dumps(round_block, indent=2)}")
            for round_num, matches in round_block.items():
                print(f"[DEBUG] round_num: {round_num} (type: {type(round_num)})")
                for match in matches:
                    match_issue = []
                    home = match.get('Home', '')
                    away = match.get('Away', '')
                    # Ensure scores are int or NaN
                    def safe_int(val):
                        try:
                            return int(val)
                        except:
                            return float('nan')
                    home_score = safe_int(match.get('Home_Score', match.get('HomeScore', '')))
                    away_score = safe_int(match.get('Away_Score', match.get('AwayScore', '')))
                    # --- DEBUG: Print raw match dict for inspection ---
                    print(f"[DEBUG] Raw match dict for year {year} round {round_num}: {json.dumps(match, indent=2)}")
                    # --- DEBUG: Print extracted fields ---
                    print(f"[DEBUG] Extracted: home='{home}', away='{away}', home_score={home_score}, away_score={away_score}, round={round_num}")
                    # --- FIX: Always extract round number from match['Round'] if present, fallback to outer key ---
                    import re
                    round_num_int = None
                    round_str = match.get('Round', '')
                    digits = re.findall(r'\d+', str(round_str))
                    if digits:
                        round_num_int = int(digits[0])
                    else:
                        try:
                            round_num_int = int(round_num)
                        except Exception:
                            round_num_int = None
                    if round_num_int is None:
                        print(f"[WARN] Could not parse round number from match['Round'] ('{round_str}') or outer key '{round_num}' for year {year}. Skipping match.")
                        print(f"[DEBUG] Full match dict: {json.dumps(match, indent=2)}")
                        print(f"[DEBUG] Outer key: {round_num}")
                        continue  # Skip this match entirely
                    # Flag issues but do not skip
                    if not home or not away:
                        match_issue.append(f"Missing team: home='{home}', away='{away}'")
                    if pd.isna(home_score):
                        match_issue.append("Missing HomeScore")
                    if pd.isna(away_score):
                        match_issue.append("Missing AwayScore")
                    all_matches.append({
                        'Year': year,
                        'Round': round_num_int,
                        'HomeTeam': home,
                        'HomeScore': home_score,
                        'AwayTeam': away,
                        'AwayScore': away_score,
                        'Venue': match.get('Venue', ''),
                        'Date': match.get('Date', ''),
                        'MatchCentreURL': match.get('Match_Centre_URL', match.get('MatchCentreURL', '')),
                        'data_issues': ", ".join(match_issue) if match_issue else ""
                    })
                    if match_issue:
                        print(f"[DEBUG] Data issue in year {year} round {round_num}: {match_issue}")
                        data_issues.append({'year': year, 'round': round_num, 'match': match, 'issues': match_issue})
    if not all_matches:
        print("[FATAL] No matches found in any year. Exiting flattening.")
        return
    df = pd.DataFrame(all_matches)
    # Ensure Round is always int (or -1 for missing)
    df['Round'] = df['Round'].fillna(-1).astype(int)
    print("[DEBUG] Unique Round values and counts in match data:")
    print(df['Round'].value_counts(dropna=False).sort_index())
    # Print any rows with Round == -1 for diagnosis
    if (df['Round'] == -1).any():
        print("[WARN] Some matches have Round == -1. Sample:")
        print(df[df['Round'] == -1].head())
    # Ensure data_issues is always a string (never NaN)
    df['data_issues'] = df['data_issues'].fillna("")
    print("[DEBUG] DataFrame info before saving:")
    print(df.info())
    print(df.head())
    df.to_csv(output_csv_path, index=False)
    print(f"[SUCCESS] Flattened all matches to {output_csv_path} ({len(df)} rows)")
    if data_issues:
        issues_path = output_csv_path.replace('.csv', '_data_issues.json')
        with open(issues_path, 'w', encoding='utf-8') as f:
            json.dump(data_issues, f, indent=2)
        print(f"[WARN] Data issues found and saved to {issues_path}")

if __name__ == "__main__":
    # Use titan2.5+_processor/data as the input base, outputs as output base
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
    output_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs', 'all_matches_2019_2025.csv'))
    print("[DEBUG] Starting flatten_nrl_data.py as standalone script.")
    print(f"[DEBUG] Input base directory: {base_dir}")
    print(f"[DEBUG] Output CSV path: {output_csv}")
    flatten_nrl_match_data(base_dir, output_csv)
    print("[DEBUG] Flattening complete. Inspect your output and data_issues file.")
    # Keep the script open for inspection until user types 'exit'
    while True:
        user_input = input("Type 'exit' to close flatten_nrl_data.py: ").strip().lower()
        if user_input == 'exit':
            print("[DEBUG] Exiting flatten_nrl_data.py.")
            break
