import json
import csv
import math
import os
import argparse
import pandas as pd

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
    print("[START] Player Stats Extraction Script")
    parser = argparse.ArgumentParser(description="Extract and flatten player stats from JSON.")
    parser.add_argument('--input', type=str, default=os.path.join(os.path.dirname(__file__), '..', 'NRL_fixed', '2019', 'NRL_player_statistics_2019.json'), help='Path to input JSON file')
    parser.add_argument('--output', type=str, default=os.path.join(os.path.dirname(__file__), '..', 'outputs', 'player_stats_2019'), help='Base path for output CSV file(s), no extension')
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output

    print(f"[INFO] Input JSON file: {input_file}")
    print(f"[INFO] Output base path: {output_file}")

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"[INFO] Created output directory: {output_dir}")
    else:
        print(f"[INFO] Output directory exists: {output_dir}")

    try:
        with open(input_file, 'r') as f:
            json_data = json.load(f)
        print(f"[SUCCESS] JSON file loaded successfully from {input_file}.")
    except Exception as e:
        print(f"[ERROR] Failed to load JSON file: {e}")
        return

    # Extract fixed and dynamic fields from the JSON data
    player_data = json_data.get('PlayerStats', [])
    print(f"[INFO] Found {len(player_data)} player entries in JSON root.")

    # Process fixed fields
    fixed_fields = process_fixed_fields(player_data)
    print(f"[INFO] Fixed Fields Extracted: {fixed_fields}")

    # Process dynamic fields (game stats)
    print("[INFO] Extracting dynamic (game stats) fields for each player...")
    dynamic_fields = process_dynamic_fields(player_data)
    print(f"[INFO] Dynamic Fields Extracted: {len(dynamic_fields)} entries")

    # Replace "-" with "0" in dynamic fields
    print("[INFO] Replacing '-' with '0' in all dynamic fields...")
    for dynamic in dynamic_fields:
        replace_dashes_with_zero(dynamic)
    print("[INFO] Replacement complete.")

    # Combine fixed and dynamic fields
    print("[INFO] Combining fixed and dynamic fields for each record...")
    combined_data = []
    for idx, dynamic in enumerate(dynamic_fields):
        combined_entry = {**fixed_fields, **dynamic}  # Merge fixed and dynamic fields
        combined_data.append(combined_entry)
        if idx < 3:
            print(f"[DEBUG] Sample combined record {idx+1}: {combined_entry}")
    print(f"[INFO] Data successfully combined. {len(combined_data)} records to write.")

    # Write to multiple CSV files
    try:
        print("[INFO] Writing combined data to CSV file(s)...")
        write_to_multiple_csv_files(combined_data, fieldnames=combined_data[0].keys(), base_filename=output_file)
        print("[SUCCESS] All data written to CSV file(s).")
    except Exception as e:
        print(f"[ERROR] Error writing to CSV: {e}")

    print("[COMPLETE] Player stats extraction and flattening finished.")

    # === Combine all yearly player CSVs into a single all_players_2019_2025.csv ===
    print("\n[INFO] Combining all yearly player stats CSVs into outputs/all_players_2019_2025.csv ...")
    outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outputs'))
    os.makedirs(outputs_dir, exist_ok=True)
    combined_csv_path = os.path.join(outputs_dir, "all_players_2019_2025.csv")
    # Find all player_stats_*.csv in outputs_dir
    import glob
    player_csvs = sorted(glob.glob(os.path.join(outputs_dir, "player_stats_*.csv")))
    all_dfs = []
    for csv_path in player_csvs:
        try:
            df = pd.read_csv(csv_path)
            all_dfs.append(df)
            print(f"[INFO] Appended {csv_path} ({len(df)} rows)")
        except Exception as e:
            print(f"[WARN] Could not read {csv_path}: {e}")
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        combined_df.to_csv(combined_csv_path, index=False)
        print(f"[SUCCESS] Combined player stats CSV written to {combined_csv_path} ({len(combined_df)} rows)")
    else:
        print("[FATAL] No player stats CSVs found to combine. all_players_2019_2025.csv not created.")

if __name__ == "__main__":
    main()
