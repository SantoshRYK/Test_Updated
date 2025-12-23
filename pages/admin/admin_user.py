# pages/admin/admin_user.py
"""
Admin dashboard - Limited access
"""
import streamlit as st
from utils.database import load_users, load_pending_users
from services.allocation_service import get_allocation_records
from services.uat_service import get_uat_records_by_role
from utils.auth import get_current_user, get_current_role
from services.audit_service import log_page_view

def render_admin_dashboard():
    """Admin dashboard"""
    log_page_view("admin")
    
    st.title("🔧 Admin Dashboard")
    st.markdown("---")
    
    if st.button("⬅️ Back to Home", key="admin_back_home"):
        st.session_state.current_page = "home"
        st.rerun()
    
    st.info("ℹ️ Admin users can view users and data but cannot create or delete users")
    
    menu = st.selectbox("Select Action", ["View Users", "View Statistics"])
    
    if menu == "View Users":
        render_admin_view_users()
    elif menu == "View Statistics":
        render_admin_statistics()

def render_admin_view_users():
    """Render all users view for admin"""
    st.subheader("👥 All Users")
    
    users = load_users()
    
    if users:
        for username, details in users.items():
            role_emoji = "👑" if details.get('role') == 'superuser' else "👨‍💼" if details.get('role') == 'manager' else "🔧" if details.get('role') == 'admin' else "👤"
            
            with st.expander(f"{role_emoji} {username} ({details.get('role', 'N/A').upper()})"):
                st.write(f"**Email:** {details.get('email', 'N/A')}")
                st.write(f"**Role:** {details.get('role', 'N/A')}")
                st.write(f"**Created:** {details.get('created_at', 'N/A')}")
    else:
        st.info("No users found.")

def render_admin_statistics():
    """Render system statistics"""
    st.subheader("📊 System Statistics")
    
    users = load_users()
    allocations = get_allocation_records()
    uat_records = get_uat_records_by_role(get_current_role(), get_current_user())
    pending = len(load_pending_users())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", len(users))
    with col2:
        st.metric("Total Allocations", len(allocations))
    with col3:
        st.metric("Total UAT Records", len(uat_records))
    with col4:
        st.metric("Pending Approvals", pending)
    
    st.markdown("---")
    
    # Active users
    active_users = len([u for u in users.values() if u.get('status', 'active') == 'active'])
    st.metric("Active Users", active_users)