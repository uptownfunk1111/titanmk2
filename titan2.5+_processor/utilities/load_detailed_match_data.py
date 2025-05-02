import json
import pandas as pd

def load_detailed_match_data(filepath):
    print(f"⏳ Loading detailed match data from: {filepath}")
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        print(f"❌ Error reading detailed match data: {e}")
        return pd.DataFrame()

    # Check if the data is a list or dictionary and process accordingly
    if isinstance(raw, list):
        print("⚠️ Raw data is a list, processing directly...")
        match_list = raw  # If it's a list, process as it is
    elif isinstance(raw, dict):
        print("⚠️ Raw data is a dictionary, extracting data...")
        match_list = []
        for match_data in raw.get("NRL", []):
            for round_data in match_data.values():
                for match in round_data:
                    for match_key, match_info in match.items():
                        match_info["MatchID"] = match_key  # Ensure MatchID is set here
                        match_info["Year"] = int(match_info.get("Year", 2025))  # Ensure year is added
                        match_list.append(match_info)
    else:
        print(f"❌ Unsupported data structure: {type(raw)}")
        return pd.DataFrame()

    # Convert to DataFrame
    detailed_df = pd.DataFrame(match_list)

    if detailed_df.empty:
        print(f"⚠️ No detailed match records loaded from: {filepath}")
        return detailed_df

    # Ensure Date is converted to datetime
    detailed_df["Date"] = pd.to_datetime(detailed_df["Date"], errors="coerce")

    # Ensure MatchID is available for merging
    if "MatchID" not in detailed_df.columns:
        detailed_df["MatchID"] = detailed_df["MatchKey"]

    print(f"✅ Loaded detailed data: {len(detailed_df)} records.")
    return detailed_df
