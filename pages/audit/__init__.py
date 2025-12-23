# pages/audit/__init__.py
"""
Audit Trail module
DESIGNED FOR EASY EXTENSION
"""

from .audit_main import render_audit_page
from .audit_viewer import render_audit_viewer_tab
from .audit_logger import render_audit_logger_settings

__all__ = [
    'render_audit_page',
    'render_audit_viewer_tab',
    'render_audit_logger_settings',
    'audit_main',
    'audit_viewer',
    'audit_logger',
    'trail_documents'  # New addition
]