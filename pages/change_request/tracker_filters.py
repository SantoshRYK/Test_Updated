# pages/change_request/tracker_filters.py
"""
Change Request Tracker Filters
"""
import streamlit as st
from typing import List, Dict

def apply_filters(
    records: List[Dict],
    trial_name_dropdown: str,
    trial_name_text: str,
    cr_no_dropdown: str,
    cr_no_text: str,
    category_dropdown: str,
    version_dropdown: str,
    version_text: str
) -> List[Dict]:
    """
    Apply all filters to change requests
    
    Args:
        records: List of change request records
        trial_name_dropdown: Selected trial name from dropdown
        trial_name_text: Text search for trial name
        cr_no_dropdown: Selected CR No from dropdown
        cr_no_text: Text search for CR No
        category_dropdown: Selected category
        version_dropdown: Selected version from dropdown
        version_text: Text search for version
    
    Returns:
        Filtered list of records
    """
    filtered = records
    
    # Dropdown filters
    if trial_name_dropdown != "All":
        filtered = [r for r in filtered if r.get('trial_name') == trial_name_dropdown]
    
    if cr_no_dropdown != "All":
        filtered = [r for r in filtered if r.get('cr_no') == cr_no_dropdown]
    
    if category_dropdown != "All":
        filtered = [r for r in filtered if r.get('category') == category_dropdown]
    
    if version_dropdown != "All":
        filtered = [r for r in filtered if r.get('current_version') == version_dropdown]
    
    # Text search filters (case-insensitive, partial match)
    if trial_name_text:
        trial_text_lower = trial_name_text.lower()
        filtered = [r for r in filtered if trial_text_lower in r.get('trial_name', '').lower()]
    
    if cr_no_text:
        cr_text_lower = cr_no_text.lower()
        filtered = [r for r in filtered if cr_text_lower in r.get('cr_no', '').lower()]
    
    if version_text:
        version_text_lower = version_text.lower()
        filtered = [r for r in filtered if version_text_lower in r.get('current_version', '').lower()]
    
    return filtered

def render_filter_section(records: List[Dict]) -> Dict:
    """
    Render filter UI and return filter values
    
    Args:
        records: List of all records
    
    Returns:
        Dictionary of filter values
    """
    st.subheader("🔍 Filters")
    
    # Get unique values for dropdowns
    trial_names = ["All"] + sorted(list(set([r.get('trial_name', 'N/A') for r in records if r.get('trial_name')])))
    cr_nos = ["All"] + sorted(list(set([r.get('cr_no', 'N/A') for r in records if r.get('cr_no')])))
    categories = ["All", "Rule Change", "Form Change"]
    versions = ["All"] + sorted(list(set([r.get('current_version', 'N/A') for r in records if r.get('current_version')])))
    
    # Row 1: Dropdown filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        trial_name_dropdown = st.selectbox(
            "Trial Name",
            trial_names,
            key="filter_trial_dropdown"
        )
    
    with col2:
        cr_no_dropdown = st.selectbox(
            "CR No",
            cr_nos,
            key="filter_cr_dropdown"
        )
    
    with col3:
        category_dropdown = st.selectbox(
            "Category",
            categories,
            key="filter_category_dropdown"
        )
    
    with col4:
        version_dropdown = st.selectbox(
            "Current Version",
            versions,
            key="filter_version_dropdown"
        )
    
    # Row 2: Text search filters
    st.markdown("##### 🔎 Quick Search")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        trial_name_text = st.text_input(
            "Search Trial Name",
            placeholder="Type to search...",
            key="filter_trial_text"
        )
    
    with col2:
        cr_no_text = st.text_input(
            "Search CR No",
            placeholder="Type to search...",
            key="filter_cr_text"
        )
    
    with col3:
        st.write("")  # Spacing
    
    with col4:
        version_text = st.text_input(
            "Search Version",
            placeholder="Type to search...",
            key="filter_version_text"
        )
    
    # Clear filters button
    col_clear1, col_clear2, col_clear3 = st.columns([1, 1, 4])
    
    with col_clear1:
        if st.button("🔄 Clear All Filters", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key.startswith('filter_'):
                    del st.session_state[key]
            st.rerun()
    
    with col_clear2:
        # Show active filters count
        active_filters = 0
        if trial_name_dropdown != "All": active_filters += 1
        if cr_no_dropdown != "All": active_filters += 1
        if category_dropdown != "All": active_filters += 1
        if version_dropdown != "All": active_filters += 1
        if trial_name_text: active_filters += 1
        if cr_no_text: active_filters += 1
        if version_text: active_filters += 1
        
        if active_filters > 0:
            st.info(f"🎯 {active_filters} filter(s) active")
    
    return {
        'trial_name_dropdown': trial_name_dropdown,
        'trial_name_text': trial_name_text,
        'cr_no_dropdown': cr_no_dropdown,
        'cr_no_text': cr_no_text,
        'category_dropdown': category_dropdown,
        'version_dropdown': version_dropdown,
        'version_text': version_text
    }