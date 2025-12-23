# pages/allocation/allocation_dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from services.allocation_service import AllocationService
from components.filters import render_allocation_filters
from components.charts import (
    render_pie_chart,
    render_bar_chart,
    render_line_chart,
    render_system_distribution,
    render_category_distribution,
    render_engineer_workload,
    render_timeline_analysis,
    render_monthly_distribution
)
from components.metrics import render_allocation_metrics
from utils.excel_handler import convert_to_excel
from utils.auth import get_current_role  # ADDED FOR ROLE CHECK

def render_manager_allocation_dashboard():
    """Manager-specific allocation dashboard - SUMMARY VIEW ONLY"""
    st.title("👨‍💼 Manager Allocation Dashboard")
    st.info("📊 **Manager View:** summary data, metrics, and analytics.")
    st.markdown("---")
    
    if st.button("⬅️ Back to Home", key="manager_dash_back"):
        st.session_state.current_page = "home"
        st.rerun()
    
    # Get current role
    current_role = get_current_role()
    
    # Load all allocations (managers see everything in summary)
    allocation_service = AllocationService()
    all_allocations = allocation_service.get_all_allocations()
    
    if not all_allocations:
        st.info("📝 No allocations found in the system.")
        return
    
    # Summary Statistics (ALLOWED FOR MANAGERS)
    st.subheader("📊 Overview Statistics")
    render_allocation_metrics(all_allocations)
    
    st.markdown("---")
    
    # Filters Section (ALLOWED FOR MANAGERS)
    st.subheader("🔍 Filter Allocations")
    filtered_allocations = render_allocation_filters(all_allocations)
    
    st.markdown("---")
    
    # Show filtered count
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader(f"📋 Showing {len(filtered_allocations)} of {len(all_allocations)} Allocations")
    with col3:
        # Export to Excel (ALLOWED FOR MANAGERS)
        excel_data = convert_to_excel(filtered_allocations)
        if excel_data:
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name=f"manager_allocations_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    st.markdown("---")
    
    # Visual Analytics Section (ALLOWED FOR MANAGERS)
    if filtered_allocations:
        render_visual_analytics(filtered_allocations)
        
        st.markdown("---")
        
        # Summary Data Table (ALLOWED FOR MANAGERS)
        render_allocation_summary_table(filtered_allocations)
        
        st.markdown("---")
        
        # # ========== BLOCK DETAILED CARD VIEW FOR MANAGERS ==========
        # if current_role == "manager":
        #     st.info("ℹ️ **Detailed Allocation View Restricted**")
        #     st.warning("👨‍💼 Manager role has access to all analytics, charts, and summary tables above. Individual allocation detail cards with edit/delete actions are available for Admin and Superuser roles only.")
        #     st.markdown("""
        #     ### 📊 What Managers Have Access To:
        #     - ✅ Overview statistics and metrics
        #     - ✅ Visual analytics (charts & graphs)
        #     - ✅ Allocation summary table
        #     - ✅ Filter and search functionality
        #     - ✅ Excel export
        #     - ✅ Timeline and workload analysis
            
        #     ### 🔒 Restricted to Admin/Superuser:
        #     - ❌ Detailed allocation cards (expandable)
        #     - ❌ Full activity descriptions
        #     - ❌ Edit/Delete actions
        #     - ❌ Allocation IDs and metadata
            
        #     📧 **Need detailed access?** Contact your system administrator.
        #     """)
        # else:
        #     # Show detailed card view for admin/superuser
        #     render_allocation_cards(filtered_allocations)
    else:
        st.info("📝 No allocations match the selected filters.")

def render_visual_analytics(allocations):
    """Render comprehensive visual analytics - ALLOWED FOR MANAGERS"""
    st.subheader(f"📊 Visual Analytics - Filtered Results ({len(allocations)} allocations)")
    
    # Chart Type Selector
    col_chart1, col_chart2 = st.columns([1, 3])
    with col_chart1:
        chart_type = st.selectbox(
            "📊 Select Chart Type",
            ["Bar Chart", "Pie Chart", "Line Chart"],
            help="Choose your preferred visualization style",
            key="manager_chart_type"
        )
    
    # Create tabs for different analytics
    chart_tab1, chart_tab2, chart_tab3, chart_tab4 = st.tabs([
        "📊 System & Category",
        "👥 Engineer Distribution",
        "🎯 Trial Category vs Therapeutic Area",
        "📅 Timeline View"
    ])
    
    # TAB 1: System & Category Distribution
    with chart_tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### System Distribution")
            render_system_distribution(allocations, chart_type)
        
        with col2:
            st.markdown("#### Trial Category Distribution")
            render_category_distribution(allocations, chart_type)
    
    # TAB 2: Engineer Distribution
    with chart_tab2:
        st.markdown("#### Test Engineer Workload")
        render_engineer_workload(allocations, chart_type)
    
    # TAB 3: Category vs Therapeutic Area
    with chart_tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Trial Category Distribution")
            render_category_distribution(allocations, chart_type)
        
        with col2:
            st.markdown("#### Therapeutic Area Distribution")
            render_therapeutic_area_distribution(allocations, chart_type)
        
        st.markdown("---")
        st.markdown("#### 🔄 Trial Category vs Therapeutic Area Matrix")
        render_category_area_matrix(allocations, chart_type)
    
    # TAB 4: Timeline View
    with chart_tab4:
        st.markdown("#### 📅 Allocation Timeline")
        render_timeline_analysis(allocations, chart_type)
        
        st.markdown("---")
        st.markdown("##### 📊 Allocations by Start Month")
        render_monthly_distribution(allocations, chart_type)

