# app.py
"""
Main application entry point
Handles routing and page rendering
WITH GLOBAL STYLING - PROFESSIONAL LIGHT BACKGROUND
"""
import streamlit as st
from config import APP_TITLE, APP_ICON, PAGE_LAYOUT
from utils.auth import initialize_session_state, is_logged_in, get_current_role
from utils.database import initialize_all_files
from components.sidebar import render_sidebar
from services.audit_service import log_page_view

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=PAGE_LAYOUT
)

# ============================================
# GLOBAL STYLING - APPLIED TO ALL PAGES
# PROFESSIONAL LIGHT BACKGROUND (MATCHING LOGIN PAGE)
# ============================================
def inject_global_styles():
    """Inject global CSS styles for entire application"""
    st.markdown("""
    <style>
    /* Import Modern Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* ========== PROFESSIONAL LIGHT BACKGROUND (SAME AS LOGIN) ========== */
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Main content area */
    .main {
        background-color: transparent;
    }
    
    /* Block container */
    .block-container {
        background-color: transparent;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* ========== SIDEBAR STYLING ========== */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        background-image: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: transparent;
    }
    
    /* ========== TYPOGRAPHY ========== */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        color: #1a202c;
        font-weight: 700;
        letter-spacing: -0.03em;
    }
    
    p, span, div, label {
        font-family: 'Inter', sans-serif;
        color: #2d3748;
    }
    
    /* ========== BUTTONS ========== */
    .stButton > button {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.3s;
        border: none;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* ========== CARDS & CONTAINERS ========== */
    .element-container {
        background-color: transparent;
    }
    
    /* White cards for content */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        background-color: rgba(255, 255, 255, 0.7);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Metric containers */
    [data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        color: #1a202c;
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #4a5568;
    }
    
    /* ========== INPUTS ========== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stDateInput > div > div > input {
        font-family: 'Inter', sans-serif;
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        background-color: #f8fafc;
        transition: all 0.3s;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        background-color: #ffffff;
    }
    
    /* Input labels */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #2d3748;
    }
    
    /* ========== DATAFRAMES ========== */
    .stDataFrame {
        font-family: 'Inter', sans-serif;
        border-radius: 12px;
        background-color: #ffffff;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    /* DataFrame headers */
    .stDataFrame thead tr th {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-weight: 600;
    }
    
    /* ========== EXPANDERS ========== */
    .streamlit-expanderHeader {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        background-color: #ffffff;
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #3b82f6;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
    }
    
    /* ========== TABS (MATCHING LOGIN PAGE) ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid #e9ecef;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        color: #4a5568;
        transition: all 0.3s;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    /* ========== INFO/WARNING/ERROR BOXES ========== */
    .stAlert {
        font-family: 'Inter', sans-serif;
        border-radius: 12px;
        border: none;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    /* Success alert */
    .stAlert[data-baseweb="notification"][kind="success"] {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
    }
    
    /* Warning alert */
    .stAlert[data-baseweb="notification"][kind="warning"] {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
    }
    
    /* Error alert */
    .stAlert[data-baseweb="notification"][kind="error"] {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
    }
    
    /* Info alert */
    .stAlert[data-baseweb="notification"][kind="info"] {
        background-color: #dbeafe;
        border-left: 4px solid #3b82f6;
    }
    
    /* ========== REMOVE DEFAULT ELEMENTS ========== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ========== CUSTOM SCROLLBAR ========== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #2563eb;
    }
    
    /* ========== LOADING SPINNER ========== */
    .stSpinner > div {
        border-top-color: #3b82f6 !important;
    }
    
    /* ========== FILE UPLOADER ========== */
    [data-testid="stFileUploader"] {
        background-color: #ffffff;
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #3b82f6;
        background-color: #f8fafc;
    }
    </style>
    """, unsafe_allow_html=True)


def route_to_page(page: str):
    """Route to appropriate page based on page name"""
    
    # Log page view for audit
    try:
        log_page_view(page)
    except:
        pass
    
    # Route to pages
    if page == "home":
        from ui.home import render_home_page
        render_home_page()
    
    elif page == "allocation":
        from pages.allocation.allocation_main import render_allocation_page
        render_allocation_page()
    
    elif page == "uat":
        from pages.uat.uat_main import render_uat_page
        render_uat_page()
    
    elif page == "audit":
        from pages.audit.audit_main import render_audit_page
        render_audit_page()
    
    elif page == "quality":
        from pages.quality.quality_main import render
        render()
    
    elif page == "change_request":
        from pages.change_request.tracker_main import render
        render()
    
    elif page == "all_allocations":
        role = get_current_role()
        if role == "manager":
            from pages.allocation.allocation_dashboard import render_manager_allocation_dashboard
            render_manager_allocation_dashboard()
        else:
            from pages.allocation.allocation_view import render_all_allocations_view
            render_all_allocations_view()
    
    elif page == "superuser":
        from pages.admin.superuser import render_superuser_dashboard
        render_superuser_dashboard()
    
    elif page == "manager":
        from pages.admin.manager import render_manager_page
        render_manager_page()
    
    elif page == "admin":
        from pages.admin.admin_user import render_admin_dashboard
        render_admin_dashboard()
    
    elif page == "email_settings":
        from pages.admin.email_settings import render_email_settings_page
        render_email_settings_page()
    
    else:
        from ui.home import render_home_page
        render_home_page()


def main():
    """Main application entry point"""
    try:
        # ========== APPLY GLOBAL STYLES FIRST ==========
        inject_global_styles()
        
        # ✅ Initialize session state
        initialize_session_state()
        initialize_all_files()
        
        # ✅ NEW: Check and create automatic backup if needed
        try:
            from utils.backup_manager import backup_manager
            if backup_manager.should_create_automatic_backup():
                print("🔄 Creating automatic weekly backup...")
                success, message = backup_manager.create_backup(
                    backup_type="automatic",
                    created_by="system"
                )
                if success:
                    print(message)
                else:
                    print(f"⚠️ Backup warning: {message}")
        except Exception as e:
            print(f"⚠️ Backup check failed: {e}")
            # Don't break the app if backup fails
            pass
        
        if is_logged_in():
            # Render sidebar navigation
            render_sidebar()
            
            # Get current page from session state
            current_page = st.session_state.get('current_page', 'home')
            
            # Route to appropriate page
            route_to_page(current_page)
        
        else:
            # Show login page
            from ui.login import render_login_page
            render_login_page()
    
    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
        
        # Show detailed error in expander for debugging
        with st.expander("🔍 Error Details (for debugging)"):
            import traceback
            st.code(traceback.format_exc())
        
        # Provide recovery options
        st.markdown("---")
        st.subheader("Recovery Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Page", use_container_width=True, key="error_refresh"):
                st.rerun()
        
        with col2:
            if st.button("🏠 Go to Home", use_container_width=True, key="error_home"):
                st.session_state.current_page = "home"
                st.rerun()
        
        with col3:
            if st.button("🚪 Logout", use_container_width=True, key="error_logout"):
                from utils.auth import logout_user
                logout_user()
                st.rerun()


if __name__ == "__main__":
    main()