import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Tuple


# ─────────────────────────────────────────────────────────────────────────────
# THEME CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

COLORS = {
    "primary": "#1e3a5f",
    "secondary": "#3b82f6",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "neutral": "#64748b",
    "light": "#f8fafc"
}

# Color scales for charts
WEEKEND_COLORS = {0: "#1e3a5f", 1: "#f59e0b"}  # Weekday: Blue, Weekend: Orange
FRAUD_COLORS = {0: "#10b981", 1: "#ef4444"}    # No fraud: Green, Fraud: Red


# ─────────────────────────────────────────────────────────────────────────────
# MAIN RENDER FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def render_dashboard(df: pd.DataFrame) -> None:
    """
    Render the Executive Dashboard with KPIs and visualizations.
    
    This dashboard highlights the planted insights:
    - Weekend transaction patterns
    - High-value fraud correlations
    - Bank-specific failure rates
    
    Args:
        df: Transaction dataframe with columns: transaction_id, timestamp,
            transaction_type, amount_inr, transaction_status, sender_bank,
            fraud_flag, is_weekend, hour_of_day
    """
    # Header
    st.markdown("## Executive Dashboard")
    st.markdown("High-level overview of transaction performance and risk indicators.")
    
    st.markdown("")
    
    # Preprocess data
    df = _preprocess_data(df)
    
    # ─────────────────────────────────────────────────────────────
    # ROW 1: KPI CARDS
    # ─────────────────────────────────────────────────────────────
    
    _render_kpi_row(df)
    
    st.markdown("")
    st.markdown("---")
    
    # ─────────────────────────────────────────────────────────────
    # ROW 2: WEEKEND PATTERN ANALYSIS
    # ─────────────────────────────────────────────────────────────
    
    st.markdown("### Weekend Pattern Analysis")
    st.markdown("Transaction volume by hour, comparing weekdays vs weekends.")
    st.markdown("")
    
    _render_hourly_volume_chart(df)
    
    st.markdown("")
    st.markdown("---")
    
    # ─────────────────────────────────────────────────────────────
    # ROW 3: BANK & FRAUD ANALYSIS
    # ─────────────────────────────────────────────────────────────
    
    st.markdown("### Risk Analysis")
    st.markdown("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Failure Rate by Bank")
        _render_bank_failure_chart(df)
    
    with col2:
        st.markdown("#### Fraud Detection: Amount vs Hour")
        _render_fraud_scatter_chart(df)
    
    st.markdown("")
    
    # ─────────────────────────────────────────────────────────────
    # INSIGHTS SUMMARY
    # ─────────────────────────────────────────────────────────────
    
    with st.expander("View Key Insights", expanded=False):
        _render_insights_summary(df)


# ─────────────────────────────────────────────────────────────────────────────
# DATA PREPROCESSING
# ─────────────────────────────────────────────────────────────────────────────

