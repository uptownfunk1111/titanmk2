"""
Script to run the data scraper for match and player data.
"""

import os
import shutil
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from match_data_select import match_data_select
from match_data_detailed_select import match_data_detailed_select
from player_data_select import player_data_select

# Define the selection type for the dataset
# Options: 'NRL', 'NRLW', 'HOSTPLUS', 'KNOCKON'
SELECTION_TYPE = 'NRL'

# Define the years and corresponding rounds to fetch data for
# Only scrape 2025 data
SELECT_YEARS = [2025]  # Only 2025
SELECT_ROUNDS = [33]   # Update as needed for 2025

# Loop through each year and its respective round
for year, rounds in zip(SELECT_YEARS, SELECT_ROUNDS):
    print(f"Starting data collection for Year: {year}, Round: {rounds}")

    # Define the directory path for storing scraped data
    directory_path = f"../data/{SELECTION_TYPE}/{year}/"
    nrl_data_main_path = f"../nrl_data_main/data/{SELECTION_TYPE}/{year}/"
    os.makedirs(directory_path, exist_ok=True)
    os.makedirs(nrl_data_main_path, exist_ok=True)

    # Call functions to scrape and process match and player data
    match_data_select(year, rounds, SELECTION_TYPE)            # Basic match data
    match_data_detailed_select(year, rounds, SELECTION_TYPE)   # Detailed match data
    player_data_select(year, rounds, SELECTION_TYPE)           # Player statistics

    # Move/copy outputs to nrl_data_main/data/NRL/{year}/ and titan2.5+_processor/outputs/NRL/{year}/
    output_targets = [
        nrl_data_main_path,
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outputs', SELECTION_TYPE, str(year)))
    ]
    for target_path in output_targets:
        os.makedirs(target_path, exist_ok=True)
        # Match data
        src_match = f"../data/{SELECTION_TYPE}/{year}/{SELECTION_TYPE}_data_{year}.json"
        dst_match = os.path.join(target_path, f"{SELECTION_TYPE}_data_{year}.json")
        if os.path.exists(src_match):
            shutil.copy2(src_match, dst_match)
            print(f"[INFO] Copied match data to {dst_match}")
        # Detailed match data
        src_detailed = f"../data/{SELECTION_TYPE}/{year}/{SELECTION_TYPE}_detailed_match_data_{year}.json"
        dst_detailed = os.path.join(target_path, f"{SELECTION_TYPE}_detailed_match_data_{year}.json")
        if os.path.exists(src_detailed):
            shutil.copy2(src_detailed, dst_detailed)
            print(f"[INFO] Copied detailed match data to {dst_detailed}")
        # Player stats
        src_player = f"../data/{SELECTION_TYPE}/{year}/{SELECTION_TYPE}_player_statistics_{year}.json"
        dst_player = os.path.join(target_path, f"{SELECTION_TYPE}_player_statistics_{year}.json")
        if os.path.exists(src_player):
            shutil.copy2(src_player, dst_player)
            print(f"[INFO] Copied player stats to {dst_player}")

print("Data scraping process completed successfully.")
