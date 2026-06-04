"""
CSV Data Analyzer — core logic for the universal CSV analysis dashboard.

Provides:
  - load_csv()           : parse uploaded CSV with error handling
  - get_column_types()   : classify columns as numeric / categorical / datetime
  - summary_stats()      : mean, median, min, max, std, null counts
  - missing_report()     : per-column missing value summary
  - correlation_matrix() : Pearson correlations for numeric columns
  - top_n_values()       : most frequent values per categorical column
  - generate_insights()  : natural-language dataset summary
  - clean_drop_nulls()   : drop rows with any/all nulls
  - clean_fill_nulls()   : fill nulls with mean / median / custom value
  - clean_drop_dupes()   : remove duplicate rows
  - clean_cast_column()  : change a column's dtype
"""

from __future__ import annotations

import io
from typing import Any, Optional

import numpy as np
import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# Loading
# ─────────────────────────────────────────────────────────────────────────────

def load_csv(file_obj) -> tuple[Optional[pd.DataFrame], str]:
    """
    Parse a CSV from a file-like object or path.

    Returns
    -------
    (df, error_message)
        df is None when parsing fails; error_message is '' on success.
    """
    try:
        if hasattr(file_obj, "read"):
            raw = file_obj.read()
            # Try UTF-8 first, fall back to latin-1
            for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
                try:
                    df = pd.read_csv(io.BytesIO(raw), encoding=enc)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                return None, "Could not decode the file. Try saving it as UTF-8."
        else:
            df = pd.read_csv(file_obj)
    except pd.errors.EmptyDataError:
        return None, "The uploaded file is empty."
    except pd.errors.ParserError as exc:
        return None, f"CSV parse error: {exc}"
    except Exception as exc:
        return None, f"Unexpected error reading file: {exc}"

    if df.empty:
        return None, "The CSV has no data rows."

    # Strip leading/trailing whitespace from column names
    df.columns = df.columns.str.strip()

    # Attempt to infer better dtypes (e.g. parse numeric strings)
    df = df.infer_objects()

    return df, ""


# ─────────────────────────────────────────────────────────────────────────────
# Column classification
# ─────────────────────────────────────────────────────────────────────────────

def get_column_types(df: pd.DataFrame) -> dict[str, list[str]]:
    """
    Classify DataFrame columns into numeric, categorical, and datetime.

    Returns
    -------
    {
        "numeric":     [...],
        "categorical": [...],
        "datetime":    [...],
    }
    """
    numeric: list[str] = []
    categorical: list[str] = []
    datetime_cols: list[str] = []

    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_cols.append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            numeric.append(col)
        else:
            # Try to parse as datetime
            try:
                parsed = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
                if parsed.notna().sum() / max(len(df), 1) > 0.5:
                    datetime_cols.append(col)
                    continue
            except Exception:
                pass
            categorical.append(col)

    return {"numeric": numeric, "categorical": categorical, "datetime": datetime_cols}


# ─────────────────────────────────────────────────────────────────────────────
# Summary statistics
# ─────────────────────────────────────────────────────────────────────────────

def summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute descriptive statistics for all columns.

    Returns a DataFrame with columns:
        column, dtype, count, null_count, null_pct,
        mean, median, std, min, max  (numeric only; NaN for others)
    """
    rows = []
    for col in df.columns:
        series = df[col]
        null_count = int(series.isna().sum())
        null_pct = round(null_count / max(len(df), 1) * 100, 2)
        row: dict[str, Any] = {
            "column": col,
            "dtype": str(series.dtype),
            "count": int(series.notna().sum()),
            "null_count": null_count,
            "null_pct": null_pct,
            "mean": np.nan,
            "median": np.nan,
            "std": np.nan,
            "min": np.nan,
            "max": np.nan,
        }
        if pd.api.types.is_numeric_dtype(series):
            clean = series.dropna()
            if len(clean) > 0:
                row["mean"] = round(float(clean.mean()), 4)
                row["median"] = round(float(clean.median()), 4)
                row["std"] = round(float(clean.std()), 4)
                row["min"] = round(float(clean.min()), 4)
                row["max"] = round(float(clean.max()), 4)
        rows.append(row)

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Missing value report
# ─────────────────────────────────────────────────────────────────────────────

def missing_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame sorted by missing-value count (descending).

    Columns: column, missing_count, missing_pct
    """
    missing = df.isna().sum().reset_index()
    missing.columns = ["column", "missing_count"]
    missing["missing_pct"] = (missing["missing_count"] / max(len(df), 1) * 100).round(2)
    return missing.sort_values("missing_count", ascending=False).reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────
