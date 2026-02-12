"""
Quality Records View
Display all quality records in a table with Update/Delete options
"""
import streamlit as st
import pandas as pd
from services.quality_service import QualityService

def render_update_modal(record: dict, quality_service: QualityService):
    """Render update form in modal"""
    
    st.subheader(f"✏️ Update Record: {record['record_id']}")
    
    with st.form(f"update_form_{record['record_id']}"):
        col1, col2 = st.columns(2)
        
        with col1:
            trial_id = st.text_input("Trial ID", value=record['trial_id'])
            
            # Phase with dropdown
            phase_options = ["Phase 1 & NIS", "Phase 2", "Phase 3", "Other"]
            current_phase = record['phase']
            if current_phase not in phase_options:
                phase_selection = "Other"
                phase_other = current_phase
            else:
                phase_selection = current_phase
                phase_other = ""
            
            phase_sel = st.selectbox("Phase", phase_options, index=phase_options.index(phase_selection))
            if phase_sel == "Other":
                phase = st.text_input("Specify Phase", value=phase_other, key=f"phase_update_{record['record_id']}")
            else:
                phase = phase_sel
            
            no_of_uat_plans = st.text_input("No. of UAT Plans", value=str(record['no_of_uat_plans']))
            no_of_rounds = st.text_input("No. of Rounds", value=str(record['no_of_rounds']))
            type_of_requirement = st.selectbox(
                "Type of Requirement",
                ["Forms", "Editchecks"],
                index=["Forms", "Editchecks"].index(record['type_of_requirement'])
            )
        
        with col2:
            current_round = st.text_input("Round", value=str(record['current_round']))
            total_requirements = st.text_input("Total Requirements", value=str(record['total_requirements']))
            total_failures = st.text_input("Total Failures", value=str(record['total_failures']))
            
            # Calculate defect density
            try:
                req = int(total_requirements)
                fail = int(total_failures)
                if req > 0:
                    dd = (fail / req) * 100
                    st.metric("Defect Density", f"{dd:.2f}%")
                else:
                    st.metric("Defect Density", "0.00%")
            except:
                st.metric("Defect Density", "0.00%")
        
        st.markdown("### Failure Reasons")
        col3, col4, col5, col6 = st.columns(4)
        
        with col3:
            spec_issue = st.text_input("Spec Issue", value=str(record['spec_issue']))
        with col4:
            mock_crf_issue = st.text_input("Mock CRF Issue", value=str(record['mock_crf_issue']))
        with col5:
            programming_issue = st.text_input("Programming Issue", value=str(record['programming_issue']))
        with col6:
            scripting_issue = st.text_input("Scripting Issue", value=str(record['scripting_issue']))
        
        st.markdown("### Additional Information")
        col7, col8, col9 = st.columns(3)
        
        with col7:
            documentation_issues = st.text_input("Documentation Issues", value=record.get('documentation_issues', ''))
        with col8:
            timeline_adherence = st.text_input("Timeline Adherence", value=record.get('timeline_adherence', ''))
        with col9:
            system_deployment_delays = st.text_input("System Deployment Delays", value=record.get('system_deployment_delays', ''))
        
        submitted = st.form_submit_button("💾 Update Record", type="primary", use_container_width=True)
        
        if submitted:
            try:
                updates = {
                    'trial_id': trial_id.strip(),
                    'phase': phase.strip(),
                    'no_of_uat_plans': no_of_uat_plans.strip(),
                    'no_of_rounds': int(no_of_rounds),
                    'type_of_requirement': type_of_requirement,
                    'current_round': int(current_round),
                    'total_requirements': int(total_requirements),
                    'total_failures': int(total_failures),
                    'spec_issue': int(spec_issue) if spec_issue else 0,
                    'mock_crf_issue': int(mock_crf_issue) if mock_crf_issue else 0,
                    'programming_issue': int(programming_issue) if programming_issue else 0,
                    'scripting_issue': int(scripting_issue) if scripting_issue else 0,
                    'documentation_issues': documentation_issues.strip(),
                    'timeline_adherence': timeline_adherence.strip(),
                    'system_deployment_delays': system_deployment_delays.strip()
                }
                
                success, message = quality_service.update_record(
                    record['record_id'],
                    updates,
                    st.session_state.username
                )
                
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

