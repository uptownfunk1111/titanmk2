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

NRL_DRAW_URL = "https://www.nrl.com/draw/?season={year}&round={round}"


def fetch_fixtures_and_officials_and_teams(year, round_number, output_path):
    print(f"[START] Fetching NRL fixtures, officials, and team lists for Year: {year}, Round: {round_number}")
    url = NRL_DRAW_URL.format(year=year, round=round_number)
    print(f"[INFO] Fetching main draw page: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch main draw page. Status code: {response.status_code}")
        return
    soup = BeautifulSoup(response.text, "html.parser")
    fixtures = []
    match_cards = soup.select(".match-card")
    print(f"[INFO] Found {len(match_cards)} match cards on the page.")
    for idx, match in enumerate(match_cards):
        print(f"[PROGRESS] Processing match {idx+1} of {len(match_cards)}...")
        home = match.select_one(".home-team .team-name").text.strip() if match.select_one(".home-team .team-name") else ""
        away = match.select_one(".away-team .team-name").text.strip() if match.select_one(".away-team .team-name") else ""
        date = match.select_one(".match-date").text.strip() if match.select_one(".match-date") else ""
        venue = match.select_one(".venue").text.strip() if match.select_one(".venue") else ""
        print(f"[DEBUG] Home: {home}, Away: {away}, Date: {date}, Venue: {venue}")
        match_url_elem = match.select_one("a.match-centre-link")
        match_url = match_url_elem['href'] if match_url_elem else None
        referee = bunker = ""
        home_teamlist = []
        away_teamlist = []
        if match_url:
            full_match_url = "https://www.nrl.com" + match_url
            print(f"[INFO] Fetching match centre page: {full_match_url}")
            match_page = requests.get(full_match_url)
            if match_page.status_code != 200:
                print(f"[WARN] Failed to fetch match centre page. Status code: {match_page.status_code}")
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
                    print(f"[DEBUG] Referee: {referee}, Bunker: {bunker}")
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
                print(f"[DEBUG] Home team list: {home_teamlist}")
                print(f"[DEBUG] Away team list: {away_teamlist}")
            time.sleep(0.5)  # Be polite to the server
        else:
            print(f"[WARN] No match centre link found for this match.")
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
    print(f"[INFO] Writing {len(fixtures)} fixtures to CSV: {output_path}")
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["HomeTeam", "AwayTeam", "Date", "Venue", "Referee", "Bunker", "HomeTeamList", "AwayTeamList"])
        writer.writeheader()
        writer.writerows(fixtures)
    print(f"[SUCCESS] Saved fixtures, officials, and team lists to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch NRL fixtures, officials, and team lists for a round.")
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--round', type=int, required=True)
    parser.add_argument('--output', type=str, default=None)
    args = parser.parse_args()
    output_file = args.output or f"outputs/upcoming_fixtures_and_officials_{args.year}_round{args.round}.csv"
    fetch_fixtures_and_officials_and_teams(args.year, args.round, output_file)
