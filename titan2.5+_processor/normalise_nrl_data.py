import pandas as pd
import os
from colorama import Fore, Style, init
init(autoreset=True)

# This script normalises the flattened NRL match data for ML and reporting.
# It reads all_matches_2019_2025.csv, cleans/standardises columns, and outputs normalised_all_matches_2019_2025.csv.

def main():
    input_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outputs', 'all_matches_2019_2025.csv'))
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outputs', 'normalised_all_matches_2019_2025.csv'))
    if not os.path.exists(input_path):
        print(Fore.RED + f"[ERROR] Input file not found: {input_path}" + Style.RESET_ALL)
        return
    print(Fore.CYAN + f"[INFO] Loading: {input_path}" + Style.RESET_ALL)
    df = pd.read_csv(input_path)

    # Example normalisation: lower-case column names, fill missing values, strip whitespace
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.fillna('NA')

    # Example: ensure numeric columns are numeric (if any)
    for col in df.columns:
        if any(s in col for s in ['score', 'round', 'year', 'margin']):
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    print(Fore.GREEN + f"[SUCCESS] Normalised data shape: {df.shape}" + Style.RESET_ALL)
    df.to_csv(output_path, index=False)
    print(Fore.GREEN + f"[SUCCESS] Normalised data saved to {output_path}" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
