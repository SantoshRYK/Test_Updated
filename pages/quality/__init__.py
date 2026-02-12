"""
Quality Module Package
"""
from pages.quality import quality_main
from pages.quality import quality_create
from pages.quality import quality_view
from pages.quality import quality_dashboard
from pages.quality import quality_utils

# NEW: Add wizard pages
from pages.quality import quality_trial_setup
from pages.quality import quality_record_entry
from pages.quality import quality_wizard_utils

__all__ = [
    'quality_main',
    'quality_create',
    'quality_view',
    'quality_dashboard',
    'quality_utils',
    'quality_trial_setup',      # NEW
    'quality_record_entry',      # NEW
    'quality_wizard_utils'       # NEW
]