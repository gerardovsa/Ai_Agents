"""
Test: Create Quote with Template and Attach to Draft Email Workflow

This test demonstrates the complete workflow:
1. Find customer contact
2. Get available branding themes (templates)
3. Create quote with template
4. Get quote details
5. Create draft email with quote information

Note: Email will be saved as DRAFT in Outlook (not sent automatically)
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.implementations.xero import xero_get_contacts, xero_get_contact_by_id
from tools.implementations.xero_quotes import xero_create_quote, xero_get_quote_by_id, xero_get_branding_themes
# Note: Outlook email functions would be imported here if needed
# from tools.implementations.microsoft_outlook_tools import outlook_send_email

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "═" * 80)
    print(f"  {title}")
    print("═" * 80)

def print_step(step_num: int, description: str):
    """Print a formatted step header"""
    print(f"\n📍 STEP {step_num}: {description}")
    print("-" * 80)

def main():
    print_section("🔄 QUOTE CREATION + EMAIL WORKFLOW TEST")
    print("\n📋 Workflow Steps:")
    print("   1. Find customer contact")
    print("   2. Get branding themes (templates)")
    print("   3. Create quote with template")
    print("   4. Get quote details with PDF URL")
    print("   5. Create draft email with quote info")
    
    business_id = 1  # InHouse Print
    
    # ============================================================================
    # STEP 1: Find Customer Contact
    # ============================================================================
    print_step(1, "Find Customer Contact")
    
    try:
        contacts_result = xero_get_contacts(business_id=business_id, limit=5)
        
        if not contacts_result.get('success'):
            print(f"❌ Failed to get contacts: {contacts_result.get('error')}")
            return
        
        contacts = contacts_result.get('contacts', [])
        if not contacts:
            print("❌ No contacts found")
            return
        
        # Use first contact for demo
        contact = contacts[0]
        contact_id = contact['contact_id']
        contact_name = contact['name']
        
        print(f"✅ Found contact: {contact_name}")
        print(f"   Contact ID: {contact_id}")
        
        # Get full contact details including email
        contact_details = xero_get_contact_by_id(business_id=business_id, contact_id=contact_id)
        
        if contact_details.get('success'):
            email = contact_details.get('email_address', 'N/A')
            print(f"   Email: {email}")
        
    except Exception as e:
        print(f"❌ Error in Step 1: {e}")
        return
    
    # ============================================================================
    # STEP 2: Get Branding Themes (Templates)
    # ============================================================================
    print_step(2, "Get Available Branding Themes (Quote Templates)")
    
    try:
        themes_result = xero_get_branding_themes(business_id=business_id)
        
        if not themes_result.get('success'):
            error_msg = themes_result.get('error', 'Unknown error')
            print(f"⚠️  Could not fetch branding themes: {error_msg}")
            
            if '401' in str(error_msg) or 'Unauthorized' in str(error_msg):
                print("   This requires 'accounting.settings.read' OAuth scope")
                print("   📝 Note: We can still create quotes using template_name parameter")
            
            # Use default template name instead
            template_name = "Standard Invoice"
            print(f"\n   Using default template: '{template_name}'")
        else:
            themes = themes_result.get('branding_themes', [])
            print(f"✅ Found {len(themes)} branding themes:")
            
            for i, theme in enumerate(themes[:3], 1):
                print(f"   {i}. {theme['name']} (ID: {theme['branding_theme_id'][:8]}...)")
            
            # Use first theme or default
            template_name = themes[0]['name'] if themes else "Standard Invoice"
            print(f"\n   📌 Selected template: '{template_name}'")
    
    except Exception as e:
        print(f"⚠️  Error in Step 2: {e}")
        template_name = "Standard Invoice"
        print(f"   Using fallback template: '{template_name}'")
    
    # ============================================================================
    # STEP 3: Create Quote with Template
    # ============================================================================
    print_step(3, "Create Quote with Template and Line Items")
    
    try:
        # Define line items for the quote
        line_items = [
            {
                "description": "Business Cards - 1000qty, 350GSM Premium",
                "quantity": 1,
                "unit_amount": 150.00,
                "account_code": "200"
            },
            {
                "description": "Letterhead - 500 sheets, Full Color",
                "quantity": 1,
                "unit_amount": 85.00,
                "account_code": "200"
            }
        ]
        
        print(f"   Creating quote for: {contact_name}")
        print(f"   Template: {template_name}")
        print(f"   Line Items: {len(line_items)}")
        
        quote_result = xero_create_quote(
            business_id=business_id,
            contact_id=contact_id,
            line_items=line_items,
            template_name=template_name,
            title="Professional Printing Services Quote",
            expiry_date="2025-12-31",
            summary="Thank you for your interest in our printing services. This quote includes premium business cards and letterhead."
        )
        
        if not quote_result.get('success'):
            print(f"❌ Failed to create quote: {quote_result.get('error')}")
            return
        
        quote_id = quote_result.get('quote_id')
        quote_number = quote_result.get('quote_number')
        quote_total = quote_result.get('total', 0)
        quote_status = quote_result.get('status')
        
        print(f"✅ Quote created successfully!")
        print(f"   Quote Number: {quote_number}")
        print(f"   Quote ID: {quote_id}")
        print(f"   Status: {quote_status}")
        print(f"   Total: ${quote_total:.2f}")
    
    except Exception as e:
        print(f"❌ Error in Step 3: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ============================================================================
    # STEP 4: Get Quote Details
    # ============================================================================
    print_step(4, "Get Complete Quote Details")
    
    try:
        quote_details = xero_get_quote_by_id(business_id=business_id, quote_id=quote_id)
        
        if not quote_details.get('success'):
            print(f"❌ Failed to get quote details: {quote_details.get('error')}")
        else:
            print(f"✅ Retrieved quote details")
            
            # Check for PDF URL
            pdf_url = quote_details.get('pdf_url', 'N/A')
            line_items_count = len(quote_details.get('line_items', []))
            
            print(f"   Line Items: {line_items_count}")
            print(f"   PDF URL: {pdf_url[:50]}..." if len(pdf_url) > 50 else f"   PDF URL: {pdf_url}")
            
            if pdf_url and pdf_url != 'N/A':
                print("   💡 PDF can be downloaded and attached to email")
    
    except Exception as e:
        print(f"⚠️  Error in Step 4: {e}")
    
    # ============================================================================
    # STEP 5: Create Draft Email with Quote Info
    # ============================================================================
    print_step(5, "Create Draft Email with Quote Information")
    
    try:
        # Get contact email (use dummy if not available)
        if 'email' in locals() and email and email != 'N/A':
            recipient_email = email
        else:
            # Use a placeholder - in real scenario, get from contact details
            recipient_email = "customer@example.com"
            print(f"   ⚠️  Using placeholder email: {recipient_email}")
        
        # Prepare email content
        email_subject = f"Quote {quote_number} - Professional Printing Services"
        
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c5aa0;">Your Printing Services Quote</h2>
            
            <p>Dear {contact_name},</p>
            
            <p>Thank you for your interest in our professional printing services. Please find your quote details below:</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #2c5aa0; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Quote Number:</strong> {quote_number}</p>
                <p style="margin: 5px 0;"><strong>Total Amount:</strong> ${quote_total:.2f}</p>
                <p style="margin: 5px 0;"><strong>Valid Until:</strong> December 31, 2025</p>
            </div>
            
            <h3>Quote Items:</h3>
            <ul>
                <li>Business Cards - 1000qty, 350GSM Premium - $150.00</li>
                <li>Letterhead - 500 sheets, Full Color - $85.00</li>
            </ul>
            
            <p>If you have any questions or would like to proceed with this order, please don't hesitate to contact us.</p>
            
            <p style="margin-top: 30px;">Best regards,<br>
            <strong>InHouse Print Team</strong></p>
        </body>
        </html>
        """
        
        print(f"   Recipient: {recipient_email}")
        print(f"   Subject: {email_subject}")
        print(f"   Body: HTML formatted with quote details")
        
        # NOTE: Outlook client would need to be initialized with OAuth credentials
        # For demo purposes, we'll show what would be called
        
        print("\n   📧 Email Draft Configuration:")
        print(f"      To: {recipient_email}")
        print(f"      Subject: {email_subject}")
        print(f"      Quote Total: ${quote_total:.2f}")
        print(f"      Quote Number: {quote_number}")
        
        print("\n   ⚠️  To actually create the draft, you would call:")
        print("      outlook_send_email(")
        print(f"          to=['{recipient_email}'],")
        print(f"          subject='{email_subject}',")
        print("          body='<html content>',")
        print("          body_type='html'")
        print("      )")
        
        print("\n   💡 Note: outlook_send_email creates DRAFTS (not sent automatically)")
        print("      User must manually send from Outlook Drafts folder")
    
    except Exception as e:
        print(f"⚠️  Error in Step 5: {e}")
    
    # ============================================================================
    # SUMMARY
    # ============================================================================
    print_section("✅ WORKFLOW COMPLETE")
    
    print("\n📊 Summary:")
    print(f"   ✅ Customer: {contact_name}")
    print(f"   ✅ Quote Created: {quote_number}")
    print(f"   ✅ Quote Total: ${quote_total:.2f}")
    print(f"   ✅ Template Used: {template_name}")
    print(f"   ✅ Email Ready: Draft configuration prepared")
    
    print("\n🎯 Next Steps:")
    print("   1. Download quote PDF from Xero")
    print("   2. Encode PDF to base64")
    print("   3. Call outlook_send_email() with attachment")
    print("   4. Open Outlook and send draft manually")
    
    print("\n" + "═" * 80)

if __name__ == "__main__":
    main()
