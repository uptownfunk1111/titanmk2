"""
Master NRL Data Update and Prediction Runner
Runs scraping, data processing, and prediction in sequence.
"""
import subprocess
import sys

# User-configurable parameters
YEAR = 2025
ROUND = 10  # Update as the season progresses
COMP_TYPE = 'NRL'

# Step 1: Scrape latest data
scrape_cmd = [
    sys.executable, "nrl_data_main/scraping/update_nrl_data.py",
    "--year", str(YEAR), "--round", str(ROUND), "--type", COMP_TYPE
]
print("\n=== STEP 1: SCRAPING DATA ===\n")
subprocess.run(scrape_cmd, check=True)

# Step 2: (Optional) Flatten or process raw data if needed
# Example: subprocess.run([sys.executable, "flatten_nrl_data.py"], check=True)

# Step 3: Run prediction/model pipeline
print("\n=== STEP 2: RUNNING PREDICTIONS ===\n")
prediction_cmd = [
    sys.executable, "titan2.5+_processor/new_prediction_models/predictor_ml.py"
]
subprocess.run(prediction_cmd, check=True)

print("\n=== ALL STEPS COMPLETE ===\n")
