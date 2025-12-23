# components/forms.py
"""
Reusable form components
"""
import streamlit as st
from datetime import date
from typing import Dict, Optional

def render_category_input(key_prefix: str = "category") -> tuple:
    """
    Render category input (Build/Change Request)
    Returns: (category_type, category_detail, final_category)
    """
    # Initialize session state
    session_key = f'{key_prefix}_type'
    if session_key not in st.session_state:
        st.session_state[session_key] = "Build"
    
    category_type = st.selectbox(
        "Category Type*",
        ["Build", "Change Request"],
        help="Select the category type",
        key=f"{key_prefix}_select"
    )
    
    # Update session state
    st.session_state[session_key] = category_type
    
    # Conditional input for Change Request
    category_detail = ""
    if category_type == "Change Request":
        category_detail = st.text_input(
            "Change Request Details*",
            placeholder="e.g., CR01, CR02, CR-2024-001...",
            help="Enter the change request number or details",
            key=f"{key_prefix}_detail_input"
        )
    
    # Construct final category
    if category_type == "Build":
        final_category = "Build"
    else:
        if category_detail and category_detail.strip():
            final_category = f"Change Request - {category_detail.strip()}"
        else:
            final_category = ""
    
    return category_type, category_detail, final_category

def render_date_range_input(
    start_label: str = "Start Date*",
    end_label: str = "End Date*",
    key_prefix: str = "date",
    start_value: Optional[date] = None,
    end_value: Optional[date] = None,
    allow_none: bool = False
) -> tuple:
    """
    Render date range input
    Returns: (start_date, end_date)
    """
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            start_label,
            value=start_value,
            key=f"{key_prefix}_start"
        )
    
    with col2:
        end_date = st.date_input(
            end_label,
            value=end_value,
            key=f"{key_prefix}_end"
        )
    
    # Validation
    if start_date and end_date and end_date < start_date:
        st.warning("⚠️ End date should be after start date")
    
    return start_date, end_date

def render_status_result_input(key_prefix: str = "status") -> tuple:
    """
    Render Status and Result dropdowns
    Returns: (status, result)
    """
    from config import UAT_STATUS_OPTIONS, UAT_RESULT_OPTIONS
    
    col1, col2 = st.columns(2)
    
    with col1:
        status = st.selectbox(
            "Status*",
            UAT_STATUS_OPTIONS,
            help="Current status",
            key=f"{key_prefix}_status_select"
        )
    
    with col2:
        result = st.selectbox(
            "Result*",
            UAT_RESULT_OPTIONS,
            help="Test result",
            key=f"{key_prefix}_result_select"
        )
    
    return status, result