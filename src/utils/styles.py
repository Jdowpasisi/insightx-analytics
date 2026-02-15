"""
Minimal CSS styles for InsightX - based on working test_selectbox_minimal.py
"""
import streamlit as st


def apply_custom_styles():
    """Apply custom CSS styles."""
    st.markdown("""
    <style>
        /* Hide deploy button */
        .stDeployButton {display: none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Basic theme colors */
        :root {
            --primary-color: #1e3a5f;
        }
        
        /* SELECTBOX FIX - Exact copy from test_selectbox_minimal.py */
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
        
        div[class*="st-bn"],
        div[class*="st-al"],
        div[class*="st-bo"] {
            color: #1e3a5f !important;
            -webkit-text-fill-color: #1e3a5f !important;
        }
        
        [data-testid="stSidebar"] .stSelectbox *,
        [data-testid="stSidebar"] [data-baseweb="select"] * {
            color: #1e3a5f !important;
            -webkit-text-fill-color: #1e3a5f !important;
        }
        
        /* Dropdown menu */
        [data-baseweb="menu"] * {
            color: #1e3a5f !important;
            -webkit-text-fill-color: #1e3a5f !important;
        }
        
        /* SIDEBAR STYLING */
        
        /* Reduce top padding in sidebar */
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 0.25rem !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        
        /* Tighter heading spacing */
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] h5 {
            margin-top: 0 !important;
            margin-bottom: 0.25rem !important;
        }
        
        /* Left align all sidebar content */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            align-items: flex-start !important;
        }
        
        [data-testid="stSidebar"] .stMarkdown {
            text-align: left !important;
        }
        
        /* Selected chat session - light background (#F8FAFC) with midnight blue border */
        [data-testid="stSidebar"] .stButton button[kind="primary"],
        [data-testid="stSidebar"] .stButton button[data-testid="baseButton-primary"] {
            background-color: #F8FAFC !important;
            color: #1e3a5f !important;
            border: 1px solid #1e3a5f !important;
        }
        
        /* Secondary buttons in sidebar - transparent */
        [data-testid="stSidebar"] .stButton button[kind="secondary"],
        [data-testid="stSidebar"] .stButton button[data-testid="baseButton-secondary"] {
            background-color: transparent !important;
            color: #1e3a5f !important;
            border: 1px solid transparent !important;
        }
        
        [data-testid="stSidebar"] .stButton button[kind="secondary"]:hover,
        [data-testid="stSidebar"] .stButton button[data-testid="baseButton-secondary"]:hover {
            background-color: #f1f5f9 !important;
            border: 1px solid #e2e8f0 !important;
        }
        
        /* Popover trigger button (⋯ menu) - no border, compact */
        [data-testid="stSidebar"] .stPopover > div:first-child button {
            min-width: 32px !important;
            width: 32px !important;
            height: 32px !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 16px !important;
            border: none !important;
            background-color: transparent !important;
        }
        
        [data-testid="stSidebar"] .stPopover > div:first-child button:hover {
            background-color: #f1f5f9 !important;
        }
        
        /* Hide popover arrow */
        [data-testid="stPopover"] [data-popper-arrow],
        .stPopover [data-popper-arrow],
        [data-baseweb="popover"] [data-popper-arrow] {
            display: none !important;
        }
        
        /* Narrow popover content */
        [data-testid="stPopoverBody"] {
            padding: 4px !important;
            min-width: 60px !important;
            width: auto !important;
        }
        
        [data-baseweb="popover"] > div {
            min-width: 60px !important;
        }
        
        /* Popover content styling */
        [data-testid="stPopoverBody"] {
            padding: 0.5rem !important;
        }
        
        /* Sidebar popover (Delete button) - red */
        [data-testid="stSidebar"] [data-testid="stPopoverBody"] .stButton button {
            color: #ef4444 !important;
            background-color: transparent !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stPopoverBody"] .stButton button:hover {
            background-color: #fef2f2 !important;
        }
        
        /* Main content popover (Suggestions) - primary color */
        [data-testid="stMain"] [data-testid="stPopoverBody"] .stButton button,
        [data-testid="stAppViewContainer"] > div:not([data-testid="stSidebar"]) [data-testid="stPopoverBody"] .stButton button {
            color: #1e3a5f !important;
            background-color: transparent !important;
        }
        
        [data-testid="stMain"] [data-testid="stPopoverBody"] .stButton button:hover,
        [data-testid="stAppViewContainer"] > div:not([data-testid="stSidebar"]) [data-testid="stPopoverBody"] .stButton button:hover {
            background-color: #f1f5f9 !important;
        }
        
        /* Tighter spacing for chat session rows in sidebar */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }
        
        [data-testid="stSidebar"] .stButton {
            margin-bottom: 0 !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
            gap: 0 !important;
            margin-bottom: 0 !important;
        }
        
        /* Reduce gap between columns in session rows */
        [data-testid="stSidebar"] [data-testid="column"] {
            padding: 0 !important;
        }
        
        /* Show more link styling */
        [data-testid="stSidebar"] button[kind="tertiary"],
        [data-testid="stSidebar"] button[data-testid="baseButton-tertiary"] {
            background-color: transparent !important;
            color: #64748b !important;
            font-size: 13px !important;
            padding: 4px 8px !important;
            border: none !important;
        }
        
        [data-testid="stSidebar"] button[kind="tertiary"]:hover,
        [data-testid="stSidebar"] button[data-testid="baseButton-tertiary"]:hover {
            color: #1e3a5f !important;
            text-decoration: underline !important;
        }
    </style>
    """, unsafe_allow_html=True)
