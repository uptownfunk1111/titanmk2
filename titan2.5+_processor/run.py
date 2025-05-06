"""
Master NRL Data Update and Prediction Runner
Runs scraping, data processing, and prediction in sequence.
"""
import subprocess
import sys

# User-configurable parameters
YEARS = '2019-2025'
ROUND = 10  # Update as the season progresses
COMP_TYPE = 'NRL'

print("\n==============================")
print("[RUNNER] NRL Data Pipeline Start")
print(f"[INFO] Years: {YEARS}, Round: {ROUND}, Comp: {COMP_TYPE}")
print("==============================\n")

# Step 1: Scrape latest data
scrape_cmd = [
    sys.executable, "titan2.5+_processor/scraping/downloader.py",
    "--years", YEARS, "--type", COMP_TYPE
]
print("\n=== STEP 1: SCRAPING DATA ===\n")
print(f"[INFO] Running: {' '.join(scrape_cmd)}")
try:
    subprocess.run(scrape_cmd, check=True)
    print("[SUCCESS] Data scraping completed.")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Data scraping failed: {e}")
    sys.exit(1)

# Step 2: Flatten or process raw data
print("\n=== STEP 2: FLATTENING DATA ===\n")
flatten_cmd = [sys.executable, "flatten_nrl_data.py"]
print(f"[INFO] Running: {' '.join(flatten_cmd)}")
try:
    subprocess.run(flatten_cmd, check=True)
    print("[SUCCESS] Data flattening completed.")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Data flattening failed: {e}")
    sys.exit(1)

# Step 3: Run prediction/model pipeline
print("\n=== STEP 3: RUNNING PREDICTIONS ===\n")
prediction_cmd = [
    sys.executable, "titan2.5+_processor/new_prediction_models/predictor_ml.py"
]
print(f"[INFO] Running: {' '.join(prediction_cmd)}")
try:
    subprocess.run(prediction_cmd, check=True)
    print("[SUCCESS] Prediction/model pipeline completed.")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Prediction/model pipeline failed: {e}")
    sys.exit(1)

print("\n==============================")
print("[RUNNER] All steps complete.")
print("==============================\n")
