import streamlit as st
from typing import Optional, Callable, List
from dataclasses import dataclass
from enum import Enum


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SUCCESS = "success"


@dataclass
class SystemAlert:
    """Data class representing a system alert."""
    message: str
    severity: AlertSeverity
    category: Optional[str] = None
    action_label: Optional[str] = None
    action_key: Optional[str] = None


# Severity style configurations
SEVERITY_STYLES = {
    AlertSeverity.INFO: {
        "bg_color": "#eff6ff",
        "border_color": "#3b82f6",
        "text_color": "#1e40af",
        "icon": "ℹ"  # Using simple character, not emoji
    },
    AlertSeverity.WARNING: {
        "bg_color": "#fff7ed",
        "border_color": "#f97316",
        "text_color": "#9a3412",
        "icon": "!"
    },
    AlertSeverity.CRITICAL: {
        "bg_color": "#fef2f2",
        "border_color": "#ef4444",
        "text_color": "#991b1b",
        "icon": "!!"
    },
    AlertSeverity.SUCCESS: {
        "bg_color": "#ecfdf5",
        "border_color": "#10b981",
        "text_color": "#065f46",
        "icon": "✓"
    }
}


def render_alert_banner(
    alert_active: bool = True,
    alert_message: str = "System Notice: High failure rate detected in 'Bill Payment' category (Last 2 hours).",
    severity: AlertSeverity = AlertSeverity.WARNING,
    action_label: str = "Investigate",
    on_action_click: Optional[Callable[[], None]] = None
) -> bool:
    """
    Render a system alert banner at the top of the main content area.
    
    Args:
        alert_active: Whether the alert should be displayed.
        alert_message: The alert message to display.
        severity: Alert severity level (INFO, WARNING, CRITICAL, SUCCESS).
        action_label: Label for the action button.
        on_action_click: Optional callback function when action button is clicked.
    
    Returns:
        bool: True if the action button was clicked, False otherwise.
    
    Example:
        if render_alert_banner(
            alert_active=True,
            alert_message="High failure rate detected",
            severity=AlertSeverity.WARNING,
            action_label="Investigate"
        ):
            st.session_state.pending_investigation = True
    """
    action_clicked = False
    
    if not alert_active:
        return action_clicked
    
    style = SEVERITY_STYLES.get(severity, SEVERITY_STYLES[AlertSeverity.WARNING])
    
    # Create the alert container
    alert_container = st.container()
    
    with alert_container:
        # Use columns for layout: message | action button
        col_icon, col_message, col_action = st.columns([0.5, 8, 1.5])
        
        with col_icon:
            st.markdown(
                f"""
                <div style="
                    background-color: {style['border_color']};
                    color: white;
                    width: 28px;
                    height: 28px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 700;
                    font-size: 0.875rem;
                    margin-top: 0.25rem;
                ">
                    {style['icon']}
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col_message:
            st.markdown(
                f"""
                <div style="
                    background-color: {style['bg_color']};
                    border-left: 4px solid {style['border_color']};
                    border-radius: 0 0.5rem 0.5rem 0;
                    padding: 0.75rem 1rem;
                    color: {style['text_color']};
                    font-size: 0.9rem;
                    font-weight: 500;
                    line-height: 1.5;
                ">
                    {alert_message}
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col_action:
            if st.button(action_label, key="alert_action_btn", type="primary"):
                action_clicked = True
                if on_action_click:
                    on_action_click()
        
        # Add spacing after the alert
        st.markdown("")
    
    return action_clicked


def render_multi_alert_banner(
    alerts: List[SystemAlert],
    on_action_click: Optional[Callable[[str], None]] = None,
    max_visible: int = 3
) -> Optional[str]:
    """
    Render multiple system alerts in a stacked banner format.
    
    Args:
        alerts: List of SystemAlert objects to display.
        on_action_click: Optional callback with action_key parameter.
        max_visible: Maximum number of alerts to show (others collapsed).
    
    Returns:
        The action_key of the clicked alert button, or None.
    """
    if not alerts:
        return None
    
    clicked_action = None
    visible_alerts = alerts[:max_visible]
    hidden_count = len(alerts) - max_visible
    
    for idx, alert in enumerate(visible_alerts):
        style = SEVERITY_STYLES.get(alert.severity, SEVERITY_STYLES[AlertSeverity.WARNING])
        
        col_message, col_action = st.columns([9, 1])
        
        with col_message:
            st.markdown(
                f"""
                <div style="
                    background-color: {style['bg_color']};
                    border-left: 4px solid {style['border_color']};
                    border-radius: 0 0.5rem 0.5rem 0;
                    padding: 0.6rem 1rem;
                    color: {style['text_color']};
                    font-size: 0.85rem;
                    font-weight: 500;
                    margin-bottom: 0.5rem;
                ">
                    <span style="font-weight: 600;">[{alert.category or 'System'}]</span> {alert.message}
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col_action:
            if alert.action_label:
                if st.button(
                    alert.action_label,
                    key=f"alert_btn_{idx}_{alert.action_key or idx}",
                    type="secondary"
                ):
                    clicked_action = alert.action_key
                    if on_action_click:
                        on_action_click(alert.action_key)
    
    # Show hidden alerts count
    if hidden_count > 0:
        st.markdown(
            f"""
            <div style="
                color: #64748b;
                font-size: 0.8rem;
                padding: 0.25rem 0;
                text-align: center;
            ">
                +{hidden_count} more alert{'s' if hidden_count > 1 else ''} 
            </div>
            """,
            unsafe_allow_html=True
        )
        
        with st.expander("View all alerts"):
            for idx, alert in enumerate(alerts[max_visible:], start=max_visible):
                style = SEVERITY_STYLES.get(alert.severity, SEVERITY_STYLES[AlertSeverity.WARNING])
                st.markdown(
                    f"""
                    <div style="
                        border-left: 3px solid {style['border_color']};
                        padding: 0.5rem 0.75rem;
                        margin-bottom: 0.5rem;
                        font-size: 0.8rem;
                        color: {style['text_color']};
                    ">
                        <strong>[{alert.category or 'System'}]</strong> {alert.message}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    return clicked_action


def get_mock_system_alerts() -> List[SystemAlert]:
    """
    Generate mock system alerts for demonstration purposes.
    
    Returns:
        List of SystemAlert objects.
    """
    return [
        SystemAlert(
            message="High failure rate detected in 'Bill Payment' category (Last 2 hours).",
            severity=AlertSeverity.WARNING,
            category="Transactions",
            action_label="Investigate",
            action_key="bill_payment_failure"
        ),
        SystemAlert(
            message="3 high-value transactions flagged for review.",
            severity=AlertSeverity.CRITICAL,
            category="Risk",
            action_label="Review",
            action_key="high_value_review"
        ),
        SystemAlert(
            message="Weekend transaction volume 15% below forecast.",
            severity=AlertSeverity.INFO,
            category="Analytics",
            action_label="Details",
            action_key="weekend_volume"
        )
    ]

