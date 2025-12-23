# pages/admin/superuser.py
"""
Superuser dashboard - Full user management and approvals
"""
import streamlit as st
from datetime import datetime
from utils.auth import get_current_user, hash_password
from utils.database import (
    load_users, save_users, load_pending_users, save_pending_users,
    load_password_reset_requests, save_password_reset_requests
)
from utils.validators import validate_email, validate_password, validate_username
from utils.email_handler import send_email, send_password_reset_notification
from services.user_service import (
    create_user, update_user_role, delete_user,
    approve_pending_user, reject_pending_user, get_user_statistics
)
from services.audit_service import log_user_action, log_page_view

def render_superuser_dashboard():
    """Superuser dashboard"""
    log_page_view("superuser")
    
    st.title("👑 Super User Dashboard")
    st.markdown("---")
    
    if st.button("⬅️ Back to Home", key="super_back_home"):
        st.session_state.current_page = "home"
        st.rerun()
    
    # Count pending items
    pending_users_count = len(load_pending_users())
    pending_resets_count = len([r for r in load_password_reset_requests() if r.get('status') == 'pending'])
    
    menu = st.selectbox("Select Action", [
        f"Pending Approvals ({pending_users_count})",
        f"Password Reset Requests ({pending_resets_count})",
        "Add User Directly",
        "View All Users",
        "Manage Users",
        "Delete User"
    ])
    
    if menu.startswith("Pending Approvals"):
        render_pending_approvals()
    elif menu.startswith("Password Reset Requests"):
        render_password_reset_requests()
    elif menu == "Add User Directly":
        render_add_user_directly()
    elif menu == "View All Users":
        render_view_all_users()
    elif menu == "Manage Users":
        render_manage_users()
    elif menu == "Delete User":
        render_delete_user()

def render_pending_approvals():
    """Render pending user approvals"""
    st.subheader("⏳ Pending User Approvals")
    
    pending_users = load_pending_users()
    
    if pending_users:
        st.info(f"📋 {len(pending_users)} user(s) waiting for approval")
        
        for idx, pending in enumerate(pending_users):
            with st.expander(f"👤 {pending['username']} - Requested: {pending['requested_at']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Username:** {pending['username']}")
                    st.write(f"**Email:** {pending['email']}")
                    st.write(f"**Requested Role:** {pending['requested_role']}")
                    st.write(f"**Status:** {pending['status']}")
                
                with col2:
                    st.write(f"**Requested At:** {pending['requested_at']}")
                    
                    # Approve with role selection
                    approve_as_role = st.selectbox(
                        "Approve as Role:",
                        ["user", "admin", "manager"],
                        key=f"approve_role_{idx}"
                    )
                    
                    col_approve, col_reject = st.columns(2)
                    
                    with col_approve:
                        if st.button("✅ Approve", key=f"approve_{idx}", type="primary"):
                            success, message = approve_pending_user(pending['username'], approve_as_role)
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                    
                    with col_reject:
                        if st.button("❌ Reject", key=f"reject_{idx}"):
                            success, message = reject_pending_user(pending['username'])
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
    else:
        st.info("✅ No pending approvals")

