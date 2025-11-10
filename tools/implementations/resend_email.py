"""
Resend Email Tools - Production-Grade Email Sending

Functions:
- resend_send_email: Send transactional emails
- resend_send_email_html: Send HTML emails with plain text fallback
- resend_send_batch_emails: Send multiple emails efficiently
- resend_get_email_status: Check delivery status

Author: AI Agents Platform
Date: November 5, 2025
"""

import os
import resend
from typing import Dict, Any, List, Optional


class ResendError(Exception):
    """Custom exception for Resend email errors"""
    pass


def resend_send_email(
    from_email: str,
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    reply_to: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Send a plain text email via Resend
    
    Args:
        from_email: Sender email address (e.g., 'gerardo@minivetguide.com')
        to: Recipient email address
        subject: Email subject line
        body: Email body (plain text)
        cc: Optional CC recipients (comma-separated)
        bcc: Optional BCC recipients (comma-separated)
        reply_to: Optional reply-to address
        **kwargs: Additional parameters (api_key injected if not provided)
    
    Returns:
        Dict with email_id, status, and delivery info
    
    Raises:
        ResendError: If email sending fails
    
    Example:
        result = resend_send_email(
            from_email='gerardo@minivetguide.com',
            to='client@example.com',
            subject='Invoice #12345',
            body='Thank you for your business!'
        )
    """
    try:
        # Get API key from kwargs or environment
        api_key = kwargs.get('api_key') or os.getenv('RESEND_API_KEY')
        if not api_key:
            raise ResendError("RESEND_API_KEY not found in environment variables")
        
        # Set API key
        resend.api_key = api_key
        
        # Build recipient lists
        to_list = [to] if isinstance(to, str) else to
        
        # Build email parameters
        params = {
            "from": from_email,
            "to": to_list,
            "subject": subject,
            "text": body
        }
        
        # Add optional fields
        if cc:
            params["cc"] = [cc] if isinstance(cc, str) else cc
        if bcc:
            params["bcc"] = [bcc] if isinstance(bcc, str) else bcc
        if reply_to:
            params["reply_to"] = reply_to
        
        # Send email
        response = resend.Emails.send(params)
        
        return {
            "success": True,
            "email_id": response.get("id"),
            "from": from_email,
            "to": to,
            "subject": subject,
            "message": "Email sent successfully via Resend"
        }
        
    except Exception as e:
        raise ResendError(f"Failed to send email: {str(e)}")


def resend_send_email_html(
    from_email: str,
    to: str,
    subject: str,
    html_body: str,
    plain_body: Optional[str] = None,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    reply_to: Optional[str] = None,
    attachments: Optional[List[Dict[str, str]]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Send an HTML email with plain text fallback via Resend
    
    Args:
        from_email: Sender email address
        to: Recipient email address
        subject: Email subject line
        html_body: Email body (HTML format)
        plain_body: Plain text version (optional, auto-generated if not provided)
        cc: Optional CC recipients
        bcc: Optional BCC recipients
        reply_to: Optional reply-to address
        attachments: List of attachments [{"filename": "file.pdf", "content": base64_str}]
        **kwargs: Additional parameters
    
    Returns:
        Dict with email_id, status, and delivery info
    
    Raises:
        ResendError: If email sending fails
    
    Example:
        result = resend_send_email_html(
            from_email='gerardo@minivetguide.com',
            to='client@example.com',
            subject='Invoice #12345',
            html_body='<h1>Invoice</h1><p>Total: $500</p>',
            plain_body='Invoice\nTotal: $500'
        )
    """
    try:
        # Get API key
        api_key = kwargs.get('api_key') or os.getenv('RESEND_API_KEY')
        if not api_key:
            raise ResendError("RESEND_API_KEY not found in environment variables")
        
        resend.api_key = api_key
        
        # Build recipient lists
        to_list = [to] if isinstance(to, str) else to
        
        # Build email parameters
        params = {
            "from": from_email,
            "to": to_list,
            "subject": subject,
            "html": html_body
        }
        
        # Add plain text version
        if plain_body:
            params["text"] = plain_body
        
        # Add optional fields
        if cc:
            params["cc"] = [cc] if isinstance(cc, str) else cc
        if bcc:
            params["bcc"] = [bcc] if isinstance(bcc, str) else bcc
        if reply_to:
            params["reply_to"] = reply_to
        if attachments:
            params["attachments"] = attachments
        
        # Send email
        response = resend.Emails.send(params)
        
        return {
            "success": True,
            "email_id": response.get("id"),
            "from": from_email,
            "to": to,
            "subject": subject,
            "has_attachments": bool(attachments),
            "message": "HTML email sent successfully via Resend"
        }
        
    except Exception as e:
        raise ResendError(f"Failed to send HTML email: {str(e)}")


def resend_send_batch_emails(
    from_email: str,
    emails: List[Dict[str, str]],
    **kwargs
) -> Dict[str, Any]:
    """
    Send multiple emails efficiently in batch
    
    Args:
        from_email: Sender email address
        emails: List of email dicts [{"to": "user@example.com", "subject": "Hi", "body": "Hello"}]
        **kwargs: Additional parameters
    
    Returns:
        Dict with sent_count, failed_count, and details
    
    Example:
        result = resend_send_batch_emails(
            from_email='gerardo@minivetguide.com',
            emails=[
                {"to": "client1@example.com", "subject": "Invoice", "body": "Your invoice"},
                {"to": "client2@example.com", "subject": "Invoice", "body": "Your invoice"}
            ]
        )
    """
    try:
        api_key = kwargs.get('api_key') or os.getenv('RESEND_API_KEY')
        if not api_key:
            raise ResendError("RESEND_API_KEY not found")
        
        resend.api_key = api_key
        
        sent_count = 0
        failed_count = 0
        results = []
        
        for email in emails:
            try:
                params = {
                    "from": from_email,
                    "to": [email["to"]],
                    "subject": email["subject"],
                    "text": email.get("body", email.get("text", ""))
                }
                
                # Add HTML if provided
                if "html" in email:
                    params["html"] = email["html"]
                
                response = resend.Emails.send(params)
                sent_count += 1
                results.append({
                    "to": email["to"],
                    "status": "sent",
                    "email_id": response.get("id")
                })
                
            except Exception as e:
                failed_count += 1
                results.append({
                    "to": email["to"],
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "success": True,
            "total": len(emails),
            "sent": sent_count,
            "failed": failed_count,
            "results": results,
            "message": f"Batch send complete: {sent_count} sent, {failed_count} failed"
        }
        
    except Exception as e:
        raise ResendError(f"Batch send failed: {str(e)}")


def resend_get_email_status(
    email_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Get delivery status of a sent email
    
    Args:
        email_id: Email ID returned from send operation
        **kwargs: Additional parameters
    
    Returns:
        Dict with delivery status and timestamp
    
    Example:
        status = resend_get_email_status(email_id='re_123abc')
    """
    try:
        api_key = kwargs.get('api_key') or os.getenv('RESEND_API_KEY')
        if not api_key:
            raise ResendError("RESEND_API_KEY not found")
        
        resend.api_key = api_key
        
        # Get email details
        response = resend.Emails.get(email_id)
        
        return {
            "success": True,
            "email_id": email_id,
            "status": response.get("status"),
            "created_at": response.get("created_at"),
            "last_event": response.get("last_event"),
            "from": response.get("from"),
            "to": response.get("to"),
            "subject": response.get("subject")
        }
        
    except Exception as e:
        raise ResendError(f"Failed to get email status: {str(e)}")


# Export all functions
__all__ = [
    'resend_send_email',
    'resend_send_email_html',
    'resend_send_batch_emails',
    'resend_get_email_status',
    'ResendError'
]
