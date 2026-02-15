import streamlit as st
from typing import Optional, Union


def display_insight_card(
    insight_text: str,
    metric_value: Union[str, int, float],
    metric_delta: Optional[str] = None,
    code_snippet: Optional[str] = None,
    metric_label: str = "Key Metric",
    delta_color: str = "normal"
) -> None:
    """
    Display a styled insight card with metric, summary, and optional code reveal.
    
    This component creates a card-like UI element for displaying AI-generated
    insights in a professional, executive-friendly format.
    
    Args:
        insight_text: The business summary or insight explanation.
        metric_value: The primary metric value to display prominently (e.g., "5.2%", 1234).
        metric_delta: Optional comparison text (e.g., "+2% vs Weekday", "-15% MoM").
        code_snippet: Optional Python/Pandas code that generated the insight.
        metric_label: Label for the metric (default: "Key Metric").
        delta_color: Color behavior for delta - "normal", "inverse", or "off".
                    "normal": green for positive, red for negative
                    "inverse": red for positive, green for negative
                    "off": gray for both
    
    Example:
        display_insight_card(
            insight_text="P2M transactions show elevated failure rates during peak hours.",
            metric_value="5.9%",
            metric_delta="+0.8% vs last week",
            code_snippet="df[df['transaction_type'] == 'P2M']['status'].value_counts(normalize=True)",
            metric_label="Failure Rate"
        )
    """
    
    # Use a Streamlit container with custom border styling
    with st.container(border=True):
        # Top Row: Metric display
        st.metric(
            label=metric_label,
            value=metric_value,
            delta=metric_delta,
            delta_color=delta_color
        )
        
        # Middle: Insight text
        st.markdown(
            f"""
            <div style="
                color: #334155;
                font-size: 0.95rem;
                line-height: 1.6;
                padding: 0.5rem 0;
                border-top: 1px solid #f1f5f9;
                margin-top: 0.5rem;
            ">
                {insight_text}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Bottom: Code expander (if code provided)
        if code_snippet:
            with st.expander("View Analysis Logic", expanded=False):
                st.code(code_snippet, language="python")


def display_multi_metric_card(
    insight_text: str,
    metrics: list[dict],
    code_snippet: Optional[str] = None,
    title: Optional[str] = None
) -> None:
    """
    Display an insight card with multiple metrics in a row.
    
    Args:
        insight_text: The business summary or insight explanation.
        metrics: List of metric dictionaries, each containing:
                 - "label": Metric label
                 - "value": Metric value
                 - "delta": Optional delta string
                 - "delta_color": Optional delta color ("normal", "inverse", "off")
        code_snippet: Optional Python/Pandas code that generated the insight.
        title: Optional title for the card.
    
    Example:
        display_multi_metric_card(
            insight_text="Weekend transactions show different patterns.",
            metrics=[
                {"label": "Weekday Vol", "value": "18.2", "delta": None},
                {"label": "Weekend Vol", "value": "12.8", "delta": "-30%"},
                {"label": "Avg Amount", "value": "3,120", "delta": "+27%"}
            ],
            code_snippet="df.groupby('is_weekend').agg({'amount': 'mean'})"
        )
    """
    
    # Use a Streamlit container with border
    with st.container(border=True):
        # Optional title
        if title:
            st.markdown(f"**{title}**")
        
        # Top Row: Multiple metrics
        if metrics:
            cols = st.columns(len(metrics))
            for col, metric in zip(cols, metrics):
                with col:
                    st.metric(
                        label=metric.get("label", "Metric"),
                        value=metric.get("value", "N/A"),
                        delta=metric.get("delta"),
                        delta_color=metric.get("delta_color", "normal")
                    )
        
        # Middle: Insight text
        st.markdown(
            f"""
            <div style="
                color: #334155;
                font-size: 0.95rem;
                line-height: 1.6;
                padding: 0.5rem 0;
                border-top: 1px solid #f1f5f9;
                margin-top: 0.5rem;
            ">
                {insight_text}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Bottom: Code expander
        if code_snippet:
            with st.expander("View Analysis Logic", expanded=False):
                st.code(code_snippet, language="python")


def display_alert_card(
    alert_text: str,
    severity: str = "info",
    metric_value: Optional[Union[str, int, float]] = None,
    metric_label: Optional[str] = None,
    action_text: Optional[str] = None
) -> None:
    """
    Display a proactive alert/insight card with severity styling.
    
    Args:
        alert_text: The alert message or proactive insight.
        severity: Alert severity - "info", "warning", "error", or "success".
        metric_value: Optional metric value associated with the alert.
        metric_label: Optional label for the metric.
        action_text: Optional recommended action text.
    
    Example:
        display_alert_card(
            alert_text="Unusual spike in failed transactions detected",
            severity="warning",
            metric_value="12.3%",
            metric_label="Failure Rate",
            action_text="Review recent P2M transactions"
        )
    """
    
    # Severity color mapping
    severity_styles = {
        "info": {
            "border_color": "#3b82f6",
            "bg_color": "#eff6ff",
            "text_color": "#1e40af",
            "icon": "Info"
        },
        "warning": {
            "border_color": "#f59e0b",
            "bg_color": "#fffbeb",
            "text_color": "#92400e",
            "icon": "Warning"
        },
        "error": {
            "border_color": "#ef4444",
            "bg_color": "#fef2f2",
            "text_color": "#991b1b",
            "icon": "Alert"
        },
        "success": {
            "border_color": "#10b981",
            "bg_color": "#ecfdf5",
            "text_color": "#065f46",
            "icon": "Success"
        }
    }
    
    style = severity_styles.get(severity, severity_styles["info"])
    
    # Alert card container
    st.markdown(
        f"""
        <div style="
            background-color: {style['bg_color']};
            border-left: 4px solid {style['border_color']};
            border-radius: 0 0.5rem 0.5rem 0;
            padding: 1rem 1.25rem;
            margin: 0.75rem 0;
        ">
            <div style="
                font-size: 0.75rem;
                font-weight: 600;
                color: {style['text_color']};
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.5rem;
            ">
                {style['icon']}
            </div>
            <div style="
                color: {style['text_color']};
                font-size: 0.925rem;
                line-height: 1.5;
            ">
                {alert_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Optional metric and action in columns
    if metric_value or action_text:
        col1, col2 = st.columns(2)
        
        if metric_value and metric_label:
            with col1:
                st.metric(label=metric_label, value=metric_value)
        
        if action_text:
            with col2:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #f8fafc;
                        border-radius: 0.375rem;
                        padding: 0.75rem;
                        margin-top: 0.5rem;
                    ">
                        <div style="color: #64748b; font-size: 0.75rem; margin-bottom: 0.25rem;">
                            Recommended Action
                        </div>
                        <div style="color: #334155; font-size: 0.875rem; font-weight: 500;">
                            {action_text}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
