# pages/uat/uat_utils.py
"""
UAT utility functions
HELPER FUNCTIONS for UAT module
"""
from datetime import datetime
from typing import Dict, List

def calculate_uat_duration(uat_record: Dict) -> Dict:
    """Calculate planned and actual duration for UAT record"""
    try:
        planned_start = datetime.strptime(uat_record.get('planned_start_date', '2024-01-01'), '%Y-%m-%d')
        planned_end = datetime.strptime(uat_record.get('planned_end_date', '2024-12-31'), '%Y-%m-%d')
        planned_duration = (planned_end - planned_start).days
        
        actual_duration = None
        if uat_record.get('actual_start_date') and uat_record.get('actual_end_date'):
            actual_start = datetime.strptime(uat_record['actual_start_date'], '%Y-%m-%d')
            actual_end = datetime.strptime(uat_record['actual_end_date'], '%Y-%m-%d')
            actual_duration = (actual_end - actual_start).days
        
        return {
            'planned_duration': planned_duration,
            'actual_duration': actual_duration,
            'variance': (actual_duration - planned_duration) if actual_duration else None
        }
    except:
        return {
            'planned_duration': 0,
            'actual_duration': None,
            'variance': None
        }

def get_uat_completion_percentage(uat_records: List[Dict]) -> float:
    """Calculate UAT completion percentage"""
    if not uat_records:
        return 0.0
    
    completed = len([r for r in uat_records if r.get('status') == 'Completed'])
    return (completed / len(uat_records)) * 100

def get_uat_pass_percentage(uat_records: List[Dict]) -> float:
    """Calculate UAT pass percentage"""
    if not uat_records:
        return 0.0
    
    passed = len([r for r in uat_records if r.get('result') == 'Pass'])
    return (passed / len(uat_records)) * 100

def format_uat_summary(uat_record: Dict) -> str:
    """Format UAT record as summary text"""
    summary = f"""
    Trial ID: {uat_record.get('trial_id')}
    UAT Round: {uat_record.get('uat_round')}
    Category: {uat_record.get('category')}
    Status: {uat_record.get('status')}
    Result: {uat_record.get('result')}
    Planned: {uat_record.get('planned_start_date')} to {uat_record.get('planned_end_date')}
    """
    return summary.strip()