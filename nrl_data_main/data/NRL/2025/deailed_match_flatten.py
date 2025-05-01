import json
import pandas as pd

# Step 1: Load the JSON data
file_path = input("Enter the full file path to the JSON file: ")
with open(file_path, 'r') as file:
    data = json.load(file)

# Step 2: Traverse the JSON and extract match and player data
flattened_data = []

# Traversing through the JSON to extract match and player details
for season in data:  # Iterate through each season
    for round_data in season:
        for match_data in round_data:
            for match_key, match_info in match_data.items():
                if isinstance(match_info, dict):
                    match_details = match_info.get('match', {})
                    home_team = match_info.get('home', {})
                    away_team = match_info.get('away', {})
                    
                    # Flattening the match and team stats into individual records
                    match_record = {
                        'match_key': match_key,
                        'home_team': home_team.get('team_name', None),
                        'away_team': away_team.get('team_name', None),
                        'home_score': home_team.get('score', None),
                        'away_score': away_team.get('score', None),
                        'venue': match_details.get('venue', None),
                        'date': match_details.get('date', None),
                    }
                    
                    # Flatten the home team player stats
                    for player in home_team.get('players', []):
                        player_record = match_record.copy()
                        player_record.update({
                            'player_name': player.get('Name', None),
                            'player_number': player.get('Number', None),
                            'position': player.get('Position', None),
                            'minutes_played': player.get('Mins Played', None),
                            'total_points': player.get('Total Points', None),
                            'all_runs': player.get('All Runs', None),
                            'all_run_metres': player.get('All Run Metres', None),
                            'kick_return_metres': player.get('Kick Return Metres', None),
                            # Add more stats as necessary
                        })
                        flattened_data.append(player_record)
                    
                    # Flatten the away team player stats
                    for player in away_team.get('players', []):
                        player_record = match_record.copy()
                        player_record.update({
                            'player_name': player.get('Name', None),
                            'player_number': player.get('Number', None),
                            'position': player.get('Position', None),
                            'minutes_played': player.get('Mins Played', None),
                            'total_points': player.get('Total Points', None),
                            'all_runs': player.get('All Runs', None),
                            'all_run_metres': player.get('All Run Metres', None),
                            'kick_return_metres': player.get('Kick Return Metres', None),
                            # Add more stats as necessary
                        })
                        flattened_data.append(player_record)

# Step 3: Create a pandas DataFrame
df = pd.DataFrame(flattened_data)

# Step 4: Save the DataFrame to a CSV file
output_file_path = file_path.replace('.json', '_flattened.csv')
df.to_csv(output_file_path, index=False)

print(f"Flattened data saved to: {output_file_path}")
