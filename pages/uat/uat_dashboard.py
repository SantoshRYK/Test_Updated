# pages/uat/uat_dashboard.py
"""
UAT Dashboard - Analytics and visualizations
EASY TO ADD NEW CHARTS AND METRICS
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.auth import get_current_user, get_current_role
from services.uat_service import (
    get_uat_records_by_role, get_uat_statistics, get_user_uat_statistics
)
from components.charts import (
    render_status_distribution_chart,
    render_result_distribution_chart,
    render_uat_category_distribution,  # ✅ FIXED: Changed from render_category_distribution_chart
    render_bar_chart,
    render_uat_round_distribution,
    render_uat_user_workload,
    render_uat_monthly_distribution
)
from components.metrics import render_uat_summary_metrics
from utils.helpers import get_status_emoji

def render_uat_dashboard_tab():
    """Render UAT dashboard with analytics"""
    st.subheader("📊 UAT Dashboard & Analytics")
    
    username = get_current_user()
    role = get_current_role()
    
    # Load UAT records
    uat_records = get_uat_records_by_role(role, username)
    
    if uat_records:
        # Get statistics
        stats = get_uat_statistics(uat_records)
        
        # Overall Statistics
        render_uat_summary_metrics(stats)
        
        st.markdown("---")
        
        # Charts Section
        render_uat_charts(uat_records, stats, role)
        
        st.markdown("---")
        
        # Timeline Analysis
        st.markdown("#### Timeline Analysis")
        render_uat_timeline_table(uat_records)
        
    else:
        st.info("📝 No UAT records available for dashboard.")


def render_uat_charts(records, stats, role):
    """Render UAT analytics charts"""
    
    # Chart Type Selector
    col_selector1, col_selector2 = st.columns([1, 3])
    with col_selector1:
        chart_type = st.selectbox(
            "📊 Chart Type",
            ["Pie Chart", "Bar Chart", "Line Chart"],
            key="uat_dashboard_chart_type"
        )
    
    # Create tabs for organized view
    tab1, tab2, tab3 = st.tabs(["📊 Status & Result", "📈 Trends", "👥 User Analysis"])
    
    # TAB 1: Status and Result
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Status Distribution")
            render_status_distribution_chart(records, chart_type)
        
        with col2:
            st.markdown("#### Result Distribution")
            render_result_distribution_chart(records, chart_type)
    
    # TAB 2: Category and Trends
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Category Distribution")
            render_uat_category_distribution(records, chart_type)
        
        with col2:
            st.markdown("#### UAT Round Distribution")
            render_uat_round_distribution(records, chart_type)
        
        st.markdown("---")
        st.markdown("#### 📅 Monthly Distribution")
        render_uat_monthly_distribution(records, chart_type)
    
    # TAB 3: User Analysis (especially useful for managers)
    with tab3:
        st.markdown("#### User Workload Distribution")
        render_uat_user_workload(records, chart_type)
        
        # Manager-specific: Detailed user statistics
        if role == "manager":
            st.markdown("---")
            st.markdown("#### 👥 Detailed User Statistics")
            render_manager_user_stats(records)


def render_manager_user_stats(records):
    """Render detailed user statistics for managers"""
    user_stats = {}
    
    for r in records:
        user = r.get('created_by', 'Unknown')
        if user not in user_stats:
            user_stats[user] = {
                'total': 0,
                'completed': 0,
                'passed': 0,
                'failed': 0,
                'in_progress': 0
            }
        
        user_stats[user]['total'] += 1
        
        if r.get('status') == 'Completed':
            user_stats[user]['completed'] += 1
        if r.get('status') == 'In Progress':
            user_stats[user]['in_progress'] += 1
        if r.get('result') == 'Pass':
            user_stats[user]['passed'] += 1
        if r.get('result') == 'Fail':
            user_stats[user]['failed'] += 1
    
    if user_stats:
        user_stats_list = []
        for user, stats in user_stats.items():
            completion_rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            user_stats_list.append({
                'User': user,
                'Total Records': stats['total'],
                'Completed': stats['completed'],
                'In Progress': stats['in_progress'],
                'Passed': stats['passed'],
                'Failed': stats['failed'],
                'Completion %': f"{completion_rate:.1f}%",
                'Pass %': f"{pass_rate:.1f}%"
            })
        
        df_user_stats = pd.DataFrame(user_stats_list)
        df_user_stats = df_user_stats.sort_values('Total Records', ascending=False)
        
        st.dataframe(df_user_stats, use_container_width=True, hide_index=True)


def render_uat_timeline_table(records):
    """Render UAT timeline table"""
    timeline_data = []
    
    for r in records:
        try:
            planned_start = datetime.strptime(r.get('planned_start_date', '2024-01-01'), '%Y-%m-%d')
            planned_end = datetime.strptime(r.get('planned_end_date', '2024-12-31'), '%Y-%m-%d')
            planned_duration = (planned_end - planned_start).days
            
            actual_start = r.get('actual_start_date')
            actual_end = r.get('actual_end_date')
            
            if actual_start and actual_end:
                actual_start_dt = datetime.strptime(actual_start, '%Y-%m-%d')
                actual_end_dt = datetime.strptime(actual_end, '%Y-%m-%d')
                actual_duration = (actual_end_dt - actual_start_dt).days
            else:
                actual_duration = 'Not Completed'
            
            timeline_data.append({
                'Trial ID': r.get('trial_id'),
                'UAT Round': r.get('uat_round'),
                'Category': r.get('category', 'N/A'),
                'Status': r.get('status'),
                'Result': r.get('result'),
                'Planned Duration (Days)': planned_duration,
                'Actual Duration (Days)': actual_duration,
                'Created By': r.get('created_by', 'N/A')
            })
        except:
            pass
    
    if timeline_data:
        df_timeline = pd.DataFrame(timeline_data)
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        
        completed_records = df_timeline[df_timeline['Actual Duration (Days)'] != 'Not Completed']
        
        with col1:
            avg_planned = df_timeline['Planned Duration (Days)'].mean()
            st.metric("Avg Planned Duration", f"{int(avg_planned)} days")
        
        with col2:
            if len(completed_records) > 0:
                avg_actual = completed_records['Actual Duration (Days)'].mean()
                st.metric("Avg Actual Duration", f"{int(avg_actual)} days")
            else:
                st.metric("Avg Actual Duration", "N/A")
        
        with col3:
            completed_count = len(completed_records)
            total_count = len(df_timeline)
            completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0
            st.metric("Completion Rate", f"{completion_rate:.1f}%")
        
        st.markdown("---")
        st.dataframe(df_timeline, use_container_width=True, hide_index=True)
    else:
        st.info("No timeline data available")