import json
import pandas as pd

def load_match_data(filepath, year):
    print(f"⏳ [MATCH LOADER] Loading match data from: {filepath}")
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
        print(f"[INFO] Successfully loaded JSON file: {filepath}")
    except Exception as e:
        print(f"❌ [ERROR] Error reading match data: {e}")
        return pd.DataFrame()

    match_list = []
    
    # Check if the data is a list or dictionary and process accordingly
    if isinstance(raw, list):
        print("⚠️ [WARN] Raw data is a list, processing directly...")
        for idx, match in enumerate(raw):
            if isinstance(match, dict):
                match["Year"] = year  # Ensure Year is added
                match["MatchKey"] = f"{year}-{match.get('HomeTeam', 'Unknown')}-{match.get('AwayTeam', 'Unknown')}"  # Example MatchKey format
                match_list.append(match)
                if idx < 3:
                    print(f"[DEBUG] Sample match {idx+1}: {match}")
            else:
                print(f"⚠️ [WARN] Invalid match data format for match: {match}")
    elif isinstance(raw, dict):
        print("⚠️ [WARN] Raw data is a dictionary, processing...")
        for match_data in raw.get("NRL", []):
            for round_key, round_data in match_data.items():
                print(f"[PROGRESS] Processing round: {round_key}, {len(round_data)} matches.")
                for idx, match in enumerate(round_data):
                    if isinstance(match, dict):
                        match["Year"] = year  # Ensure Year is added
                        match["MatchKey"] = match.get("MatchKey", f"{year}-{match.get('HomeTeam', 'Unknown')}-{match.get('AwayTeam', 'Unknown')}")
                        match_list.append(match)
                        if idx < 3:
                            print(f"[DEBUG] Sample match {idx+1} in round {round_key}: {match}")
                    else:
                        print(f"⚠️ [WARN] Invalid match data format for match: {match}")
    else:
        print(f"❌ [ERROR] Unsupported data structure: {type(raw)}")
        return pd.DataFrame()

    match_df = pd.DataFrame(match_list)

    # Ensure necessary columns exist
    if "MatchKey" not in match_df.columns:
        print(f"❌ [ERROR] Missing 'MatchKey' column in match data.")
        match_df["MatchKey"] = "Unknown"

    print(f"✅ [COMPLETE] Loaded match data: {len(match_df)} records. Columns: {list(match_df.columns)}")
    return match_df
