"""
NRL Team List Scraper (Playwright Version)
- Scrapes the most recent NRL team list article for player names and jersey numbers
- Returns a list of player/team dictionaries
- Can be imported and called by other scripts in the TITAN pipeline
- Not called automatically by titan_main.py, but can be used as a utility
"""
from playwright.sync_api import sync_playwright
import pandas as pd

BASE_URL = "https://www.nrl.com"
TOPIC_URL = "https://www.nrl.com/news/topic/team-lists/"

def fetch_team_lists():
    """
    Scrape the most recent team list article and extract player names and jersey numbers using Playwright
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        print("🔄 Opening NRL team lists topic page...")
        page.goto(TOPIC_URL, timeout=90000, wait_until="load")
        page.wait_for_timeout(2000)
        # Find the first article link containing 'team lists' in the text
        article_links = page.locator('a:has-text("team lists")')
        if article_links.count() == 0:
            print("❌ No team list article found.")
            browser.close()
            return []
        article_url = article_links.first.get_attribute('href')
        if not article_url.startswith('http'):
            article_url = BASE_URL + article_url
        print(f"📰 Found latest team list article: {article_url}")
        page.goto(article_url, timeout=90000, wait_until="load")
        page.wait_for_timeout(2000)
        teams_data = []
        team_blocks = page.locator('li.team-list')
        for i in range(team_blocks.count()):
            block = team_blocks.nth(i)
            try:
                number = block.locator('span.team-list-position__number').inner_text().strip()
                # Home team
                if block.locator('div.team-list-profile--home').count() > 0:
                    home = block.locator('div.team-list-profile--home')
                    fname = home.locator('span').nth(1).evaluate('el => el.previousSibling.textContent').strip()
                    lname = home.locator('span.u-font-weight-700').inner_text().strip()
                    teams_data.append({
                        "Team_Side": "Home",
                        "Full_Name": f"{fname} {lname}",
                        "Jersey_Number": number
                    })
                # Away team
                if block.locator('div.team-list-profile--away').count() > 0:
                    away = block.locator('div.team-list-profile--away')
                    fname = away.locator('span').nth(1).evaluate('el => el.previousSibling.textContent').strip()
                    lname = away.locator('span.u-font-weight-700').inner_text().strip()
                    teams_data.append({
                        "Team_Side": "Away",
                        "Full_Name": f"{fname} {lname}",
                        "Jersey_Number": number
                    })
            except Exception as e:
                print(f"⚠️ Skipping a malformed player block: {e}")
                continue
        print(f"✅ Extracted {len(teams_data)} players from latest team list.")
        browser.close()
        return teams_data

def export_team_lists_to_csv(teams_data, output_path="team_list_latest.csv"):
    if not teams_data:
        print("[WARN] No team data to export.")
        return
    df = pd.DataFrame(teams_data)
    df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Exported team list to {output_path}")

if __name__ == "__main__":
    teams_data = fetch_team_lists()
    if teams_data:
        export_team_lists_to_csv(teams_data)