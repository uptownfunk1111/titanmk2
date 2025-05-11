import json
import os

def pretty_print_json(file_path):
    # Open the JSON file and load the data
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Pretty print the data and save it to a new file
    output_file_path = file_path.replace('.json', '_pretty.json')
    
    with open(output_file_path, 'w') as file:
        json.dump(data, file, indent=4)  # Pretty print with an indent of 4

    print(f"Pretty printed JSON saved to: {output_file_path}")

# List of the files to be pretty-printed (modify with your actual file paths)
files_to_pretty_print = [
    r'C:\Users\slangston1\TITAN\nrl_data_main\data\NRL\2024\NRL_player_statistics_2025.json',
    r'C:\Users\slangston1\TITAN\nrl_data_main\data\NRL\2024\NRL_data_2025.json',
    r'C:\Users\slangston1\TITAN\nrl_data_main\data\NRL\2024\NRL_detailed_match_data_2025.json'
]

# Pretty print each JSON file
for file_path in files_to_pretty_print:
    pretty_print_json(file_path)
