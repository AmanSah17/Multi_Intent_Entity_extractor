"""
Trajectory Service
==================
Handles trajectory data fetching and processing.
"""

import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from data.duckdb_manager import DuckDBManager
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TrajectoryService:
    """
    Trajectory data fetching and processing service.
    
    This class handles fetching raw AIS trajectory data and can be
    extended to support predicted trajectories from ML models.
    """
    
    def __init__(self, db_manager: DuckDBManager):
        """
        Initialize the trajectory service.
        
        Args:
            db_manager: DuckDB manager instance
        """
        self.db = db_manager
    
    def fetch_raw_trajectory(
        self,
        vessel_ids: List[str],
        time_range: Dict[str, datetime],
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Fetch raw AIS trajectory from Parquet.
        
        Args:
            vessel_ids: List of vessel IDs (MMSIs)
            time_range: Dictionary with 'start' and 'end' datetime objects
            limit: Maximum number of points to return
            
        Returns:
            DataFrame with trajectory data
            
        Example:
            >>> service = TrajectoryService(db)
            >>> time_range = {'start': datetime(2020, 1, 5), 'end': datetime(2020, 1, 12)}
            >>> df = service.fetch_raw_trajectory(['123456789'], time_range)
        """
        logger.info(f"Fetching trajectory for {len(vessel_ids)} vessel(s)")
        
        try:
            df = self.db.fetch_trajectory(
                vessel_ids=vessel_ids,
                start_time=time_range['start'],
                end_time=time_range['end'],
                limit=limit
            )
            
            logger.info(f"Fetched {len(df)} trajectory points")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch trajectory: {e}")
            raise
    
    def fetch_predicted_trajectory(
        self,
        vessel_ids: List[str],
        time_range: Dict[str, datetime],
        model_name: str = None
    ) -> pd.DataFrame:
        """
        Fetch ML-predicted trajectory.
        
        This is a placeholder for future ML model integration.
        
        Args:
            vessel_ids: List of vessel IDs
            time_range: Time range for prediction
            model_name: Name of ML model to use
            
        Returns:
            DataFrame with predicted trajectory
        """
        logger.warning("Predicted trajectory not yet implemented")
        # TODO: Implement ML model inference
        # For now, return empty DataFrame
        return pd.DataFrame()
    
    def calculate_trajectory_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate statistics for a trajectory.
        
        Args:
            df: Trajectory DataFrame
            
        Returns:
            Dictionary with statistics
        """
        if df.empty:
            return {}
        
        stats = {
            "total_points": len(df),
            "unique_vessels": df['mmsi'].nunique() if 'mmsi' in df.columns else 0,
            "time_span_hours": 0,
            "avg_speed": 0,
            "max_speed": 0,
        }
        
        if 'timestamp' in df.columns and len(df) > 1:
            time_span = pd.to_datetime(df['timestamp'].max()) - pd.to_datetime(df['timestamp'].min())
            stats["time_span_hours"] = time_span.total_seconds() / 3600
        
        if 'sog' in df.columns:
            stats["avg_speed"] = float(df['sog'].mean())
            stats["max_speed"] = float(df['sog'].max())
        
        return stats
