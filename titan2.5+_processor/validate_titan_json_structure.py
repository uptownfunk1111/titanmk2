import os
import json
import logging

BASE_PATH = "./NRL"
YEARS = list(range(2019, 2026))

def validate_json_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load {path}: {e}")
        return None

def validate_match_data(file_path, year):
    logging.info(f"Validating match data: {file_path}")
    data = validate_json_file(file_path)
    if not data or "NRL" not in data:
        logging.error(f"'NRL' key missing in match data for {year}")
        return
    try:
        rounds = data["NRL"][0][str(year)]
        match_count = sum(len(r[r_key]) for r in rounds for r_key in r)
        logging.info(f"Match data OK — {match_count} matches found.")
    except Exception as e:
        logging.error(f"Structure error in match data: {e}")

def validate_player_stats(file_path):
    logging.info(f"Validating player stats: {file_path}")
    data = validate_json_file(file_path)
    if not data or "PlayerStats" not in data:
        logging.error("'PlayerStats' key missing.")
        return
    sample = data["PlayerStats"][:3]
    if not isinstance(sample, list):
        logging.error("'PlayerStats' is not a list.")
        return
    valid_players = 0
    for match in sample:
        if isinstance(match, dict) and "Players" in match:
            valid_players += len(match["Players"])
    logging.info(f"Player stats OK — Players in first 3 matches: {valid_players}")

def validate_detailed_match_data(file_path):
    logging.info(f"Validating detailed match data: {file_path}")
    data = validate_json_file(file_path)
    if not isinstance(data, list):
        logging.error("Expected a list of match entries.")
        return
    valid_entries = 0
    for i, entry in enumerate(data[:5]):
        if isinstance(entry, dict) and "MatchID" in entry and "main_ref" in entry:
            valid_entries += 1
    logging.info(f"Detailed match data OK — {valid_entries}/5 entries structurally valid.")

def validate_all_years():
    logging.info("Starting TITAN JSON Validation...")
    for year in YEARS:
        folder = os.path.join(BASE_PATH, str(year))
        if not os.path.exists(folder):
            logging.warning(f"Folder missing: {folder}")
            continue
        match_file = os.path.join(folder, f"NRL_data_{year}.json")
        player_file = os.path.join(folder, f"NRL_player_statistics_{year}.json")
        detailed_file = os.path.join(folder, f"NRL_detailed_match_data_{year}.json")
        if os.path.exists(match_file):
            validate_match_data(match_file, year)
        else:
            logging.warning(f"Match file missing for {year}")
        if os.path.exists(player_file):
            validate_player_stats(player_file)
        else:
            logging.warning(f"Player stats file missing for {year}")
        if os.path.exists(detailed_file):
            validate_detailed_match_data(detailed_file)
        else:
            logging.warning(f"Detailed file missing for {year}")
    logging.info("Validation complete.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    validate_all_years()
