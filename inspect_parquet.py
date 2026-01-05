"""
Parquet Schema Inspector
========================
This script inspects the schema and sample data from the AIS parquet file.

Usage:
    python inspect_parquet.py
"""

import pandas as pd
import pyarrow.parquet as pq

def inspect_parquet_schema(parquet_path: str):
    """
    Inspect parquet file schema and display sample data.
    
    Args:
        parquet_path: Path to the parquet file
    """
    print("=" * 80)
    print("PARQUET FILE INSPECTION")
    print("=" * 80)
    print(f"\nFile: {parquet_path}\n")
    
    # Method 1: Using PyArrow (fastest for schema only)
    print("-" * 80)
    print("1. SCHEMA INFORMATION (PyArrow)")
    print("-" * 80)
    parquet_file = pq.ParquetFile(parquet_path)
    schema = parquet_file.schema
    print(f"\nTotal columns: {len(schema.names)}")
    print(f"\nColumn names and types:")
    for i, (name, field) in enumerate(zip(schema.names, schema), 1):
        print(f"  {i:2d}. {name:25s} -> {field.type}")
    
    # Metadata
    print(f"\nNumber of row groups: {parquet_file.num_row_groups}")
    print(f"Total rows: {parquet_file.metadata.num_rows:,}")
    
    # Method 2: Using Pandas (for sample data)
    print("\n" + "-" * 80)
    print("2. SAMPLE DATA (First 5 rows)")
    print("-" * 80)
    df = pd.read_parquet(parquet_path, engine='pyarrow')
    print(f"\nDataFrame shape: {df.shape}")
    print(f"\nData types:")
    print(df.dtypes)
    
    print(f"\nFirst 5 rows:")
    print(df.head())
    
    # Statistics
    print("\n" + "-" * 80)
    print("3. BASIC STATISTICS")
    print("-" * 80)
    print(f"\nNumeric columns summary:")
    print(df.describe())
    
    # Missing values
    print(f"\nMissing values:")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(missing[missing > 0])
    else:
        print("  No missing values found")
    
    # Unique values for categorical columns
    print(f"\nUnique values in key columns:")
    for col in df.columns:
        if df[col].dtype == 'object' or df[col].nunique() < 20:
            print(f"  {col}: {df[col].nunique()} unique values")
    
    print("\n" + "=" * 80)
    print("INSPECTION COMPLETE")
    print("=" * 80)
    
    return df, schema


if __name__ == "__main__":
    # Path to the parquet file
    PARQUET_PATH = r"F:\PyTorch_GPU\maritime_monitoring_preprocessing\interpolated_results\interpolated_ais_data_20200105_20200112_15min_with_sog_cog.parquet"
    
    try:
        df, schema = inspect_parquet_schema(PARQUET_PATH)
        
        # Save column names to a text file for reference
        output_file = "parquet_columns.txt"
        with open(output_file, 'w') as f:
            f.write("Parquet File Columns\n")
            f.write("=" * 50 + "\n\n")
            for i, name in enumerate(schema.names, 1):
                f.write(f"{i}. {name}\n")
        
        print(f"\n✓ Column names saved to: {output_file}")
        
    except FileNotFoundError:
        print(f"ERROR: Parquet file not found at: {PARQUET_PATH}")
        print("Please verify the file path and try again.")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
