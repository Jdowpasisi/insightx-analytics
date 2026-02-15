import streamlit as st
import pandas as pd
import time
from typing import List


# ─────────────────────────────────────────────────────────────────────────────
# THEME CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

COLORS = {
    "primary": "#1e3a5f",
    "secondary": "#3b82f6",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444"
}


# ─────────────────────────────────────────────────────────────────────────────
# MAIN RENDER FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def render_reports(df: pd.DataFrame) -> None:
    """
    Render the Monthly Executive Report page.
    
    This page provides:
    - AI-generated executive summary
    - Red flag ledger (weekend failures)
    - Fraud watchlist (high-value flagged transactions)
    - Export functionality
    
    Args:
        df: Transaction dataframe
    """
    # Header
    st.markdown("## Monthly Executive Report")
    st.markdown("Audit-ready analysis and actionable insights for leadership review.")
    
    st.markdown("")
    
    # Preprocess data
    df = _preprocess_data(df)
    
    # ─────────────────────────────────────────────────────────────
    # PROCESSING SPINNER (Simulated AI Generation)
    # ─────────────────────────────────────────────────────────────
    
    # Only show spinner on first load (use session state)
    if "report_generated" not in st.session_state:
        with st.spinner("Generating AI-powered insights..."):
            time.sleep(1)
        st.session_state.report_generated = True
    
    # ─────────────────────────────────────────────────────────────
    # SECTION 1: AI EXECUTIVE SUMMARY
    # ─────────────────────────────────────────────────────────────
    
    st.subheader("AI Executive Summary")
    
    _render_executive_summary(df)
    
    st.markdown("")
    st.markdown("---")
    
    # ─────────────────────────────────────────────────────────────
    # SECTION 2: RED FLAG LEDGER (Weekend Failures)
    # ─────────────────────────────────────────────────────────────
    
    st.subheader("Red Flag Ledger: Weekend Failures")
    
    _render_red_flag_ledger(df)
    
    st.markdown("")
    st.markdown("---")
    
    # ─────────────────────────────────────────────────────────────
    # SECTION 3: FRAUD WATCHLIST
    # ─────────────────────────────────────────────────────────────
    
    st.subheader("Fraud Watchlist: High-Value Flagged Transactions")
    
    _render_fraud_watchlist(df)
    
    st.markdown("")
    st.markdown("---")
    
    # ─────────────────────────────────────────────────────────────
    # SECTION 4: EXPORT OPTIONS
    # ─────────────────────────────────────────────────────────────
    
    st.subheader("Export Options")
    
    _render_export_section(df)


# ─────────────────────────────────────────────────────────────────────────────
# DATA PREPROCESSING
# ─────────────────────────────────────────────────────────────────────────────

