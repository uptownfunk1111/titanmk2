import json
import pandas as pd

def flatten_json(json_data):
    """
    Flattens a nested JSON structure into a flat dictionary (suitable for creating a DataFrame).
    """
    def flatten(nested_dict, parent_key='', sep='_'):
        """
        Recursively flattens the dictionary.
        """
        items = []
        for k, v in nested_dict.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    return flatten(json_data)

def process_json_file(file_path):
    """
    Loads and flattens the JSON file, then returns the flattened data.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    flattened_data = []
    if isinstance(data, list):
        for item in data:
            flattened_data.append(flatten_json(item))
    else:
        flattened_data.append(flatten_json(data))
    
    return flattened_data

# Define the paths to the JSON files you uploaded
json_files = [
    r'C:\Users\slangston1\titan\nrl_data_main\data\NRL\2024\NRL_data_2024.json',
    r'C:\Users\slangston1\titan\nrl_data_main\data\NRL\2024\NRL_detailed_match_data_2024.json',
    r'C:\Users\slangston1\titan\nrl_data_main\data\NRL\2024\NRL_player_statistics_2024.json'
]

# Process all files and collect their data
all_data = []
for file_path in json_files:
    print(f"Processing file: {file_path}")
    flattened_data = process_json_file(file_path)
    all_data.extend(flattened_data)

# Convert the collected data into a DataFrame
df = pd.DataFrame(all_data)

# Display the first few rows to inspect the data
print(f"Data preview:\n{df.head()}")

# Save the resulting DataFrame to a CSV file
output_file = r'C:\Users\slangston1\titan\nrl_data_main\data\NRL\2024\merged_nrl_data.json'
df.to_json(output_file, index=False)

print(f"Data saved to: {output_file}")
