import json
import pandas as pd

def load_match_data(filepath, year):
    print(f"⏳ Loading match data from: {filepath}")
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        print(f"❌ Error reading match data: {e}")
        return pd.DataFrame()

    match_list = []
    
    # Check if the data is a list or dictionary and process accordingly
    if isinstance(raw, list):
        print("⚠️ Raw data is a list, processing directly...")
        for match in raw:
            if isinstance(match, dict):
                match["Year"] = year  # Ensure Year is added
                match["MatchKey"] = f"{year}-{match.get('HomeTeam', 'Unknown')}-{match.get('AwayTeam', 'Unknown')}"  # Example MatchKey format
                match_list.append(match)
            else:
                print(f"⚠️ Invalid match data format for match: {match}")
    elif isinstance(raw, dict):
        print("⚠️ Raw data is a dictionary, processing...")
        for match_data in raw.get("NRL", []):
            for round_data in match_data.values():
                for match in round_data:
                    if isinstance(match, dict):
                        match["Year"] = year  # Ensure Year is added
                        match["MatchKey"] = match.get("MatchKey", f"{year}-{match.get('HomeTeam', 'Unknown')}-{match.get('AwayTeam', 'Unknown')}")
                        match_list.append(match)
                    else:
                        print(f"⚠️ Invalid match data format for match: {match}")
    else:
        print(f"❌ Unsupported data structure: {type(raw)}")
        return pd.DataFrame()

    match_df = pd.DataFrame(match_list)

    # Ensure necessary columns exist
    if "MatchKey" not in match_df.columns:
        print(f"❌ Missing 'MatchKey' column in match data.")
        match_df["MatchKey"] = "Unknown"

    print(f"✅ Loaded match data: {len(match_df)} records.")
    return match_df