def render_password_reset_requests():
    """Render password reset requests"""
    st.subheader("🔑 Password Reset Requests")
    
    reset_requests = load_password_reset_requests()
    pending_requests = [r for r in reset_requests if r.get('status') == 'pending']
    
    if pending_requests:
        st.info(f"📋 {len(pending_requests)} password reset request(s) waiting for approval")
        st.caption("ℹ️ Users have already set their new passwords. You only need to approve or reject.")
        
        for idx, request in enumerate(pending_requests):
            with st.expander(f"🔑 {request['username']} - Requested: {request['requested_at']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Username:** {request['username']}")
                    st.write(f"**Email:** {request['email']}")
                    st.write(f"**Requested At:** {request['requested_at']}")
                    st.write(f"**Request ID:** {request['id']}")
                
                with col2:
                    st.write(f"**Reason:**")
                    st.info(request.get('reason', 'N/A'))
                    st.write(f"**Status:** 🟡 Pending Approval")
                
                st.markdown("---")
                st.markdown("#### 👨‍💼 Super User Action Required")
                st.caption("The user has provided a new password. Review and decide:")
                
                col_approve, col_reject = st.columns(2)
                
                with col_approve:
                    if st.button("✅ Approve Password Reset", key=f"approve_reset_{idx}", type="primary", use_container_width=True):
                        # Update user password
                        users = load_users()
                        if request['username'] in users:
                            users[request['username']]['password'] = request['new_password']
                            users[request['username']]['password_reset_by'] = get_current_user()
                            users[request['username']]['password_reset_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            if save_users(users):
                                # Update request status
                                for r in reset_requests:
                                    if r['id'] == request['id']:
                                        r['status'] = 'approved'
                                        r['approved_by'] = get_current_user()
                                        r['approved_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        break
                                
                                save_password_reset_requests(reset_requests)
                                
                                st.success(f"✅ Password reset approved for '{request['username']}'!")
                                
                                # Send notification
                                try:
                                    send_password_reset_notification(request['username'], request['email'], "approved")
                                except:
                                    pass
                                
                                log_user_action("APPROVE", "Password Reset", f"Approved password reset for {request['username']}")
                                
                                st.balloons()
                                st.rerun()
                        else:
                            st.error(f"❌ User '{request['username']}' not found!")
                
                with col_reject:
                    if st.button("❌ Reject Request", key=f"reject_reset_{idx}", use_container_width=True):
                        # Update request status
                        for r in reset_requests:
                            if r['id'] == request['id']:
                                r['status'] = 'rejected'
                                r['rejected_by'] = get_current_user()
                                r['rejected_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                break
                        
                        save_password_reset_requests(reset_requests)
                        st.success(f"✅ Password reset request rejected for '{request['username']}'")
                        
                        # Send notification
                        try:
                            send_password_reset_notification(request['username'], request['email'], "rejected")
                        except:
                            pass
                        
                        log_user_action("REJECT", "Password Reset", f"Rejected password reset for {request['username']}")
                        
                        st.rerun()
    else:
        st.info("✅ No pending password reset requests")
    
    # Show history
    st.markdown("---")
    st.subheader("📜 Reset Request History")
    
    processed_requests = [r for r in reset_requests if r.get('status') != 'pending']
    
    if processed_requests:
        for request in reversed(processed_requests[-10:]):
            status_emoji = "✅" if request['status'] == 'approved' else "❌"
            status_color = "green" if request['status'] == 'approved' else "red"
            
            with st.expander(f"{status_emoji} {request['username']} - {request['status'].title()} - {request['requested_at']}"):
                st.write(f"**Username:** {request['username']}")
                st.write(f"**Email:** {request['email']}")
                st.write(f"**Status:** :{status_color}[{request['status'].upper()}]")
                st.write(f"**Requested At:** {request['requested_at']}")
                st.write(f"**Reason:** {request.get('reason', 'N/A')}")
                
                if request.get('approved_by'):
                    st.write(f"**Approved By:** {request['approved_by']}")
                    st.write(f"**Approved At:** {request.get('approved_at', 'N/A')}")
                
                if request.get('rejected_by'):
                    st.write(f"**Rejected By:** {request['rejected_by']}")
                    st.write(f"**Rejected At:** {request.get('rejected_at', 'N/A')}")
    else:
        st.info("No processed requests yet")

def render_add_user_directly():
    """Render add user form"""
    st.subheader("➕ Add New User Directly")
    st.info("ℹ️ As Super User, you can create users with any role")
    
    new_username = st.text_input("Username*", key="super_add_username")
    new_email = st.text_input("Email*", key="super_add_email")
    new_password = st.text_input("Password*", type="password", key="super_add_password")
    new_role = st.selectbox("Role*", ["user", "admin", "manager"], key="super_add_role")
    
    if st.button("Add User", key="super_add_btn", type="primary"):
        if new_username and new_email and new_password:
            success, message = create_user(new_username, new_email, new_password, new_role)
            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
        else:
            st.warning("⚠️ Please fill in all fields.")

def render_view_all_users():
    """Render all users view"""
    st.subheader("👥 All Users")
    
    users = load_users()
    
    if users:
        # Statistics
        stats = get_user_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", stats['total'])
        with col2:
            st.metric("Users", stats['by_role'].get('user', 0))
        with col3:
            st.metric("Admins", stats['by_role'].get('admin', 0))
        with col4:
            st.metric("Managers", stats['by_role'].get('manager', 0))
        
        st.markdown("---")
        
        # Filter
        filter_role = st.selectbox("Filter by Role", ["All", "user", "admin", "manager", "superuser"])
        
        for username, details in users.items():
            if filter_role == "All" or details.get('role') == filter_role:
                role_emoji = "👑" if details.get('role') == 'superuser' else "👨‍💼" if details.get('role') == 'manager' else "🔧" if details.get('role') == 'admin' else "👤"
                
                with st.expander(f"{role_emoji} {username} ({details.get('role', 'N/A').upper()})"):
                    st.write(f"**Email:** {details.get('email', 'N/A')}")
                    st.write(f"**Role:** {details.get('role', 'N/A')}")
                    st.write(f"**Status:** {details.get('status', 'active')}")
                    st.write(f"**Created:** {details.get('created_at', 'N/A')}")
                    if details.get('approved_by'):
                        st.write(f"**Approved By:** {details.get('approved_by')}")
                    if details.get('password_reset_at'):
                        st.write(f"**Last Password Reset:** {details.get('password_reset_at')}")
    else:
        st.info("No users found.")

def render_manage_users():
    """Render user management"""
    st.subheader("⚙️ Manage User Roles")
    
    users = load_users()
    user_list = [u for u in users.keys() if u != "superuser"]
    
    if user_list:
        selected_user = st.selectbox("Select User", user_list)
        
        if selected_user:
            user_details = users[selected_user]
            st.write(f"**Current Role:** {user_details.get('role', 'N/A')}")
            st.write(f"**Email:** {user_details.get('email', 'N/A')}")
            
            new_role = st.selectbox(
                "Change Role To:",
                ["user", "admin", "manager"],
                index=["user", "admin", "manager"].index(user_details.get('role', 'user'))
            )
            
            if st.button("Update Role", type="primary"):
                success, message = update_user_role(selected_user, new_role)
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
    else:
        st.info("No users to manage.")

def render_delete_user():
    """Render user deletion"""
    st.subheader("🗑️ Delete User")
    
    users = load_users()
    user_list = [u for u in users.keys() if u != "superuser"]
    
    if user_list:
        user_to_delete = st.selectbox("Select User to Delete", user_list)
        
        if user_to_delete:
            st.warning(f"⚠️ Are you sure you want to delete user '{user_to_delete}'?")
            st.write(f"**Role:** {users[user_to_delete].get('role', 'N/A')}")
            st.write(f"**Email:** {users[user_to_delete].get('email', 'N/A')}")
            
            if st.button("🗑️ Confirm Delete", key="super_delete_btn", type="primary"):
                success, message = delete_user(user_to_delete)
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
    else:
        st.info("No users to delete.")