# services/uat_service.py
"""
UAT Status management business logic
DESIGNED FOR EASY EXTENSION - Add new features here
"""
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from utils.database import (
    load_allocations, save_allocations,
    add_uat_record, update_uat_record, delete_uat_record, get_uat_record
)
from utils.auth import get_current_user, get_current_role
from utils.validators import validate_date_range, validate_required_field
from utils.email_handler import send_uat_notification
from services.audit_service import log_user_action

def create_uat_record(uat_data: Dict) -> Tuple[bool, str]:
    """Create new UAT record with validation"""
    try:
        # Validate required fields
        required_fields = {
            'trial_id': 'Trial ID',
            'uat_round': 'UAT Round',
            'category': 'Category',
            'planned_start_date': 'Planned Start Date',
            'planned_end_date': 'Planned End Date',
            'status': 'Status',
            'result': 'Result'
        }
        
        for field, display_name in required_fields.items():
            valid, msg = validate_required_field(uat_data.get(field), display_name)
            if not valid:
                return False, msg
        
        # Validate planned dates
        planned_start = datetime.strptime(uat_data['planned_start_date'], '%Y-%m-%d').date()
        planned_end = datetime.strptime(uat_data['planned_end_date'], '%Y-%m-%d').date()
        valid, msg = validate_date_range(planned_start, planned_end)
        if not valid:
            return False, f"Planned dates: {msg}"
        
        # Validate actual dates if provided
        if uat_data.get('actual_start_date') and uat_data.get('actual_end_date'):
            actual_start = datetime.strptime(uat_data['actual_start_date'], '%Y-%m-%d').date()
            actual_end = datetime.strptime(uat_data['actual_end_date'], '%Y-%m-%d').date()
            valid, msg = validate_date_range(actual_start, actual_end)
            if not valid:
                return False, f"Actual dates: {msg}"
        
        # Add metadata
        uat_data['created_by'] = get_current_user()
        uat_data['record_type'] = 'uat'
        
        # Save UAT record (backward compatible with allocations file)
        all_data = load_allocations()
        uat_data['id'] = datetime.now().strftime("%Y%m%d%H%M%S")
        uat_data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uat_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        all_data.append(uat_data)
        
        if save_allocations(all_data):
            # Send notification
            try:
                send_uat_notification(uat_data, "created")
            except:
                pass
            
            # Log action
            log_user_action("CREATE", "UAT Status", f"Created UAT record for Trial ID: {uat_data.get('trial_id')}")
            
            return True, "UAT record created successfully"
        else:
            return False, "Failed to save UAT record"
    
    except Exception as e:
        return False, f"Error creating UAT record: {str(e)}"