def render_records_table(records: list, role: str, quality_service: QualityService):
    """Render records table with action buttons"""
    
    if not records:
        st.info("📭 No quality records found.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Select and order columns
    columns_order = [
        'record_id', 'trial_id', 'phase', 'type_of_requirement',
        'current_round', 'no_of_rounds', 'total_requirements', 
        'total_failures', 'defect_density', 'status', 'created_by', 'created_at'
    ]
    
    # Filter columns that exist
    columns_order = [col for col in columns_order if col in df.columns]
    df = df[columns_order]
    
    # Rename columns for display
    df = df.rename(columns={
        'record_id': 'Record ID',
        'trial_id': 'Trial ID',
        'phase': 'Phase',
        'type_of_requirement': 'Type',
        'current_round': 'Round',
        'no_of_rounds': 'Total Rounds',
        'total_requirements': 'Requirements',
        'total_failures': 'Failures',
        'defect_density': 'Defect Density %',
        'status': 'Status',
        'created_by': 'Created By',
        'created_at': 'Created At'
    })
    
    # Format datetime
    if 'Created At' in df.columns:
        df['Created At'] = pd.to_datetime(df['Created At']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # ✅ NEW: Action buttons for User role
    if role == 'user':
        st.markdown("---")
        st.markdown("### 🔧 Actions")
        
        # Select record to edit/delete
        record_ids = [r['record_id'] for r in records]
        selected_record_id = st.selectbox("Select Record for Action", record_ids, key="action_select")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("✏️ Update", use_container_width=True, type="primary"):
                st.session_state.editing_record = selected_record_id
                st.rerun()
        
        with col2:
            if st.button("🗑️ Delete", use_container_width=True, type="secondary"):
                st.session_state.deleting_record = selected_record_id
        
        # Show update form if editing
        if st.session_state.get('editing_record'):
            record = quality_service.get_record_by_id(st.session_state.editing_record)
            if record:
                st.markdown("---")
                render_update_modal(record, quality_service)
                
                if st.button("❌ Cancel Update", key="cancel_update"):
                    st.session_state.editing_record = None
                    st.rerun()
        
        # Show delete confirmation
        if st.session_state.get('deleting_record'):
            st.markdown("---")
            st.warning(f"⚠️ Are you sure you want to delete record {st.session_state.deleting_record}?")
            col_del1, col_del2 = st.columns(2)
            
            with col_del1:
                if st.button("✅ Yes, Delete", use_container_width=True, type="primary", key="confirm_delete"):
                    success, message = quality_service.delete_record(
                        st.session_state.deleting_record,
                        st.session_state.username
                    )
                    if success:
                        st.success(f"✅ {message}")
                        st.session_state.deleting_record = None
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            
            with col_del2:
                if st.button("❌ Cancel", use_container_width=True, key="cancel_delete"):
                    st.session_state.deleting_record = None
                    st.rerun()
    
    # Export option
    st.markdown("---")
    if st.button("📥 Export to Excel"):
        from utils.excel_handler import export_to_excel
        excel_data = export_to_excel(df, "Quality_Records")
        st.download_button(
            label="⬇️ Download Excel File",
            data=excel_data,
            file_name=f"quality_records_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def render():
    """Main render function"""
    
    st.subheader("📊 View Quality Records")
    
    quality_service = QualityService()
    role = st.session_state.get('role', 'user')
    username = st.session_state.get('username', '')
    
    # Filters
    with st.expander("🔍 Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            trial_ids = quality_service.get_unique_values('trial_id')
            trial_id_filter = st.selectbox("Trial ID", ["All"] + trial_ids)
        
        with col2:
            phases = quality_service.get_unique_values('phase')
            phase_filter = st.selectbox("Phase", ["All"] + phases)
        
        with col3:
            types = quality_service.get_unique_values('type_of_requirement')
            type_filter = st.selectbox("Type", ["All"] + types)
    
    # Get records (user sees only their records)
    if role == 'user':
        records = quality_service.get_records_by_user(username)
    else:
        records = quality_service.get_all_records()
    
    # Apply filters
    if trial_id_filter != "All":
        records = [r for r in records if r['trial_id'] == trial_id_filter]
    if phase_filter != "All":
        records = [r for r in records if r['phase'] == phase_filter]
    if type_filter != "All":
        records = [r for r in records if r['type_of_requirement'] == type_filter]
    
    # Display records
    st.markdown(f"**Total Records: {len(records)}**")
    
    render_records_table(records, role, quality_service)