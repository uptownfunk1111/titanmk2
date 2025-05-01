# titan_teamlist.py

import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_team_lists():
    try:
        # Prompt for article URL
        article_url = input("Paste the full NRL Team List article URL (e.g., https://www.nrl.com/news/2025/...): ").strip()
        if not article_url.startswith("http"):
            print("❌ Invalid URL.")
            return pd.DataFrame()

        # Load and parse the article
        article_html = requests.get(article_url, timeout=15).text
        article_soup = BeautifulSoup(article_html, "html.parser")

        match_blocks = article_soup.find_all("section", class_="match-teams")
        teams_data = []

        for match in match_blocks:
            home_team = match.find("p", class_="match-team__name--home")
            away_team = match.find("p", class_="match-team__name--away")
            home_name = home_team.text.strip() if home_team else "Unknown"
            away_name = away_team.text.strip() if away_team else "Unknown"

            player_rows = match.find_all("li", class_="team-list")

            for row in player_rows:
                number = row.find("span", class_="team-list-position__number")
                number = number.text.strip() if number else ""

                home_block = row.find("div", class_="team-list-profile--home")
                if home_block:
                    try:
                        name_block = home_block.find("div", class_="team-list-profile__name")
                        spans = name_block.find_all("span")
                        first_name = spans[1].previous_sibling.strip()
                        last_name = spans[1].text.strip()
                        teams_data.append({
                            "Team": home_name,
                            "Side": "Home",
                            "First_Name": first_name,
                            "Last_Name": last_name,
                            "Jersey_Number": number
                        })
                    except Exception:
                        continue

                away_block = row.find("div", class_="team-list-profile--away")
                if away_block:
                    try:
                        name_block = away_block.find("div", class_="team-list-profile__name")
                        spans = name_block.find_all("span")
                        first_name = spans[1].previous_sibling.strip()
                        last_name = spans[1].text.strip()
                        teams_data.append({
                            "Team": away_name,
                            "Side": "Away",
                            "First_Name": first_name,
                            "Last_Name": last_name,
                            "Jersey_Number": number
                        })
                    except Exception:
                        continue

        df = pd.DataFrame(teams_data)
        print(f"✅ Extracted {len(df)} players from provided article.")
        return df

    except Exception as e:
        print(f"❌ Error fetching team lists: {e}")
        return pd.DataFrame()
