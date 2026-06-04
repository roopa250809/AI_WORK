"""
CSV Data Analysis Dashboard
============================
A modern, interactive data analysis web app built with Streamlit.

Features:
  • Upload any CSV file
  • Explore: preview, stats, missing values, filter, sort
  • Visualize: bar, line, scatter, histogram, pie (Plotly)
  • Insights: top-N values, correlations, natural-language summary
  • Clean: drop nulls, fill nulls, remove duplicates, cast dtypes
  • Download cleaned dataset as CSV

Run:
  uv run streamlit run app.py
"""

from __future__ import annotations

import io
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st

from src.csv_analyzer import (
    clean_cast_column,
    clean_drop_dupes,
    clean_drop_nulls,
    clean_fill_nulls,
    correlation_matrix,
    generate_insights,
    get_column_types,
    load_csv,
    missing_report,
    summary_stats,
    top_n_values,
)
from src.viz_builder import (
    bar_chart,
    correlation_heatmap,
    histogram_chart,
    line_chart,
    missing_bar_chart,
    pie_chart,
    scatter_chart,
    top_n_bar_chart,
)

# ─────────────────────────────────────────────────────────────────────────────
# Page config  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WHOOP Data Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Global CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* ── KPI metric cards ── */
.kpi-card {
    background: linear-gradient(135deg, #1A1D23 0%, #252830 100%);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: 12px;
    padding: 18px 14px;
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 212, 255, 0.15);
}
.kpi-icon  { font-size: 26px; margin-bottom: 4px; }
.kpi-value { font-size: 26px; font-weight: 700; color: #00D4FF; margin: 4px 0; }
.kpi-label { font-size: 11px; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.05em; }

/* ── Section headers ── */
.section-header {
    font-size: 18px;
    font-weight: 600;
    color: #FAFAFA;
    border-left: 4px solid #00D4FF;
    padding-left: 12px;
    margin: 20px 0 14px 0;
}

/* ── Insight pills ── */
.insight-pill {
    background: rgba(0, 212, 255, 0.07);
    border: 1px solid rgba(0, 212, 255, 0.18);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
    font-size: 14px;
    color: #E5E7EB;
    line-height: 1.6;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0E1117;
    border-right: 1px solid #2D3139;
}

/* ── Tab styling ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px 6px 0 0;
    padding: 8px 18px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Session state initialisation
# ─────────────────────────────────────────────────────────────────────────────

def _init_state() -> None:
    defaults: dict = {
        "raw_df": None,          # original uploaded DataFrame
        "working_df": None,      # DataFrame after cleaning operations
        "filename": "",
        "data_loaded": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ─────────────────────────────────────────────────────────────────────────────
# Cached CSV loader
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _cached_load(file_bytes: bytes, filename: str) -> tuple[Optional[pd.DataFrame], str]:
    """Cache-friendly wrapper so re-renders don't re-parse the file."""
    import io as _io
    return load_csv(_io.BytesIO(file_bytes))


@st.cache_data(show_spinner=False)
def _cached_load_sample() -> tuple[Optional[pd.DataFrame], str]:
    return load_csv("sample_workouts.csv")


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar() -> None:
    """Render sidebar: file upload, sample data toggle, and column filter."""
    with st.sidebar:
        st.markdown("## 📊 CSV Analyzer")
        st.markdown("---")

        # ── Data source ──────────────────────────────────────────────────────
        st.markdown("### 📁 Data Source")

        uploaded = st.file_uploader(
            "Upload a CSV file",
            type=["csv"],
            help="Upload any CSV file to start exploring your data.",
        )

        use_sample = st.checkbox(
            "Use sample data (WHOOP workouts demo)",
            value=not bool(uploaded),
        )

        if uploaded is not None:
            with st.spinner("Parsing CSV…"):
                df, err = _cached_load(uploaded.read(), uploaded.name)
            if err:
                st.error(f"❌ {err}")
            elif df is not None:
                st.session_state.raw_df = df
                st.session_state.working_df = df.copy()
                st.session_state.filename = uploaded.name
                st.session_state.data_loaded = True
                st.success(f"✅ Loaded **{uploaded.name}** — {len(df):,} rows × {len(df.columns)} cols")
        elif use_sample:
            with st.spinner("Loading sample data…"):
                df, err = _cached_load_sample()
            if err:
                st.error(f"❌ {err}")
            elif df is not None:
                st.session_state.raw_df = df
                st.session_state.working_df = df.copy()
                st.session_state.filename = "sample_workouts.csv"
                st.session_state.data_loaded = True

        st.markdown("---")

        # ── Column selector (shown after data is loaded) ──────────────────
        if st.session_state.data_loaded and st.session_state.working_df is not None:
            df = st.session_state.working_df
            st.markdown("### 🔍 Column Selector")
            all_cols = df.columns.tolist()
            selected_cols = st.multiselect(
                "Show columns",
                options=all_cols,
                default=all_cols,
                help="Choose which columns to include in all views.",
            )
            if selected_cols:
                st.session_state.working_df = df[selected_cols]
            else:
                st.warning("Select at least one column.")

        st.markdown("---")
        st.markdown(
            "<small style='color:#6B7280'>WHOOP Data Analyzer · Built with Streamlit & Plotly</small>",
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Landing page
# ─────────────────────────────────────────────────────────────────────────────

def render_landing() -> None:
    st.markdown(
        "<h1 style='color:#00D4FF; text-align:center; margin-top:60px'>📊 WHOOP Data Analyzer</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#9CA3AF; text-align:center; font-size:18px'>"
        "Upload any CSV file to explore, visualize, and clean your data instantly.</p>",
        unsafe_allow_html=True,
    )

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
        <div style="background:#1A1D23; border:1px solid #2D3139; border-radius:12px; padding:32px; margin-top:24px">
            <h3 style="color:#00D4FF">🚀 Getting Started</h3>
            <ol style="color:#E5E7EB; line-height:2.2">
                <li>Use the <b>sidebar uploader</b> to upload your CSV</li>
                <li>Or check <b>"Use sample data"</b> for a quick demo</li>
                <li>Explore the <b>5 tabs</b> below</li>
            </ol>
            <hr style="border-color:#2D3139; margin:20px 0">
            <h4 style="color:#FFD700">📋 What you'll get:</h4>
            <ul style="color:#9CA3AF; line-height:2.2">
                <li>📂 <b>Upload</b> — preview, shape, dtypes</li>
                <li>🔍 <b>Explore</b> — stats, missing values, filter &amp; sort</li>
                <li>📈 <b>Visualize</b> — bar, line, scatter, histogram, pie</li>
                <li>💡 <b>Insights</b> — top-N, correlations, NL summary</li>
                <li>🧹 <b>Clean</b> — drop nulls, fill, dedupe, cast types</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 1 — Upload / Overview
# ─────────────────────────────────────────────────────────────────────────────

def render_upload_tab(df: pd.DataFrame) -> None:
    col_types = get_column_types(df)
    n_rows, n_cols = df.shape

    # ── KPI cards ────────────────────────────────────────────────────────────
    kpis = [
        ("📏", f"{n_rows:,}", "Rows"),
        ("📐", str(n_cols), "Columns"),
        ("🔢", str(len(col_types["numeric"])), "Numeric Cols"),
        ("🔤", str(len(col_types["categorical"])), "Categorical Cols"),
        ("📅", str(len(col_types["datetime"])), "Datetime Cols"),
        ("❓", f"{int(df.isna().sum().sum()):,}", "Missing Cells"),
    ]
    cols = st.columns(6)
    for col_widget, (icon, value, label) in zip(cols, kpis):
        with col_widget:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Dataset preview ───────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 Dataset Preview</div>', unsafe_allow_html=True)
    preview_rows = st.slider("Rows to preview", min_value=5, max_value=min(100, n_rows), value=min(20, n_rows), step=5)
    st.dataframe(df.head(preview_rows), use_container_width=True, height=350)



# ─────────────────────────────────────────────────────────────────────────────
# Tab 2 — Explore
# ─────────────────────────────────────────────────────────────────────────────

def render_explore_tab(df: pd.DataFrame) -> None:
    col_types = get_column_types(df)

    # ── Summary statistics ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Summary Statistics</div>', unsafe_allow_html=True)
    stats_df = summary_stats(df)
    st.dataframe(
        stats_df.style.format({
            "null_pct": "{:.1f}%",
            "mean": "{:.4g}",
            "median": "{:.4g}",
            "std": "{:.4g}",
            "min": "{:.4g}",
            "max": "{:.4g}",
        }, na_rep="—"),
        use_container_width=True,
        hide_index=True,
    )

    # ── Missing values ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">❓ Missing Values</div>', unsafe_allow_html=True)
    miss_df = missing_report(df)
    c1, c2 = st.columns([1, 2])
    with c1:
        st.dataframe(miss_df, use_container_width=True, hide_index=True)
    with c2:
        st.plotly_chart(missing_bar_chart(miss_df), use_container_width=True, key="explore_missing_bar")

    # ── Filter & Sort ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🔍 Filter & Sort</div>', unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        filter_col = st.selectbox("Filter column", options=["— none —"] + df.columns.tolist(), key="filter_col")
    with fc2:
        sort_col = st.selectbox("Sort by", options=["— none —"] + df.columns.tolist(), key="sort_col")
    with fc3:
        sort_asc = st.radio("Sort order", ["Ascending", "Descending"], horizontal=True, key="sort_order")

    filtered = df.copy()

    # Apply column filter
    if filter_col != "— none —" and filter_col in df.columns:
        series = df[filter_col]
        if pd.api.types.is_numeric_dtype(series):
            col_min = float(series.min())
            col_max = float(series.max())
            if col_min < col_max:
                lo, hi = st.slider(
                    f"Range for **{filter_col}**",
                    min_value=col_min, max_value=col_max,
                    value=(col_min, col_max),
                    key="num_filter_slider",
                )
                filtered = filtered[(filtered[filter_col] >= lo) & (filtered[filter_col] <= hi)]
        else:
            unique_vals = sorted(series.dropna().unique().tolist())
            selected_vals = st.multiselect(
                f"Values for **{filter_col}**",
                options=unique_vals,
                default=unique_vals[:min(10, len(unique_vals))],
                key="cat_filter_vals",
            )
            if selected_vals:
                filtered = filtered[filtered[filter_col].isin(selected_vals)]

    # Apply sort
    if sort_col != "— none —" and sort_col in filtered.columns:
        filtered = filtered.sort_values(sort_col, ascending=(sort_asc == "Ascending"))

    st.caption(f"Showing {len(filtered):,} of {len(df):,} rows")
    st.dataframe(filtered.reset_index(drop=True), use_container_width=True, height=400)

    # Download filtered view
    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered view as CSV",
        data=csv_bytes,
        file_name="filtered_data.csv",
        mime="text/csv",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Tab 3 — Visualize
# ─────────────────────────────────────────────────────────────────────────────

def render_visualize_tab(df: pd.DataFrame) -> None:
    col_types = get_column_types(df)
    num_cols = col_types["numeric"]
    cat_cols = col_types["categorical"]
    all_cols = df.columns.tolist()

    # ── Activity Name vs Avg HR chart ─────────────────────────────────────────
    st.markdown('<div class="section-header">🏃 Average HR by Activity Name</div>', unsafe_allow_html=True)

    # Determine best-match columns for Activity Name and Average HR
    activity_col = next((c for c in all_cols if "activity" in c.lower() and "name" in c.lower()), None)
    avg_hr_col = next((c for c in num_cols if "average" in c.lower() and "hr" in c.lower()), None)

    if activity_col and avg_hr_col:
        # Aggregate: mean HR per unique activity, sorted descending
        agg_df = (
            df.groupby(activity_col, as_index=False)[avg_hr_col]
            .mean()
            .sort_values(avg_hr_col, ascending=True)
        )
        agg_df[avg_hr_col] = agg_df[avg_hr_col].round(1)

        import plotly.express as _px
        fig_activity_hr = _px.bar(
            agg_df,
            x=avg_hr_col,
            y=activity_col,
            orientation="h",
            color=avg_hr_col,
            color_continuous_scale="Viridis",
            title=f"Avg {avg_hr_col} by {activity_col}",
            template="plotly_dark",
            text=avg_hr_col,
        )
        fig_activity_hr.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_activity_hr.update_layout(
            paper_bgcolor="#1A1D23",
            plot_bgcolor="#1A1D23",
            font=dict(color="#FAFAFA", family="Inter, Segoe UI, sans-serif", size=12),
            margin=dict(l=140, r=60, t=55, b=40),
            height=max(350, 45 * len(agg_df)),
            coloraxis_showscale=False,
            xaxis_title=avg_hr_col,
            yaxis_title="",
        )
        st.plotly_chart(fig_activity_hr, use_container_width=True, key="activity_avg_hr")
    else:
        st.info("ℹ️ Could not find 'Activity Name' and/or 'Average HR' columns in this dataset. Use the chart builder below to select columns manually.")

    st.markdown("---")
    st.markdown('<div class="section-header">📈 Interactive Charts</div>', unsafe_allow_html=True)

    # ── Chart type selector ───────────────────────────────────────────────────
    chart_type = st.selectbox(
        "Chart type",
        ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram", "Pie / Donut Chart"],
        key="chart_type",
    )

    # ── Shared controls ───────────────────────────────────────────────────────
    if chart_type in ("Bar Chart", "Line Chart"):
        c1, c2, c3 = st.columns(3)
        with c1:
            # Default x to activity col if available
            default_x_idx = all_cols.index(activity_col) if activity_col and activity_col in all_cols else 0
            x_col = st.selectbox("X-axis", options=all_cols, index=default_x_idx, key="viz_x")
        with c2:
            y_options = num_cols if num_cols else all_cols
            default_y_idx = y_options.index(avg_hr_col) if avg_hr_col and avg_hr_col in y_options else 0
            y_col = st.selectbox("Y-axis (numeric)", options=y_options, index=default_y_idx, key="viz_y")
        with c3:
            color_col = st.selectbox(
                "Color by (optional)",
                ["— none —"] + cat_cols,
                key="viz_color",
            )
            color_col = None if color_col == "— none —" else color_col

        if chart_type == "Bar Chart":
            orientation = st.radio("Orientation", ["Horizontal", "Vertical"], horizontal=True, key="bar_orient")
            fig = bar_chart(df, x_col, y_col, agg="mean", color_col=color_col,
                            orientation="h" if orientation == "Horizontal" else "v")
        else:
            fig = line_chart(df, x_col, y_col, agg="mean", color_col=color_col)

        st.plotly_chart(fig, use_container_width=True, key="viz_main_bar_line")

    elif chart_type == "Scatter Plot":
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            x_options = num_cols if num_cols else all_cols
            x_col = st.selectbox("X-axis (numeric)", options=x_options, key="scat_x")
        with c2:
            y_options = [c for c in num_cols if c != x_col] or all_cols
            y_col = st.selectbox("Y-axis (numeric)", options=y_options, key="scat_y")
        with c3:
            color_col = st.selectbox("Color by (optional)", ["— none —"] + cat_cols, key="scat_color")
            color_col = None if color_col == "— none —" else color_col
        with c4:
            size_col = st.selectbox("Size by (optional)", ["— none —"] + num_cols, key="scat_size")
            size_col = None if size_col == "— none —" else size_col

        trendline = st.checkbox("Show OLS trendline", value=True, key="scat_trend")
        fig = scatter_chart(df, x_col, y_col, color_col=color_col, size_col=size_col, trendline=trendline)
        st.plotly_chart(fig, use_container_width=True, key="viz_main_scatter")

    elif chart_type == "Histogram":
        c1, c2, c3 = st.columns(3)
        with c1:
            hist_col = st.selectbox("Column", options=num_cols if num_cols else all_cols, key="hist_col")
        with c2:
            bins = st.slider("Number of bins", 5, 100, 30, key="hist_bins")
        with c3:
            color_col = st.selectbox("Color by (optional)", ["— none —"] + cat_cols, key="hist_color")
            color_col = None if color_col == "— none —" else color_col

        fig = histogram_chart(df, hist_col, bins=bins, color_col=color_col)
        st.plotly_chart(fig, use_container_width=True, key="viz_main_histogram")

    elif chart_type == "Pie / Donut Chart":
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            label_col = st.selectbox("Label column", options=cat_cols if cat_cols else all_cols, key="pie_label")
        with c2:
            value_col = st.selectbox("Value column (optional)", ["— count —"] + num_cols, key="pie_value")
            value_col = None if value_col == "— count —" else value_col
        with c3:
            agg = st.selectbox("Aggregation", ["sum", "mean", "count"], key="pie_agg")
        with c4:
            top_n = st.slider("Max slices", 3, 20, 10, key="pie_topn")
            donut = st.checkbox("Donut style", value=True, key="pie_donut")

        fig = pie_chart(df, label_col, value_col=value_col, agg=agg, top_n=top_n, donut=donut)
        st.plotly_chart(fig, use_container_width=True, key="viz_main_pie")

    # ── Quick chart gallery ───────────────────────────────────────────────────
    if num_cols and cat_cols:
        st.markdown('<div class="section-header">🖼️ Quick Chart Gallery</div>', unsafe_allow_html=True)
        st.caption("Auto-generated charts based on your data's column types.")

        g1, g2 = st.columns(2)
        with g1:
            # Distribution of first numeric column
            fig_hist = histogram_chart(df, num_cols[0], bins=25,
                                       title=f"Distribution of {num_cols[0]}")
            st.plotly_chart(fig_hist, use_container_width=True, key="gallery_hist")
        with g2:
            # Pie of first categorical column
            fig_pie = pie_chart(df, cat_cols[0], top_n=8,
                                title=f"Distribution of {cat_cols[0]}")
            st.plotly_chart(fig_pie, use_container_width=True, key="gallery_pie")

        if len(num_cols) >= 2:
            g3, g4 = st.columns(2)
            with g3:
                fig_bar = bar_chart(df, cat_cols[0], num_cols[0], agg="mean",
                                    title=f"Avg {num_cols[0]} by {cat_cols[0]}")
                st.plotly_chart(fig_bar, use_container_width=True, key="gallery_bar")
            with g4:
                fig_scat = scatter_chart(df, num_cols[0], num_cols[1],
                                         color_col=cat_cols[0] if cat_cols else None,
                                         trendline=True,
                                         title=f"{num_cols[1]} vs {num_cols[0]}")
                st.plotly_chart(fig_scat, use_container_width=True, key="gallery_scat")


# ─────────────────────────────────────────────────────────────────────────────
# Tab 4 — Insights
# ─────────────────────────────────────────────────────────────────────────────

def render_insights_tab(df: pd.DataFrame) -> None:
    col_types = get_column_types(df)

    # ── Natural-language insights ─────────────────────────────────────────────
    st.markdown('<div class="section-header">💡 Dataset Insights</div>', unsafe_allow_html=True)
    insights = generate_insights(df)
    cols = st.columns(2)
    for i, insight in enumerate(insights):
        with cols[i % 2]:
            st.markdown(f'<div class="insight-pill">{insight}</div>', unsafe_allow_html=True)

    # ── Top-N values ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🏆 Top-N Values</div>', unsafe_allow_html=True)
    all_cols = df.columns.tolist()
    c1, c2 = st.columns([2, 1])
    with c1:
        topn_col = st.selectbox("Column", options=all_cols, key="topn_col")
    with c2:
        topn_n = st.slider("Top N", 3, 30, 10, key="topn_n")

    top_df = top_n_values(df, topn_col, n=topn_n)
    tc1, tc2 = st.columns([1, 2])
    with tc1:
        st.dataframe(top_df, use_container_width=True, hide_index=True)
    with tc2:
        st.plotly_chart(top_n_bar_chart(top_df, topn_col), use_container_width=True, key="insights_topn_bar")

    # ── Correlation matrix ────────────────────────────────────────────────────
    num_cols = col_types["numeric"]
    if len(num_cols) >= 2:
        st.markdown('<div class="section-header">🔗 Correlation Matrix</div>', unsafe_allow_html=True)

        # Column selector for correlation
        selected_num = st.multiselect(
            "Select numeric columns for correlation",
            options=num_cols,
            default=num_cols[:min(10, len(num_cols))],
            key="corr_cols",
        )
        if len(selected_num) >= 2:
            corr_df = correlation_matrix(df[selected_num])
            cc1, cc2 = st.columns([1, 2])
            with cc1:
                st.dataframe(corr_df.style.background_gradient(cmap="RdBu", vmin=-1, vmax=1),
                             use_container_width=True)
            with cc2:
                st.plotly_chart(correlation_heatmap(corr_df), use_container_width=True, key="insights_corr_heatmap")
        else:
            st.info("Select at least 2 numeric columns to compute correlations.")
    else:
        st.info("ℹ️ No numeric columns available for correlation analysis.")

    # ── Columns with highest missing data ─────────────────────────────────────
    st.markdown('<div class="section-header">⚠️ Columns with Most Missing Data</div>', unsafe_allow_html=True)
    miss_df = missing_report(df)
    top_missing = miss_df[miss_df["missing_count"] > 0].head(10)
    if top_missing.empty:
        st.success("✅ No missing values in this dataset!")
    else:
        st.dataframe(top_missing, use_container_width=True, hide_index=True)
        st.plotly_chart(missing_bar_chart(top_missing), use_container_width=True, key="insights_missing_bar")


# ─────────────────────────────────────────────────────────────────────────────
# Tab 5 — Clean
# ─────────────────────────────────────────────────────────────────────────────

def render_clean_tab(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-header">🧹 Data Cleaning Tools</div>', unsafe_allow_html=True)

    working = st.session_state.working_df.copy()
    original_shape = st.session_state.raw_df.shape

    # Status bar
    st.info(
        f"**Working dataset:** {len(working):,} rows × {len(working.columns)} columns  |  "
        f"**Original:** {original_shape[0]:,} rows × {original_shape[1]} columns"
    )

    # ── Drop missing values ───────────────────────────────────────────────────
    with st.expander("🗑️ Drop Rows with Missing Values", expanded=True):
        dc1, dc2 = st.columns(2)
        with dc1:
            drop_how = st.radio("Drop rows where", ["any column is null", "all columns are null"],
                                key="drop_how")
        with dc2:
            drop_subset = st.multiselect(
                "Consider only these columns (leave empty = all)",
                options=working.columns.tolist(),
                key="drop_subset",
            )

        n_before = len(working)
        if st.button("Apply: Drop Nulls", key="btn_drop_nulls"):
            how = "any" if "any" in drop_how else "all"
            subset = drop_subset if drop_subset else None
            working = clean_drop_nulls(working, how=how, subset=subset)
            st.session_state.working_df = working
            st.success(f"✅ Dropped {n_before - len(working):,} rows. Remaining: {len(working):,}")
            st.rerun()

    # ── Fill missing values ───────────────────────────────────────────────────
    with st.expander("✏️ Fill Missing Values", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            fill_col = st.selectbox("Column to fill", options=working.columns.tolist(), key="fill_col")
        with fc2:
            fill_strategy = st.selectbox("Fill strategy", ["mean", "median", "mode", "custom"], key="fill_strategy")
        with fc3:
            custom_val = ""
            if fill_strategy == "custom":
                custom_val = st.text_input("Custom fill value", key="fill_custom_val")

        null_count = int(working[fill_col].isna().sum()) if fill_col in working.columns else 0
        st.caption(f"Nulls in **{fill_col}**: {null_count:,}")

        if st.button("Apply: Fill Nulls", key="btn_fill_nulls"):
            if null_count == 0:
                st.info("No nulls to fill in this column.")
            else:
                cv = custom_val if fill_strategy == "custom" else None
                working = clean_fill_nulls(working, fill_col, strategy=fill_strategy, custom_value=cv)
                st.session_state.working_df = working
                st.success(f"✅ Filled {null_count:,} null(s) in **{fill_col}** using **{fill_strategy}**.")
                st.rerun()

    # ── Remove duplicates ─────────────────────────────────────────────────────
    with st.expander("🔁 Remove Duplicate Rows", expanded=False):
        dupe_subset = st.multiselect(
            "Consider only these columns (leave empty = all)",
            options=working.columns.tolist(),
            key="dupe_subset",
        )
        n_dupes = int(working.duplicated(subset=dupe_subset if dupe_subset else None).sum())
        st.caption(f"Duplicate rows detected: **{n_dupes:,}**")

        if st.button("Apply: Remove Duplicates", key="btn_drop_dupes"):
            if n_dupes == 0:
                st.info("No duplicate rows found.")
            else:
                subset = dupe_subset if dupe_subset else None
                working = clean_drop_dupes(working, subset=subset)
                st.session_state.working_df = working
                st.success(f"✅ Removed {n_dupes:,} duplicate row(s). Remaining: {len(working):,}")
                st.rerun()

    # ── Change column dtype ───────────────────────────────────────────────────
    with st.expander("🔄 Change Column Data Type", expanded=False):
        cc1, cc2 = st.columns(2)
        with cc1:
            cast_col = st.selectbox("Column", options=working.columns.tolist(), key="cast_col")
            current_dtype = str(working[cast_col].dtype) if cast_col in working.columns else "—"
            st.caption(f"Current dtype: **{current_dtype}**")
        with cc2:
            target_dtype = st.selectbox(
                "Target type",
                ["numeric", "string", "datetime", "boolean", "category"],
                key="cast_dtype",
            )

        if st.button("Apply: Cast Column", key="btn_cast"):
            new_df, err = clean_cast_column(working, cast_col, target_dtype)
            if err:
                st.error(f"❌ {err}")
            else:
                st.session_state.working_df = new_df
                working = new_df
                st.success(f"✅ Cast **{cast_col}** to **{target_dtype}**.")
                st.rerun()

    # ── Reset ─────────────────────────────────────────────────────────────────
    st.markdown("---")
    if st.button("🔄 Reset to Original Data", key="btn_reset"):
        st.session_state.working_df = st.session_state.raw_df.copy()
        st.success("✅ Reset to original uploaded data.")
        st.rerun()

    # ── Preview & Download ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 Cleaned Data Preview</div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.working_df.head(20), use_container_width=True, height=350)

    csv_bytes = st.session_state.working_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Cleaned Dataset as CSV",
        data=csv_bytes,
        file_name="cleaned_data.csv",
        mime="text/csv",
        type="primary",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main dashboard
# ─────────────────────────────────────────────────────────────────────────────

def render_dashboard() -> None:
    df = st.session_state.working_df

    # Header
    filename = st.session_state.filename
    st.markdown(
        f"<h1 style='color:#00D4FF; margin-bottom:2px'>📊 WHOOP Data Analyzer</h1>"
        f"<p style='color:#6B7280; margin-top:0'>Analyzing: <b>{filename}</b></p>",
        unsafe_allow_html=True,
    )

    # Tabs
    tab_upload, tab_viz = st.tabs([
        "📂 Upload",
        "📈 Visualize",
    ])

    with tab_upload:
        render_upload_tab(df)

    with tab_viz:
        render_visualize_tab(df)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    _init_state()
    render_sidebar()

    if not st.session_state.data_loaded or st.session_state.working_df is None:
        render_landing()
        return

    render_dashboard()


if __name__ == "__main__":
    main()
