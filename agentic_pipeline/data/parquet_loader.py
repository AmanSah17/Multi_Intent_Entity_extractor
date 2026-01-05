"""
Parquet Loader
==============
Load and inspect Parquet files for AIS data.
"""

import pyarrow.parquet as pq
from typing import Dict, List
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ParquetLoader:
    """
    Parquet file loader with schema detection.
    
    This class handles loading and inspecting Parquet files containing
    AIS (Automatic Identification System) data.
    """
    
    def __init__(self):
        """Initialize the Parquet loader."""
        self.schema = None
        self.parquet_file = None
    
    def load_schema(self, path: str) -> Dict[str, str]:
        """
        Detect and return the Parquet file schema.
        
        Args:
            path: Path to the Parquet file
            
        Returns:
            Dictionary mapping column names to data types
            
        Example:
            >>> loader = ParquetLoader()
            >>> schema = loader.load_schema("data.parquet")
            >>> print(schema)
            {'BaseDateTime': 'timestamp', 'LAT': 'double', ...}
        """
        logger.info(f"Loading schema from: {path}")
        
        try:
            self.parquet_file = pq.ParquetFile(path)
            self.schema = self.parquet_file.schema
            
            # Convert to dict
            schema_dict = {}
            for name, field in zip(self.schema.names, self.schema):
                schema_dict[name] = str(field.type)
            
            logger.info(f"Schema loaded: {len(schema_dict)} columns")
            return schema_dict
            
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            raise
    
    def get_column_names(self, path: str) -> List[str]:
        """
        Get list of column names from Parquet file.
        
        Args:
            path: Path to the Parquet file
            
        Returns:
            List of column names
        """
        if not self.schema:
            self.load_schema(path)
        
        return self.schema.names
    
    def get_row_count(self, path: str) -> int:
        """
        Get total number of rows in Parquet file.
        
        Args:
            path: Path to the Parquet file
            
        Returns:
            Total row count
        """
        if not self.parquet_file:
            self.parquet_file = pq.ParquetFile(path)
        
        return self.parquet_file.metadata.num_rows
    
    def register_with_duckdb(self, conn, path: str, table_name: str = "ais"):
        """
        Register Parquet file as a DuckDB table.
        
        Args:
            conn: DuckDB connection object
            path: Path to the Parquet file
            table_name: Name for the table in DuckDB
            
        Example:
            >>> import duckdb
            >>> conn = duckdb.connect()
            >>> loader = ParquetLoader()
            >>> loader.register_with_duckdb(conn, "data.parquet", "ais")
        """
        logger.info(f"Registering Parquet file as table '{table_name}'")
        
        try:
            # DuckDB can directly query Parquet files
            # Create a view for easier querying
            query = f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM read_parquet('{path}')"
            conn.execute(query)
            
            logger.info(f"Table '{table_name}' registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to register table: {e}")
            raise
