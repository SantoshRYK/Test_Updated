# services/user_service.py
"""
User management business logic
"""
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from utils.database import (
    load_users, save_users, get_user, user_exists,
    load_pending_users, save_pending_users,
    load_password_reset_requests, save_password_reset_requests
)
from utils.auth import hash_password, get_current_user
from utils.validators import validate_email, validate_password, validate_username
from services.audit_service import log_user_action

def create_user(username: str, email: str, password: str, role: str = "user", created_by: str = None) -> Tuple[bool, str]:
    """Create new user"""
    try:
        # Validate inputs
        valid, msg = validate_username(username)
        if not valid:
            return False, msg
        
        valid, msg = validate_email(email)
        if not valid:
            return False, msg
        
        valid, msg = validate_password(password)
        if not valid:
            return False, msg
        
        # Check if user exists
        if user_exists(username):
            return False, "Username already exists"
        
        # Create user
        users = load_users()
        users[username] = {
            "password": hash_password(password),
            "email": email,
            "role": role,
            "status": "active",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "created_by": created_by or get_current_user()
        }
        
        if save_users(users):
            # Log action
            log_user_action("CREATE", "User Management", f"Created user: {username} with role: {role}")
            return True, f"User '{username}' created successfully"
        else:
            return False, "Failed to save user"
    
    except Exception as e:
        return False, f"Error creating user: {str(e)}"

def update_user_role(username: str, new_role: str) -> Tuple[bool, str]:
    """Update user role"""
    try:
        users = load_users()
        
        if username not in users:
            return False, "User not found"
        
        old_role = users[username].get('role')
        users[username]['role'] = new_role
        users[username]['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        users[username]['updated_by'] = get_current_user()
        
        if save_users(users):
            log_user_action("UPDATE", "User Management", f"Updated {username} role from {old_role} to {new_role}")
            return True, f"User '{username}' role updated to {new_role}"
        else:
            return False, "Failed to update user"
    
    except Exception as e:
        return False, f"Error updating user: {str(e)}"

def delete_user(username: str) -> Tuple[bool, str]:
    """Delete user"""
    try:
        users = load_users()
        
        if username not in users:
            return False, "User not found"
        
        if username == "superuser":
            return False, "Cannot delete superuser"
        
        user_role = users[username].get('role')
        del users[username]
        
        if save_users(users):
            log_user_action("DELETE", "User Management", f"Deleted user: {username} (role: {user_role})")
            return True, f"User '{username}' deleted successfully"
        else:
            return False, "Failed to delete user"
    
    except Exception as e:
        return False, f"Error deleting user: {str(e)}"

def approve_pending_user(username: str, approved_role: str) -> Tuple[bool, str]:
    """Approve pending user registration"""
    try:
        pending_users = load_pending_users()
        
        # Find pending user
        pending_user = None
        for user in pending_users:
            if user.get('username') == username:
                pending_user = user
                break
        
        if not pending_user:
            return False, "Pending user not found"
        
        # Create active user
        users = load_users()
        users[username] = {
            "password": pending_user['password'],
            "email": pending_user['email'],
            "role": approved_role,
            "status": "active",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "approved_by": get_current_user()
        }
        
        if save_users(users):
            # Remove from pending
            pending_users = [u for u in pending_users if u.get('username') != username]
            save_pending_users(pending_users)
            
            log_user_action("APPROVE", "User Management", f"Approved user: {username} as {approved_role}")
            return True, f"User '{username}' approved as {approved_role}"
        else:
            return False, "Failed to approve user"
    
    except Exception as e:
        return False, f"Error approving user: {str(e)}"

def reject_pending_user(username: str) -> Tuple[bool, str]:
    """Reject pending user registration"""
    try:
        pending_users = load_pending_users()
        pending_users = [u for u in pending_users if u.get('username') != username]
        
        if save_pending_users(pending_users):
            log_user_action("REJECT", "User Management", f"Rejected user registration: {username}")
            return True, f"Registration for '{username}' rejected"
        else:
            return False, "Failed to reject user"
    
    except Exception as e:
        return False, f"Error rejecting user: {str(e)}"

def get_user_statistics() -> Dict:
    """Get user statistics"""
    users = load_users()
    
    stats = {
        'total': len(users),
        'by_role': {},
        'by_status': {},
        'pending': len(load_pending_users())
    }
    
    for user in users.values():
        role = user.get('role', 'unknown')
        status = user.get('status', 'active')
        
        stats['by_role'][role] = stats['by_role'].get(role, 0) + 1
        stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
    
    return stats