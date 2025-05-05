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
SCRAPING_SCRIPT = os.path.join(BASE_DIR, '..', 'nrl_data_main', 'scraping', 'update_nrl_data.py')
FLATTEN_SCRIPT = os.path.join(BASE_DIR, 'utilities', 'flatten_nrl_data.py')
PREDICT_SCRIPT = os.path.join(BASE_DIR, 'titan2.5+_processor', 'new_prediction_models', 'predictor_ml.py')

# Step 1: Scrape latest data
scrape_cmd = [
    sys.executable, SCRAPING_SCRIPT,
    "--year", str(YEAR), "--round", str(ROUND), "--type", COMP_TYPE
]
print("\n=== STEP 1: SCRAPING DATA ===\n")
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
