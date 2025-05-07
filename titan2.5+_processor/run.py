"""
Master NRL Data Update and Prediction Runner
Runs scraping, data processing, and prediction in sequence.
"""
import subprocess
import sys
import os
from datetime import datetime
import logging
from colorama import init, Fore, Style

init(autoreset=True)

# Setup logging
log_path = os.path.join(os.path.dirname(__file__), 'outputs', 'pipeline.log')
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def print_info(msg):
    print(Fore.CYAN + msg)
    logging.info(msg)

def print_success(msg):
    print(Fore.GREEN + msg)
    logging.info(msg)

def print_warn(msg):
    print(Fore.YELLOW + msg)
    logging.warning(msg)

def print_error(msg):
    print(Fore.RED + msg)
    logging.error(msg)

def prompt_step(step_name):
    while True:
        resp = input(Fore.MAGENTA + f"[PROMPT] Run step '{step_name}'? (y/n/exit): " + Style.RESET_ALL).strip().lower()
        if resp in ("y", "n", "exit"): return resp
        print_warn("Please enter 'y', 'n', or 'exit'.")

COMP_TYPE = 'NRL'
ROUND = 33  # Set your round here

print_info("\n==============================")
print_info("[RUNNER] NRL Data Pipeline Start")
print_info(f"[INFO] Round: {ROUND}, Comp: {COMP_TYPE}")
print_info("[INFO] Only 2025 data will be refreshed in this run.")
print_info("==============================\n")

try:
    # Step 1: Harvest Match Data
    if prompt_step("Harvest Match Data (2025)") == "y":
        cmd = [sys.executable, "titan2.5+_processor/nrl_data_main/scraping/match_data_select.py", "--year", "2025", "--rounds", str(ROUND), "--type", COMP_TYPE]
        print_info(f"[INFO] Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    elif prompt_step("Harvest Match Data (2025)") == "exit":
        sys.exit(0)

    # Step 2: Harvest Detailed Match Data
    if prompt_step("Harvest Detailed Match Data (2025)") == "y":
        cmd = [sys.executable, "titan2.5+_processor/nrl_data_main/scraping/match_data_detailed_select.py", "--year", "2025", "--rounds", str(ROUND), "--type", COMP_TYPE]
        print_info(f"[INFO] Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    elif prompt_step("Harvest Detailed Match Data (2025)") == "exit":
        sys.exit(0)

    # Step 3: Harvest Player Stats
    if prompt_step("Harvest Player Stats (2025)") == "y":
        cmd = [sys.executable, "titan2.5+_processor/nrl_data_main/scraping/player_data_select.py", "--year", "2025", "--round", str(ROUND), "--type", COMP_TYPE]
        print_info(f"[INFO] Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    elif prompt_step("Harvest Player Stats (2025)") == "exit":
        sys.exit(0)

    # Step 4: Flatten Data
    if prompt_step("Flatten Data") == "y":
        cmd = [sys.executable, "flatten_nrl_data.py"]
        print_info(f"[INFO] Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    elif prompt_step("Flatten Data") == "exit":
        sys.exit(0)

    # Step 5: Run Prediction Model
    if prompt_step("Run Prediction Model") == "y":
        cmd = [sys.executable, "titan2.5+_processor/new_prediction_models/predictor_ml.py"]
        print_info(f"[INFO] Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    elif prompt_step("Run Prediction Model") == "exit":
        sys.exit(0)

    # Step X: Generate Tactical Tipping Table
    print_info("\n=== STEP X: GENERATING TACTICAL TIPPING TABLE ===\n")
    tactical_table_cmd = [sys.executable, "tactical_tipping_table.py"]
    print_info(f"[INFO] Running: {' '.join(tactical_table_cmd)}")
    subprocess.run(tactical_table_cmd, check=True)
    print_success("[SUCCESS] Tactical tipping table generated.")

except subprocess.CalledProcessError as e:
    print_error(f"[ERROR] Pipeline step failed: {e}")
    print_error("[FATAL] Pipeline terminated due to error. See outputs/pipeline.log for details.")
    sys.exit(1)
except Exception as e:
    print_error(f"[ERROR] Unexpected error: {e}")
    sys.exit(1)

# Print summary of outputs
outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs'))
summary_files = [
    f for f in os.listdir(outputs_dir)
    if f.endswith('.csv') or f.endswith('.json') or f.endswith('.xlsx')
]
print_info("\n==============================")
print_info("[SUMMARY] Pipeline Outputs:")
for f in summary_files:
    print_success(f" - {f}")
print_info("==============================\n")
print_success("[RUNNER] All steps complete.")
