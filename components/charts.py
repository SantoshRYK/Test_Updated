# components/charts.py
"""
Modern chart rendering components with Plotly
Interactive, professional visualizations - COMPLETE FIXED VERSION
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from typing import Dict, List
import hashlib

# ============================================
# KEY GENERATION UTILITY
# ============================================

def generate_chart_key(base_name: str, data=None) -> str:
    """Generate unique key for charts"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    if data:
        data_hash = hashlib.md5(str(data).encode()).hexdigest()[:8]
        return f"chart_{base_name}_{data_hash}_{timestamp}"
    return f"chart_{base_name}_{timestamp}"

# Modern color palettes
COLOR_PALETTES = {
    'primary': ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'],
    'success': ['#43e97b', '#38f9d7', '#7bed9f', '#70a1ff'],
    'warning': ['#ffd89b', '#19547b', '#ffc107', '#ff9800'],
    'danger': ['#ff6b6b', '#ee5a6f', '#f44336', '#e74c3c'],
    'info': ['#4facfe', '#00f2fe', '#2196f3', '#03a9f4'],
    'gradient': ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7']
}

def get_color_palette(name='gradient'):
    """Get color palette by name"""
    return COLOR_PALETTES.get(name, COLOR_PALETTES['gradient'])

# ============================================
# GENERIC CHART RENDERERS
# ============================================

def render_pie_chart(data_dict, title, colors=None, show_table=True, chart_key=None):
    """Modern interactive pie chart with Plotly"""
    if not data_dict:
        st.info("📊 No data available for chart")
        return
    
    if chart_key is None:
        chart_key = generate_chart_key(f"pie_{title}", data_dict)
    
    df = pd.DataFrame(list(data_dict.items()), columns=['Label', 'Count'])
    df = df.sort_values('Count', ascending=False)
    
    if not colors:
        colors = get_color_palette('gradient')
    
    fig = go.Figure(data=[go.Pie(
        labels=df['Label'],
        values=df['Count'],
        hole=0.4,
        marker=dict(colors=colors[:len(df)]),
        textposition='inside',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
        pull=[0.05 if i == 0 else 0 for i in range(len(df))]
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=20, family='Inter, sans-serif', color='#1a202c', weight=600),
            x=0.5,
            xanchor='center'
        ),
        font=dict(family='Inter, sans-serif', size=12),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        ),
        height=450,
        margin=dict(l=20, r=150, t=80, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True, key=chart_key)
    
    if show_table:
        st.markdown("---")
        total = df['Count'].sum()
        df['Percentage'] = (df['Count'] / total * 100).round(2).astype(str) + '%'
        st.dataframe(df, use_container_width=True, hide_index=True)

def render_bar_chart(data_dict, title="", x_label='Category', y_label='Count', horizontal=False, colors=None, chart_key=None):
    """Modern interactive bar chart with Plotly"""
    if not data_dict:
        st.info("📊 No data available for chart")
        return
    
    if chart_key is None:
        chart_key = generate_chart_key(f"bar_{title}_{x_label}", data_dict)
    
    df = pd.DataFrame(list(data_dict.items()), columns=[x_label, y_label])
    df = df.sort_values(y_label, ascending=False)
    
    if not colors:
        colors = get_color_palette('primary')
    
    if horizontal:
        fig = go.Figure(data=[go.Bar(
            y=df[x_label],
            x=df[y_label],
            orientation='h',
            marker=dict(
                color=df[y_label],
                colorscale=[[0, colors[0]], [1, colors[1]]],
                line=dict(width=0)
            ),
            hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
        )])
        fig.update_xaxes(title_text=y_label)
        fig.update_yaxes(title_text=x_label)
    else:
        fig = go.Figure(data=[go.Bar(
            x=df[x_label],
            y=df[y_label],
            marker=dict(
                color=df[y_label],
                colorscale=[[0, colors[0]], [1, colors[1]]],
                line=dict(width=0)
            ),
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )])
        fig.update_xaxes(title_text=x_label)
        fig.update_yaxes(title_text=y_label)
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=20, family='Inter, sans-serif', color='#1a202c', weight=600),
            x=0.5,
            xanchor='center'
        ) if title else None,
        font=dict(family='Inter, sans-serif', size=12),
        height=400,
        margin=dict(l=20, r=20, t=80 if title else 20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef')
    )
    
    st.plotly_chart(fig, use_container_width=True, key=chart_key)

