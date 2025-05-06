import pandas as pd

# Load the combined NRL data from Excel
file_path = r'C:\Users\slangston1\titan\nrl_data_main\data\NRL\combined_nrl_data.json'
combined_nrl_data = pd.read_json(file_path)

# Impute missing values for the 'NRL' column (categorical data)
combined_nrl_data['NRL'] = combined_nrl_data['NRL'].fillna(combined_nrl_data['NRL'].mode()[0])

# Impute missing values for the 'PlayerStats' column (numerical data)
combined_nrl_data['PlayerStats'] = combined_nrl_data['PlayerStats'].fillna(combined_nrl_data['PlayerStats'].median())

# Save the imputed data back to Excel
output_file = r'C:\Users\slangston1\titan\nrl_data_main\data\NRL\combined_nrl_data_imputed.json'
combined_nrl_data.to_json(output_file, index=False)

print(f"Data imputation completed. Output saved to {output_file}")
