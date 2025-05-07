"""
Coach Impact Analysis for NRL Matches
- Assigns doctrine/style to each coach
- Compares coaching styles for a given match
- Returns a summary and tactical edge
- Updated with 2025 NRL coaches, styles, and notes
"""
import pandas as pd

# Comprehensive coach database for 2025 NRL
COACH_DB = {
    "Brisbane Broncos": {
        "coach": "Michael Maguire",
        "style": "Discipline & Grind",
        "icon": "🔨",
        "desc": "Structured defence-first coach; prefers field position and resilience. Appointed in late 2024, experience from Souths and Tigers."
    },
    "Canberra Raiders": {
        "coach": "Ricky Stuart",
        "style": "Chaos & Passion",
        "icon": "🎯",
        "desc": "Momentum-driven, emotional footy; inconsistent structure. 12th season, deep club connection."
    },
    "Canterbury Bulldogs": {
        "coach": "Cameron Ciraldo",
        "style": "Developmental Systems",
        "icon": "🧬",
        "desc": "Heavy on structure, youth integration, Penrith-style backline shapes. 3rd season."
    },
    "Cronulla Sharks": {
        "coach": "Craig Fitzgibbon",
        "style": "Defensive Rigidity",
        "icon": "🪖",
        "desc": "Defence wins games; wrestle + line-speed with edge variation. 4th season."
    },
    "Dolphins": {
        "coach": "Kristian Woolf",
        "style": "Simple Power & Control",
        "icon": "⚔️",
        "desc": "Tonga-style forward dominance, conservative backline. 1st season after Bennett."
    },
    "Gold Coast Titans": {
        "coach": "Des Hasler",
        "style": "Unpredictable Structures",
        "icon": "🧠",
        "desc": "Inventive tactics, compressed defence, wide shifts. 2nd season, veteran coach."
    },
    "Manly Sea Eagles": {
        "coach": "Anthony Seibold",
        "style": "Statistical Structuring",
        "icon": "🧮",
        "desc": "Over-structured attack; analytics-first, low flexibility. 3rd season."
    },
    "Melbourne Storm": {
        "coach": "Craig Bellamy",
        "style": "Discipline + Flex Agility",
        "icon": "🧱",
        "desc": "Gold standard: wrestle → structure → unleash. 22nd season, legendary coach."
    },
    "Newcastle Knights": {
        "coach": "Adam O'Brien",
        "style": "Developmental Systems",
        "icon": "🧬",
        "desc": "Focus on competitive edge, 6th season."
    },
    "New Zealand Warriors": {
        "coach": "Andrew Webster",
        "style": "Fresh Systems",
        "icon": "🧬",
        "desc": "Penrith-influenced, fresh strategies. 3rd season."
    },
    "North Queensland Cowboys": {
        "coach": "Todd Payten",
        "style": "Rebuilding & Integration",
        "icon": "🔄",
        "desc": "Rebuilding, integrating new talent. 5th season."
    },
    "Parramatta Eels": {
        "coach": "Jason Ryles",
        "style": "Revitalisation",
        "icon": "⚡",
        "desc": "New appointment, revitalising team. 1st season."
    },
    "Penrith Panthers": {
        "coach": "Ivan Cleary",
        "style": "Strategic Acumen",
        "icon": "♟️",
        "desc": "Multiple premierships, strategic master. 7th season (current stint)."
    },
    "South Sydney Rabbitohs": {
        "coach": "Wayne Bennett",
        "style": "Grinding",
        "icon": "🪨",
        "desc": "Returned in 2025, extensive experience, simple resilient style."
    },
    "St. George Illawarra Dragons": {
        "coach": "Shane Flanagan",
        "style": "Consistency Focus",
        "icon": "🔁",
        "desc": "Former Cronulla coach, team consistency. 2nd season."
    },
    "Sydney Roosters": {
        "coach": "Trent Robinson",
        "style": "Expansive Attack",
        "icon": "🚀",
        "desc": "Creative, offloads, attacking focus. 13th season, history of success."
    },
    "Wests Tigers": {
        "coach": "Benji Marshall",
        "style": "Culture & Instinct",
        "icon": "🔥",
        "desc": "Club legend, winning culture, instinctive play. 2nd season."
    },
}

def get_coach_info(team):
    return COACH_DB.get(team, None)

def compare_coach_matchup(home_team, away_team):
    home = get_coach_info(home_team)
    away = get_coach_info(away_team)
    if not home or not away:
        return {
            "summary": f"Coach data missing for {home_team if not home else away_team}",
            "tactical_edge": "Unknown"
        }
    summary = f"{home['coach']} ({home['icon']} {home['style']}) vs {away['coach']} ({away['icon']} {away['style']})"
    # Example tactical edge logic
    if home['style'] == away['style']:
        edge = f"Even matchup: Both teams coached with a {home['style']} doctrine."
    elif 'Defense' in home['style'] and 'Attack' in away['style']:
        edge = f"{home['coach']}'s defense may blunt {away['coach']}'s attack."
    elif 'Attack' in home['style'] and 'Defense' in away['style']:
        edge = f"{away['coach']}'s defense could contain {home['coach']}'s attack."
    elif 'Grind' in home['style'] and 'Chaos' in away['style']:
        edge = f"{home['coach']}'s grind may control {away['coach']}'s chaos, but volatility risk."
    elif 'Unpredictable' in home['style'] or 'Unpredictable' in away['style']:
        edge = "Unpredictable tactics could swing the match either way."
    else:
        edge = "Tactical edge unclear; styles may neutralise."
    return {
        "summary": summary,
        "home_desc": home['desc'],
        "away_desc": away['desc'],
        "tactical_edge": edge
    }

# Example usage:
if __name__ == "__main__":
    home_team = "Melbourne Storm"
    away_team = "Sydney Roosters"
    result = compare_coach_matchup(home_team, away_team)
    print(result["summary"])
    print("Home coach:", result["home_desc"])
    print("Away coach:", result["away_desc"])
    print("Tactical edge:", result["tactical_edge"])
