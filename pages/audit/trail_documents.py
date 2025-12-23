# pages/audit/trail_documents.py
"""
Trail Audit Documents Management Page
With Category, Edit, Delete and Enhanced Filters
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database import (
    load_trail_documents, add_trail_document, update_trail_document, 
    delete_trail_document, get_trail_document
)
from utils.auth import get_current_user, get_current_role
from utils.excel_handler import convert_to_excel
from services.audit_service import log_audit

def render_trail_documents_page():
    """Main trail audit documents page"""
    st.title("📋 Trail Audit Documents")
    st.markdown("---")
    
    # Back button
    current_role = get_current_role()
    if current_role == "superuser":
        if st.button("⬅️ Back to Audit Menu", key="back_to_audit"):
            st.session_state.audit_view = None
            st.rerun()
    else:
        if st.button("⬅️ Back to Home", key="back_to_home"):
            st.session_state.current_page = "home"
            st.rerun()
    
    # Create tabs
    tab1, tab2 = st.tabs(["➕ Add Trail Audit Document", "📋 View Trail Audit Documents"])
    
    with tab1:
        render_add_trail_document()
    
    with tab2:
        render_view_trail_documents()

def render_add_trail_document():
    """Render add trail audit document form"""
    st.subheader("Add New Trail Audit Document")
    
    # Initialize session state
    if 'te_document_value' not in st.session_state:
        st.session_state.te_document_value = "No"
    if 'category_value' not in st.session_state:
        st.session_state.category_value = "Build"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Basic Information")
        
        trail = st.text_input(
            "Trail*",
            placeholder="e.g., TRL-2024-001",
            help="Enter trail identifier",
            key="trail_input"
        )
        
        # CATEGORY FIELD
        category = st.selectbox(
            "Category*",
            ["Build", "Change Request"],
            index=0 if st.session_state.category_value == "Build" else 1,
            help="Select category type",
            key="category_select"
        )
        
        st.session_state.category_value = category
        
        # CR NUMBER FIELD - Only visible if Change Request
        cr_number = ""
        if category == "Change Request":
            cr_number = st.text_input(
                "CR Number*",
                placeholder="e.g., CR001, CR-2024-001",
                help="Enter Change Request number",
                key="cr_number_input"
            )
        
        te1 = st.text_input(
            "TE1*",
            placeholder="Test Engineer 1 name",
            help="Enter TE1 name",
            key="te1_input"
        )
        
        te2 = st.text_input(
            "TE2*",
            placeholder="Test Engineer 2 name",
            help="Enter TE2 name",
            key="te2_input"
        )
        
        document_name = st.text_input(
            "Document Name*",
            placeholder="e.g., Test Plan v1.0",
            help="Enter document name",
            key="doc_name_input"
        )
    
    with col2:
        st.markdown("#### Document Details")
        
        # TE Document - Yes/No
        te_document = st.radio(
            "TE Document?*",
            ["Yes", "No"],
            index=1 if st.session_state.te_document_value == "No" else 0,
            help="Is this a TE document?",
            key="te_doc_radio",
            horizontal=True
        )
        
        st.session_state.te_document_value = te_document
        
        uat_round = st.text_input(
            "UAT Round*",
            placeholder="e.g., Round 1, UAT Phase 1",
            help="Enter UAT round",
            key="uat_round_input"
        )
        
        tmf_vault_id = st.text_input(
            "TMF/Vault ID*",
            placeholder="e.g., TMF-123456",
            help="Enter TMF or Vault ID",
            key="tmf_vault_input"
        )
        
        st.markdown("#### Approval Dates")
        
        # Conditional fields based on TE Document value
        te1_approval_date = None
        te2_approval_date = None
        ctdm_approval_date = None
        
        if te_document == "Yes":
            st.info("📋 TE Document = Yes → TE1 & TE2 Approval dates required")
            
            te1_approval_date = st.date_input(
                "TE1 Approval Date*",
                value=None,
                help="Required when TE Document = Yes",
                key="te1_approval_input"
            )
            
            te2_approval_date = st.date_input(
                "TE2 Approval Date*",
                value=None,
                help="Required when TE Document = Yes",
                key="te2_approval_input"
            )
        else:
            st.info("📋 TE Document = No → CTDM Approval date required")
            
            ctdm_approval_date = st.date_input(
                "CTDM Approval Date*",
                value=None,
                help="Required when TE Document = No",
                key="ctdm_approval_input"
            )
        
        go_live_date = st.date_input(
            "Go Live Date*",
            value=None,
            help="Document go-live date",
            key="go_live_input"
        )
    
    st.markdown("---")
    
    # Submit button
    if st.button("💾 Save Trail Audit Document", key="save_trail_doc_btn", use_container_width=True, type="primary"):
        # Validation
        errors = []
        
        if not trail or not trail.strip():
            errors.append("Trail is required")
        if not category:
            errors.append("Category is required")
        if category == "Change Request" and (not cr_number or not cr_number.strip()):
            errors.append("CR Number is required when Category is Change Request")
        if not te1 or not te1.strip():
            errors.append("TE1 is required")
        if not te2 or not te2.strip():
            errors.append("TE2 is required")
        if not document_name or not document_name.strip():
            errors.append("Document Name is required")
        if not uat_round or not uat_round.strip():
            errors.append("UAT Round is required")
        if not tmf_vault_id or not tmf_vault_id.strip():
            errors.append("TMF/Vault ID is required")
        if not go_live_date:
            errors.append("Go Live Date is required")
        
        # Conditional validation
        if te_document == "Yes":
            if not te1_approval_date:
                errors.append("TE1 Approval Date is required when TE Document = Yes")
            if not te2_approval_date:
                errors.append("TE2 Approval Date is required when TE Document = Yes")
        else:
            if not ctdm_approval_date:
                errors.append("CTDM Approval Date is required when TE Document = No")
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            # Create trail document record
            trail_document = {
                "trail": trail.strip(),
                "category": category,
                "cr_number": cr_number.strip() if cr_number else "",
                "te1": te1.strip(),
                "te2": te2.strip(),
                "document_name": document_name.strip(),
                "te_document": te_document,
                "uat_round": uat_round.strip(),
                "tmf_vault_id": tmf_vault_id.strip(),
                "te1_approval_date": te1_approval_date.strftime("%Y-%m-%d") if te1_approval_date else None,
                "te2_approval_date": te2_approval_date.strftime("%Y-%m-%d") if te2_approval_date else None,
                "ctdm_approval_date": ctdm_approval_date.strftime("%Y-%m-%d") if ctdm_approval_date else None,
                "go_live_date": go_live_date.strftime("%Y-%m-%d"),
                "created_by": get_current_user()
            }
            
            if add_trail_document(trail_document):
                st.success(f"✅ Trail Audit Document saved successfully for Trail: {trail}")
                
                # Log audit
                log_audit(
                    username=get_current_user(),
                    action="create",
                    category="trail_audit_documents",
                    entity_type="trail_audit_document",
                    entity_id=trail_document.get('id', ''),
                    details={"trail": trail, "category": category, "document_name": document_name}
                )
                
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Failed to save trail audit document")

def render_view_trail_documents():
    """Render view trail audit documents with enhanced filters"""
    st.subheader("Trail Audit Documents")
    
    # Load trail documents
    documents = load_trail_documents()
    
    # Filter based on role
    current_role = get_current_role()
    current_user = get_current_user()
    
    if current_role in ["admin", "manager", "superuser"]:
        filtered_docs = documents
        st.info(f"👨‍💼 {current_role.title()} View: Showing all trail audit documents")
    else:
        filtered_docs = [d for d in documents if d.get("created_by") == current_user]
        st.info(f"👤 User View: Showing only your trail audit documents")
    
    if filtered_docs:
        # Summary Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        total_docs = len(filtered_docs)
        te_docs = len([d for d in filtered_docs if d.get('te_document') == 'Yes'])
        build_docs = len([d for d in filtered_docs if d.get('category') == 'Build'])
        cr_docs = len([d for d in filtered_docs if d.get('category') == 'Change Request'])
        
        with col1:
            st.metric("Total Documents", total_docs)
        with col2:
            st.metric("TE Documents", te_docs)
        with col3:
            st.metric("Build", build_docs)
        with col4:
            st.metric("Change Request", cr_docs)
        
        st.markdown("---")
        
        # ENHANCED FILTERS
        st.subheader("🔍 Filters")
        
        # Row 1: Dropdown filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            trails = ["All"] + sorted(list(set([d.get('trail', 'N/A') for d in filtered_docs])))
            filter_trail_dropdown = st.selectbox(
                "Filter by Trail ID",
                trails,
                key="filter_trail_dropdown"
            )
        
        with col2:
            filter_category = st.selectbox(
                "Filter by Category",
                ["All", "Build", "Change Request"],
                key="filter_category"
            )
        
        with col3:
            uat_rounds = ["All"] + sorted(list(set([d.get('uat_round', 'N/A') for d in filtered_docs])))
            filter_uat_dropdown = st.selectbox(
                "Filter by UAT Round",
                uat_rounds,
                key="filter_uat_dropdown"
            )
        
        with col4:
            tmf_ids = ["All"] + sorted(list(set([d.get('tmf_vault_id', 'N/A') for d in filtered_docs])))
            filter_tmf_dropdown = st.selectbox(
                "Filter by TMF/Vault ID",
                tmf_ids,
                key="filter_tmf_dropdown"
            )
        
        # Row 2: Text input search filters
        st.markdown("##### 🔎 Quick Search (Type to filter)")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            filter_trail_text = st.text_input(
                "Search Trail ID",
                placeholder="Type trail ID...",
                key="filter_trail_text",
                help="Search by typing trail ID"
            )
        
        with col2:
            filter_doc_name = st.text_input(
                "Search Document Name",
                placeholder="Type document name...",
                key="filter_doc_name",
                help="Search by document name"
            )
        
        with col3:
            filter_uat_text = st.text_input(
                "Search UAT Round",
                placeholder="Type UAT round...",
                key="filter_uat_text",
                help="Search by UAT round"
            )
        
        with col4:
            filter_tmf_text = st.text_input(
                "Search TMF/Vault ID",
                placeholder="Type TMF/Vault ID...",
                key="filter_tmf_text",
                help="Search by TMF or Vault ID"
            )
        
        # Clear filters button
        col_clear1, col_clear2, col_clear3 = st.columns([1, 1, 4])
        with col_clear1:
            if st.button("🔄 Clear All Filters", use_container_width=True):
                for key in list(st.session_state.keys()):
                    if key.startswith('filter_'):
                        del st.session_state[key]
                st.rerun()
        
        with col_clear2:
            # Show active filters count
            active_filters = 0
            if filter_trail_dropdown != "All": active_filters += 1
            if filter_category != "All": active_filters += 1
            if filter_uat_dropdown != "All": active_filters += 1
            if filter_tmf_dropdown != "All": active_filters += 1
            if filter_trail_text: active_filters += 1
            if filter_doc_name: active_filters += 1
            if filter_uat_text: active_filters += 1
            if filter_tmf_text: active_filters += 1
            
            if active_filters > 0:
                st.info(f"🎯 {active_filters} filter(s) active")
        
        st.markdown("---")
        
        # Apply filters
        display_docs = apply_enhanced_filters(
            filtered_docs,
            filter_trail_dropdown,
            filter_trail_text,
            filter_category,
            filter_uat_dropdown,
            filter_uat_text,
            filter_tmf_dropdown,
            filter_tmf_text,
            filter_doc_name
        )
        
        # Showing count
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"### Showing {len(display_docs)} of {len(filtered_docs)} Trail Audit Documents 🔗")
        
        # Export to Excel - ONLY FOR ADMIN AND SUPERUSER
        with col3:
            if current_role in ["admin", "superuser"]:
                if display_docs:
                    excel_data = prepare_excel_data(display_docs)
                    excel_output = convert_to_excel(excel_data)
                    if excel_output:
                        st.download_button(
                            label="📥 Download Excel",
                            data=excel_output,
                            file_name=f"trail_audit_documents_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
            else:
                st.info("📥 Admin/Superuser only")
        
        st.markdown("---")
        
        # TABLE VIEW
        render_trail_documents_table(display_docs)
        
        st.markdown("---")
        
        # DETAILED VIEW
        st.subheader("📋 Detailed View")
        if display_docs:
            for doc in reversed(display_docs):
                render_document_card(doc, current_user, current_role)
        else:
            st.info("No documents match the selected filters")
    
    else:
        st.info("📝 No trail audit documents found. Add your first trail audit document in the 'Add Trail Audit Document' tab!")

def apply_enhanced_filters(documents, trail_dropdown, trail_text, category, 
                          uat_dropdown, uat_text, tmf_dropdown, tmf_text, doc_name):
    """Apply all filters including text search"""
    filtered = documents
    
    # Dropdown filters
    if trail_dropdown != "All":
        filtered = [d for d in filtered if d.get('trail') == trail_dropdown]
    
    if category != "All":
        filtered = [d for d in filtered if d.get('category') == category]
    
    if uat_dropdown != "All":
        filtered = [d for d in filtered if d.get('uat_round') == uat_dropdown]
    
    if tmf_dropdown != "All":
        filtered = [d for d in filtered if d.get('tmf_vault_id') == tmf_dropdown]
    
    # Text search filters (case-insensitive, partial match)
    if trail_text:
        trail_text_lower = trail_text.lower()
        filtered = [d for d in filtered if trail_text_lower in d.get('trail', '').lower()]
    
    if doc_name:
        doc_name_lower = doc_name.lower()
        filtered = [d for d in filtered if doc_name_lower in d.get('document_name', '').lower()]
    
    if uat_text:
        uat_text_lower = uat_text.lower()
        filtered = [d for d in filtered if uat_text_lower in d.get('uat_round', '').lower()]
    
    if tmf_text:
        tmf_text_lower = tmf_text.lower()
        filtered = [d for d in filtered if tmf_text_lower in d.get('tmf_vault_id', '').lower()]
    
    return filtered

def prepare_excel_data(documents):
    """Prepare data for Excel export"""
    excel_data = []
    for doc in documents:
        # Build category display
        category_display = doc.get('category', 'N/A')
        if doc.get('cr_number'):
            category_display = f"{category_display} - {doc.get('cr_number')}"
        
        excel_data.append({
            "Trail": doc.get('trail', 'N/A'),
            "TE1": doc.get('te1', 'N/A'),
            "TE2": doc.get('te2', 'N/A'),
            "Document Name": doc.get('document_name', 'N/A'),
            "Category": category_display,
            "TE Document": doc.get('te_document', 'N/A'),
            "UAT Round": doc.get('uat_round', 'N/A'),
            "TMF/Vault ID": doc.get('tmf_vault_id', 'N/A'),
            "TE1 Approval": doc.get('te1_approval_date', 'N/A') or 'N/A',
            "TE2 Approval": doc.get('te2_approval_date', 'N/A') or 'N/A',
            "CTDM Approval": doc.get('ctdm_approval_date', 'N/A') or 'N/A',
            "Go Live Date": doc.get('go_live_date', 'N/A'),
            "Created By": doc.get('created_by', 'N/A'),
            "Created At": doc.get('created_at', 'N/A')
        })
    return excel_data

def render_trail_documents_table(documents):
    """Render trail documents as a clean table"""
    if not documents:
        st.info("No documents to display")
        return
    
    # Prepare data for table
    table_data = []
    for doc in documents:
        # Build category display with CR number
        category = doc.get('category', 'N/A')
        cr_number = doc.get('cr_number', '')
        category_display = f"{category} - {cr_number}" if cr_number else category
        
        table_data.append({
            'trail_id': doc.get('trail', 'N/A'),
            'te1': doc.get('te1', 'N/A'),
            'te2': doc.get('te2', 'N/A'),
            'document_name': doc.get('document_name', 'N/A'),
            'category': category_display,
            'te_document': doc.get('te_document', 'N/A'),
            'uat_round': doc.get('uat_round', 'N/A'),
            'tmf_vault_id': doc.get('tmf_vault_id', 'N/A'),
            'go_live_date': doc.get('go_live_date', 'N/A'),
            'created_by': doc.get('created_by', 'N/A')
        })
    
    # Create DataFrame
    df = pd.DataFrame(table_data)
    
    # Rename columns for display
    df.columns = [
        'Trail ID',
        'TE1',
        'TE2',
        'Document Name',
        'Category',
        'TE Document',
        'UAT Round',
        'TMF/Vault ID',
        'Go Live Date',
        'Created By'
    ]
    
    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

def render_document_card(doc, current_user, current_role):
    """Render individual document card with edit/delete options"""
    # Category emoji
    category_emoji = "🏗️" if doc.get('category') == 'Build' else "🔄"
    te_doc_emoji = "✅" if doc.get('te_document') == 'Yes' else "📄"
    doc_id = doc.get('id')
    
    # Build display title
    trail = doc.get('trail', 'N/A')
    category = doc.get('category', 'N/A')
    cr_number = doc.get('cr_number', '')
    doc_name = doc.get('document_name', 'N/A')
    uat_round = doc.get('uat_round', 'N/A')
    
    # Add CR number to display if exists
    category_display = f"{category} - {cr_number}" if cr_number else category
    
    # Check if user can edit/delete
    can_edit = (current_user == doc.get('created_by')) or (current_role in ["admin", "superuser"])
    
    # Check if in edit mode
    edit_mode = st.session_state.get(f"edit_mode_{doc_id}", False)
    
    with st.expander(f"{category_emoji} {te_doc_emoji} [{trail}] - {category_display} - {doc_name} - {uat_round}", expanded=edit_mode):
        if edit_mode:
            # EDIT MODE
            render_edit_form(doc, current_user)
        else:
            # VIEW MODE
            render_document_view(doc, current_user, current_role, can_edit)

def render_document_view(doc, current_user, current_role, can_edit):
    """Render document in view mode"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Trail:** {doc.get('trail', 'N/A')}")
        
        category = doc.get('category', 'N/A')
        category_emoji = "🏗️" if category == 'Build' else "🔄"
        st.write(f"**Category:** {category_emoji} {category}")
        
        cr_number = doc.get('cr_number', '')
        if cr_number:
            st.write(f"**CR Number:** {cr_number}")
        
        st.write(f"**TE1:** {doc.get('te1', 'N/A')}")
        st.write(f"**TE2:** {doc.get('te2', 'N/A')}")
        st.write(f"**Document Name:** {doc.get('document_name', 'N/A')}")
        
        te_doc_emoji = "✅" if doc.get('te_document') == 'Yes' else "📄"
        st.write(f"**TE Document:** {te_doc_emoji} {doc.get('te_document', 'N/A')}")
    
    with col2:
        st.write(f"**UAT Round:** {doc.get('uat_round', 'N/A')}")
        st.write(f"**TMF/Vault ID:** {doc.get('tmf_vault_id', 'N/A')}")
        st.write(f"**Go Live Date:** {doc.get('go_live_date', 'N/A')}")
        
        st.markdown("#### Approval Dates")
        
        if doc.get('te_document') == 'Yes':
            st.write(f"**TE1 Approval:** {doc.get('te1_approval_date', 'N/A')}")
            st.write(f"**TE2 Approval:** {doc.get('te2_approval_date', 'N/A')}")
        else:
            st.write(f"**CTDM Approval:** {doc.get('ctdm_approval_date', 'N/A')}")
    
    st.markdown("---")
    st.caption(f"Created by: {doc.get('created_by', 'N/A')} | Created at: {doc.get('created_at', 'N/A')}")
    
    if doc.get('updated_at') and doc.get('updated_at') != doc.get('created_at'):
        st.caption(f"Last updated: {doc.get('updated_at', 'N/A')} by {doc.get('updated_by', 'N/A')}")
    
    # Action buttons
    if can_edit:
        st.markdown("---")
        col_edit, col_delete = st.columns(2)
        
        with col_edit:
            if st.button("✏️ Edit", key=f"edit_btn_{doc.get('id')}", use_container_width=True):
                st.session_state[f"edit_mode_{doc.get('id')}"] = True
                st.rerun()
        
        with col_delete:
            if st.button("🗑️ Delete", key=f"delete_trail_doc_{doc.get('id')}", use_container_width=True):
                if st.session_state.get(f"confirm_delete_trail_{doc.get('id')}", False):
                    if delete_trail_document(doc.get('id')):
                        st.success(f"✅ Trail audit document deleted")
                        
                        log_audit(
                            username=current_user,
                            action="delete",
                            category="trail_audit_documents",
                            entity_type="trail_audit_document",
                            entity_id=doc.get('id', ''),
                            details={"trail": doc.get('trail'), "category": doc.get('category'), "document_name": doc.get('document_name')}
                        )
                        
                        del st.session_state[f"confirm_delete_trail_{doc.get('id')}"]
                        st.rerun()
                else:
                    st.session_state[f"confirm_delete_trail_{doc.get('id')}"] = True
                    st.warning("⚠️ Click Delete again to confirm!")