def render_line_chart(data_dict, title="", x_label='Category', y_label='Count', area=True, chart_key=None):
    """Modern interactive line/area chart with Plotly"""
    if not data_dict:
        st.info("📊 No data available for chart")
        return
    
    if chart_key is None:
        chart_key = generate_chart_key(f"line_{title}_{x_label}", data_dict)
    
    df = pd.DataFrame(list(data_dict.items()), columns=[x_label, y_label])
    df = df.sort_values(x_label)
    
    colors = get_color_palette('primary')
    
    if area:
        fig = go.Figure(data=[go.Scatter(
            x=df[x_label],
            y=df[y_label],
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color=colors[0], width=3),
            marker=dict(size=8, color=colors[1]),
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )])
    else:
        fig = go.Figure(data=[go.Scatter(
            x=df[x_label],
            y=df[y_label],
            mode='lines+markers',
            line=dict(color=colors[0], width=3),
            marker=dict(size=8, color=colors[1]),
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )])
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=20, family='Inter, sans-serif', color='#1a202c', weight=600),
            x=0.5,
            xanchor='center'
        ) if title else None,
        font=dict(family='Inter, sans-serif', size=12),
        height=400,
        margin=dict(l=20, r=20, t=80 if title else 20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title=x_label, showgrid=False),
        yaxis=dict(title=y_label, showgrid=True, gridcolor='#e9ecef'),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True, key=chart_key)

