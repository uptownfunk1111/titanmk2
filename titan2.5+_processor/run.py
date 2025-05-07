"""
Master NRL Data Update and Prediction Runner
Runs scraping, data processing, and prediction in sequence.
"""
import subprocess
import sys
import os
from datetime import datetime

def prompt_step(step_name):
    while True:
        resp = input(f"[PROMPT] Run step '{step_name}'? (y/n/exit): ").strip().lower()
        if resp in ("y", "n", "exit"): return resp
        print("Please enter 'y', 'n', or 'exit'.")

COMP_TYPE = 'NRL'
ROUND = 33  # Set your round here

print("\n==============================")
print("[RUNNER] NRL Data Pipeline Start")
print(f"[INFO] Round: {ROUND}, Comp: {COMP_TYPE}")
print("[INFO] Only 2025 data will be refreshed in this run.")
print("==============================\n")

# Step 1: Harvest Match Data
if prompt_step("Harvest Match Data (2025)") == "y":
    cmd = [sys.executable, "titan2.5+_processor/nrl_data_main/scraping/match_data_select.py", "--year", "2025", "--rounds", str(ROUND), "--type", COMP_TYPE]
    print(f"[INFO] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
elif prompt_step("Harvest Match Data (2025)") == "exit":
    sys.exit(0)

# Step 2: Harvest Detailed Match Data
if prompt_step("Harvest Detailed Match Data (2025)") == "y":
    cmd = [sys.executable, "titan2.5+_processor/nrl_data_main/scraping/match_data_detailed_select.py", "--year", "2025", "--rounds", str(ROUND), "--type", COMP_TYPE]
    print(f"[INFO] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
elif prompt_step("Harvest Detailed Match Data (2025)") == "exit":
    sys.exit(0)

# Step 3: Harvest Player Stats
if prompt_step("Harvest Player Stats (2025)") == "y":
    cmd = [sys.executable, "titan2.5+_processor/nrl_data_main/scraping/player_data_select.py", "--year", "2025", "--round", str(ROUND), "--type", COMP_TYPE]
    print(f"[INFO] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
elif prompt_step("Harvest Player Stats (2025)") == "exit":
    sys.exit(0)

# Step 4: Flatten Data
if prompt_step("Flatten Data") == "y":
    cmd = [sys.executable, "flatten_nrl_data.py"]
    print(f"[INFO] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
elif prompt_step("Flatten Data") == "exit":
    sys.exit(0)

# Step 5: Run Prediction Model
if prompt_step("Run Prediction Model") == "y":
    cmd = [sys.executable, "titan2.5+_processor/new_prediction_models/predictor_ml.py"]
    print(f"[INFO] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
elif prompt_step("Run Prediction Model") == "exit":
    sys.exit(0)

print("\n==============================")
print("[RUNNER] All steps complete.")
print("==============================\n")
