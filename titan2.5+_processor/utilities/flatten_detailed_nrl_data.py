import os
import json
import pandas as pd

def flatten_detailed_json(year, comp_type, input_dir=None, output_dir=None):
    if input_dir is None:
        input_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nrl_data_main', 'data', comp_type, str(year)))
    if output_dir is None:
        output_dir = input_dir
    files = [f for f in os.listdir(input_dir) if f.endswith('.json') and f"{comp_type}_detailed_match_data_{year}" in f]
    if not files:
        print(f"[WARN] No detailed match JSON found for {comp_type} {year} in {input_dir}.")
        return None
    file_path = os.path.join(input_dir, files[0])
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Could not read {file_path}: {e}")
        return None
    # Flatten the JSON structure
    records = []
    for season_data in data.get(comp_type, []):
        for year_key, rounds in season_data.items():
            for round_group in rounds:
                for round_key, round_data in round_group.items():
                    for match in round_data:
                        for match_key, match_info in match.items():
                            flat = {'Year': year_key, 'Round': round_key, 'MatchKey': match_key}
                            if isinstance(match_info, dict):
                                for k, v in match_info.items():
                                    flat[k] = v
                            records.append(flat)
    df = pd.DataFrame(records)
    output_file = os.path.join(output_dir, f"flattened_{comp_type}_detailed_data_{year}.csv")
    df.to_csv(output_file, index=False)
    print(f"[INFO] Flattened detailed match data for {year} to {output_file} ({len(df)} rows)")
    return output_file

def combine_detailed_csvs(years, comp_type):
    outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'outputs'))
    os.makedirs(outputs_dir, exist_ok=True)
    combined_csv_path = os.path.join(outputs_dir, f"all_detailed_matches_{years[0]}_{years[-1]}.csv")
    all_dfs = []
    for year in years:
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nrl_data_main', 'data', comp_type, str(year)))
        csv_file = os.path.join(output_dir, f"flattened_{comp_type}_detailed_data_{year}.csv")
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                all_dfs.append(df)
                print(f"[INFO] Appended {csv_file} ({len(df)} rows)")
            except Exception as e:
                print(f"[WARN] Could not read {csv_file}: {e}")
        else:
            print(f"[WARN] {csv_file} does not exist, skipping.")
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        combined_df.to_csv(combined_csv_path, index=False)
        print(f"[SUCCESS] Combined detailed CSV written to {combined_csv_path} ({len(combined_df)} rows)")
    else:
        print("[FATAL] No detailed yearly CSVs found to combine. all_detailed_matches_2019_2025.csv not created.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Flatten and combine NRL detailed match JSONs to CSV.")
    parser.add_argument('--years', type=str, default='2019-2025', help='Year(s) of the data, e.g. 2025 or 2019-2025')
    parser.add_argument('--type', type=str, default='NRL', help='Competition type (e.g. NRL, HOSTPLUS)')
    args = parser.parse_args()
    if '-' in args.years:
        start, end = map(int, args.years.split('-'))
        years = list(range(start, end + 1))
    else:
        years = [int(args.years)]
    for year in years:
        print(f"\n=== Flattening detailed match data for {args.type} {year} ===")
        flatten_detailed_json(year, args.type)
    print("\n=== Combining all yearly detailed match CSVs ===")
    combine_detailed_csvs(years, args.type)