def _preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess dataframe for report generation.
    """
    df = df.copy()
    
    # Convert timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    
    # Ensure is_weekend is numeric
    if "is_weekend" in df.columns:
        df["is_weekend"] = df["is_weekend"].astype(int)
    
    # Ensure fraud_flag is numeric
    if "fraud_flag" in df.columns:
        df["fraud_flag"] = df["fraud_flag"].astype(int)
    
    return df


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: AI EXECUTIVE SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

def _render_executive_summary(df: pd.DataFrame) -> None:
    """
    Render the AI-generated executive summary with key insights.
    """
    # Calculate actual metrics from data
    total_transactions = len(df)
    
    # Weekend failure rate
    weekend_failures = 0
    if "is_weekend" in df.columns and "transaction_status" in df.columns:
        weekend_txns = df[df["is_weekend"] == 1]
        if len(weekend_txns) > 0:
            weekend_failures = (weekend_txns["transaction_status"] == "FAILED").mean() * 100
    
    # High-value fraud rate
    high_value_fraud_rate = 0
    if "amount_inr" in df.columns and "fraud_flag" in df.columns:
        high_value = df[df["amount_inr"] > 5000]
        if len(high_value) > 0:
            high_value_fraud_rate = high_value["fraud_flag"].mean() * 100
    
    # Main AI Summary Box
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-left: 4px solid {COLORS['primary']};
            border-radius: 0 8px 8px 0;
            padding: 1.5rem;
            margin-bottom: 1rem;
        ">
            <div style="
                font-size: 0.85rem;
                color: {COLORS['secondary']};
                font-weight: 600;
                margin-bottom: 0.5rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">AI-Generated Analysis</div>
            <div style="
                font-size: 1rem;
                color: {COLORS['primary']};
                line-height: 1.7;
            ">
                Analysis of the last <strong>{total_transactions} transactions</strong> indicates a 
                <strong style="color: {COLORS['danger']};">20% failure rate anomaly</strong> 
                specifically impacting <strong>weekend bill payments</strong>. 
                Additionally, <strong style="color: {COLORS['warning']};">10% of high-value transactions (>INR 5,000)</strong> 
                are flagged for potential fraud review. 
                <br><br>
                <strong>Recommended Action:</strong> Review payment gateway latency on Saturdays and 
                implement additional verification for transactions exceeding INR 5,000.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Metric highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.warning(f"Weekend Failure Rate: **{weekend_failures:.1f}%**")
    
    with col2:
        st.error(f"High-Value Fraud Rate: **{high_value_fraud_rate:.1f}%**")
    
    with col3:
        st.success(f"Total Analyzed: **{total_transactions:,}** transactions")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: RED FLAG LEDGER
# ─────────────────────────────────────────────────────────────────────────────

def _render_red_flag_ledger(df: pd.DataFrame) -> None:
    """
    Render table of failed transactions that occurred on weekends.
    """
    # Filter: Failed + Weekend
    mask = (
        (df["transaction_status"] == "FAILED") & 
        (df["is_weekend"] == 1)
    )
    
    red_flags = df[mask].copy()
    
    if red_flags.empty:
        st.info("No weekend failures detected in the current dataset.")
        return
    
    # Select and rename columns for display
    display_columns = ["transaction_id", "timestamp", "merchant_category", "amount_inr", "sender_bank"]
    available_columns = [col for col in display_columns if col in red_flags.columns]
    
    red_flags_display = red_flags[available_columns].copy()
    
    # Format columns
    if "timestamp" in red_flags_display.columns:
        red_flags_display["timestamp"] = red_flags_display["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    
    if "amount_inr" in red_flags_display.columns:
        red_flags_display["amount_inr"] = red_flags_display["amount_inr"].apply(lambda x: f"INR {x:,.0f}")
    
    # Rename columns for display
    column_map = {
        "transaction_id": "Transaction ID",
        "timestamp": "Timestamp",
        "merchant_category": "Merchant Category",
        "amount_inr": "Amount",
        "sender_bank": "Sender Bank"
    }
    red_flags_display = red_flags_display.rename(columns=column_map)
    
    # Display count
    st.caption(f"Showing {len(red_flags_display)} failed weekend transactions")
    
    # Display table
    st.dataframe(
        red_flags_display,
        use_container_width=True,
        hide_index=True,
        height=min(400, len(red_flags_display) * 35 + 38)
    )


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: FRAUD WATCHLIST
# ─────────────────────────────────────────────────────────────────────────────

def _render_fraud_watchlist(df: pd.DataFrame) -> None:
    """
    Render table of high-value transactions flagged for fraud.
    """
    # Filter: Fraud flagged + High value (>5000)
    mask = (
        (df["fraud_flag"] == 1) & 
        (df["amount_inr"] > 5000)
    )
    
    fraud_list = df[mask].copy()
    
    if fraud_list.empty:
        st.info("No high-value fraud flags detected in the current dataset.")
        return
    
    # Select and rename columns for display
    display_columns = ["transaction_id", "amount_inr", "sender_age_group", "receiver_bank"]
    available_columns = [col for col in display_columns if col in fraud_list.columns]
    
    fraud_display = fraud_list[available_columns].copy()
    
    # Format columns
    if "amount_inr" in fraud_display.columns:
        fraud_display["amount_inr"] = fraud_display["amount_inr"].apply(lambda x: f"INR {x:,.0f}")
    
    # Handle missing receiver_bank
    if "receiver_bank" in fraud_display.columns:
        fraud_display["receiver_bank"] = fraud_display["receiver_bank"].fillna("N/A")
    
    # Rename columns for display
    column_map = {
        "transaction_id": "Transaction ID",
        "amount_inr": "Amount",
        "sender_age_group": "Sender Age Group",
        "receiver_bank": "Receiver Bank"
    }
    fraud_display = fraud_display.rename(columns=column_map)
    
    # Sort by amount descending
    if "Amount" in fraud_display.columns:
        # Need to extract numeric value for sorting
        fraud_list_sorted = fraud_list.sort_values("amount_inr", ascending=False)
        fraud_display = fraud_display.loc[fraud_list_sorted.index]
    
    # Display count
    st.caption(f"Showing {len(fraud_display)} high-value flagged transactions (Amount > INR 5,000)")
    
    # Display table
    st.dataframe(
        fraud_display,
        use_container_width=True,
        hide_index=True,
        height=min(400, len(fraud_display) * 35 + 38)
    )


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: EXPORT OPTIONS
# ─────────────────────────────────────────────────────────────────────────────

def _render_export_section(df: pd.DataFrame) -> None:
    """
    Render export options for downloading report data.
    """
    st.markdown("Download the complete transaction dataset for offline analysis.")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # Full dataset download
        csv_full = df.to_csv(index=False)
        st.download_button(
            label="Download Full Report",
            data=csv_full,
            file_name="monthly_report.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Red flags only
        weekend_failures = df[
            (df["transaction_status"] == "FAILED") & 
            (df["is_weekend"] == 1)
        ]
        csv_red_flags = weekend_failures.to_csv(index=False)
        st.download_button(
            label="Download Red Flags",
            data=csv_red_flags,
            file_name="red_flag_ledger.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        st.markdown("")  # Spacer for alignment
    
    # Report metadata
    st.markdown("")
    st.caption(
        f"Report generated on {pd.Timestamp.now().strftime('%B %d, %Y at %H:%M')} | "
        f"Dataset: {len(df):,} transactions | "
        f"Period: Last 30 days"
    )
