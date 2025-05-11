"""
NRL Match Data Fetcher (Playwright Version)
- Scrapes NRL matchups (home/away teams) from the NRL draw page
- Returns a list of matchups as dictionaries
- Can be imported and called by other scripts in the TITAN pipeline for up-to-date fixture data
- Not called automatically by titan_main.py, but can be used as a utility
"""
from playwright.sync_api import sync_playwright

def fetch_nrl_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        print("🔄 Opening NRL draw page...")
        page.goto("https://www.nrl.com/draw/", timeout=90000, wait_until="load")
        page.wait_for_timeout(3000)  # Wait for dynamic content
        # Find all match containers (update selector as needed)
        matches = []
        home_teams = page.locator('.match-team__name--home')
        away_teams = page.locator('.match-team__name--away')
        home_count = home_teams.count()
        away_count = away_teams.count()
        if home_count == away_count:
            for i in range(home_count):
                matches.append({
                    "home_team": home_teams.nth(i).inner_text().strip(),
                    "away_team": away_teams.nth(i).inner_text().strip()
                })
        else:
            print(f"⚠️ Mismatch: {home_count} home vs {away_count} away")
        browser.close()
        print(f"✅ Found {len(matches)} matchups.")
        return matches
