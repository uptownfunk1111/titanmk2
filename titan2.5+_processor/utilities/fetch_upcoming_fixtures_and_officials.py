"""
Fetches upcoming NRL fixtures, referees, bunker officials, and full team lists for a given round and year.
Saves results to outputs/upcoming_fixtures_and_officials_{year}_round{round}.csv
"""
import requests
from bs4 import BeautifulSoup
import csv
import sys
from datetime import datetime
import time
import logging
from colorama import init, Fore, Style
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import shutil
import subprocess
import importlib.util
import platform

init(autoreset=True)

log_path = 'outputs/fetch_fixtures.log'
# Ensure outputs directory exists before logging
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def print_info(msg):
    print(Fore.CYAN + msg)
    logging.info(msg)

def print_success(msg):
    print(Fore.GREEN + msg)
    logging.info(msg)

def print_warn(msg):
    print(Fore.YELLOW + msg)
    logging.warning(msg)

def print_error(msg):
    print(Fore.RED + msg)
    logging.error(msg)

NRL_DRAW_URL = "https://www.nrl.com/draw/?season={year}&round={round}"

def ensure_selenium():
    if importlib.util.find_spec('selenium') is None:
        print_info('[INFO] selenium not found, installing...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'selenium'])
        print_info('[INFO] selenium installed.')

def fetch_fixtures_and_officials_and_teams(year, round_number, output_path):
    print_info(f"[START] Fetching NRL fixtures, officials, and team lists for Year: {year}, Round: {round_number}")
    url = NRL_DRAW_URL.format(year=year, round=round_number)
    print_info(f"[INFO] Fetching main draw page with Selenium: {url}")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.match--highlighted, a.match-upcoming"))
        )
    except Exception as e:
        print_error(f"[ERROR] Timeout waiting for match cards: {e}")
        driver.quit()
        return
    soup = BeautifulSoup(driver.page_source, "html.parser")
    match_cards = soup.select("a.match--highlighted, a.match-upcoming")
    print_info(f"[INFO] Found {len(match_cards)} match cards on the page.")
    if not match_cards:
        print_warn("[WARN] No match cards found. The page structure may have changed or no matches are scheduled.")
    fixtures = []
    # Reuse the same driver for all match centre pages
    for idx, match in enumerate(match_cards):
        print_info(f"[PROGRESS] Processing match {idx+1} of {len(match_cards)}...")
        home = match.select_one(".match-team__name--home")
        home = home.text.strip() if home else ""
        away = match.select_one(".match-team__name--away")
        away = away.text.strip() if away else ""
        date_elem = match.select_one(".match-header__title")
        date = date_elem.text.strip() if date_elem else ""
        time_elem = match.select_one("time")
        time_str = time_elem.text.strip() if time_elem else ""
        date_time = f"{date} {time_str}".strip()
        venue = ""
        print_info(f"[DEBUG] Home: {home}, Away: {away}, DateTime: {date_time}, Venue: {venue}")
        match_url = match.get('href')
        referee = bunker = ""
        home_teamlist = []
        away_teamlist = []
        officials_str = ""
        if match_url:
            full_match_url = "https://www.nrl.com" + match_url
            print_info(f"[INFO] Fetching match centre page with Selenium: {full_match_url}")
            driver.get(full_match_url)
            try:
                # Try to find the Team Lists tab by ID first
                team_lists_tab = None
                try:
                    team_lists_tab = driver.find_element(By.CSS_SELECTOR, "#tab-team-lists")
                    debug_msg = "Found Team Lists tab by ID."
                except Exception:
                    # Fallback: find by visible text
                    tabs = driver.find_elements(By.CSS_SELECTOR, '[role="tab"], .tabs__tab, .tab, button')
                    for tab in tabs:
                        if 'team lists' in tab.text.lower():
                            team_lists_tab = tab
                            break
                    if team_lists_tab:
                        debug_msg = "Found Team Lists tab by text."
                    else:
                        debug_msg = "Could not find Team Lists tab by ID or text."
                print_info(debug_msg)
                # Only click if tab is found and not already selected
                if team_lists_tab:
                    is_selected = team_lists_tab.get_attribute('aria-selected') == 'true' or 'active' in team_lists_tab.get_attribute('class').lower()
                    if not is_selected:
                        driver.execute_script("arguments[0].click();", team_lists_tab)
                        print_info("[DEBUG] Clicked Team Lists tab.")
                    else:
                        print_info("[DEBUG] Team Lists tab already active.")
                    # Wait for team list player names to appear
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".team-list-profile__name, .team-list__player-name, .squads__player-name"))
                    )
                else:
                    print_warn("[WARN] Team Lists tab not found for this match.")
            except Exception as e:
                print_warn(f"[WARN] Timeout or error waiting for/clicking team lists tab or content: {e}")
            time.sleep(1)  # Allow for JS rendering
            match_soup = BeautifulSoup(driver.page_source, "html.parser")
            venue_elem = match_soup.select_one('p.match-venue.o-text')
            if venue_elem:
                venue = venue_elem.get_text(strip=True).replace('Venue:', '').strip()
            # Officials extraction
            officials = []
            officials_grid = match_soup.select('.l-news-grid .card-team-mate')
            for official in officials_grid:
                name_elem = official.select_one('.card-team-mate__name')
                pos_elem = official.select_one('.card-team-mate__position')
                if name_elem and pos_elem:
                    officials.append(f"{name_elem.text.strip()} ({pos_elem.text.strip()})")
            officials_str = '; '.join(officials)
            # Assign to fields
            referee = ''
            bunker = ''
            for official in officials:
                if 'Referee' in official and not referee:
                    referee = official
                if 'Senior Review Official' in official or 'Bunker' in official:
                    bunker = official
            # Team lists (home/away) - improved for new HTML structure, now with position and jersey number
            home_teamlist = []
            away_teamlist = []
            team_rows = match_soup.select('.team-list.team-list--match-centre')
            for row in team_rows:
                profiles = row.select('.team-list-profile')
                positions = row.select('.team-list-position')
                if len(profiles) == 2 and len(positions) == 2:
                    # Home player
                    home_name_elem = profiles[0].select_one('.team-list-profile-content .team-list-profile__name')
                    home_number_elem = positions[0].select_one('.team-list-position__number')
                    home_pos_elem = positions[0].select_one('.team-list-position__text')
                    if home_name_elem:
                        home_name = ' '.join([t.strip() for t in home_name_elem.stripped_strings])
                        home_number = home_number_elem.text.strip() if home_number_elem else ''
                        home_position = home_pos_elem.text.strip() if home_pos_elem else ''
                        home_teamlist.append(f"{home_number} - {home_name} ({home_position})")
                    # Away player
                    away_name_elem = profiles[1].select_one('.team-list-profile-content .team-list-profile__name')
                    away_number_elem = positions[1].select_one('.team-list-position__number')
                    away_pos_elem = positions[1].select_one('.team-list-position__text')
                    if away_name_elem:
                        away_name = ' '.join([t.strip() for t in away_name_elem.stripped_strings])
                        away_number = away_number_elem.text.strip() if away_number_elem else ''
                        away_position = away_pos_elem.text.strip() if away_pos_elem else ''
                        away_teamlist.append(f"{away_number} - {away_name} ({away_position})")
            # Fallback to old logic if lists are empty
            if not home_teamlist or not away_teamlist:
                squads = match_soup.select('.squads__team')
                if squads and len(squads) == 2:
                    for idx2, squad in enumerate(squads):
                        players = [p.text.strip() for p in squad.select('.squads__player-name')]
                        if idx2 == 0:
                            home_teamlist = players
                        else:
                            away_teamlist = players
            print_info(f"[DEBUG] Venue: {venue}")
            print_info(f"[DEBUG] Officials: {officials_str}")
            print_info(f"[DEBUG] Referee: {referee}, Bunker: {bunker}")
            print_info(f"[DEBUG] Home team list: {home_teamlist}")
            print_info(f"[DEBUG] Away team list: {away_teamlist}")
        else:
            print_warn(f"[WARN] No match centre link found for this match.")
        fixtures.append({
            "HomeTeam": home,
            "AwayTeam": away,
            "Date": date_time,
            "Venue": venue,
            "Referee": referee,
            "Bunker": bunker,
            "Officials": officials_str,
            "HomeTeamList": ", ".join(home_teamlist),
            "AwayTeamList": ", ".join(away_teamlist)
        })
    driver.quit()
    # Ensure output is always in C:/Users/slangston1/TITAN/titan2.5+_processor/outputs
    output_dir = r"C:/Users/slangston1/TITAN/titan2.5+_processor/outputs"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, os.path.basename(output_path))
    print_info(f"[INFO] Writing {len(fixtures)} fixtures to CSV: {output_path}")
    try:
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["HomeTeam", "AwayTeam", "Date", "Venue", "Referee", "Bunker", "Officials", "HomeTeamList", "AwayTeamList"])
            writer.writeheader()
            writer.writerows(fixtures)
        print_success(f"[SUCCESS] Saved fixtures, officials, and team lists to {output_path}")
        if fixtures:
            print_info("[SAMPLE OUTPUT]")
            for row in fixtures[:2]:
                print_info(str(row))
        abs_path = os.path.abspath(output_path)
        print_success(f"[OPEN FILE] file:///{abs_path.replace('\\', '/')}")
    except Exception as e:
        print_error(f"[ERROR] Failed to write CSV: {e}")

if __name__ == "__main__":
    import argparse
    ensure_selenium()
    try:
        import webdriver_manager
    except ImportError:
        print_info('[INFO] webdriver-manager not found, installing...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'webdriver-manager'])
        print_info('[INFO] webdriver-manager installed.')
    parser = argparse.ArgumentParser(description="Fetch NRL fixtures, officials, and team lists for a round.")
    parser.add_argument('--year', type=int, required=False)
    parser.add_argument('--round', type=int, required=False)
    parser.add_argument('--output', type=str, default=None)
    args = parser.parse_args()

    # Prompt for missing arguments
    if args.year is None:
        try:
            args.year = int(input("Enter the NRL season year (e.g., 2025): "))
        except Exception:
            print_error("[ERROR] Invalid year input. Exiting.")
            sys.exit(1)
    if args.round is None:
        try:
            args.round = int(input("Enter the NRL round number (e.g., 10): "))
        except Exception:
            print_error("[ERROR] Invalid round input. Exiting.")
            sys.exit(1)

    output_file = args.output or f"outputs/upcoming_fixtures_and_officials_{args.year}_round{args.round}.csv"
    fetch_fixtures_and_officials_and_teams(args.year, args.round, output_file)
