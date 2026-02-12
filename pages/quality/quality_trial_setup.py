"""
Trial Quality Matrix - Step 1: Trial Setup
User enters trial-level information once
"""
import streamlit as st
from datetime import datetime

def render_trial_setup():
    """Render trial setup form (Page 1 of wizard)"""
    
    st.title("📋 Trial Quality Matrix - Trial Setup")
    st.markdown("### Step 1: Enter Trial Information")
    st.info("ℹ️ These details will be applied to all records you create in the next step.")
    
    with st.form("trial_setup_form"):
        
        # Trial-level fields in a clean layout
        col1, col2 = st.columns(2)
        
        with col1:
            trial_id = st.text_input(
                "Trial ID *",
                placeholder="e.g., NN9499-8242",
                help="Unique trial identifier"
            )
            
            no_of_uat_plans = st.text_input(
                "No. of UAT Plans *",
                placeholder="e.g., 3",
                help="Total number of UAT plans for this trial"
            )
        
        with col2:
            # Phase dropdown with Other option
            phase_options = ["Phase 1 & NIS", "Phase 2", "Phase 3", "Other"]
            phase_selection = st.selectbox("Phase *", phase_options)
            
            # Show text input if "Other" is selected
            if phase_selection == "Other":
                phase_other = st.text_input(
                    "Specify Phase",
                    placeholder="Enter phase details",
                    key="phase_other"
                )
                phase = phase_other if phase_other else "Other"
            else:
                phase = phase_selection
            
            no_of_rounds = st.text_input(
                "No. of Rounds *",
                placeholder="e.g., 3",
                help="Total number of testing rounds planned"
            )
        
        st.markdown("---")
        
        # Navigation buttons
        col_back, col_space, col_next = st.columns([1, 2, 1])
        
        with col_back:
            if st.form_submit_button("◀️ Back to Dashboard", use_container_width=True):
                # Clear wizard state
                if 'wizard_trial_data' in st.session_state:
                    del st.session_state.wizard_trial_data
                if 'wizard_records' in st.session_state:
                    del st.session_state.wizard_records
                st.session_state.quality_page = 'dashboard'
                st.rerun()
        
        with col_next:
            submitted = st.form_submit_button(
                "Next: Record Details ▶️",
                use_container_width=True,
                type="primary"
            )
        
        if submitted:
            # Validation
            errors = []
            
            if not trial_id or not trial_id.strip():
                errors.append("Trial ID is required")
            
            if not phase or not phase.strip():
                errors.append("Phase is required")
            
            if not no_of_uat_plans or not no_of_uat_plans.strip():
                errors.append("No. of UAT Plans is required")
            
            if not no_of_rounds or not no_of_rounds.strip():
                errors.append("No. of Rounds is required")
            
            # Validate numeric fields
            if no_of_rounds:
                try:
                    rounds_int = int(no_of_rounds)
                    if rounds_int <= 0:
                        errors.append("No. of Rounds must be greater than 0")
                except ValueError:
                    errors.append("No. of Rounds must be a valid number")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
                return
            
            # Store trial-level data in session state
            st.session_state.wizard_trial_data = {
                'trial_id': trial_id.strip(),
                'phase': phase.strip(),
                'no_of_uat_plans': no_of_uat_plans.strip(),
                'no_of_rounds': int(no_of_rounds)
            }
            
            # Initialize records list
            if 'wizard_records' not in st.session_state:
                st.session_state.wizard_records = []
            
            # Navigate to record entry page
            st.session_state.quality_page = 'record_entry'
            st.success("✅ Trial information saved! Proceeding to record entry...")
            st.rerun()

def render():
    """Main render function"""
    render_trial_setup()