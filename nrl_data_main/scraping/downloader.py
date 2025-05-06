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
    import argparse
    from datetime import datetime
    parser = argparse.ArgumentParser(description="Download NRL.com fixtures for a range of years.")
    current_year = datetime.now().year
    parser.add_argument('--years', type=str, required=False, default='2019-2025', help='Year(s) of the fixtures, e.g. 2025 or 2019-2025')
    parser.add_argument('--type', type=str, default='NRL')
    args = parser.parse_args()

    # Parse years argument
    if '-' in args.years:
        start, end = map(int, args.years.split('-'))
        years = list(range(start, end + 1))
    else:
        years = [int(args.years)]

    for year in years:
        print(f"\n=== Downloading fixtures for {args.type} {year} ===")
        downloader = NRLDownloader(year, args.type)
        downloader.fetch_and_save_fixtures()
