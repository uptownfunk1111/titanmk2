"""
TITAN Main Pipeline Script (Full Orchestration, Verbose & Diagnostic)

Purpose:
- This is the master entry point for the TITAN NRL tipping pipeline.
- It orchestrates the entire workflow: scraping, overlays, flattening, feature engineering, ML, and reporting.

Workflow:
1. Scrape raw match, detailed match, and player data (calls match_data_select.py, match_data_detailed_select.py, player_data_select.py).
2. Run overlay/tactical scripts (fetch_upcoming_fixtures_and_officials.py, fetch_upcoming_teamlists.py, lineup_impact.py, kick_target_mapping.py, officiating_impact_analysis.py, weather_impact_analysis.py, speculative_data_sweep.py, etc.).
3. Flatten/process all JSONs to CSVs (flatten_nrl_data.py, player_stats_combined.ipynb, detailed_match_stats_combined.ipynb).
4. Feature engineering and overlay merging (predictor_ml.py, build_player_impact_scores.py).
5. Run ML prediction model (predictor_ml.py or titan_model.py).
6. Generate reports and dashboards (tactical_tipping_table.py, titan_match_insights.py, titan_dashboard.py).
7. Save all outputs in outputs/.

Best Practices:
- All configuration and paths are centralized.
- All data files are saved in the outputs directory for consistency.
- All scraping, processing, and ML logic is modular and importable.
- The pipeline is documented and automated so you only need to run this script for the full workflow.
"""
import os
import sys
import subprocess
from datetime import datetime
import pandas as pd

from utilities import titan_fetch, titan_teamlist

def ensure_output_folder():
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
        print("[INFO] Created outputs directory.")
    else:
        print("[INFO] Outputs directory already exists.")

def print_file_info(path):
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"[DIAG] File exists: {path} (size: {size} bytes)")
        if path.endswith('.csv'):
            try:
                df = pd.read_csv(path)
                print(f"[DIAG] {os.path.basename(path)}: {len(df)} rows, {len(df.columns)} columns. Columns: {list(df.columns)[:5]} ...")
            except Exception as e:
                print(f"[WARN] Could not read {path} as CSV: {e}")
    else:
        print(f"[WARN] File not found: {path}")

def save_tips_to_excel(tips):
    df = pd.DataFrame(tips)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    timestamped_path = os.path.join("outputs", f"titan_tips_{now}.xlsx")
    latest_path = os.path.join("outputs", "titan_tips_latest.xlsx")
    df.to_excel(timestamped_path, index=False)
    df.to_excel(latest_path, index=False)
    print(f"✅ Tips saved to '{timestamped_path}' and 'titan_tips_latest.xlsx'.")
    print_file_info(timestamped_path)
    print_file_info(latest_path)

