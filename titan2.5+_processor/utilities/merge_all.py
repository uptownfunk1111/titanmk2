import pandas as pd  # Ensure pandas is imported

def merge_all(match_df, player_df, detailed_df):
    print("[START] Merging all dataframes (match, player, detailed)...")
    # Add 'Year' column if missing
    if "Year" not in match_df.columns:
        print("⚠️ Missing 'Year' column in match_df. Adding 'Year'...")
        match_df["Year"] = 2025  # You can replace 2025 with the actual year if needed
    else:
        print("[INFO] 'Year' column present in match_df.")

    if "Year" not in player_df.columns:
        print("⚠️ Missing 'Year' column in player_df. Adding 'Year'...")
        player_df["Year"] = 2025  # Same for player_df
    else:
        print("[INFO] 'Year' column present in player_df.")

    if "Year" not in detailed_df.columns:
        print("⚠️ Missing 'Year' column in detailed_df. Adding 'Year'...")
        detailed_df["Year"] = 2025  # Same for detailed_df
    else:
        print("[INFO] 'Year' column present in detailed_df.")
    
    # Add MatchID in case it's missing from any dataframe
    if "MatchID" not in match_df.columns:
        print("⚠️ Missing 'MatchID' column in match_df. Adding 'MatchID' from 'MatchKey'...")
        match_df["MatchID"] = match_df["MatchKey"]
    else:
        print("[INFO] 'MatchID' column present in match_df.")

    if "MatchID" not in player_df.columns:
        print("⚠️ Missing 'MatchID' column in player_df. Adding 'MatchID' from 'MatchKey'...")
        player_df["MatchID"] = player_df["MatchKey"]  # Assuming MatchKey exists in player_df
    else:
        print("[INFO] 'MatchID' column present in player_df.")

    if "MatchID" not in detailed_df.columns:
        print("⚠️ Missing 'MatchID' column in detailed_df. Adding 'MatchID' from 'MatchKey'...")
        detailed_df["MatchID"] = detailed_df["MatchKey"]  # Assuming MatchKey exists in detailed_df
    else:
        print("[INFO] 'MatchID' column present in detailed_df.")
    
    # Check for missing 'Date' column and add placeholder if needed
    if "Date" not in match_df.columns:
        print("⚠️ Missing 'Date' column in match_df. Adding placeholder 'Date' (NaT)...")
        match_df["Date"] = pd.NaT  # Placeholder NaT (Not a Time) for missing dates
    else:
        print("[INFO] 'Date' column present in match_df.")

    if "Date" not in player_df.columns:
        print("⚠️ Missing 'Date' column in player_df. Adding placeholder 'Date' (NaT)...")
        player_df["Date"] = pd.NaT  # Placeholder NaT for missing dates
    else:
        print("[INFO] 'Date' column present in player_df.")

    if "Date" not in detailed_df.columns:
        print("⚠️ Missing 'Date' column in detailed_df. Adding placeholder 'Date' (NaT)...")
        detailed_df["Date"] = pd.NaT  # Placeholder NaT for missing dates
    else:
        print("[INFO] 'Date' column present in detailed_df.")

    print(f"[INFO] match_df shape before merge: {match_df.shape}")
    print(f"[INFO] player_df shape before merge: {player_df.shape}")
    print(f"[INFO] detailed_df shape before merge: {detailed_df.shape}")
    # Proceed with merge
    print("🔄 Merging match data with player and detailed stats...")
    df = pd.merge(match_df, player_df, on=["MatchID", "Date"], how="left", suffixes=("", "_player"))
    print(f"[INFO] Shape after merging match_df and player_df: {df.shape}")
    df = pd.merge(df, detailed_df, on=["MatchID", "Date"], how="left", suffixes=("", "_detailed"))
    print(f"[INFO] Shape after merging with detailed_df: {df.shape}")
    print("✅ Merge complete.")
    return df
