# pages/change_request/tracker_main.py
"""
Change Request Tracker Main Page
Matches the design from screenshots with Add New Entry modal
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List

from utils.auth import get_current_user, get_current_role
from utils.database import load_change_requests
from services.change_request_service import (
    get_filtered_change_requests,
    create_change_request,
    update_change_request_record,
    delete_change_request_record,
    get_unique_values
)
from pages.change_request.tracker_filters import apply_filters, render_filter_section
from pages.change_request.tracker_utils import (
    render_statistics,
    render_data_table,
    render_export_button,
    can_edit_delete,
    show_record_count,
    render_pagination,
    get_pagination_range,
    format_field_value
)
from config import CR_CATEGORIES, CR_VERSION_OPTIONS, CR_IMPACT_OPTIONS


def render_change_request_tracker():
    """Main Change Request Tracker page"""
    
    # ✅ ACCESS CONTROL
    current_user = get_current_user()
    current_role = get_current_role()
    
    # Check if user has access
    if current_role not in ['superuser', 'cdp', 'manager']:
        st.error("❌ Access Denied")
        st.warning("⚠️ Only CDP, Manager, and Superuser roles can access the Change Request Tracker.")
        st.info("📧 Please contact your administrator if you need access.")
        
        if st.button("⬅️ Back to Home"):
            st.session_state.current_page = "home"
            st.rerun()
        st.stop()
    
    st.title("🔄 Change Request Tracker")
    st.markdown("---")
    
    # Role-based info banner
    if current_role == 'cdp':
        st.info("👤 **CDP Access:** You can create, edit, and delete your own change requests.")
    elif current_role == 'manager':
        st.info("👨‍💼 **Manager Access:** You can view all change requests and download reports. (Read-only)")
    elif current_role == 'superuser':
        st.success("👑 **Superuser Access:** Full access to all change requests.")
    
    # Back button
    if st.button("⬅️ Back to Home", key="back_to_home"):
        st.session_state.current_page = "home"
        st.rerun()
    
    st.markdown("---")
    
    # ✅ RENDER MODAL FIRST IF OPEN
    if st.session_state.get('show_add_modal', False):
        render_add_entry_modal()
        return  # Stop rendering rest of page when modal is open
    
    # Load data based on role
    if current_role == 'manager':
        # Manager sees all but read-only
        all_records = load_change_requests()
        st.warning("📋 **View-Only Mode** - You can view and filter data, but cannot create or edit entries.")
    else:
        # CDP and Superuser
        all_records = get_filtered_change_requests(current_role, current_user)
    
    # Top action buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # Only CDP and Superuser can add new entries
        if current_role in ['cdp', 'superuser']:
            if st.button("➕ Add New Entry", use_container_width=True, type="primary", key="add_new_btn"):
                st.session_state.show_add_modal = True
                st.rerun()
        else:
            st.button("➕ Add New Entry", use_container_width=True, disabled=True, key="add_new_btn_disabled")
            st.caption("CDP/Superuser only")
    
    with col2:
        # Manager and Superuser can export
        if current_role in ['manager', 'superuser']:
            render_export_button(all_records, current_role)
        else:
            st.info("📥 Download: Manager+")
    
    with col3:
        if st.button("🔄 Clear Filters", use_container_width=True, key="clear_filters_top"):
            for key in list(st.session_state.keys()):
                if key.startswith('filter_'):
                    del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # Show statistics
    render_statistics(all_records)
    
    st.markdown("---")
    
    # Render filters
    if all_records:
        filter_values = render_filter_section(all_records)
        
        st.markdown("---")
        
        # Apply filters
        filtered_records = apply_filters(
            all_records,
            filter_values['trial_name_dropdown'],
            filter_values['trial_name_text'],
            filter_values['cr_no_dropdown'],
            filter_values['cr_no_text'],
            filter_values['category_dropdown'],
            filter_values['version_dropdown'],
            filter_values['version_text']
        )
        
        # Show record count
        show_record_count(len(filtered_records), len(all_records))
        
        st.markdown("---")
        
        # Get entries per page
        entries_per_page = st.session_state.get('entries_per_page', 25)
        
        # Render pagination
        if filtered_records:
            current_page = render_pagination(len(filtered_records), entries_per_page)
            start_idx, end_idx = get_pagination_range(len(filtered_records), entries_per_page, current_page)
            
            # Get paginated records
            paginated_records = filtered_records[start_idx:end_idx]
            
            # Search all columns input
            col_search1, col_search2 = st.columns([3, 1])
            with col_search1:
                search_all = st.text_input(
                    "🔎 Search all columns",
                    placeholder="Type to search across all fields...",
                    key="search_all_columns"
                )
            
            st.markdown("---")
            
            # Apply search across all columns if provided
            if search_all:
                search_lower = search_all.lower()
                paginated_records = [
                    r for r in paginated_records
                    if any(search_lower in str(v).lower() for v in r.values())
                ]
            
            # Render table
            render_data_table(paginated_records)
            
            st.markdown("---")
            
            # Render detailed cards
            st.subheader("📋 Detailed View")
            
            for record in paginated_records:
                render_record_card(record, current_user, current_role)
        else:
            st.info("📝 No records match the selected filters")
    
    else:
        st.info("📝 No change requests found. Click 'Add New Entry' to create your first entry!")


def render_add_entry_modal():
    """Render Add New Entry modal dialog"""
    
    # Modal header
    col_title, col_close = st.columns([5, 1])
    
    with col_title:
        st.markdown("## ➕ Add New Entry")
    
    with col_close:
        if st.button("❌ Close", key="close_modal", use_container_width=True):
            st.session_state.show_add_modal = False
            st.rerun()
    
    st.markdown("---")
    
    # Form
    with st.form("add_change_request_form", clear_on_submit=False):
        # Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            trial_name = st.text_input(
                "Trial Name *",
                placeholder="Enter trial name",
                key="add_trial_name"
            )
        
        with col2:
            cr_no = st.text_input(
                "CR No *",
                placeholder="e.g., CR001",
                key="add_cr_no"
            )
        
        # Row 2
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.selectbox(
                "Category *",
                ["Select Category"] + CR_CATEGORIES,
                key="add_category"
            )
        
        with col2:
            form_event_name = st.text_input(
                "Form/Event Name",
                placeholder="Enter form or event name",
                key="add_form_event"
            )
        
        # Row 3
        item_rule_name = st.text_area(
            "Item/Rule Names",
            placeholder="Enter item or rule names",
            height=100,
            key="add_item_rule"
        )
        
        # Row 4
        requirements = st.text_area(
            "Requirements",
            placeholder="Enter requirements",
            height=100,
            key="add_requirements"
        )
        
        # Row 5
        col1, col2 = st.columns(2)
        
        with col1:
            version_changes = st.selectbox(
                "Version/Versionless Changes",
                ["Select"] + CR_VERSION_OPTIONS,
                key="add_version_changes"
            )
        
        with col2:
            protocol_amendment = st.text_input(
                "Protocol Amendment",
                placeholder="Enter protocol amendment",
                key="add_protocol"
            )
        
        # Row 6
        retrospective_case_book = st.text_area(
            "Retrospective/Case Book Version/Rules_Batchrun",
            placeholder="Enter details",
            height=80,
            key="add_retrospective"
        )
        
        # Row 7 - Impact fields
        st.markdown("#### Impact Assessment")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cdb_impact = st.selectbox(
                "CDB Impact",
                CR_IMPACT_OPTIONS,
                key="add_cdb_impact"
            )
        
        with col2:
            item_def_impact = st.selectbox(
                "Item Definition Impact",
                CR_IMPACT_OPTIONS,
                key="add_item_def_impact"
            )
        
        with col3:
            datacore_impact = st.selectbox(
                "Datacore Impact",
                CR_IMPACT_OPTIONS,
                key="add_datacore_impact"
            )
        
        # Row 8
        comments = st.text_area(
            "Comments",
            placeholder="Enter any comments",
            height=80,
            key="add_comments"
        )
        
        # Row 9
        col1, col2 = st.columns(2)
        
        with col1:
            current_version = st.text_input(
                "Current Version",
                placeholder="Enter current version",
                key="add_current_version"
            )
        
        with col2:
            impacted_e2b_vsec = st.selectbox(
                "Impacted E2B/Vsec",
                CR_IMPACT_OPTIONS,
                key="add_e2b_vsec"
            )
        
        # Row 10
        col1, col2 = st.columns(2)
        
        with col1:
            impacted_rtsm = st.selectbox(
                "Impacted RTSM",
                CR_IMPACT_OPTIONS,
                key="add_rtsm"
            )
        
        with col2:
            rtsm_comments = st.text_input(
                "RTSM Comments",
                placeholder="Enter RTSM comments",
                key="add_rtsm_comments"
            )
        
        st.markdown("---")
        
        # Submit button
        submitted = st.form_submit_button(
            "💾 Save Entry",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            # Validation
            errors = []
            
            if not trial_name or not trial_name.strip():
                errors.append("Trial Name is required")
            
            if not cr_no or not cr_no.strip():
                errors.append("CR No is required")
            
            if category == "Select Category":
                errors.append("Category is required")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Create change request
                change_request_data = {
                    "trial_name": trial_name.strip(),
                    "cr_no": cr_no.strip(),
                    "category": category,
                    "form_event_name": form_event_name.strip() if form_event_name else "",
                    "item_rule_name": item_rule_name.strip() if item_rule_name else "",
                    "requirements": requirements.strip() if requirements else "",
                    "version_changes": version_changes if version_changes != "Select" else "",
                    "protocol_amendment": protocol_amendment.strip() if protocol_amendment else "",
                    "retrospective_case_book": retrospective_case_book.strip() if retrospective_case_book else "",
                    "cdb_impact": cdb_impact,
                    "item_def_impact": item_def_impact,
                    "datacore_impact": datacore_impact,
                    "comments": comments.strip() if comments else "",
                    "current_version": current_version.strip() if current_version else "",
                    "impacted_e2b_vsec": impacted_e2b_vsec,
                    "impacted_rtsm": impacted_rtsm,
                    "rtsm_comments": rtsm_comments.strip() if rtsm_comments else ""
                }
                
                if create_change_request(change_request_data):
                    st.success("✅ Change Request added successfully!")
                    st.balloons()
                    
                    # Close modal and refresh
                    st.session_state.show_add_modal = False
                    
                    # Wait a moment to show success
                    import time
                    time.sleep(1)
                    
                    st.rerun()
                else:
                    st.error("❌ Failed to add Change Request. Please try again.")


def render_record_card(record: Dict, current_user: str, current_role: str):
    """Render individual change request card with edit/delete options"""
    record_id = record.get('id')
    category = record.get('category', 'N/A')
    category_emoji = "📋" if "Rule" in category else "📝"
    
    # Check if user can edit/delete
    can_modify = can_edit_delete(record, current_user, current_role)
    
    # Check if in edit mode
    edit_mode = st.session_state.get(f"edit_mode_{record_id}", False)
    
    # Card title
    trial_name = record.get('trial_name', 'N/A')
    cr_no = record.get('cr_no', 'N/A')
    
    with st.expander(f"{category_emoji} [{trial_name}] - {cr_no} - {category}", expanded=edit_mode):
        if edit_mode:
            # EDIT MODE
            render_edit_form(record, current_user)
        else:
            # VIEW MODE
            render_record_view(record, current_user, current_role, can_modify)


def render_record_view(record: Dict, current_user: str, current_role: str, can_modify: bool):
    """Render record in view mode"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Trial Name:** {record.get('trial_name', 'N/A')}")
        st.write(f"**CR No:** {record.get('cr_no', 'N/A')}")
        st.write(f"**Category:** {record.get('category', 'N/A')}")
        st.write(f"**Form/Event Name:** {record.get('form_event_name', 'N/A')}")
        st.write(f"**Item/Rule Names:** {format_field_value(record.get('item_rule_name', 'N/A'), 100)}")
        st.write(f"**Requirements:** {format_field_value(record.get('requirements', 'N/A'), 100)}")
        st.write(f"**Version Changes:** {record.get('version_changes', 'N/A')}")
        st.write(f"**Protocol Amendment:** {record.get('protocol_amendment', 'N/A')}")
        st.write(f"**Retrospective/Case Book:** {format_field_value(record.get('retrospective_case_book', 'N/A'), 100)}")
    
    with col2:
        st.markdown("#### Impact Assessment")
        st.write(f"**CDB Impact:** {record.get('cdb_impact', 'N/A')}")
        st.write(f"**Item Def. Impact:** {record.get('item_def_impact', 'N/A')}")
        st.write(f"**Datacore Impact:** {record.get('datacore_impact', 'N/A')}")
        
        st.markdown("---")
        
        st.write(f"**Comments:** {format_field_value(record.get('comments', 'N/A'), 100)}")
        st.write(f"**Current Version:** {record.get('current_version', 'N/A')}")
        st.write(f"**Impacted E2B/Vsec:** {record.get('impacted_e2b_vsec', 'N/A')}")
        st.write(f"**Impacted RTSM:** {record.get('impacted_rtsm', 'N/A')}")
        st.write(f"**RTSM Comments:** {format_field_value(record.get('rtsm_comments', 'N/A'), 100)}")
    
    st.markdown("---")
    st.caption(f"Created by: {record.get('created_by', 'N/A')} | Created at: {record.get('created_at', 'N/A')}")
    
    if record.get('updated_at') and record.get('updated_at') != record.get('created_at'):
        st.caption(f"Last updated: {record.get('updated_at', 'N/A')} by {record.get('updated_by', 'N/A')}")
    
    # Action buttons
    if can_modify:
        st.markdown("---")
        col_edit, col_delete = st.columns(2)
        
        with col_edit:
            if st.button("✏️ Edit", key=f"edit_btn_{record.get('id')}", use_container_width=True):
                st.session_state[f"edit_mode_{record.get('id')}"] = True
                st.rerun()
        
        with col_delete:
            if st.button("🗑️ Delete", key=f"delete_btn_{record.get('id')}", use_container_width=True):
                if st.session_state.get(f"confirm_delete_{record.get('id')}", False):
                    if delete_change_request_record(record.get('id'), record):
                        st.success("✅ Change Request deleted successfully")
                        del st.session_state[f"confirm_delete_{record.get('id')}"]
                        st.rerun()
                else:
                    st.session_state[f"confirm_delete_{record.get('id')}"] = True
                    st.warning("⚠️ Click Delete again to confirm!")