# Correlation matrix
# ─────────────────────────────────────────────────────────────────────────────

def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Pearson correlation matrix for numeric columns.

    Returns an empty DataFrame if fewer than 2 numeric columns exist.
    """
    num_cols = df.select_dtypes(include="number").columns.tolist()
    if len(num_cols) < 2:
        return pd.DataFrame()
    return df[num_cols].corr(method="pearson").round(3)


# ─────────────────────────────────────────────────────────────────────────────
# Top-N values
# ─────────────────────────────────────────────────────────────────────────────

def top_n_values(df: pd.DataFrame, column: str, n: int = 10) -> pd.DataFrame:
    """
    Return the top-N most frequent values for a column.

    Returns a DataFrame with columns: value, count, pct
    """
    if column not in df.columns:
        return pd.DataFrame()
    vc = df[column].value_counts(dropna=False).head(n).reset_index()
    vc.columns = ["value", "count"]
    vc["pct"] = (vc["count"] / max(len(df), 1) * 100).round(2)
    return vc


# ─────────────────────────────────────────────────────────────────────────────
# Natural-language insights
# ─────────────────────────────────────────────────────────────────────────────

def generate_insights(df: pd.DataFrame) -> list[str]:
    """
    Generate a list of plain-English insight strings about the dataset.
    """
    insights: list[str] = []
    col_types = get_column_types(df)
    n_rows, n_cols = df.shape

    # Basic shape
    insights.append(
        f"📋 **Dataset shape:** {n_rows:,} rows × {n_cols} columns "
        f"({len(col_types['numeric'])} numeric, "
        f"{len(col_types['categorical'])} categorical, "
        f"{len(col_types['datetime'])} datetime)."
    )

    # Missing data
    total_cells = n_rows * n_cols
    total_missing = int(df.isna().sum().sum())
    if total_missing == 0:
        insights.append("✅ **No missing values** — the dataset is complete.")
    else:
        pct = round(total_missing / max(total_cells, 1) * 100, 1)
        worst_col = df.isna().sum().idxmax()
        worst_pct = round(df[worst_col].isna().mean() * 100, 1)
        insights.append(
            f"⚠️ **Missing data:** {total_missing:,} cells ({pct}% of total). "
            f"Worst column: **{worst_col}** ({worst_pct}% missing)."
        )

    # Duplicates
    n_dupes = int(df.duplicated().sum())
    if n_dupes > 0:
        insights.append(
            f"🔁 **Duplicate rows:** {n_dupes:,} ({round(n_dupes/max(n_rows,1)*100,1)}% of rows). "
            "Consider removing them in the Clean tab."
        )
    else:
        insights.append("✅ **No duplicate rows** detected.")

    # Numeric column highlights
    num_cols = col_types["numeric"]
    if num_cols:
        stats = df[num_cols].describe()
        # Highest variance column
        std_series = stats.loc["std"]
        cv_series = (std_series / stats.loc["mean"].replace(0, np.nan)).abs()
        if cv_series.notna().any():
            most_variable = cv_series.idxmax()
            insights.append(
                f"📊 **Most variable numeric column:** **{most_variable}** "
                f"(coefficient of variation = {cv_series[most_variable]:.2f})."
            )

        # Skewness
        skew_series = df[num_cols].skew().abs()
        if skew_series.notna().any() and skew_series.max() > 1.0:
            most_skewed = skew_series.idxmax()
            insights.append(
                f"📐 **Highly skewed column:** **{most_skewed}** "
                f"(|skewness| = {skew_series[most_skewed]:.2f}). "
                "Consider log-transforming for analysis."
            )

    # Categorical column highlights
    cat_cols = col_types["categorical"]
    if cat_cols:
        # High-cardinality columns
        for col in cat_cols:
            n_unique = df[col].nunique()
            if n_unique > 0.9 * n_rows and n_rows > 20:
                insights.append(
                    f"🔑 **High-cardinality column:** **{col}** has {n_unique:,} unique values "
                    "(likely an ID or free-text field)."
                )
                break

        # Dominant category
        for col in cat_cols[:3]:
            vc = df[col].value_counts(normalize=True)
            if len(vc) > 0 and vc.iloc[0] > 0.5:
                insights.append(
                    f"🏆 **Dominant category in {col}:** '{vc.index[0]}' "
                    f"appears in {vc.iloc[0]*100:.1f}% of rows."
                )

    # Correlation highlights
    corr = correlation_matrix(df)
    if not corr.empty:
        # Find strongest off-diagonal correlation using numpy directly
        corr_arr = corr.to_numpy(dtype=float, copy=True)
        np.fill_diagonal(corr_arr, 0)
        corr_abs = np.abs(corr_arr)
        max_corr = float(corr_abs.max())
        if max_corr > 0.7:
            flat_idx = int(corr_abs.argmax())
            n = corr_abs.shape[1]
            row_i, col_i = divmod(flat_idx, n)
            col_names = corr.columns.tolist()
            raw_corr = float(corr_arr[row_i, col_i])
            direction = "positive" if raw_corr > 0 else "negative"
            insights.append(
                f"🔗 **Strong {direction} correlation** ({raw_corr:.2f}) between "
                f"**{col_names[row_i]}** and **{col_names[col_i]}**."
            )

    return insights


# ─────────────────────────────────────────────────────────────────────────────
# Data cleaning helpers
# ─────────────────────────────────────────────────────────────────────────────

def clean_drop_nulls(df: pd.DataFrame, how: str = "any", subset: Optional[list[str]] = None) -> pd.DataFrame:
    """
    Drop rows containing null values.

    Parameters
    ----------
    how    : 'any' (default) or 'all'
    subset : list of columns to consider; None = all columns
    """
    return df.dropna(how=how, subset=subset).reset_index(drop=True)


def clean_fill_nulls(
    df: pd.DataFrame,
    column: str,
    strategy: str = "mean",
    custom_value: Any = None,
) -> pd.DataFrame:
    """
    Fill null values in a single column.

    Parameters
    ----------
    strategy : 'mean' | 'median' | 'mode' | 'custom'
    custom_value : used when strategy == 'custom'
    """
    df = df.copy()
    if column not in df.columns:
        return df

    series = df[column]

    if strategy == "mean":
        fill = series.mean()
    elif strategy == "median":
        fill = series.median()
    elif strategy == "mode":
        mode_vals = series.mode()
        fill = mode_vals.iloc[0] if len(mode_vals) > 0 else None
    elif strategy == "custom":
        fill = custom_value
    else:
        fill = None

    if fill is not None:
        df[column] = series.fillna(fill)

    return df


def clean_drop_dupes(df: pd.DataFrame, subset: Optional[list[str]] = None) -> pd.DataFrame:
    """Remove duplicate rows (optionally considering only a subset of columns)."""
    return df.drop_duplicates(subset=subset).reset_index(drop=True)


def clean_cast_column(df: pd.DataFrame, column: str, target_dtype: str) -> tuple[pd.DataFrame, str]:
    """
    Attempt to cast a column to a new dtype.

    Returns
    -------
    (df, error_message)
        error_message is '' on success.
    """
    df = df.copy()
    if column not in df.columns:
        return df, f"Column '{column}' not found."

    try:
        if target_dtype == "datetime":
            df[column] = pd.to_datetime(df[column], errors="coerce")
        elif target_dtype == "numeric":
            df[column] = pd.to_numeric(df[column], errors="coerce")
        elif target_dtype == "string":
            df[column] = df[column].astype(str)
        elif target_dtype == "boolean":
            df[column] = df[column].astype(bool)
        elif target_dtype == "category":
            df[column] = df[column].astype("category")
        else:
            df[column] = df[column].astype(target_dtype)
    except Exception as exc:
        return df, f"Could not cast '{column}' to {target_dtype}: {exc}"

    return df, ""
