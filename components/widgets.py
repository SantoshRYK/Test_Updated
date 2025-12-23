# components/widgets.py
"""
Custom widget components
"""
import streamlit as st
from typing import Dict, Optional
from utils.helpers import get_status_emoji, get_status_color

def render_status_badge(status: str):
    """Render colored status badge"""
    emoji = get_status_emoji(status)
    color = get_status_color(status)
    
    st.markdown(
        f'<span style="background-color: {color}; color: white; padding: 5px 10px; '
        f'border-radius: 5px; font-weight: bold;">{emoji} {status}</span>',
        unsafe_allow_html=True
    )

def render_info_card(title: str, content: Dict, emoji: str = "📝"):
    """Render information card"""
    with st.container():
        st.markdown(f"### {emoji} {title}")
        for key, value in content.items():
            st.write(f"**{key}:** {value}")

def render_action_buttons(
    show_edit: bool = True,
    show_delete: bool = True,
    show_copy: bool = False,
    edit_key: str = "edit",
    delete_key: str = "delete",
    copy_key: str = "copy",
    edit_callback = None,
    delete_callback = None,
    copy_callback = None
):
    """Render action buttons (Edit, Delete, Copy)"""
    
    button_count = sum([show_edit, show_delete, show_copy])
    cols = st.columns(button_count)
    col_idx = 0
    
    if show_edit:
        with cols[col_idx]:
            if st.button("✏️ Edit", key=edit_key, use_container_width=True):
                if edit_callback:
                    edit_callback()
        col_idx += 1
    
    if show_delete:
        with cols[col_idx]:
            if st.button("🗑️ Delete", key=delete_key, use_container_width=True):
                if delete_callback:
                    delete_callback()
        col_idx += 1
    
    if show_copy:
        with cols[col_idx]:
            if st.button("📋 Copy", key=copy_key, use_container_width=True):
                if copy_callback:
                    copy_callback()

def render_confirmation_dialog(message: str, confirm_key: str, cancel_key: str) -> Optional[bool]:
    """Render confirmation dialog"""
    st.warning(message)
    
    col1, col2 = st.columns(2)
    
    confirmed = None
    with col1:
        if st.button("✅ Confirm", key=confirm_key, type="primary", use_container_width=True):
            confirmed = True
    
    with col2:
        if st.button("❌ Cancel", key=cancel_key, use_container_width=True):
            confirmed = False
    
    return confirmed

def render_record_expander(
    record: Dict,
    title: str,
    emoji: str = "📝",
    show_actions: bool = True,
    can_edit: bool = True,
    can_delete: bool = True
):
    """Render expandable record card with consistent formatting"""
    
    with st.expander(f"{emoji} {title}"):
        # Render record details
        col1, col2 = st.columns(2)
        
        with col1:
            for key, value in list(record.items())[:len(record)//2]:
                if not key.startswith('_') and key not in ['id', 'record_type']:
                    display_key = key.replace('_', ' ').title()
                    st.write(f"**{display_key}:** {value}")
        
        with col2:
            for key, value in list(record.items())[len(record)//2:]:
                if not key.startswith('_') and key not in ['id', 'record_type']:
                    display_key = key.replace('_', ' ').title()
                    st.write(f"**{display_key}:** {value}")
        
        if show_actions:
            st.markdown("---")
            render_action_buttons(
                show_edit=can_edit,
                show_delete=can_delete,
                edit_key=f"edit_{record.get('id')}",
                delete_key=f"delete_{record.get('id')}"
            )