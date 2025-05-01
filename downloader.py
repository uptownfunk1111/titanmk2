from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run in headless mode (no UI)
chrome_options.add_argument('--disable-gpu')

# Set up the WebDriver using Service class
service = Service(ChromeDriverManager().install())

# Initialize the WebDriver with the correct Service configuration
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the NRL players page
url = "https://www.nrl.com/players/?competition=111"
driver.get(url)

# Wait for the page to load and the dropdown to be accessible
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'team-select')))  # Ensure dropdown is loaded
time.sleep(3)

# Get the dropdown element for team selection
dropdown = driver.find_element(By.ID, 'team-select')
dropdown.click()

# Get all the options (teams) in the dropdown
team_options = driver.find_elements(By.CSS_SELECTOR, 'option')

# Prepare list for storing player data
player_data = []

# Loop through each team in the dropdown
for option in team_options:
    team_name = option.text.strip()
    
    # Skip the placeholder "Select Team" option
    if team_name == "Select Team":
        continue
    
    # Select the team from the dropdown
    option.click()
    time.sleep(2)  # Wait for the page to load after selecting the team

    # Wait for the player list to load
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.player-name')))  # Adjust selector as needed

    # Extract player data for the selected team
    players = driver.find_elements(By.CSS_SELECTOR, '.player-name')  # Adjust selector as needed
    
    for player in players:
        player_name = player.text.strip()
        player_team = team_name
        player_data.append({'name': player_name, 'team': player_team})

# Close the driver after scraping is complete
driver.quit()

# Convert the player data into a pandas DataFrame
df = pd.DataFrame(player_data)

# Save the data into a CSV file
output_file = 'nrl_player_stats_2025.csv'
df.to_csv(output_file, index=False)

print(f"Data successfully saved to {output_file}")
