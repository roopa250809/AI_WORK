"""Utility functions for data processing and formatting."""

from datetime import datetime, timedelta
from typing import Any, Optional
import pandas as pd
import numpy as np


def safe_parse_date(date_str: Any, default: Optional[datetime] = None) -> Optional[datetime]:
    """
    Safely parse various date formats.
    
    Args:
        date_str: Date value to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed datetime or default
    """
    if pd.isna(date_str):
        return default
    
    if isinstance(date_str, datetime):
        return date_str
    
    if isinstance(date_str, pd.Timestamp):
        return date_str.to_pydatetime()
    
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%m/%d/%Y",
        "%m/%d/%Y %H:%M:%S",
    ]
    
    date_str = str(date_str).strip()
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    try:
        return pd.to_datetime(date_str).to_pydatetime()
    except Exception:
        return default


def round_safe(value: Any, decimals: int = 2) -> float:
    """
    Safely round values, handling NaN and None.
    
    Args:
        value: Value to round
        decimals: Number of decimal places
        
    Returns:
        Rounded float or 0.0 if invalid
    """
    if pd.isna(value) or value is None:
        return 0.0
    try:
        return float(round(float(value), decimals))
    except (ValueError, TypeError):
        return 0.0


def format_duration(minutes: float) -> str:
    """
    Format minutes as human-readable duration.
    
    Args:
        minutes: Duration in minutes
        
    Returns:
        Formatted string (e.g., "7h 30m")
    """
    if pd.isna(minutes) or minutes == 0:
        return "—"
    
    minutes = round_safe(minutes)
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"


def format_percentage(value: float) -> str:
    """Format value as percentage string."""
    if pd.isna(value):
        return "—"
    return f"{round_safe(value, 1)}%"


def date_range_to_dateindex(dates: list) -> pd.DatetimeIndex:
    """Convert list of dates to DatetimeIndex."""
    return pd.to_datetime(dates)


def get_date_range_label(start_date: datetime, end_date: datetime) -> str:
    """Generate readable date range label."""
    if (end_date - start_date).days == 0:
        return start_date.strftime("%b %d, %Y")
    return f"{start_date.strftime('%b %d')} – {end_date.strftime('%b %d, %Y')}"
