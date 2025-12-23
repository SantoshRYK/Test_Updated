# pages/uat/uat_main.py
"""
Main UAT Status page - Entry point for UAT module
ROUTER for all UAT features
"""
import streamlit as st
from utils.auth import get_current_role
from services.audit_service import log_page_view

def render_uat_page():
    """Main UAT page with tabs"""
    log_page_view("uat")
    
    st.title("✅ UAT Status")
    st.markdown("---")
    
    if st.button("⬅️ Back to Home", key="uat_back_home_btn"):
        st.session_state.current_page = "home"
        st.rerun()
    
    st.subheader("User Acceptance Testing Status")
    
    role = get_current_role()
    
    # Manager sees only View and Dashboard (no Add tab)
    if role == "manager":
        tab1, tab2 = st.tabs(["📋 View UAT Records", "📊 UAT Dashboard"])
        
        with tab1:
            from pages.uat.uat_view import render_uat_view_tab
            render_uat_view_tab(is_manager=True)
        
        with tab2:
            from pages.uat.uat_dashboard import render_uat_dashboard_tab
            render_uat_dashboard_tab()
    
    else:
        # Other users see all tabs
        tab1, tab2, tab3 = st.tabs(["➕ Add UAT Record", "📋 View UAT Records", "📊 UAT Dashboard"])
        
        with tab1:
            from pages.uat.uat_create import render_uat_create_tab
            render_uat_create_tab()
        
        with tab2:
            from pages.uat.uat_view import render_uat_view_tab
            render_uat_view_tab(is_manager=False)
        
        with tab3:
            from pages.uat.uat_dashboard import render_uat_dashboard_tab
            render_uat_dashboard_tab()