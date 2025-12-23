# pages/allocation/allocation_view.py
"""
Allocation viewing and management
MANAGER RESTRICTION: Detailed view removed for manager role
EDIT FUNCTIONALITY: Users can edit their own allocations
"""
import streamlit as st
import pandas as pd
from datetime import datetime
# Import audit service
from services.audit_service import log_page_view
# Import utilities
from utils.auth import get_current_user, get_current_role
# Import services
from services.allocation_service import (
    get_allocations_by_role,
    delete_allocation_record,
    get_all_allocations
)
# Import components
from components.filters import render_allocation_filters
from components.metrics import render_allocation_metrics
from utils.excel_handler import convert_to_excel

def render_allocation_view_tab():
    """Render allocation viewing tab"""
    st.subheader("Your Allocations")
    
    username = get_current_user()
    role = get_current_role()
    
    # Check if in edit mode
    if 'edit_allocation_id' in st.session_state:
        render_edit_mode()
        return
    
    # Load allocations based on role
    allocations = get_allocations_by_role(role, username)
    
    if role in ["admin", "manager", "superuser"]:
        st.info(f"👨‍💼 {role.title()} View: Showing all allocations from all users")
    else:
        st.info(f"👤 User View: Showing only your allocations")
    
    if allocations:
        # Render metrics using allocation list directly
        render_allocation_metrics(allocations)
        
        st.markdown("---")
        
        # Download Excel button
        col1, col2, col3 = st.columns([2, 1, 1])
        with col3:
            excel_data = convert_to_excel(allocations, "Allocations")
            if excel_data:
                filename_prefix = "all_allocations" if role in ["admin", "manager", "superuser"] else f"allocations_{username}"
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        st.markdown("---")
        
        # Filters - returns filtered allocations directly
        filtered_allocations = render_allocation_filters(allocations, key_suffix="view")
        
        st.markdown("---")
        st.subheader(f"Showing {len(filtered_allocations)} of {len(allocations)} Allocations")
        
        # Display as table
        try:
            df = pd.DataFrame(filtered_allocations)
            display_columns = ['trial_id', 'test_engineer_name', 'system', 'trial_category', 
                             'therapeutic_area', 'role', 'activity', 'start_date', 'end_date']
            available_columns = [col for col in display_columns if col in df.columns]
            if available_columns:
                st.dataframe(df[available_columns], use_container_width=True, hide_index=True)
        except Exception as e:
            st.warning(f"Could not display table: {e}")
        
        st.markdown("---")
        
        # ========== BLOCK DETAILED VIEW FOR MANAGERS ==========
        if role == "manager":
            st.info("ℹ️ **Detailed View Access Restricted**")
            st.warning("👨‍💼 Manager role can view the summary table and metrics above. Detailed allocation information is available for Admin and Superuser roles only.")
            st.markdown("📧 **Need detailed information?** Contact your system administrator or request Admin access.")
            return  # EXIT HERE - Don't show detailed view for managers
        
        # ========== DETAILED VIEW (ONLY FOR NON-MANAGERS) ==========
        st.subheader("📋 Detailed View")
        st.caption("🔒 This section is restricted to Admin and Superuser roles")
        
        # Display detailed cards
        render_allocation_cards(filtered_allocations)
    
    else:
        if role in ["admin", "manager", "superuser"]:
            st.info("📝 No allocations found in the system.")
        else:
            st.info("📝 No allocations found. Create your first allocation above!")

def render_edit_mode():
    """Render edit mode interface"""
    from pages.allocation.allocation_edit import render_allocation_edit_form
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ Back to List", key="back_from_edit_view"):
            del st.session_state['edit_allocation_id']
            st.rerun()
    
    st.markdown("---")
    render_allocation_edit_form(st.session_state['edit_allocation_id'])

