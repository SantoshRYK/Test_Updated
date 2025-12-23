# pages/audit/audit_utils.py
"""
Audit Trail utility functions
Helper functions for audit operations
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional

def format_audit_log_display(log: Dict) -> str:
    """Format audit log for display"""
    timestamp = log.get('timestamp', 'N/A')
    user = log.get('user', 'Unknown')
    action = log.get('action', 'UNKNOWN')
    module = log.get('module', 'Unknown')
    
    return f"{timestamp} | {user} | {action} | {module}"

def get_action_emoji(action: str) -> str:
    """Get emoji for audit action"""
    action_emojis = {
        "LOGIN": "🔐",
        "LOGOUT": "🚪",
        "CREATE": "➕",
        "UPDATE": "✏️",
        "DELETE": "🗑️",
        "VIEW": "👁️",
        "EXPORT": "📥",
        "APPROVE": "✅",
        "REJECT": "❌",
        "LOGIN_FAILED": "🚫"
    }
    return action_emojis.get(action, "📝")

def get_module_emoji(module: str) -> str:
    """Get emoji for module"""
    module_emojis = {
        "Authentication": "🔐",
        "User Management": "👥",
        "Allocation": "📊",
        "UAT Status": "✅",
        "Audit Trail": "🔍",
        "Email Settings": "📧"
    }
    return module_emojis.get(module, "📋")

def filter_logs_by_date_range(logs: List[Dict], days: int) -> List[Dict]:
    """Filter logs by last N days"""
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        return [log for log in logs if log.get('timestamp', '').split()[0] >= cutoff_date]
    except:
        return logs

def group_logs_by_date(logs: List[Dict]) -> Dict[str, List[Dict]]:
    """Group audit logs by date"""
    grouped = {}
    for log in logs:
        timestamp = log.get('timestamp', 'N/A')
        date = timestamp.split()[0] if ' ' in timestamp else timestamp
        
        if date not in grouped:
            grouped[date] = []
        grouped[date].append(log)
    
    return grouped

def group_logs_by_user(logs: List[Dict]) -> Dict[str, List[Dict]]:
    """Group audit logs by user"""
    grouped = {}
    for log in logs:
        user = log.get('user', 'Unknown')
        
        if user not in grouped:
            grouped[user] = []
        grouped[user].append(log)
    
    return grouped

def get_most_active_users(logs: List[Dict], top_n: int = 5) -> List[tuple]:
    """Get most active users"""
    user_counts = {}
    for log in logs:
        user = log.get('user', 'Unknown')
        user_counts[user] = user_counts.get(user, 0) + 1
    
    # Sort by count descending
    sorted_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_users[:top_n]

def get_most_common_actions(logs: List[Dict], top_n: int = 5) -> List[tuple]:
    """Get most common actions"""
    action_counts = {}
    for log in logs:
        action = log.get('action', 'Unknown')
        action_counts[action] = action_counts.get(action, 0) + 1
    
    sorted_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_actions[:top_n]

def search_audit_logs(logs: List[Dict], search_term: str) -> List[Dict]:
    """Search audit logs"""
    if not search_term:
        return logs
    
    search_term = search_term.lower()
    search_fields = ['user', 'action', 'module', 'details']
    
    filtered = []
    for log in logs:
        for field in search_fields:
            value = str(log.get(field, '')).lower()
            if search_term in value:
                filtered.append(log)
                break
    
    return filtered

def export_audit_logs_csv(logs: List[Dict]) -> str:
    """Export audit logs as CSV string"""
    if not logs:
        return ""
    
    # CSV header
    csv_lines = ["Timestamp,User,Action,Module,Details"]
    
    # CSV rows
    for log in logs:
        timestamp = log.get('timestamp', 'N/A')
        user = log.get('user', 'Unknown')
        action = log.get('action', 'UNKNOWN')
        module = log.get('module', 'Unknown')
        details = log.get('details', '').replace(',', ';')  # Escape commas
        
        csv_lines.append(f"{timestamp},{user},{action},{module},{details}")
    
    return "\n".join(csv_lines)

def calculate_audit_metrics(logs: List[Dict]) -> Dict:
    """Calculate audit metrics for dashboard"""
    if not logs:
        return {}
    
    metrics = {
        'total_logs': len(logs),
        'unique_users': len(set([log.get('user') for log in logs])),
        'unique_actions': len(set([log.get('action') for log in logs])),
        'unique_modules': len(set([log.get('module') for log in logs])),
        'most_active_user': None,
        'most_common_action': None
    }
    
    # Most active user
    user_counts = {}
    for log in logs:
        user = log.get('user', 'Unknown')
        user_counts[user] = user_counts.get(user, 0) + 1
    
    if user_counts:
        metrics['most_active_user'] = max(user_counts, key=user_counts.get)
    
    # Most common action
    action_counts = {}
    for log in logs:
        action = log.get('action', 'Unknown')
        action_counts[action] = action_counts.get(action, 0) + 1
    
    if action_counts:
        metrics['most_common_action'] = max(action_counts, key=action_counts.get)
    
    return metrics