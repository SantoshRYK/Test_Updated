# ui/login.py
"""
Login, Register, and Forgot Password page
PROFESSIONAL LIGHT BACKGROUND WITH HEADER IMAGE
"""
import streamlit as st
from datetime import datetime
import base64
from pathlib import Path
from utils.auth import hash_password, verify_password, login_user
from utils.database import (
    load_users, load_pending_users, save_pending_users,
    load_password_reset_requests, save_password_reset_requests
)
from utils.validators import validate_email, validate_password, validate_username
from utils.email_handler import send_email
from services.audit_service import log_login
from config import VALIDATION

def get_base64_image(image_path):
    """Convert image to base64 for embedding in CSS"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.warning(f"Could not load background image: {e}")
        return None

def render_login_page():
    """Display login page with professional light background and header image"""
    
    # Load and encode the background image
    image_path = "./assets/images/test_engineer_bg.jpg"
    base64_image = get_base64_image(image_path)
    
    # Create background CSS based on whether image loaded
    if base64_image:
        header_background = f"""
            background-image: linear-gradient(135deg, rgba(0, 0, 0, 0.6) 0%, rgba(0, 0, 0, 0.4) 100%), 
                              url('data:image/jpeg;base64,{base64_image}');
            background-size: cover;
            background-position: 50% 30%;
            background-repeat: no-repeat;
        """
    else:
        # Fallback gradient if image doesn't load
        header_background = """
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        """
    
    # ========== PROFESSIONAL LIGHT THEME WITH HEADER IMAGE ==========
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* Professional Light Background */
        .stApp {{
            background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
            font-family: 'Inter', sans-serif;
        }}
        
        /* Main container */
        .block-container {{
            padding-top: 5rem;
            padding-bottom: 5rem;
        }}
        
        /* Header with Background Image */
        .header-container {{
            {header_background}
            border-radius: 20px 20px 0 0;
            padding: 3.5rem 2.5rem;
            position: relative;
            overflow: hidden;
            margin: -2.5rem -2.5rem 2rem -2.5rem;
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        /* Header content */
        .header-content {{
            position: relative;
            z-index: 2;
            width: 100%;
        }}
        
        /* Header title styling - FORCE WHITE COLOR */
        .header-title {{
            font-family: 'Inter', sans-serif !important;
            font-weight: 800 !important;
            text-align: center !important;
            color: #ffffff !important;
            font-size: 2.8rem !important;
            letter-spacing: -0.02em !important;
            margin-bottom: 1.5rem !important;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5) !important;
            line-height: 1.2 !important;
        }}
        
        /* Header subtitle styling - FORCE WHITE COLOR */
        .header-subtitle {{
            text-align: center !important;
            color: #ffffff !important;
            font-size: 1.2rem !important;
            margin-top: 0 !important;
            font-weight: 500 !important;
            text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.5) !important;
        }}
        
        /* Login card - white with subtle shadow */
        [data-testid="column"] > div {{
            background-color: #ffffff;
            border-radius: 20px;
            padding: 2.5rem;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(0, 0, 0, 0.05);
        }}
        
        /* Title styling */
        h1 {{
            font-family: 'Inter', sans-serif !important;
            font-weight: 800 !important;
            text-align: center;
            color: #1a202c;
            font-size: 2.5rem;
            letter-spacing: -0.03em;
            margin-bottom: 1rem;
        }}
        
        /* Subtitle styling */
        h2, h3 {{
            font-family: 'Inter', sans-serif !important;
            color: #2d3748;
            font-weight: 600;
        }}
        
        /* Tabs styling - Professional blue accent */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: #f8f9fa;
            padding: 0.5rem;
            border-radius: 12px;
            border: 1px solid #e9ecef;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            color: #4a5568;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white !important;
        }}
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {{
            font-family: 'Inter', sans-serif;
            border-radius: 10px;
            border: 2px solid #e2e8f0;
            transition: all 0.3s;
            background-color: #f8fafc;
        }}
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            background-color: #ffffff;
        }}
        
        /* Labels */
        .stTextInput > label,
        .stTextArea > label,
        .stCheckbox > label {{
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            color: #2d3748;
        }}
        
        /* Checkbox styling */
        .stCheckbox {{
            font-family: 'Inter', sans-serif;
        }}
        
        /* Primary button */
        .stButton > button[kind="primary"] {{
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            border: none;
            box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
            transition: all 0.3s;
        }}
        
        .stButton > button[kind="primary"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        }}
        
        /* Info/Warning/Error boxes */
        .stAlert {{
            font-family: 'Inter', sans-serif;
            border-radius: 12px;
            border: none;
        }}
        
        /* Caption text */
        .caption {{
            font-family: 'Inter', sans-serif;
            color: #718096;
        }}
        
        /* Hide Streamlit elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Professional title with background image
        st.markdown('''
        <div class="header-container">
            <div class="header-content">                    
                <h1 class="header-title">TestingHub Portal</h1>                    
                <p class="header-subtitle">Test Engineer Management System</p>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["🔐 **Login**", "📝 **Register**", "🔑 **Forgot Password**"])
        
        # LOGIN TAB
        with tab1:
            render_login_tab()
        
        # REGISTER TAB
        with tab2:
            render_register_tab()
        
        # FORGOT PASSWORD TAB
        with tab3:
            render_forgot_password_tab()

def render_login_tab():
    """Render login tab"""
    st.subheader("Login to Account")
    
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login", key="login_btn", use_container_width=True, type="primary"):
        if username and password:
            users = load_users()
            hashed_password = hash_password(password)
            
            if username in users and users[username]["password"] == hashed_password:
                if users[username].get("status", "active") == "active":
                    is_audit_reviewer = users[username].get("is_audit_reviewer", False)
                    login_user(username, users[username]["role"], is_audit_reviewer)
                    
                    log_login(username, True)
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.warning("⚠️ Your account is pending approval by Super User.")
                    log_login(username, False)
            else:
                st.error("❌ Invalid username or password.")
                log_login(username, False)
        else:
            st.warning("⚠️ Please enter both username and password.")

def render_register_tab():
    """Render registration tab with Audit Reviewer request option"""
    st.subheader("Create New Account")
    st.info("ℹ️ New registrations will be pending approval by Super User")
    
    new_username = st.text_input("Username*", key="reg_username")
    new_email = st.text_input("Email*", key="reg_email")
    new_password = st.text_input("Password*", type="password", key="reg_password")
    confirm_password = st.text_input("Confirm Password*", type="password", key="reg_confirm")
    
    st.markdown("---")
    st.markdown("#### 📋 Additional Access Requests (Optional)")
    
    request_audit_reviewer = st.checkbox(
        "Request Audit Reviewer Access",
        key="reg_audit_reviewer",
        help="Audit Reviewers can view all audit documents in the system (read-only access)"
    )
    
    audit_reviewer_justification = None
    if request_audit_reviewer:
        st.info("🔍 **Audit Reviewer Access:** Allows you to view all audit trail documents across the system for compliance and review purposes.")
        audit_reviewer_justification = st.text_area(
            "Justification for Audit Reviewer Access*",
            key="reg_audit_justification",
            placeholder="Please explain why you need access to all audit documents (e.g., compliance officer, internal auditor, quality assurance role)...",
            help="This will be reviewed by the Super User along with your registration",
            max_chars=500,
            height=100
        )
        
        if not audit_reviewer_justification:
            st.warning("⚠️ Please provide justification for Audit Reviewer access")
    
    st.markdown("---")
    
    if st.button("Register", key="register_btn", use_container_width=True, type="primary"):
        if new_username and new_email and new_password and confirm_password:
            valid, msg = validate_username(new_username)
            if not valid:
                st.error(f"❌ {msg}")
                return
            
            valid, msg = validate_email(new_email)
            if not valid:
                st.error(f"❌ {msg}")
                return
            
            valid, msg = validate_password(new_password, confirm_password)
            if not valid:
                st.error(f"❌ {msg}")
                return
            
            if request_audit_reviewer and not audit_reviewer_justification:
                st.error("❌ Please provide justification for Audit Reviewer access")
                return
            
            users = load_users()
            pending_users = load_pending_users()
            
            username_exists = new_username in users or any(p['username'] == new_username for p in pending_users)
            
            if username_exists:
                st.error("❌ Username already exists or pending approval!")
            else:
                pending_user = {
                    "username": new_username,
                    "password": hash_password(new_password),
                    "email": new_email,
                    "requested_role": "user",
                    "status": "pending",
                    "requested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "audit_reviewer_requested": request_audit_reviewer,
                    "audit_reviewer_justification": audit_reviewer_justification if request_audit_reviewer else None
                }
                
                pending_users.append(pending_user)
                
                if save_pending_users(pending_users):
                    st.success("✅ Registration submitted! Your account is pending Super User approval.")
                    st.info("📧 You will be notified once your account is approved.")
                    
                    if request_audit_reviewer:
                        st.info("🔍 Your Audit Reviewer access request has also been submitted for approval.")
                    
                    try:
                        from utils.database import load_email_config
                        config = load_email_config()
                        if config.get("enabled", False):
                            admin_email = config.get("admin_email", "")
                            if admin_email:
                                email_body = f"""
                                <h3>New User Registration</h3>
                                <p>A new user has registered:</p>
                                <ul>
                                    <li><strong>Username:</strong> {new_username}</li>
                                    <li><strong>Email:</strong> {new_email}</li>
                                    <li><strong>Requested At:</strong> {pending_user['requested_at']}</li>
                                """
                                
                                if request_audit_reviewer:
                                    email_body += f"""
                                    <li><strong>⚠️ Audit Reviewer Access:</strong> REQUESTED</li>
                                    <li><strong>Justification:</strong> {audit_reviewer_justification}</li>
                                """
                                
                                email_body += """
                                </ul>
                                <p>Please log in to approve or reject this registration.</p>
                                """
                                
                                send_email(admin_email, "New User Registration - Test Engineer Portal", email_body)
                    except Exception as e:
                        pass
                else:
                    st.error("❌ Failed to submit registration. Please try again.")
        else:
            st.warning("⚠️ Please fill in all required fields.")

def render_forgot_password_tab():
    """Render forgot password tab"""
    st.subheader("🔑 Reset Password Request")
    st.info("ℹ️ Password reset requests require Super User approval")
    
    forgot_username = st.text_input("Enter your Username*", key="forgot_username")
    forgot_email = st.text_input("Enter your Email*", key="forgot_email")
    
    st.markdown("---")
    st.markdown("#### Set Your New Password")
    st.caption("Choose a new password that you will use after approval")
    
    forgot_new_password = st.text_input(
        "New Password*",
        type="password",
        key="forgot_new_password",
        help="Minimum 6 characters"
    )
    forgot_confirm_password = st.text_input(
        "Confirm New Password*",
        type="password",
        key="forgot_confirm_password"
    )
    forgot_reason = st.text_area(
        "Reason for password reset (optional)",
        placeholder="E.g., Forgot password, account locked, etc.",
        max_chars=200,
        key="forgot_reason",
        height=80
    )
    
    if st.button("🔑 Submit Reset Request", key="forgot_submit", use_container_width=True, type="primary"):
        if forgot_username and forgot_email and forgot_new_password and forgot_confirm_password:
            valid, msg = validate_password(forgot_new_password, forgot_confirm_password)
            if not valid:
                st.error(f"❌ {msg}")
                return
            
            users = load_users()
            
            if forgot_username not in users:
                st.error("❌ Username not found!")
            elif users[forgot_username].get("email", "").lower() != forgot_email.lower():
                st.error("❌ Email doesn't match our records!")
            else:
                reset_requests = load_password_reset_requests()
                
                existing_request = any(
                    r['username'] == forgot_username and r['status'] == 'pending'
                    for r in reset_requests
                )
                
                if existing_request:
                    st.warning("⚠️ You already have a pending password reset request!")
                else:
                    reset_request = {
                        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                        "username": forgot_username,
                        "email": forgot_email,
                        "new_password": hash_password(forgot_new_password),
                        "reason": forgot_reason.strip() if forgot_reason else "User requested password reset",
                        "status": "pending",
                        "requested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    
                    reset_requests.append(reset_request)
                    
                    if save_password_reset_requests(reset_requests):
                        st.success("✅ Password reset request submitted!")
                        st.info("📧 Your request has been sent to the Super User for approval.")
                        st.info("⏳ Once approved, you can login with your new password.")
                        
                        try:
                            from utils.database import load_email_config
                            config = load_email_config()
                            if config.get("enabled", False):
                                admin_email = config.get("admin_email", "")
                                if admin_email:
                                    email_body = f"""
                                    <h3>🔑 New Password Reset Request</h3>
                                    <p>A user has requested a password reset:</p>
                                    <table style="width: 100%; border-collapse: collapse;">
                                      <tr style="background-color: #f8f9fa;">
                                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Username:</strong></td>
                                        <td style="padding: 10px; border: 1px solid #ddd;">{forgot_username}</td>
                                      </tr>
                                      <tr>
                                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Email:</strong></td>
                                        <td style="padding: 10px; border: 1px solid #ddd;">{forgot_email}</td>
                                      </tr>
                                      <tr style="background-color: #f8f9fa;">
                                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Reason:</strong></td>
                                        <td style="padding: 10px; border: 1px solid #ddd;">{reset_request['reason']}</td>
                                      </tr>
                                      <tr>
                                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Requested At:</strong></td>
                                        <td style="padding: 10px; border: 1px solid #ddd;">{reset_request['requested_at']}</td>
                                      </tr>
                                    </table>
                                    <p><strong>⚠️ Action Required:</strong> Please log in to approve or reject this request.</p>
                                    """
                                    send_email(admin_email, "Password Reset Request - Test Engineer Portal", email_body)
                        except Exception as e:
                            pass
                    else:
                        st.error("❌ Failed to submit request. Please try again.")
        else:
            st.warning("⚠️ Please fill in all required fields.")
    
    st.markdown("---")
    st.caption("💡 **Tip:** Contact your administrator if you need immediate assistance.")