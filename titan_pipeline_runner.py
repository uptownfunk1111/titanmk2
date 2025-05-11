"""
Master NRL Data Update and Prediction Runner
Runs scraping, data flattening, and prediction in sequence.
"""
import subprocess
import sys
import os
import datetime

# User-configurable parameters
YEAR = 2025
ROUND = 10  # Update as the season progresses
COMP_TYPE = 'NRL'

# Get absolute paths for all scripts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRAPING_SCRIPT = os.path.join(BASE_DIR, 'titan2.5+_processor', 'scraping', 'run_2025_updates.py')
FLATTEN_SCRIPT = os.path.join(BASE_DIR, 'flatten_nrl_data.py')
PREDICT_SCRIPT = os.path.join(BASE_DIR, 'titan2.5+_processor', 'new_prediction_models', 'predictor_ml.py')

def debug_file_info(filepath, nrows=3):
    print(f"[DEBUG] Checking file: {filepath}")
    # Always use the titan2.5+_processor/outputs/ path for player_stats_2025.csv
    if filepath.endswith('player_stats_2025.csv'):
        filepath = os.path.join(os.path.dirname(__file__), 'titan2.5+_processor', 'outputs', 'player_stats_2025.csv')
    if os.path.exists(filepath):
        try:
            import pandas as pd
            df = pd.read_csv(filepath)
            print(f"[DEBUG] {filepath}: rows={len(df)}, columns={list(df.columns)}")
            print(f"[DEBUG] Sample data from {filepath}:\n{df.head(nrows)}")
        except Exception as e:
            print(f"[DEBUG] Could not read {filepath}: {e}")
    else:
        print(f"[DEBUG] File not found: {filepath}")

print(f"[DEBUG] Script started at {datetime.datetime.now()}")
print(f"[DEBUG] Current working directory: {os.getcwd()}")

def prompt_step(step_name):
    while True:
        resp = input(f"[PROMPT] Run step '{step_name}'? (y/n/exit): ").strip().lower()
        if resp in ("y", "n", "exit"): return resp
        print("Please enter 'y', 'n', or 'exit'.")

# Step 0: Run TITAN Main Pipeline (titan_main.py)
resp = prompt_step("Run TITAN Main Pipeline (titan_main.py)")
if resp == "y":
    print("[INFO] Starting: TITAN Main Pipeline (titan_main.py)")
    titan_main_path = os.path.join(BASE_DIR, "titan_main.py")
    titan_main_cmd = [sys.executable, titan_main_path]
    print(f"[INFO] Running: {' '.join(titan_main_cmd)}")
    try:
        subprocess.run(titan_main_cmd, check=True)
        print("[SUCCESS] TITAN main pipeline completed.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] TITAN main pipeline failed: {e}")
        sys.exit(1)
elif resp == "exit":
    print("[INFO] Exiting pipeline at user request.")
    sys.exit(0)

# Step 1: Harvest Match Data
resp = prompt_step("Harvest Match Data (basic results, teams, scores, 2025)")
if resp == "y":
    print("[INFO] Starting: Harvest Match Data (basic results, teams, scores, 2025)")
    run_2025_updates_cmd = [sys.executable, "titan2.5+_processor/utilities/match_data_select.py", "--year", str(YEAR), "--rounds", str(ROUND), "--type", COMP_TYPE]
    print(f"[INFO] Running: {' '.join(run_2025_updates_cmd)}")
    try:
        subprocess.run(run_2025_updates_cmd, check=True)
        print("[SUCCESS] Match data harvesting complete.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Match data harvesting failed: {e}")
        sys.exit(1)
elif resp == "exit":
    print("[INFO] Exiting pipeline at user request.")
    sys.exit(0)

