"""
Quality Module Main Router
Routes to different quality module pages based on user selection
"""
import streamlit as st
from pages.quality import quality_view, quality_dashboard

def render():
    """Main quality module router"""
    
    st.title("🎯 Trial Quality Matrix")
    
    # Check authentication
    is_authenticated = (
        st.session_state.get('username') is not None and 
        st.session_state.get('username') != ''
    )
    
    if not is_authenticated:
        st.warning("⚠️ Please login to access this page")
        return
    
    # Get user role
    role = st.session_state.get('role', 'user')
    
    # Initialize page state if not exists
    if 'quality_page' not in st.session_state:
        st.session_state.quality_page = 'dashboard'
    
    # ═══════════════════════════════════════════════════════════
    # WIZARD FLOW - Handle page navigation
    # ═══════════════════════════════════════════════════════════
    
    # If user is in wizard flow, render the appropriate page
    if st.session_state.quality_page in ['trial_setup', 'record_entry']:
        # Import wizard pages dynamically to avoid circular imports
        from pages.quality import quality_trial_setup, quality_record_entry
        
        # Show progress indicator
        display_wizard_breadcrumb()
        
        if st.session_state.quality_page == 'trial_setup':
            quality_trial_setup.render()
            return
        elif st.session_state.quality_page == 'record_entry':
            quality_record_entry.render()
            return
    
    # ═══════════════════════════════════════════════════════════
    # NORMAL TAB NAVIGATION (Dashboard/View)
    # ═══════════════════════════════════════════════════════════
    
    # Navigation tabs based on role
    if role == 'manager':
        # Manager only has Dashboard and View Records (no Create)
        tabs = st.tabs(["📊 Dashboard", "📋 View Records"])
        
        with tabs[0]:
            st.session_state.quality_page = 'dashboard'
            quality_dashboard.render()
        
        with tabs[1]:
            st.session_state.quality_page = 'view'
            quality_view.render()
    
    else:  # user, admin, superuser
        tabs = st.tabs(["📝 Create Record", "📋 View My Records"])
        
        with tabs[0]:
            st.session_state.quality_page = 'create'
            # Show button to start wizard
            render_create_landing()
        
        with tabs[1]:
            st.session_state.quality_page = 'view'
            quality_view.render()


def render_create_landing():
    """Landing page for Create - shows button to start wizard"""
    
    st.subheader("📝 Create Trial Quality Records")
    
    st.info("""
    ### 📋 Two-Step Process
    
    **Step 1: Trial Setup**
    - Enter Trial ID, Phase, UAT Plans, and Rounds (once per trial)
    
    **Step 2: Record Entry**
    - Add multiple quality records with shared trial information
    - All records will be associated with the same trial
    """)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button(
            "🚀 Start Creating Records",
            use_container_width=True,
            type="primary",
            help="Begin the two-step wizard to create quality records"
        ):
            # Clear any previous wizard state
            if 'wizard_trial_data' in st.session_state:
                del st.session_state.wizard_trial_data
            if 'wizard_records' in st.session_state:
                del st.session_state.wizard_records
            
            # Navigate to trial setup
            st.session_state.quality_page = 'trial_setup'
            st.rerun()
    
    st.markdown("---")
    
    # Show recent records for reference
    st.markdown("### 📊 Your Recent Records")
    
    from services.quality_service import QualityService
    quality_service = QualityService()
    
    user_records = quality_service.get_records_by_user(st.session_state.username)
    
    if user_records:
        # Show last 5 records
        recent_records = sorted(
            user_records,
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )[:5]
        
        for record in recent_records:
            with st.expander(
                f"🔹 {record.get('trial_id', 'Unknown')} - "
                f"{record.get('type_of_requirement', 'Unknown')} - "
                f"Round {record.get('current_round', 'N/A')}"
            ):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Phase", record.get('phase', 'N/A'))
                col2.metric("Requirements", record.get('total_requirements', 0))
                col3.metric("Failures", record.get('total_failures', 0))
                col4.metric("Defect Density", f"{record.get('defect_density', 0):.2f}%")
    else:
        st.info("📭 No records found. Start creating your first record!")


def display_wizard_breadcrumb():
    """Display wizard navigation breadcrumb"""
    
    current_page = st.session_state.quality_page
    
    # Breadcrumb
    if current_page == 'trial_setup':
        st.markdown("### 📍 Step 1 of 2: Trial Setup")
    elif current_page == 'record_entry':
        st.markdown("### 📍 Step 2 of 2: Record Entry")
    
    # Progress bar
    progress = 0.5 if current_page == 'trial_setup' else 1.0
    st.progress(progress)
    
    st.markdown("---")