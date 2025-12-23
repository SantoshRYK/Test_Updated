# pages/audit/audit_main.py
"""
Main Audit Trail page - Modern Professional UI
ROUTER for all audit features with enhanced visualizations
"""
import streamlit as st
from pages.audit.audit_viewer import render_audit_viewer_tab
from services.audit_service import log_page_view
from utils.auth import get_current_role
from datetime import datetime

# Modern CSS Styling
def inject_audit_main_css():
    st.markdown("""
    <style>
    /* Import Modern Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        opacity: 0.95;
        font-weight: 400;
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 2px solid transparent;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    .feature-card:hover::before {
        transform: scaleX(1);
    }
    
    .feature-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .feature-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
        color: #1a202c;
    }
    
    .feature-description {
        color: #718096;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    
    .feature-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 1rem;
    }
    
    /* Role Badge */
    .role-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 30px;
        font-weight: 600;
        font-size: 0.95rem;
        box-shadow: 0 4px 12px rgba(245, 87, 108, 0.3);
        margin: 1rem 0;
    }
    
    .superuser-badge {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
        border-left: 4px solid #00acc1;
        padding: 1.25rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        color: #006064;
        font-weight: 500;
    }
    
    .info-box-icon {
        font-size: 1.5rem;
        margin-right: 0.75rem;
        vertical-align: middle;
    }
    
    /* Back Button */
    .back-button {
        background: white;
        border: 2px solid #e2e8f0;
        color: #4a5568;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 2rem;
    }
    
    .back-button:hover {
        background: #f7fafc;
        border-color: #667eea;
        color: #667eea;
        transform: translateX(-4px);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f7fafc;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        background-color: transparent;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Metrics Grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card-main {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #667eea;
        transition: all 0.3s;
    }
    
    .metric-card-main:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
    }
    
    .metric-value-main {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }
    
    .metric-label-main {
        color: #718096;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Download Buttons */
    .download-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        border: 2px solid #dee2e6;
        transition: all 0.3s;
    }
    
    .download-card:hover {
        border-color: #667eea;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
    }
    
    .download-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)

def render_audit_page():
    """Main audit trail page with modern professional UI"""
    inject_audit_main_css()
    log_page_view("audit")
    
    current_role = get_current_role()
    
    # Hero Section
    st.markdown("""
    <div class="hero-section fade-in-up">
        <div class="hero-title">🔍 Audit & Trail Center</div>
        <div class="hero-subtitle">Complete visibility into system activities and document trails</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Back Button
    if st.button("⬅️ Back to Home", key="audit_back_home"):
        st.session_state.current_page = "home"
        st.rerun()
    
    # Show different views based on role
    if current_role == "superuser":
        render_superuser_audit_menu()
    else:
        render_user_trail_documents()

def render_superuser_audit_menu():
    """Render modern menu for superuser with both options"""
    
    # Role Badge
    st.markdown("""
    <div style="text-align: center;">
        <span class="role-badge superuser-badge">
            <span>👑</span>
            <span>SUPER USER ACCESS</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box fade-in-up">
        <span class="info-box-icon">✨</span>
        <strong>Full Access Granted:</strong> You have complete access to System Audit Logs and Trail Audit Documents
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Feature Cards
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="feature-card fade-in-up">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">System Audit Logs</div>
            <div class="feature-description">
                Monitor all system activities, security events, and user actions in real-time.
                Advanced analytics and comprehensive reporting.
            </div>
            <span class="feature-badge">🔒 Security & Monitoring</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Access System Audit", key="system_audit_btn", use_container_width=True, type="primary"):
            st.session_state.audit_view = "system_logs"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="feature-card fade-in-up" style="animation-delay: 0.1s;">
            <div class="feature-icon">📋</div>
            <div class="feature-title">Trail Audit Documents</div>
            <div class="feature-description">
                Track test engineer document approvals, go-live dates, and compliance records.
                Streamlined workflow management.
            </div>
            <span class="feature-badge">📊 Document Tracking</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📁 Manage Trail Documents", key="trail_docs_btn", use_container_width=True, type="primary"):
            st.session_state.audit_view = "trail_documents"
            st.rerun()
    
    st.markdown("---")
    
    # Show selected view
    audit_view = st.session_state.get('audit_view', None)
    
    if audit_view == "system_logs":
        render_system_audit_logs()
    elif audit_view == "trail_documents":
        from pages.audit.trail_documents import render_trail_documents_page
        render_trail_documents_page()

def render_user_trail_documents():
    """Render trail documents with role-based styling"""
    from pages.audit.trail_documents import render_trail_documents_page
    
    current_role = get_current_role()
    
    # Role-based badge and message
    role_config = {
        "admin": {
            "emoji": "👨‍💼",
            "title": "ADMIN ACCESS",
            "message": "Full management access to Trail Audit Documents",
            "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        },
        "manager": {
            "emoji": "👔",
            "title": "MANAGER ACCESS",
            "message": "View and manage team Trail Audit Documents",
            "gradient": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
        },
        "user": {
            "emoji": "👤",
            "title": "USER ACCESS",
            "message": "View and manage your Trail Audit Documents",
            "gradient": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
        }
    }
    
    config = role_config.get(current_role, role_config["user"])
    
    st.markdown(f"""
    <div style="text-align: center;">
        <span class="role-badge" style="background: {config['gradient']};">
            <span>{config['emoji']}</span>
            <span>{config['title']}</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="info-box fade-in-up">
        <span class="info-box-icon">📋</span>
        <strong>{config['message']}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Directly show trail documents page
    render_trail_documents_page()

def render_system_audit_logs():
    """Render system audit logs with modern tabs"""
    
    # Header with back button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("⬅️ Back", key="back_to_audit_menu"):
            st.session_state.audit_view = None
            st.rerun()
    
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h1 style="font-size: 2.5rem; font-weight: 800; 
                   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;">
            🔍 System Audit Logs
        </h1>
        <p style="color: #718096; font-size: 1.1rem; margin-top: 0.5rem;">
            Complete system activity monitoring and security analytics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Modern tabs
    tab1, tab2, tab3 = st.tabs([
        "📋 Activity Monitor",
        "📊 Analytics Dashboard", 
        "📥 Export & Reports"
    ])
    
    with tab1:
        render_audit_viewer_tab()
    
    with tab2:
        render_audit_analytics_tab()
    
    with tab3:
        render_audit_export_tab()

def render_audit_analytics_tab():
    """Render modern audit analytics dashboard"""
    from services.audit_service import get_audit_statistics, load_audit_logs
    from components.charts import render_pie_chart, render_bar_chart
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="font-weight: 700;">📊 Analytics Dashboard</h2>
        <p style="color: #718096;">Real-time insights and activity trends</p>
    </div>
    """, unsafe_allow_html=True)
    
    logs = load_audit_logs()
    
    if logs:
        stats = get_audit_statistics(logs)
        
        # Modern Metrics Grid
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            ("Total Activities", stats.get('total', 0), "📊", "#667eea"),
            ("Unique Users", len(stats.get('by_user', {})), "👥", "#f093fb"),
            ("Action Types", len(stats.get('by_action', {})), "⚡", "#4facfe"),
            ("Active Modules", len(stats.get('by_module', {})), "📦", "#43e97b")
        ]
        
        for col, (label, value, emoji, color) in zip([col1, col2, col3, col4], metrics):
            with col:
                st.markdown(f"""
                <div class="metric-card-main">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{emoji}</div>
                    <div class="metric-value-main">{value}</div>
                    <div class="metric-label-main">{label}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Charts Section
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Action Distribution")
            if stats.get('by_action'):
                render_pie_chart(stats['by_action'], "Action Types")
        
        with col2:
            st.markdown("#### 📦 Module Activity")
            if stats.get('by_module'):
                render_pie_chart(stats['by_module'], "Modules")
        
        st.markdown("---")
        
        # User Activity Bar Chart
        st.markdown("#### 👥 User Activity Breakdown")
        if stats.get('by_user'):
            render_bar_chart(stats['by_user'], "Activity by User")
        
        st.markdown("---")
        
        # Daily Activity Timeline
        st.markdown("#### 📅 Daily Activity Timeline")
        if stats.get('by_date'):
            render_bar_chart(stats['by_date'], "Activity by Date")
    else:
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 5rem; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #718096;">No Analytics Data Available</h3>
            <p style="color: #a0aec0;">Activity data will appear here as you use the system</p>
        </div>
        """, unsafe_allow_html=True)

def render_audit_export_tab():
    """Render modern export interface"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="font-weight: 700;">📥 Export & Reports</h2>
        <p style="color: #718096;">Download audit logs in your preferred format</p>
    </div>
    """, unsafe_allow_html=True)
    
    from services.audit_service import load_audit_logs
    from utils.excel_handler import convert_to_excel
    
    logs = load_audit_logs()
    
    if logs:
        # Stats
        st.markdown(f"""
        <div class="info-box" style="text-align: center;">
            <span style="font-size: 2rem; font-weight: 700;">{len(logs)}</span>
            <div style="color: #006064; margin-top: 0.5rem;">Total logs available for export</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Export Cards
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown("""
            <div class="download-card">
                <div class="download-icon">📊</div>
                <h3 style="margin-bottom: 0.5rem; color: #1a202c;">Excel Format</h3>
                <p style="color: #718096; font-size: 0.9rem;">
                    Download as spreadsheet for analysis
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            excel_data = convert_to_excel(logs, "Audit Logs")
            if excel_data:
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary"
                )
        
        with col2:
            st.markdown("""
            <div class="download-card">
                <div class="download-icon">💾</div>
                <h3 style="margin-bottom: 0.5rem; color: #1a202c;">JSON Format</h3>
                <p style="color: #718096; font-size: 0.9rem;">
                    Raw data for system integration
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            import json
            json_data = json.dumps(logs, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
                type="primary"
            )
    else:
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 5rem; margin-bottom: 1rem;">📭</div>
            <h3 style="color: #718096;">No Logs to Export</h3>
            <p style="color: #a0aec0;">Activity logs will be available for export once generated</p>
        </div>
        """, unsafe_allow_html=True)