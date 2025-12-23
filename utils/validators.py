# utils/validators.py
"""
Input validation utilities
"""
import re
from datetime import datetime, date
from typing import Tuple, Optional
from config import VALIDATION

def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format"""
    if not email:
        return False, "Email is required"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, ""

def validate_password(password: str, confirm_password: Optional[str] = None) -> Tuple[bool, str]:
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    
    min_length = VALIDATION.get("min_password_length", 6)
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"
    
    if confirm_password is not None and password != confirm_password:
        return False, "Passwords do not match"
    
    return True, ""

def validate_username(username: str) -> Tuple[bool, str]:
    """Validate username"""
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, ""

def validate_date_range(start_date: date, end_date: date) -> Tuple[bool, str]:
    """Validate date range"""
    if not start_date or not end_date:
        return False, "Both dates are required"
    
    if end_date < start_date:
        return False, "End date must be after start date"
    
    return True, ""

def validate_text_length(text: str, max_length: int, field_name: str = "Field") -> Tuple[bool, str]:
    """Validate text length"""
    if text and len(text) > max_length:
        return False, f"{field_name} must be {max_length} characters or less"
    
    return True, ""

def validate_required_field(value: any, field_name: str) -> Tuple[bool, str]:
    """Validate required field"""
    if value is None or (isinstance(value, str) and not value.strip()):
        return False, f"{field_name} is required"
    
    return True, ""