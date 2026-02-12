"""
Trial Quality Matrix - Step 2: Record Entry
User can add multiple records with shared trial data
"""
import streamlit as st
from services.quality_service import QualityService
from datetime import datetime

def render_record_entry():
    """Render record entry form (Page 2 of wizard)"""
    
    # Check if trial data exists
    if 'wizard_trial_data' not in st.session_state:
        st.error("❌ No trial data found. Please start from Trial Setup.")
        if st.button("← Go to Trial Setup"):
            st.session_state.quality_page = 'trial_setup'
            st.rerun()
        return
    
    trial_data = st.session_state.wizard_trial_data
    
    # Initialize records list if not exists
    if 'wizard_records' not in st.session_state:
        st.session_state.wizard_records = []
    
    st.title("📝 Trial Quality Matrix - Record Entry")
    st.markdown("### Step 2: Add Quality Records")
    
    # Display trial information
    with st.expander("📋 Trial Information (from Step 1)", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Trial ID", trial_data['trial_id'])
        col2.metric("Phase", trial_data['phase'])
        col3.metric("UAT Plans", trial_data['no_of_uat_plans'])
        col4.metric("Rounds", trial_data['no_of_rounds'])
    
    st.markdown("---")
    
    # Record entry form
    st.markdown("### 📊 Add New Record")
    
    with st.form("record_entry_form", clear_on_submit=True):
        
        # Row 1: Type, Round, Requirements, Failures
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            type_of_requirement = st.selectbox(
                "Type of Requirement *",
                ["Forms", "Editchecks"]
            )
        
        with col2:
            current_round = st.number_input(
                "Round *",
                min_value=1,
                max_value=trial_data['no_of_rounds'],
                value=1,
                step=1
            )
        
        with col3:
            total_requirements = st.number_input(
                "Total Requirements *",
                min_value=0,
                value=0,
                step=1
            )
        
        with col4:
            total_failures = st.number_input(
                "Total Failures *",
                min_value=0,
                value=0,
                step=1
            )
        
        # Defect Density Display
        if total_requirements > 0:
            defect_density = (total_failures / total_requirements) * 100
            st.info(f"📊 **Defect Density:** {defect_density:.2f}%")
        
        st.markdown("---")
        
        # Row 2: Failure Reasons
        st.markdown("#### Reason for Failure")
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            spec_issue = st.number_input("Spec Issue", min_value=0, value=0, step=1)
        
        with col6:
            mock_crf_issue = st.number_input("Mock CRF Issue", min_value=0, value=0, step=1)
        
        with col7:
            programming_issue = st.number_input("Programming Issue", min_value=0, value=0, step=1)
        
        with col8:
            scripting_issue = st.number_input("Scripting Issue", min_value=0, value=0, step=1)
        
        st.markdown("---")
        
        # Row 3: Additional Information
        st.markdown("#### Additional Information")
        col9, col10, col11 = st.columns(3)
        
        with col9:
            documentation_issues = st.text_area(
                "Documentation Issues",
                placeholder="Describe any documentation issues...",
                height=100
            )
        
        with col10:
            timeline_adherence = st.text_input(
                "Timeline Adherence",
                placeholder="e.g., On Time, Delayed"
            )
        
        with col11:
            system_deployment_delays = st.text_input(
                "System Deployment Delays",
                placeholder="e.g., 2 days"
            )
        
        st.markdown("---")
        
        # Add Record Button
        col_add1, col_add2, col_add3 = st.columns([2, 1, 2])
        with col_add2:
            add_record = st.form_submit_button(
                "➕ Add Record",
                use_container_width=True,
                type="secondary"
            )
        
        if add_record:
            # Validation
            errors = []
            
            if total_requirements <= 0:
                errors.append("Total Requirements must be greater than 0")
            
            if total_failures > total_requirements:
                errors.append("Total Failures cannot exceed Total Requirements")
            
            failure_sum = spec_issue + mock_crf_issue + programming_issue + scripting_issue
            if failure_sum > total_failures:
                errors.append(f"Sum of failure reasons ({failure_sum}) cannot exceed total failures ({total_failures})")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Add record to session state
                record = {
                    'type_of_requirement': type_of_requirement,
                    'current_round': current_round,
                    'total_requirements': total_requirements,
                    'total_failures': total_failures,
                    'spec_issue': spec_issue,
                    'mock_crf_issue': mock_crf_issue,
                    'programming_issue': programming_issue,
                    'scripting_issue': scripting_issue,
                    'documentation_issues': documentation_issues.strip(),
                    'timeline_adherence': timeline_adherence.strip(),
                    'system_deployment_delays': system_deployment_delays.strip()
                }
                
                st.session_state.wizard_records.append(record)
                st.success(f"✅ Record added! Total records: {len(st.session_state.wizard_records)}")
                st.rerun()
    
    st.markdown("---")
    
    # Display added records
    if st.session_state.wizard_records:
        st.markdown("### 📋 Records to be Saved")
        st.info(f"**{len(st.session_state.wizard_records)} record(s)** ready to save")
        
        # Show records in a table
        for idx, record in enumerate(st.session_state.wizard_records, 1):
            with st.expander(f"Record {idx}: {record['type_of_requirement']} - Round {record['current_round']}"):
                col1, col2, col3 = st.columns(3)
                col1.write(f"**Requirements:** {record['total_requirements']}")
                col2.write(f"**Failures:** {record['total_failures']}")
                
                defect_density = (record['total_failures'] / record['total_requirements'] * 100) if record['total_requirements'] > 0 else 0
                col3.write(f"**Defect Density:** {defect_density:.2f}%")
                
                if st.button(f"🗑️ Remove", key=f"remove_{idx}"):
                    st.session_state.wizard_records.pop(idx - 1)
                    st.rerun()
    
    st.markdown("---")
    
    # Navigation buttons
    col_back, col_space, col_save = st.columns([1, 1, 1])
    
    with col_back:
        if st.button("◀️ Back to Trial Setup", use_container_width=True):
            st.session_state.quality_page = 'trial_setup'
            st.rerun()
    
    with col_save:
        if st.button(
            f"💾 Save All Records ({len(st.session_state.wizard_records)})",
            use_container_width=True,
            type="primary",
            disabled=len(st.session_state.wizard_records) == 0
        ):
            save_all_records()

def save_all_records():
    """Save all records to database"""
    quality_service = QualityService()
    trial_data = st.session_state.wizard_trial_data
    records = st.session_state.wizard_records
    username = st.session_state.username
    
    success_count = 0
    error_count = 0
    error_messages = []
    
    with st.spinner(f"Saving {len(records)} records..."):
        for record in records:
            # Merge trial data with record data
            full_record = {
                **trial_data,
                **record
            }
            
            success, message, _ = quality_service.create_record(full_record, username)
            
            if success:
                success_count += 1
            else:
                error_count += 1
                error_messages.append(message)
    
    # Show results
    if success_count > 0:
        st.success(f"✅ Successfully saved {success_count} record(s)!")
        st.balloons()
    
    if error_count > 0:
        st.error(f"❌ Failed to save {error_count} record(s)")
        for msg in error_messages:
            st.error(msg)
    
    if success_count > 0:
        # Clear wizard state
        del st.session_state.wizard_trial_data
        del st.session_state.wizard_records
        
        # Navigate to dashboard
        import time
        time.sleep(2)
        st.session_state.quality_page = 'dashboard'
        st.rerun()

def render():
    """Main render function"""
    render_record_entry()