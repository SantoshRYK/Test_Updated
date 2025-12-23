# config.py
"""
Application configuration and constants
Centralized configuration for easy management
"""
import os
from pathlib import Path

# ==================== PATHS ====================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = os.path.join(BASE_DIR, "data")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Data file paths
USERS_FILE = os.path.join(DATA_DIR, "users.json")
ALLOCATIONS_FILE = os.path.join(DATA_DIR, "allocations.json")
UAT_RECORDS_FILE = os.path.join(DATA_DIR, "uat_records.json")  # NEW
AUDIT_LOGS_FILE = os.path.join(DATA_DIR, "audit_logs.json")    # NEW
EMAIL_CONFIG_FILE = os.path.join(DATA_DIR, "email_config.json")
PENDING_USERS_FILE = os.path.join(DATA_DIR, "pending_users.json")
PASSWORD_RESET_FILE = os.path.join(DATA_DIR, "password_reset_requests.json")
TRAIL_DOCUMENTS_FILE = os.path.join(DATA_DIR, "trail_documents.json")

# ==================== APP SETTINGS ====================
APP_TITLE = "Test Engineer Portal"
APP_ICON = "🧪"
PAGE_LAYOUT = "wide"

# ==================== DEFAULT CREDENTIALS ====================
DEFAULT_SUPERUSER = {
    "username": "superuser",
    "password": "super123",  # Will be hashed
    "email": "superuser@testportal.com",
    "role": "superuser"
}

# ==================== ROLES ====================
ROLES = {
    "superuser": {"name": "Super User", "emoji": "👑", "level": 4},
    "manager": {"name": "Manager", "emoji": "👨‍💼", "level": 3},
    "admin": {"name": "Admin", "emoji": "🔧", "level": 2},
    "user": {"name": "User", "emoji": "👤", "level": 1}
}

# ==================== UAT CONFIGURATION ====================
UAT_STATUS_OPTIONS = [
    "Not Started",
    "In Progress",
    "Completed",
    "On Hold",
    "Cancelled"
]

UAT_RESULT_OPTIONS = [
    "Pending",
    "Pass",
    "Fail",
    "Partial Pass"
]

UAT_CATEGORY_TYPES = [
    "Build",
    "Change Request"
]

UAT_PRIORITY_OPTIONS = [  # NEW: If you want to add priority
    "Critical",
    "High",
    "Medium",
    "Low"
]

# ==================== ALLOCATION CONFIGURATION ====================
SYSTEMS = [
    "INFORM",
    "VEEVA",
    "eCOA",
    "ePID",
    "CGM",
    "Others"
]

THERAPEUTIC_AREAS = [
    "Diabetic",
    "Obesity",
    "CKAD (Chronic Kidney Allograft Dysfunction)",
    "CagriSema & OLD-D",
    "Phase 1 & NIS",
    "Rare Disease",
    "Others"
]

# ADDED: Trial Categories for allocation forms
TRIAL_CATEGORIES = [
    "Build",
    "Change Request - 01",
    "Change Request - 02",
    "Change Request - 03"
]

# Role options for allocations (renamed for clarity)
ROLES_ALLOCATION = ["TE1", "TE2", "TE3", "Lead", "Scripting", "UATR1", "UATR2"]

# Activity types (optional - for future use)
ACTIVITY_TYPES = [
    "Test Execution",
    "Test Case Development",
    "Test Planning",
    "UAT Support",
    "Automation",
    "Documentation",
    "Others"
]

# ==================== AUDIT CONFIGURATION ====================
AUDIT_ACTIONS = [  # NEW
    "LOGIN",
    "LOGOUT",
    "CREATE",
    "UPDATE",
    "DELETE",
    "VIEW",
    "EXPORT",
    "APPROVE",
    "REJECT"
]

AUDIT_MODULES = [  # NEW
    "Authentication",
    "User Management",
    "Allocation",
    "UAT Status",
    "Audit Trail",
    "Email Settings"
]

# ==================== EMAIL CONFIGURATION ====================
DEFAULT_EMAIL_CONFIG = {
    "enabled": False,
    "smtp_server": "",
    "smtp_port": 587,
    "sender_email": "",
    "sender_password": "",
    "use_tls": True,
    "notify_on_create": True,
    "notify_on_update": False,
    "admin_email": "superuser@testportal.com"
}

# ==================== VALIDATION RULES ====================
VALIDATION = {
    "min_password_length": 6,
    "max_activity_length": 200,
    "max_email_body_length": 5000,
    "max_reason_length": 200,
    "allowed_file_extensions": [".xlsx", ".csv", ".pdf"],
    "max_file_size_mb": 10
}

# ==================== UI CONFIGURATION ====================
COLORS = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "success": "#4CAF50",
    "danger": "#F44336",
    "warning": "#FF9800",
    "info": "#2196F3"
}

STATUS_COLORS = {
    "Completed": "green",
    "In Progress": "blue",
    "Not Started": "gray",
    "On Hold": "orange",
    "Cancelled": "red",
    "Pass": "green",
    "Fail": "red",
    "Pending": "gray",
    "Partial Pass": "orange"
}

STATUS_EMOJIS = {
    "Completed": "✅",
    "In Progress": "🔄",
    "Not Started": "⏳",
    "On Hold": "⏸️",
    "Cancelled": "❌",
    "Pass": "✅",
    "Fail": "❌",
    "Pending": "⏳",
    "Partial Pass": "⚠️"
}

# ==================== PAGINATION ====================
ITEMS_PER_PAGE = 20
MAX_DISPLAY_ITEMS = 100

# ==================== DATE FORMATS ====================
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DISPLAY_DATE_FORMAT = "%d %b %Y"
DISPLAY_DATETIME_FORMAT = "%d %b %Y %I:%M %p"