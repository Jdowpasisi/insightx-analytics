"""
Sidebar component for InsightX - Clean implementation.
"""
import streamlit as st
import uuid
from typing import Optional, Callable


def render_sidebar(on_query_click: Optional[Callable[[str], None]] = None) -> dict:
    """Render the InsightX sidebar."""
    sidebar_state = {
        "selected_persona": None,
        "triggered_query": None,
        "selected_page": None
    }
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "app"
    
    with st.sidebar:
        # HEADER
        st.markdown("### InsightX Assistant")
        
        # NEW CHAT BUTTON
        if st.button("+ New Chat", use_container_width=True, key="new_chat_btn"):
            _create_new_session()
            st.rerun()
        
        # SESSION LIST
        st.markdown("##### Chat Sessions")
        _render_session_list()
        
        st.markdown("")
        
        # TOOLS NAVIGATION (Dashboard first, then Analytics)
        st.markdown("##### Tools")
        if st.button("Dashboard", use_container_width=True, key="nav_dashboard"):
            st.session_state.current_page = "dashboard"
        if st.button("Analytics", use_container_width=True, key="nav_analytics"):
            st.session_state.current_page = "analytics"
        if st.button("Reports", use_container_width=True, key="nav_reports"):
            st.session_state.current_page = "reports"
        
        sidebar_state["selected_page"] = st.session_state.current_page
        
        st.markdown("")
        
        # PERSONA SELECTOR - Persists across session switches
        personas = ["CEO", "Product Manager", "Engineering Lead"]
        
        # Initialize persona in session state if not set
        if "selected_persona" not in st.session_state:
            st.session_state.selected_persona = personas[0]
        
        # Get index of current persona
        current_index = personas.index(st.session_state.selected_persona) if st.session_state.selected_persona in personas else 0
        
        selected_persona = st.selectbox(
            "Viewing as:",
            personas,
            index=current_index,
            key="persona_selector"
        )
        st.session_state.selected_persona = selected_persona
        sidebar_state["selected_persona"] = selected_persona
    
    return sidebar_state


def _create_new_session() -> str:
    """Create a new chat session."""
    new_id = str(uuid.uuid4())
    
    if "sessions" not in st.session_state:
        st.session_state.sessions = {}
    
    st.session_state.sessions[new_id] = {
        "title": "New Chat",
        "messages": []
    }
    st.session_state.active_session_id = new_id
    st.session_state.current_page = "app"
    return new_id


def _render_session_list() -> None:
    """Render the list of chat sessions (last 3 only)."""
    sessions = st.session_state.get("sessions", {})
    active_id = st.session_state.get("active_session_id", None)
    
    if not sessions:
        st.caption("No sessions yet")
        return
    
    # Get sessions in reverse order (newest first) and limit to 3
    session_items = list(reversed(list(sessions.items())))
    display_sessions = session_items[:3]
    total_sessions = len(session_items)
    
    for session_id, session_data in display_sessions:
        title = session_data.get("title", "Untitled")
        is_active = session_id == active_id
        
        col1, col2 = st.columns([4, 1], vertical_alignment="center")
        
        with col1:
            if st.button(
                title,
                key=f"session_{session_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.active_session_id = session_id
                st.session_state.current_page = "app"
                st.rerun()
        
        with col2:
            with st.popover("⋯"):
                if st.button("Delete", key=f"del_{session_id}", use_container_width=True):
                    _delete_session(session_id)
                    st.rerun()
    
    # Show "Show more" link if there are more than 3 sessions
    if total_sessions > 3:
        if st.button(f"Show all ({total_sessions})", key="show_all_sessions", type="tertiary"):
            st.session_state.current_page = "chat_history"
            st.rerun()


def _delete_session(session_id: str) -> None:
    """Delete a session."""
    sessions = st.session_state.get("sessions", {})
    
    if session_id in sessions:
        del sessions[session_id]
    
    if st.session_state.get("active_session_id") == session_id:
        if sessions:
            st.session_state.active_session_id = list(sessions.keys())[0]
        else:
            _create_new_session()
