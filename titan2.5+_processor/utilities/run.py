"""
Master NRL Data Update and Prediction Runner
Runs fixture/officials/teamlist scraping, data scraping, flattening, and prediction in sequence.
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
FETCH_FIXTURES_SCRIPT = os.path.join(BASE_DIR, '..', '..', 'fetch_upcoming_fixtures_and_officials.py')
SCRAPING_SCRIPT = os.path.join(BASE_DIR, '..', 'nrl_data_main', 'scraping', 'update_nrl_data.py')
FLATTEN_SCRIPT = os.path.join(BASE_DIR, 'utilities', 'flatten_nrl_data.py')
PREDICT_SCRIPT = os.path.join(BASE_DIR, 'titan2.5+_processor', 'new_prediction_models', 'predictor_ml.py')
OUTPUTS_DIR = os.path.join(BASE_DIR, '..', '..', 'outputs')

# Step 0: Fetch fixtures, officials, and team lists for the upcoming round
print("\n=== STEP 0: FETCHING FIXTURES, OFFICIALS, AND TEAM LISTS ===\n")
fixtures_output = os.path.join(OUTPUTS_DIR, f"upcoming_fixtures_and_officials_{YEAR}_round{ROUND}.csv")
fetch_fixtures_cmd = [
    sys.executable, FETCH_FIXTURES_SCRIPT,
    "--year", str(YEAR), "--round", str(ROUND), "--output", fixtures_output
]
subprocess.run(fetch_fixtures_cmd, check=True)

# Step 1: Scrape latest data
print("\n=== STEP 1: SCRAPING DATA ===\n")
scrape_cmd = [
    sys.executable, SCRAPING_SCRIPT,
    "--year", str(YEAR), "--round", str(ROUND), "--type", COMP_TYPE
]
subprocess.run(scrape_cmd, check=True)

# Step 2: Flatten/process raw data
print("\n=== STEP 2: FLATTENING DATA ===\n")
flatten_cmd = [
    sys.executable, FLATTEN_SCRIPT,
    "--year", str(YEAR), "--type", COMP_TYPE
]
subprocess.run(flatten_cmd, check=True)

# Step 3: Run prediction/model pipeline
print("\n=== STEP 3: RUNNING PREDICTIONS ===\n")
prediction_cmd = [
    sys.executable, PREDICT_SCRIPT
]
subprocess.run(prediction_cmd, check=True)

print("\n=== ALL STEPS COMPLETE ===\n")
