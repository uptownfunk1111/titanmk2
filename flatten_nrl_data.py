import os
import json
import pandas as pd

def extract_nrl_data():
    # Prompt user for the directory path
    directory_path = input("Enter the directory path where the JSON file is located: ")
    
    # Check if the directory exists
    if not os.path.isdir(directory_path):
        print("The specified directory does not exist. Exiting.")
        return
    
    # List all JSON files in the provided directory
    files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
    
    if not files:
        print("No JSON files found in the specified directory.")
        return

    # Display the list of JSON files to the user
    print("Available JSON files:")
    for idx, file in enumerate(files, 1):
        print(f"{idx}. {file}")
    
    # Prompt user to select a file
    try:
        choice = int(input("\nEnter the number of the file to extract data from: "))
        if choice < 1 or choice > len(files):
            print("Invalid choice. Exiting.")
            return
        file_name = files[choice - 1]
    except ValueError:
        print("Invalid input. Exiting.")
        return

    # Build the full file path
    file_path = os.path.join(directory_path, file_name)

    # Read the selected JSON file
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading the file: {e}")
        return

    # Flattening the JSON data
    flattened_data = []

    # Iterate through the rounds and matches to extract all data
    for season_data in data["NRL"]:
        for year, rounds in season_data.items():
            for round_key, round_data in rounds[0].items():
                for match in round_data:
                    match_data = {
                        "Round": round_key,
                        "Home": match["Home"],
                        "Home_Score": match["Home_Score"],
                        "Away": match["Away"],
                        "Away_Score": match["Away_Score"],
                        "Venue": match["Venue"],
                        "Date": match["Date"],
                        "Match_Centre_URL": match["Match_Centre_URL"]
                    }
                    flattened_data.append(match_data)

    # Create a DataFrame from the flattened data
    df = pd.DataFrame(flattened_data)

    # Define the output file path (same directory)
    output_file_name = f"flattened_{file_name.replace('.json', '.csv')}"
    output_file_path = os.path.join(directory_path, output_file_name)

    # Save the DataFrame to CSV
    try:
        df.to_csv(output_file_path, index=False)
        print(f"\nSuccessfully extracted the data and saved it to {output_file_path}")
    except Exception as e:
        print(f"Error saving the file: {e}")
        return

if __name__ == "__main__":
    extract_nrl_data()
