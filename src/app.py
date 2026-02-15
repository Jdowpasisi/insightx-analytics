# ============================================================================
# PATH SETUP - Must be FIRST before any other imports
# ============================================================================
import sys
import os
from pathlib import Path

# Get the directory containing this file (src/)
_THIS_DIR = Path(__file__).parent.absolute()

# Add src/ to Python path if not already present (for imports like 'from utils.x')
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

# Change working directory to project root for relative file access
_PROJECT_ROOT = _THIS_DIR.parent
os.chdir(_PROJECT_ROOT)

# ============================================================================
# STANDARD IMPORTS
# ============================================================================
import streamlit as st
import time
import uuid
import pandas as pd
from typing import Dict, Any, Optional

# ============================================================================
# LOCAL IMPORTS (now work because src/ is in sys.path)
# ============================================================================
_STYLES_LOADED = False
_IMPORT_ERROR = None

try:
    from utils.styles import apply_custom_styles
    _STYLES_LOADED = True
except ImportError as e:
    _IMPORT_ERROR = str(e)
    # Fallback: define inline styles if import fails
    def apply_custom_styles():
        """Fallback inline CSS if styles.py import fails."""
        st.markdown("""
        <style>
            /* CRITICAL SELECTBOX FIX - Fallback CSS */
            [data-baseweb="select"] * {
                color: #1e3a5f !important;
                -webkit-text-fill-color: #1e3a5f !important;
            }
            [data-baseweb="select"] div[value] {
                color: #1e3a5f !important;
                -webkit-text-fill-color: #1e3a5f !important;
                opacity: 1 !important;
                visibility: visible !important;
            }
            [data-testid="stSidebar"] .stSelectbox *,
            [data-testid="stSidebar"] [data-baseweb="select"] * {
                color: #1e3a5f !important;
                -webkit-text-fill-color: #1e3a5f !important;
            }
        </style>
        """, unsafe_allow_html=True)
        print(f"⚠️  Using fallback CSS (import failed: {_IMPORT_ERROR})")

from components.sidebar import render_sidebar
from components.alert_banner import render_alert_banner, AlertSeverity
from components.insight_card import display_insight_card, display_multi_metric_card
from components.analytics import render_analytics
from components.dashboard import render_dashboard
from components.reports import render_reports
from pages.chat_history import render_chat_history


def handle_quick_analysis(query_key: str) -> None:
    """
    Handle quick analysis button clicks from the sidebar.
    
    Args:
        query_key: The identifier for the triggered query.
    """
    # Map query keys to natural language questions
    query_map = {
        "failure_rates": "What are the current transaction failure rates by payment type?",
        "weekend_trends": "Show me the weekend vs weekday volume trends.",
        "high_value_anomalies": "Identify any high-value transaction anomalies flagged for review."
    }
    
    query_text = query_map.get(query_key, f"Analyze {query_key}")
    
    # Add the query to messages as if the user typed it
    st.session_state.messages.append({
        "role": "user",
        "content": query_text
    })
    
    print(f"[InsightX] Quick Analysis triggered: {query_key}")


def handle_alert_investigation() -> None:
    """Handle the alert investigation button click."""
    # Add investigation query to chat
    investigation_query = "Analyze the high failure rate in Bill Payment category for the last 2 hours."
    st.session_state.messages.append({
        "role": "user",
        "content": investigation_query
    })
    st.session_state.alert_investigated = True
    print("[InsightX] Alert investigation triggered")


