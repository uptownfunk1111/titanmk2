# titan_model.py

import random
import requests
from bs4 import BeautifulSoup

def get_live_team_strengths():
    """
    Fetch current NRL ladder and assign strength based on ladder points.
    """
    url = "https://www.nrl.com/ladder/?competition=111&round=8&season=2025"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        ladder_rows = soup.find_all('tr', class_='ladder__row')

        strengths = {}

        for row in ladder_rows:
            team_tag = row.find('a', class_='ladder-club')
            points_tag = row.find_all('td', class_='ladder__item u-font-weight-700')

            if team_tag and points_tag:
                team_name = team_tag.text.strip()
                points_text = points_tag[-1].text.strip()  # Last bold <td> is ladder points

                try:
                    points = int(points_text)
                except ValueError:
                    points = 10  # Fallback if parsing fails

                strength = 55 + (points * 2.5)
                strengths[team_name] = strength

        return strengths

    except Exception as e:
        print(f"Error fetching ladder data: {e}")
        return {}

def predict_tips(matches):
    """
    Predict tips using ladder-points-based team strength.
    """
    team_strengths = get_live_team_strengths()

    predictions = []

    for match in matches:
        home = match["home_team"]
        away = match["away_team"]

        home_strength = team_strengths.get(home, 70)
        away_strength = team_strengths.get(away, 70)

        home_strength += 3  # Home ground advantage bonus

        if home_strength > away_strength + 5:
            tip = home
        elif away_strength > home_strength + 5:
            tip = away
        else:
            tip = home if random.random() < 0.55 else away

        predictions.append({
            "Home_Team": home,
            "Away_Team": away,
            "Tip": tip
        })

    return predictions
