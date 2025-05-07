"""
Master NRL Data Update and Prediction Runner
Runs scraping, data processing, and prediction in sequence.
"""

# TITAN NRL Data Pipeline
# This program manages the end-to-end workflow for NRL data: harvesting, flattening/normalising, machine learning predictions, and reporting. It allows you to control which stage to start from, prevents accidental data overwrites, and groups steps for clarity.
#
# Sections:
# [A] Data Harvesting: Collects raw match, detailed match, and player stats data.
# [B] Data Flattening/Normalising: Processes and normalises raw data for ML.
# [C] Machine Learning: Runs prediction models on processed data.
# [D] Output/Reporting: Generates tactical tipping tables and reports.
#
# You will be prompted to select a starting stage and confirm overwrites if data exists.

import subprocess
import sys
import os
from datetime import datetime
import logging
from colorama import init, Fore, Style
import json

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

def debug_file_info(filepath, nrows=3):
    if os.path.exists(filepath):
        try:
            import pandas as pd
            df = pd.read_csv(filepath)
            print_info(f"[DEBUG] {filepath}: rows={len(df)}, columns={list(df.columns)}")
            print_info(f"[DEBUG] Sample data from {filepath}:\n{df.head(nrows)}")
        except Exception as e:
            print_warn(f"[DEBUG] Could not read {filepath}: {e}")
    else:
        print_warn(f"[DEBUG] File not found: {filepath}")

COMP_TYPE = 'NRL'

# Check for existing 2025 data
nrl_data_path = os.path.join(os.path.dirname(__file__), 'nrl_data_main', 'data', 'NRL', '2025', 'NRL_data_2025.json')
existing_round = None
if os.path.exists(nrl_data_path):
    try:
        with open(nrl_data_path, 'r', encoding='utf-8') as f:
            nrl_data = json.load(f)
        rounds = nrl_data.get('NRL', [{}])[0].get('2025', [])
        # Find the highest round number with data
        round_numbers = []
        for r in rounds:
            for k in r.keys():
                try:
                    round_numbers.append(int(k))
                except Exception:
                    pass
        if round_numbers:
            existing_round = max(round_numbers)
    except Exception as e:
        print_warn(f"[WARN] Could not parse existing 2025 data: {e}")

if existing_round:
    print_info(f"[INFO] Existing 2025 data found up to round {existing_round}.")
    print_info(f"[INFO] The most recent NRL round in the data is round {existing_round}.")
    while True:
        resp = input("Do you want to re-import and overwrite the existing 2025 data? (y/n): ").strip().lower()
        if resp == 'y':
            print_info("[INFO] Proceeding to stage selection. You may choose a data harvesting stage.")
            stage_min = 1  # Allow all stages
            break
        elif resp == 'n':
            print_warn("You should choose to start the script at a section beyond data harvesting.")
            print_warn("Proceeding to stage selection from flattening onwards.")
            stage_min = 4  # Only allow stages 4 and above
            break
        else:
            print_warn("Please enter 'y' or 'n'.")
else:
    stage_min = 1

# Prompt user for current round (move to very top for visibility)
try:
    default_round = 10  # You can set a better default if you know it
    print("\n==============================")
    print("[RUNNER] NRL Data Pipeline Start")
    print("==============================\n")
    user_input = input("[PROMPT] Enter the current NRL round (default: 10): ").strip()
    ROUND = int(user_input) if user_input.isdigit() else default_round
except Exception:
    ROUND = 10
print(f"[INFO] Using round: {ROUND} for all harvesting steps.\n")

# Pipeline stages (with brackets)
pipeline_stages = [
    "[A] Harvest Match Data (2025)",
    "[A] Harvest Detailed Match Data (2025)",
    "[A] Harvest Player Stats (2025)",
    "[B] Flatten Data",
    "[B] Normalise/Process Data",  # New explicit stage for normalising/processing
    "[C] Run Prediction Model",
    "[D] Generate Tactical Tipping Table"
]

