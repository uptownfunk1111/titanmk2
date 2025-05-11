"""
Script to run the data scraper for match and player data.
"""

import os

from utilities.match_data_select import match_data_select
from utilities.match_data_detailed_select import match_data_detailed_select
from utilities.player_data_select import player_data_select

# Define the selection type for the dataset
# Options: 'NRL', 'NRLW', 'HOSTPLUS', 'KNOCKON'
SELECTION_TYPE = 'NRL'

# Define the years and corresponding rounds to fetch data for
SELECT_YEARS = [2025, 2024, 2023, 2022, 2021, 2019]  # List of years to scrape data for
SELECT_ROUNDS = [33, 33, 33, 33, 33, 33]       # Corresponding rounds for each year

# Loop through each year and its respective round
for year, rounds in zip(SELECT_YEARS, SELECT_ROUNDS):
    print(f"Starting data collection for Year: {year}, Round: {rounds}")

    # Define the directory path for storing scraped data
    directory_path = f"../data/{SELECTION_TYPE}/{year}/"

    # Ensure the directory exists; create it if it doesn't
    os.makedirs(directory_path, exist_ok=True)

    # Call functions to scrape and process match and player data
    match_data_select(year, rounds, SELECTION_TYPE)            # Basic match data
    match_data_detailed_select(year, rounds, SELECTION_TYPE)   # Detailed match data
    player_data_select(year, rounds, SELECTION_TYPE)           # Player statistics

print("Data scraping process completed successfully.")
