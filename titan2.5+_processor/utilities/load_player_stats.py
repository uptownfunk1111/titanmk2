import json
import pandas as pd

def load_player_stats(filepath, year):
    print(f"⏳ Loading player stats for {year} from: {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return pd.DataFrame()

    data = raw.get("PlayerStats", [])
    if not data:
        print(f"⚠️  No 'PlayerStats' section found in: {filepath}")
        return pd.DataFrame()

    player_records = []

    match_count = 0
    player_count = 0

    # Loop through each match data
    for match in data:
        match_id = match.get("MatchID")
        date = match.get("Date")
        home = match.get("HomeTeam")
        away = match.get("AwayTeam")
        round_num = match.get("Round")
        players = match.get("Players", [])

        match_count += 1
        player_count += len(players)

        # Process each player in the match
        for p in players:
            jersey = int(p.get("Jersey", 0))  # Convert Jersey to int to compare
            position = p.get("Position", "Unknown")  # Default to Unknown if Position is missing

            # Apply the rule: Players with jersey >= 14 should be "Interchange"
            if jersey >= 14:
                position = "Interchange"
            
            entry = {
                "Date": date,
                "Year": year,
                "Round": round_num,
                "MatchID": match_id,
                "HomeTeam": home,
                "AwayTeam": away,
                "Player": p.get("Name"),
                "Team": p.get("Team"),
                "Position": position,  # Updated Position
                "Jersey": jersey,  # Adding Jersey number if needed
                "Tries": p.get("Tries", 0),
                "TryAssists": p.get("Try Assists", 0),
                "RunMetres": p.get("All Run Metres", 0),
                "Tackles": p.get("Tackles Made", 0),
                "Errors": p.get("Errors", 0),
                "Minutes": p.get("Minutes", 0),
            }
            player_records.append(entry)

    print(f"📦 Processed {match_count} matches and {player_count} players.")

    # Convert player records into a DataFrame
    df = pd.DataFrame(player_records)

    # Handle missing or empty DataFrame
    if df.empty:
        print(f"[WARNING] No valid player records found in: {filepath}")
        return df

    print("🧼 Cleaning and converting stat fields...")

    # Clean all stat columns: replace '-', '', 'N/A', 'null' with 0, and convert to numeric
    stat_cols = [col for col in df.columns if col not in ['Date', 'Year', 'Round', 'MatchID', 'HomeTeam', 'AwayTeam', 'Player', 'Team', 'Position', 'Jersey']]
    df[stat_cols] = df[stat_cols].replace(['-', '', 'N/A', 'null'], 0)
    for col in stat_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    print(f"[INFO] Cleaned all stat columns: {stat_cols}")
    print(df[stat_cols].head())

    # Convert the "Date" column to datetime format
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    else:
        df["Date"] = pd.NaT
        print("⚠️  'Date' field missing — assigning NaT.")

    # Calculate ImpactScore based on relevant stats
    df["ImpactScore"] = (
        df["Tries"] * 10 +
        df["TryAssists"] * 8 +
        df["RunMetres"] * 0.1 +
        df["Tackles"] * 0.5 -
        df["Errors"] * 2
    )

    print(f"✅ Finished processing player stats for {year}.")
    return df
