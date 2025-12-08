"""
Test: Simple Quote Creation Workflow (Without Template)

This demonstrates creating a quote without specifying a template,
which should use Xero's default styling.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.implementations.xero import xero_get_contacts, xero_get_contact_by_id
from tools.implementations.xero_quotes import xero_create_quote, xero_get_quote_by_id

def main():
    print("\n" + "="*80)
    print("  SIMPLE QUOTE CREATION TEST (NO TEMPLATE)")
    print("="*80)
    
    business_id = 1
    
    # Get a contact
    print("\n📍 Step 1: Finding contact...")
    contacts_result = xero_get_contacts(business_id=business_id, limit=3)
    
    if not contacts_result.get('success') or not contacts_result.get('contacts'):
        print("❌ No contacts found")
        return
    
    contact = contacts_result['contacts'][0]
    contact_id = contact['contact_id']
    contact_name = contact['name']
    print(f"✅ Using contact: {contact_name}")
    
    # Create quote without template
    print("\n📍 Step 2: Creating quote (no template)...")
    
    line_items = [
        {
            "description": "Business Cards - 1000qty",
            "quantity": 1,
            "unit_amount": 150.00,
            "account_code": "200"
        }
    ]
    
    try:
        quote_result = xero_create_quote(
            business_id=business_id,
            contact_id=contact_id,
            line_items=line_items,
            title="Test Quote - Business Cards",
            expiry_date="2025-12-31"
            # No template_name or branding_theme_id - use Xero default
        )
        
        if quote_result.get('success'):
            print(f"✅ Quote created!")
            print(f"   Quote Number: {quote_result.get('quote_number')}")
            print(f"   Quote ID: {quote_result.get('quote_id')}")
            print(f"   Total: ${quote_result.get('total', 0):.2f}")
            print(f"   Status: {quote_result.get('status')}")
            
            # Get details
            print("\n📍 Step 3: Getting quote details...")
            quote_id = quote_result.get('quote_id')
            details = xero_get_quote_by_id(business_id=business_id, quote_id=quote_id)
            
            if details.get('success'):
                print(f"✅ Quote details retrieved")
                print(f"   Line Items: {len(details.get('line_items', []))}")
                pdf_url = details.get('pdf_url', 'N/A')
                print(f"   PDF URL: {pdf_url[:60]}..." if len(pdf_url) > 60 else f"   PDF URL: {pdf_url}")
        else:
            print(f"❌ Quote creation failed: {quote_result.get('error')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
