# pages/admin/manager.py
import streamlit as st
from datetime import datetime
import pandas as pd

def render_manager_page():
    """Manager dashboard page - Summary view only"""
    st.title("👨‍💼 Manager Dashboard")
    st.info("📊 Manager View - Summary and overview access only. Detailed views are restricted to Admin/Superuser roles.")
    st.markdown("---")
    
    if st.button("⬅️ Back to Home", key="manager_back_home_btn"):
        st.session_state.current_page = "home"
        st.rerun()
    
    menu = st.selectbox(
        "Select Action", 
        [
            "📊 Allocation Dashboard",
            "👥 Team Management",
            "👤 View Users"
        ],
        key="manager_menu_selectbox"
    )
    
    st.markdown("---")
    
    if menu == "📊 Allocation Dashboard":
        from pages.allocation.allocation_dashboard import render_manager_allocation_dashboard
        render_manager_allocation_dashboard()
    
    elif menu == "👥 Team Management":
        render_team_management()
    
    elif menu == "👤 View Users":
        render_users_view()

def render_team_management():
    """Enhanced Team Management View - Summary Only"""
    from utils.database import load_users
    from services.allocation_service import AllocationService
    
    st.header("👥 Team Management")
    st.info("📌 Manage your team members and view workload summary")
    st.markdown("---")
    
    try:
        users = load_users()
        allocation_service = AllocationService()
        allocations = allocation_service.get_all_allocations()
        
        team_members = {username: details for username, details in users.items() 
                        if details.get('role') == 'user'}
        
        if not team_members:
            st.warning("⚠️ No team members found.")
            return
        
        # ========== TEAM STATISTICS ==========
        st.subheader("📊 Team Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Team Size", len(team_members))
        
        with col2:
            total_allocations = len(allocations)
            st.metric("📋 Total Allocations", total_allocations)
        
        with col3:
            today = datetime.now().date()
            active_allocations = sum(1 for a in allocations 
                                    if datetime.strptime(a.get('end_date', '2024-12-31'), '%Y-%m-%d').date() >= today)
            st.metric("✅ Active", active_allocations)
        
        with col4:
            avg_allocations = total_allocations / len(team_members) if team_members else 0
            st.metric("📊 Avg/Member", f"{avg_allocations:.1f}")
        
        st.markdown("---")
        
        # ========== WORKLOAD TABLE ==========
        st.subheader("👥 Team Workload Overview")
        
        workload_data = []
        for username, details in team_members.items():
            user_allocs = [a for a in allocations if a.get('created_by') == username]
            today = datetime.now().date()
            active_allocs = [a for a in user_allocs 
                            if datetime.strptime(a.get('end_date', '2024-12-31'), '%Y-%m-%d').date() >= today]
            
            if len(active_allocs) <= 3:
                workload = '🟢 Light'
            elif len(active_allocs) <= 6:
                workload = '🟡 Medium'
            else:
                workload = '🔴 Heavy'
            
            workload_data.append({
                'Team Member': username,
                'Email': details.get('email', 'N/A'),
                'Total': len(user_allocs),
                'Active': len(active_allocs),
                'Workload': workload,
                'Joined': details.get('created_at', 'N/A')[:10]
            })
        
        if workload_data:
            df_workload = pd.DataFrame(workload_data)
            st.dataframe(df_workload, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # ========== MEMBER SUMMARY (NO DETAILED VIEW) ==========
        st.subheader("🔍 Member Summary")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_member = st.selectbox(
                "Select Team Member",
                options=list(team_members.keys()),
                key="team_member_select"
            )
        with col2:
            show_inactive = st.checkbox("Show Inactive", value=False)
        
        if selected_member:
            details = team_members[selected_member]
            
            # Member Info - Basic only
            st.markdown("### 👤 Member Information")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**📧 Email:** {details.get('email', 'N/A')}")
            with col2:
                st.write(f"**🎯 Role:** {details.get('role', 'N/A').upper()}")
            with col3:
                st.write(f"**📅 Joined:** {details.get('created_at', 'N/A')[:10]}")
            
            st.markdown("---")
            
            # Get user's allocations count only
            user_allocs = [a for a in allocations if a.get('created_by') == selected_member]
            
            if not show_inactive:
                today = datetime.now().date()
                user_allocs = [a for a in user_allocs 
                              if datetime.strptime(a.get('end_date', '2024-12-31'), '%Y-%m-%d').date() >= today]
            
            # ========== SUMMARY METRICS ONLY ==========
            st.markdown("### 📊 Allocation Summary")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📋 Total Allocations", len(user_allocs))
            
            with col2:
                today = datetime.now().date()
                active = sum(1 for a in user_allocs 
                           if datetime.strptime(a.get('end_date', '2024-12-31'), '%Y-%m-%d').date() >= today)
                st.metric("✅ Active", active)
            
            with col3:
                systems = len(set(a.get('system', 'Unknown') for a in user_allocs))
                st.metric("💻 Systems", systems)
            
            st.markdown("---")
            
            # ========== BREAKDOWN SUMMARY (NO DETAILED LIST) ==========
            if user_allocs:
                st.markdown("### 📊 Distribution Summary")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**💻 Systems:**")
                    systems = {}
                    for a in user_allocs:
                        sys = a.get('system', 'Unknown')
                        systems[sys] = systems.get(sys, 0) + 1
                    for sys, count in sorted(systems.items(), key=lambda x: x[1], reverse=True)[:5]:
                        st.write(f"  • {sys}: **{count}**")
                    if len(systems) > 5:
                        st.caption(f"...and {len(systems) - 5} more")
                
                with col2:
                    st.markdown("**🎯 Roles:**")
                    roles = {}
                    for a in user_allocs:
                        role = a.get('role', 'Unknown')
                        roles[role] = roles.get(role, 0) + 1
                    for role, count in sorted(roles.items(), key=lambda x: x[1], reverse=True)[:5]:
                        st.write(f"  • {role}: **{count}**")
                    if len(roles) > 5:
                        st.caption(f"...and {len(roles) - 5} more")
                
                with col3:
                    st.markdown("**🏗️ Categories:**")
                    categories = {}
                    for a in user_allocs:
                        cat = a.get('trial_category_type', 'Unknown')
                        categories[cat] = categories.get(cat, 0) + 1
                    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
                        st.write(f"  • {cat}: **{count}**")
                    if len(categories) > 5:
                        st.caption(f"...and {len(categories) - 5} more")
                
                st.markdown("---")
                
                # Info box about detailed view restriction
                st.info("ℹ️ **Detailed allocation list is available for Admin and Superuser roles only.** Contact your administrator for detailed reports.")
            else:
                status_text = "active" if not show_inactive else ""
                st.info(f"No {status_text} allocations found for {selected_member}.")
    
    except Exception as e:
        st.error(f"❌ Error loading team management: {str(e)}")
        st.error("Please check the error details and try again.")

def render_users_view():
    """View all users - Summary only"""
    from utils.database import load_users
    
    st.header("👥 All Users")
    st.info("📌 View system users summary")
    st.markdown("---")
    
    try:
        users = load_users()
        
        if users:
            # ========== SUMMARY STATISTICS ==========
            st.subheader("📊 User Statistics")
            
            role_counts = {}
            for username, details in users.items():
                role = details.get('role', 'unknown')
                role_counts[role] = role_counts.get(role, 0) + 1
            
            cols = st.columns(len(role_counts))
            role_emojis = {
                "superuser": "👑",
                "manager": "👨‍💼",
                "admin": "🔧",
                "user": "👤"
            }
            
            for col, (role, count) in zip(cols, role_counts.items()):
                with col:
                    emoji = role_emojis.get(role, "👤")
                    st.metric(f"{emoji} {role.title()}", count)
            
            st.markdown("---")
            
            # ========== USER SUMMARY TABLE ==========
            st.subheader("👥 User List")
            
            user_data = []
            for username, details in users.items():
                role_emoji = role_emojis.get(details.get('role'), "👤")
                
                user_data.append({
                    'Icon': role_emoji,
                    'Username': username,
                    'Email': details.get('email', 'N/A'),
                    'Role': details.get('role', 'N/A').upper(),
                    'Status': details.get('status', 'active').upper(),
                    'Joined': details.get('created_at', 'N/A')[:10]
                })
            
            df_users = pd.DataFrame(user_data)
            st.dataframe(df_users, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # ========== REMOVED DETAILED EXPANDABLE VIEW ==========
            # Replaced with info message
            st.info("ℹ️ **Detailed user information is available for Admin and Superuser roles only.** For user management tasks, please contact your system administrator.")
            
        else:
            st.info("No users found.")
    
    except Exception as e:
        st.error(f"❌ Error loading users: {str(e)}")