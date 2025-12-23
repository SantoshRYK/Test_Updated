# pages/uat/uat_view.py
"""
UAT record viewing and management
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.auth import get_current_user, get_current_role
from services.uat_service import (
    get_uat_records_by_role, get_uat_statistics,
    delete_uat_record_service, get_user_uat_statistics
)
from components.filters import render_uat_filters
from components.metrics import render_uat_summary_metrics
from utils.excel_handler import convert_to_excel
from utils.helpers import get_status_emoji

def render_uat_view_tab(is_manager: bool = False):
    """Render UAT viewing tab"""
    st.subheader("UAT Records")
    
    username = get_current_user()
    role = get_current_role()
    
    # Load UAT records based on role
    uat_records = get_uat_records_by_role(role, username)
    
    if role in ["admin", "manager", "superuser"]:
        st.info(f"👨‍💼 {role.title()} View: Showing all UAT records")
    else:
        st.info(f"👤 User View: Showing only your UAT records")
    
    if uat_records:
        # Get statistics
        stats = get_uat_statistics(uat_records)
        
        # Render summary metrics
        render_uat_summary_metrics(stats)
        
        # Show category breakdown
        col1, col2 = st.columns(2)
        with col1:
            build_count = stats['by_category'].get('Build', 0)
            st.metric("🏗️ Build", build_count)
        with col2:
            cr_count = stats['by_category'].get('Change Request', 0)
            st.metric("🔄 Change Request", cr_count)
        
        st.markdown("---")
        
        # Filters (with user filter for managers)
        filters = render_uat_filters(uat_records, show_user_filter=is_manager, key_suffix="view")
        
        # Apply filters
        filtered_records = apply_uat_filters(uat_records, filters)
        
        st.markdown("---")
        st.subheader(f"Showing {len(filtered_records)} of {len(uat_records)} UAT Records")
        
        # Export to Excel
        if filtered_records:
            excel_data = prepare_uat_excel_data(filtered_records)
            excel_output = convert_to_excel(excel_data, "UAT Records")
            
            if excel_output:
                st.download_button(
                    label="📥 Download UAT Records (Excel)",
                    data=excel_output,
                    file_name=f"uat_records_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=False
                )
        
        st.markdown("---")
        
        # Display detailed records
        st.subheader("📋 Detailed UAT Records")
        render_uat_record_cards(filtered_records, is_manager)
    
    else:
        if is_manager:
            st.info("📝 No UAT records found in the system.")
        else:
            st.info("📝 No UAT records found. Create your first UAT record in the 'Add UAT Record' tab!")

def apply_uat_filters(records, filters):
    """Apply filters to UAT records"""
    filtered = records
    
    # Trial ID filter
    if filters.get('trial_id') and filters['trial_id'] != 'All':
        filtered = [r for r in filtered if r.get('trial_id') == filters['trial_id']]
    
    # Category filter
    if filters.get('category') and filters['category'] != 'All':
        if filters['category'] == 'Build':
            filtered = [r for r in filtered if r.get('category_type') == 'Build']
        elif filters['category'] == 'Change Request':
            filtered = [r for r in filtered if r.get('category_type') == 'Change Request']
    
    # Status filter
    if filters.get('status') and filters['status'] != 'All':
        filtered = [r for r in filtered if r.get('status') == filters['status']]
    
    # Result filter
    if filters.get('result') and filters['result'] != 'All':
        filtered = [r for r in filtered if r.get('result') == filters['result']]
    
    # User filter (for managers)
    if filters.get('user') and filters['user'] != 'All':
        filtered = [r for r in filtered if r.get('created_by') == filters['user']]
    
    return filtered

def prepare_uat_excel_data(records):
    """Prepare UAT data for Excel export"""
    excel_data = []
    for record in records:
        excel_data.append({
            "Trial ID": record.get('trial_id', 'N/A'),
            "UAT Round": record.get('uat_round', 'N/A'),
            "Category": record.get('category', 'N/A'),
            "Planned Start Date": record.get('planned_start_date', 'N/A'),
            "Planned End Date": record.get('planned_end_date', 'N/A'),
            "Actual Start Date": record.get('actual_start_date') or 'Not Started',
            "Actual End Date": record.get('actual_end_date') or 'Not Completed',
            "Status": record.get('status', 'N/A'),
            "Result": record.get('result', 'N/A'),
            "Email Body": record.get('email_body', 'N/A'),
            "Created By": record.get('created_by', 'N/A'),
            "Created At": record.get('created_at', 'N/A')
        })
    return excel_data

def render_uat_record_cards(records, is_manager=False):
    """Render UAT record detail cards"""
    for record in reversed(records):
        # Get emojis
        status_emoji = get_status_emoji(record.get('status', ''))
        result_emoji = get_status_emoji(record.get('result', ''))
        category_emoji = "🏗️" if record.get('category_type') == 'Build' else "🔄"
        
        # Card title
        title = (f"{status_emoji} {result_emoji} {category_emoji} "
                f"[{record.get('trial_id')}] - {record.get('uat_round')} - "
                f"{record.get('category')} - {record.get('status')} ({record.get('result')})")
        
        with st.expander(title):
            render_uat_record_details(record, is_manager)

def render_uat_record_details(record, is_manager):
    """Render detailed UAT record information"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Trial ID:** {record.get('trial_id', 'N/A')}")
        st.write(f"**UAT Round:** {record.get('uat_round', 'N/A')}")
        st.write(f"**Category:** {record.get('category', 'N/A')}")
        st.write(f"**Status:** {get_status_emoji(record.get('status', ''))} {record.get('status', 'N/A')}")
        st.write(f"**Result:** {get_status_emoji(record.get('result', ''))} {record.get('result', 'N/A')}")
        
        st.markdown("#### 📅 Planned Dates")
        st.write(f"**Start:** {record.get('planned_start_date', 'N/A')}")
        st.write(f"**End:** {record.get('planned_end_date', 'N/A')}")
    
    with col2:
        st.write(f"**Created By:** {record.get('created_by', 'N/A')}")
        st.write(f"**Created At:** {record.get('created_at', 'N/A')}")
        st.write(f"**Updated At:** {record.get('updated_at', 'N/A')}")
        st.write(f"**Record ID:** {record.get('id', 'N/A')}")
        
        st.markdown("#### 📅 Actual Dates")
        actual_start = record.get('actual_start_date')
        actual_end = record.get('actual_end_date')
        st.write(f"**Start:** {actual_start if actual_start else '⏳ Not Started'}")
        st.write(f"**End:** {actual_end if actual_end else '⏳ Not Completed'}")
    
    st.markdown("---")
    
    # Email Body
    st.markdown("#### 📧 Email Body / Additional Information")
    email_body = record.get('email_body', '')
    if email_body:
        st.text_area(
            "Content",
            value=email_body,
            height=150,
            disabled=True,
            key=f"email_body_{record.get('id')}"
        )
    else:
        st.info("No email body or additional information provided.")
    
    st.markdown("---")
    
    # Action buttons
    render_uat_action_buttons(record, is_manager)

