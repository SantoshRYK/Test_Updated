# pages/uat/uat_edit.py
"""
UAT record editing
PLACEHOLDER for future implementation
"""
import streamlit as st
from services.uat_service import update_uat_record_service, get_uat_record

def render_uat_edit_form(uat_id: str):
    """
    Render UAT edit form
    TODO: Implement edit functionality
    """
    st.subheader("✏️ Edit UAT Record")
    st.info("Edit functionality will be implemented here")
    
    # Get existing record
    from utils.database import load_allocations
    all_data = load_allocations()
    record = None
    for item in all_data:
        if item.get('id') == uat_id and item.get('record_type') == 'uat':
            record = item
            break
    
    if record:
        st.write("**Editing:**", record.get('trial_id'))
        
        # TODO: Add edit form with pre-filled values
        # Similar to uat_create.py but with existing values
        
        if st.button("💾 Save Changes", key=f"save_edit_{uat_id}"):
            st.info("Save functionality coming soon")
        
        if st.button("❌ Cancel", key=f"cancel_edit_{uat_id}"):
            st.session_state[f"edit_uat_{uat_id}"] = False
            st.rerun()
    else:
        st.error("UAT record not found")