def init_session_state() -> None:
    """Initialize session state variables."""
    if "pending_query" not in st.session_state:
        st.session_state["pending_query"] = None
    if "processing" not in st.session_state:
        st.session_state["processing"] = False
    if "alert_investigated" not in st.session_state:
        st.session_state["alert_investigated"] = False
    if "show_system_alert" not in st.session_state:
        st.session_state["show_system_alert"] = True
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "app"
    if "df" not in st.session_state:
        st.session_state["df"] = None
    
    # Multi-session chat management
    if "sessions" not in st.session_state:
        # Pre-fill with one mock session
        mock_session_id = str(uuid.uuid4())
        st.session_state["sessions"] = {
            mock_session_id: {
                "title": "Previous Analysis: Weekend Failures",
                "messages": [
                    {"role": "user", "content": "What are the weekend failure rates?"},
                    {
                        "role": "assistant",
                        "content": "Weekend failure rates are approximately 4.2% higher than weekday rates. Bill Payment shows the highest spike on Saturdays at 8.7% failure rate.",
                        "response_data": {
                            "type": "insight_card",
                            "answer": "Weekend failure rates are approximately 4.2% higher than weekday rates.",
                            "metric_value": "4.2%",
                            "metric_label": "Weekend Variance",
                            "insight": "Bill Payment shows the highest spike on Saturdays at 8.7% failure rate."
                        }
                    }
                ]
            }
        }
        st.session_state["active_session_id"] = mock_session_id
    
    if "active_session_id" not in st.session_state:
        # If sessions exist but no active, pick the first one
        if st.session_state["sessions"]:
            st.session_state["active_session_id"] = list(st.session_state["sessions"].keys())[0]
        else:
            # Create a new empty session
            new_id = str(uuid.uuid4())
            st.session_state["sessions"][new_id] = {"title": "New Chat", "messages": []}
            st.session_state["active_session_id"] = new_id
    
    # Legacy support: keep messages pointing to active session
    if "messages" not in st.session_state:
        st.session_state["messages"] = []


@st.cache_data
def load_transaction_data() -> pd.DataFrame:
    """
    Load the mock transaction dataset.
    Uses st.cache_data to avoid reloading on every rerun.
    
    Returns:
        DataFrame containing transaction data.
    """
    try:
        df = pd.read_csv("data/transactions.csv")
        return df
    except FileNotFoundError:
        st.error("Transaction data file not found at 'data/transactions.csv'")
        return pd.DataFrame()


