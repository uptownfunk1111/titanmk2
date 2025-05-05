import json
import csv
import math

# Function to flatten the nested JSON structure
def flatten_json(nested_json, parent_key='', sep='_'):
    """Recursively flattens a nested JSON structure into a flat dictionary."""
    items = []
    if isinstance(nested_json, dict):
        for k, v in nested_json.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_json(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # If the value is a list, iterate through it and flatten the items
                for i, sub_item in enumerate(v):
                    items.extend(flatten_json(sub_item, f"{new_key}_{i+1}", sep=sep).items())
            else:
                items.append((new_key, v))
    elif isinstance(nested_json, list):
        # If it's a list at the top level, iterate through the list and flatten each element
        for i, item in enumerate(nested_json):
            items.extend(flatten_json(item, f"{parent_key}_{i+1}", sep=sep).items())
    else:
        # Otherwise, just return the value
        items.append((parent_key, nested_json))
    
    return dict(items)

# Function to process and extract fixed fields (static fields)
def process_fixed_fields(player_data):
    """Extract fixed fields from the player data."""
    fixed_fields = {}
    # Extract the first player's fixed fields, assuming all players have the same fixed structure
    if player_data:
        player = player_data[0]
        fixed_fields['Name'] = player.get('Name', '')
        fixed_fields['Number'] = player.get('Number', '')
        fixed_fields['Position'] = player.get('Position', '')
    return fixed_fields

# Function to process and extract dynamic fields (game stats)
def process_dynamic_fields(player_data):
    """Extract dynamic fields from the player data (e.g., stats per game)."""
    dynamic_fields = []
    for player in player_data:
        # Extract stats per game
        for year, games in player.items():
            if isinstance(games, list):
                for game in games:
                    for game_key, stats in game.items():
                        flattened_stats = flatten_json(stats)  # Flatten stats for each game
                        dynamic_fields.append(flattened_stats)
    return dynamic_fields

# Function to replace "-" with "0" in the data
def replace_dashes_with_zero(data):
    """Replace all instances of '-' with '0' in the data."""
    for key, value in data.items():
        if isinstance(value, str) and value == '-':
            data[key] = '0'
    return data

# Function to write data to multiple CSV files if it exceeds Excel's row limit
def write_to_multiple_csv_files(data, fieldnames, base_filename='output_file'):
    """Write data to multiple CSV files to avoid Excel's row limit."""
    max_rows = 1048576  # Excel's row limit
    num_files = math.ceil(len(data) / max_rows)

    for i in range(num_files):
        output_file = f"{base_filename}_{i + 1}.csv"
        start_index = i * max_rows
        end_index = min((i + 1) * max_rows, len(data))

        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data[start_index:end_index])

        print(f"Data successfully written to {output_file}")

# Main function to extract player stats and write to CSV
def main():
    # Load JSON data
    input_file = 'C:\\Users\\slangston1\\TITAN\\titan2.5+_processor\\NRL_fixed\\2019\\NRL_player_statistics_2019.json'  # Change this to the path of your JSON file
    output_file = 'C:\\Users\\slangston1\\TITAN\\titan2.5+_processor\\outputs.csv'  # This will be used as the base filename for multiple files
    
    try:
        with open(input_file, 'r') as f:
            json_data = json.load(f)
        print("JSON file loaded successfully.")
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return
    
    # Extract fixed and dynamic fields from the JSON data
    player_data = json_data.get('PlayerStats', [])
    
    # Process fixed fields
    fixed_fields = process_fixed_fields(player_data)
    print(f"Fixed Fields Extracted: {fixed_fields}")
    
    # Process dynamic fields (game stats)
    dynamic_fields = process_dynamic_fields(player_data)
    print(f"Dynamic Fields Extracted: {len(dynamic_fields)} entries")

    # Replace "-" with "0" in dynamic fields
    for dynamic in dynamic_fields:
        replace_dashes_with_zero(dynamic)

    # Combine fixed and dynamic fields
    combined_data = []
    for dynamic in dynamic_fields:
        combined_entry = {**fixed_fields, **dynamic}  # Merge fixed and dynamic fields
        combined_data.append(combined_entry)
    
    print(f"Data successfully combined. {len(combined_data)} records to write.")

    # Write to multiple CSV files
    try:
        write_to_multiple_csv_files(combined_data, fieldnames=combined_data[0].keys())
    except Exception as e:
        print(f"Error writing to CSV: {e}")

if __name__ == "__main__":
    main()
