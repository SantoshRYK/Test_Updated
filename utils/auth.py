# utils/auth.py
"""
Authentication and user management utilities
"""
import hashlib
import streamlit as st
from typing import Optional

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hashed password"""
    return hash_password(password) == hashed_password

def get_current_user() -> str:
    """Get current logged-in user"""
    return st.session_state.get('username', '')

def get_current_role() -> str:
    """Get current user role"""
    return st.session_state.get('role', '')

def is_logged_in() -> bool:
    """Check if user is logged in"""
    return st.session_state.get('logged_in', False)

def is_superuser() -> bool:
    """Check if current user is superuser"""
    return get_current_role() == 'superuser'

def is_manager() -> bool:
    """Check if current user is manager"""
    return get_current_role() == 'manager'

def is_admin() -> bool:
    """Check if current user is admin"""
    return get_current_role() == 'admin'

def is_regular_user() -> bool:
    """Check if current user is regular user"""
    return get_current_role() == 'user'

# ✅ NEW FUNCTION: Check if user is audit reviewer
def is_audit_reviewer() -> bool:
    """Check if current user has audit reviewer access"""
    return st.session_state.get('is_audit_reviewer', False)

def can_manage_users() -> bool:
    """Check if user can manage other users"""
    return get_current_role() in ['superuser', 'admin']

def can_view_all_data() -> bool:
    """Check if user can view all data"""
    return get_current_role() in ['superuser', 'admin', 'manager']

# ✅ MODIFIED: Added is_audit_reviewer parameter
def login_user(username: str, role: str, is_audit_reviewer: bool = False):
    """Log in user and set session state"""
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.role = role
    st.session_state.is_audit_reviewer = is_audit_reviewer  # ✅ NEW
    st.session_state.current_page = "home"

def logout_user():
    """Log out user"""
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.is_audit_reviewer = False  # ✅ NEW
    st.session_state.current_page = "home"

def initialize_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'role' not in st.session_state:
        st.session_state.role = ""
    if 'is_audit_reviewer' not in st.session_state:  # ✅ NEW
        st.session_state.is_audit_reviewer = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"

def get_role_display_name(role: str) -> str:
    """Get display name for role"""
    try:
        from config import ROLES
        return ROLES.get(role, {}).get('name', role.title())
    except:
        return role.title()

def get_role_emoji(role: str) -> str:
    """Get emoji for role"""
    try:
        from config import ROLES
        return ROLES.get(role, {}).get('emoji', '👤')
    except:
        role_emojis = {
            'superuser': '👑',
            'manager': '👨‍💼',
            'admin': '🔧',
            'user': '👤'
        }
        return role_emojis.get(role, '👤')

def get_role_level(role: str) -> int:
    """Get role level (higher = more privileges)"""
    role_levels = {
        'superuser': 4,
        'admin': 3,
        'manager': 2,
        'user': 1
    }
    return role_levels.get(role, 0)

def has_permission(permission: str, user_role: Optional[str] = None) -> bool:
    """Check if current user has specific permission"""
    if user_role is None:
        user_role = get_current_role()
    
    if not user_role:
        return False
    
    try:
        from config import ROLES
        role_permissions = ROLES.get(user_role, {}).get('permissions', [])
        
        # Superuser has all permissions
        if 'all' in role_permissions:
            return True
        
        return permission in role_permissions
    except:
        # Fallback permission check
        permission_map = {
            'superuser': ['all'],
            'admin': ['view_users', 'view_allocations', 'view_uat', 'email_settings'],
            'manager': ['view_users', 'view_allocations', 'view_uat', 'manage_team'],
            'user': ['create_allocation', 'view_own_allocation', 'create_uat', 'view_own_uat']
        }
        
        user_permissions = permission_map.get(user_role, [])
        if 'all' in user_permissions:
            return True
        return permission in user_permissions

def has_role_permission(required_role: str, user_role: Optional[str] = None) -> bool:
    """Check if user has required permission level based on role hierarchy"""
    if user_role is None:
        user_role = get_current_role()
    
    required_level = get_role_level(required_role)
    user_level = get_role_level(user_role)
    
    return user_level >= required_level

def get_user_permissions(role: Optional[str] = None) -> list:
    """Get list of permissions for a role"""
    if role is None:
        role = get_current_role()
    
    try:
        from config import ROLES
        return ROLES.get(role, {}).get('permissions', [])
    except:
        permission_map = {
            'superuser': ['all'],
            'admin': ['view_users', 'view_allocations', 'view_uat', 'email_settings'],
            'manager': ['view_users', 'view_allocations', 'view_uat', 'manage_team'],
            'user': ['create_allocation', 'view_own_allocation', 'create_uat', 'view_own_uat']
        }
        return permission_map.get(role, [])

def require_login(func):
    """Decorator to require login for a function"""
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            st.warning("⚠️ Please login to access this feature")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def require_role(required_role: str):
    """Decorator to require specific role for a function"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not is_logged_in():
                st.warning("⚠️ Please login to access this feature")
                st.stop()
            
            user_role = get_current_role()
            if not has_role_permission(required_role, user_role):
                st.error(f"❌ Access Denied: This feature requires {required_role} role or higher")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_permission(required_permission: str):
    """Decorator to require specific permission for a function"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not is_logged_in():
                st.warning("⚠️ Please login to access this feature")
                st.stop()
            
            if not has_permission(required_permission):
                st.error(f"❌ Access Denied: You don't have '{required_permission}' permission")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ✅ NEW DECORATOR: Require audit reviewer access
def require_audit_reviewer(func):
    """Decorator to require audit reviewer access for a function"""
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            st.warning("⚠️ Please login to access this feature")
            st.stop()
        
        if not is_audit_reviewer() and not is_superuser():
            st.error("❌ Access Denied: This feature requires Audit Reviewer access")
            st.stop()
        
        return func(*args, **kwargs)
    return wrapper