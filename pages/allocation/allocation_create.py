# pages/allocation/allocation_create.py
"""
Allocation creation form
"""
import streamlit as st
from datetime import datetime
from services.allocation_service import create_allocation_record
from components.forms import render_category_input
from config import SYSTEMS, THERAPEUTIC_AREAS, ROLES_ALLOCATION

def render_allocation_create_tab():
    """Render allocation creation form"""
    st.subheader("Create New Allocation")
    
    # Initialize session state
    if 'trial_category_type' not in st.session_state:
        st.session_state.trial_category_type = "Build"
    
    col1, col2 = st.columns(2)
    
    with col1:
        test_engineer_name = st.text_input(
            "**Test Engineer***",
            value=st.session_state.username,
            placeholder="Enter test engineer name",
            key="te_name"
        )
        
        trial_id = st.text_input(
            "**Trial ID***",
            placeholder="e.g., TRL-2024-001, TRIAL-ABC-123...",
            help="Enter the unique trial identifier",
            key="trial_id_input"
        )
        
        system = st.selectbox(
            "**System***",
            SYSTEMS,
            help="Select the system for this allocation",
            key="system_select"
        )
        
        # TRIAL CATEGORY using reusable component
        st.markdown("#### Trial Category")
        category_type, category_detail, final_trial_category = render_category_input("alloc_category")
        st.session_state.trial_category_type = category_type
        
        # THERAPEUTIC AREA
        therapeutic_area_type = st.selectbox(
            "**Therapeutic Area***",
            THERAPEUTIC_AREAS,
            help="Select the therapeutic area for this trial",
            key="therapeutic_area_select"
        )
        
        # Conditional text input for Others
        therapeutic_area_other = ""
        if therapeutic_area_type == "Others":
            therapeutic_area_other = st.text_input(
                "Please specify Therapeutic Area*",
                placeholder="Enter therapeutic area details...",
                key="therapeutic_other"
            )
    
    with col2:
        role = st.selectbox(
            "**Role***",
            ROLES_ALLOCATION,
            help="Select the role for this allocation",
            key="role_select"
        )
        
        activity = st.text_area(
            "Activity* (Max 200 characters)",
            placeholder="Enter activity/task description",
            max_chars=200,
            height=100,
            help="Describe the activity (up to 200 characters)",
            key="activity_text"
        )
        
        start_date = st.date_input("Start Date*", key="start_date_input")
        end_date = st.date_input("End Date*", key="end_date_input")
    
    # Submit button
    if st.button("Submit Allocation", type="primary", use_container_width=True, key="submit_allocation"):
        # Validation
        if not test_engineer_name or not test_engineer_name.strip():
            st.error("❌ Test Engineer name is required")
            return
        
        if not trial_id or not trial_id.strip():
            st.error("❌ Trial ID is required")
            return
        
        if not activity or not activity.strip():
            st.error("❌ Activity is required")
            return
        
        if not start_date:
            st.error("❌ Start Date is required")
            return
        
        if not end_date:
            st.error("❌ End Date is required")
            return

        # Date validation
        if end_date < start_date:
            st.error("❌ End date must be after start date")
            return
        
        # Construct full therapeutic area
        if therapeutic_area_type == "Others":
            if therapeutic_area_other:
                final_therapeutic_area = f"Others - {therapeutic_area_other.strip()}"
            else:
                st.error("❌ Please specify the therapeutic area for 'Others'")
                return
        else:
            final_therapeutic_area = therapeutic_area_type
        
        # Prepare allocation data
        allocation_data = {
            "test_engineer_name": test_engineer_name.strip(),
            "trial_id": trial_id.strip(),
            "system": system,
            "trial_category": final_trial_category,
            "trial_category_type": category_type,
            "therapeutic_area": final_therapeutic_area,
            "therapeutic_area_type": therapeutic_area_type,
            "role": role,
            "activity": activity.strip(),
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        # Get current username from session
        username = st.session_state.get('username', 'Unknown')
        
        # Create allocation using service with username parameter
        success, message = create_allocation_record(allocation_data, username)
        
        if success:
            st.success(f"✅ {message}")
           # st.balloons()
            st.balloons()
            # Wait a moment then rerun
            import time
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"❌ {message}")