# titan_teamlist.py

import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://www.nrl.com"
TOPIC_URL = "https://www.nrl.com/news/topic/team-lists/"

def fetch_team_lists():
    """
    Scrape the most recent team list article and extract player names and jersey numbers
    """

    try:
        # Step 1: Find the latest article
        topic_html = requests.get(TOPIC_URL).text
        soup = BeautifulSoup(topic_html, "html.parser")

        article_link = soup.find("a", href=True, text=lambda t: t and "team lists" in t.lower())
        if not article_link:
            print("❌ No team list article found.")
            return []

        article_url = BASE_URL + article_link['href']
        print(f"📰 Found latest team list article: {article_url}")

        # Step 2: Fetch and parse the article
        article_html = requests.get(article_url).text
        soup = BeautifulSoup(article_html, "html.parser")

        teams_data = []
        team_blocks = soup.find_all("li", class_="team-list")

        for block in team_blocks:
            try:
                number = block.find("span", class_="team-list-position__number").text.strip()

                home = block.find("div", class_="team-list-profile--home")
                if home:
                    fname = home.find_all("span")[1].previous_sibling.strip()
                    lname = home.find("span", class_="u-font-weight-700").text.strip()
                    teams_data.append({
                        "Team_Side": "Home",
                        "Full_Name": f"{fname} {lname}",
                        "Jersey_Number": number
                    })

                away = block.find("div", class_="team-list-profile--away")
                if away:
                    fname = away.find_all("span")[1].previous_sibling.strip()
                    lname = away.find("span", class_="u-font-weight-700").text.strip()
                    teams_data.append({
                        "Team_Side": "Away",
                        "Full_Name": f"{fname} {lname}",
                        "Jersey_Number": number
                    })

            except Exception as e:
                print(f"⚠️ Skipping a malformed player block: {e}")
                continue

        print(f"✅ Extracted {len(teams_data)} players from latest team list.")
        return teams_data

    except Exception as e:
        print(f"❌ Error fetching team lists: {e}")
        return []
