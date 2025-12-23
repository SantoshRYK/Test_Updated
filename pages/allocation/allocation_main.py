# pages/allocation/allocation_main.py
"""
Main Allocation page - Entry point for allocation module
"""
import streamlit as st
from pages.allocation.allocation_create import render_allocation_create_tab
from services.audit_service import log_page_view
from pages.allocation.allocation_view import render_allocation_view_tab
from services.audit_service import log_page_view
from utils.database import load_email_config

def render_allocation_page():
    """Main allocation page with tabs"""
    log_page_view("allocation")
    
    st.title("📊 Allocation Management")
    st.markdown("---")
    
    if st.button("⬅️ Back to Home", key="alloc_back_home"):
        st.session_state.current_page = "home"
        st.rerun()
    
    # Show email notification status
    config = load_email_config()
    if config.get("enabled", False):
        st.success("📧 Email notifications are enabled")
    else:
        st.info("📧 Email notifications are disabled")
    
    # Create tabs
    tab1, tab2 = st.tabs(["➕ Add Allocation", "📋 My Allocations"])
    
    with tab1:
        render_allocation_create_tab()
    
    with tab2:
        render_allocation_view_tab()