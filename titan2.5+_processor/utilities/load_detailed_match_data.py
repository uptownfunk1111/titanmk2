import json
import pandas as pd

def load_detailed_match_data(filepath):
    print(f"⏳ [DETAILED MATCH LOADER] Loading detailed match data from: {filepath}")
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
        print(f"[INFO] Successfully loaded JSON file: {filepath}")
    except Exception as e:
        print(f"❌ [ERROR] Error reading detailed match data: {e}")
        return pd.DataFrame()

    # Check if the data is a list or dictionary and process accordingly
    if isinstance(raw, list):
        print("⚠️ [WARN] Raw data is a list, processing directly...")
        match_list = raw  # If it's a list, process as it is
        for idx, match in enumerate(match_list[:3]):
            print(f"[DEBUG] Sample detailed match {idx+1}: {match}")
    elif isinstance(raw, dict):
        print("⚠️ [WARN] Raw data is a dictionary, extracting data...")
        match_list = []
        for match_data in raw.get("NRL", []):
            for round_key, round_data in match_data.items():
                print(f"[PROGRESS] Processing round: {round_key}, {len(round_data)} matches.")
                for idx, match in enumerate(round_data):
                    for match_key, match_info in match.items():
                        match_info["MatchID"] = match_key  # Ensure MatchID is set here
                        match_info["Year"] = int(match_info.get("Year", 2025))  # Ensure year is added
                        match_list.append(match_info)
                        if idx < 3:
                            print(f"[DEBUG] Sample match {idx+1} in round {round_key}: {match_info}")
    else:
        print(f"❌ [ERROR] Unsupported data structure: {type(raw)}")
        return pd.DataFrame()

    # Convert to DataFrame
    detailed_df = pd.DataFrame(match_list)

    if detailed_df.empty:
        print(f"⚠️ [WARN] No detailed match records loaded from: {filepath}")
        return detailed_df

    # Ensure Date is converted to datetime
    print("[INFO] Converting 'Date' column to datetime...")
    detailed_df["Date"] = pd.to_datetime(detailed_df["Date"], errors="coerce")

    # Ensure MatchID is available for merging
    if "MatchID" not in detailed_df.columns:
        print("⚠️ [WARN] 'MatchID' column missing, using 'MatchKey' instead.")
        detailed_df["MatchID"] = detailed_df["MatchKey"]

    print(f"✅ [COMPLETE] Loaded detailed data: {len(detailed_df)} records. Columns: {list(detailed_df.columns)}")
    return detailed_df
