"""
SendGrid Email Fallback for Production
Use when Microsoft Graph API is blocked by IP filters (common on Render.com)

Setup:
1. Sign up for SendGrid: https://sendgrid.com/
2. Create API key with Mail Send permissions
3. Add to .env: SENDGRID_API_KEY=SG.xxxxxxxxxxxx
4. Verify sender email in SendGrid dashboard
"""

import os
import requests
from typing import List, Dict, Any, Optional

def sendgrid_send_email(
    to_emails: List[str],
    subject: str,
    body: str,
    from_email: str = None,
    from_name: str = "InHouse Print",
    is_html: bool = True,
    cc_emails: Optional[List[str]] = None,
    bcc_emails: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Send email via SendGrid API (production-ready alternative to Microsoft Graph)
    
    Args:
        to_emails: List of recipient email addresses
        subject: Email subject line
        body: Email body content
        from_email: Sender email (must be verified in SendGrid)
        from_name: Sender display name
        is_html: Whether body is HTML (default: True)
        cc_emails: Optional list of CC recipients
        bcc_emails: Optional list of BCC recipients
    
    Returns:
        Dict with success status and details
    """
    api_key = os.getenv('SENDGRID_API_KEY')
    if not api_key:
        return {
            'success': False,
            'error': 'SENDGRID_API_KEY not found in environment variables'
        }
    
    if not from_email:
        from_email = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@yourdomain.com')
    
    # Build recipient list
    personalizations = [{
        'to': [{'email': email} for email in to_emails]
    }]
    
    if cc_emails:
        personalizations[0]['cc'] = [{'email': email} for email in cc_emails]
    
    if bcc_emails:
        personalizations[0]['bcc'] = [{'email': email} for email in bcc_emails]
    
    # Build email payload
    payload = {
        'personalizations': personalizations,
        'from': {
            'email': from_email,
            'name': from_name
        },
        'subject': subject,
        'content': [{
            'type': 'text/html' if is_html else 'text/plain',
            'value': body
        }]
    }
    
    # Send via SendGrid API
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            'https://api.sendgrid.com/v3/mail/send',
            json=payload,
            headers=headers
        )
        
        if response.status_code == 202:
            return {
                'success': True,
                'message': f'Email sent via SendGrid to {len(to_emails)} recipient(s)',
                'recipients': to_emails,
                'method': 'sendgrid',
                'status_code': 202
            }
        else:
            return {
                'success': False,
                'error': f'SendGrid API error: {response.status_code} - {response.text}',
                'status_code': response.status_code
            }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to send email via SendGrid: {str(e)}',
            'method': 'sendgrid'
        }


def microsoft_outlook_send_email_with_fallback(
    to: List[str],
    subject: str,
    body: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Smart email sending with automatic fallback:
    1. Try Microsoft Graph API first
    2. If IP blocked (550 5.7.708), automatically use SendGrid
    
    This is the wrapper you should expose to the AI agent
    """
    from tools.implementations.microsoft_outlook_tools import microsoft_outlook_send_email
    
    # Try Microsoft Graph API first
    result = microsoft_outlook_send_email(to=to, subject=subject, body=body, **kwargs)
    
    # Check if IP was blocked
    if not result.get('success'):
        error_msg = result.get('error', '')
        status_code = result.get('status_code', 0)
        
        # IP blocking errors
        if status_code == 550 or '5.7.708' in error_msg or 'traffic not accepted from this IP' in error_msg:
            print(f"[EMAIL FALLBACK] Microsoft Graph blocked (IP issue), trying SendGrid...")
            
            # Parse recipients if needed
            if isinstance(to, str):
                to_list = [email.strip() for email in to.split(',')]
            else:
                to_list = to
            
            # Fallback to SendGrid
            return sendgrid_send_email(
                to_emails=to_list,
                subject=subject,
                body=body,
                **kwargs
            )
    
    return result