def render_gauge_chart(value, title, max_value=100, colors=['#ff6b6b', '#ffd89b', '#43e97b'], chart_key=None):
    """Modern gauge chart for metrics like compliance score"""
    if chart_key is None:
        chart_key = generate_chart_key(f"gauge_{title}", str(value))
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20, 'family': 'Inter, sans-serif'}},
        delta={'reference': max_value * 0.8},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1, 'tickcolor': "#1a202c"},
            'bar': {'color': colors[2] if value > max_value * 0.7 else (colors[1] if value > max_value * 0.4 else colors[0])},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e9ecef",
            'steps': [
                {'range': [0, max_value * 0.4], 'color': '#fee'},
                {'range': [max_value * 0.4, max_value * 0.7], 'color': '#ffc'},
                {'range': [max_value * 0.7, max_value], 'color': '#efe'}
            ],
            'threshold': {
                'line': {'color': "#1a202c", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif')
    )
    
    st.plotly_chart(fig, use_container_width=True, key=chart_key)

def render_heatmap(data, title="Heatmap", x_label="X", y_label="Y", chart_key=None):
    """Modern heatmap visualization"""
    if data.empty:
        st.info("📊 No data available for heatmap")
        return
    
    if chart_key is None:
        chart_key = generate_chart_key(f"heatmap_{title}", str(data.shape))
    
    fig = go.Figure(data=go.Heatmap(
        z=data.values,
        x=data.columns,
        y=data.index,
        colorscale='Viridis',
        hovertemplate='%{y}<br>%{x}<br>Value: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=20, family='Inter, sans-serif', color='#1a202c', weight=600),
            x=0.5,
            xanchor='center'
        ),
        xaxis_title=x_label,
        yaxis_title=y_label,
        font=dict(family='Inter, sans-serif', size=12),
        height=500,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True, key=chart_key)

# ============================================
# ALLOCATION SPECIFIC CHARTS
# ============================================

def render_system_distribution(allocations, chart_type="Pie Chart"):
    """Render system distribution chart"""
    system_data = {}
    for a in allocations:
        sys = a.get('system', 'Unknown')
        system_data[sys] = system_data.get(sys, 0) + 1
    
    if not system_data:
        st.info("📊 No system data available")
        return
    
    chart_key = generate_chart_key("system_distribution", system_data)
    
    if chart_type == "Bar Chart":
        render_bar_chart(system_data, "System Distribution", 'System', 'Count', chart_key=chart_key)
    elif chart_type == "Pie Chart":
        render_pie_chart(system_data, 'System Distribution', chart_key=chart_key)
    elif chart_type == "Line Chart":
        render_line_chart(system_data, 'System Distribution', 'System', 'Count', chart_key=chart_key)

def render_category_distribution(allocations, chart_type="Pie Chart"):
    """Render trial category distribution chart"""
    category_data = {}
    for a in allocations:
        cat_type = a.get('trial_category_type', 'Unknown')
        if not cat_type:
            cat = a.get('trial_category', 'Unknown')
            cat_type = 'Change Request' if 'Change Request' in cat else 'Build'
        category_data[cat_type] = category_data.get(cat_type, 0) + 1
    
    if not category_data:
        st.info("📊 No category data available")
        return
    
    chart_key = generate_chart_key("category_distribution", category_data)
    
    if chart_type == "Bar Chart":
        render_bar_chart(category_data, "Trial Category Distribution", 'Category', 'Count', colors=get_color_palette('info'), chart_key=chart_key)
    elif chart_type == "Pie Chart":
        render_pie_chart(category_data, 'Trial Category Distribution', colors=get_color_palette('info'), chart_key=chart_key)
    elif chart_type == "Line Chart":
        render_line_chart(category_data, 'Trial Category Distribution', 'Category', 'Count', chart_key=chart_key)

def render_engineer_workload(allocations, chart_type="Bar Chart"):
    """Render test engineer workload distribution"""
    engineer_data = {}
    for a in allocations:
        eng = a.get('test_engineer_name', 'Unknown')
        engineer_data[eng] = engineer_data.get(eng, 0) + 1
    
    if not engineer_data:
        st.info("📊 No engineer data available")
        return
    
    df_engineer = pd.DataFrame(list(engineer_data.items()), columns=['Engineer', 'Allocations'])
    df_engineer = df_engineer.sort_values('Allocations', ascending=False)
    
    chart_key = generate_chart_key("engineer_workload", engineer_data)
    
    if chart_type == "Bar Chart":
        render_bar_chart(dict(zip(df_engineer['Engineer'], df_engineer['Allocations'])), 
                        "Engineer Workload Distribution", 'Engineer', 'Allocations', 
                        horizontal=True, colors=get_color_palette('success'), chart_key=chart_key)
    elif chart_type == "Pie Chart":
        render_pie_chart(dict(zip(df_engineer['Engineer'], df_engineer['Allocations'])), 
                        'Engineer Workload Distribution', colors=get_color_palette('gradient'), chart_key=chart_key)
    elif chart_type == "Line Chart":
        render_line_chart(dict(zip(df_engineer['Engineer'], df_engineer['Allocations'])), 
                         'Engineer Workload', 'Engineer', 'Allocations', chart_key=chart_key)
    
    st.markdown("---")
    total = df_engineer['Allocations'].sum()
    df_engineer['Percentage'] = (df_engineer['Allocations'] / total * 100).round(2).astype(str) + '%'
    st.dataframe(df_engineer, use_container_width=True, hide_index=True)

def render_timeline_analysis(allocations, chart_type="Bar Chart"):
    """Render timeline analysis with enhanced visuals"""
    timeline_data = []
    for a in allocations:
        try:
            start = datetime.strptime(a.get('start_date', '2024-01-01'), '%Y-%m-%d')
            end = datetime.strptime(a.get('end_date', '2024-12-31'), '%Y-%m-%d')
            duration = (end - start).days
            timeline_data.append({
                'Engineer': a.get('test_engineer_name', 'Unknown'),
                'System': a.get('system', 'Unknown'),
                'Start Date': start.strftime('%Y-%m-%d'),
                'End Date': end.strftime('%Y-%m-%d'),
                'Duration (Days)': duration,
                'Trial ID': a.get('trial_id', 'Unknown')
            })
        except:
            pass
    
    if not timeline_data:
        st.info("📊 No timeline data available")
        return
    
    df_timeline = pd.DataFrame(timeline_data)
    
    # Modern Metrics Cards
    col1, col2, col3 = st.columns(3)
    
    avg_duration = df_timeline['Duration (Days)'].mean()
    max_duration = df_timeline['Duration (Days)'].max()
    min_duration = df_timeline['Duration (Days)'].min()
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 12px; color: white; text-align: center;">
            <div style="font-size: 2rem; font-weight: 700;">{int(avg_duration)}</div>
            <div style="font-size: 0.875rem; opacity: 0.9;">AVG DURATION (DAYS)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 1.5rem; border-radius: 12px; color: white; text-align: center;">
            <div style="font-size: 2rem; font-weight: 700;">{int(max_duration)}</div>
            <div style="font-size: 0.875rem; opacity: 0.9;">LONGEST (DAYS)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1.5rem; border-radius: 12px; color: white; text-align: center;">
            <div style="font-size: 2rem; font-weight: 700;">{int(min_duration)}</div>
            <div style="font-size: 0.875rem; opacity: 0.9;">SHORTEST (DAYS)</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("##### 📊 Duration Distribution by Engineer")
    
    duration_data = df_timeline.groupby('Engineer')['Duration (Days)'].sum().to_dict()
    chart_key = generate_chart_key("timeline_duration", duration_data)
    
    if chart_type == "Bar Chart":
        render_bar_chart(duration_data, "", 'Engineer', 'Total Days', horizontal=True, colors=get_color_palette('warning'), chart_key=chart_key)
    elif chart_type == "Pie Chart":
        sorted_items = sorted(duration_data.items(), key=lambda x: x[1], reverse=True)[:10]
        render_pie_chart(dict(sorted_items), 'Duration Distribution (Top 10 Engineers)', colors=get_color_palette('gradient'), chart_key=chart_key)
    elif chart_type == "Line Chart":
        render_line_chart(duration_data, '', 'Engineer', 'Total Days', chart_key=chart_key)
    
    st.markdown("---")
    st.markdown("##### 📋 Detailed Timeline View")
    df_timeline_sorted = df_timeline.sort_values('Start Date', ascending=False)
    st.dataframe(df_timeline_sorted, use_container_width=True, hide_index=True)

def render_monthly_distribution(allocations, chart_type="Bar Chart"):
    """Render monthly allocation distribution"""
    monthly_data = {}
    for a in allocations:
        try:
            start = datetime.strptime(a.get('start_date', '2024-01-01'), '%Y-%m-%d')
            month_key = start.strftime('%Y-%m')
            monthly_data[month_key] = monthly_data.get(month_key, 0) + 1
        except:
            pass
    
    if not monthly_data:
        st.info("📊 No monthly data available")
        return
    
    chart_key = generate_chart_key("monthly_distribution", monthly_data)
    
    if chart_type == "Bar Chart":
        render_bar_chart(monthly_data, "Monthly Allocation Distribution", 'Month', 'Allocations', colors=get_color_palette('info'), chart_key=chart_key)
    elif chart_type == "Pie Chart":
        render_pie_chart(monthly_data, 'Monthly Allocation Distribution', colors=get_color_palette('gradient'), chart_key=chart_key)
    elif chart_type == "Line Chart":
        render_line_chart(monthly_data, 'Monthly Allocation Trend', 'Month', 'Allocations', area=True, chart_key=chart_key)

def render_therapeutic_area_distribution(allocations, chart_type="Pie Chart"):
    """Render therapeutic area distribution"""
    area_data = {}
    for a in allocations:
        area_type = a.get('therapeutic_area_type', '')
        if not area_type:
            area = a.get('therapeutic_area', 'Unknown')
            area_type = 'Others' if 'Others -' in area else area
        if area_type:
            area_data[area_type] = area_data.get(area_type, 0) + 1
    
    if not area_data:
        st.info("📊 No therapeutic area data available")
        return
    
    chart_key = generate_chart_key("therapeutic_area", area_data)
    
    if chart_type == "Bar Chart":
        render_bar_chart(area_data, "Therapeutic Area Distribution", 'Therapeutic Area', 'Count', colors=get_color_palette('success'), chart_key=chart_key)
    elif chart_type == "Pie Chart":
        render_pie_chart(area_data, 'Therapeutic Area Distribution', colors=get_color_palette('gradient'), chart_key=chart_key)
    elif chart_type == "Line Chart":
        render_line_chart(area_data, '', 'Therapeutic Area', 'Count', chart_key=chart_key)

def render_category_area_matrix(allocations, chart_type="Bar Chart"):
    """Render category vs therapeutic area matrix"""
    matrix_data = {}
    for a in allocations:
        cat_type = a.get('trial_category_type', 'Unknown')
        if not cat_type:
            cat = a.get('trial_category', 'Unknown')
            cat_type = 'Change Request' if 'Change Request' in cat else 'Build'
        
        area_type = a.get('therapeutic_area_type', '')
        if not area_type:
            area = a.get('therapeutic_area', 'Unknown')
            area_type = 'Others' if 'Others -' in area else area
        
        key = f"{cat_type} × {area_type}"
        matrix_data[key] = matrix_data.get(key, 0) + 1
    
    if not matrix_data:
        st.info("📊 No matrix data available")
        return
    
    chart_key = generate_chart_key("category_area_matrix", matrix_data)
    
    if chart_type == "Bar Chart":
        render_bar_chart(matrix_data, "Category × Therapeutic Area Matrix", 'Category-Area', 'Count', horizontal=True, chart_key=chart_key)
    elif chart_type == "Pie Chart":
        sorted_items = sorted(matrix_data.items(), key=lambda x: x[1], reverse=True)[:10]
        render_pie_chart(dict(sorted_items), 'Category × Area Matrix (Top 10)', colors=get_color_palette('gradient'), chart_key=chart_key)
    elif chart_type == "Line Chart":
        render_line_chart(matrix_data, '', 'Category-Area', 'Count', chart_key=chart_key)

# ============================================
# UAT SPECIFIC CHARTS
# ============================================

def render_status_distribution_chart(uat_records, chart_type="Pie Chart"):
    """Render UAT status distribution"""
    status_data = {}
    for r in uat_records:
        status = r.get('status', 'Unknown')
        status_data[status] = status_data.get(status, 0) + 1
    
    if not status_data:
        st.info("📊 No status data available")
        return
    
    status_colors = ['#FFC107', '#2196F3', '#4CAF50', '#FF9800', '#F44336']
    chart_key = generate_chart_key("uat_status", status_data)
    
    if chart_type == "Bar Chart":
        render_bar_chart(status_data, "UAT Status Distribution", 'Status', 'Count', colors=status_colors, chart_key=chart_key)
    elif chart_type == "Pie Chart":
        render_pie_chart(status_data, 'UAT Status Distribution', colors=status_colors, chart_key=chart_key)
    elif chart_type == "Line Chart":
        render_line_chart(status_data, '', 'Status', 'Count', chart_key=chart_key)

def render_result_distribution_chart(uat_records, chart_type="Pie Chart"):
    """Render UAT result distribution"""
    result_data = {}
    for r in uat_records:
        result = r.get('result', 'Unknown')
        result_data[result] = result_data.get(result, 0) + 1
    
    if not result_data:
        st.info("📊 No result data available")
        return
    
    result_colors = ['#9E9E9E', '#4CAF50', '#F44336', '#FF9800']
    chart_key = generate_chart_key("uat_result", result_data)
    
    if chart_type == "Bar Chart":
        render_bar_chart(result_data, "UAT Result Distribution", 'Result', 'Count', colors=result_colors, chart_key=chart_key)
    elif chart_type == "Pie Chart":
        render_pie_chart(result_data, 'UAT Result Distribution', colors=result_colors, chart_key=chart_key)
    elif chart_type == "Line Chart":
        render_line_chart(result_data, '', 'Result', 'Count', chart_key=chart_key)

def render_uat_category_distribution(uat_records, chart_type="Pie Chart"):
    """Render UAT category distribution"""
    category_data = {}
    for r in uat_records:
        cat_type = r.get('category_type', 'Unknown')
        category_data[cat_type] = category_data.get(cat_type, 0) + 1
    
    if not category_data:
        st.info("📊 No category data available")
        return
    
    chart_key = generate_chart_key("uat_category", category_data)
    
    if chart_type == "Bar Chart":
        render_bar_chart(category_data, "UAT Category Distribution", 'Category', 'Count', colors=get_color_palette('info'), chart_key=chart_key)
    elif chart_type == "Pie Chart":
        render_pie_chart(category_data, 'UAT Category Distribution', colors=get_color_palette('info'), chart_key=chart_key)
    elif chart_type == "Line Chart":
        render_line_chart(category_data, '', 'Category', 'Count', chart_key=chart_key)

def render_uat_round_distribution(uat_records, chart_type="Bar Chart"):
    """Render UAT round distribution"""
    round_data = {}
    for r in uat_records:
        uat_round = r.get('uat_round', 'Unknown')
        round_data[uat_round] = round_data.get(uat_round, 0) + 1
    
    if not round_data:
        st.info("📊 No UAT round data available")
        return
    
    chart_key = generate_chart_key("uat_round", round_data)
    
    df_round = pd.DataFrame(list(round_data.items()), columns=['UAT Round', 'Count'])
    df_round = df_round.sort_values('Count', ascending=False)
    
    if chart_type == "Bar Chart":
        render_bar_chart(round_data, "UAT Round Distribution", 'UAT Round', 'Count', colors=get_color_palette('primary'), chart_key=chart_key)
    elif chart_type == "Pie Chart":
        render_pie_chart(round_data, 'UAT Round Distribution', colors=get_color_palette('gradient'), chart_key=chart_key)
    elif chart_type == "Line Chart":
        render_line_chart(round_data, '', 'UAT Round', 'Count', chart_key=chart_key)
    
    st.markdown("---")
    st.dataframe(df_round, use_container_width=True, hide_index=True)

def render_uat_timeline_analysis(uat_records, chart_type="Bar Chart"):
    """Render comprehensive UAT timeline analysis"""
    timeline_data = []
    for r in uat_records:
        try:
            planned_start = datetime.strptime(r.get('planned_start_date', '2024-01-01'), '%Y-%m-%d')
            planned_end = datetime.strptime(r.get('planned_end_date', '2024-12-31'), '%Y-%m-%d')
            planned_duration = (planned_end - planned_start).days
            
            actual_start = r.get('actual_start_date')
            actual_end = r.get('actual_end_date')
            
            actual_duration = None
            if actual_start and actual_end:
                actual_start_dt = datetime.strptime(actual_start, '%Y-%m-%d')
                actual_end_dt = datetime.strptime(actual_end, '%Y-%m-%d')
                actual_duration = (actual_end_dt - actual_start_dt).days
            
            timeline_data.append({
                'Trial ID': r.get('trial_id'),
                'UAT Round': r.get('uat_round'),
                'Category': r.get('category', 'N/A'),
                'Created By': r.get('created_by', 'N/A'),
                'Planned Duration (Days)': planned_duration,
                'Actual Duration (Days)': actual_duration if actual_duration else 'Not Completed',
                'Status': r.get('status')
            })
        except:
            pass
    
    if not timeline_data:
        st.info("📊 No timeline data available")
        return
    
    df_timeline = pd.DataFrame(timeline_data)
    completed_records = df_timeline[df_timeline['Actual Duration (Days)'] != 'Not Completed']
    
    # Modern Metrics
    col1, col2, col3 = st.columns(3)
    
    avg_planned = df_timeline['Planned Duration (Days)'].mean()
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 12px; color: white; text-align: center;">
            <div style="font-size: 2rem; font-weight: 700;">{int(avg_planned)}</div>
            <div style="font-size: 0.875rem; opacity: 0.9;">AVG PLANNED (DAYS)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if len(completed_records) > 0:
            avg_actual = completed_records['Actual Duration (Days)'].mean()
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        padding: 1.5rem; border-radius: 12px; color: white; text-align: center;">
                <div style="font-size: 2rem; font-weight: 700;">{int(avg_actual)}</div>
                <div style="font-size: 0.875rem; opacity: 0.9;">AVG ACTUAL (DAYS)</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No completed records")
    
    with col3:
        completion_rate = (len(completed_records) / len(df_timeline) * 100) if len(df_timeline) > 0 else 0
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                    padding: 1.5rem; border-radius: 12px; color: white; text-align: center;">
            <div style="font-size: 2rem; font-weight: 700;">{completion_rate:.1f}%</div>
            <div style="font-size: 0.875rem; opacity: 0.9;">COMPLETION RATE</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("##### 📋 Detailed Timeline Data")
    st.dataframe(df_timeline, use_container_width=True, hide_index=True)

def render_uat_user_workload(uat_records, chart_type="Bar Chart"):
    """Render UAT user workload distribution"""
    user_data = {}
    for r in uat_records:
        user = r.get('created_by', 'Unknown')
        user_data[user] = user_data.get(user, 0) + 1
    
    if not user_data:
        st.info("📊 No user data available")
        return
    
    df_user = pd.DataFrame(list(user_data.items()), columns=['User', 'UAT Records'])
    df_user = df_user.sort_values('UAT Records', ascending=False)
    
    chart_key = generate_chart_key("uat_user_workload", user_data)
    
    if chart_type == "Bar Chart":
        render_bar_chart(user_data, "User UAT Workload Distribution", 'User', 'UAT Records', horizontal=True, colors=get_color_palette('success'), chart_key=chart_key)
    elif chart_type == "Pie Chart":
        render_pie_chart(user_data, 'User UAT Workload Distribution', colors=get_color_palette('gradient'), chart_key=chart_key)
    elif chart_type == "Line Chart":
        render_line_chart(user_data, '', 'User', 'UAT Records', chart_key=chart_key)
    
    st.markdown("---")
    total_records = len(uat_records)
    df_user['Percentage'] = (df_user['UAT Records'] / total_records * 100).round(2).astype(str) + '%'
    st.dataframe(df_user, use_container_width=True, hide_index=True)

def render_uat_monthly_distribution(uat_records, chart_type="Bar Chart"):
    """Render monthly UAT distribution"""
    monthly_data = {}
    for r in uat_records:
        try:
            planned_start = datetime.strptime(r.get('planned_start_date', '2024-01-01'), '%Y-%m-%d')
            month_key = planned_start.strftime('%Y-%m')
            monthly_data[month_key] = monthly_data.get(month_key, 0) + 1
        except:
            pass
    
    if not monthly_data:
        st.info("📊 No monthly data available")
        return
    
    chart_key = generate_chart_key("uat_monthly", monthly_data)
    
    if chart_type == "Bar Chart":
        render_bar_chart(monthly_data, "Monthly UAT Distribution", 'Month', 'UAT Records', colors=get_color_palette('info'), chart_key=chart_key)
    elif chart_type == "Pie Chart":
        render_pie_chart(monthly_data, 'Monthly UAT Distribution', colors=get_color_palette('gradient'), chart_key=chart_key)
    elif chart_type == "Line Chart":
        render_line_chart(monthly_data, 'Monthly UAT Trend', 'Month', 'UAT Records', area=True, chart_key=chart_key)

def render_uat_status_result_matrix(uat_records, chart_type="Bar Chart"):
    """Render UAT status vs result matrix"""
    matrix_data = {}
    for r in uat_records:
        status = r.get('status', 'Unknown')
        result = r.get('result', 'Unknown')
        key = f"{status} × {result}"
        matrix_data[key] = matrix_data.get(key, 0) + 1
    
    if not matrix_data:
        st.info("📊 No matrix data available")
        return
    
    df_matrix = pd.DataFrame(list(matrix_data.items()), columns=['Status-Result', 'Count'])
    df_matrix = df_matrix.sort_values('Count', ascending=False)
    
    chart_key = generate_chart_key("uat_status_result_matrix", matrix_data)
    
    if chart_type == "Bar Chart":
        render_bar_chart(matrix_data, "Status × Result Matrix", 'Status-Result', 'Count', horizontal=True, chart_key=chart_key)
    elif chart_type == "Pie Chart":
        sorted_items = sorted(matrix_data.items(), key=lambda x: x[1], reverse=True)[:10]
        render_pie_chart(dict(sorted_items), 'Status × Result Matrix (Top 10)', colors=get_color_palette('gradient'), chart_key=chart_key)
    elif chart_type == "Line Chart":
        render_line_chart(matrix_data, '', 'Status-Result', 'Count', chart_key=chart_key)
    
    st.markdown("---")
    st.dataframe(df_matrix, use_container_width=True, hide_index=True)