# Step 2: Harvest Detailed Match Data
resp = prompt_step("Harvest Detailed Match Data (in-depth stats, play-by-play, 2025)")
if resp == "y":
    print("[INFO] Starting: Harvest Detailed Match Data (in-depth stats, play-by-play, 2025)")
    run_2025_updates_cmd = [sys.executable, "titan2.5+_processor/utilities/match_data_detailed_select.py", "--year", str(YEAR), "--rounds", str(ROUND), "--type", COMP_TYPE]
    print(f"[INFO] Running: {' '.join(run_2025_updates_cmd)}")
    try:
        subprocess.run(run_2025_updates_cmd, check=True)
        print("[SUCCESS] Detailed match data harvesting complete.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Detailed match data harvesting failed: {e}")
        sys.exit(1)
    # --- NEW STEP: Rebuild/Clean Detailed Match Data ---
    resp_rebuild = prompt_step("Rebuild/Clean Detailed Match Data (utilities/rebuild_detailed_match_data.py)")
    if resp_rebuild == "y":
        print("[INFO] Running: Rebuild/Clean Detailed Match Data (utilities/rebuild_detailed_match_data.py)")
        rebuild_script = os.path.join("titan2.5+_processor", "utilities", "rebuild_detailed_match_data.py")
        rebuild_cmd = [sys.executable, rebuild_script]
        print(f"[INFO] Running: {' '.join(rebuild_cmd)}")
        try:
            subprocess.run(rebuild_cmd, check=True)
            print("[SUCCESS] Detailed match data rebuild/clean complete.")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Detailed match data rebuild/clean failed: {e}")
            sys.exit(1)
    elif resp_rebuild == "exit":
        print("[INFO] Exiting pipeline at user request.")
        sys.exit(0)
elif resp == "exit":
    print("[INFO] Exiting pipeline at user request.")
    sys.exit(0)

# Step 3: Harvest Player Stats
resp = prompt_step("Harvest Player Stats (individual player statistics, 2025)")
if resp == "y":
    print("[INFO] Starting: Harvest Player Stats (individual player statistics, 2025)")
    run_2025_updates_cmd = [sys.executable, "titan2.5+_processor/utilities/player_data_select.py", "--year", str(YEAR), "--round", str(ROUND), "--type", COMP_TYPE]
    print(f"[INFO] Running: {' '.join(run_2025_updates_cmd)}")
    try:
        subprocess.run(run_2025_updates_cmd, check=True)
        print("[SUCCESS] Player stats harvesting complete.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Player stats harvesting failed: {e}")
        sys.exit(1)
elif resp == "exit":
    print("[INFO] Exiting pipeline at user request.")
    sys.exit(0)

# Step 4: Harvest Detailed Player Stats (if you have a script for this)
detailed_player_stats_script = os.path.join('titan2.5+_processor', 'nrl_data_main', 'scraping', 'player_data_detailed_select.py')
if os.path.exists(detailed_player_stats_script):
    resp = prompt_step("Harvest Detailed Player Stats (advanced per-player stats, 2025)")
    if resp == "y":
        print("[INFO] Starting: Harvest Detailed Player Stats (advanced per-player stats, 2025)")
        run_2025_updates_cmd = [sys.executable, detailed_player_stats_script, "--year", str(YEAR), "--round", str(ROUND), "--type", COMP_TYPE]
        print(f"[INFO] Running: {' '.join(run_2025_updates_cmd)}")
        try:
            subprocess.run(run_2025_updates_cmd, check=True)
            print("[SUCCESS] Detailed player stats harvesting complete.")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Detailed player stats harvesting failed: {e}")
            sys.exit(1)
    elif resp == "exit":
        print("[INFO] Exiting pipeline at user request.")
        sys.exit(0)
else:
    print("[INFO] Skipping 'Harvest Detailed Player Stats' step: player_data_detailed_select.py not found.")

