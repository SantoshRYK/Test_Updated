# pages/change_request/tracker_utils.py
"""
Change Request Tracker Utility Functions
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict
from utils.excel_handler import convert_to_excel
from utils.auth import get_current_user, get_current_role

def prepare_excel_data(records: List[Dict]) -> List[Dict]:
    """
    Prepare change request data for Excel export
    
    Args:
        records: List of change request records
    
    Returns:
        List of dictionaries formatted for Excel
    """
    excel_data = []
    
    for record in records:
        excel_data.append({
            "Trial Name": record.get('trial_name', 'N/A'),
            "CR No": record.get('cr_no', 'N/A'),
            "Category": record.get('category', 'N/A'),
            "Form/Event Name": record.get('form_event_name', 'N/A'),
            "Item/Rule Name": record.get('item_rule_name', 'N/A'),
            "Requirements": record.get('requirements', 'N/A'),
            "Version Changes": record.get('version_changes', 'N/A'),
            "Protocol Amendment": record.get('protocol_amendment', 'N/A'),
            "Retrospective/Case Book": record.get('retrospective_case_book', 'N/A'),
            "CDB Impact": record.get('cdb_impact', 'N/A'),
            "Item Def. Impact": record.get('item_def_impact', 'N/A'),
            "Datacore Impact": record.get('datacore_impact', 'N/A'),
            "Comments": record.get('comments', 'N/A'),
            "Current Version": record.get('current_version', 'N/A'),
            "Impacted E2B/Vsec": record.get('impacted_e2b_vsec', 'N/A'),
            "Impacted RTSM": record.get('impacted_rtsm', 'N/A'),
            "RTSM Comments": record.get('rtsm_comments', 'N/A'),
            "Created By": record.get('created_by', 'N/A'),
            "Created At": record.get('created_at', 'N/A')
        })
    
    return excel_data

def render_export_button(records: List[Dict], current_role: str):
    """
    Render export to Excel button (only for authorized roles)
    
    Args:
        records: List of records to export
        current_role: Current user's role
    """
    if current_role in ["superuser", "cdp", "manager"]:
        if records:
            excel_data = prepare_excel_data(records)
            excel_output = convert_to_excel(excel_data)
            
            if excel_output:
                st.download_button(
                    label="📥 Export Filtered Data",
                    data=excel_output,
                    file_name=f"change_requests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary"
                )
        else:
            st.info("No data to export")
    else:
        st.info("📥 Export available for CDP/Manager/Superuser")

def render_statistics(records: List[Dict]):
    """
    Render statistics cards
    
    Args:
        records: List of change request records
    """
    col1, col2, col3, col4 = st.columns(4)
    
    total_records = len(records)
    rule_changes = len([r for r in records if 'Rule' in r.get('category', '')])
    form_changes = len([r for r in records if 'Form' in r.get('category', '')])
    
    # Count impacts
    cdb_impacts = len([r for r in records if r.get('cdb_impact') == 'Yes'])
    
    with col1:
        st.metric("📊 Total Entries", total_records)
    
    with col2:
        st.metric("📋 Rule Changes", rule_changes)
    
    with col3:
        st.metric("📝 Form Changes", form_changes)
    
    with col4:
        st.metric("💾 CDB Impacts", cdb_impacts)

def render_data_table(records: List[Dict]):
    """
    Render change requests as a table
    
    Args:
        records: List of change request records
    """
    if not records:
        st.info("No records to display")
        return
    
    # Prepare data for table
    table_data = []
    
    for record in records:
        table_data.append({
            'Trial Name': record.get('trial_name', 'N/A'),
            'CR No': record.get('cr_no', 'N/A'),
            'Category': record.get('category', 'N/A'),
            'Form/Event Name': record.get('form_event_name', 'N/A'),
            'Item/Rule Names': record.get('item_rule_name', 'N/A'),
            'Requirements': record.get('requirements', 'N/A')[:50] + '...' if len(record.get('requirements', '')) > 50 else record.get('requirements', 'N/A'),
            'Version Changes': record.get('version_changes', 'N/A'),
            'Protocol Amendment': record.get('protocol_amendment', 'N/A'),
            'CDB Impact': record.get('cdb_impact', 'N/A'),
            'Item Def. Impact': record.get('item_def_impact', 'N/A'),
            'Datacore Impact': record.get('datacore_impact', 'N/A'),
        })
    
    # Create DataFrame
    df = pd.DataFrame(table_data)
    
    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=400
    )

def can_edit_delete(record: Dict, current_user: str, current_role: str) -> bool:
    """
    Check if user can edit/delete a record
    
    Args:
        record: Change request record
        current_user: Current username
        current_role: Current user role
    
    Returns:
        True if user can edit/delete
    """
    # Superuser and CDP can edit/delete all
    if current_role in ['superuser', 'cdp', 'manager']:
        return True
    
    # Regular users can only edit/delete their own records
    return record.get('created_by') == current_user

def show_record_count(filtered_count: int, total_count: int):
    """
    Show record count with filters applied
    
    Args:
        filtered_count: Number of filtered records
        total_count: Total number of records
    """
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if filtered_count == total_count:
            st.markdown(f"### 📋 Showing All {total_count} Change Requests")
        else:
            st.markdown(f"### 📋 Showing {filtered_count} of {total_count} Change Requests")
    
    with col2:
        # Entries per page selector
        entries_per_page = st.selectbox(
            "Show",
            [10, 25, 50, 100],
            index=1,
            key="entries_per_page",
            label_visibility="collapsed"
        )
        st.caption("entries per page")

def get_pagination_range(total_records: int, entries_per_page: int, current_page: int):
    """
    Calculate pagination range
    
    Args:
        total_records: Total number of records
        entries_per_page: Number of entries per page
        current_page: Current page number (0-indexed)
    
    Returns:
        Tuple of (start_index, end_index)
    """
    start_idx = current_page * entries_per_page
    end_idx = min(start_idx + entries_per_page, total_records)
    return start_idx, end_idx

def render_pagination(total_records: int, entries_per_page: int):
    """
    Render pagination controls
    
    Args:
        total_records: Total number of records
        entries_per_page: Number of entries per page
    
    Returns:
        Current page number (0-indexed)
    """
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    
    total_pages = (total_records + entries_per_page - 1) // entries_per_page
    
    if total_pages <= 1:
        return 0
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("⏮️ First", disabled=st.session_state.current_page == 0, use_container_width=True):
            st.session_state.current_page = 0
            st.rerun()
    
    with col2:
        if st.button("◀️ Previous", disabled=st.session_state.current_page == 0, use_container_width=True):
            st.session_state.current_page -= 1
            st.rerun()
    
    with col3:
        st.markdown(f"<div style='text-align: center; padding: 8px;'>Page {st.session_state.current_page + 1} of {total_pages}</div>", unsafe_allow_html=True)
    
    with col4:
        if st.button("Next ▶️", disabled=st.session_state.current_page >= total_pages - 1, use_container_width=True):
            st.session_state.current_page += 1
            st.rerun()
    
    with col5:
        if st.button("Last ⏭️", disabled=st.session_state.current_page >= total_pages - 1, use_container_width=True):
            st.session_state.current_page = total_pages - 1
            st.rerun()
    
    # Show record range
    start_idx, end_idx = get_pagination_range(total_records, entries_per_page, st.session_state.current_page)
    st.caption(f"Showing {start_idx + 1} to {end_idx} of {total_records} entries")
    
    return st.session_state.current_page

def format_field_value(value, max_length=50):
    """
    Format field value for display (truncate if too long)
    
    Args:
        value: Field value
        max_length: Maximum length before truncation
    
    Returns:
        Formatted string
    """
    if not value or value == "N/A":
        return "N/A"
    
    value_str = str(value)
    
    if len(value_str) <= max_length:
        return value_str
    
    return value_str[:max_length] + "..."