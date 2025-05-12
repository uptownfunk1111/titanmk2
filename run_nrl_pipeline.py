"""
NRL Data Pipeline Orchestrator
- Runs scraping, flattening, processing, feature engineering, modeling, and reporting in order.
- Handles errors and missing files gracefully.
- Runs notebooks programmatically using papermill (install if missing).
- Cross-platform (Windows/PowerShell and Unix shells).

Usage:
    python run_nrl_pipeline.py
"""
import subprocess
import sys
import os
import shutil

def run_step(description, command, check_files=None, is_notebook=False):
    print("\n" + "="*80)
    print(f"[STEP START] {description}")
    print(f"[DEBUG] Command to run: {command}")
    if is_notebook:
        print(f"[DEBUG] Notebook mode: input/output = {command}")
    if check_files:
        print(f"[DEBUG] Will check for output files: {check_files}")
    print("="*80)
    try:
        if is_notebook:
            print(f"[DEBUG] Importing papermill and running notebook...")
            import papermill as pm
            input_path, output_path = command
            print(f"[DEBUG] Executing notebook: {input_path} -> {output_path}")
            pm.execute_notebook(input_path, output_path)
            print(f"[DEBUG] Notebook execution finished: {output_path}")
        else:
            print(f"[DEBUG] Running subprocess: {command}")
            result = subprocess.run(command, shell=True, check=True)
            print(f"[DEBUG] Subprocess finished with return code: {result.returncode}")
        if check_files:
            for f in check_files:
                print(f"[DEBUG] Checking for output file: {f}")
                if not os.path.exists(f):
                    print(f"[ERROR] Expected output file not found: {f}")
                    raise FileNotFoundError(f"Expected output file not found: {f}")
                else:
                    print(f"[DEBUG] Output file found: {f}")
        print(f"[SUCCESS] {description}")
    except Exception as e:
        print(f"[ERROR] {description} failed: {e}")
        print(f"[DEBUG] Exception details:", repr(e))
        sys.exit(1)

def ensure_papermill():
    print("[DEBUG] Checking for papermill installation...")
    try:
        import papermill
        print("[DEBUG] papermill is already installed.")
    except ImportError:
        print("[INFO] papermill not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "papermill"])
        print("[DEBUG] papermill installed successfully.")
        import papermill

if __name__ == "__main__":
    print("\n" + "#"*80)
    print("[START] NRL Data Pipeline Orchestrator")
    print(f"[DEBUG] Python executable: {sys.executable}")
    BASE = os.path.dirname(os.path.abspath(__file__))
    print(f"[DEBUG] Script base directory: {BASE}")
    print("#"*80)
    # 1. Scraping
    print("\n[INFO] Starting Step 1: Data scraping")
    run_step(
        "Data scraping (nrl_data_main/scraping/run.py)",
        f'{sys.executable} "{os.path.join(BASE, "nrl_data_main", "scraping", "run.py")}"',
        check_files=[os.path.join(BASE, "outputs", "all_players_2019_2025.csv"), os.path.join(BASE, "outputs", "all_matches_2019_2025.csv")]
    )
    print("[INFO] Step 1 complete. Proceeding to Step 2.")
    # 2. Flattening
    print("\n[INFO] Starting Step 2: Flattening NRL data")
    run_step(
        "Flatten NRL data (utilities/flatten_nrl_data.py)",
        f'{sys.executable} "{os.path.join(BASE, "utilities", "flatten_nrl_data.py")}"',
        check_files=[os.path.join(BASE, "outputs", "all_players_2019_2025.csv")]
    )
    print("[INFO] Step 2 complete. Proceeding to Step 3.")
    # 3. Processing
    print("\n[INFO] Starting Step 3: Processing NRL data")
    run_step(
        "Process NRL data (utilities/process_nrl_data.py)",
        f'{sys.executable} "{os.path.join(BASE, "utilities", "process_nrl_data.py")}"',
        check_files=[os.path.join(BASE, "outputs", "all_matches_2019_2025.csv")]
    )
    print("[INFO] Step 3 complete. Proceeding to Step 4.")
    # 4. Feature engineering
    print("\n[INFO] Starting Step 4: Build player impact scores")
    run_step(
        "Build player impact scores (utilities/build_player_impact_scores.py)",
        f'{sys.executable} "{os.path.join(BASE, "utilities", "build_player_impact_scores.py")}"',
        check_files=[os.path.join(BASE, "outputs", "player_impact_scores_2019_2025.csv")]
    )
    print("[INFO] Step 4 complete. Proceeding to Step 5.")
    # 5. Modeling (notebook)
    print("\n[INFO] Starting Step 5: Modeling notebook")
    ensure_papermill()
    model_nb = os.path.join(BASE, "nrl_data_main", "predictions", "model_1.ipynb")
    model_nb_out = os.path.join(BASE, "outputs", "model_1_output.ipynb")
    run_step(
        "Run model notebook (nrl_data_main/predictions/model_1.ipynb)",
        (model_nb, model_nb_out),
        is_notebook=True
    )
    print("[INFO] Step 5 complete. Proceeding to Step 6.")
    # 6. Reporting (notebook)
    print("\n[INFO] Starting Step 6: Reporting notebook")
    review_nb = os.path.join(BASE, "nrl_data_main", "player_stats_review.ipynb")
    review_nb_out = os.path.join(BASE, "outputs", "player_stats_review_output.ipynb")
    run_step(
        "Run review notebook (nrl_data_main/player_stats_review.ipynb)",
        (review_nb, review_nb_out),
        is_notebook=True
    )
    print("\n[COMPLETE] NRL Data Pipeline finished. Check the outputs/ directory for results.")
