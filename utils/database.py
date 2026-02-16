# utils/database.py
"""
Database operations for JSON file storage
Handles all data persistence operations
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

from config import (
    USERS_FILE, 
    ALLOCATIONS_FILE, 
    UAT_RECORDS_FILE, 
    AUDIT_LOGS_FILE,
    EMAIL_CONFIG_FILE, 
    PENDING_USERS_FILE, 
    PASSWORD_RESET_FILE,
    TRAIL_DOCUMENTS_FILE,
    CHANGE_REQUESTS_FILE,
    DEFAULT_SUPERUSER, 
    DEFAULT_EMAIL_CONFIG
)
from utils.auth import hash_password

# ==================== GENERIC FILE OPERATIONS ====================

# utils/database.py
# REPLACE load_json and save_json functions

def load_json(filepath: str, default: Any = None) -> Any:
    """Load JSON file with simple protection check"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # ✅ SIMPLE: Just log to file, no circular dependency
            try:
                from utils.data_protection import data_protection
                data_protection.log_access_simple("read", os.path.basename(filepath))
            except:
                pass  # Don't break if logging fails
            
            return data
        
        return default if default is not None else {}
    
    except json.JSONDecodeError as e:
        print(f"JSON decode error in {filepath}: {e}")
        return default if default is not None else {}
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return default if default is not None else {}


