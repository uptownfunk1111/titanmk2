import os
import json
import pandas as pd
import argparse

def extract_nrl_data(year, comp_type, input_dir=None, output_dir=None):
    # Set default directories if not provided
    if input_dir is None:
        input_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nrl_data_main', 'data', comp_type, str(year)))
    if output_dir is None:
        output_dir = input_dir

    # Find the main match data JSON file
    files = [f for f in os.listdir(input_dir) if f.endswith('.json') and f"{comp_type}_data_{year}" in f]
    if not files:
        print(f"No JSON files found for {comp_type} {year} in {input_dir}.")
        return
    file_name = files[0]  # Use the first matching file
    file_path = os.path.join(input_dir, file_name)

    # Read the selected JSON file
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading the file: {e}")
        return

    # Flattening the JSON data
    flattened_data = []
    for season_data in data[comp_type]:
        for year_key, rounds in season_data.items():
            for round_group in rounds:  # <-- Iterate over all round groups
                for round_key, round_data in round_group.items():
                    for match in round_data:
                        match_data = {
                            "Year": year_key,
                            "Round": round_key,
                            "Home": match["Home"],
                            "Home_Score": match["Home_Score"],
                            "Away": match["Away"],
                            "Away_Score": match["Away_Score"],
                            "Venue": match["Venue"],
                            "Date": match["Date"],
                            "Match_Centre_URL": match["Match_Centre_URL"]
                        }
                        flattened_data.append(match_data)

    # Create a DataFrame from the flattened data
    df = pd.DataFrame(flattened_data)

    print(f"Extracted {len(df)} matches for {comp_type} {year}.")
    if df.empty:
        print(f"⚠️ No match data extracted for {comp_type} {year}. Check your input JSON structure and path: {file_path}")

    # Define the output file path
    output_file_name = f"flattened_{comp_type}_data_{year}.csv"
    output_file_path = os.path.join(output_dir, output_file_name)

    # Save the DataFrame to CSV
    try:
        df.to_csv(output_file_path, index=False)
        print(f"Successfully extracted the data and saved it to {output_file_path}")
        if os.path.getsize(output_file_path) == 0:
            print(f"❌ Output CSV {output_file_path} is empty! Check your extraction logic.")
    except Exception as e:
        print(f"Error saving the file: {e}")
        return

if __name__ == "__main__":
    import datetime
    parser = argparse.ArgumentParser(description="Flatten NRL JSON data to CSV.")
    parser.add_argument('--years', type=str, required=False, default='2019-2025', help='Year(s) of the data, e.g. 2025 or 2019-2025')
    parser.add_argument('--type', type=str, required=False, default='NRL', help='Competition type (e.g. NRL, HOSTPLUS)')
    parser.add_argument('--input_dir', type=str, default=None, help='Input directory containing JSON files')
    parser.add_argument('--output_dir', type=str, default=None, help='Directory to save the flattened CSV')
    args = parser.parse_args()

    # Parse years argument
    if '-' in args.years:
        start, end = map(int, args.years.split('-'))
        years = list(range(start, end + 1))
    else:
        years = [int(args.years)]

    summary = []
    for year in years:
        print(f"\n=== Processing {args.type} {year} ===")
        extract_nrl_data(year, args.type, args.input_dir, args.output_dir)
        # Check output file for summary
        if args.output_dir:
            output_dir = args.output_dir
        else:
            output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nrl_data_main', 'data', args.type, str(year)))
        output_file_name = f"flattened_{args.type}_data_{year}.csv"
        output_file_path = os.path.join(output_dir, output_file_name)
        if os.path.exists(output_file_path):
            try:
                df = pd.read_csv(output_file_path)
                summary.append((year, len(df)))
            except Exception:
                summary.append((year, 0))
        else:
            summary.append((year, 0))
    print("\n=== Extraction Summary ===")
    for year, count in summary:
        print(f"{args.type} {year}: {count} matches extracted.")
