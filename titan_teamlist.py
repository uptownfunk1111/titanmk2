# titan_teamlist.py

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def fetch_team_lists():
    """
    Uses Selenium to scrape team lists from the NRL.com Magic Round 2025 page (or later pages).
    """

    url = input("Paste the full NRL Team List article URL (e.g., https://www.nrl.com/news/2025/...):\n").strip()
    if not url:
        print("No URL provided. Cannot fetch team lists.")
        return {}

    # Setup Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Optional: uncomment to make browser invisible
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver_path = "drivers/chromedriver/chromedriver.exe"

    try:
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Error launching Chrome WebDriver: {e}")
        return {}

    try:
        driver.get(url)

        # Step 1: Wait for full page load
        try:
            WebDriverWait(driver, 45).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("Document loaded fully.")
        except Exception:
            print("Warning: Page did not fully finish loading within timeout.")
            driver.quit()
            return {}

        # Step 2: Pull HTML source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        team_lists = {}

        # Step 3: Find all team blocks
        team_blocks = soup.find_all("div", class_="team-list__team")
        print(f"Found {len(team_blocks)} team blocks.")

        for team_block in team_blocks:
            try:
                # Find team name
                team_name_tag = team_block.find("h2", class_="team-list__team-name")
                if not team_name_tag:
                    continue
                team_name = team_name_tag.get_text(strip=True)

                # Initialize list
                team_lists[team_name] = []

                # Find players under this team
                players = team_block.find_all("li", class_="team-list__player")
                for player in players:
                    try:
                        jersey_span = player.find("span", class_="team-list__player-jumper-number")
                        name_span = player.find("span", class_="team-list__player-name")

                        if jersey_span and name_span:
                            jersey_number = int(jersey_span.get_text(strip=True))
                            player_name = name_span.get_text(strip=True)

                            team_lists[team_name].append({
                                "number": jersey_number,
                                "name": player_name
                            })
                    except Exception:
                        continue

            except Exception:
                continue

        driver.quit()

        if not team_lists:
            print("No team data could be extracted.")
        return team_lists

    except Exception as e:
        print(f"Error fetching team lists: {e}")
        driver.quit()
        return {}
