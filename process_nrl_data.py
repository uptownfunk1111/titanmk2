import json

def inspect_json_structure(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Print the type of the loaded data
    print(f"Type of data: {type(data)}")

    # Print first-level keys of the data to inspect its structure
    print(f"Keys in the JSON: {list(data.keys())}")

    # For now, we'll print a portion of the "PlayerStats" or "NRL" keys
    if "NRL" in data:
        print(f"Sample NRL Data: {data['NRL'][:1]}")  # Print the first item in NRL list if available
    if "PlayerStats" in data:
        print(f"Sample PlayerStats: {data['PlayerStats'][:1]}")  # Print the first item in PlayerStats list if available

def extract_match_data(data):
    extracted_data = []
    if "NRL" in data:
        for season_data in data["NRL"]:
            for year, rounds in season_data.items():
                for round_key, round_data in rounds[0].items():
                    for match in round_data:
                        if isinstance(match, dict):  # Check if the match is a dictionary
                            match_data = {
                                "Round": round_key,
                                "Home": match.get("Home", "N/A"),
                                "Home_Score": match.get("Home_Score", "N/A"),
                                "Away": match.get("Away", "N/A"),
                                "Away_Score": match.get("Away_Score", "N/A"),
                                "Venue": match.get("Venue", "N/A"),
                                "Date": match.get("Date", "N/A"),
                                "Match_Centre_URL": match.get("Match_Centre_URL", "N/A")
                            }
                            extracted_data.append(match_data)
    return extracted_data

def extract_player_stats(data):
    extracted_data = []
    if "PlayerStats" in data:
        for season_data in data['PlayerStats']:
            for year_data in season_data:
                for match_data in year_data:
                    for match_key, match_info in match_data.items():
                        for player_details in match_info:
                            player_record = {
                                'game': match_key,
                                'player_name': player_details.get('Name', None),
                                'player_number': player_details.get('Number', None),
                                'position': player_details.get('Position', None),
                                'minutes_played': player_details.get('Mins Played', None),
                                'total_points': player_details.get('Total Points', None),
                                # Add more fields as needed
                            }
                            extracted_data.append(player_record)
    return extracted_data

def main():
    file_path = input("Enter the file path: ")

    # First, inspect the JSON structure
    inspect_json_structure(file_path)

    # After inspecting the structure, let's extract data based on the previous logic
    with open(file_path, 'r') as f:
        data = json.load(f)

    match_data = extract_match_data(data)
    player_stats = extract_player_stats(data)

    # Print out the extracted match data and player stats to verify
    print("Extracted Match Data:")
    print(match_data[:5])  # Print first 5 match records
    print("Extracted Player Stats:")
    print(player_stats[:5])  # Print first 5 player stats records

if __name__ == "__main__":
    main()
