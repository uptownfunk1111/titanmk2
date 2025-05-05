"""
Master NRL Data Scraping Script
Runs all scraping modules to update match, detailed match, and player data for a given year and round.
"""
import sys
import os

# Ensure the scraping directory is in the path for imports
SCRAPING_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRAPING_DIR)

from match_data_select import match_data_select
from match_data_detailed_select import match_data_detailed_select
from player_data_select import player_data_select

def update_nrl_data(year, round_num, selection_type):
    print(f"\n=== Updating NRL Data for {selection_type} {year} up to Round {round_num} ===\n")
    try:
        print("[1/3] Scraping match data...")
        match_data_select(year, round_num, selection_type)
    except Exception as e:
        print(f"Error in match_data_select: {e}")
    try:
        print("[2/3] Scraping detailed match data...")
        match_data_detailed_select(year, round_num, selection_type)
    except Exception as e:
        print(f"Error in match_data_detailed_select: {e}")
    try:
        print("[3/3] Scraping player data...")
        player_data_select(year, round_num, selection_type)
    except Exception as e:
        print(f"Error in player_data_select: {e}")
    print("\n=== NRL Data Update Complete ===\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Update NRL data for a given year and round.")
    parser.add_argument('--year', type=int, required=True, help='Year to update (e.g. 2025)')
    parser.add_argument('--round', type=int, required=True, help='Latest round to update (e.g. 10)')
    parser.add_argument('--type', type=str, default='NRL', help='Competition type (NRL, HOSTPLUS, etc.)')
    args = parser.parse_args()
    update_nrl_data(args.year, args.round, args.type)
