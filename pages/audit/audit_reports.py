# pages/audit/audit_reports.py
"""
Audit reporting features - Modern Professional UI
Advanced compliance reports with interactive visualizations
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import List, Dict
import json

# Modern CSS for Reports
def inject_reports_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Report Container */
    .report-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        margin-bottom: 2rem;
    }
    
    /* Report Header */
    .report-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 16px;
        margin-bottom: 2rem;
    }
    
    .report-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .report-subtitle {
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    /* Report Stats */
    .report-stat-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border-left: 4px solid #667eea;
        transition: all 0.3s;
        height: 100%;
    }
    
    .report-stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .report-stat-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
    }
    
    .report-stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }
    
    .report-stat-label {
        color: #718096;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Section Headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e9ecef;
    }
    
    .section-icon {
        font-size: 1.5rem;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a202c;
    }
    
    /* Summary Box */
    .summary-box {
        background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
        border-left: 4px solid #00acc1;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
    }
    
    .summary-title {
        font-weight: 700;
        color: #006064;
        margin-bottom: 0.75rem;
        font-size: 1.1rem;
    }
    
    .summary-content {
        color: #00838f;
        line-height: 1.8;
    }
    
    /* Table Styles */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Export Section */
    .export-card {
        background: white;
        border: 2px dashed #cbd5e0;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s;
    }
    
    .export-card:hover {
        border-color: #667eea;
        background: #f8f9fa;
    }
    
    .export-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    /* Timeline Item */
    .timeline-item {
        position: relative;
        padding-left: 2.5rem;
        padding-bottom: 2rem;
        border-left: 3px solid #e9ecef;
    }
    
    .timeline-item:last-child {
        border-left: none;
    }
    
    .timeline-dot {
        position: absolute;
        left: -0.65rem;
        width: 1.25rem;
        height: 1.25rem;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: 3px solid white;
        box-shadow: 0 0 0 3px #667eea33;
    }
    
    .timeline-content {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Alert Styles */
    .alert-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 8px;
        color: #155724;
        margin: 1rem 0;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 8px;
        color: #856404;
        margin: 1rem 0;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        border-radius: 8px;
        color: #0c5460;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def generate_compliance_report(logs: List[Dict], start_date: str, end_date: str) -> Dict:
    """Generate comprehensive compliance report with analytics"""
    
    if not logs:
        return {
            'period': f"{start_date} to {end_date}",
            'total_activities': 0,
            'users_active': 0,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'compliance_score': 0
        }
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(logs)
    
    # Calculate metrics
    total_activities = len(logs)
    unique_users = df['user'].nunique() if 'user' in df.columns else 0
    unique_actions = df['action'].nunique() if 'action' in df.columns else 0
    unique_modules = df['module'].nunique() if 'module' in df.columns else 0
    
    # Action breakdown
    action_breakdown = df['action'].value_counts().to_dict() if 'action' in df.columns else {}
    
    # Module breakdown
    module_breakdown = df['module'].value_counts().to_dict() if 'module' in df.columns else {}
    
    # User activity
    user_activity = df['user'].value_counts().to_dict() if 'user' in df.columns else {}
    
    # Daily activity
    if 'timestamp' in df.columns:
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily_activity = df.groupby('date').size().to_dict()
        daily_activity = {str(k): v for k, v in daily_activity.items()}
    else:
        daily_activity = {}
    
    # Calculate compliance score (example logic)
    compliance_score = min(100, (total_activities / 100) * 50 + (unique_users * 10))
    
    # Security events
    security_actions = ['LOGIN', 'LOGOUT', 'DELETE', 'REJECT']
    security_events = len(df[df['action'].isin(security_actions)]) if 'action' in df.columns else 0
    
    report = {
        'period': f"{start_date} to {end_date}",
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'summary': {
            'total_activities': total_activities,
            'users_active': unique_users,
            'unique_actions': unique_actions,
            'unique_modules': unique_modules,
            'compliance_score': round(compliance_score, 2),
            'security_events': security_events
        },
        'breakdowns': {
            'by_action': action_breakdown,
            'by_module': module_breakdown,
            'by_user': user_activity,
            'by_date': daily_activity
        },
        'raw_data': logs
    }
    
    return report

def generate_user_activity_report(username: str, days: int = 30) -> Dict:
    """Generate detailed user activity report"""
    from services.audit_service import get_user_activity
    
    activities = get_user_activity(username, days)
    
    if not activities:
        return {
            'username': username,
            'period_days': days,
            'total_activities': 0,
            'activities': []
        }
    
    # Convert to DataFrame
    df = pd.DataFrame(activities)
    
    # Calculate metrics
    total_activities = len(activities)
    actions_performed = df['action'].value_counts().to_dict() if 'action' in df.columns else {}
    modules_accessed = df['module'].value_counts().to_dict() if 'module' in df.columns else {}
    
    # Daily activity
    if 'timestamp' in df.columns:
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily_activity = df.groupby('date').size().to_dict()
        daily_activity = {str(k): v for k, v in daily_activity.items()}
    else:
        daily_activity = {}
    
    # Most active time (hour of day)
    if 'timestamp' in df.columns:
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        hourly_activity = df['hour'].value_counts().to_dict()
    else:
        hourly_activity = {}
    
    report = {
        'username': username,
        'period_days': days,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'summary': {
            'total_activities': total_activities,
            'actions_performed': len(actions_performed),
            'modules_accessed': len(modules_accessed),
            'average_daily': round(total_activities / days, 2) if days > 0 else 0
        },
        'breakdowns': {
            'by_action': actions_performed,
            'by_module': modules_accessed,
            'by_date': daily_activity,
            'by_hour': hourly_activity
        },
        'activities': activities
    }
    
    return report

def render_compliance_report_page():
    """Render interactive compliance report page"""
    inject_reports_css()
    
    st.markdown("""
    <div class="report-header">
        <div class="report-title">📊 Compliance Report Generator</div>
        <div class="report-subtitle">Generate comprehensive audit compliance reports</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Report Configuration
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Report Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input(
            "📅 Start Date",
            value=datetime.now().date() - timedelta(days=30),
            key="report_start_date"
        )
    
    with col2:
        end_date = st.date_input(
            "📅 End Date",
            value=datetime.now().date(),
            key="report_end_date"
        )
    
    with col3:
        report_format = st.selectbox(
            "📄 Format",
            ["Interactive Dashboard", "PDF Report", "Excel Spreadsheet"],
            key="report_format"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate Report Button
    if st.button("🚀 Generate Report", type="primary", use_container_width=True):
        with st.spinner("Generating comprehensive report..."):
            # Get filtered logs
            from services.audit_service import load_audit_logs
            all_logs = load_audit_logs()
            
            # Filter by date range
            filtered_logs = [
                log for log in all_logs
                if start_date <= datetime.strptime(log.get('timestamp', ''), '%Y-%m-%d %H:%M:%S').date() <= end_date
            ] if all_logs else []
            
            # Generate report
            report = generate_compliance_report(
                filtered_logs,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            # Store in session state
            st.session_state['compliance_report'] = report
            st.success("✅ Report generated successfully!")
    
    # Display Report
    if 'compliance_report' in st.session_state:
        report = st.session_state['compliance_report']
        render_compliance_report_display(report)

def render_compliance_report_display(report: Dict):
    """Display the generated compliance report"""
    
    st.markdown("---")
    
    # Report Header
    st.markdown(f"""
    <div class="summary-box">
        <div class="summary-title">📋 Report Summary</div>
        <div class="summary-content">
            <strong>Period:</strong> {report['period']}<br>
            <strong>Generated:</strong> {report['generated_at']}<br>
            <strong>Total Activities:</strong> {report['summary']['total_activities']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics
    st.markdown('<div class="section-header">', unsafe_allow_html=True)
    st.markdown('<span class="section-icon">📈</span><span class="section-title">Key Metrics</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("Total Activities", report['summary']['total_activities'], "📊", "#667eea"),
        ("Active Users", report['summary']['users_active'], "👥", "#f093fb"),
        ("Compliance Score", f"{report['summary']['compliance_score']}%", "✅", "#43e97b"),
        ("Security Events", report['summary']['security_events'], "🔒", "#f5576c")
    ]
    
    for col, (label, value, icon, color) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f"""
            <div class="report-stat-card">
                <div class="report-stat-icon">{icon}</div>
                <div class="report-stat-value">{value}</div>
                <div class="report-stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Visualizations
    st.markdown('<div class="section-header">', unsafe_allow_html=True)
    st.markdown('<span class="section-icon">📊</span><span class="section-title">Activity Analysis</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Action Distribution
        if report['breakdowns']['by_action']:
            fig = go.Figure(data=[go.Pie(
                labels=list(report['breakdowns']['by_action'].keys()),
                values=list(report['breakdowns']['by_action'].values()),
                hole=.4,
                marker=dict(colors=px.colors.qualitative.Set3)
            )])
            fig.update_layout(
                title="Action Distribution",
                font=dict(family="Inter, sans-serif"),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Module Distribution
        if report['breakdowns']['by_module']:
            fig = go.Figure(data=[go.Bar(
                x=list(report['breakdowns']['by_module'].keys()),
                y=list(report['breakdowns']['by_module'].values()),
                marker=dict(
                    color=list(report['breakdowns']['by_module'].values()),
                    colorscale='Viridis'
                )
            )])
            fig.update_layout(
                title="Module Activity",
                xaxis_title="Module",
                yaxis_title="Count",
                font=dict(family="Inter, sans-serif"),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Timeline Chart
    if report['breakdowns']['by_date']:
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.markdown('<span class="section-icon">📅</span><span class="section-title">Activity Timeline</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        dates = sorted(report['breakdowns']['by_date'].keys())
        values = [report['breakdowns']['by_date'][date] for date in dates]
        
        fig = go.Figure(data=[go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8, color='#764ba2')
        )])
        fig.update_layout(
            title="Daily Activity Trend",
            xaxis_title="Date",
            yaxis_title="Activities",
            font=dict(family="Inter, sans-serif"),
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # User Activity Table
    if report['breakdowns']['by_user']:
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.markdown('<span class="section-icon">👥</span><span class="section-title">User Activity Breakdown</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        user_df = pd.DataFrame([
            {'User': user, 'Activities': count}
            for user, count in report['breakdowns']['by_user'].items()
        ]).sort_values('Activities', ascending=False)
        
        st.dataframe(user_df, use_container_width=True, height=300)
    
    # Export Options
    st.markdown("---")
    st.markdown('<div class="section-header">', unsafe_allow_html=True)
    st.markdown('<span class="section-icon">📥</span><span class="section-title">Export Report</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON Export
        json_data = json.dumps(report, indent=2)
        st.download_button(
            label="📄 Download JSON",
            data=json_data,
            file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Excel Export
        from utils.excel_handler import convert_to_excel
        excel_data = convert_to_excel(report['raw_data'], "Compliance Report")
        if excel_data:
            st.download_button(
                label="📊 Download Excel",
                data=excel_data,
                file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    with col3:
        # PDF Export (placeholder)
        st.button(
            "📑 Download PDF",
            use_container_width=True,
            disabled=True,
            help="PDF export coming soon"
        )

def render_user_activity_report_page():
    """Render user activity report page"""
    inject_reports_css()
    
    st.markdown("""
    <div class="report-header">
        <div class="report-title">👤 User Activity Report</div>
        <div class="report-subtitle">Detailed analysis of individual user activities</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuration
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Report Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Get all users
        from services.audit_service import load_audit_logs
        all_logs = load_audit_logs()
        users = sorted(list(set([log.get('user', 'Unknown') for log in all_logs]))) if all_logs else []
        
        username = st.selectbox("👤 Select User", users, key="user_report_username")
    
    with col2:
        days = st.slider("📅 Period (Days)", min_value=7, max_value=90, value=30, key="user_report_days")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate Button
    if st.button("🚀 Generate User Report", type="primary", use_container_width=True):
        with st.spinner(f"Generating activity report for {username}..."):
            report = generate_user_activity_report(username, days)
            st.session_state['user_activity_report'] = report
            st.success("✅ User report generated successfully!")
    
    # Display Report
    if 'user_activity_report' in st.session_state:
        report = st.session_state['user_activity_report']
        render_user_activity_display(report)

def render_user_activity_display(report: Dict):
    """Display user activity report"""
    
    st.markdown("---")
    
    # Summary
    st.markdown(f"""
    <div class="summary-box">
        <div class="summary-title">👤 User: {report['username']}</div>
        <div class="summary-content">
            <strong>Analysis Period:</strong> Last {report['period_days']} days<br>
            <strong>Generated:</strong> {report['generated_at']}<br>
            <strong>Total Activities:</strong> {report['summary']['total_activities']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("Total Activities", report['summary']['total_activities'], "📊"),
        ("Actions", report['summary']['actions_performed'], "⚡"),
        ("Modules", report['summary']['modules_accessed'], "📦"),
        ("Avg Daily", report['summary']['average_daily'], "📈")
    ]
    
    for col, (label, value, icon) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f"""
            <div class="report-stat-card">
                <div class="report-stat-icon">{icon}</div>
                <div class="report-stat-value">{value}</div>
                <div class="report-stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        if report['breakdowns']['by_action']:
            fig = go.Figure(data=[go.Pie(
                labels=list(report['breakdowns']['by_action'].keys()),
                values=list(report['breakdowns']['by_action'].values()),
                hole=.4
            )])
            fig.update_layout(title="Actions Performed", font=dict(family="Inter"), height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if report['breakdowns']['by_module']:
            fig = go.Figure(data=[go.Bar(
                x=list(report['breakdowns']['by_module'].keys()),
                y=list(report['breakdowns']['by_module'].values()),
                marker=dict(color='#667eea')
            )])
            fig.update_layout(title="Modules Accessed", font=dict(family="Inter"), height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    # Activity Timeline
    if report['breakdowns']['by_date']:
        dates = sorted(report['breakdowns']['by_date'].keys())
        values = [report['breakdowns']['by_date'][date] for date in dates]
        
        fig = go.Figure(data=[go.Scatter(
            x=dates, y=values,
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='#667eea', width=3)
        )])
        fig.update_layout(
            title="Activity Timeline",
            xaxis_title="Date",
            yaxis_title="Activities",
            font=dict(family="Inter"),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)