def render_uat_action_buttons(record, is_manager):
    """Render action buttons for UAT record"""
    if is_manager:
        # Manager can only copy email body
        if st.button("📋 Copy Email Body", key=f"copy_uat_{record.get('id')}", use_container_width=True):
            email_body = record.get('email_body', '')
            if email_body:
                st.code(email_body, language=None)
                st.success("✅ Email body displayed above - you can copy it manually")
            else:
                st.info("No email body to copy")
    else:
        # Other users can edit/delete/copy
        col_edit, col_delete, col_copy = st.columns(3)
        
        with col_edit:
            if st.button("✏️ Edit", key=f"edit_uat_{record.get('id')}", use_container_width=True):
                st.session_state[f"edit_uat_{record.get('id')}"] = True
                st.info("✏️ Edit functionality - Coming soon!")
        
        with col_delete:
            if st.button("🗑️ Delete", key=f"delete_uat_{record.get('id')}", use_container_width=True):
                # Delete confirmation
                confirm_key = f"confirm_delete_{record.get('id')}"
                if st.session_state.get(confirm_key, False):
                    success, message = delete_uat_record_service(record.get('id'))
                    if success:
                        st.success(f"✅ {message}")
                        if confirm_key in st.session_state:
                            del st.session_state[confirm_key]
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.session_state[confirm_key] = True
                    st.warning("⚠️ Click Delete again to confirm!")
        
        with col_copy:
            if st.button("📋 Copy Email Body", key=f"copy_uat_{record.get('id')}", use_container_width=True):
                email_body = record.get('email_body', '')
                if email_body:
                    st.code(email_body, language=None)
                    st.success("✅ Email body displayed above - you can copy it manually")
                else:
                    st.info("No email body to copy")