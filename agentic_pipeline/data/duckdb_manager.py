"""
DuckDB Manager
==============
DuckDB connection manager with safe query execution.
"""

import duckdb
import pandas as pd
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DuckDBManager:
    """
    DuckDB connection manager with query builders.
    
    This class provides safe, parameterized query execution for AIS data
    stored in Parquet files.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize DuckDB connection.
        
        Args:
            db_path: Path to DuckDB database file, or ":memory:" for in-memory
        """
        self.db_path = db_path or settings.duckdb_path
        self.conn = duckdb.connect(self.db_path)
        logger.info(f"DuckDB connection established: {self.db_path}")
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> pd.DataFrame:
        """
        Execute a SQL query safely and return results as DataFrame.
        
        Args:
            query: SQL query string (use ? for parameters)
            params: Optional tuple of parameters
            
        Returns:
            Pandas DataFrame with query results
            
        Example:
            >>> db = DuckDBManager()
            >>> df = db.execute_query("SELECT * FROM ais WHERE MMSI = ?", ("123456789",))
        """
        try:
            logger.debug(f"Executing query: {query}")
            if params:
                result = self.conn.execute(query, params)
            else:
                result = self.conn.execute(query)
            
            df = result.df()
            logger.info(f"Query returned {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            raise
    
    def build_trajectory_query(
        self,
        vessel_ids: List[str],
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000
    ) -> str:
        """
        Build a safe trajectory query.
        
        Args:
            vessel_ids: List of vessel IDs (MMSIs)
            start_time: Start datetime
            end_time: End datetime
            limit: Maximum number of rows to return
            
        Returns:
            SQL query string
        """
        # Build MMSI list for IN clause
        mmsi_list = ", ".join([f"'{mmsi}'" for mmsi in vessel_ids])
        
        # Format timestamps
        start_str = start_time.isoformat()
        end_str = end_time.isoformat()
        
        query = f"""
        SELECT 
            {settings.col_timestamp} as timestamp,
            {settings.col_latitude} as latitude,
            {settings.col_longitude} as longitude,
            {settings.col_mmsi} as mmsi,
            {settings.col_sog} as sog,
            {settings.col_cog} as cog,
            {settings.col_interpolated} as interpolated
        FROM ais
        WHERE {settings.col_mmsi} IN ({mmsi_list})
          AND {settings.col_timestamp} >= '{start_str}'
          AND {settings.col_timestamp} <= '{end_str}'
        ORDER BY {settings.col_timestamp}
        LIMIT {limit}
        """
        
        return query
    
    def fetch_trajectory(
        self,
        vessel_ids: List[str],
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Fetch trajectory data for specified vessels and time range.
        
        Args:
            vessel_ids: List of vessel IDs (MMSIs)
            start_time: Start datetime
            end_time: End datetime
            limit: Maximum number of rows
            
        Returns:
            DataFrame with trajectory data
        """
        query = self.build_trajectory_query(vessel_ids, start_time, end_time, limit)
        return self.execute_query(query)
    
    def get_unique_vessels(self) -> List[str]:
        """
        Get list of unique vessel MMSIs in the dataset.
        
        Returns:
            List of unique MMSIs
        """
        query = f"SELECT DISTINCT {settings.col_mmsi} as mmsi FROM ais ORDER BY mmsi"
        df = self.execute_query(query)
        return df['mmsi'].tolist()
    
    def get_vessel_count(self) -> int:
        """
        Get total number of unique vessels.
        
        Returns:
            Count of unique vessels
        """
        query = f"SELECT COUNT(DISTINCT {settings.col_mmsi}) as count FROM ais"
        df = self.execute_query(query)
        return int(df['count'].iloc[0])
    
    def get_time_range(self) -> Tuple[datetime, datetime]:
        """
        Get the time range of data in the dataset.
        
        Returns:
            Tuple of (min_time, max_time)
        """
        query = f"""
        SELECT 
            MIN({settings.col_timestamp}) as min_time,
            MAX({settings.col_timestamp}) as max_time
        FROM ais
        """
        df = self.execute_query(query)
        return pd.to_datetime(df['min_time'].iloc[0]), pd.to_datetime(df['max_time'].iloc[0])
    
    def close(self):
        """Close the DuckDB connection."""
        if self.conn:
            self.conn.close()
            logger.info("DuckDB connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
