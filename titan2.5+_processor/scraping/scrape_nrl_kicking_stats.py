import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# URL for NRL player kicking stats
URL = "https://www.foxsports.com.au/nrl/nrl-premiership/stats/players?wpa=BB44D82C3D7223D393F2AE47579FB5EA6791ABE4&editiondata=none&fromakamai=true&pt=none&device=DESKTOP&category=kicking&sortBy=attackingKicks"

# Output path
output_csv = os.path.join(os.path.dirname(__file__), "..", "outputs", "nrl_kicking_stats_2025.csv")

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Start Selenium WebDriver
driver = webdriver.Chrome(options=chrome_options)
driver.get(URL)

all_data = []
page = 1
max_pages = 20

while page <= max_pages:
    print(f"[INFO] Scraping page {page} of {max_pages}")
    time.sleep(2)  # Wait for page to load
    soup = BeautifulSoup(driver.page_source, "html.parser")
    all_tables = soup.find_all('table')
    main_table = max(all_tables, key=lambda t: len(t.find_all('tr')), default=None)
    if main_table:
        rows = main_table.find_all('tr')
        headers_row = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
        for row in rows[1:]:
            cols = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
            if len(cols) == len(headers_row):
                all_data.append(cols)
    else:
        print(f"[WARN] No main table found on page {page}")
    # Try to click the next page button
    try:
        next_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".fiso-lab-pagination__button--next"))
        )
        driver.execute_script("arguments[0].click();", next_btn)
        page += 1
    except Exception as e:
        print(f"[INFO] No more pages or error navigating: {e}")
        break

driver.quit()

if all_data:
    # Use the last headers_row found
    df = pd.DataFrame(all_data, columns=headers_row)
    df.to_csv(output_csv, index=False)
    print(f"[SUCCESS] Scraped {len(df)} player kicking stats to {output_csv}")
else:
    print("[ERROR] No player stats found across all pages.")
