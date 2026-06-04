"""Data loading and validation for WHOOP CSV exports."""

from typing import Optional, Tuple
import pandas as pd
import numpy as np
from src.utils import safe_parse_date


class WHOOPDataLoader:
    """Load and validate WHOOP CSV files (workout-only focus)."""

    # Column mapping for WHOOP workout exports
    WORKOUT_COLUMNS = {
        'date': ['Workout start time', 'date', 'workout_date', 'Date', 'Workout Date'],
        'end_time': ['Workout end time', 'end_time', 'workout_end', 'End Time', 'Workout End'],
        'duration_min': ['Duration (min)', 'duration_minutes', 'duration_min', 'Duration (Minutes)', 'Duration'],
        'activity_type': ['Activity name', 'activity', 'activity_type', 'Activity Type', 'Sport'],
        'workout_intensity': ['Activity Strain', 'intensity', 'strain', 'Intensity', 'Strain Score'],
        'calories_burned': ['Energy burned (cal)', 'calories', 'calories_burned', 'Calories Burned'],
        'avg_heart_rate': ['Average HR (bpm)', 'avg_hr', 'average_heart_rate', 'Avg HR', 'Average Heart Rate'],
        'max_heart_rate': ['Max HR (bpm)', 'max_hr', 'maximum_heart_rate', 'Max HR', 'Maximum Heart Rate'],
        'hr_zone1': ['HR Zone 1 %', 'hr_zone1', 'zone1_pct', 'Zone 1 %'],
        'hr_zone2': ['HR Zone 2 %', 'hr_zone2', 'zone2_pct', 'Zone 2 %'],
        'hr_zone3': ['HR Zone 3 %', 'hr_zone3', 'zone3_pct', 'Zone 3 %'],
        'hr_zone4': ['HR Zone 4 %', 'hr_zone4', 'zone4_pct', 'Zone 4 %'],
        'hr_zone5': ['HR Zone 5 %', 'hr_zone5', 'zone5_pct', 'Zone 5 %'],
    }

    @staticmethod
    def find_column(df: pd.DataFrame, column_candidates: list) -> Optional[str]:
        """
        Find matching column from candidates (case-insensitive).

        Args:
            df: DataFrame to search
            column_candidates: List of possible column names

        Returns:
            Matched column name or None
        """
        df_cols_lower = {col.lower(): col for col in df.columns}
        for candidate in column_candidates:
            if candidate.lower() in df_cols_lower:
                return df_cols_lower[candidate.lower()]
        return None

    @classmethod
    def load_workout_data(cls, file) -> Tuple[Optional[pd.DataFrame], list]:
        """
        Load workout data from a CSV file or file-like object.

        Args:
            file: File upload object or path string

        Returns:
            Tuple of (DataFrame, list of errors/warnings)
        """
        messages = []

        try:
            df = pd.read_csv(file)
        except Exception as e:
            return None, [f"Failed to read CSV file: {str(e)}"]

        if df.empty:
            return None, ["Workout data file is empty"]

        # Find and rename date column
        date_col = cls.find_column(df, cls.WORKOUT_COLUMNS['date'])
        if not date_col:
            return None, ["No date column found in workout data"]

        df = df.rename(columns={date_col: 'date'})
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

        if df['date'].isna().all():
            return None, ["All dates are invalid"]

        invalid_dates = df['date'].isna().sum()
        if invalid_dates > 0:
            messages.append(f"Removed {invalid_dates} rows with invalid dates")
            df = df.dropna(subset=['date'])

        # Map all optional columns
        optional_mappings = {k: v for k, v in cls.WORKOUT_COLUMNS.items() if k != 'date'}

        for standard_name, candidates in optional_mappings.items():
            found_col = cls.find_column(df, candidates)
            if found_col and found_col != standard_name:
                df = df.rename(columns={found_col: standard_name})

        # Convert numeric columns
        numeric_cols = [
            'duration_min', 'workout_intensity', 'calories_burned',
            'avg_heart_rate', 'max_heart_rate',
            'hr_zone1', 'hr_zone2', 'hr_zone3', 'hr_zone4', 'hr_zone5',
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Ensure activity_type is string
        if 'activity_type' in df.columns:
            df['activity_type'] = df['activity_type'].astype(str).str.strip().fillna('Unknown')

        # Add derived time columns
        df['workout_date'] = df['date'].dt.date
        df['day_of_week'] = df['date'].dt.day_name()
        df['week'] = df['date'].dt.to_period('W').dt.start_time
        df['month'] = df['date'].dt.to_period('M').dt.start_time
        df['year_week'] = df['date'].dt.strftime('%Y-W%U')

        # Sort by date ascending
        df = df.sort_values('date').reset_index(drop=True)

        return df, messages

    @classmethod
    def load_sleep_data(cls, file) -> Tuple[Optional[pd.DataFrame], list]:
        """
        Load sleep data from CSV file (kept for backward compatibility).

        Args:
            file: File upload object

        Returns:
            Tuple of (DataFrame, list of errors/warnings)
        """
        messages = []
        try:
            df = pd.read_csv(file)
        except Exception as e:
            return None, [f"Failed to read CSV file: {str(e)}"]

        if df.empty:
            return None, ["Sleep data file is empty"]

        # Try to find a date column
        date_candidates = ['Sleep onset', 'date', 'Date', 'Cycle start time']
        date_col = None
        df_cols_lower = {col.lower(): col for col in df.columns}
        for c in date_candidates:
            if c.lower() in df_cols_lower:
                date_col = df_cols_lower[c.lower()]
                break

        if not date_col:
            return None, ["No date column found in sleep data"]

        df = df.rename(columns={date_col: 'date'})
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        df = df.sort_values('date').reset_index(drop=True)

        return df, messages


def validate_data(
    sleep_df: Optional[pd.DataFrame],
    workout_df: Optional[pd.DataFrame],
) -> Tuple[bool, list]:
    """
    Validate loaded data.  Sleep data is optional for this dashboard.

    Args:
        sleep_df: Sleep DataFrame (may be None)
        workout_df: Workout DataFrame

    Returns:
        Tuple of (is_valid, list of errors)
    """
    errors = []

    if workout_df is None or workout_df.empty:
        errors.append("No valid workout data available")

    if workout_df is not None and 'date' not in workout_df.columns:
        errors.append("Workout data missing date column")

    return len(errors) == 0, errors
