import pandas as pd

file_path = "/home/crimsondeepdarshak/Desktop/Deep_Darshak/AIS_data_demo/processed/10_Day_US_interpolated_15min.parquet"

try:
    df = pd.read_parquet(file_path)
    print("Columns:", df.columns.tolist())
    print("\nData Types:")
    print(df.dtypes)
    print("\nSample Data (First 3 rows):")
    print(df.head(3))
    
    # Check if 'timestamp' or similar exists and convert to datetime to see format
    if 'timestamp' in df.columns:
        print("\nTimestamp range:")
        print(df['timestamp'].min(), "to", df['timestamp'].max())
    else:
        # Try to guess timestamp column
        print("\nNo 'timestamp' column found. Checking for datetime columns...")
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                 print(f"Found datetime column: {col}")
                 print(df[col].min(), "to", df[col].max())
                 
except Exception as e:
    print(f"Error reading parquet: {e}")
