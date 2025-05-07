"""
nrl_downloader.py

This module defines a class for downloading NRL.com draw/fixtures
for a given year and saving them as JSON files.

Requires:
    - requests
    - BeautifulSoup from bs4
"""

import sys
import os
import requests
import json
from typing import List
import subprocess  # <-- Add this import

NRL_API_URL = "https://www.nrl.com/draw/data?competition=111&season={year}"


class NRLDownloader:
    """
    A class used to download NRL.com draw/fixtures for a specific year.

    Attributes
    ----------
    year : int
        The year of the fixtures (e.g., 2023)
    comp_type : str
        The competition type (default is 'NRL')
    base_path : str
        Local directory to store downloaded fixtures
    directory_path : str
        Full path to save files for the given competition and year
    """

    def __init__(self, year, comp_type='NRL', base_path=None):
        """
        Initialize the downloader for a specific year.

        Parameters
        ----------
        year : int
            Year of the fixtures
        comp_type : str, optional
            Competition type (default is 'NRL')
        base_path : str, optional
            Path to save downloaded files (default is titan2.5+_processor/outputs)
        """
        if base_path is None:
            # Set default to titan2.5+_processor/outputs
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'titan2.5+_processor', 'outputs'))
        self.year = year
        self.comp_type = comp_type
        self.base_path = base_path
        self.directory_path = os.path.join(base_path, comp_type, str(year))
        os.makedirs(self.directory_path, exist_ok=True)

    def fetch_and_save_fixtures(self):
        """
        Fetch the NRL.com API for the specified year,
        and save the fixtures as a JSON file.
        """
        url = NRL_API_URL.format(year=self.year)
        print(f"[INFO] Fetching NRL.com API: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"[ERROR] Failed to fetch NRL.com API. Status code: {response.status_code}")
            return
        data = response.json()
        matches = data.get('matches', [])
        print(f"[INFO] Found {len(matches)} matches for {self.year}.")
        if not matches:
            print(f"[WARN] No matches found for {self.year}. Skipping file save to avoid overwriting existing data.")
            return
        output_file = os.path.join(self.directory_path, f"NRL_fixtures_{self.year}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(matches, f, ensure_ascii=False, indent=4)
        print(f"[SUCCESS] Saved fixtures to {output_file}")


if __name__ == "__main__":
    from datetime import datetime

    # Interactive prompts for years and type
    years_input = input("Enter year(s) to download (e.g. 2023 or 2020-2025 or 2021,2022,2023): ").strip()
    if '-' in years_input:
        start, end = map(int, years_input.split('-'))
        years = list(range(start, end + 1))
    elif ',' in years_input:
        years = [int(y.strip()) for y in years_input.split(',') if y.strip().isdigit()]
    else:
        years = [int(years_input)]
    comp_type = input("Enter competition type (NRL, NRLW, HOSTPLUS, KNOCKON): ").strip().upper() or 'NRL'
    print("Which datasets do you want to download/scrape?")
    do_fixtures = input("  Download fixtures? (y/n): ").strip().lower() == 'y'
    do_match = input("  Scrape match data? (y/n): ").strip().lower() == 'y'
    do_detailed = input("  Scrape detailed match data? (y/n): ").strip().lower() == 'y'
    do_player = input("  Scrape player stats? (y/n): ").strip().lower() == 'y'
    do_referee = input("  Download referee stats? (y/n): ").strip().lower() == 'y'
    do_bunker = input("  Download bunker decisions? (y/n): ").strip().lower() == 'y'
    do_penalties = input("  Download penalties? (y/n): ").strip().lower() == 'y'
    do_weather = input("  Download weather impact? (y/n): ").strip().lower() == 'y'

    for year in years:
        print(f"\n=== Processing {comp_type} {year} ===")
        if do_fixtures:
            downloader = NRLDownloader(year, comp_type)
            downloader.fetch_and_save_fixtures()
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if do_match:
            script = os.path.join(base_dir, 'titan2.5+_processor', 'match_data_select.py')
            args = ['--year', str(year), '--rounds', '27', '--type', comp_type]
            print(f"[INFO] Running: {sys.executable} {script} {' '.join(args)}")
            try:
                subprocess.run([sys.executable, script] + args, check=True)
            except Exception as e:
                print(f"[ERROR] Failed to run {script}: {e}")
        if do_detailed:
            script = os.path.join(base_dir, 'titan2.5+_processor', 'match_data_detailed_select.py')
            args = ['--year', str(year), '--rounds', '27', '--type', comp_type]
            print(f"[INFO] Running: {sys.executable} {script} {' '.join(args)}")
            try:
                subprocess.run([sys.executable, script] + args, check=True)
            except Exception as e:
                print(f"[ERROR] Failed to run {script}: {e}")
        if do_player:
            script = os.path.join(base_dir, 'titan2.5+_processor', 'player_data_select.py')
            args = ['--year', str(year), '--round', '27', '--type', comp_type]
            print(f"[INFO] Running: {sys.executable} {script} {' '.join(args)}")
            try:
                subprocess.run([sys.executable, script] + args, check=True)
            except Exception as e:
                print(f"[ERROR] Failed to run {script}: {e}")
        # Referee, bunker, penalties, weather, etc. (CSV fetch or placeholder)
        outputs_dir = os.path.join(base_dir, 'titan2.5+_processor', 'outputs')
        if do_referee:
            ref_csv = os.path.join(outputs_dir, 'referee_stats.csv')
            if not os.path.exists(ref_csv):
                with open(ref_csv, 'w') as f:
                    f.write('referee,year,stat1,stat2\n')
            print(f"[INFO] Referee stats placeholder created: {ref_csv}")
        if do_bunker:
            bunker_csv = os.path.join(outputs_dir, 'bunker_decisions.csv')
            if not os.path.exists(bunker_csv):
                with open(bunker_csv, 'w') as f:
                    f.write('decision_id,match_id,minute,decision_type,referee,bunker,controversy_flag\n')
            print(f"[INFO] Bunker decisions placeholder created: {bunker_csv}")
        if do_penalties:
            penalties_csv = os.path.join(outputs_dir, 'penalties.csv')
            if not os.path.exists(penalties_csv):
                with open(penalties_csv, 'w') as f:
                    f.write('penalty_id,match_id,team,against_team,referee,minute\n')
            print(f"[INFO] Penalties placeholder created: {penalties_csv}")
        if do_weather:
            weather_csv = os.path.join(outputs_dir, 'weather_impact_analysis.csv')
            if not os.path.exists(weather_csv):
                with open(weather_csv, 'w') as f:
                    f.write('Date,Venue,Rain,WindSpeed,WindDirection,Temperature,Humidity,WeatherCondition,Pressure,CloudCover,DewPoint,UVIndex\n')
            print(f"[INFO] Weather impact placeholder created: {weather_csv}")
