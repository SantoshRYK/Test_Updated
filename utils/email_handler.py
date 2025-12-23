# utils/email_handler.py
"""
Email notification utilities
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple
from utils.database import load_email_config

def send_email(to_email: str, subject: str, body: str) -> Tuple[bool, str]:
    """Send email notification"""
    try:
        config = load_email_config()
        
        if not config.get("enabled", False):
            return False, "Email notifications are disabled"
        
        # Validate email configuration
        if not config.get("smtp_server") or not config.get("sender_email"):
            return False, "Email configuration incomplete"
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = config.get("sender_email")
        message["To"] = to_email
        
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
              <h2 style="color: #2c3e50;">🧪 Test Engineer Portal Notification</h2>
              {body}
              <hr style="margin: 20px 0;">
              <p style="color: #7f8c8d; font-size: 12px;">
                This is an automated message from Test Engineer Portal. Please do not reply to this email.
              </p>
            </div>
          </body>
        </html>
        """
        
        part = MIMEText(html_body, "html")
        message.attach(part)
        
        # Connect to SMTP server
        if config.get("use_tls", True):
            server = smtplib.SMTP(config.get("smtp_server"), config.get("smtp_port", 587))
            server.starttls()
        else:
            server = smtplib.SMTP(config.get("smtp_server"), config.get("smtp_port", 587))
        
        server.login(config.get("sender_email"), config.get("sender_password"))
        server.send_message(message)
        server.quit()
        
        return True, "Email sent successfully"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

def send_allocation_notification(allocation: dict, action: str = "created"):
    """Send notification for allocation creation/update"""
    config = load_email_config()
    
    if not config.get("enabled", False):
        return
    
    if action == "created" and not config.get("notify_on_create", True):
        return
    if action == "updated" and not config.get("notify_on_update", False):
        return
    
    body = f"""
    <h3>Allocation {action.title()}</h3>
    <table style="width: 100%; border-collapse: collapse;">
      <tr style="background-color: #f8f9fa;">
        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Trial ID:</strong></td>
        <td style="padding: 10px; border: 1px solid #ddd;">{allocation.get('trial_id', 'N/A')}</td>
      </tr>
      <tr>
        <td style="padding: 10px; border: 1px solid #ddd;"><strong>System:</strong></td>
        <td style="padding: 10px; border: 1px solid #ddd;">{allocation.get('system', 'N/A')}</td>
      </tr>
      <tr style="background-color: #f8f9fa;">
        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Test Engineer:</strong></td>
        <td style="padding: 10px; border: 1px solid #ddd;">{allocation.get('test_engineer_name', 'N/A')}</td>
      </tr>
      <tr>
        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Created By:</strong></td>
        <td style="padding: 10px; border: 1px solid #ddd;">{allocation.get('created_by', 'N/A')}</td>
      </tr>
    </table>
    """
    
    subject = f"Allocation {action.title()}: {allocation.get('trial_id', 'N/A')}"
    admin_email = config.get("admin_email", "")
    
    if admin_email:
        send_email(admin_email, subject, body)

def send_uat_notification(uat_record: dict, action: str = "created"):
    """Send notification for UAT record creation/update"""
    config = load_email_config()
    
    if not config.get("enabled", False):
        return
    
    body = f"""
    <h3>UAT Record {action.title()}</h3>
    <table style="width: 100%; border-collapse: collapse;">
      <tr style="background-color: #f8f9fa;">
        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Trial ID:</strong></td>
        <td style="padding: 10px; border: 1px solid #ddd;">{uat_record.get('trial_id', 'N/A')}</td>
      </tr>
      <tr>
        <td style="padding: 10px; border: 1px solid #ddd;"><strong>UAT Round:</strong></td>
        <td style="padding: 10px; border: 1px solid #ddd;">{uat_record.get('uat_round', 'N/A')}</td>
      </tr>
      <tr style="background-color: #f8f9fa;">
        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Status:</strong></td>
        <td style="padding: 10px; border: 1px solid #ddd;">{uat_record.get('status', 'N/A')}</td>
      </tr>
      <tr>
        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Result:</strong></td>
        <td style="padding: 10px; border: 1px solid #ddd;">{uat_record.get('result', 'N/A')}</td>
      </tr>
      <tr style="background-color: #f8f9fa;">
        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Created By:</strong></td>
        <td style="padding: 10px; border: 1px solid #ddd;">{uat_record.get('created_by', 'N/A')}</td>
      </tr>
    </table>
    """
    
    subject = f"UAT Record {action.title()}: {uat_record.get('trial_id', 'N/A')}"
    admin_email = config.get("admin_email", "")
    
    if admin_email:
        send_email(admin_email, subject, body)

def send_password_reset_notification(username: str, email: str, action: str = "requested"):
    """Send password reset notification"""
    config = load_email_config()
    
    if not config.get("enabled", False):
        return
    
    if action == "requested":
        body = f"""
        <h3>🔑 Password Reset Requested</h3>
        <p>A password reset has been requested for your account.</p>
        <table style="width: 100%; border-collapse: collapse;">
          <tr style="background-color: #f8f9fa;">
            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Username:</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">{username}</td>
          </tr>
        </table>
        <p>Your request is pending approval from the administrator.</p>
        """
        subject = "Password Reset Requested"
    elif action == "approved":
        body = f"""
        <h3>✅ Password Reset Approved</h3>
        <p>Your password reset request has been approved.</p>
        <p>You can now log in with your new password.</p>
        """
        subject = "Password Reset Approved"
    else:  # rejected
        body = f"""
        <h3>❌ Password Reset Rejected</h3>
        <p>Your password reset request has been rejected.</p>
        <p>Please contact your administrator for assistance.</p>
        """
        subject = "Password Reset Rejected"
    
    send_email(email, subject, body)