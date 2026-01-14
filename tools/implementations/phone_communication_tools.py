#!/usr/bin/env python3
"""
Phone Communication Tools for VSA Platform
Enables email and SMS sending for coaching documents, alerts, and follow-ups
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

# Try to import Twilio (optional dependency)
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("Twilio not installed. SMS functionality will be unavailable. Install with: pip install twilio")


def send_email_veterinary_coaching(
    call_id: str,
    to_email: str,
    subject: str = "AI Coaching Document - Call Review",
    custom_message: Optional[str] = None,
    include_transcript: bool = False,
    smtp_config: Optional[Dict] = None
) -> Dict:
    """
    Send AI coaching document to staff member via email
    
    Args:
        call_id: The call ID for which coaching was generated
        to_email: Recipient email address (staff member)
        subject: Email subject line
        custom_message: Optional custom message to prepend to coaching
        include_transcript: Whether to include call transcript in email
        smtp_config: Optional SMTP configuration (overrides environment)
    
    Returns:
        Dict with success status, message, and metadata
    """
    try:
        # Get database connector
        from tools.Database_Data import get_unified_connector
        connector = get_unified_connector()
        
        # Fetch coaching document
        coaching_result = connector.supabase_client\
            .table('call_manager_alerts')\
            .select('ai_coaching_support, ai_coaching_generated_date, manager_alerts_tags')\
            .eq('call_id', call_id)\
            .single()\
            .execute()
        
        if not coaching_result.data:
            return {
                'success': False,
                'error': f'No coaching document found for call {call_id}'
            }
        
        coaching_content = coaching_result.data.get('ai_coaching_support', '')
        if not coaching_content:
            return {
                'success': False,
                'error': f'Coaching document is empty for call {call_id}'
            }
        
        coaching_date = coaching_result.data.get('ai_coaching_generated_date', 'Unknown')
        alert_tags = coaching_result.data.get('manager_alerts_tags', 'N/A')
        
        # Fetch call data for context
        call_result = connector.supabase_client\
            .table('veterinary_calls')\
            .select('key_staffname, key_call_date, key_otherspeaker_firstname, key_otherspeaker_lastname')\
            .eq('call_id', call_id)\
            .single()\
            .execute()
        
        staff_name = call_result.data.get('key_staffname', 'Unknown') if call_result.data else 'Unknown'
        call_date = call_result.data.get('key_call_date', 'Unknown') if call_result.data else 'Unknown'
        client_name = ''
        if call_result.data:
            first = call_result.data.get('key_otherspeaker_firstname', '')
            last = call_result.data.get('key_otherspeaker_lastname', '')
            client_name = f"{first} {last}".strip() or 'Unknown Client'
        
        # Build email body
        email_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: #4A90E2; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .coaching {{ background: #f5f5f5; padding: 15px; border-left: 4px solid #4A90E2; margin: 20px 0; }}
        .metadata {{ color: #666; font-size: 0.9em; margin-top: 20px; }}
        .footer {{ background: #f9f9f9; padding: 15px; text-align: center; font-size: 0.85em; color: #666; }}
        h2 {{ color: #4A90E2; }}
        h3 {{ color: #333; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Coaching Document</h1>
        <p>Veterinary Services Analytics</p>
    </div>
    
    <div class="content">
        <h2>Call Information</h2>
        <ul>
            <li><strong>Call ID:</strong> {call_id}</li>
            <li><strong>Staff Member:</strong> {staff_name}</li>
            <li><strong>Client:</strong> {client_name}</li>
            <li><strong>Call Date:</strong> {call_date}</li>
            <li><strong>Alert Tags:</strong> {alert_tags}</li>
        </ul>
"""
        
        # Add custom message if provided
        if custom_message and custom_message.strip():
            email_body += f"""
        <div style="background: #FFF8DC; padding: 15px; border-left: 4px solid #FFD700; margin: 20px 0;">
            <h3>Manager's Note:</h3>
            <p>{custom_message.replace(chr(10), '<br>')}</p>
        </div>
"""
        
        # Add coaching content
        coaching_html = coaching_content.replace('\n', '<br>')
        email_body += f"""
        <div class="coaching">
            <h2>AI-Generated Coaching Document</h2>
            {coaching_html}
        </div>
        
        <div class="metadata">
            <p><strong>Generated:</strong> {coaching_date}</p>
            <p><em>This coaching document was automatically generated using AI analysis of the call transcript and performance metrics.</em></p>
        </div>
"""
        
        # Add transcript if requested
        if include_transcript:
            transcript_result = connector.supabase_client\
                .table('call_full_transcript_and_full_analysis')\
                .select('full_transcript_text')\
                .eq('call_id', call_id)\
                .single()\
                .execute()
            
            if transcript_result.data and transcript_result.data.get('full_transcript_text'):
                transcript_html = transcript_result.data['full_transcript_text'].replace('\n', '<br>')
                email_body += f"""
        <hr>
        <h2>Call Transcript</h2>
        <div style="background: #f9f9f9; padding: 15px; font-family: monospace; font-size: 0.9em;">
            {transcript_html}
        </div>
"""
        
        email_body += """
    </div>
    
    <div class="footer">
        <p>This is an automated message from VSA Veterinary Services Analytics Platform</p>
        <p>For questions or concerns, please contact your manager</p>
    </div>
</body>
</html>
"""
        
        # Send email using SMTP
        result = _send_email_smtp_internal(
            to_email=to_email,
            subject=subject,
            body=email_body,
            smtp_config=smtp_config
        )
        
        if result['success']:
            # Log send event to database
            _log_communication_event(
                call_id=call_id,
                communication_type='email',
                recipient=to_email,
                subject=subject,
                status='sent'
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to send coaching email: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def send_sms_veterinary_alert(
    call_id: str,
    to_phone: str,
    message_text: str,
    alert_type: Optional[str] = None,
    twilio_config: Optional[Dict] = None
) -> Dict:
    """
    Send alert notification to staff member via SMS
    
    Args:
        call_id: The call ID related to the alert
        to_phone: Recipient phone number (E.164 format: +1234567890)
        message_text: SMS message content (max 1600 chars)
        alert_type: Optional alert type for categorization
        twilio_config: Optional Twilio configuration (overrides environment)
    
    Returns:
        Dict with success status, message, and SID
    """
    if not TWILIO_AVAILABLE:
        return {
            'success': False,
            'error': 'Twilio SDK not installed. Install with: pip install twilio'
        }
    
    try:
        # Validate phone format
        phone_clean = to_phone.strip()
        if not phone_clean.startswith('+'):
            # Try to add +1 for US numbers
            if len(phone_clean) == 10:
                phone_clean = f'+1{phone_clean}'
            else:
                phone_clean = f'+{phone_clean}'
        
        # Truncate message if too long (SMS has 1600 char limit)
        if len(message_text) > 1600:
            message_text = message_text[:1590] + "...\n(View full alert in dashboard)"
        
        # Build message with call context
        sms_body = f"VSA Alert - Call {call_id}\n"
        if alert_type:
            sms_body += f"Type: {alert_type}\n"
        sms_body += f"\n{message_text}"
        
        # Send SMS using Twilio
        result = _send_sms_twilio_internal(
            to_phone=phone_clean,
            body=sms_body,
            twilio_config=twilio_config
        )
        
        if result['success']:
            # Log send event to database
            _log_communication_event(
                call_id=call_id,
                communication_type='sms',
                recipient=phone_clean,
                subject=f"Alert: {alert_type}" if alert_type else "Alert",
                status='sent',
                sms_sid=result.get('sms_sid')
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to send alert SMS: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def send_bulk_coaching_emails(
    call_ids: List[str],
    to_emails: List[str],
    subject_template: str = "AI Coaching Document - Call {call_id}",
    custom_message: Optional[str] = None,
    smtp_config: Optional[Dict] = None
) -> Dict:
    """
    Send coaching documents to multiple staff members in batch
    
    Args:
        call_ids: List of call IDs to send coaching for
        to_emails: List of recipient email addresses (must match call_ids length)
        subject_template: Email subject template ({call_id} will be replaced)
        custom_message: Optional custom message for all emails
        smtp_config: Optional SMTP configuration
    
    Returns:
        Dict with success status, sent_count, failed_count, and details
    """
    if len(call_ids) != len(to_emails):
        return {
            'success': False,
            'error': 'call_ids and to_emails must have the same length'
        }
    
    results = {
        'success': True,
        'sent_count': 0,
        'failed_count': 0,
        'details': []
    }
    
    for call_id, to_email in zip(call_ids, to_emails):
        try:
            subject = subject_template.replace('{call_id}', call_id)
            result = send_email_veterinary_coaching(
                call_id=call_id,
                to_email=to_email,
                subject=subject,
                custom_message=custom_message,
                smtp_config=smtp_config
            )
            
            if result['success']:
                results['sent_count'] += 1
                results['details'].append({
                    'call_id': call_id,
                    'email': to_email,
                    'status': 'sent'
                })
            else:
                results['failed_count'] += 1
                results['details'].append({
                    'call_id': call_id,
                    'email': to_email,
                    'status': 'failed',
                    'error': result.get('error', 'Unknown error')
                })
        
        except Exception as e:
            results['failed_count'] += 1
            results['details'].append({
                'call_id': call_id,
                'email': to_email,
                'status': 'error',
                'error': str(e)
            })
    
    if results['failed_count'] > 0:
        results['success'] = False
        results['message'] = f"Sent {results['sent_count']}/{len(call_ids)} emails. {results['failed_count']} failed."
    else:
        results['message'] = f"Successfully sent all {results['sent_count']} emails"
    
    return results


# ============================================================================
# INTERNAL HELPER FUNCTIONS
# ============================================================================

def _send_email_smtp_internal(
    to_email: str,
    subject: str,
    body: str,
    smtp_config: Optional[Dict] = None
) -> Dict:
    """Internal SMTP email sending function"""
    try:
        # Get SMTP configuration from environment or parameter
        if smtp_config is None:
            smtp_config = {}
        
        smtp_server = smtp_config.get('smtp_server') or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(smtp_config.get('smtp_port') or os.getenv('SMTP_PORT', 587))
        smtp_user = smtp_config.get('smtp_user') or os.getenv('SMTP_USER', '')
        smtp_password = smtp_config.get('smtp_password') or os.getenv('SMTP_PASSWORD', '')
        from_email = smtp_config.get('from_email') or os.getenv('SMTP_FROM_EMAIL', smtp_user)
        
        if not smtp_user or not smtp_password:
            return {
                'success': False,
                'error': 'SMTP credentials not configured. Set SMTP_USER and SMTP_PASSWORD environment variables.'
            }
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Reply-To'] = smtp_user
        
        # Attach HTML body
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        return {
            'success': True,
            'message': f'Email sent successfully to {to_email}',
            'sent_at': datetime.now().isoformat()
        }
        
    except smtplib.SMTPAuthenticationError:
        return {
            'success': False,
            'error': 'SMTP authentication failed. For Gmail, use an App Password (not your regular password).'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Email sending failed: {str(e)}'
        }


def _send_sms_twilio_internal(
    to_phone: str,
    body: str,
    twilio_config: Optional[Dict] = None
) -> Dict:
    """Internal Twilio SMS sending function"""
    if not TWILIO_AVAILABLE:
        return {
            'success': False,
            'error': 'Twilio SDK not installed'
        }
    
    try:
        # Get Twilio configuration from environment or parameter
        if twilio_config is None:
            twilio_config = {}
        
        account_sid = twilio_config.get('account_sid') or os.getenv('TWILIO_ACCOUNT_SID', '')
        auth_token = twilio_config.get('auth_token') or os.getenv('TWILIO_AUTH_TOKEN', '')
        from_phone = twilio_config.get('from_phone') or os.getenv('TWILIO_FROM_PHONE', '')
        
        if not account_sid or not auth_token or not from_phone:
            return {
                'success': False,
                'error': 'Twilio credentials not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_PHONE environment variables.'
            }
        
        # Send SMS
        client = TwilioClient(account_sid, auth_token)
        message = client.messages.create(
            body=body,
            from_=from_phone,
            to=to_phone
        )
        
        return {
            'success': True,
            'message': f'SMS sent successfully to {to_phone}',
            'sms_sid': message.sid,
            'sent_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'SMS sending failed: {str(e)}'
        }


def _log_communication_event(
    call_id: str,
    communication_type: str,
    recipient: str,
    subject: str,
    status: str,
    sms_sid: Optional[str] = None
) -> None:
    """Log communication event to database for tracking"""
    try:
        from tools.Database_Data import get_unified_connector
        connector = get_unified_connector()
        
        # Log to manager_alert_notes field
        current_notes = connector.supabase_client\
            .table('call_manager_alerts')\
            .select('manager_alert_notes')\
            .eq('call_id', call_id)\
            .single()\
            .execute()
        
        existing_notes = ''
        if current_notes.data and current_notes.data.get('manager_alert_notes'):
            existing_notes = current_notes.data['manager_alert_notes']
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        log_entry = f"\n✓ {communication_type.upper()} sent to {recipient} on {timestamp}"
        if sms_sid:
            log_entry += f" (SID: {sms_sid})"
        
        updated_notes = (existing_notes + log_entry).strip()
        
        connector.supabase_client\
            .table('call_manager_alerts')\
            .update({'manager_alert_notes': updated_notes})\
            .eq('call_id', call_id)\
            .execute()
        
        logger.info(f"Logged {communication_type} communication for call {call_id}")
        
    except Exception as e:
        logger.error(f"Failed to log communication event: {e}")


# Tool registration metadata
TOOL_METADATA = {
    'send_email_veterinary_coaching': {
        'category': 'phone_communication',
        'requires_credentials': True,
        'credentials_needed': ['SMTP_USER', 'SMTP_PASSWORD'],
        'optional_credentials': ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_FROM_EMAIL']
    },
    'send_sms_veterinary_alert': {
        'category': 'phone_communication',
        'requires_credentials': True,
        'credentials_needed': ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_FROM_PHONE'],
        'requires_package': 'twilio'
    },
    'send_bulk_coaching_emails': {
        'category': 'phone_communication',
        'requires_credentials': True,
        'credentials_needed': ['SMTP_USER', 'SMTP_PASSWORD']
    }
}
