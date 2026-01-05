"""
Response Builder
================
Formats query results into user-friendly outputs.
"""

import pandas as pd
from typing import Any, Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ResponseBuilder:
    """
    Builds formatted responses from query results.
    
    This class handles formatting data into different output formats:
    - Table: Pandas DataFrame or formatted string
    - Map: GeoJSON or coordinate data for visualization
    - Summary: Natural language summary
    """
    
    def __init__(self):
        """Initialize the response builder."""
        pass
    
    def build_response(
        self,
        df: pd.DataFrame,
        output_format: str = "table",
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Build a formatted response from DataFrame.
        
        Args:
            df: Result DataFrame
            output_format: Output format ("table", "map", "summary")
            limit: Maximum number of rows to include
            
        Returns:
            Dictionary with formatted response
            
        Example:
            >>> builder = ResponseBuilder()
            >>> response = builder.build_response(df, "table", 50)
        """
        if df is None or df.empty:
            return {
                "format": output_format,
                "data": None,
                "message": "No results found",
                "count": 0
            }
        
        # Apply limit
        df_limited = df.head(limit)
        
        if output_format == "table":
            return self.build_table_response(df_limited)
        elif output_format == "map":
            return self.build_map_response(df_limited)
        elif output_format == "summary":
            return self.build_summary(df_limited)
        else:
            logger.warning(f"Unknown output format: {output_format}, defaulting to table")
            return self.build_table_response(df_limited)
    
    def build_table_response(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Format as table response.
        
        Args:
            df: DataFrame to format
            
        Returns:
            Dictionary with table data
        """
        return {
            "format": "table",
            "data": df.to_dict(orient='records'),
            "columns": list(df.columns),
            "count": len(df),
            "message": f"Found {len(df)} results"
        }
    
    def build_map_response(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Format as map visualization data.
        
        Args:
            df: DataFrame with latitude/longitude columns
            
        Returns:
            Dictionary with map data (GeoJSON-like format)
        """
        if 'latitude' not in df.columns or 'longitude' not in df.columns:
            logger.warning("DataFrame missing latitude/longitude columns for map")
            return self.build_table_response(df)
        
        # Build GeoJSON-like structure
        features = []
        for _, row in df.iterrows():
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row['longitude'], row['latitude']]
                },
                "properties": {k: v for k, v in row.items() if k not in ['latitude', 'longitude']}
            }
            features.append(feature)
        
        return {
            "format": "map",
            "data": {
                "type": "FeatureCollection",
                "features": features
            },
            "count": len(features),
            "message": f"Found {len(features)} points"
        }
    
    def build_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Build a natural language summary.
        
        Args:
            df: DataFrame to summarize
            
        Returns:
            Dictionary with summary text
        """
        if df.empty:
            return {
                "format": "summary",
                "data": "No results found",
                "count": 0
            }
        
        summary_parts = []
        
        # Basic stats
        summary_parts.append(f"Found {len(df)} records")
        
        # Vessel count
        if 'mmsi' in df.columns:
            vessel_count = df['mmsi'].nunique()
            summary_parts.append(f"from {vessel_count} vessel(s)")
        
        # Time range
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            start_time = df['timestamp'].min()
            end_time = df['timestamp'].max()
            summary_parts.append(f"between {start_time} and {end_time}")
        
        # Speed stats
        if 'sog' in df.columns:
            avg_speed = df['sog'].mean()
            max_speed = df['sog'].max()
            summary_parts.append(f"Average speed: {avg_speed:.2f} knots, Max speed: {max_speed:.2f} knots")
        
        # Loitering-specific summary
        if 'dwell_time_hours' in df.columns:
            total_dwell = df['dwell_time_hours'].sum()
            avg_dwell = df['dwell_time_hours'].mean()
            summary_parts.append(f"Total dwell time: {total_dwell:.2f} hours, Average: {avg_dwell:.2f} hours")
        
        summary_text = ". ".join(summary_parts) + "."
        
        return {
            "format": "summary",
            "data": summary_text,
            "count": len(df),
            "message": summary_text
        }
