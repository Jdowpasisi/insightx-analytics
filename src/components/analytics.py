import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Tuple


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

DIMENSION_OPTIONS = [
    "transaction_type",
    "merchant_category", 
    "sender_bank",
    "sender_state",
    "device_type",
    "network_type",
    "sender_age_group"
]

METRIC_OPTIONS = [
    "Transaction Count",
    "Total Volume (INR)",
    "Failure Rate"
]

# Clean display names for dimensions
DIMENSION_LABELS = {
    "transaction_type": "Transaction Type",
    "merchant_category": "Merchant Category",
    "sender_bank": "Sender Bank",
    "sender_state": "Sender State",
    "device_type": "Device Type",
    "network_type": "Network Type",
    "sender_age_group": "Sender Age Group"
}

# Color palette (Midnight Blue theme)
COLORS = {
    "primary": "#1e3a5f",
    "secondary": "#3b82f6",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444"
}

COLOR_SCALE = ["#1e3a5f", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd"]


# ─────────────────────────────────────────────────────────────────────────────
# MAIN RENDER FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def render_analytics(df: pd.DataFrame) -> None:
    """
    Render the Dynamic Field Explorer analytics page.
    
    Args:
        df: The main transactions dataframe.
    """
    # Header
    st.markdown("## Dynamic Field Explorer")
    st.markdown("Select a dimension and metric to explore your transaction data interactively.")
    
    st.markdown("")
    
    # Preprocess dataframe - handle nulls
    df = _preprocess_dataframe(df)
    
    # ─────────────────────────────────────────────────────────────
    # CONTROL PANEL
    # ─────────────────────────────────────────────────────────────
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_dimension = st.selectbox(
            "Select Dimension to Analyze",
            options=DIMENSION_OPTIONS,
            format_func=lambda x: DIMENSION_LABELS.get(x, x),
            key="analytics_dimension"
        )
    
    with col2:
        selected_metric = st.selectbox(
            "Select Metric",
            options=METRIC_OPTIONS,
            key="analytics_metric"
        )
    
    st.markdown("---")
    
    # Dynamic title based on selection
    dimension_label = DIMENSION_LABELS.get(selected_dimension, selected_dimension)
    st.markdown(f"### Analysis of: {dimension_label}")
    st.markdown("")
    
    # ─────────────────────────────────────────────────────────────
    # CALCULATE AGGREGATIONS
    # ─────────────────────────────────────────────────────────────
    
    summary_df = _calculate_summary(df, selected_dimension, selected_metric)
    time_series_df = _calculate_time_series(df, selected_dimension)
    failure_df = _calculate_failure_rates(df, selected_dimension)
    
    # ─────────────────────────────────────────────────────────────
    # CHART A: PRIMARY DISTRIBUTION (Bar Chart)
    # ─────────────────────────────────────────────────────────────
    
    st.markdown(f"#### {selected_metric} by {dimension_label}")
    _render_distribution_chart(summary_df, selected_dimension, selected_metric, dimension_label)
    
    st.markdown("")
    
    # ─────────────────────────────────────────────────────────────
    # CHART ROW: TIME TREND + RISK HEATMAP
    # ─────────────────────────────────────────────────────────────
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown(f"#### Daily Trend by {dimension_label}")
        _render_time_trend_chart(time_series_df, selected_dimension, dimension_label)
    
    with chart_col2:
        st.markdown(f"#### Failure Rate by {dimension_label}")
        _render_failure_heatmap(failure_df, selected_dimension, dimension_label)
    
    st.markdown("")
    st.markdown("---")
    
    # ─────────────────────────────────────────────────────────────
    # DATA DRILL-DOWN TABLE
    # ─────────────────────────────────────────────────────────────
    
    st.markdown("#### Aggregated Summary")
    _render_summary_table(df, selected_dimension, dimension_label)


# ─────────────────────────────────────────────────────────────────────────────
# DATA PROCESSING FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def _preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess dataframe - handle nulls and convert types.
    """
    df = df.copy()
    
    # Fill nulls with "Unknown" for categorical columns
    for col in DIMENSION_OPTIONS:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str)
    
    # Ensure timestamp is datetime
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["date"] = df["timestamp"].dt.date
    
    return df


def _calculate_summary(df: pd.DataFrame, dimension: str, metric: str) -> pd.DataFrame:
    """
    Calculate summary statistics grouped by dimension.
    """
    if dimension not in df.columns:
        return pd.DataFrame()
    
    if metric == "Transaction Count":
        summary = df.groupby(dimension).size().reset_index(name="value")
    elif metric == "Total Volume (INR)":
        summary = df.groupby(dimension)["amount_inr"].sum().reset_index(name="value")
    elif metric == "Failure Rate":
        df["is_failed"] = (df["transaction_status"] == "FAILED").astype(int)
        summary = df.groupby(dimension)["is_failed"].mean().reset_index(name="value")
        summary["value"] = summary["value"] * 100  # Convert to percentage
    else:
        summary = df.groupby(dimension).size().reset_index(name="value")
    
    # Sort descending
    summary = summary.sort_values("value", ascending=False)
    
    return summary


def _calculate_time_series(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """
    Calculate daily transaction counts by dimension.
    """
    if dimension not in df.columns or "date" not in df.columns:
        return pd.DataFrame()
    
    # Get top 5 categories to avoid chart clutter
    top_categories = df[dimension].value_counts().head(5).index.tolist()
    df_filtered = df[df[dimension].isin(top_categories)]
    
    time_series = df_filtered.groupby(["date", dimension]).size().reset_index(name="count")
    time_series["date"] = pd.to_datetime(time_series["date"])
    
    return time_series


def _calculate_failure_rates(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """
    Calculate failure rates by dimension.
    """
    if dimension not in df.columns or "transaction_status" not in df.columns:
        return pd.DataFrame()
    
    df["is_failed"] = (df["transaction_status"] == "FAILED").astype(int)
    
    failure_df = df.groupby(dimension).agg(
        total_transactions=("is_failed", "count"),
        failed_transactions=("is_failed", "sum"),
        failure_rate=("is_failed", "mean")
    ).reset_index()
    
    failure_df["failure_rate_pct"] = failure_df["failure_rate"] * 100
    failure_df = failure_df.sort_values("failure_rate_pct", ascending=False)
    
    return failure_df


# ─────────────────────────────────────────────────────────────────────────────
# CHART RENDERING FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def _render_distribution_chart(
    summary_df: pd.DataFrame, 
    dimension: str, 
    metric: str,
    dimension_label: str
) -> None:
    """
    Render the primary distribution bar chart.
    """
    if summary_df.empty:
        st.warning(f"No data available for {dimension_label}.")
        return
    
    # Format y-axis label
    if metric == "Total Volume (INR)":
        y_label = "Volume (INR)"
    elif metric == "Failure Rate":
        y_label = "Failure Rate (%)"
    else:
        y_label = "Count"
    
    fig = px.bar(
        summary_df,
        x=dimension,
        y="value",
        color="value",
        color_continuous_scale=COLOR_SCALE,
        template="plotly_white"
    )
    
    fig.update_layout(
        xaxis_title=dimension_label,
        yaxis_title=y_label,
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=40, r=40, t=20, b=80),
        height=350,
        xaxis_tickangle=-45
    )
    
    fig.update_traces(
        hovertemplate=f"<b>{dimension_label}:</b> %{{x}}<br><b>{metric}:</b> %{{y:,.2f}}<extra></extra>"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _render_time_trend_chart(
    time_series_df: pd.DataFrame,
    dimension: str,
    dimension_label: str
) -> None:
    """
    Render the time trend line chart.
    """
    if time_series_df.empty:
        st.info(f"No time series data available for {dimension_label}.")
        return
    
    fig = px.line(
        time_series_df,
        x="date",
        y="count",
        color=dimension,
        template="plotly_white",
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Transaction Count",
        legend_title=dimension_label,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.4,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=20, t=20, b=100),
        height=350,
        hovermode="x unified"
    )
    
    fig.update_traces(line=dict(width=2))
    
    st.plotly_chart(fig, use_container_width=True)


def _render_failure_heatmap(
    failure_df: pd.DataFrame,
    dimension: str,
    dimension_label: str
) -> None:
    """
    Render the failure rate risk chart.
    """
    if failure_df.empty:
        st.info(f"No failure data available for {dimension_label}.")
        return
    
    # Use horizontal bar chart for failure rates (easier to read)
    fig = px.bar(
        failure_df.head(10),  # Top 10 only
        x="failure_rate_pct",
        y=dimension,
        orientation="h",
        color="failure_rate_pct",
        color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],  # Green to Red
        template="plotly_white"
    )
    
    fig.update_layout(
        xaxis_title="Failure Rate (%)",
        yaxis_title="",
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=20, r=40, t=20, b=40),
        height=350,
        yaxis=dict(categoryorder="total ascending")
    )
    
    fig.update_traces(
        hovertemplate=f"<b>{dimension_label}:</b> %{{y}}<br><b>Failure Rate:</b> %{{x:.2f}}%<extra></extra>"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _render_summary_table(
    df: pd.DataFrame,
    dimension: str,
    dimension_label: str
) -> None:
    """
    Render the aggregated summary data table.
    """
    if dimension not in df.columns:
        st.warning(f"Column '{dimension}' not found in dataset.")
        return
    
    # Calculate comprehensive summary
    df["is_failed"] = (df["transaction_status"] == "FAILED").astype(int)
    df["is_success"] = (df["transaction_status"] == "SUCCESS").astype(int)
    
    summary = df.groupby(dimension).agg(
        total_transactions=("transaction_id", "count"),
        total_volume=("amount_inr", "sum"),
        avg_amount=("amount_inr", "mean"),
        success_count=("is_success", "sum"),
        failed_count=("is_failed", "sum"),
        failure_rate=("is_failed", "mean")
    ).reset_index()
    
    # Format columns
    summary["total_volume"] = summary["total_volume"].apply(lambda x: f"INR {x:,.0f}")
    summary["avg_amount"] = summary["avg_amount"].apply(lambda x: f"INR {x:,.0f}")
    summary["failure_rate"] = summary["failure_rate"].apply(lambda x: f"{x*100:.1f}%")
    
    # Sort by total transactions
    summary = summary.sort_values("total_transactions", ascending=False)
    
    # Rename columns for display
    summary.columns = [
        dimension_label,
        "Total Transactions",
        "Total Volume",
        "Avg Amount",
        "Success Count",
        "Failed Count",
        "Failure Rate"
    ]
    
    st.dataframe(summary, use_container_width=True, hide_index=True)
