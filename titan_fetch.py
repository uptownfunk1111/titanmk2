# titan_fetch.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_nrl_data():
    """
    Selenium-based scraper with updated selectors to fetch NRL fixtures from NRL.com
    """

    # Set Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # <-- keep Chrome visible
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Full path to your ChromeDriver
    driver_path = r"C:\Users\slangston1\TITAN\drivers\chromedriver\chromedriver.exe"

    try:
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Open NRL draw page
        driver.get("https://www.nrl.com/draw/")

        # Smart wait until any home team appears (max 15 seconds)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "match-team__name--home"))
        )

        matches = []

        # Find all home teams
        home_teams = driver.find_elements(By.CLASS_NAME, "match-team__name--home")
        # Find all away teams
        away_teams = driver.find_elements(By.CLASS_NAME, "match-team__name--away")

        # Make sure lengths match
        if len(home_teams) == len(away_teams):
            for i in range(len(home_teams)):
                home_team = home_teams[i].text.strip()
                away_team = away_teams[i].text.strip()
                matches.append({
                    "home_team": home_team,
                    "away_team": away_team
                })
        else:
            print(f"Warning: Different number of home and away teams ({len(home_teams)} vs {len(away_teams)})")

        driver.quit()

        if not matches:
            print("Warning: No matches found. Website structure may have changed.")

        return matches

    except Exception as e:
        print(f"Error fetching NRL match data: {e}")
        return []
