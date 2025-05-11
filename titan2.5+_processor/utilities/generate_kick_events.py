"""
Generate a scaffolded kick_events.csv for NRL matches
- Uses available match and player data to create a base for kick event annotation
- Output: outputs/kick_events.csv
"""
import pandas as pd
import os
from datetime import datetime
import subprocess
import sys

# Paths
outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs'))
os.makedirs(outputs_dir, exist_ok=True)
match_file = os.path.join(outputs_dir, 'all_matches_2019_2025.csv')
player_file = os.path.join(outputs_dir, 'all_players_2019_2025.csv')
kick_events_file = os.path.join(outputs_dir, 'kick_events.csv')

# Run the web scraper to get the latest NRL kicking stats
scraper_path = os.path.join(os.path.dirname(__file__), "scraping", "scrape_nrl_kicking_stats.py")
subprocess.run([sys.executable, scraper_path], check=True)

# Read the scraped kicking stats if the file exists
kicking_stats_path = os.path.join(outputs_dir, "nrl_kicking_stats_2025.csv")
if not os.path.exists(kicking_stats_path):
    print(f"[ERROR] Kicking stats file not found: {kicking_stats_path}\nScraper may have failed or the page structure may have changed.")
    exit(1)

kicking_stats = pd.read_csv(kicking_stats_path)

# Save the kicking stats as the new kick_events.csv (overwrite scaffold)
kicking_stats.to_csv(kick_events_file, index=False)
print(f"[SUCCESS] Kick events file generated from web-scraped stats: {kick_events_file}")