def render_therapeutic_area_distribution(allocations, chart_type):
    """Render therapeutic area distribution chart - ALLOWED FOR MANAGERS"""
    area_data = {}
    for a in allocations:
        area_type = a.get('therapeutic_area_type', '')
        if not area_type:
            area = a.get('therapeutic_area', 'Unknown')
            if 'Others -' in area:
                area_type = 'Others'
            else:
                area_type = area
        if area_type:
            area_data[area_type] = area_data.get(area_type, 0) + 1
    
    if area_data:
        df_area = pd.DataFrame(list(area_data.items()), columns=['Therapeutic Area', 'Count'])
        df_area = df_area.sort_values('Count', ascending=False)
        
        if chart_type == "Bar Chart":
            st.bar_chart(df_area.set_index('Therapeutic Area')['Count'])
        elif chart_type == "Pie Chart":
            fig, ax = plt.subplots(figsize=(10, 10))
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#C39BD3']
            labels = [label[:25] + '...' if len(label) > 25 else label for label in df_area['Therapeutic Area']]
            wedges, texts, autotexts = ax.pie(
                df_area['Count'],
                labels=labels,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors[:len(df_area)],
                textprops={'fontsize': 8, 'weight': 'bold'}
            )
            for i, (wedge, autotext) in enumerate(zip(wedges, autotexts)):
                autotext.set_text(f"{df_area.iloc[i]['Count']}\n({autotext.get_text()})")
            ax.set_title('Therapeutic Area Distribution', fontsize=14, weight='bold')
            st.pyplot(fig)
            plt.close()
        elif chart_type == "Line Chart":
            st.line_chart(df_area.set_index('Therapeutic Area')['Count'])
        
        st.markdown("---")
        st.dataframe(df_area, use_container_width=True, hide_index=True)

def render_category_area_matrix(allocations, chart_type):
    """Render category vs therapeutic area matrix - ALLOWED FOR MANAGERS"""
    matrix_data = {}
    for a in allocations:
        cat_type = a.get('trial_category_type', 'Unknown')
        if not cat_type:
            cat = a.get('trial_category', 'Unknown')
            if 'Change Request' in cat:
                cat_type = 'Change Request'
            else:
                cat_type = cat
        
        area_type = a.get('therapeutic_area_type', '')
        if not area_type:
            area = a.get('therapeutic_area', 'Unknown')
            if 'Others -' in area:
                area_type = 'Others'
            else:
                area_type = area
        
        key = f"{cat_type} - {area_type}"
        matrix_data[key] = matrix_data.get(key, 0) + 1
    
    if matrix_data:
        df_matrix = pd.DataFrame(list(matrix_data.items()), columns=['Category-Area', 'Count'])
        df_matrix = df_matrix.sort_values('Count', ascending=False)
        
        if chart_type == "Bar Chart":
            st.bar_chart(df_matrix.set_index('Category-Area')['Count'])
        elif chart_type == "Pie Chart":
            df_matrix_top = df_matrix.head(10)
            fig, ax = plt.subplots(figsize=(12, 12))
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
                     '#F7DC6F', '#C39BD3', '#F8B4D9', '#AED6F1', '#FAD7A0']
            wedges, texts, autotexts = ax.pie(
                df_matrix_top['Count'],
                labels=df_matrix_top['Category-Area'],
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                textprops={'fontsize': 8, 'weight': 'bold'}
            )
            for i, (wedge, autotext) in enumerate(zip(wedges, autotexts)):
                autotext.set_text(f"{df_matrix_top.iloc[i]['Count']}\n({autotext.get_text()})")
            ax.set_title('Category-Area Matrix (Top 10)', fontsize=14, weight='bold')
            st.pyplot(fig)
            plt.close()
        elif chart_type == "Line Chart":
            st.line_chart(df_matrix.set_index('Category-Area')['Count'])
        
        st.markdown("---")
        st.dataframe(df_matrix, use_container_width=True, hide_index=True)

def render_allocation_summary_table(allocations):
    """Render allocation summary table - ALLOWED FOR MANAGERS (NO SENSITIVE DATA)"""
    st.subheader("📋 Allocation Summary Table")
    try:
        df = pd.DataFrame(allocations)
        # ONLY show summary columns (no IDs, no activities)
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
            df_display = df[available_columns]
            st.dataframe(df_display, use_container_width=True, hide_index=True)
    except Exception as e:
        st.warning(f"Could not display table: {e}")

def render_allocation_cards(allocations):
    """Render detailed allocation cards - ADMIN/SUPERUSER ONLY"""
    st.subheader("📋 Detailed Allocation View")
    st.caption("🔒 Admin/Superuser Access Only")
    
    for idx, allocation in enumerate(reversed(allocations)):
        # System emoji
        system_emoji = {
            "INFORM": "📊",
            "VEEVA": "📁",
            "eCOA": "📱",
            "ePID": "🔬",
            "CGM": "📈"
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
        elif "Phase 1 & NIS" in therapeutic_area_full:
            area_emoji = "🔬"
        elif "Rare Disease" in therapeutic_area_full:
            area_emoji = "🩺"
        else:
            area_emoji = "🏥"
        
        test_engineer = allocation.get('test_engineer_name', 'N/A')
        trial_id_val = allocation.get('trial_id', 'N/A')
        system = allocation.get('system', 'N/A')
        trial_category = allocation.get('trial_category', 'N/A')
        
        with st.expander(f"{system_emoji} {area_emoji} [{trial_id_val}] {test_engineer} - {system} - {trial_category}"):
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
            
            st.markdown("---")
            st.write(f"**Activity:**")
            st.text_area(
                "Activity Details",
                value=allocation.get('activity', 'N/A'),
                height=100,
                disabled=True,
                key=f"activity_dash_{allocation.get('id')}_{idx}"
            )
            st.caption(f"Allocation ID: {allocation.get('id', 'N/A')}")