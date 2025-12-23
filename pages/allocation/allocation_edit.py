# pages/allocation/allocation_edit.py
"""
Allocation editing functionality
Matches create form logic exactly - Build vs Change Request
"""
import streamlit as st
from datetime import datetime
from services.allocation_service import get_allocation_by_id, update_allocation_record
from utils.auth import get_current_user, get_current_role
from config import SYSTEMS, THERAPEUTIC_AREAS

def render_allocation_edit_form(allocation_id: str):
    """Render allocation edit form - matches create form exactly"""
    
    # Load the allocation
    allocation = get_allocation_by_id(allocation_id)
    
    if not allocation:
        st.error("❌ Allocation not found")
        return
    
    # Check permissions
    current_user = get_current_user()
    current_role_user = get_current_role()
    
    if current_user != allocation.get('created_by') and current_role_user not in ['admin', 'superuser']:
        st.error("❌ You don't have permission to edit this allocation")
        return
    
    st.subheader(f"✏️ Edit Allocation: {allocation.get('trial_id')}")
    st.info("📝 Modify the allocation details below and click Save Changes")
    
    # Show read-only info
    st.markdown("---")
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.markdown(f"**🎯 Role (Read-Only):** `{allocation.get('role', 'N/A')}`")
    with col_info2:
        st.markdown(f"**👤 Created By:** `{allocation.get('created_by', 'N/A')}`")
    with col_info3:
        st.markdown(f"**📅 Created:** `{allocation.get('created_at', 'N/A')[:16]}`")
    st.markdown("---")
    
    # Pre-extract current category info for initialization
    current_category_full = allocation.get('trial_category', 'Build')
    if 'Change Request' in current_category_full:
        initial_category_type = 'Change Request'
        initial_category_detail = current_category_full.replace('Change Request - ', '').strip()
    else:
        initial_category_type = 'Build'
        initial_category_detail = ''
    
    # Initialize session state for edit mode
    edit_cat_key = f'edit_trial_category_type_{allocation_id}'
    if edit_cat_key not in st.session_state:
        st.session_state[edit_cat_key] = initial_category_type
    
    with st.form(key=f"edit_allocation_form_{allocation_id}"):
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Test Engineer Name
            test_engineer_name = st.text_input(
                "Test Engineer*",
                value=allocation.get('test_engineer_name', ''),
                placeholder="Enter test engineer name",
                key=f"edit_te_{allocation_id}"
            )
            
            # Trial ID
            trial_id = st.text_input(
                "Trial ID*",
                value=allocation.get('trial_id', ''),
                placeholder="e.g., TRL-2024-001",
                help="Enter the unique trial identifier",
                key=f"edit_trial_{allocation_id}"
            )
            
            # System
            current_system = allocation.get('system', SYSTEMS[0])
            system_index = SYSTEMS.index(current_system) if current_system in SYSTEMS else 0
            
            system = st.selectbox(
                "System*",
                options=SYSTEMS,
                index=system_index,
                help="Select the system",
                key=f"edit_sys_{allocation_id}"
            )
            
            # ========== TRIAL CATEGORY - SAME LOGIC AS CREATE ==========
            st.markdown("#### Trial Category")
            
            category_type = st.selectbox(
                "Category Type*",
                ["Build", "Change Request"],
                index=0 if initial_category_type == "Build" else 1,
                help="Select the category type",
                key=f"edit_cat_type_{allocation_id}"
            )
            
            # Update session state
            st.session_state[edit_cat_key] = category_type
            
            # Conditional input for Change Request ONLY
            category_detail = ""
            if category_type == "Change Request":
                category_detail = st.text_input(
                    "Change Request Details*",
                    value=initial_category_detail if initial_category_type == "Change Request" else "",
                    placeholder="e.g., CR01, CR02, 01, 02...",
                    help="Enter the change request number or details",
                    key=f"edit_cat_detail_{allocation_id}"
                )
            
            # Construct final category (SAME AS CREATE FORM)
            if category_type == "Build":
                final_trial_category = "Build"
            else:
                if category_detail and category_detail.strip():
                    final_trial_category = f"Change Request - {category_detail.strip()}"
                else:
                    final_trial_category = ""
            
            # ========== THERAPEUTIC AREA ==========
            current_area = allocation.get('therapeutic_area', THERAPEUTIC_AREAS[0])
            
            # Check if Others with details
            if 'Others -' in current_area:
                current_area_type = 'Others'
                current_area_other = current_area.replace('Others - ', '').strip()
            else:
                current_area_type = current_area
                current_area_other = ''
            
            area_index = THERAPEUTIC_AREAS.index(current_area_type) if current_area_type in THERAPEUTIC_AREAS else 0
            
            therapeutic_area_type = st.selectbox(
                "Therapeutic Area*",
                options=THERAPEUTIC_AREAS,
                index=area_index,
                help="Select the therapeutic area",
                key=f"edit_thera_{allocation_id}"
            )
            
            # Conditional input for Others
            therapeutic_area_other = ""
            if therapeutic_area_type == "Others":
                therapeutic_area_other = st.text_input(
                    "Please specify Therapeutic Area*",
                    value=current_area_other,
                    placeholder="Enter therapeutic area details...",
                    key=f"edit_thera_other_{allocation_id}"
                )
        
        with col2:
            # Activity
            activity = st.text_area(
                "Activity* (Max 200 characters)",
                value=allocation.get('activity', ''),
                placeholder="Enter activity/task description",
                max_chars=200,
                height=100,
                help="Describe the activity (up to 200 characters)",
                key=f"edit_act_{allocation_id}"
            )
            
            # Dates
            try:
                start_date_value = datetime.strptime(allocation.get('start_date', '2024-01-01'), '%Y-%m-%d').date()
            except:
                start_date_value = datetime.now().date()
            
            start_date = st.date_input(
                "Start Date*",
                value=start_date_value,
                key=f"edit_start_{allocation_id}"
            )
            
            try:
                end_date_value = datetime.strptime(allocation.get('end_date', '2024-12-31'), '%Y-%m-%d').date()
            except:
                end_date_value = datetime.now().date()
            
            end_date = st.date_input(
                "End Date*",
                value=end_date_value,
                key=f"edit_end_{allocation_id}"
            )
        
        st.markdown("---")
        
        # Form buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            submit_button = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
        
        with col2:
            cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        # Handle submission
        if submit_button:
            # Validation
            if not trial_id or not trial_id.strip():
                st.error("❌ Trial ID is required")
                return
            
            if not test_engineer_name or not test_engineer_name.strip():
                st.error("❌ Test Engineer name is required")
                return
            
            if not activity or not activity.strip():
                st.error("❌ Activity is required")
                return
            
            # Validate category
            if category_type == "Change Request":
                if not category_detail or not category_detail.strip():
                    st.error("❌ Please enter Change Request details!")
                    return
            
            if not final_trial_category:
                st.error("❌ Please complete trial category!")
                return
            
            # Date validation
            if end_date < start_date:
                st.error("❌ End date must be after start date")
                return
            
            # Handle therapeutic area
            if therapeutic_area_type == "Others":
                if not therapeutic_area_other or not therapeutic_area_other.strip():
                    st.error("❌ Please specify the therapeutic area")
                    return
                final_therapeutic_area = f"Others - {therapeutic_area_other.strip()}"
            else:
                final_therapeutic_area = therapeutic_area_type
            
            # Prepare updated data
            updated_data = {
                'trial_id': trial_id.strip(),
                'test_engineer_name': test_engineer_name.strip(),
                'system': system,
                'trial_category': final_trial_category,
                'trial_category_type': category_type,
                'therapeutic_area': final_therapeutic_area,
                'therapeutic_area_type': therapeutic_area_type,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'activity': activity.strip()
            }
            
            # Update
            success, message = update_allocation_record(allocation_id, updated_data)
            
            if success:
                st.success(f"✅ {message}")
                st.balloons()
                
                # Clear session state
                if 'edit_allocation_id' in st.session_state:
                    del st.session_state['edit_allocation_id']
                if 'edit_allocation_id_admin' in st.session_state:
                    del st.session_state['edit_allocation_id_admin']
                if edit_cat_key in st.session_state:
                    del st.session_state[edit_cat_key]
                
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ {message}")
        
        if cancel_button:
            # Clear edit mode
            if 'edit_allocation_id' in st.session_state:
                del st.session_state['edit_allocation_id']
            if 'edit_allocation_id_admin' in st.session_state:
                del st.session_state['edit_allocation_id_admin']
            if edit_cat_key in st.session_state:
                del st.session_state[edit_cat_key]
            st.rerun()