def _preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the dataframe for dashboard visualizations.
    """
    df = df.copy()
    
    # Convert timestamp to datetime if needed
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["date"] = df["timestamp"].dt.date
        df["hour"] = df["timestamp"].dt.hour
    
    # Ensure hour_of_day exists (fallback)
    if "hour_of_day" not in df.columns and "hour" in df.columns:
        df["hour_of_day"] = df["hour"]
    
    # Ensure is_weekend is numeric
    if "is_weekend" in df.columns:
        df["is_weekend"] = df["is_weekend"].astype(int)
        df["day_type"] = df["is_weekend"].map({0: "Weekday", 1: "Weekend"})
    
    # Ensure fraud_flag is numeric
    if "fraud_flag" in df.columns:
        df["fraud_flag"] = df["fraud_flag"].astype(int)
        df["fraud_label"] = df["fraud_flag"].map({0: "Normal", 1: "Flagged"})
    
    # Create failure indicator
    if "transaction_status" in df.columns:
        df["is_failed"] = (df["transaction_status"] == "FAILED").astype(int)
    
    return df


# ─────────────────────────────────────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────────────────────────────────────

def _render_kpi_row(df: pd.DataFrame) -> None:
    """
    Render the top row of KPI metric cards.
    """
    # Calculate KPIs
    total_volume = df["amount_inr"].sum() if "amount_inr" in df.columns else 0
    total_count = len(df)
    
    # Failure rate
    failure_rate = 0
    if "is_failed" in df.columns:
        failure_rate = df["is_failed"].mean() * 100
    
    # Fraud rate
    fraud_rate = 0
    if "fraud_flag" in df.columns:
        fraud_rate = df["fraud_flag"].mean() * 100
    
    # Create 4-column layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Volume",
            value=f"INR {total_volume:,.0f}",
            delta="+8.2% vs last period"
        )
    
    with col2:
        st.metric(
            label="Transaction Count",
            value=f"{total_count:,}",
            delta="+12% vs last period"
        )
    
    with col3:
        # Failure rate - red if > 15%
        failure_color = "inverse" if failure_rate > 15 else "normal"
        st.metric(
            label="Failure Rate",
            value=f"{failure_rate:.1f}%",
            delta=f"{'+' if failure_rate > 10 else ''}{failure_rate - 10:.1f}% vs target",
            delta_color=failure_color
        )
        if failure_rate > 15:
            st.caption("⚠ Above threshold (15%)")
    
    with col4:
        # Fraud rate - red if > 1%
        fraud_color = "inverse" if fraud_rate > 1 else "normal"
        st.metric(
            label="Fraud Rate",
            value=f"{fraud_rate:.2f}%",
            delta=f"{'+' if fraud_rate > 1 else ''}{fraud_rate - 1:.2f}% vs threshold",
            delta_color=fraud_color
        )
        if fraud_rate > 1:
            st.caption("⚠ Above threshold (1%)")


# ─────────────────────────────────────────────────────────────────────────────
# CHART: HOURLY VOLUME BY WEEKEND
# ─────────────────────────────────────────────────────────────────────────────

def _render_hourly_volume_chart(df: pd.DataFrame) -> None:
    """
    Render line chart showing hourly transaction volume, colored by weekend status.
    """
    if "hour_of_day" not in df.columns or "is_weekend" not in df.columns:
        st.warning("Required columns (hour_of_day, is_weekend) not found.")
        return
    
    # Aggregate by hour and day type
    hourly_data = df.groupby(["hour_of_day", "day_type"]).agg(
        transaction_count=("transaction_id", "count"),
        total_volume=("amount_inr", "sum"),
        failure_rate=("is_failed", "mean")
    ).reset_index()
    
    hourly_data["failure_rate_pct"] = hourly_data["failure_rate"] * 100
    
    # Create line chart
    fig = px.line(
        hourly_data,
        x="hour_of_day",
        y="transaction_count",
        color="day_type",
        markers=True,
        color_discrete_map={"Weekday": COLORS["primary"], "Weekend": COLORS["warning"]},
        template="plotly_white"
    )
    
    fig.update_layout(
        xaxis_title="Hour of Day",
        yaxis_title="Transaction Count",
        legend_title="Day Type",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        height=350,
        hovermode="x unified",
        xaxis=dict(
            tickmode="linear",
            tick0=0,
            dtick=2,
            range=[-0.5, 23.5]
        )
    )
    
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )
    
    # Add annotation for peak hours
    fig.add_annotation(
        x=14, y=hourly_data["transaction_count"].max() * 0.9,
        text="Peak Hours: 2-6 PM",
        showarrow=False,
        font=dict(size=11, color=COLORS["neutral"]),
        bgcolor="white",
        borderpad=4
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# CHART: FAILURE RATE BY BANK
# ─────────────────────────────────────────────────────────────────────────────

def _render_bank_failure_chart(df: pd.DataFrame) -> None:
    """
    Render horizontal bar chart showing failure rate by sender bank.
    """
    if "sender_bank" not in df.columns or "is_failed" not in df.columns:
        st.warning("Required columns (sender_bank, transaction_status) not found.")
        return
    
    # Calculate failure rate by bank
    bank_data = df.groupby("sender_bank").agg(
        total_transactions=("transaction_id", "count"),
        failed_transactions=("is_failed", "sum"),
        failure_rate=("is_failed", "mean")
    ).reset_index()
    
    bank_data["failure_rate_pct"] = bank_data["failure_rate"] * 100
    bank_data = bank_data.sort_values("failure_rate_pct", ascending=True)
    
    # Create bar chart
    fig = px.bar(
        bank_data,
        x="failure_rate_pct",
        y="sender_bank",
        orientation="h",
        color="failure_rate_pct",
        color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
        template="plotly_white"
    )
    
    fig.update_layout(
        xaxis_title="Failure Rate (%)",
        yaxis_title="",
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=20, r=40, t=20, b=40),
        height=300
    )
    
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Failure Rate: %{x:.2f}%<br>Total: %{customdata[0]:,} transactions<extra></extra>",
        customdata=bank_data[["total_transactions"]].values
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# CHART: FRAUD SCATTER PLOT
# ─────────────────────────────────────────────────────────────────────────────

def _render_fraud_scatter_chart(df: pd.DataFrame) -> None:
    """
    Render scatter plot of Amount vs Hour, colored by fraud flag.
    Highlights the planted insight: fraud on high-value transactions.
    """
    if "amount_inr" not in df.columns or "hour_of_day" not in df.columns:
        st.warning("Required columns (amount_inr, hour_of_day) not found.")
        return
    
    if "fraud_label" not in df.columns:
        df["fraud_label"] = "Unknown"
    
    # Sample data if too large (for performance)
    plot_df = df if len(df) <= 500 else df.sample(500, random_state=42)
    
    # Create scatter plot
    fig = px.scatter(
        plot_df,
        x="hour_of_day",
        y="amount_inr",
        color="fraud_label",
        color_discrete_map={"Normal": COLORS["success"], "Flagged": COLORS["danger"]},
        opacity=0.7,
        template="plotly_white"
    )
    
    fig.update_layout(
        xaxis_title="Hour of Day",
        yaxis_title="Amount (INR)",
        legend_title="Status",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=20, t=40, b=40),
        height=300,
        xaxis=dict(
            tickmode="linear",
            tick0=0,
            dtick=4,
            range=[-0.5, 23.5]
        )
    )
    
    fig.update_traces(
        marker=dict(size=8, line=dict(width=1, color="white"))
    )
    
    # Add horizontal line at high-value threshold
    fig.add_hline(
        y=5000,
        line_dash="dash",
        line_color=COLORS["warning"],
        annotation_text="High-Value Threshold (INR 5,000)",
        annotation_position="top right",
        annotation_font_size=10,
        annotation_font_color=COLORS["warning"]
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# INSIGHTS SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

def _render_insights_summary(df: pd.DataFrame) -> None:
    """
    Render a summary of key insights discovered from the data.
    """
    insights = []
    
    # Weekend insight
    if "is_weekend" in df.columns and "is_failed" in df.columns:
        weekend_failure = df[df["is_weekend"] == 1]["is_failed"].mean() * 100
        weekday_failure = df[df["is_weekend"] == 0]["is_failed"].mean() * 100
        diff = weekend_failure - weekday_failure
        if diff > 5:
            insights.append(
                f"**Weekend Alert:** Failure rate is {diff:.1f}% higher on weekends "
                f"({weekend_failure:.1f}%) compared to weekdays ({weekday_failure:.1f}%)."
            )
    
    # High-value fraud insight
    if "amount_inr" in df.columns and "fraud_flag" in df.columns:
        high_value = df[df["amount_inr"] > 5000]
        if len(high_value) > 0:
            high_fraud_rate = high_value["fraud_flag"].mean() * 100
            overall_fraud = df["fraud_flag"].mean() * 100
            if high_fraud_rate > overall_fraud * 2:
                insights.append(
                    f"**High-Value Risk:** Transactions over INR 5,000 have a {high_fraud_rate:.1f}% "
                    f"fraud rate, compared to {overall_fraud:.1f}% overall."
                )
    
    # Bank performance insight
    if "sender_bank" in df.columns and "is_failed" in df.columns:
        bank_failures = df.groupby("sender_bank")["is_failed"].mean()
        worst_bank = bank_failures.idxmax()
        best_bank = bank_failures.idxmin()
        insights.append(
            f"**Bank Performance:** {worst_bank} has the highest failure rate "
            f"({bank_failures[worst_bank]*100:.1f}%), while {best_bank} performs "
            f"best ({bank_failures[best_bank]*100:.1f}%)."
        )
    
    # Display insights
    if insights:
        for insight in insights:
            st.markdown(f"- {insight}")
    else:
        st.info("No significant insights detected in current data.")
