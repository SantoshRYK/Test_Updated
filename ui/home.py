# pages/home.py
"""
Home page - Landing page after login
"""
import streamlit as st
from utils.auth import get_current_user, get_current_role, get_role_emoji
from utils.database import load_users
from services.audit_service import log_page_view

def render_home_page():
    """Render home page"""
    log_page_view("home")
    
    username = get_current_user()
    role = get_current_role()
    
    st.title(f"Welcome, {username}! 👋")
    
    # Role-specific greeting
    role_display = {
        "superuser": "👑 Super User",
        "manager": "👨‍💼 Manager",
        "admin": "🔧 Admin",
        "user": "👤 Test Engineer"
    }
    
    st.markdown(f"### {role_display.get(role, '👤 User')}")
    st.markdown("---")
    
    # User details
    users = load_users()
    user_details = users.get(username, {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Role:** {user_details.get('role', 'N/A').upper()}")
    with col2:
        st.info(f"**Email:** {user_details.get('email', 'N/A')}")
    with col3:
        created_at = user_details.get('created_at', 'N/A')
        display_date = created_at[:10] if len(created_at) > 10 else created_at
        st.info(f"**Member Since:** {display_date}")
    
    st.markdown("---")
    
    # Quick access cards - navy blue themed
    st.subheader("📋 Quick Access")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    # Card 1 - Allocation (deep navy)
    with col1:
        st.markdown("""
        <div style='text-align:center; padding:22px; background-color:#0B2545; border: 1px solid rgba(11,37,69,0.25); border-radius:12px; box-shadow: 0 6px 18px rgba(2,6,23,0.25);'>
            <h2 style='color:#F8FAFF; margin:0; font-size:30px;'>📊</h2>
            <h3 style='color:#F8FAFF; margin-top:8px;'>Allocation</h3>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Allocation", key="home_allocation_btn", use_container_width=True):
            st.session_state.current_page = "allocation"
            st.rerun()
        st.caption("Manage test allocations and assignments")
    
    # Card 2 - Audit Trail (slate navy)
    with col2:
        st.markdown("""
        <div style='text-align:center; padding:22px; background-color:#14213D; border: 1px solid rgba(20,33,61,0.25); border-radius:12px; box-shadow: 0 6px 18px rgba(3,9,36,0.22);'>
            <h2 style='color:#7DD3FC; margin:0; font-size:30px;'>🔍</h2>
            <h3 style='color:#E6F7FF; margin-top:8px;'>Audit Documents</h3>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Audit Documents", key="home_audit_btn", use_container_width=True):
            st.session_state.current_page = "audit"
            st.rerun()
        st.caption("View audit Documents and history")
    
    # Card 3 - UAT Status (navy-teal)
    with col3:
        st.markdown("""
        <div style='text-align:center; padding:22px; background-color:#0F4568; border: 1px solid rgba(15,69,104,0.25); border-radius:12px; box-shadow: 0 6px 18px rgba(2,12,32,0.22);'>
            <h2 style='color:#F8FAFF; margin:0; font-size:30px;'>✅</h2>
            <h3 style='color:#F8FAFF; margin-top:8px;'>UAT Status</h3>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to UAT Status", key="home_uat_btn", use_container_width=True):
            st.session_state.current_page = "uat"
            st.rerun()
        st.caption("Check UAT testing status")
    
    st.markdown("---")
    
    # Recent activity summary (optional)
    if role in ['superuser', 'admin', 'manager']:
        render_admin_summary()

def render_admin_summary():
    """Render summary for admin roles"""
    from utils.database import load_pending_users, load_password_reset_requests
    from services.allocation_service import get_allocation_statistics, get_allocation_records
    from services.uat_service import get_uat_statistics, get_uat_records_by_role
    from utils.auth import get_current_user, get_current_role
    
    st.subheader("📊 Quick Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pending_users = len(load_pending_users())
        st.metric("Pending User Approvals", pending_users)
    
    with col2:
        pending_resets = len([r for r in load_password_reset_requests() if r.get('status') == 'pending'])
        st.metric("Pending Password Resets", pending_resets)
    
    with col3:
        allocations = get_allocation_records()
        st.metric("Total Allocations", len(allocations))
    
    with col4:
        uat_records = get_uat_records_by_role(get_current_role(), get_current_user())
        st.metric("Total UAT Records", len(uat_records))