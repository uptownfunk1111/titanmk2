import pandas as pd  # Ensure pandas is imported

def merge_all(match_df, player_df, detailed_df):
    # Add 'Year' column if missing
    if "Year" not in match_df.columns:
        print("⚠️ Missing 'Year' column in match_df. Adding 'Year'...")
        match_df["Year"] = 2025  # You can replace 2025 with the actual year if needed

    if "Year" not in player_df.columns:
        print("⚠️ Missing 'Year' column in player_df. Adding 'Year'...")
        player_df["Year"] = 2025  # Same for player_df

    if "Year" not in detailed_df.columns:
        print("⚠️ Missing 'Year' column in detailed_df. Adding 'Year'...")
        detailed_df["Year"] = 2025  # Same for detailed_df
    
    # Add MatchID in case it's missing from any dataframe
    if "MatchID" not in match_df.columns:
        print("⚠️ Missing 'MatchID' column in match_df. Adding 'MatchID'...")
        match_df["MatchID"] = match_df["MatchKey"]

    if "MatchID" not in player_df.columns:
        print("⚠️ Missing 'MatchID' column in player_df. Adding 'MatchID'...")
        player_df["MatchID"] = player_df["MatchKey"]  # Assuming MatchKey exists in player_df

    if "MatchID" not in detailed_df.columns:
        print("⚠️ Missing 'MatchID' column in detailed_df. Adding 'MatchID'...")
        detailed_df["MatchID"] = detailed_df["MatchKey"]  # Assuming MatchKey exists in detailed_df
    
    # Check for missing 'Date' column and add placeholder if needed
    if "Date" not in match_df.columns:
        print("⚠️ Missing 'Date' column in match_df. Adding 'Date'...")
        match_df["Date"] = pd.NaT  # Placeholder NaT (Not a Time) for missing dates

    if "Date" not in player_df.columns:
        print("⚠️ Missing 'Date' column in player_df. Adding 'Date'...")
        player_df["Date"] = pd.NaT  # Placeholder NaT for missing dates

    if "Date" not in detailed_df.columns:
        print("⚠️ Missing 'Date' column in detailed_df. Adding 'Date'...")
        detailed_df["Date"] = pd.NaT  # Placeholder NaT for missing dates

    # Proceed with merge
    print("🔄 Merging match data with player and detailed stats...")
    df = pd.merge(match_df, player_df, on=["MatchID", "Date"], how="left")
    df = pd.merge(df, detailed_df, on=["MatchID", "Date"], how="left")

    print("✅ Merge complete.")
    return df
