"""Workout metrics computation from WHOOP data."""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from src.utils import round_safe


class WorkoutMetrics:
    """Calculate comprehensive workout metrics from WHOOP data."""

    # ─────────────────────────────────────────────
    # KPI / Summary
    # ─────────────────────────────────────────────

    @staticmethod
    def kpi_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Compute top-level KPI cards.

        Returns:
            Dict with total_workouts, total_duration_hrs, total_calories,
            avg_duration_min, avg_heart_rate, avg_strain
        """
        if df.empty:
            return {}

        total_workouts = len(df)
        total_duration_hrs = round_safe(df['duration_min'].sum() / 60, 1) if 'duration_min' in df.columns else 0.0
        total_calories = round_safe(df['calories_burned'].sum(), 0) if 'calories_burned' in df.columns else 0.0
        avg_duration = round_safe(df['duration_min'].mean(), 1) if 'duration_min' in df.columns else 0.0
        avg_hr = round_safe(df['avg_heart_rate'].mean(), 1) if 'avg_heart_rate' in df.columns else 0.0
        avg_strain = round_safe(df['workout_intensity'].mean(), 1) if 'workout_intensity' in df.columns else 0.0

        return {
            'total_workouts': total_workouts,
            'total_duration_hrs': total_duration_hrs,
            'total_calories': total_calories,
            'avg_duration_min': avg_duration,
            'avg_heart_rate': avg_hr,
            'avg_strain': avg_strain,
        }

    # ─────────────────────────────────────────────
    # Personal Records
    # ─────────────────────────────────────────────

    @staticmethod
    def personal_records(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Compute personal records (longest, highest calorie, highest strain).

        Returns:
            Dict with record rows and values
        """
        if df.empty:
            return {}

        records: Dict[str, Any] = {}

        if 'duration_min' in df.columns:
            idx = df['duration_min'].idxmax()
            row = df.loc[idx]
            records['longest_workout'] = {
                'value': round_safe(row['duration_min'], 1),
                'date': row['date'].strftime('%b %d, %Y'),
                'activity': row.get('activity_type', 'Unknown'),
            }

        if 'calories_burned' in df.columns:
            idx = df['calories_burned'].idxmax()
            row = df.loc[idx]
            records['highest_calorie'] = {
                'value': round_safe(row['calories_burned'], 0),
                'date': row['date'].strftime('%b %d, %Y'),
                'activity': row.get('activity_type', 'Unknown'),
            }

        if 'workout_intensity' in df.columns:
            idx = df['workout_intensity'].idxmax()
            row = df.loc[idx]
            records['highest_strain'] = {
                'value': round_safe(row['workout_intensity'], 1),
                'date': row['date'].strftime('%b %d, %Y'),
                'activity': row.get('activity_type', 'Unknown'),
            }

        return records

    # ─────────────────────────────────────────────
    # Weekly & Monthly Aggregations
    # ─────────────────────────────────────────────

    @staticmethod
    def weekly_summary(df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate workouts by ISO week.

        Returns:
            DataFrame with week, workout_count, total_duration_min,
            total_calories, avg_strain
        """
        if df.empty:
            return pd.DataFrame()

        agg: Dict[str, Any] = {'date': 'count'}
        if 'duration_min' in df.columns:
            agg['duration_min'] = 'sum'
        if 'calories_burned' in df.columns:
            agg['calories_burned'] = 'sum'
        if 'workout_intensity' in df.columns:
            agg['workout_intensity'] = 'mean'

        weekly = df.groupby('week').agg(agg).reset_index()
        weekly = weekly.rename(columns={'date': 'workout_count'})
        weekly['week'] = pd.to_datetime(weekly['week'])
        return weekly.sort_values('week')

    @staticmethod
    def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate workouts by calendar month.

        Returns:
            DataFrame with month, workout_count, total_duration_min,
            total_calories, avg_strain
        """
        if df.empty:
            return pd.DataFrame()

        agg: Dict[str, Any] = {'date': 'count'}
        if 'duration_min' in df.columns:
            agg['duration_min'] = 'sum'
        if 'calories_burned' in df.columns:
            agg['calories_burned'] = 'sum'
        if 'workout_intensity' in df.columns:
            agg['workout_intensity'] = 'mean'

        monthly = df.groupby('month').agg(agg).reset_index()
        monthly = monthly.rename(columns={'date': 'workout_count'})
        monthly['month'] = pd.to_datetime(monthly['month'])
        return monthly.sort_values('month')

    # ─────────────────────────────────────────────
    # Training Load
    # ─────────────────────────────────────────────

    @staticmethod
    def avg_weekly_training_load(df: pd.DataFrame) -> float:
        """Average total strain per week."""
        if df.empty or 'workout_intensity' not in df.columns:
            return 0.0
        weekly = df.groupby('week')['workout_intensity'].sum()
        return round_safe(weekly.mean(), 1)

    @staticmethod
    def avg_monthly_training_load(df: pd.DataFrame) -> float:
        """Average total strain per month."""
        if df.empty or 'workout_intensity' not in df.columns:
            return 0.0
        monthly = df.groupby('month')['workout_intensity'].sum()
        return round_safe(monthly.mean(), 1)

    # ─────────────────────────────────────────────
    # Activity Analysis
    # ─────────────────────────────────────────────

    @staticmethod
    def activity_distribution(df: pd.DataFrame) -> pd.DataFrame:
        """Count of workouts per activity type."""
        if df.empty or 'activity_type' not in df.columns:
            return pd.DataFrame()
        counts = df['activity_type'].value_counts().reset_index()
        counts.columns = ['activity_type', 'count']
        return counts

    @staticmethod
    def avg_duration_by_activity(df: pd.DataFrame) -> pd.DataFrame:
        """Average duration (min) per activity type."""
        if df.empty or 'activity_type' not in df.columns or 'duration_min' not in df.columns:
            return pd.DataFrame()
        result = df.groupby('activity_type')['duration_min'].mean().reset_index()
        result.columns = ['activity_type', 'avg_duration_min']
        return result.sort_values('avg_duration_min', ascending=False)

    @staticmethod
    def total_calories_by_activity(df: pd.DataFrame) -> pd.DataFrame:
        """Total calories burned per activity type."""
        if df.empty or 'activity_type' not in df.columns or 'calories_burned' not in df.columns:
            return pd.DataFrame()
        result = df.groupby('activity_type')['calories_burned'].sum().reset_index()
        result.columns = ['activity_type', 'total_calories']
        return result.sort_values('total_calories', ascending=False)

    # ─────────────────────────────────────────────
    # Insights Panel
    # ─────────────────────────────────────────────

    @staticmethod
    def generate_insights(df: pd.DataFrame) -> List[str]:
        """
        Auto-generate textual insights from workout data.

        Returns:
            List of insight strings
        """
        if df.empty:
            return ["No data available for insights."]

        insights: List[str] = []

        # Most active day of week
        if 'day_of_week' in df.columns:
            day_counts = df['day_of_week'].value_counts()
            most_active_day = day_counts.idxmax()
            insights.append(
                f"📅 **Most active day:** {most_active_day} "
                f"({day_counts.max()} workouts)"
            )

        # Average workouts per week
        if 'week' in df.columns:
            weeks = df['week'].nunique()
            if weeks > 0:
                avg_per_week = round_safe(len(df) / weeks, 1)
                insights.append(f"🔁 **Average workouts per week:** {avg_per_week}")

        # Best calorie-burning activity
        if 'activity_type' in df.columns and 'calories_burned' in df.columns:
            cal_by_act = df.groupby('activity_type')['calories_burned'].mean()
            best_act = cal_by_act.idxmax()
            insights.append(
                f"🔥 **Best calorie-burning activity:** {best_act} "
                f"(avg {round_safe(cal_by_act.max(), 0):.0f} cal/session)"
            )

        # Workout frequency trend (first half vs second half)
        if len(df) >= 10 and 'week' in df.columns:
            weeks_sorted = sorted(df['week'].unique())
            mid = len(weeks_sorted) // 2
            first_half = df[df['week'].isin(weeks_sorted[:mid])]
            second_half = df[df['week'].isin(weeks_sorted[mid:])]
            first_rate = len(first_half) / max(1, len(weeks_sorted[:mid]))
            second_rate = len(second_half) / max(1, len(weeks_sorted[mid:]))
            if second_rate > first_rate * 1.1:
                insights.append("📈 **Workout frequency trend:** Increasing — great consistency!")
            elif second_rate < first_rate * 0.9:
                insights.append("📉 **Workout frequency trend:** Decreasing — consider ramping back up.")
            else:
                insights.append("➡️ **Workout frequency trend:** Stable — maintaining consistency.")

        # Cardiovascular fitness trend (avg HR over time)
        if 'avg_heart_rate' in df.columns and len(df) >= 10:
            df_sorted = df.sort_values('date')
            first_hr = df_sorted.head(len(df_sorted) // 2)['avg_heart_rate'].mean()
            last_hr = df_sorted.tail(len(df_sorted) // 2)['avg_heart_rate'].mean()
            if last_hr < first_hr - 2:
                insights.append(
                    "❤️ **Cardio fitness trend:** Improving — average HR is decreasing over time, "
                    "indicating better cardiovascular efficiency."
                )
            elif last_hr > first_hr + 2:
                insights.append(
                    "❤️ **Cardio fitness trend:** Declining — average HR is increasing. "
                    "Consider more aerobic base training."
                )
            else:
                insights.append("❤️ **Cardio fitness trend:** Stable cardiovascular performance.")

        return insights

    # ─────────────────────────────────────────────
    # Regression helper
    # ─────────────────────────────────────────────

    @staticmethod
    def linear_regression_line(
        x: pd.Series, y: pd.Series, n_points: int = 100
    ) -> tuple:
        """
        Compute a linear regression trend line.

        Returns:
            (x_line, y_line) arrays for plotting
        """
        mask = x.notna() & y.notna()
        x_clean = x[mask].values.astype(float)
        y_clean = y[mask].values.astype(float)

        if len(x_clean) < 2:
            return np.array([]), np.array([])

        coeffs = np.polyfit(x_clean, y_clean, 1)
        poly = np.poly1d(coeffs)
        x_line = np.linspace(x_clean.min(), x_clean.max(), n_points)
        y_line = poly(x_line)
        return x_line, y_line
