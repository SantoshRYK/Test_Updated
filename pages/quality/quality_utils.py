"""
Quality Module Utilities
Helper functions for quality module
"""
import streamlit as st
from typing import List, Dict, Optional

def validate_quality_form_data(data: dict) -> tuple[bool, str]:
    """
    Validate quality form data
    
    Args:
        data: Form data dictionary
        
    Returns:
        (is_valid, error_message)
    """
    # Check required fields
    required_fields = ['trial_id', 'phase', 'no_of_uat_plans']
    for field in required_fields:
        if not data.get(field):
            return False, f"{field.replace('_', ' ').title()} is required"
    
    # Validate numeric fields
    try:
        no_of_rounds = int(data.get('no_of_rounds', 0))
        current_round = int(data.get('current_round', 0))
        total_requirements = int(data.get('total_requirements', 0))
        total_failures = int(data.get('total_failures', 0))
        
        if no_of_rounds <= 0:
            return False, "Number of rounds must be positive"
        
        if current_round <= 0:
            return False, "Current round must be positive"
        
        if current_round > no_of_rounds:
            return False, "Current round cannot exceed total rounds"
        
        if total_requirements <= 0:
            return False, "Total requirements must be positive"
        
        if total_failures > total_requirements:
            return False, "Total failures cannot exceed total requirements"
        
    except ValueError:
        return False, "Invalid numeric value"
    
    return True, "Valid"

def calculate_completion_percentage(current_round: int, total_rounds: int) -> float:
    """Calculate completion percentage"""
    if total_rounds == 0:
        return 0.0
    return round((current_round / total_rounds) * 100, 2)

def get_status_color(status: str) -> str:
    """Get color for status badge"""
    colors = {
        'Active': 'green',
        'Completed': 'blue',
        'On Hold': 'orange',
        'Cancelled': 'red'
    }
    return colors.get(status, 'gray')

def format_defect_density(defect_density: float) -> str:
    """Format defect density with color coding"""
    if defect_density < 10:
        return f"🟢 {defect_density:.2f}%"
    elif defect_density < 25:
        return f"🟡 {defect_density:.2f}%"
    else:
        return f"🔴 {defect_density:.2f}%"

def export_quality_data_to_excel(records: List[dict], filename: str = "quality_records.xlsx"):
    """Export quality records to Excel"""
    import pandas as pd
    from io import BytesIO
    
    df = pd.DataFrame(records)
    
    # Create Excel writer
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Quality Records')
    
    output.seek(0)
    return output

def create_quality_summary_report(records: List[dict]) -> Dict:
    """Create summary report from quality records"""
    if not records:
        return {}
    
    total_records = len(records)
    total_failures = sum(r['total_failures'] for r in records)
    total_requirements = sum(r['total_requirements'] for r in records)
    
    avg_defect_density = sum(r.get('defect_density', 0) for r in records) / total_records
    
    # Group by phase
    phase_summary = {}
    for record in records:
        phase = record['phase']
        if phase not in phase_summary:
            phase_summary[phase] = {
                'count': 0,
                'failures': 0,
                'requirements': 0
            }
        phase_summary[phase]['count'] += 1
        phase_summary[phase]['failures'] += record['total_failures']
        phase_summary[phase]['requirements'] += record['total_requirements']
    
    return {
        'total_records': total_records,
        'total_failures': total_failures,
        'total_requirements': total_requirements,
        'avg_defect_density': round(avg_defect_density, 2),
        'phase_summary': phase_summary
    }