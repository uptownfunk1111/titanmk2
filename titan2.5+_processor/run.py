"""
Master NRL Data Update and Prediction Runner
Runs scraping, data processing, and prediction in sequence.
"""
import subprocess
import sys
from datetime import datetime

# User-configurable parameters
YEARS = '2019-2025'
ROUND = 10  # Update as the season progresses
COMP_TYPE = 'NRL'

print("\n==============================")
print("[RUNNER] NRL Data Pipeline Start")
print(f"[INFO] Years: {YEARS}, Round: {ROUND}, Comp: {COMP_TYPE}")
print("==============================\n")

# Step 0: Fetch latest team lists
print("\n=== STEP 0: FETCHING LATEST TEAM LISTS ===\n")
teamlist_cmd = [sys.executable, "fetch_upcoming_teamlists.py"]
print(f"[INFO] Running: {' '.join(teamlist_cmd)}")
try:
    subprocess.run(teamlist_cmd, check=True)
    print("[SUCCESS] Team lists fetched.")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Team list fetching failed: {e}")
    # Optionally: sys.exit(1)

# Step 0b: Fetch upcoming fixtures, officials, and team lists for the current round
print("\n=== STEP 0b: FETCHING UPCOMING FIXTURES, OFFICIALS, AND TEAM LISTS ===\n")
current_year = datetime.now().year
current_round = ROUND  # Uses the ROUND variable defined earlier in run.py
fixtures_cmd = [
    sys.executable, "utilities/fetch_upcoming_fixtures_and_officials.py",
    "--year", str(current_year),
    "--round", str(current_round)
]
print(f"[INFO] Running: {' '.join(fixtures_cmd)}")
try:
    subprocess.run(fixtures_cmd, check=True)
    print("[SUCCESS] Upcoming fixtures, officials, and team lists fetched.")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Fetching upcoming fixtures/officials failed: {e}")
    # Optionally: sys.exit(1)

# Step 0c: Build player impact scores for use in predictions
print("\n=== STEP 0c: BUILDING PLAYER IMPACT SCORES ===\n")
impact_cmd = [sys.executable, "utilities/build_player_impact_scores.py"]
print(f"[INFO] Running: {' '.join(impact_cmd)}")
try:
    subprocess.run(impact_cmd, check=True)
    print("[SUCCESS] Player impact scores built.")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Player impact score build failed: {e}")
    # Optionally: sys.exit(1)

# Step 0d: Build teamlist-based predictions for the upcoming round
print("\n=== STEP 0d: BUILDING TEAMLIST-BASED PREDICTIONS ===\n")
teamlist_pred_cmd = [sys.executable, "build_teamlist_based_predictions.py"]
print(f"[INFO] Running: {' '.join(teamlist_pred_cmd)}")
try:
    subprocess.run(teamlist_pred_cmd, check=True)
    print("[SUCCESS] Teamlist-based predictions built.")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Teamlist-based prediction build failed: {e}")
    # Optionally: sys.exit(1)

# Step 0e: Officiating impact and risk analysis
print("\n=== STEP 0e: OFFICIATING IMPACT AND RISK ANALYSIS ===\n")
officiating_cmd = [sys.executable, "officiating_impact_analysis.py"]
print(f"[INFO] Running: {' '.join(officiating_cmd)}")
try:
    subprocess.run(officiating_cmd, check=True)
    print("[SUCCESS] Officiating impact analysis complete.")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Officiating impact analysis failed: {e}")
    # Optionally: sys.exit(1)

# Step 0f: Generate this week's tips for the upcoming round
print("\n=== STEP 0f: GENERATING THIS WEEK'S TIPS ===\n")
tips_cmd = [sys.executable, "this_weeks_tips.py"]
print(f"[INFO] Running: {' '.join(tips_cmd)}")
try:
    subprocess.run(tips_cmd, check=True)
    print("[SUCCESS] This week's tips generated.")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] This week's tips generation failed: {e}")
    # Optionally: sys.exit(1)

# Step 0g: Kick Target Mapping (KTM) Analysis
print("\n=== STEP 0g: KICK TARGET MAPPING (KTM) ANALYSIS ===\n")
ktm_cmd = [sys.executable, "kick_target_mapping.py"]
print(f"[INFO] Running: {' '.join(ktm_cmd)}")
try:
    subprocess.run(ktm_cmd, check=True)
    print("[SUCCESS] Kick Target Mapping analysis complete.")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Kick Target Mapping analysis failed: {e}")
    # Optionally: sys.exit(1)

# Step 0h: Player Injury Impact Analysis
print("\n=== STEP 0h: PLAYER INJURY IMPACT ANALYSIS ===\n")
injury_impact_cmd = [sys.executable, "player_injury_impact.py"]
print(f"[INFO] Running: {' '.join(injury_impact_cmd)}")
try:
    subprocess.run(injury_impact_cmd, check=True)
    print("[SUCCESS] Player injury impact analysis complete.")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Player injury impact analysis failed: {e}")
    # Optionally: sys.exit(1)

# Step 0i: Weather Impact Analysis
print("\n=== STEP 0i: WEATHER IMPACT ANALYSIS ===\n")
weather_impact_cmd = [sys.executable, "weather_impact_analysis.py"]
print(f"[INFO] Running: {' '.join(weather_impact_cmd)}")
try:
    subprocess.run(weather_impact_cmd, check=True)
    print("[SUCCESS] Weather impact analysis complete.")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Weather impact analysis failed: {e}")
    # Optionally: sys.exit(1)

# Step 0j: Opponent Analysis and Adaptation
print("\n=== STEP 0j: OPPONENT ANALYSIS AND ADAPTATION ===\n")
opponent_analysis_cmd = [sys.executable, "opponent_analysis.py"]
print(f"[INFO] Running: {' '.join(opponent_analysis_cmd)}")
try:
    subprocess.run(opponent_analysis_cmd, check=True)
    print("[SUCCESS] Opponent analysis complete.")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Opponent analysis failed: {e}")
    # Optionally: sys.exit(1)

# Step 0k: Prediction Confidence and Uncertainty Modeling
print("\n=== STEP 0k: PREDICTION CONFIDENCE AND UNCERTAINTY MODELING ===\n")
pred_conf_cmd = [sys.executable, "prediction_confidence.py"]
print(f"[INFO] Running: {' '.join(pred_conf_cmd)}")
try:
    subprocess.run(pred_conf_cmd, check=True)
    print("[SUCCESS] Prediction confidence and uncertainty modeling complete.")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Prediction confidence and uncertainty modeling failed: {e}")
    # Optionally: sys.exit(1)

# Step 0l: Team Lineup Impact Analysis
print("\n=== STEP 0l: TEAM LINEUP IMPACT ANALYSIS ===\n")
lineup_impact_cmd = [sys.executable, "lineup_impact.py"]
print(f"[INFO] Running: {' '.join(lineup_impact_cmd)}")
try:
    subprocess.run(lineup_impact_cmd, check=True)
    print("[SUCCESS] Team lineup impact analysis complete.")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Team lineup impact analysis failed: {e}")
    # Optionally: sys.exit(1)

# Step 1: Scrape latest data using the main scraping runner
scrape_cmd = [
    sys.executable, "titan2.5+_processor/nrl_data_main/scraping/run.py"
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
