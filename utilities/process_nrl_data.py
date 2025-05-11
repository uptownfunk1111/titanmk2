import json

def inspect_json_structure(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    print(f"Type of data: {type(data)}")
    print(f"Keys in the JSON: {list(data.keys())}")
    if "NRL" in data:
        print(f"Sample NRL Data: {data['NRL'][:1]}")
    if "PlayerStats" in data:
        print(f"Sample PlayerStats: {data['PlayerStats'][:1]}")

def extract_match_data(data):
    extracted_data = []
    data_issues = []
    if "NRL" in data:
        for season_data in data["NRL"]:
            for year, rounds in season_data.items():
                for round_key, round_data in rounds[0].items():
                    for match in round_data:
                        if isinstance(match, dict):
                            match_issue = []
                            home = match.get("Home", "N/A")
                            away = match.get("Away", "N/A")
                            home_score = match.get("Home_Score", "N/A")
                            away_score = match.get("Away_Score", "N/A")
                            if not home or home == "N/A" or not away or away == "N/A":
                                match_issue.append(f"Missing team: home='{home}', away='{away}'")
                            if home_score in ("", None, "-", "N/A") or away_score in ("", None, "-", "N/A"):
                                match_issue.append(f"Missing score: home_score='{home_score}', away_score='{away_score}'")
                            match_data = {
                                "Round": round_key,
                                "Home": home,
                                "Home_Score": home_score,
                                "Away": away,
                                "Away_Score": away_score,
                                "Venue": match.get("Venue", "N/A"),
                                "Date": match.get("Date", "N/A"),
                                "Match_Centre_URL": match.get("Match_Centre_URL", "N/A"),
                                "data_issues": match_issue if match_issue else None
                            }
                            extracted_data.append(match_data)
                            if match_issue:
                                data_issues.append({"round": round_key, "match": match, "issues": match_issue})
    return extracted_data, data_issues

def extract_player_stats(data):
    extracted_data = []
    data_issues = []
    if "PlayerStats" in data:
        for season_data in data['PlayerStats']:
            for year_data in season_data:
                for match_data in year_data:
                    for match_key, match_info in match_data.items():
                        for player_details in match_info:
                            player_issue = []
                            name = player_details.get('Name', None)
                            mins = player_details.get('Mins Played', None)
                            if not name:
                                player_issue.append("Missing player name")
                            if mins in (None, '', '-', 'N/A'):
                                player_issue.append("Missing minutes played")
                            player_record = {
                                'game': match_key,
                                'player_name': name,
                                'player_number': player_details.get('Number', None),
                                'position': player_details.get('Position', None),
                                'minutes_played': mins,
                                'total_points': player_details.get('Total Points', None),
                                'data_issues': player_issue if player_issue else None
                            }
                            extracted_data.append(player_record)
                            if player_issue:
                                data_issues.append({'game': match_key, 'player': player_details, 'issues': player_issue})
    return extracted_data, data_issues

if __name__ == "__main__":
    print("[DEBUG] Starting process_nrl_data.py as standalone script.")
    file_path = input("Enter the file path: ")
    print(f"[DEBUG] Inspecting JSON structure for: {file_path}")
    inspect_json_structure(file_path)
    with open(file_path, 'r') as f:
        data = json.load(f)
    print("[DEBUG] Extracting match data...")
    match_data, match_issues = extract_match_data(data)
    print(f"[DEBUG] Extracted {len(match_data)} match records.")
    print("[DEBUG] Extracting player stats...")
    player_stats, player_issues = extract_player_stats(data)
    print(f"[DEBUG] Extracted {len(player_stats)} player records.")
    print("[DEBUG] Sample match data:")
    print(match_data[:3])
    print("[DEBUG] Sample player stats:")
    print(player_stats[:3])
    if match_issues:
        with open("match_data_issues.json", "w", encoding="utf-8") as f:
            json.dump(match_issues, f, indent=2)
        print(f"[WARN] Match data issues found and saved to match_data_issues.json")
    if player_issues:
        with open("player_data_issues.json", "w", encoding="utf-8") as f:
            json.dump(player_issues, f, indent=2)
        print(f"[WARN] Player data issues found and saved to player_data_issues.json")
    print("[DEBUG] Processing complete. Inspect your outputs and issues files.")
    while True:
        user_input = input("Type 'exit' to close process_nrl_data.py: ").strip().lower()
        if user_input == 'exit':
            print("[DEBUG] Exiting process_nrl_data.py.")
            break
