# titan_fetch.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_nrl_data():
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")  # Uncomment if needed
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver_path = r"C:\Users\slangston1\titan\titan\drivers\chromedriver\chromedriver.exe"

    try:
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        print("🔄 Opening NRL draw page...")
        driver.get("https://www.nrl.com/draw/")

        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "match-team__name"))
        )

        home_teams = driver.find_elements(By.CLASS_NAME, "match-team__name--home")
        away_teams = driver.find_elements(By.CLASS_NAME, "match-team__name--away")

        matches = []
        if len(home_teams) == len(away_teams):
            for i in range(len(home_teams)):
                matches.append({
                    "home_team": home_teams[i].text.strip(),
                    "away_team": away_teams[i].text.strip()
                })
        else:
            print(f"⚠️ Mismatch: {len(home_teams)} home vs {len(away_teams)} away")

        driver.quit()
        print(f"✅ Found {len(matches)} matchups.")
        return matches

    except Exception as e:
        print(f"❌ Error fetching NRL match data: {e}")
        return []
