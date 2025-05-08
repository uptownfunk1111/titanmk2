import json
import pandas as pd
import re

# === Jersey number → expected position mapping ===
POSITION_BY_NUMBER = {
    1: "Fullback",
    2: "Wing",
    3: "Centre",
    4: "Centre",
    5: "Wing",
    6: "Five-Eighth",
    7: "Halfback",
    8: "Prop",
    9: "Hooker",
    10: "Prop",
    11: "Second Row",
    12: "Second Row",
    13: "Lock",
    14: "Utility",
    15: "Interchange",
    16: "Interchange",
    17: "Interchange",
}

# === Acceptable label mappings ===
EQUIVALENT_POSITIONS = {
    "Winger": "Wing",
    "2nd Row": "Second Row",
    "Replacement": "Interchange",
    "Bench": "Interchange",
    "Substitute": "Interchange",
    "Lock Forward": "Lock",
    "Five-eighth": "Five-Eighth",
    "Half": "Halfback",
    "Interchange": "Utility",  # Optional equivalence
}

def safe_number(val):
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, str):
        val = val.strip()
        if val in ["-", "", "N/A", "null", None]:
            return 0
        try:
            return int(val)
        except:
            try:
                return float(val)
            except:
                return 0
    return 0

def safe_minutes(val):
    if isinstance(val, str) and re.match(r"^\d+:\d+$", val):
        minutes, seconds = map(int, val.split(":"))
        return round(minutes + seconds / 60, 2)
    return safe_number(val)

def infer_team(num_str, home, away):
    try:
        num = int(num_str)
        if 1 <= num <= 13:
            return home
        elif 14 <= num <= 24:
            return away
    except:
        pass
    return None

def infer_position_from_number(num_str):
    try:
        num = int(num_str)
        return POSITION_BY_NUMBER.get(num, "Unknown")
    except:
        return "Unknown"

def load_player_stats_custom(filepath, year):
    print(f"⏳ [Custom Loader] Loading structured player stats from: {filepath}")
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
        print(f"[INFO] Successfully loaded JSON file: {filepath}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return pd.DataFrame()

    player_records = []
    root = raw.get("PlayerStats", [])
    print(f"[INFO] Found {len(root)} year entries in PlayerStats root.")

    for year_entry in root:
        if not isinstance(year_entry, dict):
            print(f"[WARN] Skipping non-dict year entry: {year_entry}")
            continue
        for round_group in year_entry.get(str(year), []):
            for round_num, match_blocks in round_group.items():
                print(f"[PROGRESS] Processing Year {year}, Round {round_num}, {len(match_blocks)} matches.")
                for match_dict in match_blocks:
                    for match_key, players in match_dict.items():
                        try:
                            match_parts = match_key.split("-")
                            home_team = match_parts[-3]
                            away_team = match_parts[-1]
                        except:
                            home_team = None
                            away_team = None
                        print(f"[DEBUG] MatchKey: {match_key}, Home: {home_team}, Away: {away_team}, Players: {len(players)}")
                        for player in players:
                            jersey = player.get("Number")
                            inferred_team = infer_team(jersey, home_team, away_team)
                            inferred_pos = infer_position_from_number(jersey)
                            original_pos = player.get("Position")

                            # Normalise both sides
                            norm_original = EQUIVALENT_POSITIONS.get(original_pos, original_pos)
                            norm_inferred = EQUIVALENT_POSITIONS.get(inferred_pos, inferred_pos)

                            # Suppress warnings for interchange range (14–17)
                            try:
                                jersey_num = int(jersey)
                                suppress_warning = jersey_num in [14, 15, 16, 17]
                            except:
                                suppress_warning = False

                            if not suppress_warning and norm_original and norm_inferred and norm_original.lower() != norm_inferred.lower():
                                print(f"⚠️ Position mismatch: {player.get('Name')} — Jersey {jersey} marked as '{original_pos}', expected '{inferred_pos}'")

                            entry = {
                                "Year": year,
                                "Round": round_num,
                                "MatchKey": match_key,
                                "HomeTeam": home_team,
                                "AwayTeam": away_team,
                                "Player": player.get("Name"),
                                "Number": jersey,
                                "Team": inferred_team,
                                "Position": original_pos,
                                "PosFromNumber": inferred_pos,
                                "Tries": safe_number(player.get("Tries")),
                                "TryAssists": safe_number(player.get("Try Assists")),
                                "RunMetres": safe_number(player.get("All Run Metres")),
                                "Tackles": safe_number(player.get("Tackles Made")),
                                "Errors": safe_number(player.get("Errors")),
                                "Minutes": safe_minutes(player.get("Mins Played")),
                            }
                            player_records.append(entry)
                        print(f"[INFO] Processed {len(players)} players for match {match_key}.")

    df = pd.DataFrame(player_records)

    if df.empty:
        print(f"⚠️ No valid players loaded from: {filepath}")
        return df

    # Clean all stat columns: replace '-', '', 'N/A', 'null' with 0, and convert to numeric
    stat_cols = [col for col in df.columns if col not in ['Year', 'Round', 'MatchKey', 'HomeTeam', 'AwayTeam', 'Player', 'Number', 'Team', 'Position', 'PosFromNumber']]
    df[stat_cols] = df[stat_cols].replace(['-', '', 'N/A', 'null'], 0)
    for col in stat_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    print(f"[INFO] Cleaned all stat columns: {stat_cols}")
    print(df[stat_cols].head())

    print(f"[INFO] Total player records loaded: {len(df)}")
    df["ImpactScore"] = (
        df["Tries"] * 10 +
        df["TryAssists"] * 8 +
        df["RunMetres"] * 0.1 +
        df["Tackles"] * 0.5 -
        df["Errors"] * 2
    )

    print(f"✅ Loaded {len(df)} players with team and position inference.")
    print(f"[COMPLETE] Player stats loading and processing finished.")
    return df
