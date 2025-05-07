"""
Master NRL Data Update and Prediction Runner
Runs scraping, data flattening, and prediction in sequence.
"""
import subprocess
import sys
import os

# User-configurable parameters
YEAR = 2025
ROUND = 10  # Update as the season progresses
COMP_TYPE = 'NRL'

# Get absolute paths for all scripts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRAPING_SCRIPT = os.path.join(BASE_DIR, 'titan2.5+_processor', 'scraping', 'run_2025_updates.py')
FLATTEN_SCRIPT = os.path.join(BASE_DIR, 'flatten_nrl_data.py')
PREDICT_SCRIPT = os.path.join(BASE_DIR, 'titan2.5+_processor', 'new_prediction_models', 'predictor_ml.py')

def prompt_step(step_name):
    while True:
        resp = input(f"[PROMPT] Run step '{step_name}'? (y/n/exit): ").strip().lower()
        if resp in ("y", "n", "exit"): return resp
        print("Please enter 'y', 'n', or 'exit'.")

# Step 1: Harvest Match Data
resp = prompt_step("Harvest Match Data (basic results, teams, scores, 2025)")
if resp == "y":
    run_2025_updates_cmd = [sys.executable, "titan2.5+_processor/nrl_data_main/scraping/match_data_select.py", "--year", str(YEAR), "--rounds", str(ROUND), "--type", COMP_TYPE]
    print(f"[INFO] Running: {' '.join(run_2025_updates_cmd)}")
    subprocess.run(run_2025_updates_cmd, check=True)
elif resp == "exit":
    sys.exit(0)

# Step 2: Harvest Detailed Match Data
resp = prompt_step("Harvest Detailed Match Data (in-depth stats, play-by-play, 2025)")
if resp == "y":
    run_2025_updates_cmd = [sys.executable, "titan2.5+_processor/nrl_data_main/scraping/match_data_detailed_select.py", "--year", str(YEAR), "--rounds", str(ROUND), "--type", COMP_TYPE]
    print(f"[INFO] Running: {' '.join(run_2025_updates_cmd)}")
    subprocess.run(run_2025_updates_cmd, check=True)
elif resp == "exit":
    sys.exit(0)

# Step 3: Harvest Player Stats
resp = prompt_step("Harvest Player Stats (individual player statistics, 2025)")
if resp == "y":
    run_2025_updates_cmd = [sys.executable, "titan2.5+_processor/nrl_data_main/scraping/player_data_select.py", "--year", str(YEAR), "--round", str(ROUND), "--type", COMP_TYPE]
    print(f"[INFO] Running: {' '.join(run_2025_updates_cmd)}")
    subprocess.run(run_2025_updates_cmd, check=True)
elif resp == "exit":
    sys.exit(0)

# Step 4: Harvest Detailed Player Stats (if you have a script for this)
detailed_player_stats_script = os.path.join('titan2.5+_processor', 'nrl_data_main', 'scraping', 'player_data_detailed_select.py')
if os.path.exists(detailed_player_stats_script):
    resp = prompt_step("Harvest Detailed Player Stats (advanced per-player stats, 2025)")
    if resp == "y":
        run_2025_updates_cmd = [sys.executable, detailed_player_stats_script, "--year", str(YEAR), "--round", str(ROUND), "--type", COMP_TYPE]
        print(f"[INFO] Running: {' '.join(run_2025_updates_cmd)}")
        subprocess.run(run_2025_updates_cmd, check=True)
    elif resp == "exit":
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
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Data flattening failed: {e}")
        sys.exit(1)
elif prompt_step("FLATTENING DATA") == "exit":
    sys.exit(0)

# Step 6: Run prediction/model pipeline
if prompt_step("RUNNING PREDICTIONS") == "y":
    print("\n=== STEP 6: RUNNING PREDICTIONS ===\n")
    prediction_cmd = [
        sys.executable, PREDICT_SCRIPT
    ]
    subprocess.run(prediction_cmd, check=True)
elif prompt_step("RUNNING PREDICTIONS") == "exit":
    sys.exit(0)

print("\n=== ALL STEPS COMPLETE ===\n")
