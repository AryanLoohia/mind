import pandas as pd
import os
import json

# Directory containing JSON files
json_dir = 'C:\\Users\\bit\\Desktop\\reg\\reg\\user_data\\'  # Use double backslashes or a raw string

# List to hold extracted data
data = []

# Loop through all JSON files in the directory
for filename in os.listdir(json_dir):
    if filename.endswith('.json'):
        filepath = os.path.join(json_dir, filename)
        with open(filepath, 'r') as file:
            json_data = json.load(file)
            # Extract name and phone number
            name = json_data.get('name')
            phone = json_data.get('phone')
            # Append extracted data to list
            data.append({'name': name, 'phone': phone})

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to an Excel file
output_excel_path = 'output_file.xlsx'  # You can change this to your desired file name
df.to_excel(output_excel_path, index=False)

print(f'Data successfully extracted to {output_excel_path}')
