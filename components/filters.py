# components/filters.py
"""
Filter components for allocation and UAT dashboards
COMPLETE VERSION - All filter functions
"""
import streamlit as st
from datetime import datetime


# ============== ALLOCATION FILTERS ==============

def render_allocation_filters(allocations, show_user_filter=True, key_suffix="", return_filters=False):
    """
    Render comprehensive allocation filters
    
    Args:
        allocations: List of allocation records
        show_user_filter: Whether to show user filter (default True)
        key_suffix: Suffix for widget keys to avoid conflicts
        return_filters: If True, return filter dict instead of filtered data
    
    Returns:
        Either filtered allocations (list) or filter values (dict) based on return_filters
    """
    
    # Get unique values for filters
    systems = ["All"] + sorted(list(set([a.get('system', 'N/A') for a in allocations if a.get('system')])))
    
    # Trial categories
    category_types = ["All", "Build", "Change Request"]
    
    # Therapeutic areas
    therapeutic_types = ["All"]
    for a in allocations:
        area_type = a.get('therapeutic_area_type', '')
        if not area_type:
            area = a.get('therapeutic_area', 'N/A')
            if 'Others -' in area:
                area_type = 'Others'
            else:
                area_type = area
        if area_type and area_type not in therapeutic_types:
            therapeutic_types.append(area_type)
    therapeutic_types = sorted([t for t in therapeutic_types if t and t != "All"]) 
    therapeutic_types = ["All"] + therapeutic_types
    
    # Engineers
    engineers = ["All"] + sorted(list(set([a.get('test_engineer_name', 'N/A') for a in allocations if a.get('test_engineer_name')])))
    
    # Roles
    roles = ["All"] + sorted(list(set([a.get('role', 'N/A') for a in allocations if a.get('role')])))
    
    # Trial IDs
    trial_ids = ["All"] + sorted(list(set([a.get('trial_id', 'N/A') for a in allocations if a.get('trial_id')])))
    
    # Created By
    created_by_list = ["All"] + sorted(list(set([a.get('created_by', 'N/A') for a in allocations if a.get('created_by')])))
    
    # Build unique keys
    def make_key(base):
        if key_suffix:
            return f"{base}_{key_suffix}"
        else:
            return f"{base}_mgr"  # default suffix
    
    # Filter UI - Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_system = st.selectbox("Filter by System", systems, key=make_key("filter_system"))
    
    with col2:
        filter_category_type = st.selectbox("Filter by Trial Category", category_types, key=make_key("filter_category"))
    
    with col3:
        filter_therapeutic = st.selectbox("Filter by Therapeutic Area", therapeutic_types, key=make_key("filter_therapeutic"))
    
    with col4:
        filter_engineer = st.selectbox("Filter by Test Engineer", engineers, key=make_key("filter_engineer"))
    
    # Filter UI - Row 2
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        filter_role = st.selectbox("Filter by Role", roles, key=make_key("filter_role"))
    
    with col6:
        filter_trial = st.selectbox("Filter by Trial ID", trial_ids, key=make_key("filter_trial"))
    
    with col7:
        if show_user_filter:
            filter_created_by = st.selectbox("Filter by Created By", created_by_list, key=make_key("filter_created_by"))
        else:
            filter_created_by = "All"
    
    # Date range filters
    st.markdown("**Date Range Filter:**")
    col_date1, col_date2, col_date3 = st.columns(3)
    
    with col_date1:
        try:
            all_start_dates = [datetime.strptime(a.get('start_date', '2024-01-01'), '%Y-%m-%d') 
                              for a in allocations if a.get('start_date')]
            all_end_dates = [datetime.strptime(a.get('end_date', '2024-12-31'), '%Y-%m-%d') 
                            for a in allocations if a.get('end_date')]
            min_date = min(all_start_dates) if all_start_dates else datetime.now()
            max_date = max(all_end_dates) if all_end_dates else datetime.now()
        except:
            min_date = datetime.now()
            max_date = datetime.now()
        
        filter_start_date = st.date_input(
            "From Start Date",
            value=None,
            min_value=min_date,
            max_value=max_date,
            help="Filter allocations starting from this date",
            key=make_key("filter_start_date")
        )
    
    with col_date2:
        filter_end_date = st.date_input(
            "To End Date",
            value=None,
            min_value=min_date,
            max_value=max_date,
            help="Filter allocations ending by this date",
            key=make_key("filter_end_date")
        )
    
    with col_date3:
        st.write("")
        st.write("")
        if st.button("🔄 Reset All Filters", use_container_width=True, key=make_key("reset_filters")):
            st.rerun()
    
    # If return_filters is True, return the filter dictionary
    if return_filters:
        return {
            'system': filter_system,
            'category': filter_category_type,
            'therapeutic_area': filter_therapeutic,
            'engineer': filter_engineer,
            'role': filter_role,
            'trial_id': filter_trial,
            'created_by': filter_created_by,
            'start_date': filter_start_date,
            'end_date': filter_end_date
        }
    
    # Otherwise, apply filters and return filtered data
    filtered_allocations = allocations
    
    if filter_system != "All":
        filtered_allocations = [a for a in filtered_allocations if a.get('system') == filter_system]
    
    if filter_category_type != "All":
        if filter_category_type == "Build":
            filtered_allocations = [a for a in filtered_allocations 
                                   if a.get('trial_category_type') == 'Build' or a.get('trial_category') == 'Build']
        elif filter_category_type == "Change Request":
            filtered_allocations = [a for a in filtered_allocations 
                                   if a.get('trial_category_type') == 'Change Request' or 'Change Request' in a.get('trial_category', '')]
    
    if filter_therapeutic != "All":
        if filter_therapeutic == "Others":
            filtered_allocations = [a for a in filtered_allocations 
                                   if a.get('therapeutic_area_type') == 'Others' or 'Others -' in a.get('therapeutic_area', '')]
        else:
            filtered_allocations = [a for a in filtered_allocations 
                                   if a.get('therapeutic_area_type') == filter_therapeutic or 
                                   filter_therapeutic in a.get('therapeutic_area', '')]
    
    if filter_engineer != "All":
        filtered_allocations = [a for a in filtered_allocations if a.get('test_engineer_name') == filter_engineer]
    
    if filter_role != "All":
        filtered_allocations = [a for a in filtered_allocations if a.get('role') == filter_role]
    
    if filter_trial != "All":
        filtered_allocations = [a for a in filtered_allocations if a.get('trial_id') == filter_trial]
    
    if filter_created_by != "All":
        filtered_allocations = [a for a in filtered_allocations if a.get('created_by') == filter_created_by]
    
    if filter_start_date:
        try:
            filtered_allocations = [a for a in filtered_allocations 
                                   if datetime.strptime(a.get('start_date', '2024-01-01'), '%Y-%m-%d').date() >= filter_start_date]
        except:
            pass
    
    if filter_end_date:
        try:
            filtered_allocations = [a for a in filtered_allocations 
                                   if datetime.strptime(a.get('end_date', '2024-12-31'), '%Y-%m-%d').date() <= filter_end_date]
        except:
            pass
    
    return filtered_allocations