def render_allocation_cards(allocations):
    """Render allocation detail cards with EDIT functionality - NOT FOR MANAGERS"""
    current_user = get_current_user()
    current_role = get_current_role()
    
    for allocation in reversed(allocations):
        # System emoji
        system_emoji = {
            "INFORM": "📊",
            "VEEVA": "📁",
            "eCOA": "📱",
            "ePID": "🔬",
            "CGM": "📈",
            "Others": "📋"
        }.get(allocation.get('system'), "📋")
        
        # Therapeutic area emoji
        therapeutic_area_full = allocation.get('therapeutic_area', 'N/A')
        if "Diabetic" in therapeutic_area_full and "Obesity" not in therapeutic_area_full:
            area_emoji = "💉"
        elif "Obesity" in therapeutic_area_full:
            area_emoji = "⚖️"
        elif "CKAD" in therapeutic_area_full:
            area_emoji = "🫀"
        elif "CagriSema" in therapeutic_area_full:
            area_emoji = "💊"
        elif "Phase 1" in therapeutic_area_full or "NIS" in therapeutic_area_full:
            area_emoji = "🔬"
        elif "Rare Disease" in therapeutic_area_full:
            area_emoji = "🩺"
        else:
            area_emoji = "🏥"
        
        trial_id = allocation.get('trial_id', 'N/A')
        engineer = allocation.get('test_engineer_name', 'N/A')
        system = allocation.get('system', 'N/A')
        category = allocation.get('trial_category', 'N/A')
        
        with st.expander(f"{system_emoji} {area_emoji} [{trial_id}] {engineer} - {system} - {category}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Trial ID:** {allocation.get('trial_id', 'N/A')}")
                st.write(f"**Test Engineer:** {allocation.get('test_engineer_name', 'N/A')}")
                st.write(f"**System:** {allocation.get('system', 'N/A')}")
                st.write(f"**Trial Category:** {allocation.get('trial_category', 'N/A')}")
                st.write(f"**Therapeutic Area:** {allocation.get('therapeutic_area', 'N/A')}")
            
            with col2:
                st.write(f"**Role:** {allocation.get('role', 'N/A')}")
                st.write(f"**Start Date:** {allocation.get('start_date', 'N/A')}")
                st.write(f"**End Date:** {allocation.get('end_date', 'N/A')}")
                st.write(f"**Created By:** {allocation.get('created_by', 'N/A')}")
            
            st.markdown("---")
            st.write(f"**Activity:**")
            st.write(allocation.get('activity', 'N/A'))
            
            st.caption(f"Allocation ID: {allocation.get('id', 'N/A')}")
            
            # Action buttons (only for creator or admin/superuser)
            # Show edit/delete for creator or superuser/admin (NOT for managers)
            if current_user == allocation.get('created_by') or current_role in ['superuser', 'admin']:
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                # EDIT BUTTON
                with col1:
                    if st.button("✏️ Edit", key=f"edit_alloc_{allocation.get('id')}", use_container_width=True):
                        st.session_state['edit_allocation_id'] = allocation.get('id')
                        st.rerun()
                
                # DELETE BUTTON
                with col2:
                    confirm_key = f"confirm_delete_alloc_{allocation.get('id')}"
                    
                    if st.button(f"🗑️ Delete", key=f"delete_alloc_{allocation.get('id')}", use_container_width=True):
                        if st.session_state.get(confirm_key, False):
                            # User confirmed, delete it
                            success, message = delete_allocation_record(allocation.get('id'))
                            if success:
                                st.success(f"✅ {message}")
                                # Clear confirmation state
                                if confirm_key in st.session_state:
                                    del st.session_state[confirm_key]
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        else:
                            # First click, ask for confirmation
                            st.session_state[confirm_key] = True
                            st.warning("⚠️ Click Delete again to confirm!")
                            st.rerun()