def update_uat_record_service(uat_id: str, updated_data: Dict) -> Tuple[bool, str]:
    """Update UAT record"""
    try:
        all_data = load_allocations()
        
        for i, record in enumerate(all_data):
            if record.get('id') == uat_id and record.get('record_type') == 'uat':
                # Update record
                all_data[i].update(updated_data)
                all_data[i]['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                all_data[i]['updated_by'] = get_current_user()
                
                if save_allocations(all_data):
                    log_user_action("UPDATE", "UAT Status", f"Updated UAT record: {all_data[i].get('trial_id')}")
                    return True, "UAT record updated successfully"
                else:
                    return False, "Failed to save changes"
        
        return False, "UAT record not found"
    
    except Exception as e:
        return False, f"Error updating UAT record: {str(e)}"

def delete_uat_record_service(uat_id: str) -> Tuple[bool, str]:
    """Delete UAT record"""
    try:
        all_data = load_allocations()
        
        # Find record to get trial_id for logging
        trial_id = None
        for record in all_data:
            if record.get('id') == uat_id and record.get('record_type') == 'uat':
                trial_id = record.get('trial_id')
                break
        
        if not trial_id:
            return False, "UAT record not found"
        
        # Remove record
        all_data = [item for item in all_data if not (item.get('id') == uat_id and item.get('record_type') == 'uat')]
        
        if save_allocations(all_data):
            log_user_action("DELETE", "UAT Status", f"Deleted UAT record for Trial ID: {trial_id}")
            return True, "UAT record deleted successfully"
        else:
            return False, "Failed to delete UAT record"
    
    except Exception as e:
        return False, f"Error deleting UAT record: {str(e)}"

def get_user_uat_records(username: str) -> List[Dict]:
    """Get UAT records for specific user"""
    all_data = load_allocations()
    uat_records = [item for item in all_data if item.get('record_type') == 'uat']
    return [r for r in uat_records if r.get('created_by') == username]

def get_uat_records_by_role(role: str, username: str) -> List[Dict]:
    """Get UAT records based on user role"""
    all_data = load_allocations()
    uat_records = [item for item in all_data if item.get('record_type') == 'uat']
    
    if role in ['superuser', 'admin', 'manager']:
        return uat_records
    else:
        return [r for r in uat_records if r.get('created_by') == username]

def get_uat_statistics(uat_records: List[Dict]) -> Dict:
    """Calculate UAT statistics"""
    stats = {
        'total': len(uat_records),
        'by_status': {},
        'by_result': {},
        'by_category': {},
        'by_round': {},
        'by_user': {},
        'completed': 0,
        'in_progress': 0,
        'passed': 0,
        'failed': 0
    }
    
    for record in uat_records:
        # Status
        status = record.get('status', 'Unknown')
        stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        if status == 'Completed':
            stats['completed'] += 1
        elif status == 'In Progress':
            stats['in_progress'] += 1
        
        # Result
        result = record.get('result', 'Unknown')
        stats['by_result'][result] = stats['by_result'].get(result, 0) + 1
        
        if result == 'Pass':
            stats['passed'] += 1
        elif result == 'Fail':
            stats['failed'] += 1
        
        # Category
        category_type = record.get('category_type', 'Unknown')
        stats['by_category'][category_type] = stats['by_category'].get(category_type, 0) + 1
        
        # Round
        uat_round = record.get('uat_round', 'Unknown')
        stats['by_round'][uat_round] = stats['by_round'].get(uat_round, 0) + 1
        
        # User
        created_by = record.get('created_by', 'Unknown')
        stats['by_user'][created_by] = stats['by_user'].get(created_by, 0) + 1
    
    # Calculate rates
    if stats['total'] > 0:
        stats['completion_rate'] = (stats['completed'] / stats['total']) * 100
        stats['pass_rate'] = (stats['passed'] / stats['total']) * 100
    else:
        stats['completion_rate'] = 0
        stats['pass_rate'] = 0
    
    return stats

def filter_uat_records(records: List[Dict], filters: Dict) -> List[Dict]:
    """Filter UAT records based on multiple criteria"""
    filtered = records
    
    # Filter by trial ID
    if filters.get('trial_id') and filters['trial_id'] != 'All':
        filtered = [r for r in filtered if r.get('trial_id') == filters['trial_id']]
    
    # Filter by category
    if filters.get('category') and filters['category'] != 'All':
        if filters['category'] == 'Build':
            filtered = [r for r in filtered if r.get('category_type') == 'Build']
        elif filters['category'] == 'Change Request':
            filtered = [r for r in filtered if r.get('category_type') == 'Change Request']
    
    # Filter by status
    if filters.get('status') and filters['status'] != 'All':
        filtered = [r for r in filtered if r.get('status') == filters['status']]
    
    # Filter by result
    if filters.get('result') and filters['result'] != 'All':
        filtered = [r for r in filtered if r.get('result') == filters['result']]
    
    # Filter by user (for managers)
    if filters.get('user') and filters['user'] != 'All':
        filtered = [r for r in filtered if r.get('created_by') == filters['user']]
    
    return filtered

def get_user_uat_statistics(uat_records: List[Dict]) -> Dict:
    """Get user-wise UAT statistics (for managers)"""
    user_stats = {}
    
    for record in uat_records:
        user = record.get('created_by', 'Unknown')
        
        if user not in user_stats:
            user_stats[user] = {
                'total': 0,
                'completed': 0,
                'in_progress': 0,
                'passed': 0,
                'failed': 0
            }
        
        user_stats[user]['total'] += 1
        
        if record.get('status') == 'Completed':
            user_stats[user]['completed'] += 1
        elif record.get('status') == 'In Progress':
            user_stats[user]['in_progress'] += 1
        
        if record.get('result') == 'Pass':
            user_stats[user]['passed'] += 1
        elif record.get('result') == 'Fail':
            user_stats[user]['failed'] += 1
    
    # Calculate percentages
    for user, stats in user_stats.items():
        if stats['total'] > 0:
            stats['completion_rate'] = round((stats['completed'] / stats['total']) * 100, 1)
            stats['pass_rate'] = round((stats['passed'] / stats['total']) * 100, 1)
        else:
            stats['completion_rate'] = 0
            stats['pass_rate'] = 0
    
    return user_stats

# ==================== FUTURE UAT FEATURES (Easy to add) ====================

def add_uat_comment(uat_id: str, comment: str, user: str) -> Tuple[bool, str]:
    """
    Add comment to UAT record
    PLACEHOLDER for future enhancement
    """
    # TODO: Implement UAT comments feature
    return False, "Comments feature coming soon"

def add_uat_attachment(uat_id: str, file_data: Dict) -> Tuple[bool, str]:
    """
    Add attachment to UAT record
    PLACEHOLDER for future enhancement
    """
    # TODO: Implement UAT attachments feature
    return False, "Attachments feature coming soon"

def create_uat_approval_workflow(uat_id: str, approvers: List[str]) -> Tuple[bool, str]:
    """
    Create UAT approval workflow
    PLACEHOLDER for future enhancement
    """
    # TODO: Implement UAT approval workflow
    return False, "Approval workflow coming soon"