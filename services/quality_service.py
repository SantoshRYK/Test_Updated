"""
Trial Quality Matrix Service
Handles business logic for quality records
"""
import json
import os
from datetime import datetime
from typing import List, Optional, Dict
from models.quality import QualityRecord
from utils.database import save_json, load_json
from services.audit_service import log_audit  # ✅ FIXED: Correct import

class QualityService:
    """Service for managing trial quality records"""
    
    QUALITY_FILE = "data/quality_records.json"
    
    def __init__(self):
        """Initialize service"""
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure data file exists"""
        if not os.path.exists(self.QUALITY_FILE):
            os.makedirs(os.path.dirname(self.QUALITY_FILE), exist_ok=True)
            save_json(self.QUALITY_FILE, [])
    
    def generate_record_id(self) -> str:
        """Generate unique record ID"""
        records = self.get_all_records()
        if not records:
            return "QM001"
        
        # Extract numeric part and increment
        try:
            last_id = max([int(r['record_id'][2:]) for r in records if r['record_id'].startswith('QM')])
            return f"QM{str(last_id + 1).zfill(3)}"
        except (ValueError, KeyError):
            return "QM001"
    
    def create_record(self, record_data: dict, username: str) -> tuple[bool, str, Optional[QualityRecord]]:
        """
        Create new quality record
        
        Args:
            record_data: Record data
            username: User creating the record
            
        Returns:
            (success, message, record)
        """
        try:
            # Generate ID and add metadata
            record_data['record_id'] = self.generate_record_id()
            record_data['created_by'] = username
            record_data['created_at'] = datetime.now().isoformat()
            record_data['updated_at'] = datetime.now().isoformat()
            record_data['status'] = 'Active'
            
            # Create record object
            record = QualityRecord(**record_data)
            
            # Validate
            is_valid, msg = record.validate()
            if not is_valid:
                return False, msg, None
            
            # Save to file
            records = self.get_all_records()
            records.append(record.to_dict())
            save_json(self.QUALITY_FILE, records)
            
            # ✅ FIXED: Audit log using correct function signature
            try:
                log_audit(
                    username=username,
                    action="CREATE",
                    category="quality_matrix",
                    entity_type="Quality Record",
                    entity_id=record.record_id,
                    details={
                        'trial_id': record.trial_id,
                        'phase': record.phase,
                        'defect_density': record.defect_density
                    },
                    success=True
                )
            except Exception as e:
                print(f"Audit logging error: {e}")
            
            return True, f"Quality record {record.record_id} created successfully", record
            
        except Exception as e:
            return False, f"Error creating record: {str(e)}", None
    
    def get_all_records(self) -> List[dict]:
        """Get all quality records"""
        try:
            return load_json(self.QUALITY_FILE)
        except:
            return []
    
    def get_record_by_id(self, record_id: str) -> Optional[dict]:
        """Get record by ID"""
        records = self.get_all_records()
        for record in records:
            if record.get('record_id') == record_id:
                return record
        return None
    
    def get_records_by_trial(self, trial_id: str) -> List[dict]:
        """Get all records for a specific trial"""
        records = self.get_all_records()
        return [r for r in records if r.get('trial_id') == trial_id]
    
    def get_records_by_user(self, username: str) -> List[dict]:
        """Get records created by user"""
        records = self.get_all_records()
        return [r for r in records if r.get('created_by') == username]
    
    def update_record(self, record_id: str, updates: dict, username: str) -> tuple[bool, str]:
        """
        Update quality record
        
        Args:
            record_id: Record ID
            updates: Fields to update
            username: User updating the record
            
        Returns:
            (success, message)
        """
        try:
            records = self.get_all_records()
            
            for i, record in enumerate(records):
                if record.get('record_id') == record_id:
                    # Store old values for audit
                    old_values = {k: record.get(k) for k in updates.keys()}
                    
                    # Update fields
                    record.update(updates)
                    record['updated_at'] = datetime.now().isoformat()
                    
                    # Recalculate defect density
                    temp_record = QualityRecord.from_dict(record)
                    record['defect_density'] = temp_record.calculate_defect_density()
                    
                    # Validate
                    is_valid, msg = temp_record.validate()
                    if not is_valid:
                        return False, msg
                    
                    records[i] = record
                    save_json(self.QUALITY_FILE, records)
                    
                    # ✅ FIXED: Audit log
                    try:
                        log_audit(
                            username=username,
                            action="UPDATE",
                            category="quality_matrix",
                            entity_type="Quality Record",
                            entity_id=record_id,
                            details={
                                'updated_fields': list(updates.keys()),
                                'old_values': old_values,
                                'new_values': updates
                            },
                            success=True
                        )
                    except Exception as e:
                        print(f"Audit logging error: {e}")
                    
                    return True, f"Record {record_id} updated successfully"
            
            return False, f"Record {record_id} not found"
            
        except Exception as e:
            return False, f"Error updating record: {str(e)}"
    
    def delete_record(self, record_id: str, username: str) -> tuple[bool, str]:
        """Delete quality record"""
        try:
            records = self.get_all_records()
            initial_count = len(records)
            
            # Find the record before deleting (for audit)
            deleted_record = None
            for record in records:
                if record.get('record_id') == record_id:
                    deleted_record = record
                    break
            
            records = [r for r in records if r.get('record_id') != record_id]
            
            if len(records) == initial_count:
                return False, f"Record {record_id} not found"
            
            save_json(self.QUALITY_FILE, records)
            
            # ✅ FIXED: Audit log
            try:
                log_audit(
                    username=username,
                    action="DELETE",
                    category="quality_matrix",
                    entity_type="Quality Record",
                    entity_id=record_id,
                    details={
                        'trial_id': deleted_record.get('trial_id') if deleted_record else 'Unknown',
                        'phase': deleted_record.get('phase') if deleted_record else 'Unknown'
                    },
                    success=True
                )
            except Exception as e:
                print(f"Audit logging error: {e}")
            
            return True, f"Record {record_id} deleted successfully"
            
        except Exception as e:
            return False, f"Error deleting record: {str(e)}"
    
    def get_statistics(self, filters: Optional[dict] = None) -> Dict:
        """
        Get statistics for dashboard
        CORRECTED: Calculate cumulative requirements and cumulative failures properly
        
        Logic:
        Trial A:
        ├── Round 1: Req=50, Fail=10
        └── Round 2: Req=12, Fail=0
        
        Calculations:
        - Total Requirements: Round 1 (50) + New in Round 2 (12-10=2) = 52
        - Total Failures: Round 1 (10) + Round 2 (0) = 10
        - Overall Defect Density: (10/52) × 100 = 19.23%
        
        Args:
            filters: Optional filters
            
        Returns:
            Statistics dictionary
        """
        all_records = self.get_all_records()
        
        # Apply filters
        filtered_records = all_records
        if filters:
            if filters.get('trial_id'):
                filtered_records = [r for r in filtered_records if r.get('trial_id') == filters['trial_id']]
            if filters.get('phase'):
                filtered_records = [r for r in filtered_records if r.get('phase') == filters['phase']]
            if filters.get('type_of_requirement'):
                filtered_records = [r for r in filtered_records if r.get('type_of_requirement') == filters['type_of_requirement']]
            if filters.get('created_by'):
                filtered_records = [r for r in filtered_records if r.get('created_by') == filters['created_by']]
            if filters.get('current_round'):
                filtered_records = [r for r in filtered_records if r.get('current_round') == filters['current_round']]
        
        if not filtered_records:
            return self._empty_statistics()
        
        # Group records by trial and sort by round
        trials_data = {}
        for record in filtered_records:
            trial_id = record.get('trial_id')
            if trial_id not in trials_data:
                trials_data[trial_id] = []
            trials_data[trial_id].append(record)
        
        # Sort each trial's records by round
        for trial_id in trials_data:
            trials_data[trial_id].sort(key=lambda x: x.get('current_round', 0))
        
        # Calculate cumulative requirements and cumulative failures per trial
        total_requirements = 0
        total_failures = 0
        unique_trials = len(trials_data)
        
        latest_records = []
        
        for trial_id, records in trials_data.items():
            if not records:
                continue
            
            # CUMULATIVE CALCULATION
            trial_total_req = 0
            trial_total_fail = 0
            previous_failures = 0
            
            for i, record in enumerate(records):
                current_req = record.get('total_requirements', 0)
                current_fail = record.get('total_failures', 0)
                
                if i == 0:  # Round 1
                    # All requirements are new in Round 1
                    trial_total_req = current_req
                    trial_total_fail = current_fail
                else:
                    # Round 2+: Requirements = Failed from previous + New additions
                    # New additions = current_req - previous_failures
                    new_additions = current_req - previous_failures
                    if new_additions > 0:
                        trial_total_req += new_additions
                    
                    # Accumulate failures from current round
                    trial_total_fail += current_fail
                
                # Update previous failures for next iteration
                previous_failures = current_fail
            
            # Add to totals
            total_requirements += trial_total_req
            total_failures += trial_total_fail
            latest_records.append(records[-1])
        
        # Calculate average defect density from latest records
        avg_defect_density = sum(r.get('defect_density', 0) for r in latest_records) / len(latest_records) if latest_records else 0
        
        # Failure reasons from ALL rounds (cumulative)
        failure_reasons = {
            'Spec Issue': sum(r.get('spec_issue', 0) for r in filtered_records),
            'Mock CRF Issue': sum(r.get('mock_crf_issue', 0) for r in filtered_records),
            'Programming Issue': sum(r.get('programming_issue', 0) for r in filtered_records),
            'Scripting Issue': sum(r.get('scripting_issue', 0) for r in filtered_records)
        }
        
        # Type breakdown
        type_breakdown = {}
        for record in filtered_records:
            req_type = record.get('type_of_requirement', 'Unknown')
            type_breakdown[req_type] = type_breakdown.get(req_type, 0) + 1
        
        # Phase breakdown
        phase_breakdown = {}
        for record in filtered_records:
            phase = record.get('phase', 'Unknown')
            phase_breakdown[phase] = phase_breakdown.get(phase, 0) + 1
        
        # Round breakdown
        round_breakdown = {}
        for record in filtered_records:
            current_round = record.get('current_round', 0)
            round_key = f"Round {current_round}"
            round_breakdown[round_key] = round_breakdown.get(round_key, 0) + 1
        
        return {
            'total_records': len(filtered_records),
            'unique_trials': unique_trials,
            'total_requirements': total_requirements,
            'total_failures': total_failures,
            'avg_defect_density': round(avg_defect_density, 2),
            'failure_reasons': failure_reasons,
            'type_breakdown': type_breakdown,
            'phase_breakdown': phase_breakdown,
            'round_breakdown': round_breakdown
        }

    def _empty_statistics(self) -> Dict:
        """Return empty statistics"""
        return {
            'total_records': 0,
            'unique_trials': 0,  # ✅ NEW
            'total_failures': 0,
            'total_requirements': 0,
            'avg_defect_density': 0.0,
            'failure_reasons': {},
            'type_breakdown': {},
            'phase_breakdown': {},
            'round_breakdown': {}  # ✅ NEW
        }
    
    def get_unique_values(self, field: str) -> List[str]:
        """Get unique values for a field (for filters)"""
        records = self.get_all_records()
        values = set(r.get(field) for r in records if field in r and r.get(field))
        return sorted(list(values))