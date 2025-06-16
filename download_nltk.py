import nltk
import os

# Define the local directory for NLTK data
local_nltk_data_path = os.path.join('.', 'nltk_data')

# Create the directory if it doesn't exist
if not os.path.exists(local_nltk_data_path):
    os.mkdir(local_nltk_data_path)
    print(f"Created directory: {local_nltk_data_path}")

# Add the local path to NLTK's data path
nltk.data.path.append(local_nltk_data_path)

# Download the 'punkt_tab' package to the specified directory
print(f"Downloading 'punkt_tab' to {local_nltk_data_path}...")
nltk.download('punkt_tab', download_dir=local_nltk_data_path)
print("Download complete.")