print("\nPipeline Stages:")
for idx, stage in enumerate(pipeline_stages, 1):
    if idx >= stage_min:
        print(f"  {idx}: {stage}")
while True:
    start_stage_input = input(f"\n[SELECT] Enter the number of the stage to start from ({stage_min}-7, default {stage_min}): ").strip()
    if not start_stage_input:
        start_stage = stage_min
        break
    if start_stage_input.isdigit() and stage_min <= int(start_stage_input) <= len(pipeline_stages):
        start_stage = int(start_stage_input)
        break
    print_warn(f"Please enter a valid stage number ({stage_min}-7) or press Enter for {stage_min}.")

print_info("\n==============================")
print_info("[RUNNER] NRL Data Pipeline Start")
print_info(f"[INFO] Round: {ROUND}, Comp: {COMP_TYPE}")
print_info("[INFO] Only 2025 data will be refreshed in this run.")
print_info("==============================\n")

try:
    base_dir = os.path.dirname(__file__)
    current_stage = 1
    # Step 1: Harvest Match Data
    if current_stage >= start_stage and prompt_step("Harvest Match Data (2025)") == "y":
        script_path = os.path.join(base_dir, "nrl_data_main", "scraping", "match_data_select.py")
        cmd = [sys.executable, script_path, "--year", "2025", "--rounds", str(ROUND), "--type", COMP_TYPE]
        print_info(f"[INFO] Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        # Feedback: count matches in output JSON
        try:
            data_dir = os.path.join(base_dir, 'nrl_data_main', 'data', COMP_TYPE, '2025')
            match_file = os.path.join(data_dir, f"{COMP_TYPE}_data_2025.json")
            with open(match_file, 'r', encoding='utf-8') as f:
                match_data = json.load(f)
            matches = match_data.get(COMP_TYPE, [{}])[0].get('2025', [])
            total_matches = sum(len(r.get(str(i+1), [])) for i, r in enumerate(matches))
            print_success(f"[FEEDBACK] Total matches harvested: {total_matches}")
        except Exception as e:
            print_warn(f"[WARN] Could not count harvested matches: {e}")
        print(Fore.MAGENTA + "\n🏉-------------------🏉\n" + Style.RESET_ALL)
        print(Fore.GREEN + "✅ Step 1 complete! Moving to Step 2..." + Style.RESET_ALL)
    elif current_stage >= start_stage and prompt_step("Harvest Match Data (2025)") == "exit":
        sys.exit(0)
    current_stage += 1

    # Step 2: Harvest Detailed Match Data
    if current_stage >= start_stage and prompt_step("Harvest Detailed Match Data (2025)") == "y":
        script_path = os.path.join(base_dir, "nrl_data_main", "scraping", "match_data_detailed_select.py")
        cmd = [sys.executable, script_path, "--year", "2025", "--rounds", str(ROUND), "--type", COMP_TYPE]
        print_info(f"[INFO] Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        # Feedback: count detailed matches in output JSON
        try:
            data_dir = os.path.join(base_dir, 'nrl_data_main', 'data', COMP_TYPE, '2025')
            detailed_file = os.path.join(data_dir, f"{COMP_TYPE}_detailed_match_data_2025.json")
            with open(detailed_file, 'r', encoding='utf-8') as f:
                detailed_data = json.load(f)
            detailed_matches = detailed_data.get(COMP_TYPE, [])
            total_detailed = sum(len(list(r.values())[0]) for r in detailed_matches)
            print_success(f"[FEEDBACK] Total detailed matches harvested: {total_detailed}")
        except Exception as e:
            print_warn(f"[WARN] Could not count detailed matches: {e}")
        print(Fore.MAGENTA + "\n🏉-------------------🏉\n" + Style.RESET_ALL)
        print(Fore.GREEN + "✅ Step 2 complete! Moving to Step 3..." + Style.RESET_ALL)
    elif current_stage >= start_stage and prompt_step("Harvest Detailed Match Data (2025)") == "exit":
        sys.exit(0)
    current_stage += 1

    # Step 3: Harvest Player Stats
    if current_stage >= start_stage and prompt_step("Harvest Player Stats (2025)") == "y":
        script_path = os.path.join(base_dir, "nrl_data_main", "scraping", "player_data_select.py")
        cmd = [sys.executable, script_path, "--year", "2025", "--rounds", str(ROUND), "--type", COMP_TYPE]
        print_info(f"[INFO] Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        # Feedback: count player stats in output JSON
        try:
            data_dir = os.path.join(base_dir, 'nrl_data_main', 'data', COMP_TYPE, '2025')
            player_file = os.path.join(data_dir, f"{COMP_TYPE}_player_statistics_2025.json")
            with open(player_file, 'r', encoding='utf-8') as f:
                player_data = json.load(f)
            player_stats = player_data.get('PlayerStats', [{}])[0].get('2025', [])
            total_players = 0
            for round_entry in player_stats:
                for round_results in round_entry.values():
                    for match in round_results:
                        for players in match.values():
                            total_players += len(players)
            print_success(f"[FEEDBACK] Total player stats harvested: {total_players}")
        except Exception as e:
            print_warn(f"[WARN] Could not count player stats: {e}")
        print(Fore.MAGENTA + "\n🏉-------------------🏉\n" + Style.RESET_ALL)
        print(Fore.GREEN + "✅ Step 3 complete! Moving to Step 4..." + Style.RESET_ALL)
    elif current_stage >= start_stage and prompt_step("Harvest Player Stats (2025)") == "exit":
        sys.exit(0)
    current_stage += 1

    # Step 4: Flatten Data
    if current_stage >= start_stage and prompt_step("Flatten Data") == "y":
        flatten_script = os.path.join(os.path.dirname(base_dir), "flatten_nrl_data.py")
        flatten_player_stats_script = os.path.join(base_dir, "flatten_player_stats.py")
        # Run match flattening
        print_info(f"[INFO] Running: {sys.executable} {flatten_script}")
        subprocess.run([sys.executable, flatten_script], check=True)
        # Run player stats flattening (ensures player_stats_2025.csv is created in the correct location)
        print_info(f"[INFO] Running: {sys.executable} {flatten_player_stats_script}")
        subprocess.run([sys.executable, flatten_player_stats_script], check=True)
        # Debug output files
        debug_file_info(os.path.join(base_dir, 'outputs', 'all_matches_2019_2025.csv'))
        debug_file_info(os.path.join(base_dir, 'outputs', 'player_stats_2025.csv'))
        print(Fore.MAGENTA + "\n🏉-------------------🏉\n" + Style.RESET_ALL)
        print(Fore.GREEN + "✅ Step 4 complete! Moving to Step 5..." + Style.RESET_ALL)
    elif current_stage >= start_stage and prompt_step("Flatten Data") == "exit":
        sys.exit(0)
    current_stage += 1

    # Step 5: Normalise/Process Data
    if current_stage >= start_stage and prompt_step("Normalise/Process Data") == "y":
        normalise_script = os.path.join(base_dir, "normalise_nrl_data.py")
        cmd = [sys.executable, normalise_script]
        print_info(f"[INFO] Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        # Debug output files
        debug_file_info(os.path.join(base_dir, '..', 'outputs', 'normalised_all_matches_2019_2025.csv'))
        print(Fore.MAGENTA + "\n🏉-------------------🏉\n" + Style.RESET_ALL)
        print(Fore.GREEN + "✅ Step 5 complete! Moving to Step 6..." + Style.RESET_ALL)
    elif current_stage >= start_stage and prompt_step("Normalise/Process Data") == "exit":
        sys.exit(0)
    current_stage += 1

    # Step 6: Run Prediction Model
    if current_stage >= start_stage and prompt_step("Run Prediction Model") == "y":
        print_info("\n[COMMAND] Commander, confirm: All feature enhancement modules will be loaded into the predictive modelling arsenal.\n")
        confirm_enhancements = input(Fore.YELLOW + "[PROMPT] Do you wish to proceed with loading all feature enhancements for maximum tactical advantage? (y/n): " + Style.RESET_ALL).strip().lower()
        if confirm_enhancements != 'y':
            print_warn("[ABORT] Mission aborted by commander. Returning to base.")
            sys.exit(0)
        print_info("[BRIEFING] Deploying all feature enhancement units. Stand by for integration...")
        feature_scripts = [
            "build_player_impact_scores.py",
            "fetch_upcoming_fixtures_and_officials.py",
            "weather_impact_analysis.py",
            "lineup_impact.py",
            "kick_target_mapping.py",
            "officiating_impact_analysis.py",
            "speculative_data_sweep.py",
            "opponent_analysis.py",
            "player_injury_impact.py",
            "coach_impact_analysis.py",
            "generate_kick_events.py"
        ]
        for script in feature_scripts:
            script_path = os.path.join(base_dir, script)
            if not os.path.exists(script_path):
                script_path = os.path.join(os.path.dirname(base_dir), script)
            if os.path.exists(script_path):
                print_info(f"[TACTICAL] Deploying enhancement: {os.path.basename(script_path)}")
                if os.path.basename(script_path) == "fetch_upcoming_fixtures_and_officials.py":
                    cmd = [sys.executable, script_path, "--year", "2025", "--round", str(ROUND)]
                else:
                    cmd = [sys.executable, script_path]
                subprocess.run(cmd, check=True)
                # Debug output for player impact scores
                if os.path.basename(script_path) == "build_player_impact_scores.py":
                    debug_file_info(os.path.join(base_dir, '..', 'outputs', 'player_impact_scores_2019_2025.csv'))
            else:
                print_warn(f"[INTEL] Enhancement script not found: {script}")
        print_info("\n[MISSION] All enhancements loaded. Commander, the arsenal is ready.")
        # Thematic confirmation prompt before proceeding to Skynet/ML
        print_info(Fore.YELLOW + "\n[COMMAND] Tactical systems report: All enhancement modules are online and operational." + Style.RESET_ALL)
        print_info(Fore.YELLOW + "[COMMAND] Awaiting your final command, Commander. The fate of the round rests in your hands." + Style.RESET_ALL)
        print_info(Fore.CYAN + "[PROMPT] Do you wish to EXECUTE SKYNET and unleash the full predictive arsenal? (y/n): " + Style.RESET_ALL)
        skynet_go = input().strip().lower()
        if skynet_go != 'y':
            print_warn("[ABORT] Skynet launch aborted. Standing down. The future remains unwritten.")
            sys.exit(0)
        print_info("[SKYNET] Skynet is online. Initiating predictive model deployment. Good luck, Commander!\n")
        predictor_script = os.path.join(base_dir, "new_prediction_models", "predictor_ml.py")
        cmd = [sys.executable, predictor_script]
        print_info(f"[INFO] Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print(Fore.MAGENTA + "\n🏉-------------------🏉\n" + Style.RESET_ALL)
        print(Fore.GREEN + "✅ Step 6 complete! Moving to Step 7..." + Style.RESET_ALL)
    elif current_stage >= start_stage and prompt_step("Run Prediction Model") == "exit":
        sys.exit(0)
    current_stage += 1

    # Step 7: Generate Tactical Tipping Table
    if current_stage >= start_stage:
        print_info("\n=== STEP 7: GENERATING TACTICAL TIPPING TABLE ===\n")
        tactical_table_cmd = [sys.executable, "tactical_tipping_table.py"]
        print_info(f"[INFO] Running: {' '.join(tactical_table_cmd)}")
        subprocess.run(tactical_table_cmd, check=True)
        print_success("[SUCCESS] Tactical tipping table generated.")

except KeyboardInterrupt:
    print_warn("\n[STOPPED] Script interrupted by user (Ctrl+C). Exiting gracefully.")
    sys.exit(130)
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
print(Fore.YELLOW + Style.BRIGHT + "\n🏆🎉 Pipeline complete! Check your outputs for results. 🎉🏆\n" + Style.RESET_ALL)
print_info(f"[LINK] Results and outputs are available in: {outputs_dir}")