# Step 5: Flatten/process raw data
if prompt_step("FLATTENING DATA") == "y":
    print("\n=== STEP 5: FLATTENING DATA ===\n")
    flatten_cmd = [sys.executable, "flatten_nrl_data.py"]
    print(f"[INFO] Running: {' '.join(flatten_cmd)}")
    try:
        subprocess.run(flatten_cmd, check=True)
        print("[SUCCESS] Data flattening completed.")
        # Debug output files
        debug_file_info(os.path.join("outputs", "all_matches_2019_2025.csv"))
        debug_file_info(os.path.join("outputs", "player_stats_2025.csv"))
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Data flattening failed: {e}")
        sys.exit(1)
    output_path = os.path.join('outputs', f'coach_impact_analysis_round{ROUND}.csv')
    coach_analysis_path = os.path.join(BASE_DIR, 'titan2.5+_processor', 'utilities', 'coach_impact_analysis.py')
    fixtures_path = os.path.join('outputs', f'upcoming_fixtures_and_officials_{YEAR}_round{ROUND}.csv')
    if not os.path.exists(fixtures_path):
        print(f"[WARN] Fixtures file not found: {fixtures_path}")
    elif not os.path.exists(coach_analysis_path):
        print(f"[WARN] coach_impact_analysis.py not found: {coach_analysis_path}")
    else:
        print(f"[INFO] Running coach impact analysis for round {ROUND}...")
        import importlib.util
        import pandas as pd
        spec = importlib.util.spec_from_file_location("coach_impact_analysis", coach_analysis_path)
        coach_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(coach_mod)
        fixtures = pd.read_csv(fixtures_path)
        results = []
        for _, row in fixtures.iterrows():
            home = row['HomeTeam'] if 'HomeTeam' in row else None
            away = row['AwayTeam'] if 'AwayTeam' in row else None
            if home and away:
                res = coach_mod.compare_coach_matchup(home, away)
                results.append({
                    'HomeTeam': home,
                    'AwayTeam': away,
                    'CoachMatchupSummary': res.get('summary', ''),
                    'HomeCoachDesc': res.get('home_desc', ''),
                    'AwayCoachDesc': res.get('away_desc', ''),
                    'TacticalEdge': res.get('tactical_edge', '')
                })
        if results:
            df = pd.DataFrame(results)
            df.to_csv(output_path, index=False)
            print(f"[SUCCESS] Coach impact analysis exported to {output_path}")
        else:
            print("[WARN] No coach matchup results generated.")
    # Step 5.5: Run Ref Analysis (Half/Tries/Team Stats)
    resp = prompt_step("Run Ref Analysis (utilities/ref_analysis.py)")
    if resp == "y":
        print("[INFO] Running: Ref Analysis (utilities/ref_analysis.py)")
        ref_analysis_script = os.path.join("titan2.5+_processor", "utilities", "ref_analysis.py")
        ref_analysis_cmd = [sys.executable, ref_analysis_script]
        print(f"[INFO] Running: {' '.join(ref_analysis_cmd)}")
        try:
            subprocess.run(ref_analysis_cmd, check=True)
            print("[SUCCESS] Ref analysis complete.")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Ref analysis failed: {e}")
            sys.exit(1)
    elif resp == "exit":
        print("[INFO] Exiting pipeline at user request.")
        sys.exit(0)
elif prompt_step("COACH IMPACT ANALYSIS (generate coach matchup insights)") == "exit":
    print("[INFO] Exiting pipeline at user request.")
    sys.exit(0)

print("\n=== ALL STEPS COMPLETE ===\n")

# Step 6: Teamlist-Based Predictions
if prompt_step("TEAMLIST-BASED PREDICTIONS (build_teamlist_based_predictions.py)") == "y":
    print("\n=== STEP 6: TEAMLIST-BASED PREDICTIONS ===\n")
    teamlist_pred_script = os.path.join(BASE_DIR, "titan2.5+_processor", "utilities", "build_teamlist_based_predictions.py")
    if os.path.exists(teamlist_pred_script):
        teamlist_pred_cmd = [sys.executable, teamlist_pred_script]
        print(f"[INFO] Running: {' '.join(teamlist_pred_cmd)}")
        try:
            subprocess.run(teamlist_pred_cmd, check=True)
            print("[SUCCESS] Teamlist-based predictions completed.")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Teamlist-based predictions failed: {e}")
    else:
        print(f"[ERROR] Script not found: {teamlist_pred_script}")
