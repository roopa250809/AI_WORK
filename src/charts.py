"""
Chart generation for WHOOP Fitness Analytics Dashboard.

All charts use Plotly for interactivity and support dark/light themes.
"""

from typing import Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from src.metrics import WorkoutMetrics
from src.utils import round_safe

# ─────────────────────────────────────────────────────────────────────────────
# Colour palette (WHOOP-inspired dark theme)
# ─────────────────────────────────────────────────────────────────────────────
COLORS = {
    'primary': '#00D4FF',       # cyan
    'secondary': '#FF6B6B',     # coral
    'accent': '#FFD700',        # gold
    'green': '#2ECC71',
    'purple': '#9B59B6',
    'orange': '#F39C12',
    'pink': '#E91E8C',
    'teal': '#1ABC9C',
    'blue': '#3498DB',
    'red': '#E74C3C',
    'bg_dark': '#0E1117',
    'bg_card': '#1A1D23',
    'text': '#FAFAFA',
    'grid': '#2D3139',
}

# HR zone colours (zone 1 = easy blue → zone 5 = max red)
HR_ZONE_COLORS = ['#3498DB', '#2ECC71', '#F39C12', '#E67E22', '#E74C3C']

PLOTLY_TEMPLATE = 'plotly_dark'


def _base_layout(**kwargs) -> dict:
    """Return a base Plotly layout dict with dark theme defaults."""
    base = dict(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text'], family='Inter, sans-serif', size=12),
        margin=dict(l=50, r=20, t=50, b=50),
        height=400,
        hovermode='x unified',
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1,
        ),
    )
    base.update(kwargs)
    return base


