"""
Quality Record Creation Form
User can enter trial quality data with exact layout
"""
import streamlit as st
from services.quality_service import QualityService

def render_create_form():
    """Render quality record creation form with exact layout"""
    
    st.subheader("📝 Create Trial Quality Record")
    
    quality_service = QualityService()
    
    with st.form("quality_create_form"):
        
        # ROW 1: Trial ID | Phase | No. of UAT Plans | No. of Rounds | Type of Requirement
        st.markdown("### Basic Information")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            trial_id = st.text_input("Trial ID *", placeholder="e.g., TRIAL-001")
        
        with col2:
            # ✅ MODIFIED: Phase with dropdown + Other option
            phase_options = ["Phase 1 & NIS", "Phase 2", "Phase 3", "Other"]
            phase_selection = st.selectbox("Phase *", phase_options)
            
            # Show text input if "Other" is selected
            if phase_selection == "Other":
                phase_other = st.text_input("Specify Phase", placeholder="Enter phase details", key="phase_other")
                phase = phase_other if phase_other else "Other"
            else:
                phase = phase_selection
        
        with col3:
            # ✅ MODIFIED: Remove +/- buttons - plain text input for numbers
            no_of_uat_plans = st.text_input("No. of UAT Plans *", placeholder="e.g., 5")
        
        with col4:
            # ✅ MODIFIED: Remove +/- buttons - plain text input for numbers
            no_of_rounds = st.text_input("No. of Rounds *", placeholder="e.g., 3")
        
        with col5:
            type_of_requirement = st.selectbox(
                "Type of Requirement *",
                ["Forms", "Editchecks"]
            )
        
        st.markdown("---")
        
        # ✅ MODIFIED: ROW 2 - Round & UAT Metrics all in single horizontal line
        st.markdown("### Round & UAT Metrics")
        col6, col7, col8, col9 = st.columns(4)
        
        with col6:
            # ✅ MODIFIED: Changed "Current Round" to "Round"
            current_round = st.text_input("Round *", placeholder="1", key="current_round")
        
        with col7:
            total_requirements = st.text_input("Total Requirements *", placeholder="10", key="total_req")
        
        with col8:
            total_failures = st.text_input("Total Failures *", placeholder="0", key="total_fail")
        
        with col9:
            st.markdown("**Defect Density**")
            # Calculate defect density
            try:
                req = int(total_requirements) if total_requirements else 0
                fail = int(total_failures) if total_failures else 0
                if req > 0:
                    defect_density = (fail / req) * 100
                    st.metric("", f"{defect_density:.2f}%", help="(Total Failures / Total Requirements) × 100")
                else:
                    st.metric("", "0.00%")
            except:
                st.metric("", "0.00%")
        
        st.markdown("---")
        
        # ROW 3: Reason for Failure (4 fields)
        st.markdown("### Reason for Failure")
        col10, col11, col12, col13 = st.columns(4)
        
        with col10:
            spec_issue = st.text_input("Spec Issue", placeholder="0", key="spec_issue")
        
        with col11:
            mock_crf_issue = st.text_input("Mock CRF Issue", placeholder="0", key="mock_crf")
        
        with col12:
            programming_issue = st.text_input("Programming Issue", placeholder="0", key="prog_issue")
        
        with col13:
            scripting_issue = st.text_input("Scripting Issue", placeholder="0", key="script_issue")
        
        st.markdown("---")
        
        # ROW 4: Documentation Issues | Timeline Adherence | System Deployment Delays
        st.markdown("### Additional Information")
        col14, col15, col16 = st.columns(3)
        
        with col14:
            documentation_issues = st.text_input("Documentation Issues", placeholder="Describe issues...")
        
        with col15:
            timeline_adherence = st.text_input("Timeline Adherence", placeholder="e.g., On Time, Delayed")
        
        with col16:
            system_deployment_delays = st.text_input("System Deployment Delays", placeholder="e.g., 2 days")
        
        st.markdown("---")
        
        # Submit button
        col_submit1, col_submit2, col_submit3 = st.columns([2, 1, 2])
        with col_submit2:
            submitted = st.form_submit_button("✅ Create Record", use_container_width=True, type="primary")
        
        if submitted:
            # Validation
            if not trial_id:
                st.error("❌ Trial ID is required")
                return
            
            if not phase:
                st.error("❌ Phase is required")
                return
            
            if not no_of_uat_plans:
                st.error("❌ No. of UAT Plans is required")
                return
            
            if not no_of_rounds:
                st.error("❌ No. of Rounds is required")
                return
            
            if not current_round:
                st.error("❌ Round is required")
                return
            
            # Convert text inputs to numbers
            try:
                no_of_rounds_int = int(no_of_rounds)
                current_round_int = int(current_round)
                total_requirements_int = int(total_requirements) if total_requirements else 0
                total_failures_int = int(total_failures) if total_failures else 0
                spec_issue_int = int(spec_issue) if spec_issue else 0
                mock_crf_issue_int = int(mock_crf_issue) if mock_crf_issue else 0
                programming_issue_int = int(programming_issue) if programming_issue else 0
                scripting_issue_int = int(scripting_issue) if scripting_issue else 0
            except ValueError:
                st.error("❌ Please enter valid numbers for numeric fields")
                return
            
            # Additional validation
            failure_sum = spec_issue_int + mock_crf_issue_int + programming_issue_int + scripting_issue_int
            if failure_sum > total_failures_int:
                st.error(f"❌ Sum of failure reasons ({failure_sum}) cannot exceed total failures ({total_failures_int})")
                return
            
            if current_round_int > no_of_rounds_int:
                st.error(f"❌ Round ({current_round_int}) cannot exceed total rounds ({no_of_rounds_int})")
                return
            
            if total_requirements_int <= 0:
                st.error("❌ Total Requirements must be greater than 0")
                return
            
            # Prepare data
            record_data = {
                'trial_id': trial_id.strip(),
                'phase': phase.strip(),
                'no_of_uat_plans': no_of_uat_plans.strip(),
                'no_of_rounds': no_of_rounds_int,
                'type_of_requirement': type_of_requirement,
                'current_round': current_round_int,
                'total_requirements': total_requirements_int,
                'total_failures': total_failures_int,
                'spec_issue': spec_issue_int,
                'mock_crf_issue': mock_crf_issue_int,
                'programming_issue': programming_issue_int,
                'scripting_issue': scripting_issue_int,
                'documentation_issues': documentation_issues.strip(),
                'timeline_adherence': timeline_adherence.strip(),
                'system_deployment_delays': system_deployment_delays.strip()
            }
            
            # Create record
            success, message, record = quality_service.create_record(
                record_data, 
                st.session_state.username
            )
            
            if success:
                st.success(f"✅ {message}")
                st.balloons()
                # Wait a moment then rerun
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ {message}")

def render():
    """Main render function"""
    render_create_form()