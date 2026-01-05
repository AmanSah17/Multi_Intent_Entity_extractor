"""
Data Validation Utilities
==========================
Helper functions for validating and parsing data.
"""

import re
from datetime import datetime, timedelta
from typing import Tuple, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


def validate_mmsi(mmsi: str) -> bool:
    """
    Validate MMSI format.
    
    MMSI should be a 9-digit number.
    
    Args:
        mmsi: MMSI string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not mmsi:
        return False
    
    # Remove any whitespace
    mmsi = mmsi.strip()
    
    # Check if it's a 9-digit number
    return bool(re.match(r'^\d{9}$', mmsi))


def validate_time_range(start: Optional[str], end: Optional[str]) -> bool:
    """
    Validate time range.
    
    Args:
        start: Start datetime string (ISO format)
        end: End datetime string (ISO format)
        
    Returns:
        True if valid, False otherwise
    """
    if not start or not end:
        return False
    
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        return start_dt < end_dt
    except (ValueError, TypeError):
        return False


def parse_relative_time(relative_expr: str) -> Tuple[datetime, datetime]:
    """
    Parse relative time expressions to absolute datetime range.
    
    Supported expressions:
    - last_Xh: Last X hours
    - last_Xd: Last X days
    - last_week: Last 7 days
    - last_weekend: Last weekend
    - today: Today
    - yesterday: Yesterday
    
    Args:
        relative_expr: Relative time expression
        
    Returns:
        Tuple of (start_datetime, end_datetime)
        
    Raises:
        ValueError: If expression is not recognized
    """
    now = datetime.now()
    relative_expr = relative_expr.lower().strip()
    
    # Last X hours
    if match := re.match(r'last_(\d+)h', relative_expr):
        hours = int(match.group(1))
        start = now - timedelta(hours=hours)
        return start, now
    
    # Last X days
    if match := re.match(r'last_(\d+)d', relative_expr):
        days = int(match.group(1))
        start = now - timedelta(days=days)
        return start, now
    
    # Last week
    if relative_expr == 'last_week':
        start = now - timedelta(days=7)
        return start, now
    
    # Last weekend (Saturday and Sunday)
    if relative_expr == 'last_weekend':
        # Find last Sunday
        days_since_sunday = (now.weekday() + 1) % 7
        if days_since_sunday == 0:
            days_since_sunday = 7
        last_sunday = now - timedelta(days=days_since_sunday)
        last_saturday = last_sunday - timedelta(days=1)
        
        start = last_saturday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = last_sunday.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start, end
    
    # Today
    if relative_expr == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, now
    
    # Yesterday
    if relative_expr == 'yesterday':
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start, end
    
    # Default: last 24 hours
    logger.warning(f"Unrecognized relative time expression: {relative_expr}. Using last 24 hours.")
    start = now - timedelta(days=1)
    return start, now


def format_datetime_for_query(dt: datetime) -> str:
    """
    Format datetime for SQL query.
    
    Args:
        dt: Datetime object
        
    Returns:
        ISO format datetime string
    """
    return dt.isoformat()
