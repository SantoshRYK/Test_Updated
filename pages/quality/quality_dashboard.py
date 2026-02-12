"""
Quality Dashboard for Managers
Displays pie charts and statistics with filters
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from services.quality_service import QualityService
import pandas as pd

def render_metrics_cards(stats: dict):
    """Render key metrics cards"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Trials",
            stats['unique_trials'],
            help="Number of unique trial IDs"
        )
    
    with col2:
        st.metric(
            "Total Requirements",
            stats['total_requirements'],
            help="Cumulative requirements across all trials"
        )
    
    with col3:
        st.metric(
            "Total Failures",
            stats['total_failures'],
            help="Cumulative failures across all rounds"
        )
    
    with col4:
        st.metric(
            "Avg Defect Density",
            f"{stats['avg_defect_density']:.2f}%",
            help="Average defect density across all records"
        )

def render_overall_summary_card(stats: dict):
    """
    Render overall summary visualization showing:
    - Total Requirements (cumulative)
    - Total Failures (cumulative)
    - Overall Defect Density (calculated from cumulative)
    """
    
    total_req = stats['total_requirements']
    total_fail = stats['total_failures']
    
    # Calculate overall defect density from cumulative values
    if total_req > 0:
        overall_defect_density = (total_fail / total_req) * 100
    else:
        overall_defect_density = 0.0
    
    # Determine status color
    if overall_defect_density < 10:
        color = "#10b981"  # Green
        status = "🟢 Excellent"
    elif overall_defect_density < 25:
        color = "#f59e0b"  # Yellow
        status = "🟡 Good"
    elif overall_defect_density < 50:
        color = "#f97316"  # Orange
        status = "🟠 Warning"
    else:
        color = "#ef4444"  # Red
        status = "🔴 Critical"
    
    st.markdown("### 📊 Overall Quality Summary")
    
    # Display as metric cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📝 Total Requirements",
            value=f"{total_req}",
            help="Cumulative requirements: Round 1 + New additions in subsequent rounds"
        )
    
    with col2:
        st.metric(
            label="❌ Total Failures",
            value=f"{total_fail}",
            delta=f"{total_fail} out of {total_req}",
            delta_color="inverse",
            help="Cumulative failures across all rounds"
        )
    
    with col3:
        # Calculate delta color
        if overall_defect_density < 25:
            dd_color = "normal"
        else:
            dd_color = "inverse"
        
        st.metric(
            label="📈 Overall Defect Density",
            value=f"{overall_defect_density:.2f}%",
            delta=status,
            delta_color=dd_color,
            help=f"Calculated as: ({total_fail}/{total_req}) × 100"
        )
    
    # Add bar chart visualization
    fig = go.Figure()
    
    # Passed requirements
    passed = total_req - total_fail
    
    # Add stacked bar
    fig.add_trace(go.Bar(
        x=['Overall Status'],
        y=[passed],
        name='Passed',
        marker_color='#10b981',
        text=[f"Passed: {passed}"],
        textposition='inside',
        textfont=dict(size=14, color='white'),
        hovertemplate='<b>Passed Requirements</b><br>Count: %{y}<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=['Overall Status'],
        y=[total_fail],
        name='Failed',
        marker_color='#ef4444',
        text=[f"Failed: {total_fail}"],
        textposition='inside',
        textfont=dict(size=14, color='white'),
        hovertemplate='<b>Failed Requirements</b><br>Count: %{y}<extra></extra>'
    ))
    
    # Add annotation for defect density
    fig.add_annotation(
        x='Overall Status',
        y=total_req,
        text=f"<b>Defect Density: {overall_defect_density:.2f}%</b><br>{status}",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor=color,
        ax=0,
        ay=-60,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor=color,
        borderwidth=3,
        borderpad=8,
        font=dict(size=16, color=color)
    )
    
    fig.update_layout(
        barmode='stack',
        xaxis_title="",
        yaxis_title="Count",
        showlegend=True,
        height=350,
        hovermode='x',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_failure_reasons_chart(stats: dict):
    """Render failure reasons pie chart"""
    
    failure_data = stats['failure_reasons']
    
    if not failure_data or sum(failure_data.values()) == 0:
        st.info("📊 No failure data available for chart")
        return
    
    fig = px.pie(
        values=list(failure_data.values()),
        names=list(failure_data.keys()),
        title="Failure Reasons Breakdown",
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}'
    )
    
    fig.update_layout(
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_type_breakdown_chart(stats: dict):
    """Render type of requirement breakdown chart"""
    
    type_data = stats['type_breakdown']
    
    if not type_data:
        st.info("📊 No type data available for chart")
        return
    
    fig = px.pie(
        values=list(type_data.values()),
        names=list(type_data.keys()),
        title="Type of Requirement Distribution",
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}'
    )
    
    fig.update_layout(
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_phase_breakdown_chart(stats: dict):
    """Render phase breakdown chart"""
    
    phase_data = stats['phase_breakdown']
    
    if not phase_data:
        st.info("📊 No phase data available for chart")
        return
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(phase_data.keys()),
            y=list(phase_data.values()),
            text=list(phase_data.values()),
            textposition='auto',
            marker_color='lightblue'
        )
    ])
    
    fig.update_layout(
        title="Records by Phase",
        xaxis_title="Phase",
        yaxis_title="Number of Records",
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_round_breakdown_chart(stats: dict):
    """Render round breakdown chart"""
    
    round_data = stats['round_breakdown']
    
    if not round_data:
        st.info("📊 No round data available for chart")
        return
    
    fig = px.pie(
        values=list(round_data.values()),
        names=list(round_data.keys()),
        title="Distribution by Round",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}'
    )
    
    fig.update_layout(
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render():
    """Main render function"""
    
    st.subheader("📊 Trial Quality Dashboard")
    
    # Check if user is manager
    if st.session_state.get('role') != 'manager':
        st.warning("⚠️ This dashboard is only available for Managers")
        return
    
    quality_service = QualityService()
    
    # Filters
    st.markdown("### 🔍 Filters")
    with st.expander("Filter Options", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            trial_ids = quality_service.get_unique_values('trial_id')
            trial_id_filter = st.selectbox("Trial ID", ["All"] + trial_ids, key="dash_trial")
        
        with col2:
            phases = quality_service.get_unique_values('phase')
            phase_filter = st.selectbox("Phase", ["All"] + phases, key="dash_phase")
        
        with col3:
            types = quality_service.get_unique_values('type_of_requirement')
            type_filter = st.selectbox("Type", ["All"] + types, key="dash_type")
        
        with col4:
            rounds = quality_service.get_unique_values('current_round')
            round_filter = st.selectbox("Round", ["All"] + [str(r) for r in sorted(rounds)], key="dash_round")
    
    # Build filters dict
    filters = {}
    if trial_id_filter != "All":
        filters['trial_id'] = trial_id_filter
    if phase_filter != "All":
        filters['phase'] = phase_filter
    if type_filter != "All":
        filters['type_of_requirement'] = type_filter
    if round_filter != "All":
        filters['current_round'] = int(round_filter)
    
    # Get statistics
    stats = quality_service.get_statistics(filters if filters else None)
    
    # Get filtered records
    all_records = quality_service.get_all_records()
    filtered_records = all_records
    
    if filters:
        for key, value in filters.items():
            filtered_records = [r for r in filtered_records if r.get(key) == value]
    
    st.markdown("---")
    
    # Top metrics cards
    render_metrics_cards(stats)
    
    st.markdown("---")
    
    # Overall Quality Summary
    render_overall_summary_card(stats)
    
    st.markdown("---")
    
    # Breakdown Analytics
    st.markdown("### 📊 Breakdown Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_failure_reasons_chart(stats)
    
    with col2:
        render_type_breakdown_chart(stats)
    
    col3, col4 = st.columns(2)
    
    with col3:
        render_phase_breakdown_chart(stats)
    
    with col4:
        render_round_breakdown_chart(stats)
    
    st.markdown("---")
    
    # Data table
    if st.checkbox("📋 Show Detailed Data Table"):
        if filtered_records:
            df = pd.DataFrame(filtered_records)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No records match the selected filters")