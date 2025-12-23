# components/sidebar.py
"""
Sidebar navigation component
Handles all navigation logic
"""
import streamlit as st
from utils.auth import (
    get_current_user, get_current_role, logout_user, get_role_emoji,
    is_superuser, is_manager, is_admin
)
from utils.database import load_pending_users, load_password_reset_requests
from config import ROLES

def render_sidebar():
    """Render sidebar navigation"""
    username = get_current_user()
    role = get_current_role()
    role_emoji = get_role_emoji(role)
    
    with st.sidebar:
        # User info
        st.write(f"**User:** {username}")
        st.write(f"**Role:** {role_emoji} {role.upper()}")
        st.markdown("---")
        
        # Main navigation
        st.subheader("📍 Navigation")
        
        render_main_navigation(role)
        
        # Role-specific menus
        if is_superuser():
            render_superuser_menu()
        elif is_manager():
            render_manager_menu()
        elif is_admin():
            render_admin_menu()
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="primary", key="nav_logout"):
            logout_user()
            st.rerun()

def render_main_navigation(role: str):
    """Render main navigation buttons"""
    
    # Home
    if st.button("🏠 Home", use_container_width=True, key="nav_home"):
        st.session_state.current_page = "home"
        st.rerun()
    
    # Allocation
    if st.button("📊 Allocation", use_container_width=True, key="nav_allocation"):
        st.session_state.current_page = "allocation"
        st.rerun()
    
    # Audit Trail
    if st.button("🔍 Audit Documents", use_container_width=True, key="nav_audit"):
        st.session_state.current_page = "audit"
        st.rerun()
    
    # UAT Status (hide for managers - they access via their menu)
    if role != "manager":
        if st.button("✅ UAT Status", use_container_width=True, key="nav_uat"):
            st.session_state.current_page = "uat"
            st.rerun()

def render_superuser_menu():
    """Render superuser-specific menu"""
    st.markdown("---")
    st.subheader("👑 Super User Menu")
    
    # Count pending items
    pending_count = len(load_pending_users())
    pending_resets = len([r for r in load_password_reset_requests() if r.get('status') == 'pending'])
    total_pending = pending_count + pending_resets
    
    # User Management with badge
    pending_label = "⏳ User Management"
    if total_pending > 0:
        pending_label = f"⏳ Pending Items ({total_pending})"
    
    if st.button(pending_label, use_container_width=True, key="nav_superuser"):
        st.session_state.current_page = "superuser"
        st.rerun()
    
    # View All Allocations
    if st.button("📋 View All Allocations", use_container_width=True, key="nav_all_allocations"):
        st.session_state.current_page = "all_allocations"
        st.rerun()
    
    # Email Settings
    if st.button("📧 Email Settings", use_container_width=True, key="nav_email"):
        st.session_state.current_page = "email_settings"
        st.rerun()

def render_manager_menu():
    """Render manager-specific menu"""
    st.markdown("---")
    st.subheader("👨‍💼 Manager Menu")
    
    # Team Management
    if st.button("👥 Team Management", use_container_width=True, key="nav_manager"):
        st.session_state.current_page = "manager"
        st.rerun()
    
    # View All Allocations
    if st.button("📋 View All Allocations", use_container_width=True, key="nav_all_allocations_mgr"):
        st.session_state.current_page = "all_allocations"
        st.rerun()
    
    # UAT Status (Manager accesses here)
    if st.button("✅ UAT Status", use_container_width=True, key="nav_uat_manager"):
        st.session_state.current_page = "uat"
        st.rerun()

def render_admin_menu():
    """Render admin-specific menu"""
    st.markdown("---")
    st.subheader("🔧 Admin Menu")
    
    # View Users
    if st.button("👥 View Users", use_container_width=True, key="nav_admin"):
        st.session_state.current_page = "admin"
        st.rerun()
    
    # View All Allocations
    if st.button("📋 View All Allocations", use_container_width=True, key="nav_all_allocations_admin"):
        st.session_state.current_page = "all_allocations"
        st.rerun()
    
    # Email Settings
    if st.button("📧 Email Settings", use_container_width=True, key="nav_email_admin"):
        st.session_state.current_page = "email_settings"
        st.rerun()