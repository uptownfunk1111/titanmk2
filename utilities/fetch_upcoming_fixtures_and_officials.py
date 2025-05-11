from colorama import init, Fore, Style
init(autoreset=True)

print(Fore.CYAN + Style.BRIGHT + ">>> Welcome, Commander. The TITAN AI is ready for mission deployment. <<<\n" + Style.RESET_ALL)

import requests
from bs4 import BeautifulSoup
import csv
import sys
from datetime import datetime
import time

NRL_DRAW_URL = "https://www.nrl.com/draw/?season={year}&round={round}"


def fetch_fixtures_and_officials_and_teams(year, round_number, output_path):
    url = NRL_DRAW_URL.format(year=year, round=round_number)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    fixtures = []
    for match in soup.select(".match-card"):
        home = match.select_one(".home-team .team-name").text.strip() if match.select_one(".home-team .team-name") else ""
        away = match.select_one(".away-team .team-name").text.strip() if match.select_one(".away-team .team-name") else ""
        date = match.select_one(".match-date").text.strip() if match.select_one(".match-date") else ""
        venue = match.select_one(".venue").text.strip() if match.select_one(".venue") else ""
        # Officials (may need to follow match link for full details)
        match_url_elem = match.select_one("a.match-centre-link")
        match_url = match_url_elem['href'] if match_url_elem else None
        referee = bunker = ""
        home_teamlist = []
        away_teamlist = []
        if match_url:
            match_page = requests.get("https://www.nrl.com" + match_url)
            match_soup = BeautifulSoup(match_page.text, "html.parser")
            # Try to find officials (selectors may need updating)
            officials_section = match_soup.find("section", class_="officials")
            if officials_section:
                officials = officials_section.get_text("\n", strip=True)
                for line in officials.split("\n"):
                    if "Referee" in line:
                        referee = line.replace("Referee:", "").strip()
                    if "Bunker" in line:
                        bunker = line.replace("Bunker:", "").strip()
            # Try to find team lists (selectors may need updating)
            for team_side, teamlist in [(".team-list--home", home_teamlist), (".team-list--away", away_teamlist)]:
                team_section = match_soup.select_one(team_side)
                if team_section:
                    for player in team_section.select(".team-list__player"):
                        player_name = player.select_one(".team-list__player-name")
                        if player_name:
                            teamlist.append(player_name.text.strip())
            # If above selectors don't work, try fallback (NRL may change layout)
            if not home_teamlist or not away_teamlist:
                squads = match_soup.select(".squads__team")
                if squads and len(squads) == 2:
                    for idx, squad in enumerate(squads):
                        players = [p.text.strip() for p in squad.select(".squads__player-name")]
                        if idx == 0:
                            home_teamlist = players
                        else:
                            away_teamlist = players
            time.sleep(0.5)  # Be polite to the server
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
    # Save to CSV
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["HomeTeam", "AwayTeam", "Date", "Venue", "Referee", "Bunker", "HomeTeamList", "AwayTeamList"])
        writer.writeheader()
        writer.writerows(fixtures)
    print(f"Saved fixtures, officials, and team lists to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch NRL fixtures, officials, and team lists for a round.")
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--round', type=int, required=True)
    parser.add_argument('--output', type=str, default=None)
    args = parser.parse_args()
    output_file = args.output or f"outputs/upcoming_fixtures_and_officials_{args.year}_round{args.round}.csv"
    fetch_fixtures_and_officials_and_teams(args.year, args.round, output_file)
