
import pandas as pd
import glob
import os

# Define the pattern for CSV files
csv_pattern = "/home/crimsondeepdarshak/Desktop/Deep_Darshak/AIS_data_demo/ais-*.csv"

# Get the first matching file
files = glob.glob(csv_pattern)
if not files:
    print("No CSV files found matching the pattern.")
else:
    file_path = files[0]
    print(f"Inspecting file: {file_path}")
    try:
        # Read just the first few rows
        df = pd.read_csv(file_path, nrows=5)
        print("Columns:", df.columns.tolist())
        print("\nSample Data:")
        print(df.head())
    except Exception as e:
        print(f"Error reading CSV: {e}")
