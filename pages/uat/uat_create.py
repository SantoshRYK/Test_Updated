# pages/uat/uat_create.py
"""
UAT record creation form
EASY TO EXTEND - Add new fields here
"""
import streamlit as st
from datetime import datetime
from services.uat_service import create_uat_record
from components.forms import render_category_input, render_status_result_input
from config import UAT_STATUS_OPTIONS, UAT_RESULT_OPTIONS

def render_uat_create_tab():
    """Render UAT creation form"""
    st.subheader("Create New UAT Record")
    
    # Initialize session state for category
    if 'uat_category_type' not in st.session_state:
        st.session_state.uat_category_type = "Build"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Trial Information")
        
        trial_id = st.text_input(
            "Trial ID*",
            placeholder="e.g., TRL-2024-001",
            help="Enter the unique trial identifier",
            key="uat_trial_id"
        )
        
        # UAT ROUND - FREE TEXT
        uat_round = st.text_input(
            "UAT Round*",
            placeholder="e.g., Round 1, UAT-Phase1, Initial Testing...",
            help="Enter the UAT testing round/phase",
            key="uat_round_input"
        )
        
        # CATEGORY using reusable component
        st.markdown("#### Category")
        category_type, category_detail, final_category = render_category_input("uat_category")
        st.session_state.uat_category_type = category_type
        
        # PLANNED DATES
        st.markdown("#### Planned Dates")
        planned_start_date = st.date_input(
            "Planned Start Date*",
            help="When UAT is planned to start",
            key="uat_planned_start"
        )
        
        planned_end_date = st.date_input(
            "Planned End Date*",
            help="When UAT is planned to end",
            key="uat_planned_end"
        )
        
        # Validation for planned dates
        if planned_end_date < planned_start_date:
            st.warning("⚠️ Planned End Date should be after Planned Start Date")
    
    with col2:
        # ACTUAL DATES
        st.markdown("#### Actual Dates")
        st.caption("Leave empty if UAT not started/completed yet")
        
        actual_start_date = st.date_input(
            "Actual Start Date",
            value=None,
            help="When UAT actually started (leave empty if not started)",
            key="uat_actual_start"
        )
        
        actual_end_date = st.date_input(
            "Actual End Date",
            value=None,
            help="When UAT actually ended (leave empty if not completed)",
            key="uat_actual_end"
        )
        
        # Validation for actual dates
        if actual_start_date and actual_end_date and actual_end_date < actual_start_date:
            st.warning("⚠️ Actual End Date should be after Actual Start Date")
        
        # STATUS & RESULT using reusable component
        st.markdown("#### Status & Result")
        status, result = render_status_result_input("uat")
    
    # EMAIL BODY
    st.markdown("---")
    st.markdown("#### Email Body / Additional Information")
    email_body = st.text_area(
        "Email Body / Comments",
        placeholder="Enter email content, test summary, issues found, or any additional information...",
        height=200,
        help="This can be used for email notifications or detailed UAT summary",
        key="uat_email_body"
    )
    
    # SUBMIT BUTTON
    if st.button("💾 Save UAT Record", key="save_uat_btn", use_container_width=True, type="primary"):
        # Prepare UAT data
        uat_data = {
            "trial_id": trial_id.strip() if trial_id else "",
            "uat_round": uat_round.strip() if uat_round else "",
            "category": final_category,
            "category_type": category_type,
            "planned_start_date": planned_start_date.strftime("%Y-%m-%d"),
            "planned_end_date": planned_end_date.strftime("%Y-%m-%d"),
            "actual_start_date": actual_start_date.strftime("%Y-%m-%d") if actual_start_date else None,
            "actual_end_date": actual_end_date.strftime("%Y-%m-%d") if actual_end_date else None,
            "status": status,
            "result": result,
            "email_body": email_body.strip() if email_body else ""
        }
        
        # Create UAT record using service
        success, message = create_uat_record(uat_data)
        
        if success:
            st.success(f"✅ {message}")
            st.balloons()
            st.rerun()
        else:
            st.error(f"❌ {message}")