def get_mock_response(user_message: str) -> Dict[str, Any]:
    """
    Generate a mock AI response based on user input (Wizard of Oz pattern).
    
    Args:
        user_message: The user's query.
    
    Returns:
        Dictionary containing:
        - type: Response type ('insight_card', 'multi_metric', 'text')
        - answer: Main answer text
        - metric_value: Primary metric (optional)
        - metric_label: Label for the metric (optional)
        - delta: Comparison string (optional)
        - insight: Key insight text (optional)
        - code: Python/Pandas code used (optional)
        - metrics: List of metrics for multi-metric cards (optional)
    """
    message_lower = user_message.lower()
    
    # Pattern: "fail" keyword - Failure rate analysis
    if "fail" in message_lower:
        return {
            "type": "insight_card",
            "answer": "The failure rate for Bill Payments is 8.2%.",
            "metric_value": "8.2%",
            "metric_label": "Failure Rate",
            "delta": "+3% vs Avg",
            "insight": "High timeouts detected in HDFC Bank gateway. Bill Payment transactions show elevated failure rates, particularly during peak hours (2-4 PM). The primary error code is GATEWAY_TIMEOUT, suggesting infrastructure issues rather than user errors.",
            "code": "df[df['transaction_status']=='FAILED'].groupby('transaction_type').size() / df.groupby('transaction_type').size() * 100"
        }
    
    # Pattern: "volume" keyword - Volume analysis
    elif "volume" in message_lower:
        return {
            "type": "multi_metric",
            "answer": "Transaction volume analysis across different time periods.",
            "title": "Volume Analysis",
            "metrics": [
                {"label": "Daily Avg", "value": "16.7", "delta": None},
                {"label": "Weekend", "value": "12.8", "delta": "-23%"},
                {"label": "Weekday", "value": "18.2", "delta": "+9%"}
            ],
            "insight": "Weekend transaction volume is 23% lower than weekdays, but average transaction value is 27% higher. This suggests users make fewer but larger transactions on weekends.",
            "code": "df.groupby('is_weekend').agg({'transaction_id': 'count', 'amount_inr': 'mean'})"
        }
    
    # Pattern: "weekend" keyword - Weekend trends
    elif "weekend" in message_lower or "weekday" in message_lower:
        return {
            "type": "multi_metric",
            "answer": "Weekend vs Weekday comparison shows distinct patterns.",
            "title": "Weekend vs Weekday Trends",
            "metrics": [
                {"label": "Weekday Vol", "value": "18.2", "delta": None},
                {"label": "Weekend Vol", "value": "12.8", "delta": "-30%"},
                {"label": "Weekend AOV", "value": "INR 3,120", "delta": "+27%"}
            ],
            "insight": "Weekend transactions show 30% lower volume but 27% higher average order value. P2P dominates weekends while P2M peaks on weekdays.",
            "code": "df.pivot_table(index='is_weekend', values=['amount_inr', 'transaction_id'], aggfunc={'amount_inr': 'mean', 'transaction_id': 'count'})"
        }
    
    # Pattern: "anomal", "high-value", "fraud" keywords
    elif "anomal" in message_lower or "high-value" in message_lower or "fraud" in message_lower:
        return {
            "type": "insight_card",
            "answer": "Found 10 transactions flagged for review (2% of dataset).",
            "metric_value": "10",
            "metric_label": "Flagged Transactions",
            "delta": "2% of total",
            "insight": "70% of flagged transactions occurred during non-business hours (10 PM - 6 AM). 60% involved new sender-receiver pairs. Average flagged amount is 8x higher than normal transactions. Recommend manual review of 3 high-risk cases.",
            "code": "df[df['fraud_flag']==1].groupby(['hour_of_day', 'transaction_type']).agg({'amount_inr': ['mean', 'count']})"
        }
    
    # Pattern: Bill payment investigation
    elif "bill payment" in message_lower and ("last 2 hours" in message_lower or "investigate" in message_lower):
        return {
            "type": "insight_card",
            "answer": "Bill Payment failure spike detected - root cause identified.",
            "metric_value": "25%",
            "metric_label": "Current Hour Failure Rate",
            "delta": "+20% vs normal",
            "insight": "83% of failures originate from a single biller: 'State Electricity Board'. Error code BILLER_TIMEOUT accounts for all failures. Issue began at 14:32 UTC. This appears to be an external dependency issue - recommend contacting biller integration team.",
            "code": "df[(df['transaction_type']=='Bill Payment') & (df['timestamp'] > now - 2h)].groupby(['merchant_category', 'transaction_status']).size()"
        }
    
    # Default response - generic analysis
    else:
        return {
            "type": "text",
            "answer": f"I am analyzing the dataset based on your query: '{user_message}'",
            "insight": "This is a simulated response. Try asking about 'failure rates', 'volume trends', 'weekend patterns', or 'high-value anomalies' to see the full insight card UI.",
            "code": None
        }


def render_response(response: Dict[str, Any]) -> None:
    """
    Render an AI response using appropriate UI components.
    
    Args:
        response: Dictionary containing response data from get_mock_response().
    """
    response_type = response.get("type", "text")
    
    if response_type == "insight_card":
        # Use the insight card component
        st.markdown(response.get("answer", ""))
        display_insight_card(
            insight_text=response.get("insight", ""),
            metric_value=response.get("metric_value", "N/A"),
            metric_delta=response.get("delta"),
            code_snippet=response.get("code"),
            metric_label=response.get("metric_label", "Key Metric")
        )
    
    elif response_type == "multi_metric":
        # Use the multi-metric card component
        st.markdown(response.get("answer", ""))
        display_multi_metric_card(
            insight_text=response.get("insight", ""),
            metrics=response.get("metrics", []),
            code_snippet=response.get("code"),
            title=response.get("title")
        )
    
    else:
        # Default text response
        st.markdown(response.get("answer", ""))
        if response.get("insight"):
            st.markdown(f"\n{response.get('insight')}")
        if response.get("code"):
            with st.expander("View Analysis Logic", expanded=False):
                st.code(response.get("code"), language="python")


