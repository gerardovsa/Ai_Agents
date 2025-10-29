"""
Office 365 Email Sender Utility for InHouse Print System

This module provides a reusable email sending class for automated notifications.
Integrates with Office 365 SMTP for reliable email delivery.

Features:
- Send plain text and HTML emails
- Job completion notifications
- Invoice notifications
- Quote request confirmations
- Order status updates
- Customizable email templates
- Attachment support

Usage:
    from email_sender import EmailSender
    
    sender = EmailSender()
    sender.send_job_completion_email(
        to_email="client@example.com",
        job_number="12345",
        client_name="ABC Company"
    )

Author: InHouse Print Development Team
Date: October 20, 2025
"""

import os
import sys
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailSender:
    """
    Office 365 Email Sender for InHouse Print System
    
    Handles all automated email notifications with customizable templates
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize email sender
        
        Args:
            config_path: Path to database-config.json (optional)
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'config', 'database-config.json'
            )
        
        self.smtp_server = "smtp.office365.com"
        self.smtp_port = 587
        
        # Email credentials
        self.email_username = None
        self.email_password = None
        self.from_address = None
        
        self._load_config(config_path)
    
    def _load_config(self, config_path: str):
        """Load email configuration from config file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Get Email config
            email_config = config.get('ExternalAPIs', {}).get('Email', {}).get('Office365', {})
            
            self.email_username = email_config.get('Username', os.environ.get('OFFICE365_EMAIL'))
            self.email_password = email_config.get('Password', os.environ.get('OFFICE365_PASSWORD'))
            self.from_address = email_config.get('FromAddress', self.email_username)
            
            if self.email_username and self.email_password:
                logger.info(f"Email sender initialized: {self.email_username}")
            else:
                logger.warning("Email credentials not found. Set OFFICE365_EMAIL and OFFICE365_PASSWORD")
            
        except Exception as e:
            logger.error(f"Failed to load email config: {e}")
    
    def send_email(self,
                   to_addresses: List[str],
                   subject: str,
                   body_text: str,
                   body_html: Optional[str] = None,
                   cc_addresses: Optional[List[str]] = None,
                   attachments: Optional[List[str]] = None) -> bool:
        """
        Send email via Office 365 SMTP
        
        Args:
            to_addresses: List of recipient email addresses
            subject: Email subject
            body_text: Plain text email body
            body_html: Optional HTML email body
            cc_addresses: Optional CC recipients
            attachments: Optional list of file paths to attach
            
        Returns:
            True if email sent successfully
        """
        if not self.email_username or not self.email_password:
            logger.error("Email credentials not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_address
            msg['To'] = ', '.join(to_addresses)
            
            if cc_addresses:
                msg['Cc'] = ', '.join(cc_addresses)
            
            # Attach text and HTML parts
            part1 = MIMEText(body_text, 'plain')
            msg.attach(part1)
            
            if body_html:
                part2 = MIMEText(body_html, 'html')
                msg.attach(part2)
            
            # Attach files if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            server.starttls()
            server.login(self.email_username, self.email_password)
            
            # Send to all recipients (to + cc)
            all_recipients = to_addresses + (cc_addresses or [])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent: '{subject}' to {', '.join(to_addresses)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_job_completion_email(self,
                                  to_email: str,
                                  job_number: str,
                                  client_name: str,
                                  job_description: str,
                                  completion_date: Optional[str] = None) -> bool:
        """
        Send job completion notification
        
        Args:
            to_email: Client email address
            job_number: Job ticket number
            client_name: Client name
            job_description: Job description
            completion_date: Optional completion date (defaults to now)
            
        Returns:
            True if email sent successfully
        """
        if completion_date is None:
            completion_date = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        subject = f"Job #{job_number} Complete - InHouse Print"
        
        # Plain text version
        body_text = f"""
Dear {client_name},

Your printing job has been completed and is ready for collection or dispatch.

Job Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Job Number:      {job_number}
Description:     {job_description}
Completion Date: {completion_date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please contact us to arrange collection or confirm delivery details.

Thank you for your business!

Best regards,
InHouse Print Team

---
This is an automated notification from the InHouse Print Management System.
        """
        
        # HTML version
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        .header {{ background-color: #0078D4; color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .content {{ padding: 30px; background-color: #f9f9f9; }}
        .job-details {{ background-color: white; padding: 20px; border-left: 4px solid #0078D4; margin: 20px 0; }}
        .job-details h3 {{ margin-top: 0; color: #0078D4; }}
        .detail-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }}
        .detail-label {{ font-weight: bold; color: #666; }}
        .detail-value {{ color: #333; }}
        .success-badge {{ 
            display: inline-block;
            background-color: #107C10;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 18px;
        }}
        .footer {{ 
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
            background-color: #f0f0f0;
        }}
        .button {{ 
            display: inline-block;
            background-color: #0078D4;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>InHouse Print</h1>
            <div style="margin-top: 15px;">
                <span class="success-badge">✓ Job Complete</span>
            </div>
        </div>
        
        <div class="content">
            <p>Dear <strong>{client_name}</strong>,</p>
            <p>Great news! Your printing job has been completed and is ready for collection or dispatch.</p>
            
            <div class="job-details">
                <h3>Job Details</h3>
                <div class="detail-row">
                    <span class="detail-label">Job Number:</span>
                    <span class="detail-value">{job_number}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Description:</span>
                    <span class="detail-value">{job_description}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Completion Date:</span>
                    <span class="detail-value">{completion_date}</span>
                </div>
            </div>
            
            <p>Please contact us to arrange collection or confirm delivery details.</p>
            <p>Thank you for your business!</p>
            
            <p>Best regards,<br><strong>InHouse Print Team</strong></p>
        </div>
        
        <div class="footer">
            <p>This is an automated notification from the InHouse Print Management System.</p>
            <p>If you have any questions, please contact us.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return self.send_email(
            to_addresses=[to_email],
            subject=subject,
            body_text=body_text,
            body_html=body_html
        )
    
    def send_invoice_email(self,
                          to_email: str,
                          invoice_number: str,
                          client_name: str,
                          total_amount: float,
                          due_date: str,
                          invoice_file: Optional[str] = None) -> bool:
        """
        Send invoice notification
        
        Args:
            to_email: Client email address
            invoice_number: Invoice number
            client_name: Client name
            total_amount: Invoice total amount
            due_date: Payment due date
            invoice_file: Optional path to invoice PDF
            
        Returns:
            True if email sent successfully
        """
        subject = f"Invoice #{invoice_number} - InHouse Print"
        
        # Plain text version
        body_text = f"""
Dear {client_name},

Your invoice is ready.

Invoice Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Invoice Number: {invoice_number}
Amount:         ${total_amount:.2f} AUD
Due Date:       {due_date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{'Invoice attached for your reference.' if invoice_file else 'Invoice available upon request.'}

Please contact us if you have any questions.

Thank you for your business!

Best regards,
InHouse Print Team
        """
        
        # HTML version
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        .header {{ background-color: #0078D4; color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; background-color: #f9f9f9; }}
        .invoice-box {{ background-color: white; padding: 20px; border-left: 4px solid #0078D4; margin: 20px 0; }}
        .amount {{ font-size: 32px; color: #0078D4; font-weight: bold; }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; background-color: #f0f0f0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Invoice Ready</h1>
        </div>
        <div class="content">
            <p>Dear <strong>{client_name}</strong>,</p>
            <p>Your invoice is ready for review.</p>
            
            <div class="invoice-box">
                <h3>Invoice #{invoice_number}</h3>
                <p><strong>Amount:</strong> <span class="amount">${total_amount:.2f}</span> AUD</p>
                <p><strong>Due Date:</strong> {due_date}</p>
            </div>
            
            <p>{'Invoice attached for your reference.' if invoice_file else 'Invoice available upon request.'}</p>
            <p>Please contact us if you have any questions.</p>
            <p>Thank you for your business!</p>
        </div>
        <div class="footer">
            <p>InHouse Print - Automated Notification System</p>
        </div>
    </div>
</body>
</html>
        """
        
        attachments = [invoice_file] if invoice_file else None
        
        return self.send_email(
            to_addresses=[to_email],
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            attachments=attachments
        )
    
    def send_quote_confirmation_email(self,
                                     to_email: str,
                                     quote_number: str,
                                     client_name: str,
                                     description: str) -> bool:
        """
        Send quote request confirmation
        
        Args:
            to_email: Client email address
            quote_number: Quote request number
            client_name: Client name
            description: Quote description
            
        Returns:
            True if email sent successfully
        """
        subject = f"Quote Request #{quote_number} Received - InHouse Print"
        
        body_text = f"""
Dear {client_name},

Thank you for your quote request!

We have received your request and will respond within 24 hours.

Quote Request Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Quote Number: {quote_number}
Description:  {description}
Received:     {datetime.now().strftime('%Y-%m-%d %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

We'll contact you shortly with a detailed quotation.

Best regards,
InHouse Print Team
        """
        
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        .header {{ background-color: #0078D4; color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; background-color: #f9f9f9; }}
        .quote-box {{ background-color: white; padding: 20px; border-left: 4px solid #28a745; margin: 20px 0; }}
        .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Quote Request Received</h1>
        </div>
        <div class="content">
            <p>Dear <strong>{client_name}</strong>,</p>
            <p>Thank you for your quote request!</p>
            
            <div class="quote-box">
                <h3>Quote #{quote_number}</h3>
                <p><strong>Description:</strong> {description}</p>
                <p><strong>Received:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            
            <p>We'll contact you within 24 hours with a detailed quotation.</p>
            <p>Best regards,<br><strong>InHouse Print Team</strong></p>
        </div>
        <div class="footer">
            <p>InHouse Print - Quote Management System</p>
        </div>
    </div>
</body>
</html>
        """
        
        return self.send_email(
            to_addresses=[to_email],
            subject=subject,
            body_text=body_text,
            body_html=body_html
        )


# Example usage
if __name__ == "__main__":
    """
    Example usage for testing
    """
    print("Email Sender Module - InHouse Print System")
    print("=" * 60)
    
    sender = EmailSender()
    
    if sender.email_username and sender.email_password:
        print(f"✓ Email sender configured: {sender.email_username}")
        print("\nReady to send notifications!")
        print("\nExample usage:")
        print("  sender.send_job_completion_email(...)")
        print("  sender.send_invoice_email(...)")
        print("  sender.send_quote_confirmation_email(...)")
    else:
        print("✗ Email credentials not configured")
        print("\nConfigure email in database-config.json or set environment variables:")
        print("  OFFICE365_EMAIL")
        print("  OFFICE365_PASSWORD")
    
    print("=" * 60)