# ============== UAT FILTERS ==============

def render_uat_filters(uat_records, show_user_filter=False, key_suffix=""):
    """
    Render UAT filters
    
    Args:
        uat_records: List of UAT records to filter
        show_user_filter: Whether to show user filter (for managers)
        key_suffix: Suffix for widget keys to avoid conflicts
    
    Returns:
        Dictionary with filter values
    """
    
    # Get unique values for filters
    trial_ids = ["All"] + sorted(list(set([r.get('trial_id', 'N/A') for r in uat_records if r.get('trial_id')])))
    
    # Categories
    category_types = ["All", "Build", "Change Request"]
    
    # UAT Status
    uat_status_options = ["All", "Not Started", "In Progress", "Completed", "On Hold", "Cancelled"]
    
    # UAT Results
    uat_result_options = ["All", "Pending", "Pass", "Fail", "Partial Pass"]
    
    # Created By (for managers)
    created_by_list = ["All"] + sorted(list(set([r.get('created_by', 'N/A') for r in uat_records if r.get('created_by')])))
    
    # Build unique keys
    def make_key(base):
        return f"{base}_uat_{key_suffix}" if key_suffix else f"{base}_uat"
    
    # Filter UI
    if show_user_filter:
        col1, col2, col3, col4, col5 = st.columns(5)
    else:
        col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_trial = st.selectbox(
            "Filter by Trial ID", 
            trial_ids, 
            key=make_key("filter_trial")
        )
    
    with col2:
        filter_category = st.selectbox(
            "Filter by Category",
            category_types,
            key=make_key("filter_category")
        )
    
    with col3:
        filter_status = st.selectbox(
            "Filter by Status",
            uat_status_options,
            key=make_key("filter_status")
        )
    
    with col4:
        filter_result = st.selectbox(
            "Filter by Result",
            uat_result_options,
            key=make_key("filter_result")
        )
    
    # User filter for managers
    filter_user = "All"
    if show_user_filter:
        with col5:
            filter_user = st.selectbox(
                "Filter by User",
                created_by_list,
                key=make_key("filter_user")
            )
    
    # Reset button
    col_reset1, col_reset2, col_reset3 = st.columns([2, 1, 2])
    with col_reset2:
        if st.button("🔄 Reset Filters", use_container_width=True, key=make_key("reset_filters")):
            st.rerun()
    
    # Return filter values as dictionary
    filters = {
        'trial_id': filter_trial,
        'category': filter_category,
        'status': filter_status,
        'result': filter_result,
        'user': filter_user
    }
    
    return filters


