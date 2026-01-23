# pages/audit/audit_main.py
"""
Main Audit Trail page - Modern Professional UI
ROUTER for all audit features with enhanced visualizations
Includes Audit Reviewer dual-view functionality for Trail Documents
"""
import streamlit as st
from pages.audit.audit_viewer import render_audit_viewer_tab
from services.audit_service import log_page_view
from utils.auth import get_current_role
from datetime import datetime, timedelta

# Modern CSS Styling
def inject_audit_main_css():
    st.markdown("""
    <style>
    /* Import Modern Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        opacity: 0.95;
        font-weight: 400;
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 2px solid transparent;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    .feature-card:hover::before {
        transform: scaleX(1);
    }
    
    .feature-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .feature-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
        color: #1a202c;
    }
    
    .feature-description {
        color: #718096;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    
    .feature-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 1rem;
    }
    
    /* Role Badge */
    .role-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 30px;
        font-weight: 600;
        font-size: 0.95rem;
        box-shadow: 0 4px 12px rgba(245, 87, 108, 0.3);
        margin: 1rem 0;
    }
    
    .superuser-badge {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
    }
    
    .reviewer-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 4px 12px rgba(240, 147, 251, 0.3);
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
        border-left: 4px solid #00acc1;
        padding: 1.25rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        color: #006064;
        font-weight: 500;
    }
    
    .info-box-icon {
        font-size: 1.5rem;
        margin-right: 0.75rem;
        vertical-align: middle;
    }
    
    /* Back Button */
    .back-button {
        background: white;
        border: 2px solid #e2e8f0;
        color: #4a5568;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 2rem;
    }
    
    .back-button:hover {
        background: #f7fafc;
        border-color: #667eea;
        color: #667eea;
        transform: translateX(-4px);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f7fafc;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        background-color: transparent;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Metrics Grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card-main {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #667eea;
        transition: all 0.3s;
    }
    
    .metric-card-main:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
    }
    
    .metric-value-main {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }
    
    .metric-label-main {
        color: #718096;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Download Buttons */
    .download-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        border: 2px solid #dee2e6;
        transition: all 0.3s;
    }
    
    .download-card:hover {
        border-color: #667eea;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
    }
    
    .download-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)

def render_audit_page():
    """Main audit trail page with modern professional UI"""
    inject_audit_main_css()
    log_page_view("audit")
    
    current_role = get_current_role()
    is_audit_reviewer = st.session_state.get('is_audit_reviewer', False)
    
    # Hero Section
    st.markdown("""
    <div class="hero-section fade-in-up">
        <div class="hero-title">🔍 Audit & Trail Center</div>
        <div class="hero-subtitle">Complete visibility into system activities and document trails</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Back Button
    if st.button("⬅️ Back to Home", key="audit_back_home"):
        st.session_state.current_page = "home"
        st.rerun()
    
    # Show different views based on role AND audit reviewer status
    if current_role == "superuser":
        render_superuser_audit_menu()
    elif is_audit_reviewer:
        render_audit_reviewer_view()
    else:
        render_user_trail_documents()

def render_audit_reviewer_view():
    """Render dual-view interface for audit reviewers - Trail Documents Only"""
    
    # Reviewer Badge
    st.markdown("""
    <div style="text-align: center;">
        <span class="role-badge reviewer-badge">
            <span>🔍</span>
            <span>AUDIT REVIEWER ACCESS</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    st.success("""
    🔍 **Audit Reviewer Mode Active**
    
    You have special access to view all Trail Audit Documents across the system for compliance and review purposes.
    """)
    
    st.markdown("---")
    
    # Dual Tab Interface
    tab1, tab2 = st.tabs([
        "📄 My Documents",
        "🔍 All Trail Documents (Reviewer Mode)"
    ])
    
    # TAB 1: My Documents (Normal user view)
    with tab1:
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="font-weight: 700;">📄 My Trail Documents</h2>
            <p style="color: #718096;">Documents you created and manage</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if trail_documents module exists
        try:
            from pages.audit.trail_documents import render_trail_documents_page
            render_trail_documents_page()
        except ImportError:
            st.warning("⚠️ Trail Documents module not found.")
            st.info("""
            **Expected location:** `pages/audit/trail_documents.py`
            
            Trail documents are records that include:
            - Document approvals
            - Go-live dates
            - Test completion records
            - Compliance documentation
            """)
    
    # TAB 2: All Trail Documents (Reviewer view - read-only)
    with tab2:
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="font-weight: 700;">🔍 All Trail Documents</h2>
            <p style="color: #718096;">Complete trail documents across all users (Read-Only)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("👁️ **Reviewer Mode:** You can view all documents but cannot edit them")
        
        render_all_trail_documents_for_reviewer()

def render_all_trail_documents_for_reviewer():
    """Display all Trail Audit Documents for audit reviewers with proper filters"""
    from utils.database import load_users
    import pandas as pd
    import os
    import json
    
    # Load Trail Documents
    try:
        trail_docs_file = "data/trail_documents.json"
        
        if not os.path.exists(trail_docs_file):
            st.warning("⚠️ Trail Documents file not found")
            st.info("Trail documents will appear here once users start uploading them")
            
            # Show instructions
            st.markdown("""
            ### 📋 What are Trail Audit Documents?
            
            Trail Audit Documents are records created by Test Engineers that include:
            - **Trail ID** - Unique trail identifier
            - **Category** - Build or Change Request
            - **CR Number** - Change Request number (if applicable)
            - **UAT Round** - Testing round information
            - **TMF/Vault ID** - Document identifier
            - **Approval dates** - TE1, TE2, or CTDM approvals
            - **Go-live dates** - Production deployment dates
            
            These documents will be accessible here once users create them.
            
            **File location:** `data/trail_documents.json`
            """)
            return
        
        # Load trail documents
        with open(trail_docs_file, 'r') as f:
            trail_docs = json.load(f)
        
        if not trail_docs or len(trail_docs) == 0:
            st.info("📭 No trail documents available yet")
            st.caption("Documents will appear here once users create them")
            return
        
        users = load_users()
        
    except json.JSONDecodeError:
        st.error("❌ Error: Trail documents file is corrupted")
        st.info("Please check the JSON format in `data/trail_documents.json`")
        return
    except Exception as e:
        st.error(f"❌ Error loading trail documents: {e}")
        return
    
    # FILTERS SECTION
    st.markdown("#### 🔍 Filter Options")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Trail ID filter (dropdown)
        all_trails = ["All"] + sorted(list(set(doc.get('trail', 'N/A') for doc in trail_docs if doc.get('trail'))))
        selected_trail = st.selectbox(
            "Filter by Trail ID",
            options=all_trails,
            key="reviewer_trail_filter"
        )
    
    with col2:
        # Category filter
        selected_category = st.selectbox(
            "Filter by Category",
            options=["All", "Build", "Change Request"],
            key="reviewer_category_filter"
        )
    
    with col3:
        # CR Number filter - Only show if Change Request selected or All
        if selected_category in ["All", "Change Request"]:
            all_cr_numbers = ["All"] + sorted(list(set(
                doc.get('cr_number', 'N/A') 
                for doc in trail_docs 
                if doc.get('cr_number') and doc.get('category') == 'Change Request'
            )))
            selected_cr_number = st.selectbox(
                "Filter by CR Number",
                options=all_cr_numbers,
                key="reviewer_cr_filter"
            )
        else:
            selected_cr_number = "All"
            st.selectbox(
                "Filter by CR Number",
                options=["All"],
                disabled=True,
                key="reviewer_cr_filter_disabled",
                help="Available only for Change Request category"
            )
    
    with col4:
        # UAT Round filter
        all_uat_rounds = ["All"] + sorted(list(set(doc.get('uat_round', 'N/A') for doc in trail_docs if doc.get('uat_round'))))
        selected_uat_round = st.selectbox(
            "Filter by UAT Round",
            options=all_uat_rounds,
            key="reviewer_uat_filter"
        )
    
    # Additional Quick Search Row
    st.markdown("##### 🔎 Quick Search")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_trail = st.text_input(
            "Search Trail ID",
            placeholder="Type to search...",
            key="reviewer_search_trail"
        )
    
    with col2:
        search_doc_name = st.text_input(
            "Search Document Name",
            placeholder="Type to search...",
            key="reviewer_search_doc"
        )
    
    with col3:
        search_tmf = st.text_input(
            "Search TMF/Vault ID",
            placeholder="Type to search...",
            key="reviewer_search_tmf"
        )
    
    # Apply filters
    filtered_docs = trail_docs.copy()
    
    # Filter by Trail ID (dropdown)
    if selected_trail != "All":
        filtered_docs = [doc for doc in filtered_docs if doc.get('trail') == selected_trail]
    
    # Filter by Category
    if selected_category != "All":
        filtered_docs = [doc for doc in filtered_docs if doc.get('category') == selected_category]
    
    # Filter by CR Number
    if selected_cr_number != "All":
        filtered_docs = [doc for doc in filtered_docs if doc.get('cr_number') == selected_cr_number]
    
    # Filter by UAT Round (dropdown)
    if selected_uat_round != "All":
        filtered_docs = [doc for doc in filtered_docs if doc.get('uat_round') == selected_uat_round]
    
    # Text search filters (case-insensitive, partial match)
    if search_trail:
        search_trail_lower = search_trail.lower()
        filtered_docs = [doc for doc in filtered_docs if search_trail_lower in doc.get('trail', '').lower()]
    
    if search_doc_name:
        search_doc_lower = search_doc_name.lower()
        filtered_docs = [doc for doc in filtered_docs if search_doc_lower in doc.get('document_name', '').lower()]
    
    if search_tmf:
        search_tmf_lower = search_tmf.lower()
        filtered_docs = [doc for doc in filtered_docs if search_tmf_lower in doc.get('tmf_vault_id', '').lower()]
    
    # Clear filters button
    col_clear1, col_clear2 = st.columns([1, 5])
    with col_clear1:
        if st.button("🔄 Clear All Filters", use_container_width=True, key="reviewer_clear_filters_btn"):
            for key in list(st.session_state.keys()):
                if key.startswith('reviewer_'):
                    del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # Display Statistics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Documents", len(filtered_docs))
    
    with col2:
        unique_users_count = len(set(doc.get('created_by', 'Unknown') for doc in filtered_docs))
        st.metric("Unique Users", unique_users_count)
    
    with col3:
        build_count = len([doc for doc in filtered_docs if doc.get('category') == 'Build'])
        st.metric("Build", build_count)
    
    with col4:
        cr_count = len([doc for doc in filtered_docs if doc.get('category') == 'Change Request'])
        st.metric("Change Request", cr_count)
    
    with col5:
        te_doc_count = len([doc for doc in filtered_docs if doc.get('te_document') == 'Yes'])
        st.metric("TE Documents", te_doc_count)
    
    st.markdown("---")
    
    # ✅ TABULAR DISPLAY
    st.markdown("#### 📋 Trail Document Records")
    
    if filtered_docs:
        # Sort by created date (newest first)
        filtered_docs_sorted = sorted(
            filtered_docs, 
            key=lambda x: x.get('created_at', ''), 
            reverse=True
        )
        
        # Pagination
        items_per_page = 20
        total_pages = max(1, (len(filtered_docs_sorted) + items_per_page - 1) // items_per_page)
        
        col_page, col_info = st.columns([1, 3])
        
        with col_page:
            page = st.selectbox(
                "Page",
                range(1, total_pages + 1),
                key="reviewer_pagination"
            )
        
        with col_info:
            st.info(f"📊 Showing page {page} of {total_pages} ({len(filtered_docs_sorted)} total documents)")
        
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(filtered_docs_sorted))
        page_docs = filtered_docs_sorted[start_idx:end_idx]
        
        # Prepare data for table
        table_data = []
        for idx, doc in enumerate(page_docs):
            # Build category display
            category = doc.get('category', 'N/A')
            cr_number = doc.get('cr_number', '')
            category_display = f"{category} - {cr_number}" if cr_number else category
            
            # Get approval date based on TE Document
            if doc.get('te_document') == 'Yes':
                approval_info = f"TE1: {doc.get('te1_approval_date', 'N/A')} | TE2: {doc.get('te2_approval_date', 'N/A')}"
            else:
                approval_info = f"CTDM: {doc.get('ctdm_approval_date', 'N/A')}"
            
            table_data.append({
                '#': start_idx + idx + 1,
                'Trail ID': doc.get('trail', 'N/A'),
                'Category': category_display,
                'TE1': doc.get('te1', 'N/A'),
                'TE2': doc.get('te2', 'N/A'),
                'Document Name': doc.get('document_name', 'N/A'),
                'TE Doc': doc.get('te_document', 'N/A'),
                'UAT Round': doc.get('uat_round', 'N/A'),
                'TMF/Vault ID': doc.get('tmf_vault_id', 'N/A'),
                'Approval Dates': approval_info,
                'Go-Live': doc.get('go_live_date', 'N/A'),
                'Created By': doc.get('created_by', 'N/A'),
                'Created At': doc.get('created_at', 'N/A')[:10] if doc.get('created_at') else 'N/A'
            })
        
        # Create DataFrame
        df = pd.DataFrame(table_data)
        
        # Display as interactive table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "#": st.column_config.NumberColumn(
                    "#",
                    width="small",
                ),
                "Trail ID": st.column_config.TextColumn(
                    "Trail ID",
                    width="medium",
                ),
                "Category": st.column_config.TextColumn(
                    "Category",
                    width="medium",
                ),
                "Document Name": st.column_config.TextColumn(
                    "Document Name",
                    width="large",
                ),
                "TMF/Vault ID": st.column_config.TextColumn(
                    "TMF/Vault ID",
                    width="medium",
                ),
                "UAT Round": st.column_config.TextColumn(
                    "UAT Round",
                    width="small",
                ),
            }
        )
        
        # Option to view detailed information for selected document
        st.markdown("---")
        st.markdown("##### 🔍 View Detailed Information")
        
        # Select document by TMF/Vault ID
        tmf_ids_list = [doc.get('tmf_vault_id', 'N/A') for doc in page_docs]
        selected_tmf = st.selectbox(
            "Select document by TMF/Vault ID to view details:",
            options=["- Select a document -"] + tmf_ids_list,
            key="reviewer_select_detail_view"
        )
        
        if selected_tmf and selected_tmf != "- Select a document -":
            # Find the selected document
            selected_doc = next((doc for doc in page_docs if doc.get('tmf_vault_id') == selected_tmf), None)
            
            if selected_doc:
                st.markdown("---")
                
                # Display title with emojis
                trail = selected_doc.get('trail', 'N/A')
                category = selected_doc.get('category', 'N/A')
                doc_name = selected_doc.get('document_name', 'N/A')
                category_emoji = "🏗️" if category == 'Build' else "🔄"
                te_emoji = "✅" if selected_doc.get('te_document') == 'Yes' else "📄"
                
                st.markdown(f"### {category_emoji} {te_emoji} {doc_name}")
                st.caption(f"Trail: {trail} | Category: {category}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📄 Document Information**")
                    st.write(f"**Trail ID:** {trail}")
                    st.write(f"**Category:** {category_emoji} {category}")
                    
                    cr_number = selected_doc.get('cr_number', '')
                    if cr_number:
                        st.write(f"**CR Number:** {cr_number}")
                    
                    st.write(f"**Document Name:** {doc_name}")
                    st.write(f"**TE Document:** {te_emoji} {selected_doc.get('te_document', 'N/A')}")
                    st.write(f"**UAT Round:** {selected_doc.get('uat_round', 'N/A')}")
                    st.write(f"**TMF/Vault ID:** 🔑 {selected_doc.get('tmf_vault_id', 'N/A')}")
                
                with col2:
                    st.markdown("**📋 Details & Approvals**")
                    st.write(f"**TE1:** {selected_doc.get('te1', 'N/A')}")
                    st.write(f"**TE2:** {selected_doc.get('te2', 'N/A')}")
                    st.write(f"**Go-Live Date:** {selected_doc.get('go_live_date', 'N/A')}")
                    
                    st.markdown("**Approval Dates:**")
                    if selected_doc.get('te_document') == 'Yes':
                        st.write(f"- TE1 Approval: {selected_doc.get('te1_approval_date', 'N/A')}")
                        st.write(f"- TE2 Approval: {selected_doc.get('te2_approval_date', 'N/A')}")
                    else:
                        st.write(f"- CTDM Approval: {selected_doc.get('ctdm_approval_date', 'N/A')}")
                
                st.markdown("---")
                st.markdown("**📎 Metadata**")
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.write(f"**Created By:** {selected_doc.get('created_by', 'N/A')}")
                    st.write(f"**Created At:** {selected_doc.get('created_at', 'N/A')}")
                
                with col_b:
                    if selected_doc.get('updated_by'):
                        st.write(f"**Updated By:** {selected_doc.get('updated_by')}")
                        st.write(f"**Updated At:** {selected_doc.get('updated_at', 'N/A')}")
                
                # Show raw JSON data option
                if st.checkbox("Show raw JSON data", key="reviewer_show_raw_selected"):
                    st.json(selected_doc)
                
                st.caption("👁️ Read-only view (Reviewer Mode) - You cannot edit this document")
    
    else:
        st.info("📭 No documents match the selected filters")
        st.caption("Try adjusting your filter criteria")
    
    # Export Section
    st.markdown("---")
    st.markdown("#### 📥 Export Filtered Documents")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export to Excel", use_container_width=True, type="primary", key="reviewer_export_excel_btn"):
            try:
                import pandas as pd
                from io import BytesIO
                
                # Prepare data for export
                export_data = []
                for doc in filtered_docs:
                    category_display = doc.get('category', 'N/A')
                    if doc.get('cr_number'):
                        category_display = f"{category_display} - {doc.get('cr_number')}"
                    
                    export_data.append({
                        "Trail ID": doc.get('trail', 'N/A'),
                        "Category": category_display,
                        "CR Number": doc.get('cr_number', '') or 'N/A',
                        "TE1": doc.get('te1', 'N/A'),
                        "TE2": doc.get('te2', 'N/A'),
                        "Document Name": doc.get('document_name', 'N/A'),
                        "TE Document": doc.get('te_document', 'N/A'),
                        "UAT Round": doc.get('uat_round', 'N/A'),
                        "TMF/Vault ID": doc.get('tmf_vault_id', 'N/A'),
                        "TE1 Approval": doc.get('te1_approval_date', '') or 'N/A',
                        "TE2 Approval": doc.get('te2_approval_date', '') or 'N/A',
                        "CTDM Approval": doc.get('ctdm_approval_date', '') or 'N/A',
                        "Go Live Date": doc.get('go_live_date', 'N/A'),
                        "Created By": doc.get('created_by', 'N/A'),
                        "Created At": doc.get('created_at', 'N/A')
                    })
                
                df = pd.DataFrame(export_data)
                
                # Create Excel file
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Trail Documents')
                
                excel_data = output.getvalue()
                
                st.download_button(
                    label="📥 Download Excel File",
                    data=excel_data,
                    file_name=f"trail_documents_reviewer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="reviewer_download_excel_btn"
                )
                st.success("✅ Excel file ready for download!")
                
            except Exception as e:
                st.error(f"❌ Export failed: {e}")
                st.info("Make sure pandas and openpyxl are installed")
    
    with col2:
        if st.button("💾 Export to JSON", use_container_width=True, key="reviewer_export_json_btn"):
            import json
            
            json_data = json.dumps(filtered_docs, indent=2)
            
            st.download_button(
                label="📥 Download JSON File",
                data=json_data,
                file_name=f"trail_documents_reviewer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
                key="reviewer_download_json_btn"
            )
            st.success("✅ JSON file ready for download!")
    
    with col3:
        if st.button("📄 Export to CSV", use_container_width=True, key="reviewer_export_csv_btn"):
            try:
                import pandas as pd
                
                # Prepare data
                export_data = []
                for doc in filtered_docs:
                    category_display = doc.get('category', 'N/A')
                    if doc.get('cr_number'):
                        category_display = f"{category_display} - {doc.get('cr_number')}"
                    
                    export_data.append({
                        "Trail ID": doc.get('trail', 'N/A'),
                        "Category": category_display,
                        "Document Name": doc.get('document_name', 'N/A'),
                        "UAT Round": doc.get('uat_round', 'N/A'),
                        "TMF/Vault ID": doc.get('tmf_vault_id', 'N/A'),
                        "Go Live Date": doc.get('go_live_date', 'N/A'),
                        "Created By": doc.get('created_by', 'N/A'),
                        "Created At": doc.get('created_at', 'N/A')
                    })
                
                df = pd.DataFrame(export_data)
                csv_data = df.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download CSV File",
                    data=csv_data,
                    file_name=f"trail_documents_reviewer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="reviewer_download_csv_btn"
                )
                st.success("✅ CSV file ready for download!")
                
            except Exception as e:
                st.error(f"❌ Export failed: {e}")

def render_superuser_audit_menu():
    """Render modern menu for superuser with both options"""
    
    # Role Badge
    st.markdown("""
    <div style="text-align: center;">
        <span class="role-badge superuser-badge">
            <span>👑</span>
            <span>SUPER USER ACCESS</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box fade-in-up">
        <span class="info-box-icon">✨</span>
        <strong>Full Access Granted:</strong> You have complete access to System Audit Logs and Trail Audit Documents
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Feature Cards
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="feature-card fade-in-up">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">System Audit Logs</div>
            <div class="feature-description">
                Monitor all system activities, security events, and user actions in real-time.
                Advanced analytics and comprehensive reporting.
            </div>
            <span class="feature-badge">🔒 Security & Monitoring</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Access System Audit", key="system_audit_btn", use_container_width=True, type="primary"):
            st.session_state.audit_view = "system_logs"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="feature-card fade-in-up" style="animation-delay: 0.1s;">
            <div class="feature-icon">📋</div>
            <div class="feature-title">Trail Audit Documents</div>
            <div class="feature-description">
                Track test engineer document approvals, go-live dates, and compliance records.
                Streamlined workflow management.
            </div>
            <span class="feature-badge">📊 Document Tracking</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📁 Manage Trail Documents", key="trail_docs_btn", use_container_width=True, type="primary"):
            st.session_state.audit_view = "trail_documents"
            st.rerun()
    
    st.markdown("---")
    
    # Show selected view
    audit_view = st.session_state.get('audit_view', None)
    
    if audit_view == "system_logs":
        render_system_audit_logs()
    elif audit_view == "trail_documents":
        try:
            from pages.audit.trail_documents import render_trail_documents_page
            render_trail_documents_page()
        except ImportError:
            st.error("Trail Documents module not found")

def render_user_trail_documents():
    """Render trail documents with role-based styling"""
    try:
        from pages.audit.trail_documents import render_trail_documents_page
    except ImportError:
        st.error("Trail Documents module not found at pages/audit/trail_documents.py")
        return
    
    current_role = get_current_role()
    
    # Role-based badge and message
    role_config = {
        "admin": {
            "emoji": "👨‍💼",
            "title": "ADMIN ACCESS",
            "message": "Full management access to Trail Audit Documents",
            "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        },
        "manager": {
            "emoji": "👔",
            "title": "MANAGER ACCESS",
            "message": "View and manage team Trail Audit Documents",
            "gradient": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
        },
        "user": {
            "emoji": "👤",
            "title": "USER ACCESS",
            "message": "View and manage your Trail Audit Documents",
            "gradient": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
        }
    }
    
    config = role_config.get(current_role, role_config["user"])
    
    st.markdown(f"""
    <div style="text-align: center;">
        <span class="role-badge" style="background: {config['gradient']};">
            <span>{config['emoji']}</span>
            <span>{config['title']}</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="info-box fade-in-up">
        <span class="info-box-icon">📋</span>
        <strong>{config['message']}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Directly show trail documents page
    render_trail_documents_page()

def render_system_audit_logs():
    """Render system audit logs with modern tabs"""
    
    # Header with back button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("⬅️ Back", key="back_to_audit_menu"):
            st.session_state.audit_view = None
            st.rerun()
    
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h1 style="font-size: 2.5rem; font-weight: 800; 
                   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;">
            🔍 System Audit Logs
        </h1>
        <p style="color: #718096; font-size: 1.1rem; margin-top: 0.5rem;">
            Complete system activity monitoring and security analytics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Modern tabs
    tab1, tab2, tab3 = st.tabs([
        "📋 Activity Monitor",
        "📊 Analytics Dashboard", 
        "📥 Export & Reports"
    ])
    
    with tab1:
        render_audit_viewer_tab()
    
    with tab2:
        render_audit_analytics_tab()
    
    with tab3:
        render_audit_export_tab()

def render_audit_analytics_tab():
    """Render modern audit analytics dashboard"""
    from services.audit_service import get_audit_statistics, load_audit_logs
    from components.charts import render_pie_chart, render_bar_chart
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="font-weight: 700;">📊 Analytics Dashboard</h2>
        <p style="color: #718096;">Real-time insights and activity trends</p>
    </div>
    """, unsafe_allow_html=True)
    
    logs = load_audit_logs()
    
    if logs:
        stats = get_audit_statistics(logs)
        
        # Modern Metrics Grid
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            ("Total Activities", stats.get('total', 0), "📊", "#667eea"),
            ("Unique Users", len(stats.get('by_user', {})), "👥", "#f093fb"),
            ("Action Types", len(stats.get('by_action', {})), "⚡", "#4facfe"),
            ("Active Modules", len(stats.get('by_module', {})), "📦", "#43e97b")
        ]
        
        for col, (label, value, emoji, color) in zip([col1, col2, col3, col4], metrics):
            with col:
                st.markdown(f"""
                <div class="metric-card-main">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{emoji}</div>
                    <div class="metric-value-main">{value}</div>
                    <div class="metric-label-main">{label}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Charts Section
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Action Distribution")
            if stats.get('by_action'):
                render_pie_chart(stats['by_action'], "Action Types")
        
        with col2:
            st.markdown("#### 📦 Module Activity")
            if stats.get('by_module'):
                render_pie_chart(stats['by_module'], "Modules")
        
        st.markdown("---")
        
        # User Activity Bar Chart
        st.markdown("#### 👥 User Activity Breakdown")
        if stats.get('by_user'):
            render_bar_chart(stats['by_user'], "Activity by User")
        
        st.markdown("---")
        
        # Daily Activity Timeline
        st.markdown("#### 📅 Daily Activity Timeline")
        if stats.get('by_date'):
            render_bar_chart(stats['by_date'], "Activity by Date")
    else:
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 5rem; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #718096;">No Analytics Data Available</h3>
            <p style="color: #a0aec0;">Activity data will appear here as you use the system</p>
        </div>
        """, unsafe_allow_html=True)

def render_audit_export_tab():
    """Render modern export interface"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="font-weight: 700;">📥 Export & Reports</h2>
        <p style="color: #718096;">Download audit logs in your preferred format</p>
    </div>
    """, unsafe_allow_html=True)
    
    from services.audit_service import load_audit_logs
    from utils.excel_handler import convert_to_excel
    
    logs = load_audit_logs()
    
    if logs:
        # Stats
        st.markdown(f"""
        <div class="info-box" style="text-align: center;">
            <span style="font-size: 2rem; font-weight: 700;">{len(logs)}</span>
            <div style="color: #006064; margin-top: 0.5rem;">Total logs available for export</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Export Cards
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown("""
            <div class="download-card">
                <div class="download-icon">📊</div>
                <h3 style="margin-bottom: 0.5rem; color: #1a202c;">Excel Format</h3>
                <p style="color: #718096; font-size: 0.9rem;">
                    Download as spreadsheet for analysis
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            excel_data = convert_to_excel(logs, "Audit Logs")
            if excel_data:
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary"
                )
        
        with col2:
            st.markdown("""
            <div class="download-card">
                <div class="download-icon">💾</div>
                <h3 style="margin-bottom: 0.5rem; color: #1a202c;">JSON Format</h3>
                <p style="color: #718096; font-size: 0.9rem;">
                    Raw data for system integration
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            import json
            json_data = json.dumps(logs, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
                type="primary"
            )
    else:
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 5rem; margin-bottom: 1rem;">📭</div>
            <h3 style="color: #718096;">No Logs to Export</h3>
            <p style="color: #a0aec0;">Activity logs will be available for export once generated</p>
        </div>
        """, unsafe_allow_html=True)