def render_edit_form(doc, current_user):
    """Render edit form for document"""
    st.info("✏️ **Edit Mode** - Make your changes below")
    
    doc_id = doc.get('id')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Basic Information")
        
        trail = st.text_input(
            "Trail*",
            value=doc.get('trail', ''),
            key=f"edit_trail_{doc_id}"
        )
        
        category = st.selectbox(
            "Category*",
            ["Build", "Change Request"],
            index=0 if doc.get('category') == 'Build' else 1,
            key=f"edit_category_{doc_id}"
        )
        
        cr_number = ""
        if category == "Change Request":
            cr_number = st.text_input(
                "CR Number*",
                value=doc.get('cr_number', ''),
                placeholder="e.g., CR001",
                key=f"edit_cr_number_{doc_id}"
            )
        
        te1 = st.text_input(
            "TE1*",
            value=doc.get('te1', ''),
            key=f"edit_te1_{doc_id}"
        )
        
        te2 = st.text_input(
            "TE2*",
            value=doc.get('te2', ''),
            key=f"edit_te2_{doc_id}"
        )
        
        document_name = st.text_input(
            "Document Name*",
            value=doc.get('document_name', ''),
            key=f"edit_doc_name_{doc_id}"
        )
    
    with col2:
        st.markdown("#### Document Details")
        
        te_document = st.radio(
            "TE Document?*",
            ["Yes", "No"],
            index=0 if doc.get('te_document') == 'Yes' else 1,
            key=f"edit_te_doc_{doc_id}",
            horizontal=True
        )
        
        uat_round = st.text_input(
            "UAT Round*",
            value=doc.get('uat_round', ''),
            key=f"edit_uat_round_{doc_id}"
        )
        
        tmf_vault_id = st.text_input(
            "TMF/Vault ID*",
            value=doc.get('tmf_vault_id', ''),
            key=f"edit_tmf_{doc_id}"
        )
        
        st.markdown("#### Approval Dates")
        
        if te_document == "Yes":
            st.info("📋 TE Document = Yes → TE1 & TE2 Approval dates required")
            
            te1_approval = doc.get('te1_approval_date')
            te1_approval_date = st.date_input(
                "TE1 Approval Date*",
                value=datetime.strptime(te1_approval, "%Y-%m-%d").date() if te1_approval else None,
                key=f"edit_te1_approval_{doc_id}"
            )
            
            te2_approval = doc.get('te2_approval_date')
            te2_approval_date = st.date_input(
                "TE2 Approval Date*",
                value=datetime.strptime(te2_approval, "%Y-%m-%d").date() if te2_approval else None,
                key=f"edit_te2_approval_{doc_id}"
            )
            
            ctdm_approval_date = None
        else:
            st.info("📋 TE Document = No → CTDM Approval date required")
            
            ctdm_approval = doc.get('ctdm_approval_date')
            ctdm_approval_date = st.date_input(
                "CTDM Approval Date*",
                value=datetime.strptime(ctdm_approval, "%Y-%m-%d").date() if ctdm_approval else None,
                key=f"edit_ctdm_approval_{doc_id}"
            )
            
            te1_approval_date = None
            te2_approval_date = None
        
        go_live = doc.get('go_live_date')
        go_live_date = st.date_input(
            "Go Live Date*",
            value=datetime.strptime(go_live, "%Y-%m-%d").date() if go_live else None,
            key=f"edit_go_live_{doc_id}"
        )
    
    st.markdown("---")
    
    # Action buttons
    col_save, col_cancel = st.columns(2)
    
    with col_save:
        if st.button("💾 Save Changes", key=f"save_edit_{doc_id}", use_container_width=True, type="primary"):
            # Validation
            errors = []
            
            if not trail or not trail.strip():
                errors.append("Trail is required")
            if not category:
                errors.append("Category is required")
            if category == "Change Request" and (not cr_number or not cr_number.strip()):
                errors.append("CR Number is required when Category is Change Request")
            if not te1 or not te1.strip():
                errors.append("TE1 is required")
            if not te2 or not te2.strip():
                errors.append("TE2 is required")
            if not document_name or not document_name.strip():
                errors.append("Document Name is required")
            if not uat_round or not uat_round.strip():
                errors.append("UAT Round is required")
            if not tmf_vault_id or not tmf_vault_id.strip():
                errors.append("TMF/Vault ID is required")
            if not go_live_date:
                errors.append("Go Live Date is required")
            
            if te_document == "Yes":
                if not te1_approval_date:
                    errors.append("TE1 Approval Date is required")
                if not te2_approval_date:
                    errors.append("TE2 Approval Date is required")
            else:
                if not ctdm_approval_date:
                    errors.append("CTDM Approval Date is required")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Update document
                updated_data = {
                    "trail": trail.strip(),
                    "category": category,
                    "cr_number": cr_number.strip() if cr_number else "",
                    "te1": te1.strip(),
                    "te2": te2.strip(),
                    "document_name": document_name.strip(),
                    "te_document": te_document,
                    "uat_round": uat_round.strip(),
                    "tmf_vault_id": tmf_vault_id.strip(),
                    "te1_approval_date": te1_approval_date.strftime("%Y-%m-%d") if te1_approval_date else None,
                    "te2_approval_date": te2_approval_date.strftime("%Y-%m-%d") if te2_approval_date else None,
                    "ctdm_approval_date": ctdm_approval_date.strftime("%Y-%m-%d") if ctdm_approval_date else None,
                    "go_live_date": go_live_date.strftime("%Y-%m-%d"),
                    "updated_by": current_user
                }
                
                if update_trail_document(doc_id, updated_data):
                    st.success("✅ Trail Audit Document updated successfully!")
                    
                    log_audit(
                        username=current_user,
                        action="update",
                        category="trail_audit_documents",
                        entity_type="trail_audit_document",
                        entity_id=doc_id,
                        details={"trail": trail, "category": category, "document_name": document_name}
                    )
                    
                    del st.session_state[f"edit_mode_{doc_id}"]
                    st.rerun()
                else:
                    st.error("❌ Failed to update document")
    
    with col_cancel:
        if st.button("❌ Cancel", key=f"cancel_edit_{doc_id}", use_container_width=True):
            del st.session_state[f"edit_mode_{doc_id}"]
            st.rerun()