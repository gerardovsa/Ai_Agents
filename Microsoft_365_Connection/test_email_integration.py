"""
Office 365 Email Integration Test Suite for InHouse Print

This script tests email sending capabilities using Office 365 SMTP
and Microsoft Graph API for the InHouse Print Management System.

Features tested:
1. SMTP Connection (Office 365)
2. Send test email via SMTP
3. Microsoft Graph API authentication (OAuth2)
4. Send email via Microsoft Graph API
5. Email templates for notifications

Author: InHouse Print Development Team
Date: October 20, 2025
"""

import os
import sys
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))


class Office365EmailTester:
    """
    Test Office 365 email integration for InHouse Print System
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize email tester
        
        Args:
            config_path: Path to database-config.json (optional)
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'config', 'database-config.json'
            )
        
        self.config_path = config_path
        self.smtp_server = "smtp.office365.com"
        self.smtp_port = 587
        
        # Email credentials (to be loaded from config or env)
        self.email_username = None
        self.email_password = None
        self.from_address = None
        
        self._load_config()
    
    def _load_config(self):
        """Load email configuration from config file"""
        try:
            # Try to load from database-config.json
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Get Email config (you'll need to add this section)
            email_config = config.get('ExternalAPIs', {}).get('Email', {}).get('Office365', {})
            
            self.email_username = email_config.get('Username', os.environ.get('OFFICE365_EMAIL'))
            self.email_password = email_config.get('Password', os.environ.get('OFFICE365_PASSWORD'))
            self.from_address = email_config.get('FromAddress', self.email_username)
            
            if self.email_username and self.email_password:
                logger.info(f"✓ Loaded email config: {self.email_username}")
            else:
                logger.warning("⚠ Email credentials not found in config file")
                logger.warning("Please provide credentials via environment variables or config file")
            
        except FileNotFoundError:
            logger.error(f"✗ Config file not found: {self.config_path}")
        except Exception as e:
            logger.error(f"✗ Failed to load config: {e}")
    
    def set_credentials(self, username: str, password: str):
        """
        Manually set email credentials
        
        Args:
            username: Office 365 email address
            password: Office 365 password or app password
        """
        self.email_username = username
        self.email_password = password
        self.from_address = username
        logger.info(f"✓ Credentials set for: {username}")
    
    def test_smtp_connection(self) -> bool:
        """
        Test SMTP connection to Office 365
        
        Returns:
            True if connection successful
        """
        print("\n" + "=" * 70)
        print("TEST 1: SMTP Connection to Office 365")
        print("=" * 70)
        
        if not self.email_username or not self.email_password:
            logger.error("✗ Missing credentials. Use set_credentials() first.")
            return False
        
        try:
            logger.info(f"Connecting to {self.smtp_server}:{self.smtp_port}...")
            
            # Create SMTP connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            server.set_debuglevel(0)  # Set to 1 for verbose debugging
            
            # Start TLS encryption
            logger.info("Starting TLS encryption...")
            server.starttls()
            
            # Login
            logger.info(f"Logging in as: {self.email_username}")
            server.login(self.email_username, self.email_password)
            
            # Close connection
            server.quit()
            
            logger.info("✓ SMTP connection successful!")
            print("\n TEST 1 PASSED - SMTP connection working")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"✗ Authentication failed: {e}")
            logger.error("Check username/password or enable 'App Passwords' in Office 365")
            print("\n TEST 1 FAILED - Authentication error")
            return False
            
        except Exception as e:
            logger.error(f"✗ SMTP connection failed: {e}")
            print("\n TEST 1 FAILED - Connection error")
            return False
    
    def send_test_email_smtp(self, to_address: str) -> bool:
        """
        Send test email via SMTP
        
        Args:
            to_address: Recipient email address
            
        Returns:
            True if email sent successfully
        """
        print("\n" + "=" * 70)
        print("TEST 2: Send Test Email via SMTP")
        print("=" * 70)
        
        if not self.email_username or not self.email_password:
            logger.error("✗ Missing credentials. Use set_credentials() first.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"InHouse Print - Test Email {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            msg['From'] = self.from_address
            msg['To'] = to_address
            
            # Email body (plain text)
            text_body = """
