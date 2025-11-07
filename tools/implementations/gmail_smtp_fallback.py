"""
Gmail SMTP Fallback for Email Sending
Use when Microsoft Graph API is blocked by IP filters
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional

def send_email_via_gmail_smtp(
    gmail_address: str,
    gmail_app_password: str,
    to_emails: List[str],
    subject: str,
    body: str,
    is_html: bool = True,
    cc_emails: Optional[List[str]] = None,
    bcc_emails: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Send email via Gmail SMTP (fallback when Graph API is blocked)
    
    Setup:
    1. Enable 2FA on Gmail account
    2. Generate App Password: https://myaccount.google.com/apppasswords
    3. Store in environment variable: GMAIL_APP_PASSWORD
    
    Args:
        gmail_address: Your Gmail address (e.g., 'yourname@gmail.com')
        gmail_app_password: App-specific password from Google
        to_emails: List of recipient email addresses
        subject: Email subject
        body: Email body content
        is_html: Whether body is HTML (default: True)
        cc_emails: Optional list of CC recipients
        bcc_emails: Optional list of BCC recipients
    
    Returns:
        Dict with success status and message
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = gmail_address
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject
        
        if cc_emails:
            msg['Cc'] = ', '.join(cc_emails)
        
        # Attach body
        mime_type = 'html' if is_html else 'plain'
        msg.attach(MIMEText(body, mime_type))
        
        # Combine all recipients
        all_recipients = to_emails.copy()
        if cc_emails:
            all_recipients.extend(cc_emails)
        if bcc_emails:
            all_recipients.extend(bcc_emails)
        
        # Connect and send
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_address, gmail_app_password)
            server.sendmail(gmail_address, all_recipients, msg.as_string())
        
        return {
            'success': True,
            'message': f'Email sent via Gmail SMTP to {len(to_emails)} recipient(s)',
            'recipients': to_emails,
            'method': 'gmail_smtp'
        }
    
    except smtplib.SMTPAuthenticationError:
        return {
            'success': False,
            'error': 'Gmail authentication failed. Check your app password.',
            'method': 'gmail_smtp'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to send email via Gmail SMTP: {str(e)}',
            'method': 'gmail_smtp'
        }
