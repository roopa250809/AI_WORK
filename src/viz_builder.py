"""
Visualization builder for the universal CSV analysis dashboard.

All charts use Plotly for interactivity (zoom, hover, pan).
Supports dark and light themes via the `template` parameter.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

PLOTLY_TEMPLATE = "plotly_dark"

QUALITATIVE_PALETTE = px.colors.qualitative.Bold

_LAYOUT_DEFAULTS = dict(
    template=PLOTLY_TEMPLATE,
    paper_bgcolor="#1A1D23",
    plot_bgcolor="#1A1D23",
    font=dict(color="#FAFAFA", family="Inter, Segoe UI, sans-serif", size=12),
    margin=dict(l=55, r=20, t=55, b=55),
    height=420,
    hovermode="closest",
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(255,255,255,0.1)",
        borderwidth=1,
    ),
)


def _layout(**overrides) -> dict:
    base = dict(_LAYOUT_DEFAULTS)
    base.update(overrides)
    return base


def _empty(message: str = "Not enough data to render this chart.") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=15, color="#9CA3AF"),
    )
    fig.update_layout(
        **_layout(),
        xaxis={"visible": False},
        yaxis={"visible": False},
    )
    return fig


def _agg_series(df: pd.DataFrame, x_col: str, y_col: str, agg: str) -> pd.DataFrame:
    """Group df by x_col and aggregate y_col with the chosen function."""
    agg_map = {"sum": "sum", "mean": "mean", "count": "count"}
    func = agg_map.get(agg, "sum")
    grouped = df.groupby(x_col)[y_col].agg(func).reset_index()
    grouped.columns = [x_col, y_col]
    return grouped


# ─────────────────────────────────────────────────────────────────────────────
# Bar chart
# ─────────────────────────────────────────────────────────────────────────────

def bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    agg: str = "sum",
    color_col: Optional[str] = None,
    title: str = "",
    orientation: str = "v",
) -> go.Figure:
    """
    Aggregated bar chart.

    Parameters
    ----------
    orientation : 'v' (vertical) or 'h' (horizontal)
    """
    if df.empty or x_col not in df.columns or y_col not in df.columns:
        return _empty("Select valid X and Y columns.")

    grouped = _agg_series(df, x_col, y_col, agg)
    grouped = grouped.sort_values(y_col, ascending=(orientation == "h"))

    if orientation == "h":
        fig = px.bar(
            grouped, x=y_col, y=x_col,
            orientation="h",
            color=y_col,
            color_continuous_scale="Viridis",
            title=title or f"{agg.title()} of {y_col} by {x_col}",
            template=PLOTLY_TEMPLATE,
        )
    else:
        fig = px.bar(
            grouped, x=x_col, y=y_col,
            color=y_col,
            color_continuous_scale="Viridis",
            title=title or f"{agg.title()} of {y_col} by {x_col}",
            template=PLOTLY_TEMPLATE,
        )

    fig.update_layout(**_layout(title=title or f"{agg.title()} of {y_col} by {x_col}"))
    fig.update_coloraxes(showscale=False)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Line chart
# ─────────────────────────────────────────────────────────────────────────────

def line_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    agg: str = "mean",
    color_col: Optional[str] = None,
    title: str = "",
) -> go.Figure:
    """Line chart with optional grouping by a categorical column."""
    if df.empty or x_col not in df.columns or y_col not in df.columns:
        return _empty("Select valid X and Y columns.")

    if color_col and color_col in df.columns:
        fig = px.line(
            df.sort_values(x_col),
            x=x_col, y=y_col,
            color=color_col,
            markers=True,
            title=title or f"{y_col} over {x_col}",
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=QUALITATIVE_PALETTE,
        )
    else:
        grouped = _agg_series(df, x_col, y_col, agg).sort_values(x_col)
        fig = px.line(
            grouped, x=x_col, y=y_col,
            markers=True,
            title=title or f"{agg.title()} of {y_col} over {x_col}",
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=["#00D4FF"],
        )

    fig.update_layout(**_layout(title=title or f"{y_col} over {x_col}"))
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Scatter plot
# ─────────────────────────────────────────────────────────────────────────────

def scatter_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: Optional[str] = None,
    size_col: Optional[str] = None,
    trendline: bool = True,
    title: str = "",
) -> go.Figure:
    """Scatter plot with optional colour coding, size, and OLS trendline."""
    if df.empty or x_col not in df.columns or y_col not in df.columns:
        return _empty("Select valid X and Y columns.")

    plot_df = df[[c for c in [x_col, y_col, color_col, size_col] if c and c in df.columns]].dropna(subset=[x_col, y_col])

    if plot_df.empty:
        return _empty("No non-null data for the selected columns.")

    kwargs: dict = dict(
        x=x_col, y=y_col,
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=QUALITATIVE_PALETTE,
        opacity=0.75,
        title=title or f"{y_col} vs {x_col}",
    )
    if color_col and color_col in plot_df.columns:
        kwargs["color"] = color_col
    if size_col and size_col in plot_df.columns:
        kwargs["size"] = size_col
        kwargs["size_max"] = 20
    if trendline:
        kwargs["trendline"] = "ols"
        kwargs["trendline_color_override"] = "#FFD700"

    try:
        fig = px.scatter(plot_df, **kwargs)
    except Exception:
        # trendline may fail if scipy not available or too few points
        kwargs.pop("trendline", None)
        kwargs.pop("trendline_color_override", None)
        fig = px.scatter(plot_df, **kwargs)

    fig.update_layout(**_layout(title=title or f"{y_col} vs {x_col}"))
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Histogram
# ─────────────────────────────────────────────────────────────────────────────

def histogram_chart(
    df: pd.DataFrame,
    col: str,
    bins: int = 30,
    color_col: Optional[str] = None,
    title: str = "",
) -> go.Figure:
    """Histogram for a numeric column with optional colour grouping."""
    if df.empty or col not in df.columns:
        return _empty("Select a valid column.")

    plot_df = df[[c for c in [col, color_col] if c and c in df.columns]].dropna(subset=[col])

    kwargs: dict = dict(
        x=col,
        nbins=bins,
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=["#00D4FF"],
        title=title or f"Distribution of {col}",
        opacity=0.85,
    )
    if color_col and color_col in plot_df.columns:
        kwargs["color"] = color_col
        kwargs["color_discrete_sequence"] = QUALITATIVE_PALETTE
        kwargs["barmode"] = "overlay"

    fig = px.histogram(plot_df, **kwargs)
    fig.update_layout(**_layout(title=title or f"Distribution of {col}"))
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Pie / Donut chart
# ─────────────────────────────────────────────────────────────────────────────

def pie_chart(
    df: pd.DataFrame,
    label_col: str,
    value_col: Optional[str] = None,
    agg: str = "count",
    top_n: int = 12,
    donut: bool = True,
    title: str = "",
) -> go.Figure:
    """
    Pie / donut chart.

    If value_col is None, counts occurrences of label_col.
    """
    if df.empty or label_col not in df.columns:
        return _empty("Select a valid label column.")

    if value_col and value_col in df.columns:
        grouped = _agg_series(df, label_col, value_col, agg)
        labels = grouped[label_col]
        values = grouped[value_col]
    else:
        vc = df[label_col].value_counts().head(top_n)
        labels = vc.index.tolist()
        values = vc.values.tolist()

    # Limit to top_n
    if len(labels) > top_n:
        labels = labels[:top_n]
        values = values[:top_n]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.45 if donut else 0,
        marker=dict(colors=QUALITATIVE_PALETTE),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Value: %{value}<br>%{percent}<extra></extra>",
    )])

    fig.update_layout(**_layout(title=title or f"Distribution of {label_col}"))
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Correlation heatmap
# ─────────────────────────────────────────────────────────────────────────────

def correlation_heatmap(corr_df: pd.DataFrame, title: str = "Correlation Matrix") -> go.Figure:
    """Annotated heatmap of a correlation matrix."""
    if corr_df.empty:
        return _empty("Need at least 2 numeric columns for a correlation matrix.")

    fig = go.Figure(data=go.Heatmap(
        z=corr_df.values,
        x=corr_df.columns.tolist(),
        y=corr_df.index.tolist(),
        colorscale="RdBu",
        zmid=0,
        zmin=-1, zmax=1,
        text=corr_df.round(2).values,
        texttemplate="%{text}",
        hovertemplate="<b>%{y} × %{x}</b><br>r = %{z:.3f}<extra></extra>",
        showscale=True,
    ))

    fig.update_layout(
        **_layout(title=title, height=max(350, 60 * len(corr_df))),
        xaxis=dict(tickangle=-30),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Missing-value bar chart
# ─────────────────────────────────────────────────────────────────────────────

def missing_bar_chart(missing_df: pd.DataFrame, title: str = "Missing Values per Column") -> go.Figure:
    """Horizontal bar chart showing missing-value percentages."""
    if missing_df.empty or missing_df["missing_count"].sum() == 0:
        return _empty("No missing values found — the dataset is complete! ✅")

    plot_df = missing_df[missing_df["missing_count"] > 0].copy()

    fig = go.Figure(go.Bar(
        y=plot_df["column"],
        x=plot_df["missing_pct"],
        orientation="h",
        marker=dict(
            color=plot_df["missing_pct"],
            colorscale="Reds",
            showscale=False,
        ),
        hovertemplate="<b>%{y}</b><br>Missing: %{x:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        **_layout(title=title, height=max(300, 35 * len(plot_df))),
        xaxis_title="Missing %",
        yaxis_title="",
        yaxis=dict(autorange="reversed"),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Top-N bar chart
# ─────────────────────────────────────────────────────────────────────────────

def top_n_bar_chart(top_df: pd.DataFrame, column: str, title: str = "") -> go.Figure:
    """Horizontal bar chart for top-N value frequencies."""
    if top_df.empty:
        return _empty("No data available.")

    fig = go.Figure(go.Bar(
        y=top_df["value"].astype(str),
        x=top_df["count"],
        orientation="h",
        marker=dict(
            color=top_df["count"],
            colorscale="Blues",
            showscale=False,
        ),
        hovertemplate="<b>%{y}</b><br>Count: %{x}<br>%{customdata:.1f}%<extra></extra>",
        customdata=top_df["pct"],
    ))

    fig.update_layout(
        **_layout(title=title or f"Top values in '{column}'", height=max(300, 35 * len(top_df))),
        xaxis_title="Count",
        yaxis_title="",
        yaxis=dict(autorange="reversed"),
    )
    return fig