def format_response_for_history(response: Dict[str, Any]) -> str:
    """
    Format a response dictionary as a string for chat history storage.
    
    Args:
        response: Dictionary containing response data.
    
    Returns:
        Formatted string representation of the response.
    """
    parts = [response.get("answer", "")]
    
    if response.get("metric_value"):
        metric_str = f"**{response.get('metric_label', 'Metric')}:** {response.get('metric_value')}"
        if response.get("delta"):
            metric_str += f" ({response.get('delta')})"
        parts.append(metric_str)
    
    if response.get("insight"):
        parts.append(f"**Insight:** {response.get('insight')}")
    
    return "\n\n".join(parts)


def render_chat_interface() -> None:
    """Render the chat interface with conditional layout based on chat state."""
    
    # Get current session messages
    active_id = st.session_state.get("active_session_id")
    sessions = st.session_state.get("sessions", {})
    
    if active_id and active_id in sessions:
        current_messages = sessions[active_id].get("messages", [])
    else:
        current_messages = []
    
    # Check if chat is empty (Empty State vs Active State)
    is_empty_state = len(current_messages) == 0
    
    if is_empty_state:
        # EMPTY STATE: Hero section with centered layout
        _render_empty_state()
    else:
        # ACTIVE STATE: Normal chat history
        _render_active_state(current_messages)


def _render_empty_state() -> None:
    """Render the hero section when no messages exist."""
    st.markdown("")
    st.markdown("")
    
    # Centered hero title
    st.markdown(
        "<h2 style='text-align: center; color: #1e3a5f; margin-bottom: 2rem;'>"
        "How can I help you analyze the data?"
        "</h2>",
        unsafe_allow_html=True
    )
    
    # Suggestion buttons in 3-column layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Weekend Failure Rate", key="hero_weekend", use_container_width=True):
            _handle_suggestion_click("What are the weekend failure rates compared to weekdays?")
    
    with col2:
        if st.button("High Value Fraud", key="hero_fraud", use_container_width=True):
            _handle_suggestion_click("Show me high-value transactions flagged for fraud.")
    
    with col3:
        if st.button("Weekly Volume", key="hero_volume", use_container_width=True):
            _handle_suggestion_click("What is the weekly transaction volume trend?")
    
    st.markdown("")
    st.markdown("---")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about transaction data..."):
        _process_user_query(prompt)


def _render_active_state(messages: list) -> None:
    """Render the chat history with header row and popover suggestions."""
    # Header row with title and popover
    header_col1, header_col2 = st.columns([4, 1])
    
    with header_col1:
        st.markdown("### Current Session")
    
    with header_col2:
        with st.popover("Suggestions"):
            if st.button("Weekend Failure Rate", key="pop_weekend", use_container_width=True):
                _handle_suggestion_click("What are the weekend failure rates compared to weekdays?")
            if st.button("High Value Fraud", key="pop_fraud", use_container_width=True):
                _handle_suggestion_click("Show me high-value transactions flagged for fraud.")
            if st.button("Weekly Volume", key="pop_volume", use_container_width=True):
                _handle_suggestion_click("What is the weekly transaction volume trend?")
    
    # Display chat history
    for message in messages:
        avatar = "user" if message["role"] == "user" else "assistant"
        with st.chat_message(message["role"], avatar=avatar):
            if isinstance(message.get("response_data"), dict):
                render_response(message["response_data"])
            else:
                st.markdown(message["content"])
    
    # Chat input at the bottom
    if prompt := st.chat_input("Ask a question about transaction data..."):
        _process_user_query(prompt)


def _handle_suggestion_click(query: str) -> None:
    """Handle suggestion chip click by adding query to active session."""
    active_id = st.session_state.get("active_session_id")
    if active_id and active_id in st.session_state.sessions:
        st.session_state.sessions[active_id]["messages"].append({
            "role": "user",
            "content": query
        })
        # Update session title if it's the first message
        if len(st.session_state.sessions[active_id]["messages"]) == 1:
            # Use first few words as title
            st.session_state.sessions[active_id]["title"] = query[:30] + "..." if len(query) > 30 else query
    st.rerun()


