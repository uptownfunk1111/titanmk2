# titan_model.py

def predict_tips(matches, team_lists):
    """
    Predict winners based on matchups and optionally team list data
    """
    tips = []

    for match in matches:
        home = match.get("home_team", "")
        away = match.get("away_team", "")

        # Very basic logic: home advantage
        tip = home if len(home) <= len(away) else away

        tips.append({
            "Home_Team": home,
            "Away_Team": away,
            "Tip": tip
        })

    return tips
