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
init(autoreset=True)

print(Fore.GREEN + Style.BRIGHT + r'''
╔════════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ████████╗██╗████████╗ █████╗ ███╗   ██╗██╗   ██╗               ║
║   ╚══██╔══╝██║╚══██╔══╝██╔══██╗████╗  ██║╚██╗ ██╔╝               ║
║      ██║   ██║   ██║   ███████║██╔██╗ ██║ ╚████╔╝                ║
║      ██║   ██║   ██║   ██╔══██║██║╚██╗██║  ╚██╔╝                 ║
║      ██║   ██║   ██║   ██║  ██║██║ ╚████║   ██║                  ║
║      ╚═╝   ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝                  ║
║                                                                  ║
║   [TITAN TIPPING PIPELINE - COMMAND INTERFACE ONLINE]             ║
║   Status: ALL SYSTEMS NOMINAL | Awaiting Operator Input...        ║
╚════════════════════════════════════════════════════════════════════╝
''')
print(Fore.CYAN + Style.BRIGHT + ">>> Welcome, Commander. The TITAN AI is ready for mission deployment. <<<\n" + Style.RESET_ALL)

log_path = 'outputs/fetch_fixtures.log'
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

def fetch_fixtures_and_officials_and_teams(year, round_number, output_path):
    print_info(f"[START] Fetching NRL fixtures, officials, and team lists for Year: {year}, Round: {round_number}")
    url = NRL_DRAW_URL.format(year=year, round=round_number)
    print_info(f"[INFO] Fetching main draw page: {url}")
    try:
        response = requests.get(url)
    except Exception as e:
        print_error(f"[ERROR] Exception fetching main draw page: {e}")
        return
    if response.status_code != 200:
        print_error(f"[ERROR] Failed to fetch main draw page. Status code: {response.status_code}")
        return
    soup = BeautifulSoup(response.text, "html.parser")
    fixtures = []
    match_cards = soup.select(".match-card")
    print_info(f"[INFO] Found {len(match_cards)} match cards on the page.")
    if not match_cards:
        print_warn("[WARN] No match cards found. The page structure may have changed or no matches are scheduled.")
    for idx, match in enumerate(match_cards):
        print_info(f"[PROGRESS] Processing match {idx+1} of {len(match_cards)}...")
        home = match.select_one(".home-team .team-name").text.strip() if match.select_one(".home-team .team-name") else ""
        away = match.select_one(".away-team .team-name").text.strip() if match.select_one(".away-team .team-name") else ""
        date = match.select_one(".match-date").text.strip() if match.select_one(".match-date") else ""
        venue = match.select_one(".venue").text.strip() if match.select_one(".venue") else ""
        print_info(f"[DEBUG] Home: {home}, Away: {away}, Date: {date}, Venue: {venue}")
        match_url_elem = match.select_one("a.match-centre-link")
        match_url = match_url_elem['href'] if match_url_elem else None
        referee = bunker = ""
        home_teamlist = []
        away_teamlist = []
        if match_url:
            full_match_url = "https://www.nrl.com" + match_url
            print_info(f"[INFO] Fetching match centre page: {full_match_url}")
            try:
                match_page = requests.get(full_match_url)
            except Exception as e:
                print_error(f"[ERROR] Exception fetching match centre page: {e}")
                continue
            if match_page.status_code != 200:
                print_warn(f"[WARN] Failed to fetch match centre page. Status code: {match_page.status_code}")
            else:
                match_soup = BeautifulSoup(match_page.text, "html.parser")
                officials_section = match_soup.find("section", class_="officials")
                if officials_section:
                    officials = officials_section.get_text("\n", strip=True)
                    for line in officials.split("\n"):
                        if "Referee" in line:
                            referee = line.replace("Referee:", "").strip()
                        if "Bunker" in line:
                            bunker = line.replace("Bunker:", "").strip()
                    print_info(f"[DEBUG] Referee: {referee}, Bunker: {bunker}")
                for team_side, teamlist in [(".team-list--home", home_teamlist), (".team-list--away", away_teamlist)]:
                    team_section = match_soup.select_one(team_side)
                    if team_section:
                        for player in team_section.select(".team-list__player"):
                            player_name = player.select_one(".team-list__player-name")
                            if player_name:
                                teamlist.append(player_name.text.strip())
                if not home_teamlist or not away_teamlist:
                    squads = match_soup.select(".squads__team")
                    if squads and len(squads) == 2:
                        for idx2, squad in enumerate(squads):
                            players = [p.text.strip() for p in squad.select(".squads__player-name")]
                            if idx2 == 0:
                                home_teamlist = players
                            else:
                                away_teamlist = players
                print_info(f"[DEBUG] Home team list: {home_teamlist}")
                print_info(f"[DEBUG] Away team list: {away_teamlist}")
            time.sleep(0.5)  # Be polite to the server
        else:
            print_warn(f"[WARN] No match centre link found for this match.")
        fixtures.append({
            "HomeTeam": home,
            "AwayTeam": away,
            "Date": date,
            "Venue": venue,
            "Referee": referee,
            "Bunker": bunker,
            "HomeTeamList": ", ".join(home_teamlist),
            "AwayTeamList": ", ".join(away_teamlist)
        })
    print_info(f"[INFO] Writing {len(fixtures)} fixtures to CSV: {output_path}")
    try:
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["HomeTeam", "AwayTeam", "Date", "Venue", "Referee", "Bunker", "HomeTeamList", "AwayTeamList"])
            writer.writeheader()
            writer.writerows(fixtures)
        print_success(f"[SUCCESS] Saved fixtures, officials, and team lists to {output_path}")
        if fixtures:
            print_info("[SAMPLE OUTPUT]")
            for row in fixtures[:2]:
                print_info(str(row))
    except Exception as e:
        print_error(f"[ERROR] Failed to write CSV: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch NRL fixtures, officials, and team lists for a round.")
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--round', type=int, required=True)
    parser.add_argument('--output', type=str, default=None)
    args = parser.parse_args()
    output_file = args.output or f"outputs/upcoming_fixtures_and_officials_{args.year}_round{args.round}.csv"
    fetch_fixtures_and_officials_and_teams(args.year, args.round, output_file)
