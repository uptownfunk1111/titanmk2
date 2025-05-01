from downloader import fetch_player_stats
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd

# Set up the Chrome WebDriver for Selenium
def setup_driver():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path='C:/path_to_chromedriver/chromedriver.exe', options=options)
    return driver

# Fetch match data and player statistics for a selected year
def fetch_match_data(year):
    driver = setup_driver()

    url = f"https://www.nrl.com/draw/{year}"
    driver.get(url)

    # Example of scraping match data (customize based on actual structure)
    match_data = []
    matches = driver.find_elements_by_class_name("match-list")
    for match in matches:
        team_home = match.find_element_by_class_name("team-home").text
        team_away = match.find_element_by_class_name("team-away").text
        round_num = match.find_element_by_class_name("round").text

        match_data.append({
            'round': round_num,
            'home_team': team_home,
            'away_team': team_away
        })

    driver.quit()

    # Convert to DataFrame and save as CSV or JSON
    match_df = pd.DataFrame(match_data)
    match_df.to_csv(f'data/match_data_{year}.csv', index=False)
    # match_df.to_json(f'data/match_data_{year}.json', orient='records', lines=True)

# Main function to execute scraping
if __name__ == "__main__":
    year = 2025  # Update to desired year
    fetch_player_stats(year)  # Fetch player stats first
    fetch_match_data(year)    # Fetch match data second