def render_all_allocations_view():
    """
    Render all allocations view for admins/superusers
    MANAGERS ARE BLOCKED FROM DETAILED VIEW
    """
    log_page_view("all_allocations")
    
    current_role = get_current_role()
    
    # Check if in edit mode
    if 'edit_allocation_id_admin' in st.session_state:
        render_admin_edit_mode()
        return
    
    st.title("👨‍💼 All Allocations")
    
    # Role-specific info
    if current_role == "manager":
        st.info("👨‍💼 **Manager View:** You have access to summary data and metrics. Detailed allocation information is restricted to Admin and Superuser roles.")
    else:
        st.info("🔧 **Admin/Superuser View:** Full access to all allocation details and management functions.")
    
    st.markdown("---")
    
    if st.button("⬅️ Back to Home", key="all_alloc_back"):
        st.session_state.current_page = "home"
        st.rerun()
    
    # Load all allocations
    allocations = get_all_allocations()
    
    if not allocations:
        st.info("📝 No allocations found in the system.")
        return
    
    # Render metrics (ALL ROLES)
    render_allocation_metrics(allocations)
    
    st.markdown("---")
    
    # Filters - returns filtered data directly (ALL ROLES)
    filtered_allocations = render_allocation_filters(allocations, key_suffix="admin")
    
    st.markdown("---")
    
    # Show count and download
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader(f"📋 Showing {len(filtered_allocations)} of {len(allocations)} Allocations")
    
    with col3:
        # Download button (ALL ROLES)
        excel_data = convert_to_excel(filtered_allocations, "Allocations")
        if excel_data:
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name=f"allocations_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    st.markdown("---")
    
    # Table view (ALL ROLES)
    st.subheader("📊 Allocation Summary Table")
    render_allocation_table(filtered_allocations)
    
    st.markdown("---")
    
    # ========== BLOCK DETAILED VIEW FOR MANAGERS ==========
    if current_role == "manager":
        st.info("ℹ️ **Detailed View Access Restricted**")
        st.warning("👨‍💼 Manager role has access to the summary table and metrics above. Individual allocation details, including expandable cards and management actions, are available for Admin and Superuser roles only.")
        st.markdown("""
        ### 📊 Available to Managers:
        - ✅ Summary metrics and statistics
        - ✅ Allocation table view
        - ✅ Filter and search functionality
        - ✅ Excel export
        
        ### 🔒 Restricted Access:
        - ❌ Detailed allocation cards
        - ❌ Edit/Delete actions
        - ❌ Full allocation history
        
        📧 **Need detailed access?** Contact your system administrator.
        """)
        return  # EXIT HERE for managers
    
    # ========== DETAILED VIEW (ADMIN/SUPERUSER ONLY) ==========
    st.subheader("📋 Detailed View")
    st.caption("🔒 Admin/Superuser Access Only")
    render_allocation_cards_admin(filtered_allocations)

def render_admin_edit_mode():
    """Render edit mode for admin view"""
    from pages.allocation.allocation_edit import render_allocation_edit_form
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ Back to List", key="back_from_edit_admin"):
            del st.session_state['edit_allocation_id_admin']
            st.rerun()
    
    st.markdown("---")
    render_allocation_edit_form(st.session_state['edit_allocation_id_admin'])

def render_allocation_table(allocations):
    """Render allocations as a data table - AVAILABLE TO ALL ROLES"""
    try:
        if not allocations:
            st.info("No data to display")
            return
        
        df = pd.DataFrame(allocations)
        display_columns = [
            'trial_id', 
            'test_engineer_name', 
            'system', 
            'trial_category',
            'therapeutic_area', 
            'role', 
            'start_date', 
            'end_date', 
            'created_by'
        ]
        available_columns = [col for col in display_columns if col in df.columns]
        
        if available_columns:
            # Sort by created_at descending (most recent first)
            if 'created_at' in df.columns:
                df_display = df[available_columns].sort_values('created_at', ascending=False)
            else:
                df_display = df[available_columns]
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.warning("No displayable columns found")
    
    except Exception as e:
        st.error(f"Error displaying table: {e}")

