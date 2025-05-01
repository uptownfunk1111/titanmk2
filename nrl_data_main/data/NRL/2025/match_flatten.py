import json
import pandas as pd

# Load JSON file
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Flatten and prepare data
def flatten_data(json_data):
    # This will store the flattened data
    flat_data = []
    
    # Loop through all rounds and matchups
    for year_data in json_data.get('NRL', []):
        for year, rounds in year_data.items():
            for round_data in rounds:
                for round_key, matches in round_data.items():
                    for match in matches:
                        match_info = {
                            "Round": match.get("Round"),
                            "Home": match.get("Home"),
                            "Home_Score": match.get("Home_Score"),
                            "Away": match.get("Away"),
                            "Away_Score": match.get("Away_Score"),
                            "Venue": match.get("Venue"),
                            "Date": match.get("Date"),
                            "Match_Centre_URL": match.get("Match_Centre_URL")
                        }
                        flat_data.append(match_info)
    
    return flat_data

# Convert to DataFrame
def convert_to_dataframe(flat_data):
    df = pd.DataFrame(flat_data)
    
    # Example of creating a label for home win
    df["Home_Win"] = df["Home_Score"] > df["Away_Score"]
    
    # Optional: convert Date to datetime and extract more features
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    
    return df

# Main function to load, flatten, and prepare the data
def process_nrl_data(file_path):
    json_data = load_json(file_path)
    flat_data = flatten_data(json_data)
    df = convert_to_dataframe(flat_data)
    
    return df

# File path to JSON data
file_path = "C:/Users/slangston1/TITAN/nrl_data_main/data/NRL/2025/NRL_data_2025_pretty.json"
nrl_df = process_nrl_data(file_path)

# Output to CSV for further use
nrl_df.to_csv("nrl_data_2025_processed.csv", index=False)
print("Processed data saved to 'nrl_data_2025_processed.csv'")
