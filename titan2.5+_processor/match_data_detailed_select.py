import os
import json
import logging
import pandas as pd
import numpy as np
from utilities.get_detailed_match_data import get_detailed_nrl_data
from utilities.set_up_driver import set_up_driver
import sys

sys.path.append("..")
import ENVIRONMENT_VARIABLES as EV

def match_data_detailed_select(SELECT_YEAR, SELECT_ROUNDS, SELECTION_TYPE):
    """
    Fetches detailed NRL match data for a given year and number of rounds.
    Args:
        SELECT_YEAR (int): The year to fetch.
        SELECT_ROUNDS (int): Number of rounds to fetch.
        SELECTION_TYPE (str): Competition type (e.g., 'NRL', 'NRLW').
    """
    VARIABLES = ["Year", "Win", "Defense", "Attack", "Margin", "Home", "Versus", "Round"]
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', SELECTION_TYPE, str(SELECT_YEAR)))
    os.makedirs(data_dir, exist_ok=True)
    JSON_FILE_PATH = os.path.join(data_dir, f"{SELECTION_TYPE}_data_{SELECT_YEAR}.json")
    OUTPUT_FILE_PATH = os.path.join(data_dir, f"{SELECTION_TYPE}_detailed_match_data_{SELECT_YEAR}.json")
    selection_mapping = {
        'NRLW': (EV.NRLW_TEAMS, EV.NRLW_WEBSITE),
        'KNOCKON': (EV.KNOCKON_TEAMS, EV.KNOCKON_WEBSITE),
        'HOSTPLUS': (EV.HOSTPLUS_TEAMS, EV.HOSTPLUS_WEBSITE)
    }
    WEBSITE = EV.NRL_WEBSITE
    TEAMS = EV.TEAMS
    TEAMS, WEBSITE = selection_mapping.get(SELECTION_TYPE, (TEAMS, WEBSITE))
    try:
        with open(JSON_FILE_PATH, "r") as file:
            data = json.load(file)[f"{SELECTION_TYPE}"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        logging.error(f"Error loading JSON data: {e}")
        sys.exit(1)
    try:
        years_arr = {SELECT_YEAR: data[0][str(SELECT_YEAR)]}
    except IndexError as e:
        logging.error(f"Error accessing year data: {e}")
        sys.exit(1)
    df = pd.DataFrame(columns=[f"{team} {variable}" for team in TEAMS for variable in VARIABLES])
    def fetch_match_data(driver, game, round_num):
        h_team, a_team = game["Home"], game["Away"]
        game_data = None
        for attempt in range(2):
            try:
                game_data = get_detailed_nrl_data(
                    round=round_num + 1, year=SELECT_YEAR,
                    home_team=h_team.lower(), away_team=a_team.lower(),
                    driver=driver, nrl_website=WEBSITE
                )
                if "match" in game_data:
                    return {f"{h_team} v {a_team}": game_data}
            except Exception as ex:
                logging.warning(f"Attempt {attempt + 1} failed for {h_team} vs {a_team}: {ex}")
        return None
    driver = set_up_driver()
    match_json_datas = []
    for round_num in range(SELECT_ROUNDS):
        try:
            round_data = years_arr[SELECT_YEAR][round_num][str(round_num + 1)]
            round_data_scores = []
            for game in round_data:
                match_data = fetch_match_data(driver, game, round_num)
                if match_data:
                    round_data_scores.append(match_data)
            match_json_datas.append({round_num + 1: round_data_scores})
            with open(OUTPUT_FILE_PATH, "w") as file:
                json.dump({f"{SELECTION_TYPE}": match_json_datas}, file, indent=4)
            logging.info(f"✅ Round {round_num + 1} data saved.")
        except Exception as ex:
            logging.error(f"Error processing round {round_num + 1}: {ex}")
    driver.quit()
    logging.info(f"Final player statistics saved to {OUTPUT_FILE_PATH}")

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    parser = argparse.ArgumentParser(description="NRL Detailed Match Data Scraper")
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--rounds', type=int, required=True)
    parser.add_argument('--type', type=str, default='NRL')
    args = parser.parse_args()
    match_data_detailed_select(args.year, args.rounds, args.type)
