"""
This script fetches NRL match data for the selected year and saves it to a JSON file
"""
import os
import sys
import json
import logging
from utilities.get_nrl_data import get_nrl_data
sys.path.append('..')
import ENVIRONMENT_VARIABLES as EV

def match_data_select(SELECT_YEAR, SELECT_ROUNDS, SELECTION_TYPE):
    """
    Fetches NRL match data for a selected year and saves it to a JSON file.
    Args:
        SELECT_YEAR (int): The year to fetch.
        SELECT_ROUNDS (int): Number of rounds to fetch.
        SELECTION_TYPE (str): Competition type (e.g., 'NRL', 'NRLW').
    """
    try:
        COMPETITION_TYPE = EV.COMPETITION[SELECTION_TYPE]
    except (TypeError, KeyError):
        logging.error(f"Unknown Competition Type: {SELECTION_TYPE}")
        return
    logging.info(f"Fetching data for {SELECTION_TYPE} {SELECT_YEAR}...")
    match_json_datas = []
    for year in [SELECT_YEAR]:
        year_json_data = []
        for round_nu in range(1, SELECT_ROUNDS + 1):
            try:
                match_json = get_nrl_data(round_nu, year, COMPETITION_TYPE)
                year_json_data.append(match_json)
            except Exception as ex:
                logging.error(f"Error fetching round {round_nu}: {ex}")
        match_json_datas.append({f"{year}": year_json_data})
    overall_data = {f"{SELECTION_TYPE}": match_json_datas}
    directory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', SELECTION_TYPE, str(SELECT_YEAR)))
    os.makedirs(directory_path, exist_ok=True)
    file_path = os.path.join(directory_path, f"{SELECTION_TYPE}_data_{SELECT_YEAR}.json")
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(overall_data, file, ensure_ascii=False, separators=(',', ':'))
        logging.info(f"Saved match data to: {file_path}")
    except Exception as e:
        logging.error(f"Error writing file: {e}")

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    parser = argparse.ArgumentParser(description="NRL Match Data Scraper")
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--rounds', type=int, required=True)
    parser.add_argument('--type', type=str, default='NRL')
    args = parser.parse_args()
    match_data_select(args.year, args.rounds, args.type)