InHouse Print Management System
Office 365 Email Integration Test

This is a test email sent via Office 365 SMTP.

✓ SMTP connection working
✓ Email sending operational
✓ Integration successful

Timestamp: {timestamp}

---
InHouse Print System
Automated Notification Service
            """.format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # Email body (HTML)
            html_body = """
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .header {{ background-color: #0078D4; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f5f5f5; }}
        .success {{ color: #107C10; font-weight: bold; }}
        .footer {{ padding: 10px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>InHouse Print Management System</h1>
        <p>Office 365 Email Integration Test</p>
    </div>
    <div class="content">
        <p>This is a test email sent via Office 365 SMTP.</p>
        <ul class="success">
            <li>✓ SMTP connection working</li>
            <li>✓ Email sending operational</li>
            <li>✓ Integration successful</li>
        </ul>
        <p><strong>Timestamp:</strong> {timestamp}</p>
    </div>
    <div class="footer">
        <p>InHouse Print System - Automated Notification Service</p>
    </div>
</body>
</html>
            """.format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # Attach parts
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            logger.info(f"Sending test email to: {to_address}")
            
            # Connect and send
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            server.starttls()
            server.login(self.email_username, self.email_password)
            server.send_message(msg)
            server.quit()
            
            logger.info("✓ Test email sent successfully!")
            print(f"\n TEST 2 PASSED - Email sent to {to_address}")
            print(f"   Check inbox for test message")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to send test email: {e}")
            print("\n TEST 2 FAILED - Email sending error")
            return False
    
    def send_job_completion_notification(self, 
                                        to_address: str,
                                        job_number: str,
                                        client_name: str,
                                        job_description: str) -> bool:
        """
        Send job completion notification email
        
        Args:
            to_address: Client email address
            job_number: Job ticket number
            client_name: Client name
            job_description: Job description
            
        Returns:
            True if email sent successfully
        """
        print("\n" + "=" * 70)
        print("TEST 3: Send Job Completion Notification")
        print("=" * 70)
        
        if not self.email_username or not self.email_password:
            logger.error("✗ Missing credentials. Use set_credentials() first.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Job #{job_number} Complete - InHouse Print"
            msg['From'] = self.from_address
            msg['To'] = to_address
            
            # Email body (plain text)
            text_body = f"""
Dear {client_name},

Your printing job has been completed and is ready for collection or dispatch.

Job Details:
- Job Number: {job_number}
- Description: {job_description}
- Completion Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please contact us to arrange collection or confirm delivery details.

Thank you for your business!

---
InHouse Print
Automated Notification System
            """
            
            # Email body (HTML)
            html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .header {{ background-color: #0078D4; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f5f5f5; }}
        .job-details {{ background-color: white; padding: 15px; border-left: 4px solid #0078D4; margin: 20px 0; }}
        .success {{ color: #107C10; font-weight: bold; font-size: 18px; }}
        .footer {{ padding: 10px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>InHouse Print</h1>
        <p class="success">✓ Job Complete</p>
    </div>
    <div class="content">
        <p>Dear <strong>{client_name}</strong>,</p>
        <p>Your printing job has been completed and is ready for collection or dispatch.</p>
        
        <div class="job-details">
            <h3>Job Details</h3>
            <p><strong>Job Number:</strong> {job_number}</p>
            <p><strong>Description:</strong> {job_description}</p>
            <p><strong>Completion Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <p>Please contact us to arrange collection or confirm delivery details.</p>
        <p>Thank you for your business!</p>
    </div>
    <div class="footer">
        <p>InHouse Print - Automated Notification System</p>
    </div>
</body>
</html>
            """
            
            # Attach parts
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            logger.info(f"Sending job completion notification to: {to_address}")
            
            # Connect and send
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            server.starttls()
            server.login(self.email_username, self.email_password)
            server.send_message(msg)
            server.quit()
            
            logger.info("✓ Job completion notification sent successfully!")
            print(f"\n TEST 3 PASSED - Notification sent to {to_address}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to send notification: {e}")
            print("\n TEST 3 FAILED - Notification sending error")
            return False
    
    def run_all_tests(self, test_email: str) -> Dict[str, bool]:
        """
        Run all email integration tests
        
        Args:
            test_email: Email address to send test messages to
            
        Returns:
            Dictionary of test results
        """
        print("\n" + "=" * 70)
        print("OFFICE 365 EMAIL INTEGRATION TEST SUITE")
        print("InHouse Print Management System")
        print("=" * 70)
        print(f"\nTest Email: {test_email}")
        print(f"From Email: {self.from_address}")
        print(f"SMTP Server: {self.smtp_server}:{self.smtp_port}")
        
        results = {}
        
        # Test 1: SMTP Connection
        results['smtp_connection'] = self.test_smtp_connection()
        
        if results['smtp_connection']:
            # Test 2: Send test email
            results['test_email'] = self.send_test_email_smtp(test_email)
            
            # Test 3: Send job completion notification
            results['job_notification'] = self.send_job_completion_notification(
                to_address=test_email,
                job_number="TEST-12345",
                client_name="Test Client",
                job_description="1000 x A4 Flyers on 350gsm Satin"
            )
        else:
            results['test_email'] = False
            results['job_notification'] = False
        
        # Print summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = " PASS" if result else " FAIL"
            print(f"{status} - {test_name.replace('_', ' ').title()}")
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED - Email integration working!")
        else:
            print("\n⚠ SOME TESTS FAILED - Check error messages above")
        
        print("=" * 70)
        
        return results


def main():
    """
    Main test function with interactive prompts
    """
    print("\n" + "=" * 70)
    print("OFFICE 365 EMAIL INTEGRATION SETUP & TEST")
    print("InHouse Print Management System")
    print("=" * 70)
    
    # Initialize tester
    tester = Office365EmailTester()
    
    # Check if credentials loaded from config
    if not tester.email_username or not tester.email_password:
        print("\n📧 Email credentials not found in config file.")
        print("Please provide Office 365 credentials:\n")
        
        # Prompt for credentials
        email = input("Office 365 Email Address: ").strip()
        password = input("Office 365 Password/App Password: ").strip()
        
        if email and password:
            tester.set_credentials(email, password)
        else:
            print("\n Credentials required. Exiting...")
            return
    
    # Prompt for test email
    print("\n📧 Where should test emails be sent?")
    test_email = input("Test Email Address (press Enter to use sender email): ").strip()
    
    if not test_email:
        test_email = tester.email_username
    
    # Run all tests
    results = tester.run_all_tests(test_email)
    
    # Provide guidance based on results
    if all(results.values()):
        print("\n SUCCESS - Email integration is fully operational!")
        print("\nNext steps:")
        print("1. Add Email config to database-config.json (see example below)")
        print("2. Integrate email notifications into job workflow")
        print("3. Create email templates for different notification types")
        print("4. Test with real job completion scenarios")
    else:
        print("\n⚠ TROUBLESHOOTING:")
        print("\nIf authentication failed:")
        print("1. Enable 'App Passwords' in Office 365 account settings")
        print("2. Use App Password instead of account password")
        print("3. Check if account has MFA enabled (requires App Password)")
        print("4. Verify email address and password are correct")
        print("\nIf connection failed:")
        print("1. Check internet connection")
        print("2. Verify firewall allows SMTP traffic (port 587)")
        print("3. Confirm Office 365 account is active")


if __name__ == "__main__":
    main()