def save_json(filepath: str, data: Any) -> bool:
    """Save data to JSON file with simple protection"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        # ✅ SIMPLE: Just log to file, no circular dependency
        try:
            from utils.data_protection import data_protection
            data_protection.log_access_simple("write", os.path.basename(filepath))
        except:
            pass  # Don't break if logging fails
        
        return True
    
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        return False

# ==================== USERS ====================

def initialize_users_file():
    """Initialize users file with default superuser"""
    if not os.path.exists(USERS_FILE):
        default_users = {
            DEFAULT_SUPERUSER["username"]: {
                "password": hash_password(DEFAULT_SUPERUSER["password"]),
                "email": DEFAULT_SUPERUSER["email"],
                "role": DEFAULT_SUPERUSER["role"],
                "status": "active",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        save_json(USERS_FILE, default_users)

def load_users() -> Dict:
    """Load users from file"""
    initialize_users_file()
    return load_json(USERS_FILE, {})

def save_users(users: Dict) -> bool:
    """Save users to file"""
    return save_json(USERS_FILE, users)

def get_user(username: str) -> Optional[Dict]:
    """Get specific user"""
    users = load_users()
    return users.get(username)

def user_exists(username: str) -> bool:
    """Check if user exists"""
    return username in load_users()

# ==================== ALLOCATIONS ====================

def initialize_allocations_file():
    """Initialize allocations file"""
    if not os.path.exists(ALLOCATIONS_FILE):
        save_json(ALLOCATIONS_FILE, [])

def load_allocations() -> List:
    """Load all allocations (includes UAT records for backward compatibility)"""
    initialize_allocations_file()
    return load_json(ALLOCATIONS_FILE, [])

def save_allocations(allocations: List) -> bool:
    """Save allocations to file"""
    return save_json(ALLOCATIONS_FILE, allocations)

def get_allocation_records() -> List:
    """Get only allocation records (not UAT)"""
    all_data = load_allocations()
    return [item for item in all_data if item.get('record_type') != 'uat']

def add_allocation(allocation: Dict) -> bool:
    """Add new allocation"""
    allocations = load_allocations()
    allocation['id'] = datetime.now().strftime("%Y%m%d%H%M%S")
    allocation['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    allocation['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    allocations.append(allocation)
    return save_allocations(allocations)

def update_allocation(allocation_id: str, updated_data: Dict) -> bool:
    """Update existing allocation"""
    allocations = load_allocations()
    for i, alloc in enumerate(allocations):
        if alloc.get('id') == allocation_id:
            allocations[i].update(updated_data)
            allocations[i]['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return save_allocations(allocations)
    return False

def delete_allocation(allocation_id: str) -> bool:
    """Delete allocation"""
    allocations = load_allocations()
    allocations = [a for a in allocations if a.get('id') != allocation_id]
    return save_allocations(allocations)

# ==================== UAT RECORDS ====================

def initialize_uat_records_file():
    """Initialize UAT records file"""
    if not os.path.exists(UAT_RECORDS_FILE):
        save_json(UAT_RECORDS_FILE, [])

def load_uat_records() -> List:
    """Load UAT records from dedicated file or allocations file (backward compatible)"""
    if os.path.exists(UAT_RECORDS_FILE):
        return load_json(UAT_RECORDS_FILE, [])
    else:
        all_data = load_allocations()
        return [item for item in all_data if item.get('record_type') == 'uat']

def save_uat_records(uat_records: List) -> bool:
    """Save UAT records"""
    if os.path.exists(UAT_RECORDS_FILE):
        return save_json(UAT_RECORDS_FILE, uat_records)
    else:
        all_data = load_allocations()
        all_data = [item for item in all_data if item.get('record_type') != 'uat']
        all_data.extend(uat_records)
        return save_allocations(all_data)

def add_uat_record(uat_record: Dict) -> bool:
    """Add new UAT record"""
    uat_records = load_uat_records()
    uat_record['id'] = datetime.now().strftime("%Y%m%d%H%M%S")
    uat_record['record_type'] = 'uat'
    uat_record['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    uat_record['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    uat_records.append(uat_record)
    return save_uat_records(uat_records)

def update_uat_record(uat_id: str, updated_data: Dict) -> bool:
    """Update existing UAT record"""
    uat_records = load_uat_records()
    for i, uat in enumerate(uat_records):
        if uat.get('id') == uat_id:
            uat_records[i].update(updated_data)
            uat_records[i]['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return save_uat_records(uat_records)
    return False

def delete_uat_record(uat_id: str) -> bool:
    """Delete UAT record"""
    uat_records = load_uat_records()
    uat_records = [u for u in uat_records if u.get('id') != uat_id]
    return save_uat_records(uat_records)

def get_uat_record(uat_id: str) -> Optional[Dict]:
    """Get specific UAT record"""
    uat_records = load_uat_records()
    for uat in uat_records:
        if uat.get('id') == uat_id:
            return uat
    return None

# ==================== AUDIT LOGS ====================

def initialize_audit_logs_file():
    """Initialize audit logs file"""
    if not os.path.exists(AUDIT_LOGS_FILE):
        save_json(AUDIT_LOGS_FILE, [])

def load_audit_logs() -> List:
    """Load audit logs"""
    initialize_audit_logs_file()
    return load_json(AUDIT_LOGS_FILE, [])

def save_audit_logs(logs: List) -> bool:
    """Save audit logs"""
    return save_json(AUDIT_LOGS_FILE, logs)

def add_audit_log(log: Dict) -> bool:
    """Add new audit log"""
    logs = load_audit_logs()
    log['id'] = datetime.now().strftime("%Y%m%d%H%M%S%f")
    log['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logs.append(log)
    return save_audit_logs(logs)

# ==================== EMAIL CONFIG ====================

def initialize_email_config():
    """Initialize email configuration file"""
    if not os.path.exists(EMAIL_CONFIG_FILE):
        save_json(EMAIL_CONFIG_FILE, DEFAULT_EMAIL_CONFIG)

def load_email_config() -> Dict:
    """Load email configuration"""
    initialize_email_config()
    return load_json(EMAIL_CONFIG_FILE, DEFAULT_EMAIL_CONFIG)

def save_email_config(config: Dict) -> bool:
    """Save email configuration"""
    return save_json(EMAIL_CONFIG_FILE, config)

# ==================== PENDING USERS ====================

def initialize_pending_users_file():
    """Initialize pending users file"""
    if not os.path.exists(PENDING_USERS_FILE):
        save_json(PENDING_USERS_FILE, [])

def load_pending_users() -> List:
    """Load pending users"""
    initialize_pending_users_file()
    return load_json(PENDING_USERS_FILE, [])

def save_pending_users(pending_users: List) -> bool:
    """Save pending users"""
    return save_json(PENDING_USERS_FILE, pending_users)

def add_pending_user(user: Dict) -> bool:
    """Add pending user"""
    pending_users = load_pending_users()
    user['requested_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pending_users.append(user)
    return save_pending_users(pending_users)

def remove_pending_user(username: str) -> bool:
    """Remove pending user"""
    pending_users = load_pending_users()
    pending_users = [u for u in pending_users if u.get('username') != username]
    return save_pending_users(pending_users)

# ==================== PASSWORD RESET ====================

def initialize_password_reset_file():
    """Initialize password reset file"""
    if not os.path.exists(PASSWORD_RESET_FILE):
        save_json(PASSWORD_RESET_FILE, [])

def load_password_reset_requests() -> List:
    """Load password reset requests"""
    initialize_password_reset_file()
    return load_json(PASSWORD_RESET_FILE, [])

def save_password_reset_requests(requests: List) -> bool:
    """Save password reset requests"""
    return save_json(PASSWORD_RESET_FILE, requests)

def add_password_reset_request(request: Dict) -> bool:
    """Add password reset request"""
    requests = load_password_reset_requests()
    request['id'] = datetime.now().strftime("%Y%m%d%H%M%S")
    request['requested_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    request['status'] = 'pending'
    requests.append(request)
    return save_password_reset_requests(requests)

# ==================== TRAIL DOCUMENTS ====================

def initialize_trail_documents_file():
    """Initialize trail documents file"""
    if not os.path.exists(TRAIL_DOCUMENTS_FILE):
        save_json(TRAIL_DOCUMENTS_FILE, [])

def load_trail_documents() -> List:
    """Load trail documents"""
    initialize_trail_documents_file()
    return load_json(TRAIL_DOCUMENTS_FILE, [])

def save_trail_documents(documents: List) -> bool:
    """Save trail documents"""
    return save_json(TRAIL_DOCUMENTS_FILE, documents)

def add_trail_document(document: Dict) -> bool:
    """Add new trail document"""
    documents = load_trail_documents()
    document['id'] = datetime.now().strftime("%Y%m%d%H%M%S")
    document['created_by'] = document.get('created_by', '')
    document['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    document['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    documents.append(document)
    return save_trail_documents(documents)

def update_trail_document(doc_id: str, updated_data: Dict) -> bool:
    """Update existing trail document"""
    documents = load_trail_documents()
    for i, doc in enumerate(documents):
        if doc.get('id') == doc_id:
            documents[i].update(updated_data)
            documents[i]['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return save_trail_documents(documents)
    return False

def delete_trail_document(doc_id: str) -> bool:
    """Delete trail document"""
    documents = load_trail_documents()
    original_length = len(documents)
    documents = [d for d in documents if d.get('id') != doc_id]
    if len(documents) < original_length:
        return save_trail_documents(documents)
    return False

def get_trail_document(doc_id: str) -> Optional[Dict]:
    """Get specific trail document"""
    documents = load_trail_documents()
    for doc in documents:
        if doc.get('id') == doc_id:
            return doc
    return None

# ==================== CHANGE REQUESTS ====================

def initialize_change_requests_file():
    """Initialize change requests file"""
    if not os.path.exists(CHANGE_REQUESTS_FILE):
        save_json(CHANGE_REQUESTS_FILE, [])

def load_change_requests() -> List:
    """Load change requests"""
    initialize_change_requests_file()
    return load_json(CHANGE_REQUESTS_FILE, [])

def save_change_requests(change_requests: List) -> bool:
    """Save change requests"""
    return save_json(CHANGE_REQUESTS_FILE, change_requests)

def add_change_request(change_request: Dict) -> bool:
    """Add new change request"""
    try:
        change_requests = load_change_requests()
        change_request['id'] = datetime.now().strftime("%Y%m%d%H%M%S")
        change_request['created_by'] = change_request.get('created_by', '')
        change_request['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        change_request['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        change_requests.append(change_request)
        
        success = save_change_requests(change_requests)
        
        if success:
            print(f"✅ Change request saved successfully. ID: {change_request['id']}")
        else:
            print(f"❌ Failed to save change request")
        
        return success
    except Exception as e:
        print(f"❌ Error in add_change_request: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_change_request(cr_id: str, updated_data: Dict) -> bool:
    """Update existing change request"""
    change_requests = load_change_requests()
    for i, cr in enumerate(change_requests):
        if cr.get('id') == cr_id:
            change_requests[i].update(updated_data)
            change_requests[i]['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return save_change_requests(change_requests)
    return False

def delete_change_request(cr_id: str) -> bool:
    """Delete change request"""
    change_requests = load_change_requests()
    original_length = len(change_requests)
    change_requests = [cr for cr in change_requests if cr.get('id') != cr_id]
    if len(change_requests) < original_length:
        return save_change_requests(change_requests)
    return False

def get_change_request(cr_id: str) -> Optional[Dict]:
    """Get specific change request"""
    change_requests = load_change_requests()
    for cr in change_requests:
        if cr.get('id') == cr_id:
            return cr
    return None

# ==================== INITIALIZE ALL ====================

def initialize_all_files():
    """Initialize all data files"""
    initialize_users_file()
    initialize_allocations_file()
    initialize_uat_records_file()
    initialize_audit_logs_file()
    initialize_email_config()
    initialize_pending_users_file()
    initialize_password_reset_file()
    initialize_trail_documents_file()
    initialize_change_requests_file()  # ✅ NOW INCLUDED
    print("✅ All database files initialized successfully")