def render_allocation_cards_admin(allocations):
    """
    Render allocation detail cards for admin view with EDIT functionality
    ONLY CALLED FOR ADMIN/SUPERUSER (Managers never reach this function)
    """
    current_role = get_current_role()
    current_user = get_current_user()
    
    for allocation in reversed(allocations):
        # System emoji
        system_emoji = {
            "INFORM": "📊",
            "VEEVA": "📁",
            "eCOA": "📱",
            "ePID": "🔬",
            "CGM": "📈",
            "Others": "📋"
        }.get(allocation.get('system'), "📋")
        
        # Therapeutic area emoji
        therapeutic_area_full = allocation.get('therapeutic_area', 'N/A')
        if "Diabetic" in therapeutic_area_full and "Obesity" not in therapeutic_area_full:
            area_emoji = "💉"
        elif "Obesity" in therapeutic_area_full:
            area_emoji = "⚖️"
        elif "CKAD" in therapeutic_area_full:
            area_emoji = "🫀"
        elif "CagriSema" in therapeutic_area_full:
            area_emoji = "💊"
        elif "Phase 1" in therapeutic_area_full or "NIS" in therapeutic_area_full:
            area_emoji = "🔬"
        elif "Rare Disease" in therapeutic_area_full:
            area_emoji = "🩺"
        else:
            area_emoji = "🏥"
        
        trial_id = allocation.get('trial_id', 'N/A')
        engineer = allocation.get('test_engineer_name', 'N/A')
        system = allocation.get('system', 'N/A')
        category = allocation.get('trial_category', 'N/A')
        created_by = allocation.get('created_by', 'N/A')
        
        # Expander title with creator info
        expander_title = f"{system_emoji} {area_emoji} [{trial_id}] {engineer} - {system} - {category} (by {created_by})"
        
        with st.expander(expander_title):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Trial ID:** {allocation.get('trial_id', 'N/A')}")
                st.write(f"**Test Engineer:** {allocation.get('test_engineer_name', 'N/A')}")
                st.write(f"**System:** {allocation.get('system', 'N/A')}")
                st.write(f"**Trial Category:** {allocation.get('trial_category', 'N/A')}")
                st.write(f"**Therapeutic Area:** {allocation.get('therapeutic_area', 'N/A')}")
            
            with col2:
                st.write(f"**Role:** {allocation.get('role', 'N/A')}")
                st.write(f"**Start Date:** {allocation.get('start_date', 'N/A')}")
                st.write(f"**End Date:** {allocation.get('end_date', 'N/A')}")
                st.write(f"**Created By:** {allocation.get('created_by', 'N/A')}")
                st.write(f"**Created At:** {allocation.get('created_at', 'N/A')}")
                
                # Show updated info if exists
                if allocation.get('updated_at'):
                    st.write(f"**Updated At:** {allocation.get('updated_at', 'N/A')}")
                    st.write(f"**Updated By:** {allocation.get('updated_by', 'N/A')}")
            
            st.markdown("---")
            st.write(f"**Activity:**")
            st.text_area(
                "Activity Details",
                value=allocation.get('activity', 'N/A'),
                height=100,
                disabled=True,
                key=f"activity_admin_{allocation.get('id')}"
            )
            
            st.caption(f"Allocation ID: {allocation.get('id', 'N/A')}")
            
            # Action buttons (only for superuser)
            if current_role == 'superuser':
                st.markdown("---")
                render_admin_allocation_actions(allocation)

def render_admin_allocation_actions(allocation):
    """Render action buttons for admin view - SUPERUSER ONLY with EDIT"""
    col1, col2 = st.columns(2)
    
    with col1:
        # EDIT BUTTON
        if st.button("✏️ Edit", key=f"edit_alloc_admin_{allocation.get('id')}", use_container_width=True):
            st.session_state['edit_allocation_id_admin'] = allocation.get('id')
            st.rerun()
    
    with col2:
        # DELETE BUTTON
        confirm_key = f"confirm_delete_admin_{allocation.get('id')}"
        
        if st.button(f"🗑️ Delete", key=f"delete_alloc_admin_{allocation.get('id')}", use_container_width=True):
            if st.session_state.get(confirm_key, False):
                # User confirmed, delete it
                success, message = delete_allocation_record(allocation.get('id'))
                if success:
                    st.success(f"✅ {message}")
                    # Clear confirmation state
                    if confirm_key in st.session_state:
                        del st.session_state[confirm_key]
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                # First click, ask for confirmation
                st.session_state[confirm_key] = True
                st.warning("⚠️ Click Delete again to confirm!")
                st.rerun()