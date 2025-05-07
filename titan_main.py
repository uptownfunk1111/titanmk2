# titan_main.py

from titan_fetch import fetch_nrl_data
from titan_teamlist import fetch_team_lists
from titan_model import predict_tips
import pandas as pd
from datetime import datetime
import os
import subprocess
import sys

def ensure_output_folder():
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

def save_tips_to_excel(tips):
    df = pd.DataFrame(tips)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    timestamped_path = f"outputs/titan_tips_{now}.xlsx"
    latest_path = "outputs/titan_tips_latest.xlsx"
    
    df.to_excel(timestamped_path, index=False)
    df.to_excel(latest_path, index=False)
    
    print(f"✅ Tips saved to '{timestamped_path}' and 'titan_tips_latest.xlsx'.")

def main():
    print("\n==============================")
    print("[TITAN MAIN] Starting TITAN NRL Data & Prediction Pipeline")
    print("==============================\n")

    # Step 1: Data Download (fully automated overlays)
    print("[STEP 1] Downloading latest NRL data and overlays...")
    scrape_cmd = [
        sys.executable, "titan2.5+_processor/utilities/downloader.py",
        "--years", "2025", "--type", "NRL"
    ]
    print(f"[INFO] Running: {' '.join(scrape_cmd)}")
    try:
        subprocess.run(scrape_cmd, check=True)
        print("[SUCCESS] Data download completed.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Data download failed: {e}")
        return

    # Step 2: Fetch overlays (teamlists, fixtures, refs, weather, etc.)
    print("\n[STEP 2] Fetching overlays and tactical data...")
    try:
        subprocess.run([sys.executable, "fetch_upcoming_fixtures_and_officials.py", "--year", "2025", "--round", "10"], check=True)
        subprocess.run([sys.executable, "titan2.5+_processor/fetch_upcoming_teamlists.py"], check=True)
        subprocess.run([sys.executable, "titan2.5+_processor/lineup_impact.py"], check=True)
        subprocess.run([sys.executable, "titan2.5+_processor/kick_target_mapping.py"], check=True)
        subprocess.run([sys.executable, "titan2.5+_processor/officiating_impact_analysis.py"], check=True)
        subprocess.run([sys.executable, "titan2.5+_processor/weather_impact_analysis.py"], check=True)
        subprocess.run([sys.executable, "titan2.5+_processor/speculative_data_sweep.py"], check=True)
        print("[SUCCESS] Overlay and tactical data fetch completed.")
    except Exception as e:
        print(f"[ERROR] Overlay/tactical data fetch failed: {e}")
        return

    # Step 3: Data Processing
    print("\n[STEP 3] Processing and flattening NRL data...")
    try:
        import process_nrl_data
        process_nrl_data.main()
        print("[SUCCESS] Data processing completed.")
    except Exception as e:
        print(f"[ERROR] Data processing failed: {e}")
        return

    # Step 4: Model Prediction
    print("\n[STEP 4] Running prediction models...")
    try:
        import titan2_5__processor.new_prediction_models.predictor_ml as predictor_ml
        predictor_ml.main()
        print("[SUCCESS] Prediction/model pipeline completed.")
    except Exception as e:
        print(f"[ERROR] Prediction/model pipeline failed: {e}")
        return

    print("\n==============================")
    print("[TITAN MAIN] All steps complete.")
    print("==============================\n")

if __name__ == "__main__":
    main()