def render_simple_uat_filters(uat_records, show_user_filter=False):
    """Render simplified UAT filters (for smaller views)"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Get unique trial IDs
        trial_ids = ["All"] + sorted(list(set([r.get('trial_id', 'N/A') for r in uat_records if r.get('trial_id')])))
        filter_trial = st.selectbox("Filter by Trial ID", trial_ids, key="simple_filter_trial_uat")
    
    with col2:
        # Status filter
        filter_status = st.selectbox(
            "Filter by Status",
            ["All", "Not Started", "In Progress", "Completed", "On Hold", "Cancelled"],
            key="simple_filter_status_uat"
        )
    
    # Return filter values as dictionary
    filters = {
        'trial_id': filter_trial,
        'status': filter_status
    }
    
    return filters


# ============== AUDIT FILTERS ==============

def render_audit_filters(audit_logs):
    """Render audit log filters and return filtered logs"""
    
    # Get unique values
    actions = ["All"] + sorted(list(set([log.get('action', 'N/A') for log in audit_logs if log.get('action')])))
    users = ["All"] + sorted(list(set([log.get('username', 'N/A') for log in audit_logs if log.get('username')])))
    pages = ["All"] + sorted(list(set([log.get('page', 'N/A') for log in audit_logs if log.get('page')])))
    
    # Filter UI
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_action = st.selectbox("Filter by Action", actions, key="filter_action_audit")
    
    with col2:
        filter_user = st.selectbox("Filter by User", users, key="filter_user_audit")
    
    with col3:
        filter_page = st.selectbox("Filter by Page", pages, key="filter_page_audit")
    
    # Date filter
    st.markdown("**Date Range Filter:**")
    col_date1, col_date2, col_date3 = st.columns(3)
    
    with col_date1:
        filter_from_date = st.date_input(
            "From Date",
            value=None,
            help="Filter logs from this date",
            key="filter_from_date_audit"
        )
    
    with col_date2:
        filter_to_date = st.date_input(
            "To Date",
            value=None,
            help="Filter logs to this date",
            key="filter_to_date_audit"
        )
    
    with col_date3:
        st.write("")
        st.write("")
        if st.button("🔄 Reset Filters", use_container_width=True, key="reset_filters_audit"):
            st.rerun()
    
    # Apply filters
    filtered_logs = audit_logs
    
    if filter_action != "All":
        filtered_logs = [log for log in filtered_logs if log.get('action') == filter_action]
    
    if filter_user != "All":
        filtered_logs = [log for log in filtered_logs if log.get('username') == filter_user]
    
    if filter_page != "All":
        filtered_logs = [log for log in filtered_logs if log.get('page') == filter_page]
    
    if filter_from_date:
        try:
            filtered_logs = [log for log in filtered_logs 
                            if datetime.strptime(log.get('timestamp', '2024-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S').date() >= filter_from_date]
        except:
            pass
    
    if filter_to_date:
        try:
            filtered_logs = [log for log in filtered_logs 
                            if datetime.strptime(log.get('timestamp', '2024-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S').date() <= filter_to_date]
        except:
            pass
    
    return filtered_logs


# ============== HELPER FUNCTIONS ==============

def apply_allocation_filter_logic(allocations, filters):
    """
    Apply allocation filters manually (helper function)
    
    Args:
        allocations: List of allocations
        filters: Dictionary with filter values
    
    Returns:
        Filtered list of allocations
    """
    filtered = allocations
    
    if filters.get('system') and filters['system'] != "All":
        filtered = [a for a in filtered if a.get('system') == filters['system']]
    
    if filters.get('category') and filters['category'] != "All":
        if filters['category'] == "Build":
            filtered = [a for a in filtered 
                       if a.get('trial_category_type') == 'Build' or a.get('trial_category') == 'Build']
        elif filters['category'] == "Change Request":
            filtered = [a for a in filtered 
                       if a.get('trial_category_type') == 'Change Request' or 'Change Request' in a.get('trial_category', '')]
    
    if filters.get('therapeutic_area') and filters['therapeutic_area'] != "All":
        if filters['therapeutic_area'] == "Others":
            filtered = [a for a in filtered 
                       if a.get('therapeutic_area_type') == 'Others' or 'Others -' in a.get('therapeutic_area', '')]
        else:
            filtered = [a for a in filtered 
                       if a.get('therapeutic_area_type') == filters['therapeutic_area'] or 
                       filters['therapeutic_area'] in a.get('therapeutic_area', '')]
    
    if filters.get('engineer') and filters['engineer'] != "All":
        filtered = [a for a in filtered if a.get('test_engineer_name') == filters['engineer']]
    
    if filters.get('role') and filters['role'] != "All":
        filtered = [a for a in filtered if a.get('role') == filters['role']]
    
    if filters.get('trial_id') and filters['trial_id'] != "All":
        filtered = [a for a in filtered if a.get('trial_id') == filters['trial_id']]
    
    if filters.get('created_by') and filters['created_by'] != "All":
        filtered = [a for a in filtered if a.get('created_by') == filters['created_by']]
    
    if filters.get('start_date'):
        try:
            filtered = [a for a in filtered 
                       if datetime.strptime(a.get('start_date', '2024-01-01'), '%Y-%m-%d').date() >= filters['start_date']]
        except:
            pass
    
    if filters.get('end_date'):
        try:
            filtered = [a for a in filtered 
                       if datetime.strptime(a.get('end_date', '2024-12-31'), '%Y-%m-%d').date() <= filters['end_date']]
        except:
            pass
    
    return filtered


def apply_uat_filter_logic(uat_records, filters):
    """
    Apply UAT filters manually (helper function)
    
    Args:
        uat_records: List of UAT records
        filters: Dictionary with filter values
    
    Returns:
        Filtered list of UAT records
    """
    filtered = uat_records
    
    if filters.get('trial_id') and filters['trial_id'] != "All":
        filtered = [r for r in filtered if r.get('trial_id') == filters['trial_id']]
    
    if filters.get('category') and filters['category'] != "All":
        if filters['category'] == "Build":
            filtered = [r for r in filtered if r.get('category_type') == 'Build']
        elif filters['category'] == "Change Request":
            filtered = [r for r in filtered if r.get('category_type') == 'Change Request']
    
    if filters.get('status') and filters['status'] != "All":
        filtered = [r for r in filtered if r.get('status') == filters['status']]
    
    if filters.get('result') and filters['result'] != "All":
        filtered = [r for r in filtered if r.get('result') == filters['result']]
    
    if filters.get('user') and filters['user'] != "All":
        filtered = [r for r in filtered if r.get('created_by') == filters['user']]
    
    return filtered


def apply_audit_filter_logic(audit_logs, filters):
    """
    Apply audit filters manually (helper function)
    
    Args:
        audit_logs: List of audit logs
        filters: Dictionary with filter values
    
    Returns:
        Filtered list of audit logs
    """
    filtered = audit_logs
    
    if filters.get('action') and filters['action'] != "All":
        filtered = [log for log in filtered if log.get('action') == filters['action']]
    
    if filters.get('user') and filters['user'] != "All":
        filtered = [log for log in filtered if log.get('username') == filters['user']]
    
    if filters.get('page') and filters['page'] != "All":
        filtered = [log for log in filtered if log.get('page') == filters['page']]
    
    if filters.get('from_date'):
        try:
            filtered = [log for log in filtered 
                       if datetime.strptime(log.get('timestamp', '2024-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S').date() >= filters['from_date']]
        except:
            pass
    
    if filters.get('to_date'):
        try:
            filtered = [log for log in filtered 
                       if datetime.strptime(log.get('timestamp', '2024-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S').date() <= filters['to_date']]
        except:
            pass
    
    return filtered