def render_edit_form(record: Dict, current_user: str):
    """Render edit form for record"""
    st.info("✏️ **Edit Mode** - Make your changes below")
    
    record_id = record.get('id')
    
    col1, col2 = st.columns(2)
    
    with col1:
        trial_name = st.text_input(
            "Trial Name *",
            value=record.get('trial_name', ''),
            key=f"edit_trial_{record_id}"
        )
        
        cr_no = st.text_input(
            "CR No *",
            value=record.get('cr_no', ''),
            key=f"edit_cr_{record_id}"
        )
        
        category_index = 0
        if record.get('category') in CR_CATEGORIES:
            category_index = CR_CATEGORIES.index(record.get('category'))
        
        category = st.selectbox(
            "Category *",
            CR_CATEGORIES,
            index=category_index,
            key=f"edit_category_{record_id}"
        )
        
        form_event_name = st.text_input(
            "Form/Event Name",
            value=record.get('form_event_name', ''),
            key=f"edit_form_{record_id}"
        )
        
        item_rule_name = st.text_area(
            "Item/Rule Names",
            value=record.get('item_rule_name', ''),
            height=100,
            key=f"edit_item_{record_id}"
        )
        
        requirements = st.text_area(
            "Requirements",
            value=record.get('requirements', ''),
            height=100,
            key=f"edit_req_{record_id}"
        )
        
        version_index = 0
        if record.get('version_changes') in CR_VERSION_OPTIONS:
            version_index = CR_VERSION_OPTIONS.index(record.get('version_changes'))
        
        version_changes = st.selectbox(
            "Version/Versionless Changes",
            CR_VERSION_OPTIONS,
            index=version_index,
            key=f"edit_version_{record_id}"
        )
    
    with col2:
        protocol_amendment = st.text_input(
            "Protocol Amendment",
            value=record.get('protocol_amendment', ''),
            key=f"edit_protocol_{record_id}"
        )
        
        retrospective_case_book = st.text_area(
            "Retrospective/Case Book",
            value=record.get('retrospective_case_book', ''),
            height=80,
            key=f"edit_retro_{record_id}"
        )
        
        st.markdown("#### Impact Assessment")
        
        cdb_impact = st.selectbox(
            "CDB Impact",
            CR_IMPACT_OPTIONS,
            index=CR_IMPACT_OPTIONS.index(record.get('cdb_impact', 'No')),
            key=f"edit_cdb_{record_id}"
        )
        
        item_def_impact = st.selectbox(
            "Item Definition Impact",
            CR_IMPACT_OPTIONS,
            index=CR_IMPACT_OPTIONS.index(record.get('item_def_impact', 'No')),
            key=f"edit_item_def_{record_id}"
        )
        
        datacore_impact = st.selectbox(
            "Datacore Impact",
            CR_IMPACT_OPTIONS,
            index=CR_IMPACT_OPTIONS.index(record.get('datacore_impact', 'No')),
            key=f"edit_datacore_{record_id}"
        )
        
        comments = st.text_area(
            "Comments",
            value=record.get('comments', ''),
            height=80,
            key=f"edit_comments_{record_id}"
        )
        
        current_version = st.text_input(
            "Current Version",
            value=record.get('current_version', ''),
            key=f"edit_curr_ver_{record_id}"
        )
        
        impacted_e2b_vsec = st.selectbox(
            "Impacted E2B/Vsec",
            CR_IMPACT_OPTIONS,
            index=CR_IMPACT_OPTIONS.index(record.get('impacted_e2b_vsec', 'No')),
            key=f"edit_e2b_{record_id}"
        )
        
        impacted_rtsm = st.selectbox(
            "Impacted RTSM",
            CR_IMPACT_OPTIONS,
            index=CR_IMPACT_OPTIONS.index(record.get('impacted_rtsm', 'No')),
            key=f"edit_rtsm_{record_id}"
        )
        
        rtsm_comments = st.text_input(
            "RTSM Comments",
            value=record.get('rtsm_comments', ''),
            key=f"edit_rtsm_com_{record_id}"
        )
    
    st.markdown("---")
    
    # Action buttons
    col_save, col_cancel = st.columns(2)
    
    with col_save:
        if st.button("💾 Save Changes", key=f"save_edit_{record_id}", use_container_width=True, type="primary"):
            # Validation
            errors = []
            
            if not trial_name or not trial_name.strip():
                errors.append("Trial Name is required")
            
            if not cr_no or not cr_no.strip():
                errors.append("CR No is required")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Update record
                updated_data = {
                    "trial_name": trial_name.strip(),
                    "cr_no": cr_no.strip(),
                    "category": category,
                    "form_event_name": form_event_name.strip() if form_event_name else "",
                    "item_rule_name": item_rule_name.strip() if item_rule_name else "",
                    "requirements": requirements.strip() if requirements else "",
                    "version_changes": version_changes,
                    "protocol_amendment": protocol_amendment.strip() if protocol_amendment else "",
                    "retrospective_case_book": retrospective_case_book.strip() if retrospective_case_book else "",
                    "cdb_impact": cdb_impact,
                    "item_def_impact": item_def_impact,
                    "datacore_impact": datacore_impact,
                    "comments": comments.strip() if comments else "",
                    "current_version": current_version.strip() if current_version else "",
                    "impacted_e2b_vsec": impacted_e2b_vsec,
                    "impacted_rtsm": impacted_rtsm,
                    "rtsm_comments": rtsm_comments.strip() if rtsm_comments else ""
                }
                
                if update_change_request_record(record_id, updated_data):
                    st.success("✅ Change Request updated successfully!")
                    del st.session_state[f"edit_mode_{record_id}"]
                    st.rerun()
                else:
                    st.error("❌ Failed to update Change Request")
    
    with col_cancel:
        if st.button("❌ Cancel", key=f"cancel_edit_{record_id}", use_container_width=True):
            del st.session_state[f"edit_mode_{record_id}"]
            st.rerun()


# Main render function
def render():
    """Main entry point for Change Request Tracker"""
    render_change_request_tracker()