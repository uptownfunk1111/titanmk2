import pandas as pd
import time
import os

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    import subprocess
    import sys
    print("[INFO] playwright not found, installing via pip...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'playwright'])
    from playwright.sync_api import sync_playwright
    print("[INFO] Installing Playwright browsers...")
    subprocess.check_call([sys.executable, '-m', 'playwright', 'install'])

# Try to import playwright-stealth, but continue if not available
# type: ignore
try:
    from playwright_stealth import stealth_sync  # type: ignore
except ImportError:
    stealth_sync = None
    print("[WARN] playwright-stealth not found. Running without stealth mode.")

if __name__ == "__main__":
    player_data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Run in visible mode to avoid bot detection
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US"
        )
        page = context.new_page()
        if stealth_sync:
            stealth_sync(page)  # Apply stealth to evade bot detection
        else:
            print("[WARN] playwright-stealth not available, running without stealth.")
        try:
            print("[INFO] Navigating to NRL players page (timeout: 90s)...")
            page.goto("https://www.nrl.com/players/?competition=111", timeout=90000, wait_until="load")
            page.wait_for_timeout(3000)  # Wait 3 seconds for dynamic content
        except Exception as e:
            print(f"[ERROR] Failed to load NRL players page: {e}")
            browser.close()
            exit(1)
        
        # 1. Click the competition dropdown and select 'Telstra Premiership' if not already selected
        print("[PROGRESS] Competition dropdown located. Selecting 'Telstra Premiership'...")
        comp_dropdown = page.locator('.filter-dropdown-button__content').first
        comp_dropdown.wait_for(state='visible', timeout=60000)
        comp_dropdown.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        comp_dropdown.click(force=True)
        page.wait_for_timeout(500)
        try:
            telstra_option = page.get_by_role("button", name="Telstra Premiership")
            if telstra_option.is_visible():
                print("[PROGRESS] Selecting 'Telstra Premiership' competition...")
                telstra_option.click(force=True)
                page.wait_for_timeout(1500)
        except Exception:
            print("[INFO] 'Telstra Premiership' already selected or not found.")
            pass

        # 2. Click the team dropdown (All Teams)
        print("[PROGRESS] Using robust selectors for team dropdown and team options...")
        # Open the team dropdown using the button with aria-controls="team-dropdown"
        team_dropdown_btn = page.locator('button[aria-controls="team-dropdown"]')
        team_dropdown_btn.wait_for(state='visible', timeout=60000)
        team_dropdown_btn.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        team_dropdown_btn.click(force=True)
        page.wait_for_timeout(500)
        # Get all team option buttons inside the dropdown
        team_buttons = page.locator('div#team-dropdown button.filter-dropdown-option')
        team_count = team_buttons.count()
        print(f"[DEBUG] Found {team_count} team buttons in dropdown.")
        for team_idx in range(team_count):
            team_btn = team_buttons.nth(team_idx)
            team_name = team_btn.inner_text().strip()
            if team_name.lower() in ["all teams", "select team", ""]:
                continue
            print(f"[PROGRESS] Selecting team {team_idx+1}/{team_count}: {team_name}")
            # Re-open the dropdown before each click
            team_dropdown_btn.click(force=True)
            page.wait_for_timeout(300)
            team_btn = page.locator('div#team-dropdown button.filter-dropdown-option').nth(team_idx)
            try:
                team_btn.wait_for(state='visible', timeout=5000)
                team_btn.click(force=True)
                print(f"[SUCCESS] Team '{team_name}' selected.")
            except Exception as e:
                print(f"[WARN] Could not click team option '{team_name}': {e}")
                continue
            page.wait_for_timeout(2000)
            # Collect all player card hrefs and names for this team
            player_cards = page.locator('a.card-themed-hero-profile')
            player_count = player_cards.count()
            print(f"[DEBUG] Found {player_count} player cards for team '{team_name}'.")
            player_links = []
            for i in range(player_count):
                card = player_cards.nth(i)
                href = card.get_attribute('href')
                name = card.locator('.card-themed-hero__name').inner_text().replace('\n', ' ').strip()
                player_links.append((href, name))
            for player_idx, (href, player_name) in enumerate(player_links):
                if not href:
                    continue
                print(f"[PROGRESS] [{team_name}] Player {player_idx+1}/{len(player_links)}: {player_name} - Navigating to profile...")
                # Go to the player profile page
                page.goto(f'https://www.nrl.com{href}', timeout=60000)
                page.wait_for_timeout(1500)
                # Scrape all rows in the stats table tbody
                stats = []
                try:
                    rows = page.locator('tbody.table-tbody.u-white-space-no-wrap > tr.table-tbody__tr')
                    row_count = rows.count()
                    print(f"[DEBUG] Scraping {row_count} stat rows for player '{player_name}'.")
                    for j in range(row_count):
                        row = rows.nth(j)
                        cells = row.locator('td')
                        stat_row = [cells.nth(k).inner_text().strip() for k in range(cells.count())]
                        stats.append(stat_row)
                except Exception as e:
                    print(f"[WARN] Could not scrape stats table for {player_name}: {e}")
                try:
                    team = page.locator('.player-profile__team-name, .card-themed-hero__team-name').first.inner_text().strip()
                except Exception:
                    team = ''
                try:
                    position = page.locator('.player-profile__position, .card-themed-hero__position').first.inner_text().strip()
                except Exception:
                    position = ''
                player_data.append({'name': player_name, 'team': team, 'position': position, 'profile_url': f'https://www.nrl.com{href}', 'stats_table': stats})
                print(f"[SUCCESS] Scraped stats for {player_name} ({team}, {position}). Returning to team page...")
                # Go back to the team page
                page.go_back(timeout=60000)
                page.wait_for_timeout(1000)
        print(f"[COMPLETE] Finished scraping all teams and players.")
        browser.close()
    
    # Always save to the outputs directory at the project root
    outputs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)
    out_csv = os.path.join(outputs_dir, 'nrl_player_stats_2025.csv')
    df = pd.DataFrame(player_data)
    df.to_csv(out_csv, index=False)
    print(f"[SUCCESS] Data successfully saved to {out_csv} ({len(df)} players)")
