# pages/audit/audit_viewer.py
"""
Audit log viewer with modern professional UI
Enhanced visualizations and typography
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from services.audit_service import get_audit_logs_filtered, load_audit_logs
from utils.auth import get_current_user, get_current_role
from config import AUDIT_ACTIONS, AUDIT_MODULES
from utils.helpers import format_datetime
from typing import Dict

# Modern CSS Styling
def inject_custom_css():
    st.markdown("""
    <style>
    /* Import Modern Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Font */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    
    /* Main Title */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: white;
        text-align: center;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Filter Section */
    .filter-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid #e9ecef;
    }
    
    /* Log Cards */
    .log-card {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .log-card:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border-color: #667eea;
    }
    
    .log-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .log-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-login { background: #d4edda; color: #155724; }
    .badge-logout { background: #f8d7da; color: #721c24; }
    .badge-create { background: #d1ecf1; color: #0c5460; }
    .badge-update { background: #fff3cd; color: #856404; }
    .badge-delete { background: #f8d7da; color: #721c24; }
    .badge-approve { background: #d4edda; color: #155724; }
    .badge-reject { background: #f8d7da; color: #721c24; }
    
    /* Timeline */
    .timeline-item {
        position: relative;
        padding-left: 2rem;
        padding-bottom: 1.5rem;
        border-left: 2px solid #e9ecef;
    }
    
    .timeline-item:last-child {
        border-left: none;
    }
    
    .timeline-dot {
        position: absolute;
        left: -0.5rem;
        width: 1rem;
        height: 1rem;
        border-radius: 50%;
        background: #667eea;
        border: 3px solid white;
        box-shadow: 0 0 0 2px #667eea;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    </style>
    """, unsafe_allow_html=True)

def render_audit_viewer_tab():
    """Render modern audit log viewer with enhanced visualizations"""
    inject_custom_css()
    
    # Header with gradient
    st.markdown('<h1 class="main-title">📊 Activity Monitor</h1>', unsafe_allow_html=True)
    st.markdown("Track and analyze all system activities in real-time")
    
    # Get all logs
    all_logs = load_audit_logs()
    
    if not all_logs:
        st.info("📝 No audit logs available yet. Activity will be logged as you use the system.")
        return
    
    # Convert to DataFrame for analytics
    df = pd.DataFrame(all_logs)
    
    # TOP METRICS DASHBOARD
    render_metrics_dashboard(df)
    
    st.markdown("---")
    
    # FILTERS SECTION
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.markdown("### 🔍 Smart Filters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        users = ["All"] + sorted(list(set([log.get('user', 'Unknown') for log in all_logs])))
        filter_user = st.selectbox("👤 User", users, key="audit_filter_user")
    
    with col2:
        actions = ["All"] + sorted(list(set([log.get('action', 'Unknown') for log in all_logs])))
        filter_action = st.selectbox("⚡ Action", actions, key="audit_filter_action")
    
    with col3:
        modules = ["All"] + sorted(list(set([log.get('module', 'Unknown') for log in all_logs])))
        filter_module = st.selectbox("📦 Module", modules, key="audit_filter_module")
    
    with col4:
        date_preset = st.selectbox(
            "📅 Time Range",
            ["All Time", "Today", "Last 7 Days", "Last 30 Days", "Custom"],
            key="audit_date_preset"
        )
    
    # Custom date range
    start_date = None
    end_date = None
    
    if date_preset == "Custom":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From Date", key="audit_start_date")
        with col2:
            end_date = st.date_input("To Date", key="audit_end_date")
    elif date_preset == "Today":
        start_date = end_date = datetime.now().date()
    elif date_preset == "Last 7 Days":
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
    elif date_preset == "Last 30 Days":
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filters = {
        'user': filter_user,
        'action': filter_action,
        'module': filter_module,
        'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
        'end_date': end_date.strftime('%Y-%m-%d') if end_date else None
    }
    
    filtered_logs = get_audit_logs_filtered(filters)
    
    # ANALYTICS CHARTS
    if len(filtered_logs) > 0:
        render_analytics_section(filtered_logs)
    
    st.markdown("---")
    
    # RESULTS HEADER
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 📋 Activity Log ({len(filtered_logs)} entries)")
    with col2:
        view_mode = st.radio("View", ["Cards", "Timeline", "Table"], horizontal=True, key="view_mode")
    
    # Display logs based on view mode
    if filtered_logs:
        if view_mode == "Cards":
            render_log_cards(filtered_logs)
        elif view_mode == "Timeline":
            render_timeline_view(filtered_logs)
        else:
            render_table_view(filtered_logs)
    else:
        st.info("🔍 No logs match the selected filters.")

def render_metrics_dashboard(df):
    """Render top metrics with modern cards"""
    st.markdown("### 📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Total Activities
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div class="metric-label">Total Activities</div>
            <div class="metric-value">{len(df)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Unique Users
    with col2:
        unique_users = df['user'].nunique() if 'user' in df.columns else 0
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="metric-label">Active Users</div>
            <div class="metric-value">{unique_users}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Today's Activities
    with col3:
        today = datetime.now().date()
        if 'timestamp' in df.columns:
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
            today_count = len(df[df['date'] == today])
        else:
            today_count = 0
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="metric-label">Today's Activity</div>
            <div class="metric-value">{today_count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Most Active Module
    with col4:
        if 'module' in df.columns:
            most_active = df['module'].mode()[0] if len(df) > 0 else "N/A"
        else:
            most_active = "N/A"
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="metric-label">Most Active</div>
            <div class="metric-value" style="font-size: 1.5rem;">{most_active}</div>
        </div>
        """, unsafe_allow_html=True)

def render_analytics_section(logs):
    """Render interactive analytics charts"""
    st.markdown("### 📊 Activity Analytics")
    
    df = pd.DataFrame(logs)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Actions distribution - Donut Chart
        if 'action' in df.columns:
            action_counts = df['action'].value_counts()
            fig = go.Figure(data=[go.Pie(
                labels=action_counts.index,
                values=action_counts.values,
                hole=.4,
                marker=dict(colors=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'])
            )])
            fig.update_layout(
                title="Actions Distribution",
                font=dict(family="Inter, sans-serif"),
                height=350,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Module activity - Bar Chart
        if 'module' in df.columns:
            module_counts = df['module'].value_counts()
            fig = go.Figure(data=[go.Bar(
                x=module_counts.index,
                y=module_counts.values,
                marker=dict(
                    color=module_counts.values,
                    colorscale='Viridis'
                )
            )])
            fig.update_layout(
                title="Module Activity",
                xaxis_title="Module",
                yaxis_title="Count",
                font=dict(family="Inter, sans-serif"),
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Timeline Chart
    if 'timestamp' in df.columns:
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        timeline_data = df.groupby('date').size().reset_index(name='count')
        
        fig = go.Figure(data=[go.Scatter(
            x=timeline_data['date'],
            y=timeline_data['count'],
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8, color='#764ba2')
        )])
        fig.update_layout(
            title="Activity Timeline",
            xaxis_title="Date",
            yaxis_title="Activities",
            font=dict(family="Inter, sans-serif"),
            height=300,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

def render_log_cards(logs):
    """Render logs as modern cards"""
    for log in reversed(logs[-50:]):  # Show last 50
        action = log.get('action', 'UNKNOWN')
        user = log.get('user', 'Unknown')
        timestamp = log.get('timestamp', 'N/A')
        module = log.get('module', 'Unknown')
        
        action_emoji = {
            "LOGIN": "🔐", "LOGOUT": "🚪", "CREATE": "➕",
            "UPDATE": "✏️", "DELETE": "🗑️", "VIEW": "👁️",
            "EXPORT": "📥", "APPROVE": "✅", "REJECT": "❌"
        }.get(action, "📝")
        
        badge_class = f"badge-{action.lower()}"
        
        st.markdown(f"""
        <div class="log-card">
            <div class="log-header">
                <span style="font-size: 1.5rem;">{action_emoji}</span>
                <span>{user}</span>
                <span class="log-badge {badge_class}">{action}</span>
                <span style="margin-left: auto; color: #6c757d; font-size: 0.875rem;">{timestamp}</span>
            </div>
            <div style="color: #6c757d; margin-bottom: 0.5rem;">
                📦 {module}
            </div>
            <div style="background: #f8f9fa; padding: 0.75rem; border-radius: 6px; font-size: 0.875rem;">
                {log.get('details', 'No details available')}
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_timeline_view(logs):
    """Render logs as timeline"""
    st.markdown('<div style="padding: 1rem;">', unsafe_allow_html=True)
    for log in reversed(logs[-50:]):
        action_emoji = {
            "LOGIN": "🔐", "LOGOUT": "🚪", "CREATE": "➕",
            "UPDATE": "✏️", "DELETE": "🗑️", "VIEW": "👁️",
            "EXPORT": "📥", "APPROVE": "✅", "REJECT": "❌"
        }.get(log.get('action', ''), "📝")
        
        st.markdown(f"""
        <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div style="font-weight: 600; margin-bottom: 0.25rem;">
                {action_emoji} {log.get('user', 'Unknown')} - {log.get('action', 'UNKNOWN')}
            </div>
            <div style="color: #6c757d; font-size: 0.875rem; margin-bottom: 0.5rem;">
                {log.get('timestamp', 'N/A')} • {log.get('module', 'Unknown')}
            </div>
            <div style="color: #495057; font-size: 0.875rem;">
                {log.get('details', 'No details')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_table_view(logs):
    """Render logs as interactive table"""
    df = pd.DataFrame(logs[-50:])
    display_cols = ['timestamp', 'user', 'action', 'module', 'details']
    available_cols = [col for col in display_cols if col in df.columns]
    
    if available_cols:
        st.dataframe(
            df[available_cols].sort_values('timestamp', ascending=False),
            use_container_width=True,
            height=600
        )