def _process_user_query(prompt: str) -> None:
    """Process a user query and generate response."""
    active_id = st.session_state.get("active_session_id")
    if not active_id or active_id not in st.session_state.sessions:
        return
    
    session = st.session_state.sessions[active_id]
    
    # Update session title if this is the first message
    if len(session["messages"]) == 0:
        session["title"] = prompt[:30] + "..." if len(prompt) > 30 else prompt
    
    # Add user message to session
    session["messages"].append({
        "role": "user",
        "content": prompt
    })
    
    # Display user message immediately
    with st.chat_message("user", avatar="user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant", avatar="assistant"):
        # Show thinking spinner
        with st.spinner("Analyzing dataset..."):
            time.sleep(1.5)  # Simulate processing time
            response = get_mock_response(prompt)
        
        # Render using appropriate component
        render_response(response)
    
    # Add assistant response to session
    session["messages"].append({
        "role": "assistant",
        "content": format_response_for_history(response),
        "response_data": response
    })
    
    # Rerun to update the UI
    st.rerun()


def render_metric_cards(sidebar_state: dict) -> None:
    """
    Render the metric cards at the top of the main content area.
    
    Args:
        sidebar_state: Dictionary containing sidebar state including selected_persona.
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div style="
                background-color: #f8fafc;
                border-radius: 0.5rem;
                padding: 1rem;
                text-align: center;
                border: 1px solid #e2e8f0;
            ">
                <div style="color: #64748b; font-size: 0.875rem;">Current Persona</div>
                <div style="color: #1e293b; font-size: 1.25rem; font-weight: 600;">
                    {sidebar_state['selected_persona']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            """
            <div style="
                background-color: #f8fafc;
                border-radius: 0.5rem;
                padding: 1rem;
                text-align: center;
                border: 1px solid #e2e8f0;
            ">
                <div style="color: #64748b; font-size: 0.875rem;">Total Transactions</div>
                <div style="color: #1e293b; font-size: 1.25rem; font-weight: 600;">500</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            """
            <div style="
                background-color: #f8fafc;
                border-radius: 0.5rem;
                padding: 1rem;
                text-align: center;
                border: 1px solid #e2e8f0;
            ">
                <div style="color: #64748b; font-size: 0.875rem;">System Status</div>
                <div style="color: #10b981; font-size: 1.25rem; font-weight: 600;">Online</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="InsightX Analytics",
        page_icon="chart_with_upwards_trend",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom styling
    apply_custom_styles()
    
    # Initialize session state
    init_session_state()
    
    # Load transaction data
    df = load_transaction_data()
    
    # Render sidebar and get state
    sidebar_state = render_sidebar(on_query_click=handle_quick_analysis)
    
    # Route based on current_page
    current_page = st.session_state.current_page
    
    if current_page == "app":
        # Main dashboard content
        _render_main_dashboard(sidebar_state)
    elif current_page == "analytics":
        # Render analytics page with dataframe
        render_analytics(df)
    elif current_page == "dashboard":
        # Render executive dashboard with dataframe
        render_dashboard(df)
    elif current_page == "reports":
        # Render executive reports page with dataframe
        render_reports(df)
    elif current_page == "chat_history":
        # Render chat history page
        render_chat_history()
    else:
        _render_main_dashboard(sidebar_state)


def _render_main_dashboard(sidebar_state: dict):
    """Render the main dashboard content."""
    # Main content area
    st.markdown("## InsightX Leadership Analytics")
    st.markdown("Ask questions about your payment transaction data using natural language.")
    
    st.markdown("---")
    
    # Render system alert banner FIRST (above everything else)
    # Only show if not already investigated
    alert_active = st.session_state.show_system_alert and not st.session_state.alert_investigated
    
    if render_alert_banner(
        alert_active=alert_active,
        alert_message="System Notice: High failure rate detected in 'Bill Payment' category (Last 2 hours).",
        severity=AlertSeverity.WARNING,
        action_label="Investigate",
        on_action_click=handle_alert_investigation
    ):
        # Alert was clicked, rerun to show the investigation in chat
        st.rerun()
    
    # Render metric cards
    render_metric_cards(sidebar_state)
    
    st.markdown("---")
    
    # Render chat interface
    render_chat_interface()


# Always call main() - works for both local run and Streamlit Cloud
main()