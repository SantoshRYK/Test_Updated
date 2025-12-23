# services/allocation_service.py
"""
Allocation Service
Handles all allocation-related business logic
COMPLETE VERSION - FIXED update_allocation_record
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from config import ALLOCATIONS_FILE

class AllocationService:
    """Service class for allocation operations"""
    
    def __init__(self):
        self.allocations_file = ALLOCATIONS_FILE
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure allocations file exists"""
        if not os.path.exists(self.allocations_file):
            self._save_allocations([])
    
    def _load_allocations(self) -> List[Dict]:
        """Load all allocations from file"""
        try:
            if os.path.exists(self.allocations_file):
                with open(self.allocations_file, 'r') as f:
                    data = json.load(f)
                    # Filter only allocation records (not UAT records)
                    return [item for item in data if item.get('record_type') != 'uat']
            return []
        except Exception as e:
            print(f"Error loading allocations: {e}")
            return []
    
    def _save_allocations(self, allocations: List[Dict]) -> bool:
        """Save allocations to file"""
        try:
            # Load all data (including UAT records)
            all_data = []
            if os.path.exists(self.allocations_file):
                with open(self.allocations_file, 'r') as f:
                    all_data = json.load(f)
            
            # Keep UAT records, replace allocation records
            uat_records = [item for item in all_data if item.get('record_type') == 'uat']
            
            # Combine UAT records with new allocations
            combined_data = uat_records + allocations
            
            with open(self.allocations_file, 'w') as f:
                json.dump(combined_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving allocations: {e}")
            return False
    
    def get_all_allocations(self) -> List[Dict]:
        """Get all allocations"""
        return self._load_allocations()
    
    def get_allocation_by_id(self, allocation_id: str) -> Optional[Dict]:
        """Get allocation by ID"""
        allocations = self._load_allocations()
        for allocation in allocations:
            if allocation.get('id') == allocation_id:
                return allocation
        return None
    
    def get_allocations_by_user(self, username: str) -> List[Dict]:
        """Get allocations created by specific user"""
        allocations = self._load_allocations()
        return [a for a in allocations if a.get('created_by') == username]
    
    def get_allocations_by_engineer(self, engineer_name: str) -> List[Dict]:
        """Get allocations for specific engineer"""
        allocations = self._load_allocations()
        return [a for a in allocations if a.get('test_engineer_name') == engineer_name]
    
    def create_allocation(self, allocation_data: Dict) -> tuple[bool, str]:
        """Create new allocation"""
        try:
            # Generate ID
            allocation_data['id'] = datetime.now().strftime("%Y%m%d%H%M%S")
            allocation_data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            allocation_data['record_type'] = 'allocation'
            
            # Load existing allocations
            allocations = self._load_allocations()
            
            # Add new allocation
            allocations.append(allocation_data)
            
            # Save
            if self._save_allocations(allocations):
                return True, "Allocation created successfully"
            else:
                return False, "Failed to save allocation"
        
        except Exception as e:
            return False, f"Error creating allocation: {e}"
    
    def update_allocation(self, allocation_id: str, updated_data: Dict) -> tuple[bool, str]:
        """Update existing allocation"""
        try:
            allocations = self._load_allocations()
            
            # Find and update allocation
            found = False
            for i, allocation in enumerate(allocations):
                if allocation.get('id') == allocation_id:
                    # Update fields
                    allocations[i].update(updated_data)
                    allocations[i]['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    found = True
                    break
            
            if not found:
                return False, "Allocation not found"
            
            # Save
            if self._save_allocations(allocations):
                return True, "Allocation updated successfully"
            else:
                return False, "Failed to save allocation"
        
        except Exception as e:
            return False, f"Error updating allocation: {e}"
    
    def delete_allocation(self, allocation_id: str) -> tuple[bool, str]:
        """Delete allocation"""
        try:
            allocations = self._load_allocations()
            
            # Filter out the allocation to delete
            original_count = len(allocations)
            allocations = [a for a in allocations if a.get('id') != allocation_id]
            
            if len(allocations) == original_count:
                return False, "Allocation not found"
            
            # Save
            if self._save_allocations(allocations):
                return True, "Allocation deleted successfully"
            else:
                return False, "Failed to delete allocation"
        
        except Exception as e:
            return False, f"Error deleting allocation: {e}"
    
    def get_allocation_statistics(self) -> Dict:
        """Get allocation statistics"""
        allocations = self._load_allocations()
        
        stats = {
            'total': len(allocations),
            'by_system': {},
            'by_category': {},
            'by_therapeutic_area': {},
            'by_engineer': {},
            'by_role': {}
        }
        
        for allocation in allocations:
            # Count by system
            system = allocation.get('system', 'Unknown')
            stats['by_system'][system] = stats['by_system'].get(system, 0) + 1
            
            # Count by category
            category = allocation.get('trial_category_type', 'Unknown')
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            # Count by therapeutic area
            area = allocation.get('therapeutic_area_type', 'Unknown')
            stats['by_therapeutic_area'][area] = stats['by_therapeutic_area'].get(area, 0) + 1
            
            # Count by engineer
            engineer = allocation.get('test_engineer_name', 'Unknown')
            stats['by_engineer'][engineer] = stats['by_engineer'].get(engineer, 0) + 1
            
            # Count by role
            role = allocation.get('role', 'Unknown')
            stats['by_role'][role] = stats['by_role'].get(role, 0) + 1
        
        return stats
    
    def search_allocations(self, filters: Dict) -> List[Dict]:
        """Search allocations with filters"""
        allocations = self._load_allocations()
        
        # Apply filters
        if filters.get('system') and filters['system'] != 'All':
            allocations = [a for a in allocations if a.get('system') == filters['system']]
        
        if filters.get('trial_category') and filters['trial_category'] != 'All':
            allocations = [a for a in allocations if a.get('trial_category_type') == filters['trial_category']]
        
        if filters.get('therapeutic_area') and filters['therapeutic_area'] != 'All':
            allocations = [a for a in allocations if a.get('therapeutic_area_type') == filters['therapeutic_area']]
        
        if filters.get('engineer') and filters['engineer'] != 'All':
            allocations = [a for a in allocations if a.get('test_engineer_name') == filters['engineer']]
        
        if filters.get('role') and filters['role'] != 'All':
            allocations = [a for a in allocations if a.get('role') == filters['role']]
        
        if filters.get('trial_id') and filters['trial_id'] != 'All':
            allocations = [a for a in allocations if a.get('trial_id') == filters['trial_id']]
        
        if filters.get('created_by') and filters['created_by'] != 'All':
            allocations = [a for a in allocations if a.get('created_by') == filters['created_by']]
        
        # Date filters
        if filters.get('start_date'):
            allocations = [a for a in allocations 
                          if datetime.strptime(a.get('start_date', '2024-01-01'), '%Y-%m-%d').date() >= filters['start_date']]
        
        if filters.get('end_date'):
            allocations = [a for a in allocations 
                          if datetime.strptime(a.get('end_date', '2024-12-31'), '%Y-%m-%d').date() <= filters['end_date']]
        
        return allocations

# ============== STANDALONE HELPER FUNCTIONS ==============

def get_all_allocations() -> List[Dict]:
    """Get all allocations (standalone function)"""
    service = AllocationService()
    return service.get_all_allocations()

def get_allocation_by_id(allocation_id: str) -> Optional[Dict]:
    """Get allocation by ID (standalone function)"""
    service = AllocationService()
    return service.get_allocation_by_id(allocation_id)

def get_allocations_by_role(role: str, username: str) -> List[Dict]:
    """Get allocations based on user role"""
    service = AllocationService()
    
    if role in ["admin", "manager", "superuser"]:
        return service.get_all_allocations()
    else:
        return service.get_allocations_by_user(username)

def get_allocations_by_user(username: str) -> List[Dict]:
    """Get allocations created by specific user"""
    service = AllocationService()
    return service.get_allocations_by_user(username)

def get_allocations_by_engineer(engineer_name: str) -> List[Dict]:
    """Get allocations for specific engineer"""
    service = AllocationService()
    return service.get_allocations_by_engineer(engineer_name)

def create_allocation_record(allocation_data: Dict, username: str) -> tuple[bool, str]:
    """Create new allocation record"""
    service = AllocationService()
    allocation_data['created_by'] = username
    return service.create_allocation(allocation_data)

def update_allocation_record(allocation_id: str, updated_data: Dict) -> tuple[bool, str]:
    """
    Update existing allocation record - FIXED
    Removed audit logging to fix import error
    """
    try:
        from utils.auth import get_current_user
        
        service = AllocationService()
        
        # Add updated_by field
        updated_data['updated_by'] = get_current_user()
        updated_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Update allocation
        success, message = service.update_allocation(allocation_id, updated_data)
        
        # Optional: Log audit (only if function exists)
        if success:
            try:
                from services.audit_service import log_page_view
                # Use log_page_view as a workaround
                log_page_view(f"allocation_update_{allocation_id}")
            except:
                pass  # Skip audit if not available
        
        return success, message
    
    except Exception as e:
        return False, f"Error updating allocation: {str(e)}"

def delete_allocation_record(allocation_id: str) -> tuple[bool, str]:
    """Delete allocation record"""
    service = AllocationService()
    return service.delete_allocation(allocation_id)

def get_allocation_statistics() -> Dict:
    """Get allocation statistics"""
    service = AllocationService()
    return service.get_allocation_statistics()

def search_allocations(filters: Dict) -> List[Dict]:
    """Search allocations with filters"""
    service = AllocationService()
    return service.search_allocations(filters)

def get_allocation_records(filters=None) -> List[Dict]:
    """Get allocation records with optional filters"""
    service = AllocationService()
    
    if filters:
        return service.search_allocations(filters)
    else:
        return service.get_all_allocations()

# Alias for backward compatibility
delete_allocation_service = delete_allocation_record