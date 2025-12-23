# pages/uat/uat_filters.py
"""
UAT-specific filtering logic
EXTEND HERE for advanced filtering
"""
import streamlit as st
from typing import Dict, List
from datetime import datetime

def apply_advanced_uat_filters(records: List[Dict], filters: Dict) -> List[Dict]:
    """
    Apply advanced filters to UAT records
    EXTEND THIS for custom filtering logic
    """
    filtered = records
    
    # Date range filter
    if filters.get('date_from'):
        filtered = [r for r in filtered if r.get('planned_start_date', '') >= filters['date_from']]
    
    if filters.get('date_to'):
        filtered = [r for r in filtered if r.get('planned_end_date', '') <= filters['date_to']]
    
    # Duration filter (if needed in future)
    if filters.get('min_duration'):
        filtered = filter_by_duration(filtered, filters['min_duration'])
    
    # Search across multiple fields
    if filters.get('search_term'):
        filtered = search_uat_records(filtered, filters['search_term'])
    
    return filtered

def filter_by_duration(records: List[Dict], min_days: int) -> List[Dict]:
    """Filter UAT records by minimum duration"""
    filtered = []
    for record in records:
        try:
            start = datetime.strptime(record.get('planned_start_date', '2024-01-01'), '%Y-%m-%d')
            end = datetime.strptime(record.get('planned_end_date', '2024-12-31'), '%Y-%m-%d')
            duration = (end - start).days
            if duration >= min_days:
                filtered.append(record)
        except:
            pass
    return filtered

def search_uat_records(records: List[Dict], search_term: str) -> List[Dict]:
    """Search UAT records across multiple fields"""
    if not search_term:
        return records
    
    search_term = search_term.lower()
    search_fields = ['trial_id', 'uat_round', 'category', 'status', 'result', 'email_body', 'created_by']
    
    filtered = []
    for record in records:
        for field in search_fields:
            value = str(record.get(field, '')).lower()
            if search_term in value:
                filtered.append(record)
                break
    
    return filtered