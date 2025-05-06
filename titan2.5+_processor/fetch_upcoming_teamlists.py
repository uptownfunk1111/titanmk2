"""
Fetches the official NRL team lists for the upcoming round from the latest post on https://www.nrl.com/news/topic/team-lists/.
Saves the data as a structured JSON file for use in the prediction pipeline.
"""
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def fetch_latest_teamlist_article_url():
    url = "https://www.nrl.com/news/topic/team-lists/"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    # Find the first article link (most recent team list)
    article = soup.find("a", class_="card card--article")
    if not article:
        raise Exception("Could not find latest team list article.")
    article_url = article.get("href")
    if not article_url.startswith("http"):
        article_url = f"https://www.nrl.com{article_url}"
    return article_url

def parse_teamlists_from_article(article_url):
    resp = requests.get(article_url)
    soup = BeautifulSoup(resp.text, "html.parser")
    # Find all match sections (usually h3 or h2 for matchups, followed by team lists)
    matches = []
    for header in soup.find_all(["h2", "h3"]):
        matchup = header.get_text(strip=True)
        # Look for the next ul or table (team list)
        ul = header.find_next("ul")
        if not ul:
            continue
        players = []
        for li in ul.find_all("li"):
            text = li.get_text(" ", strip=True)
            # Try to extract number, name, position
            parts = text.split(" ", 2)
            if len(parts) == 3:
                number, name, position = parts
            elif len(parts) == 2:
                number, name = parts
                position = ""
            else:
                number, name, position = "", text, ""
            players.append({"number": number, "name": name, "position": position})
        if players:
            matches.append({"matchup": matchup, "team_list": players})
    return matches

def save_teamlists_json(matches, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"fetched": datetime.now().isoformat(), "matches": matches}, f, indent=2)
    print(f"[SUCCESS] Saved team lists to {output_path}")

def main():
    print("[INFO] Fetching latest NRL team lists article...")
    article_url = fetch_latest_teamlist_article_url()
    print(f"[INFO] Latest team list article: {article_url}")
    matches = parse_teamlists_from_article(article_url)
    if not matches:
        print("[WARN] No team lists found in the article.")
        return
    output_path = os.path.join(os.path.dirname(__file__), "outputs", f"NRL_teamlists_{datetime.now().date()}.json")
    save_teamlists_json(matches, output_path)

if __name__ == "__main__":
    main()
