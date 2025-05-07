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
        for round_block in year_data:
            for round_num, matches in round_block.items():
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
                    if not home or not away:
                        match_issue.append(f"Missing team: home='{home}', away='{away}'")
                    if pd.isna(home_score) or pd.isna(away_score):
                        match_issue.append(f"Missing score: home_score='{home_score}', away_score='{away_score}'")
                    all_matches.append({
                        'Year': year,
                        'Round': int(round_num),
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
    flatten_nrl_match_data(base_dir, output_csv)
