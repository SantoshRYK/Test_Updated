# services/audit_service.py
"""
Audit trail management business logic
DESIGNED FOR EASY EXTENSION - Add new audit features here
"""
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from utils.database import load_audit_logs, save_audit_logs, add_audit_log
from utils.auth import get_current_user
from config import AUDIT_ACTIONS, AUDIT_MODULES

def log_user_action(action: str, module: str, details: str, metadata: Optional[Dict] = None):
    """
    Log user action for audit trail
    
    Args:
        action: Action type (LOGIN, CREATE, UPDATE, DELETE, etc.)
        module: Module name (Authentication, Allocation, UAT, etc.)
        details: Detailed description of the action
        metadata: Additional metadata (optional)
    """
    try:
        log_entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": get_current_user(),
            "action": action,
            "module": module,
            "details": details,
            "metadata": metadata or {}
        }
        
        add_audit_log(log_entry)
    except Exception as e:
        # Silently fail - don't break app if audit logging fails
        print(f"Audit logging error: {e}")

# ==================== NEW FUNCTION - ADD THIS ====================

def log_audit(username: str, action: str, category: str, entity_type: str = None, 
              entity_id: str = None, details: dict = None, success: bool = True):
    """
    Enhanced audit logging function
    Used by trail_documents and other modules
    
    Args:
        username: User performing the action
        action: Action performed (create, update, delete, view, etc.)
        category: Category (trail_documents, allocation, uat, etc.)
        entity_type: Type of entity (optional)
        entity_id: ID of entity (optional)
        details: Additional details dictionary (optional)
        success: Whether action was successful
    """
    try:
        # Convert category to module name
        module = category.replace('_', ' ').title()
        
        # Format details
        detail_str = ""
        if details:
            detail_str = ", ".join([f"{k}: {v}" for k, v in details.items()])
        else:
            detail_str = f"{action.title()} operation"
        
        # Add entity information if provided
        if entity_type and entity_id:
            detail_str = f"{entity_type} {entity_id} - {detail_str}"
        
        # Create metadata
        metadata = {
            'category': category,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'success': success,
            'details': details or {}
        }
        
        log_entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": username,
            "action": action.upper(),
            "module": module,
            "details": detail_str,
            "metadata": metadata
        }
        
        add_audit_log(log_entry)
    except Exception as e:
        # Silently fail - don't break app if audit logging fails
        print(f"Audit logging error: {e}")

# ==================== END NEW FUNCTION ====================

def log_login(username: str, success: bool = True):
    """Log user login attempt"""
    action = "LOGIN" if success else "LOGIN_FAILED"
    details = f"User '{username}' logged in successfully" if success else f"Failed login attempt for '{username}'"
    log_user_action(action, "Authentication", details)

def log_logout(username: str):
    """Log user logout"""
    log_user_action("LOGOUT", "Authentication", f"User '{username}' logged out")

def log_page_view(page_name: str):
    """Log page view for analytics"""
    log_user_action("VIEW", page_name.title(), f"Viewed {page_name} page")

def log_data_change(module: str, action: str, record_id: str, changes: Dict):
    """
    Log data changes with before/after values
    USEFUL for compliance and debugging
    """
    details = f"{action} record {record_id}"
    metadata = {
        "record_id": record_id,
        "changes": changes
    }
    log_user_action(action, module, details, metadata)

def get_audit_logs_filtered(filters: Dict) -> List[Dict]:
    """Get filtered audit logs"""
    logs = load_audit_logs()
    filtered = logs
    
    # Filter by user
    if filters.get('user') and filters['user'] != 'All':
        filtered = [log for log in filtered if log.get('user') == filters['user']]
    
    # Filter by action
    if filters.get('action') and filters['action'] != 'All':
        filtered = [log for log in filtered if log.get('action') == filters['action']]
    
    # Filter by module
    if filters.get('module') and filters['module'] != 'All':
        filtered = [log for log in filtered if log.get('module') == filters['module']]
    
    # Filter by date range
    if filters.get('start_date'):
        filtered = [log for log in filtered if log.get('timestamp', '').split()[0] >= filters['start_date']]
    
    if filters.get('end_date'):
        filtered = [log for log in filtered if log.get('timestamp', '').split()[0] <= filters['end_date']]
    
    return filtered

def get_audit_statistics(logs: List[Dict]) -> Dict:
    """Calculate audit statistics"""
    stats = {
        'total': len(logs),
        'by_action': {},
        'by_module': {},
        'by_user': {},
        'by_date': {}
    }
    
    for log in logs:
        # By action
        action = log.get('action', 'Unknown')
        stats['by_action'][action] = stats['by_action'].get(action, 0) + 1
        
        # By module
        module = log.get('module', 'Unknown')
        stats['by_module'][module] = stats['by_module'].get(module, 0) + 1
        
        # By user
        user = log.get('user', 'Unknown')
        stats['by_user'][user] = stats['by_user'].get(user, 0) + 1
        
        # By date
        timestamp = log.get('timestamp', '')
        if timestamp:
            date = timestamp.split()[0]
            stats['by_date'][date] = stats['by_date'].get(date, 0) + 1
    
    return stats

def get_user_activity(username: str, days: int = 30) -> List[Dict]:
    """Get user activity for last N days"""
    logs = load_audit_logs()
    user_logs = [log for log in logs if log.get('user') == username]
    
    # Sort by timestamp descending
    user_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return user_logs[:100]  # Return last 100 activities

def export_audit_report(filters: Dict, format: str = "excel") -> Tuple[bool, any]:
    """
    Export audit report
    PLACEHOLDER for future enhancement
    """
    # TODO: Implement full audit report export
    return False, "Export feature coming soon"

# ==================== FUTURE AUDIT FEATURES (Easy to add) ====================

def track_field_changes(record_type: str, record_id: str, old_data: Dict, new_data: Dict):
    """
    Track field-level changes
    PLACEHOLDER for future enhancement
    """
    # TODO: Implement field-level change tracking
    pass

def generate_compliance_report(start_date: str, end_date: str) -> Dict:
    """
    Generate compliance report
    PLACEHOLDER for future enhancement
    """
    # TODO: Implement compliance reporting
    return {}

def archive_old_logs(days: int = 90):
    """
    Archive logs older than specified days
    PLACEHOLDER for future enhancement
    """
    # TODO: Implement log archival
    pass