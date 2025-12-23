# pages/admin/email_settings.py
"""
Email notification settings
"""
import streamlit as st
from utils.database import load_email_config, save_email_config
from utils.email_handler import send_email
from services.audit_service import log_user_action, log_page_view

def render_email_settings_page():
    """Email settings page"""
    log_page_view("email_settings")
    
    st.title("📧 Email Notification Settings")
    st.markdown("---")
    
    if st.button("⬅️ Back to Home", key="email_back_home"):
        st.session_state.current_page = "home"
        st.rerun()
    
    config = load_email_config()
    
    st.subheader("SMTP Configuration")
    st.info("ℹ️ Configure your email server settings to enable notifications")
    
    with st.form("email_config_form"):
        enabled = st.checkbox("Enable Email Notifications", value=config.get("enabled", False))
        
        col1, col2 = st.columns(2)
        
        with col1:
            smtp_server = st.text_input(
                "SMTP Server",
                value=config.get("smtp_server", ""),
                placeholder="smtp.gmail.com"
            )
            sender_email = st.text_input(
                "Sender Email",
                value=config.get("sender_email", ""),
                placeholder="your-email@gmail.com"
            )
            admin_email = st.text_input(
                "Admin Email (for notifications)",
                value=config.get("admin_email", ""),
                placeholder="admin@testportal.com"
            )
        
        with col2:
            smtp_port = st.number_input(
                "SMTP Port",
                value=config.get("smtp_port", 587),
                min_value=1,
                max_value=65535
            )
            sender_password = st.text_input(
                "Sender Password",
                type="password",
                value=config.get("sender_password", ""),
                placeholder="Your email password or app password"
            )
            use_tls = st.checkbox("Use TLS/SSL", value=config.get("use_tls", True))
        
        st.markdown("---")
        st.subheader("Notification Settings")
        
        col3, col4 = st.columns(2)
        with col3:
            notify_on_create = st.checkbox(
                "Notify on Allocation Created",
                value=config.get("notify_on_create", True)
            )
        with col4:
            notify_on_update = st.checkbox(
                "Notify on Allocation Updated",
                value=config.get("notify_on_update", False)
            )
        
        save_button = st.form_submit_button("💾 Save Configuration", use_container_width=True, type="primary")
        
        if save_button:
            new_config = {
                "enabled": enabled,
                "smtp_server": smtp_server,
                "smtp_port": smtp_port,
                "sender_email": sender_email,
                "sender_password": sender_password,
                "use_tls": use_tls,
                "notify_on_create": notify_on_create,
                "notify_on_update": notify_on_update,
                "admin_email": admin_email
            }
            
            if save_email_config(new_config):
                st.success("✅ Email configuration saved successfully!")
                log_user_action("UPDATE", "Email Settings", "Updated email configuration")
            else:
                st.error("❌ Failed to save configuration")
    
    st.markdown("---")
    
    # Test email
    st.subheader("Test Email Configuration")
    test_email = st.text_input("Test Email Address", placeholder="test@example.com")
    
    if st.button("📨 Send Test Email", type="primary"):
        if test_email:
            test_body = """
            <h3>Test Email</h3>
            <p>This is a test email from Test Engineer Portal.</p>
            <p>If you received this email, your email configuration is working correctly! ✅</p>
            """
            success, message = send_email(test_email, "Test Email - Test Engineer Portal", test_body)
            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
        else:
            st.warning("⚠️ Please enter a test email address")
    
    # Common SMTP configurations
    with st.expander("📚 Common SMTP Server Configurations"):
        st.markdown("""
        ### Gmail
        - **SMTP Server:** smtp.gmail.com
        - **Port:** 587 (TLS) or 465 (SSL)
        - **Note:** Use App Password, not regular password
        
        ### Outlook/Hotmail
        - **SMTP Server:** smtp-mail.outlook.com or smtp.office365.com
        - **Port:** 587
        
        ### Yahoo
        - **SMTP Server:** smtp.mail.yahoo.com
        - **Port:** 587 or 465
        """)