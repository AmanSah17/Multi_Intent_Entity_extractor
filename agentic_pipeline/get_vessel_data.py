"""
Get Actual Vessel Data
=======================
Extract real MMSI values from the parquet file for testing.
"""

import duckdb
import pandas as pd

# Connect to DuckDB
conn = duckdb.connect()

# Path to parquet file
parquet_path = r"F:\PyTorch_GPU\maritime_monitoring_preprocessing\interpolated_results\interpolated_ais_data_20200105_20200112_15min_with_sog_cog.parquet"

print("=" * 80)
print("EXTRACTING ACTUAL VESSEL DATA")
print("=" * 80)

# Get unique MMSIs
print("\n1. Getting unique MMSIs...")
query = f"""
SELECT DISTINCT MMSI, COUNT(*) as point_count
FROM read_parquet('{parquet_path}')
GROUP BY MMSI
ORDER BY point_count DESC
LIMIT 10
"""

df = conn.execute(query).df()
print(f"\nTop 10 vessels by data points:")
print(df)

# Get time range
print("\n2. Getting time range...")
query_time = f"""
SELECT 
    MIN(BaseDateTime) as min_time,
    MAX(BaseDateTime) as max_time
FROM read_parquet('{parquet_path}')
"""

df_time = conn.execute(query_time).df()
print(f"\nTime range:")
print(df_time)

# Get sample data for first vessel
if len(df) > 0:
    first_mmsi = df.iloc[0]['MMSI']
    print(f"\n3. Sample data for MMSI {first_mmsi}:")
    
    query_sample = f"""
    SELECT BaseDateTime, LAT, LON, SOG, COG
    FROM read_parquet('{parquet_path}')
    WHERE MMSI = '{first_mmsi}'
    ORDER BY BaseDateTime
    LIMIT 5
    """
    
    df_sample = conn.execute(query_sample).df()
    print(df_sample)

# Save MMSIs to file
print("\n4. Saving MMSIs to file...")
mmsi_list = df['MMSI'].tolist()
with open('actual_mmsis.txt', 'w') as f:
    f.write("Actual MMSIs from Dataset\n")
    f.write("=" * 50 + "\n\n")
    for i, mmsi in enumerate(mmsi_list, 1):
        f.write(f"{i}. {mmsi}\n")

print(f"\n✓ Saved {len(mmsi_list)} MMSIs to actual_mmsis.txt")

print("\n" + "=" * 80)
print("EXTRACTION COMPLETE")
print("=" * 80)
