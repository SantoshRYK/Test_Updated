"""
Utility functions for Quality Matrix Wizard
"""
import streamlit as st

def clear_wizard_state():
    """Clear all wizard-related session state"""
    keys_to_remove = ['wizard_trial_data', 'wizard_records']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

def get_wizard_progress():
    """
    Get current wizard progress
    
    Returns:
        tuple: (current_step, total_steps)
    """
    if 'quality_page' not in st.session_state:
        return (0, 2)
    
    page = st.session_state.quality_page
    
    if page == 'trial_setup':
        return (1, 2)
    elif page == 'record_entry':
        return (2, 2)
    else:
        return (0, 2)

def display_wizard_progress():
    """Display wizard progress indicator"""
    current, total = get_wizard_progress()
    
    if current == 0:
        return
    
    st.markdown("---")
    
    # Progress bar
    progress = current / total
    st.progress(progress)
    
    # Step indicator
    cols = st.columns(total)
    for i in range(total):
        with cols[i]:
            if i < current:
                st.success(f"✅ Step {i+1}")
            elif i == current - 1:
                st.info(f"📍 Step {i+1}")
            else:
                st.write(f"⏳ Step {i+1}")
    
    st.markdown("---")