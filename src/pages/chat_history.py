"""
Chat History page - shows all chat sessions.
"""
import streamlit as st


def render_chat_history():
    """Render the full chat history page."""
    st.markdown("## Chat History")
    st.markdown("All your previous chat sessions.")
    
    # Back button
    if st.button("← Back to Assistant", key="back_to_app"):
        st.session_state.current_page = "app"
        st.rerun()
    
    st.markdown("---")
    
    sessions = st.session_state.get("sessions", {})
    active_id = st.session_state.get("active_session_id", None)
    
    if not sessions:
        st.info("No chat sessions yet. Start a new chat!")
        return
    
    # Show all sessions in reverse order (newest first)
    for session_id, session_data in reversed(list(sessions.items())):
        title = session_data.get("title", "Untitled")
        messages = session_data.get("messages", [])
        is_active = session_id == active_id
        
        col1, col2, col3 = st.columns([5, 1, 1])
        
        with col1:
            # Session card
            status = "● Active" if is_active else ""
            message_count = len(messages)
            st.markdown(f"**{title}** {status}")
            st.caption(f"{message_count} messages")
        
        with col2:
            if st.button("Open", key=f"open_{session_id}", use_container_width=True):
                st.session_state.active_session_id = session_id
                st.session_state.current_page = "app"
                st.rerun()
        
        with col3:
            if st.button("Delete", key=f"delete_{session_id}", use_container_width=True):
                _delete_session_from_history(session_id)
                st.rerun()
        
        st.markdown("---")


def _delete_session_from_history(session_id: str) -> None:
    """Delete a session from history."""
    sessions = st.session_state.get("sessions", {})
    
    if session_id in sessions:
        del sessions[session_id]
    
    if st.session_state.get("active_session_id") == session_id:
        if sessions:
            st.session_state.active_session_id = list(sessions.keys())[0]
        else:
            # Create a new empty session
            import uuid
            new_id = str(uuid.uuid4())
            st.session_state.sessions = {new_id: {"title": "New Chat", "messages": []}}
            st.session_state.active_session_id = new_id