def _empty_chart(message: str, height: int = 400) -> go.Figure:
    """Return a placeholder figure with a centred message."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref='paper', yref='paper',
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color=COLORS['text']),
    )
    fig.update_layout(
        **_base_layout(height=height),
        xaxis={'visible': False},
        yaxis={'visible': False},
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Workout Trends
# ─────────────────────────────────────────────────────────────────────────────

def chart_duration_by_day(df: pd.DataFrame) -> go.Figure:
    """
    Line chart: Workout Duration (min) by date.
    Each point is a single workout session.
    """
    if df.empty or 'duration_min' not in df.columns:
        return _empty_chart("No duration data available")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['duration_min'],
        mode='markers+lines',
        name='Duration (min)',
        marker=dict(size=6, color=COLORS['primary'], opacity=0.8),
        line=dict(color=COLORS['primary'], width=1.5),
        hovertemplate='<b>%{x|%b %d, %Y}</b><br>Duration: %{y:.0f} min<extra></extra>',
    ))

    # 7-day rolling average
    daily_avg = df.groupby(df['date'].dt.date)['duration_min'].sum().reset_index()
    daily_avg['date'] = pd.to_datetime(daily_avg['date'])
    daily_avg['rolling'] = daily_avg['duration_min'].rolling(7, min_periods=1).mean()

    fig.add_trace(go.Scatter(
        x=daily_avg['date'],
        y=daily_avg['rolling'],
        mode='lines',
        name='7-Day Avg',
        line=dict(color=COLORS['accent'], width=2.5, dash='dot'),
        hovertemplate='7-Day Avg: %{y:.0f} min<extra></extra>',
    ))

    fig.update_layout(
        **_base_layout(title='Workout Duration by Day'),
        xaxis_title='Date',
        yaxis_title='Duration (min)',
    )
    return fig


def chart_calories_over_time(df: pd.DataFrame) -> go.Figure:
    """
    Line chart: Calories Burned over time with trend line.
    """
    if df.empty or 'calories_burned' not in df.columns:
        return _empty_chart("No calorie data available")

    df_sorted = df.sort_values('date').dropna(subset=['calories_burned'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_sorted['date'],
        y=df_sorted['calories_burned'],
        mode='markers+lines',
        name='Calories',
        marker=dict(size=6, color=COLORS['orange'], opacity=0.8),
        line=dict(color=COLORS['orange'], width=1.5),
        hovertemplate='<b>%{x|%b %d}</b><br>Calories: %{y:.0f}<extra></extra>',
    ))

    # Trend line
    x_num = (df_sorted['date'] - df_sorted['date'].min()).dt.days.values.astype(float)
    y_vals = df_sorted['calories_burned'].values.astype(float)
    if len(x_num) >= 2:
        coeffs = np.polyfit(x_num, y_vals, 1)
        poly = np.poly1d(coeffs)
        x_line = np.linspace(x_num.min(), x_num.max(), 200)
        y_line = poly(x_line)
        date_line = df_sorted['date'].min() + pd.to_timedelta(x_line, unit='D')
        fig.add_trace(go.Scatter(
            x=date_line,
            y=y_line,
            mode='lines',
            name='Trend',
            line=dict(color=COLORS['red'], width=2, dash='dash'),
            hoverinfo='skip',
        ))

    fig.update_layout(
        **_base_layout(title='Calories Burned Over Time'),
        xaxis_title='Date',
        yaxis_title='Calories (kcal)',
    )
    return fig


def chart_strain_over_time(df: pd.DataFrame) -> go.Figure:
    """
    Line chart: Activity Strain over time, highlighting highest strain workouts.
    """
    if df.empty or 'workout_intensity' not in df.columns:
        return _empty_chart("No strain data available")

    df_sorted = df.sort_values('date').dropna(subset=['workout_intensity'])
    threshold = df_sorted['workout_intensity'].quantile(0.85)

    high_strain = df_sorted[df_sorted['workout_intensity'] >= threshold]
    normal = df_sorted[df_sorted['workout_intensity'] < threshold]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_sorted['date'],
        y=df_sorted['workout_intensity'],
        mode='lines',
        name='Strain',
        line=dict(color=COLORS['purple'], width=1.5),
        hovertemplate='<b>%{x|%b %d}</b><br>Strain: %{y:.1f}<extra></extra>',
    ))

    fig.add_trace(go.Scatter(
        x=high_strain['date'],
        y=high_strain['workout_intensity'],
        mode='markers',
        name='High Strain',
        marker=dict(size=10, color=COLORS['red'], symbol='star'),
        hovertemplate='<b>%{x|%b %d}</b><br>⭐ High Strain: %{y:.1f}<extra></extra>',
    ))

    fig.update_layout(
        **_base_layout(title='Activity Strain Over Time'),
        xaxis_title='Date',
        yaxis_title='Strain Score',
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Activity Analysis
# ─────────────────────────────────────────────────────────────────────────────

def chart_activity_distribution(df: pd.DataFrame) -> go.Figure:
    """Donut chart: Workout count by activity type."""
    dist = WorkoutMetrics.activity_distribution(df)
    if dist.empty:
        return _empty_chart("No activity data available")

    fig = go.Figure(data=[go.Pie(
        labels=dist['activity_type'],
        values=dist['count'],
        hole=0.45,
        marker=dict(colors=px.colors.qualitative.Bold),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Workouts: %{value}<br>%{percent}<extra></extra>',
    )])

    fig.update_layout(
        **_base_layout(title='Workout Distribution by Activity Type'),
        showlegend=True,
    )
    return fig


def chart_avg_duration_by_activity(df: pd.DataFrame) -> go.Figure:
    """Bar chart: Average duration per activity type."""
    data = WorkoutMetrics.avg_duration_by_activity(df)
    if data.empty:
        return _empty_chart("No duration data available")

    fig = go.Figure(go.Bar(
        x=data['activity_type'],
        y=data['avg_duration_min'],
        marker=dict(
            color=data['avg_duration_min'],
            colorscale='Viridis',
            showscale=False,
        ),
        hovertemplate='<b>%{x}</b><br>Avg Duration: %{y:.1f} min<extra></extra>',
    ))

    fig.update_layout(
        **_base_layout(title='Average Duration by Activity'),
        xaxis_title='Activity',
        yaxis_title='Avg Duration (min)',
        xaxis_tickangle=-30,
    )
    return fig


def chart_total_calories_by_activity(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart: Total calories burned per activity type."""
    data = WorkoutMetrics.total_calories_by_activity(df)
    if data.empty:
        return _empty_chart("No calorie data available")

    fig = go.Figure(go.Bar(
        y=data['activity_type'],
        x=data['total_calories'],
        orientation='h',
        marker=dict(
            color=data['total_calories'],
            colorscale='Plasma',
            showscale=False,
        ),
        hovertemplate='<b>%{y}</b><br>Total Calories: %{x:.0f}<extra></extra>',
    ))

    fig.update_layout(
        **_base_layout(title='Total Calories Burned by Activity', height=420),
        xaxis_title='Total Calories (kcal)',
        yaxis_title='',
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Heart Rate Analytics
# ─────────────────────────────────────────────────────────────────────────────

def chart_avg_hr_trend(df: pd.DataFrame) -> go.Figure:
    """Line chart: Average HR trend over time."""
    if df.empty or 'avg_heart_rate' not in df.columns:
        return _empty_chart("No heart rate data available")

    df_sorted = df.sort_values('date').dropna(subset=['avg_heart_rate'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_sorted['date'],
        y=df_sorted['avg_heart_rate'],
        mode='markers+lines',
        name='Avg HR',
        marker=dict(size=5, color=COLORS['pink']),
        line=dict(color=COLORS['pink'], width=1.5),
        hovertemplate='<b>%{x|%b %d}</b><br>Avg HR: %{y:.0f} bpm<extra></extra>',
    ))

    # Rolling 7-day average
    daily = df_sorted.groupby(df_sorted['date'].dt.date)['avg_heart_rate'].mean().reset_index()
    daily['date'] = pd.to_datetime(daily['date'])
    daily['rolling'] = daily['avg_heart_rate'].rolling(7, min_periods=1).mean()

    fig.add_trace(go.Scatter(
        x=daily['date'],
        y=daily['rolling'],
        mode='lines',
        name='7-Day Avg',
        line=dict(color=COLORS['accent'], width=2.5, dash='dot'),
        hoverinfo='skip',
    ))

    fig.update_layout(
        **_base_layout(title='Average Heart Rate Trend'),
        xaxis_title='Date',
        yaxis_title='Heart Rate (bpm)',
    )
    return fig


def chart_max_hr_trend(df: pd.DataFrame) -> go.Figure:
    """Line chart: Max HR trend over time."""
    if df.empty or 'max_heart_rate' not in df.columns:
        return _empty_chart("No max HR data available")

    df_sorted = df.sort_values('date').dropna(subset=['max_heart_rate'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_sorted['date'],
        y=df_sorted['max_heart_rate'],
        mode='markers+lines',
        name='Max HR',
        marker=dict(size=5, color=COLORS['red']),
        line=dict(color=COLORS['red'], width=1.5),
        hovertemplate='<b>%{x|%b %d}</b><br>Max HR: %{y:.0f} bpm<extra></extra>',
    ))

    fig.update_layout(
        **_base_layout(title='Max Heart Rate Trend'),
        xaxis_title='Date',
        yaxis_title='Max HR (bpm)',
    )
    return fig


def chart_hr_zone_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Stacked bar chart: HR Zone distribution per workout date.
    Zones: hr_zone1 … hr_zone5 (percentage columns).
    """
    zone_cols = ['hr_zone1', 'hr_zone2', 'hr_zone3', 'hr_zone4', 'hr_zone5']
    available = [c for c in zone_cols if c in df.columns]

    if not available or df.empty:
        return _empty_chart("No HR zone data available")

    df_sorted = df.sort_values('date').dropna(subset=available, how='all')

    zone_labels = ['Zone 1 (Recovery)', 'Zone 2 (Aerobic)', 'Zone 3 (Tempo)',
                   'Zone 4 (Threshold)', 'Zone 5 (Max)']

    fig = go.Figure()

    for i, col in enumerate(available):
        label = zone_labels[i] if i < len(zone_labels) else col
        fig.add_trace(go.Bar(
            x=df_sorted['date'],
            y=df_sorted[col],
            name=label,
            marker_color=HR_ZONE_COLORS[i],
            hovertemplate=f'<b>%{{x|%b %d}}</b><br>{label}: %{{y:.1f}}%<extra></extra>',
        ))

    fig.update_layout(
        **_base_layout(title='HR Zone Distribution per Workout', height=420),
        barmode='stack',
        xaxis_title='Date',
        yaxis_title='% of Workout Time',
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Performance Insights (Scatter Plots)
# ─────────────────────────────────────────────────────────────────────────────

def _scatter_with_regression(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    x_label: str,
    y_label: str,
    title: str,
    color_col: Optional[str] = None,
) -> go.Figure:
    """Generic scatter plot with optional regression line and colour coding."""
    mask = df[x_col].notna() & df[y_col].notna()
    plot_df = df[mask].copy()

    if plot_df.empty:
        return _empty_chart(f"Not enough data for {title}")

    # Colour by activity type if requested
    if color_col and color_col in plot_df.columns:
        activities = plot_df[color_col].unique()
        palette = px.colors.qualitative.Bold
        color_map = {act: palette[i % len(palette)] for i, act in enumerate(activities)}
        colors = plot_df[color_col].map(color_map)
    else:
        colors = COLORS['primary']

    fig = go.Figure()

    if color_col and color_col in plot_df.columns:
        for act in activities:
            sub = plot_df[plot_df[color_col] == act]
            fig.add_trace(go.Scatter(
                x=sub[x_col],
                y=sub[y_col],
                mode='markers',
                name=act,
                marker=dict(size=8, color=color_map[act], opacity=0.8),
                hovertemplate=(
                    f'<b>{act}</b><br>'
                    f'{x_label}: %{{x:.1f}}<br>'
                    f'{y_label}: %{{y:.1f}}<extra></extra>'
                ),
            ))
    else:
        fig.add_trace(go.Scatter(
            x=plot_df[x_col],
            y=plot_df[y_col],
            mode='markers',
            name='Workout',
            marker=dict(size=8, color=COLORS['primary'], opacity=0.8),
            hovertemplate=f'{x_label}: %{{x:.1f}}<br>{y_label}: %{{y:.1f}}<extra></extra>',
        ))

    # Regression line
    x_line, y_line = WorkoutMetrics.linear_regression_line(plot_df[x_col], plot_df[y_col])
    if len(x_line) > 0:
        fig.add_trace(go.Scatter(
            x=x_line,
            y=y_line,
            mode='lines',
            name='Trend',
            line=dict(color=COLORS['accent'], width=2, dash='dash'),
            hoverinfo='skip',
        ))

    fig.update_layout(
        **_base_layout(title=title),
        xaxis_title=x_label,
        yaxis_title=y_label,
    )
    return fig


def chart_duration_vs_calories(df: pd.DataFrame) -> go.Figure:
    """Scatter: Duration vs Calories Burned with regression line."""
    return _scatter_with_regression(
        df, 'duration_min', 'calories_burned',
        'Duration (min)', 'Calories Burned',
        'Duration vs Calories Burned',
        color_col='activity_type',
    )


def chart_strain_vs_calories(df: pd.DataFrame) -> go.Figure:
    """Scatter: Strain vs Calories Burned."""
    return _scatter_with_regression(
        df, 'workout_intensity', 'calories_burned',
        'Activity Strain', 'Calories Burned',
        'Strain vs Calories Burned',
        color_col='activity_type',
    )


def chart_strain_vs_avg_hr(df: pd.DataFrame) -> go.Figure:
    """Scatter: Strain vs Average Heart Rate."""
    return _scatter_with_regression(
        df, 'workout_intensity', 'avg_heart_rate',
        'Activity Strain', 'Avg Heart Rate (bpm)',
        'Strain vs Average Heart Rate',
        color_col='activity_type',
    )


# ─────────────────────────────────────────────────────────────────────────────
# Weekly & Monthly Analysis
# ─────────────────────────────────────────────────────────────────────────────

def chart_weekly_workout_count(df: pd.DataFrame) -> go.Figure:
    """Bar chart: Number of workouts per week."""
    weekly = WorkoutMetrics.weekly_summary(df)
    if weekly.empty:
        return _empty_chart("No weekly data available")

    fig = go.Figure(go.Bar(
        x=weekly['week'],
        y=weekly['workout_count'],
        marker=dict(color=COLORS['teal']),
        hovertemplate='<b>Week of %{x|%b %d}</b><br>Workouts: %{y}<extra></extra>',
    ))

    fig.update_layout(
        **_base_layout(title='Weekly Workout Count'),
        xaxis_title='Week',
        yaxis_title='Workouts',
    )
    return fig


def chart_weekly_duration(df: pd.DataFrame) -> go.Figure:
    """Bar chart: Total workout duration per week."""
    weekly = WorkoutMetrics.weekly_summary(df)
    if weekly.empty or 'duration_min' not in weekly.columns:
        return _empty_chart("No weekly duration data available")

    fig = go.Figure(go.Bar(
        x=weekly['week'],
        y=weekly['duration_min'],
        marker=dict(color=COLORS['blue']),
        hovertemplate='<b>Week of %{x|%b %d}</b><br>Duration: %{y:.0f} min<extra></extra>',
    ))

    fig.update_layout(
        **_base_layout(title='Weekly Total Duration'),
        xaxis_title='Week',
        yaxis_title='Total Duration (min)',
    )
    return fig


def chart_weekly_calories(df: pd.DataFrame) -> go.Figure:
    """Bar chart: Total calories burned per week."""
    weekly = WorkoutMetrics.weekly_summary(df)
    if weekly.empty or 'calories_burned' not in weekly.columns:
        return _empty_chart("No weekly calorie data available")

    fig = go.Figure(go.Bar(
        x=weekly['week'],
        y=weekly['calories_burned'],
        marker=dict(color=COLORS['orange']),
        hovertemplate='<b>Week of %{x|%b %d}</b><br>Calories: %{y:.0f}<extra></extra>',
    ))

    fig.update_layout(
        **_base_layout(title='Weekly Calories Burned'),
        xaxis_title='Week',
        yaxis_title='Total Calories (kcal)',
    )
    return fig


def chart_monthly_summary(df: pd.DataFrame) -> go.Figure:
    """
    Grouped bar chart: Monthly workout count, duration, and calories.
    Uses a secondary y-axis for calories.
    """
    monthly = WorkoutMetrics.monthly_summary(df)
    if monthly.empty:
        return _empty_chart("No monthly data available")

    month_labels = monthly['month'].dt.strftime('%b %Y')

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=month_labels,
        y=monthly['workout_count'],
        name='Workouts',
        marker_color=COLORS['teal'],
        hovertemplate='<b>%{x}</b><br>Workouts: %{y}<extra></extra>',
    ), secondary_y=False)

    if 'duration_min' in monthly.columns:
        fig.add_trace(go.Bar(
            x=month_labels,
            y=monthly['duration_min'],
            name='Duration (min)',
            marker_color=COLORS['blue'],
            hovertemplate='<b>%{x}</b><br>Duration: %{y:.0f} min<extra></extra>',
        ), secondary_y=False)

    if 'calories_burned' in monthly.columns:
        fig.add_trace(go.Scatter(
            x=month_labels,
            y=monthly['calories_burned'],
            mode='lines+markers',
            name='Calories',
            line=dict(color=COLORS['orange'], width=2),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>Calories: %{y:.0f}<extra></extra>',
        ), secondary_y=True)

    fig.update_layout(
        **_base_layout(title='Monthly Workout Summary', height=420),
        barmode='group',
        xaxis_title='Month',
    )
    fig.update_yaxes(title_text='Count / Duration', secondary_y=False)
    fig.update_yaxes(title_text='Calories (kcal)', secondary_y=True)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Backward-compatible wrappers (used by old app.py)
# ─────────────────────────────────────────────────────────────────────────────

class HealthCharts:
    """Thin wrapper kept for backward compatibility."""

    @staticmethod
    def sleep_duration_trend(sleep_df: pd.DataFrame, rolling_window: int = 7) -> go.Figure:
        return _empty_chart("Sleep data not used in this dashboard")

    @staticmethod
    def workout_intensity_trend(workout_df: pd.DataFrame) -> go.Figure:
        return chart_strain_over_time(workout_df)

    @staticmethod
    def sleep_quality_distribution(sleep_df: pd.DataFrame) -> go.Figure:
        return _empty_chart("Sleep data not used in this dashboard")

    @staticmethod
    def sleep_composition(sleep_df: pd.DataFrame) -> go.Figure:
        return _empty_chart("Sleep data not used in this dashboard")

    @staticmethod
    def activity_type_breakdown(workout_df: pd.DataFrame) -> go.Figure:
        return chart_activity_distribution(workout_df)

    @staticmethod
    def sleep_workout_correlation_chart(sleep_df: pd.DataFrame,
                                        workout_df: pd.DataFrame) -> go.Figure:
        return chart_duration_vs_calories(workout_df)
