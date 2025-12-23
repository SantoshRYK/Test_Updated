# components/tables.py
"""
Modern table display components with professional styling
Interactive, sortable, and filterable data tables
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
from utils.helpers import format_date, format_datetime

# ============================================
# MODERN CSS FOR TABLES
# ============================================

def inject_tables_css():
    """Inject modern CSS for tables"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Modern Table Container */
    .modern-table-container {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        margin: 1.5rem 0;
    }
    
    /* Table Header */
    .table-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e9ecef;
    }
    
    .table-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a202c;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .table-count {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    /* Status Badges in Tables */
    .table-badge {
        display: inline-block;
        padding: 0.375rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-completed { background: #d4edda; color: #155724; }
    .badge-in-progress { background: #d1ecf1; color: #0c5460; }
    .badge-pending { background: #fff3cd; color: #856404; }
    .badge-failed { background: #f8d7da; color: #721c24; }
    .badge-pass { background: #d4edda; color: #155724; }
    .badge-fail { background: #f8d7da; color: #721c24; }
    .badge-not-started { background: #e9ecef; color: #6c757d; }
    
    /* Timeline Metrics Bar */
    .timeline-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .timeline-metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 1.25rem;
        border-left: 4px solid #667eea;
        transition: all 0.3s;
    }
    
    .timeline-metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .timeline-metric-value {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .timeline-metric-label {
        color: #718096;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-top: 0.5rem;
    }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: #f8f9fa;
        border-radius: 12px;
        margin: 2rem 0;
    }
    
    .empty-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .empty-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #718096;
        margin-bottom: 0.5rem;
    }
    
    .empty-text {
        color: #a0aec0;
        font-size: 1rem;
    }
    
    /* DataFrame Styling Override */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Download Button Styling */
    .download-section {
        display: flex;
        justify-content: flex-end;
        margin-top: 1rem;
        gap: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================
# ENHANCED TABLE RENDERERS
# ============================================

def render_data_table(data: List[Dict], 
                      columns: List[str] = None, 
                      hide_index: bool = True,
                      title: str = None,
                      searchable: bool = True,
                      downloadable: bool = True):
    """
    Render modern interactive data table
    
    Args:
        data: List of dictionaries to display
        columns: Optional list of columns to display
        hide_index: Hide DataFrame index
        title: Optional table title
        searchable: Enable search functionality
        downloadable: Enable download button
    """
    inject_tables_css()
    
    try:
        if not data:
            render_empty_state("No Data Available", "Add some data to see it displayed here")
            return
        
        df = pd.DataFrame(data)
        
        if columns:
            available_columns = [col for col in columns if col in df.columns]
            df = df[available_columns]
        
        # Table Header
        if title:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div class="table-title">
                    <span>📊 {title}</span>
                    <span class="table-count">{len(df)} records</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if downloadable:
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"{title.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        
        # Search functionality
        if searchable and len(df) > 10:
            search_term = st.text_input("🔍 Search in table", "", key=f"search_{id(df)}")
            if search_term:
                mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                df = df[mask]
                st.info(f"Found {len(df)} matching records")
        
        # Display table with custom styling
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=hide_index,
            height=min(600, (len(df) + 1) * 35 + 3)
        )
        
    except Exception as e:
        st.error(f"❌ Error displaying table: {e}")

def render_empty_state(title: str = "No Data", message: str = "No data available to display", icon: str = "📭"):
    """Render empty state for tables"""
    inject_tables_css()
    
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-icon">{icon}</div>
        <div class="empty-title">{title}</div>
        <div class="empty-text">{message}</div>
    </div>
    """, unsafe_allow_html=True)

def render_timeline_metrics_bar(metrics: List[Dict]):
    """Render timeline metrics bar above table"""
    inject_tables_css()
    
    cols = st.columns(len(metrics))
    
    for col, metric in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="timeline-metric-card" style="border-left-color: {metric.get('color', '#667eea')};">
                <div class="timeline-metric-value">{metric.get('value', 'N/A')}</div>
                <div class="timeline-metric-label">{metric.get('label', 'Metric')}</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================
# UAT TABLES
# ============================================

def render_uat_timeline_table(records: List[Dict]):
    """Render UAT timeline analysis with modern metrics and table"""
    inject_tables_css()
    
    timeline_data = []
    
    for record in records:
        try:
            planned_start = datetime.strptime(record.get('planned_start_date', '2024-01-01'), '%Y-%m-%d')
            planned_end = datetime.strptime(record.get('planned_end_date', '2024-12-31'), '%Y-%m-%d')
            planned_duration = (planned_end - planned_start).days
            
            actual_start = record.get('actual_start_date')
            actual_end = record.get('actual_end_date')
            
            actual_duration = None
            variance = None
            
            if actual_start and actual_end:
                actual_start_dt = datetime.strptime(actual_start, '%Y-%m-%d')
                actual_end_dt = datetime.strptime(actual_end, '%Y-%m-%d')
                actual_duration = (actual_end_dt - actual_start_dt).days
                variance = actual_duration - planned_duration
            
            timeline_data.append({
                'Trial ID': record.get('trial_id'),
                'UAT Round': record.get('uat_round'),
                'Category': record.get('category', 'N/A'),
                'Status': record.get('status'),
                'Result': record.get('result'),
                'Planned Start': record.get('planned_start_date', 'N/A'),
                'Planned End': record.get('planned_end_date', 'N/A'),
                'Planned Duration': f"{planned_duration} days",
                'Actual Duration': f"{actual_duration} days" if actual_duration is not None else 'Not Completed',
                'Variance': f"{variance:+d} days" if variance is not None else 'N/A',
                'Created By': record.get('created_by', 'N/A')
            })
        except Exception:
            pass
    
    if timeline_data:
        df = pd.DataFrame(timeline_data)
        
        # Calculate metrics
        completed_records = [d for d in timeline_data if d['Actual Duration'] != 'Not Completed']
        
        avg_planned = sum([int(d['Planned Duration'].split()[0]) for d in timeline_data]) / len(timeline_data)
        
        avg_actual = "N/A"
        if completed_records:
            avg_actual = sum([int(d['Actual Duration'].split()[0]) for d in completed_records]) / len(completed_records)
            avg_actual = f"{int(avg_actual)} days"
        
        completion_rate = (len(completed_records) / len(timeline_data) * 100) if timeline_data else 0
        
        avg_variance = "N/A"
        if completed_records:
            variances = [int(d['Variance'].split()[0]) for d in completed_records if d['Variance'] != 'N/A']
            if variances:
                avg_variance = sum(variances) / len(variances)
                avg_variance = f"{avg_variance:+.0f} days"
        
        # Render metrics bar
        metrics = [
            {'label': 'Avg Planned Duration', 'value': f"{int(avg_planned)} days", 'color': '#667eea'},
            {'label': 'Avg Actual Duration', 'value': avg_actual, 'color': '#4facfe'},
            {'label': 'Completion Rate', 'value': f"{completion_rate:.1f}%", 'color': '#43e97b'},
            {'label': 'Avg Variance', 'value': avg_variance, 'color': '#f093fb'}
        ]
        
        render_timeline_metrics_bar(metrics)
        
        st.markdown("---")
        
        # Render table
        render_data_table(
            timeline_data,
            title="UAT Timeline Analysis",
            searchable=True,
            downloadable=True
        )
    else:
        render_empty_state("No Timeline Data", "UAT timeline data will appear here once records are added", "📅")

def render_uat_records_table(records: List[Dict], status_filter: str = "All"):
    """Render UAT records with status badges and filtering"""
    inject_tables_css()
    
    if not records:
        render_empty_state("No UAT Records", "Create your first UAT record to get started", "📋")
        return
    
    # Apply status filter
    if status_filter != "All":
        records = [r for r in records if r.get('status') == status_filter]
    
    # Format for display
    display_data = []
    for record in records:
        display_data.append({
            'Trial ID': record.get('trial_id'),
            'UAT Round': record.get('uat_round'),
            'Category': record.get('category', 'N/A'),
            'Status': record.get('status'),
            'Result': record.get('result'),
            'Planned Start': record.get('planned_start_date'),
            'Planned End': record.get('planned_end_date'),
            'Created By': record.get('created_by'),
            'Created At': record.get('created_at')
        })
    
    render_data_table(
        display_data,
        title="UAT Records",
        searchable=True,
        downloadable=True
    )

# ============================================
# ALLOCATION TABLES
# ============================================

def render_allocation_timeline_table(records: List[Dict]):
    """Render Allocation timeline analysis with modern metrics"""
    inject_tables_css()
    
    timeline_data = []
    
    for record in records:
        try:
            start = datetime.strptime(record.get('start_date', '2024-01-01'), '%Y-%m-%d')
            end = datetime.strptime(record.get('end_date', '2024-12-31'), '%Y-%m-%d')
            duration = (end - start).days
            
            timeline_data.append({
                'Trial ID': record.get('trial_id'),
                'Engineer': record.get('test_engineer_name', 'Unknown'),
                'System': record.get('system', 'Unknown'),
                'Category': record.get('trial_category', 'N/A'),
                'Role': record.get('role', 'N/A'),
                'Start Date': start.strftime('%Y-%m-%d'),
                'End Date': end.strftime('%Y-%m-%d'),
                'Duration': f"{duration} days",
                'Created By': record.get('created_by', 'N/A')
            })
        except:
            pass
    
    if timeline_data:
        # Calculate metrics
        durations = [int(d['Duration'].split()[0]) for d in timeline_data]
        
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        total_duration = sum(durations)
        
        # Render metrics bar
        metrics = [
            {'label': 'Avg Duration', 'value': f"{int(avg_duration)} days", 'color': '#667eea'},
            {'label': 'Longest', 'value': f"{max_duration} days", 'color': '#f093fb'},
            {'label': 'Shortest', 'value': f"{min_duration} days", 'color': '#4facfe'},
            {'label': 'Total Duration', 'value': f"{total_duration} days", 'color': '#43e97b'}
        ]
        
        render_timeline_metrics_bar(metrics)
        
        st.markdown("---")
        
        # Render table
        render_data_table(
            timeline_data,
            title="Allocation Timeline Analysis",
            searchable=True,
            downloadable=True
        )
    else:
        render_empty_state("No Timeline Data", "Allocation timeline data will appear here", "📅")

def render_allocation_table(allocations: List[Dict], filters: Dict = None):
    """Render allocations table with filters"""
    inject_tables_css()
    
    if not allocations:
        render_empty_state("No Allocations", "Create your first allocation to get started", "📊")
        return
    
    # Apply filters if provided
    if filters:
        if filters.get('system') and filters['system'] != "All":
            allocations = [a for a in allocations if a.get('system') == filters['system']]
        if filters.get('engineer') and filters['engineer'] != "All":
            allocations = [a for a in allocations if a.get('test_engineer_name') == filters['engineer']]
        if filters.get('category') and filters['category'] != "All":
            allocations = [a for a in allocations if filters['category'] in a.get('trial_category', '')]
    
    # Format for display
    display_data = []
    for allocation in allocations:
        display_data.append({
            'Trial ID': allocation.get('trial_id'),
            'System': allocation.get('system'),
            'Engineer': allocation.get('test_engineer_name'),
            'Role': allocation.get('role'),
            'Category': allocation.get('trial_category'),
            'Therapeutic Area': allocation.get('therapeutic_area'),
            'Start Date': allocation.get('start_date'),
            'End Date': allocation.get('end_date'),
            'Created By': allocation.get('created_by')
        })
    
    render_data_table(
        display_data,
        title="Test Engineer Allocations",
        searchable=True,
        downloadable=True
    )

# ============================================
# AUDIT TABLES
# ============================================

def render_audit_log_table(logs: List[Dict], limit: int = 100):
    """Render audit log table with modern styling"""
    inject_tables_css()
    
    if not logs:
        render_empty_state("No Audit Logs", "System activity will be logged here", "📝")
        return
    
    try:
        # Limit to most recent logs
        logs = sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
        
        df = pd.DataFrame(logs)
        
        # Select and rename columns
        column_mapping = {
            'timestamp': 'Timestamp',
            'user': 'User',
            'role': 'Role',
            'action': 'Action',
            'module': 'Module',
            'details': 'Details',
            'ip_address': 'IP Address'
        }
        
        available_columns = [col for col in column_mapping.keys() if col in df.columns]
        df_display = df[available_columns].copy()
        df_display.columns = [column_mapping[col] for col in available_columns]
        
        # Add action emoji
        if 'Action' in df_display.columns:
            action_emoji = {
                'LOGIN': '🔐', 'LOGOUT': '🚪', 'CREATE': '➕',
                'UPDATE': '✏️', 'DELETE': '🗑️', 'VIEW': '👁️',
                'EXPORT': '📥', 'APPROVE': '✅', 'REJECT': '❌'
            }
            df_display['Action'] = df_display['Action'].apply(
                lambda x: f"{action_emoji.get(x, '📝')} {x}"
            )
        
        render_data_table(
            df_display.to_dict('records'),
            title=f"System Audit Logs (Latest {limit})",
            searchable=True,
            downloadable=True
        )
        
    except Exception as e:
        st.error(f"❌ Error displaying audit logs: {e}")

# ============================================
# USER TABLES
# ============================================

def render_user_table(users: Dict):
    """Render users table with role badges"""
    inject_tables_css()
    
    if not users:
        render_empty_state("No Users", "User accounts will appear here", "👥")
        return
    
    try:
        user_list = []
        for username, details in users.items():
            user_list.append({
                'Username': username,
                'Email': details.get('email', 'N/A'),
                'Role': details.get('role', 'N/A').title(),
                'Status': details.get('status', 'active').title(),
                'Created At': details.get('created_at', 'N/A')
            })
        
        render_data_table(
            user_list,
            title="System Users",
            searchable=True,
            downloadable=True
        )
        
    except Exception as e:
        st.error(f"❌ Error displaying users: {e}")

# ============================================
# GENERIC SUMMARY TABLES
# ============================================

def render_summary_table(data: List[Dict], 
                         title: str = "Summary",
                         icon: str = "📊",
                         group_by: str = None,
                         sort_by: str = None):
    """
    Render a summary table with grouping and sorting
    
    Args:
        data: List of dictionaries
        title: Table title
        icon: Icon for title
        group_by: Column to group by
        sort_by: Column to sort by
    """
    inject_tables_css()
    
    if not data:
        render_empty_state(f"No {title}", f"{title} data will appear here", icon)
        return
    
    try:
        df = pd.DataFrame(data)
        
        # Format date columns
        date_columns = ['created_at', 'updated_at', 'start_date', 'end_date', 
                       'planned_start_date', 'planned_end_date', 
                       'actual_start_date', 'actual_end_date']
        
        for col in date_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: format_date(x) if x else 'N/A')
        
        # Apply grouping
        if group_by and group_by in df.columns:
            st.markdown(f"### {icon} {title} - Grouped by {group_by}")
            for group_value in df[group_by].unique():
                with st.expander(f"{group_by}: {group_value}"):
                    group_df = df[df[group_by] == group_value]
                    st.dataframe(group_df, use_container_width=True, hide_index=True)
        else:
            # Apply sorting
            if sort_by and sort_by in df.columns:
                df = df.sort_values(sort_by, ascending=False)
            
            render_data_table(
                df.to_dict('records'),
                title=f"{icon} {title}",
                searchable=True,
                downloadable=True
            )
        
    except Exception as e:
        st.error(f"❌ Error displaying {title.lower()}: {e}")

def render_comparison_table(data1: List[Dict], data2: List[Dict], 
                            label1: str = "Dataset 1", 
                            label2: str = "Dataset 2"):
    """Render two datasets side by side for comparison"""
    inject_tables_css()
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_data_table(data1, title=label1, downloadable=False)
    
    with col2:
        render_data_table(data2, title=label2, downloadable=False)