if __name__ == "__main__":
    print("""
==============================
TITAN NRL Data & Prediction Pipeline (Full Orchestration, Verbose & Diagnostic)
==============================
[INFO] This script orchestrates the full workflow: scraping, overlays, flattening, feature engineering, ML, and reporting.
""")
    print("[STEP 0] Ensuring outputs directory exists...")
    ensure_output_folder()

    # 1. Data Harvesting (Scraping Raw Data)
    print("[STEP 1] Scraping basic match data (match_data_select.py)...")
    subprocess.run([sys.executable, os.path.join("titan2.5+_processor", "utilities", "match_data_select.py")], check=True)
    print_file_info(os.path.join("outputs", "NRL_data_2025.json"))
    print("[STEP 1A] Scraping detailed match data (match_data_detailed_select.py)...")
    subprocess.run([sys.executable, os.path.join("titan2.5+_processor", "utilities", "match_data_detailed_select.py")], check=True)
    print_file_info(os.path.join("outputs", "NRL_detailed_match_data_2025.json"))
    print("[STEP 1B] Scraping player stats (player_data_select.py)...")
    subprocess.run([sys.executable, os.path.join("titan2.5+_processor", "utilities", "player_data_select.py")], check=True)
    print_file_info(os.path.join("outputs", "NRL_player_statistics_2025.json"))
    # Optionally: detailed player stats
    detailed_player_stats_path = os.path.join("titan2.5+_processor", "nrl_data_main", "scraping", "player_data_detailed_select.py")
    if os.path.exists(detailed_player_stats_path):
        print("[STEP 1C] Scraping detailed player stats (player_data_detailed_select.py)...")
        subprocess.run([sys.executable, detailed_player_stats_path], check=True)
        print_file_info(os.path.join("outputs", "NRL_player_detailed_statistics_2025.json"))

    # 2. Overlay & Tactical Data Fetch
    print("[STEP 2] Fetching overlays and tactical data...")
    overlay_scripts = [
        os.path.join("utilities", "fetch_upcoming_fixtures_and_officials.py"),
        os.path.join("titan2.5+_processor", "fetch_upcoming_teamlists.py"),
        os.path.join("titan2.5+_processor", "utilities", "lineup_impact.py"),
        os.path.join("titan2.5+_processor", "kick_target_mapping.py"),
        os.path.join("titan2.5+_processor", "utilities", "officiating_impact_analysis.py"),
        os.path.join("titan2.5+_processor", "utilities", "weather_impact_analysis.py"),
        os.path.join("titan2.5+_processor", "utilities", "speculative_data_sweep.py"),
        os.path.join("titan2.5+_processor", "utilities", "opponent_analysis.py"),
        os.path.join("titan2.5+_processor", "utilities", "player_injury_impact.py"),
        os.path.join("titan2.5+_processor", "utilities", "coach_impact_analysis.py"),
    ]
    for script in overlay_scripts:
        if os.path.exists(script):
            print(f"[STEP 2] Running overlay script: {script}")
            subprocess.run([sys.executable, script], check=True)
        else:
            print(f"[WARN] Overlay script not found: {script}")

    # 3. Data Flattening & Processing
    print("[STEP 3] Flattening and processing NRL data...")
    flatten_scripts = [
        "flatten_nrl_data.py",
        os.path.join("titan2.5+_processor", "flatten_player_stats.py"),
        # Add more flattening/processing scripts as needed
        "process_nrl_data.py",
    ]
    for script in flatten_scripts:
        if os.path.exists(script):
            print(f"[STEP 3] Running flattening/processing script: {script}")
            subprocess.run([sys.executable, script], check=True)
        else:
            print(f"[WARN] Flattening/processing script not found: {script}")
    # Print info on key output files
    print_file_info(os.path.join("outputs", "all_matches_2019_2025.csv"))
    print_file_info(os.path.join("outputs", "all_players_2019_2025.csv"))

    # 4. Feature Engineering & Overlay Merging
    print("[STEP 4] Feature engineering and overlay merging (predictor_ml.py, build_player_impact_scores.py)...")
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utilities'))
    feature_scripts = [
        os.path.join("titan2.5+_processor", "build_player_impact_scores.py"),
        os.path.join("titan2.5+_processor", "predictor_ml.py"),
    ]
    for script in feature_scripts:
        if os.path.exists(script):
            print(f"[STEP 4] Running feature engineering script: {script}")
            subprocess.run([sys.executable, script], check=True)
        else:
            print(f"[WARN] Feature engineering script not found: {script}")
    print_file_info(os.path.join("outputs", "player_impact_scores_2019_2025.csv"))

    # 5. Machine Learning & Prediction
    print("[STEP 5] Running ML prediction model (predictor_ml.py or titan_model.py > predict_tips)...")
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from titan import titan_model
        predict_tips = titan_model.predict_tips
        fetch_nrl_data = titan_fetch.fetch_nrl_data
        fetch_team_lists = titan_teamlist.fetch_team_lists
        matches = fetch_nrl_data()
        print(f"[DIAG] {len(matches)} matches fetched for prediction.")
        team_lists = fetch_team_lists()
        print(f"[DIAG] {len(team_lists)} team list entries fetched for prediction.")
        tips = predict_tips(matches, team_lists)
        if not tips:
            print("[ERROR] No tips generated. Check the ML model and input data.")
            exit(1)
        print(f"[STEP 5 COMPLETE] {len(tips)} tips generated. Sample: {tips[:2] if len(tips) > 2 else tips}")
        print("[STEP 6] Saving tips to Excel in outputs/ directory...")
        save_tips_to_excel(tips)
        print("[STEP 6 COMPLETE] Tips saved to outputs/titan_tips_latest.xlsx and timestamped file.")
    except Exception as e:
        print(f"[ERROR] ML prediction step failed: {e}")

    # 6. Reporting & Output Generation
    print("[STEP 7] Generating reports and dashboards...")
    reporting_scripts = [
        os.path.join("titan2.5+_processor", "utilities", "tactical_tipping_table.py"),
        os.path.join("titan2.5+_processor", "utilities", "titan_match_insights.py"),
        "titan_dashboard.py",
    ]
    for script in reporting_scripts:
        if os.path.exists(script):
            print(f"[STEP 7] Running reporting/dashboard script: {script}")
            # titan_dashboard.py is a Streamlit app, so run with streamlit if found
            if script.endswith("titan_dashboard.py"):
                subprocess.run(["streamlit", "run", script])
            else:
                subprocess.run([sys.executable, script], check=True)
        else:
            print(f"[WARN] Reporting/dashboard script not found: {script}")

    print("==============================")
    print("[COMPLETE] TITAN pipeline finished. Review outputs for results.")
    print("==============================")
