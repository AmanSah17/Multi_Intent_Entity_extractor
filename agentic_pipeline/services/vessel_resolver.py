"""
Vessel Resolver
===============
Resolves vessel identifiers (IMO/MMSI/name) to internal IDs.
"""

from typing import List
from config.schemas import VesselIdentifier
from data.duckdb_manager import DuckDBManager
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class VesselResolver:
    """
    Resolves vessel identifiers to MMSIs.
    
    This class maps vessel identifiers (IMO, MMSI, name) to the actual
    MMSIs present in the dataset.
    """
    
    def __init__(self, db_manager: DuckDBManager):
        """
        Initialize the vessel resolver.
        
        Args:
            db_manager: DuckDB manager instance
        """
        self.db = db_manager
    
    def resolve(self, vessels: List[VesselIdentifier]) -> List[str]:
        """
        Resolve vessel identifiers to MMSIs.
        
        Args:
            vessels: List of vessel identifiers
            
        Returns:
            List of resolved MMSIs
            
        Example:
            >>> resolver = VesselResolver(db)
            >>> vessels = [VesselIdentifier(mmsi="123456789")]
            >>> mmsis = resolver.resolve(vessels)
            >>> print(mmsis)
            ['123456789']
        """
        resolved_mmsis = []
        
        for vessel in vessels:
            # If MMSI is provided, use it directly
            if vessel.mmsi:
                # Verify it exists in the dataset
                if self._verify_mmsi_exists(vessel.mmsi):
                    resolved_mmsis.append(vessel.mmsi)
                    logger.info(f"Resolved MMSI: {vessel.mmsi}")
                else:
                    logger.warning(f"MMSI not found in dataset: {vessel.mmsi}")
            
            # TODO: Add IMO and name resolution when vessel metadata is available
            # For now, we only have MMSI in the dataset
            elif vessel.imo:
                logger.warning(f"IMO resolution not yet implemented: {vessel.imo}")
            elif vessel.name:
                logger.warning(f"Name resolution not yet implemented: {vessel.name}")
        
        return resolved_mmsis
    
    def _verify_mmsi_exists(self, mmsi: str) -> bool:
        """
        Verify that an MMSI exists in the dataset.
        
        Args:
            mmsi: MMSI to verify
            
        Returns:
            True if exists, False otherwise
        """
        try:
            query = f"SELECT COUNT(*) as count FROM ais WHERE {settings.col_mmsi} = '{mmsi}' LIMIT 1"
            df = self.db.execute_query(query)
            return int(df['count'].iloc[0]) > 0
        except Exception as e:
            logger.error(f"Failed to verify MMSI: {e}")
            return False
    
    def get_all_mmsis(self) -> List[str]:
        """
        Get all unique MMSIs in the dataset.
        
        Returns:
            List of all MMSIs
        """
        return self.db.get_unique_vessels()
