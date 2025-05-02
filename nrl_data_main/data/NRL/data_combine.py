import pandas as pd
import os

# List of all the CSV files for each year (adjust as necessary)
files = [
    'C:/Users/slangston1/TITAN/nrl_data_main/data/NRL/2025/merged_nrl_data.csv',
    'C:/Users/slangston1/TITAN/nrl_data_main/data/NRL/2024/merged_nrl_data.csv',
    'C:/Users/slangston1/TITAN/nrl_data_main/data/NRL/2023/merged_nrl_data.csv',
    'C:/Users/slangston1/TITAN/nrl_data_main/data/NRL/2023/merged_nrl_data.csv',
    'C:/Users/slangston1/TITAN/nrl_data_main/data/NRL/2022/merged_nrl_data.csv',
    'C:/Users/slangston1/TITAN/nrl_data_main/data/NRL/2021/merged_nrl_data.csv',
    'C:/Users/slangston1/TITAN/nrl_data_main/data/NRL/2020/merged_nrl_data.csv',
    'C:/Users/slangston1/TITAN/nrl_data_main/data/NRL/2019/merged_nrl_data.csv',
    # Add more files as needed
]

# Create an empty DataFrame to combine all data
combined_data = pd.DataFrame()

# Iterate over the files and concatenate them into the combined_data DataFrame
for file in files:
    year_data = pd.read_csv(file)
    combined_data = pd.concat([combined_data, year_data])

# Reset the index to avoid duplicates
combined_data.reset_index(drop=True, inplace=True)

# Check for missing data
print("Missing Data:")
print(combined_data.isnull().sum())

# Save the combined data to a new CSV file
combined_data.to_csv("combined_nrl_data.csv", index=False)

print("Data combined and saved as combined_nrl_data.csv")
