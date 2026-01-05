"""
Loitering Service
=================
Detects loitering behavior in vessel trajectories.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from config.schemas import SpatialConstraint
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class LoiteringService:
    """
    Loitering detection service.
    
    This class implements loitering detection based on:
    1. Speed threshold (vessels moving slowly)
    2. Dwell time (vessels staying in area for extended period)
    3. Spatial constraints (coastal distance, polygons)
    """
    
    def __init__(self):
        """Initialize the loitering service."""
        self.speed_threshold = settings.loitering_speed_threshold_knots
        self.dwell_time_hours = settings.loitering_dwell_time_hours
    
    def detect_loitering(
        self,
        df: pd.DataFrame,
        speed_threshold: Optional[float] = None,
        dwell_time_hours: Optional[float] = None,
        spatial_constraint: Optional[SpatialConstraint] = None
    ) -> pd.DataFrame:
        """
        Detect loitering events in trajectory data.
        
        Algorithm:
        1. Filter by speed threshold
        2. Group consecutive low-speed points
        3. Calculate dwell time for each group
        4. Apply spatial filters
        5. Flag loitering events
        
        Args:
            df: Trajectory DataFrame
            speed_threshold: Speed threshold in knots (default from settings)
            dwell_time_hours: Minimum dwell time in hours (default from settings)
            spatial_constraint: Optional spatial constraint
            
        Returns:
            DataFrame with loitering events
            
        Example:
            >>> service = LoiteringService()
            >>> loitering_df = service.detect_loitering(trajectory_df)
        """
        if df.empty:
            logger.warning("Empty DataFrame provided")
            return pd.DataFrame()
        
        speed_threshold = speed_threshold or self.speed_threshold
        dwell_time_hours = dwell_time_hours or self.dwell_time_hours
        
        logger.info(f"Detecting loitering (speed < {speed_threshold} knots, dwell > {dwell_time_hours} hours)")
        
        try:
            # Step 1: Filter by speed threshold
            df_slow = df[df['sog'] < speed_threshold].copy()
            
            if df_slow.empty:
                logger.info("No slow-moving vessels found")
                return pd.DataFrame()
            
            # Step 2: Group by vessel
            loitering_events = []
            
            for mmsi, group in df_slow.groupby('mmsi'):
                # Sort by timestamp
                group = group.sort_values('timestamp')
                
                # Convert timestamp to datetime
                group['timestamp'] = pd.to_datetime(group['timestamp'])
                
                # Step 3: Find consecutive low-speed periods
                # Add a group ID for consecutive points
                group['time_diff'] = group['timestamp'].diff().dt.total_seconds() / 3600  # hours
                group['new_event'] = (group['time_diff'] > 1.0) | group['time_diff'].isna()  # Gap > 1 hour = new event
                group['event_id'] = group['new_event'].cumsum()
                
                # Step 4: Calculate dwell time for each event
                for event_id, event_group in group.groupby('event_id'):
                    if len(event_group) < 2:
                        continue
                    
                    start_time = event_group['timestamp'].min()
                    end_time = event_group['timestamp'].max()
                    dwell_time = (end_time - start_time).total_seconds() / 3600
                    
                    if dwell_time >= dwell_time_hours:
                        # Calculate center position
                        center_lat = event_group['latitude'].mean()
                        center_lon = event_group['longitude'].mean()
                        
                        loitering_events.append({
                            'mmsi': mmsi,
                            'start_time': start_time,
                            'end_time': end_time,
                            'dwell_time_hours': dwell_time,
                            'center_latitude': center_lat,
                            'center_longitude': center_lon,
                            'num_points': len(event_group),
                            'avg_speed': event_group['sog'].mean()
                        })
            
            if not loitering_events:
                logger.info("No loitering events detected")
                return pd.DataFrame()
            
            loitering_df = pd.DataFrame(loitering_events)
            
            # Step 5: Apply spatial filters (if provided)
            if spatial_constraint and spatial_constraint.type != "none":
                loitering_df = self._apply_spatial_filter(loitering_df, spatial_constraint)
            
            logger.info(f"Detected {len(loitering_df)} loitering events")
            return loitering_df
            
        except Exception as e:
            logger.error(f"Loitering detection failed: {e}")
            raise
    
    def _apply_spatial_filter(
        self,
        df: pd.DataFrame,
        spatial_constraint: SpatialConstraint
    ) -> pd.DataFrame:
        """
        Apply spatial filtering to loitering events.
        
        Args:
            df: Loitering events DataFrame
            spatial_constraint: Spatial constraint to apply
            
        Returns:
            Filtered DataFrame
        """
        if spatial_constraint.type == "coastal_distance":
            # TODO: Implement coastal distance filtering
            # This requires coastline data and geospatial calculations
            logger.warning("Coastal distance filtering not yet implemented")
            return df
        
        elif spatial_constraint.type == "polygon":
            # TODO: Implement polygon filtering
            # This requires polygon data (EEZ, TTW, etc.)
            logger.warning("Polygon filtering not yet implemented")
            return df
        
        return df
