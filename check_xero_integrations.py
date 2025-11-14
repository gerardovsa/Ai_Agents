"""
Check Xero for Any Integrations/Automations
Check if Xero has webhooks, connected apps, or automation pulling from FRED
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
import json

# Load environment
env_path = Path(__file__).parent / '.env.master'
load_dotenv(env_path)

XERO_TOKEN_URL = "https://identity.xero.com/connect/token"
XERO_API_BASE = "https://api.xero.com/api.xro/2.0"

# Business 1: InHouse Print
CLIENT_ID = os.getenv('XERO_PRINT_CLIENT_ID')
CLIENT_SECRET = os.getenv('XERO_PRINT_CLIENT_SECRET')

def get_access_token():
    """Get Xero API access token"""
    response = requests.post(
        XERO_TOKEN_URL,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={'grant_type': 'client_credentials', 'scope': 'accounting.transactions accounting.contacts'},
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"❌ Failed to get token: {response.status_code}")
        print(response.text)
        return None

def check_organisation_info(token):
    """Check Xero organization details"""
    print("\n" + "="*70)
    print("🏢 CHECKING XERO ORGANIZATION INFO")
    print("="*70)
    
    response = requests.get(
        f"{XERO_API_BASE}/Organisation",
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
    )
    
    if response.status_code == 200:
        org = response.json()['Organisations'][0]
        print(f"\n📊 Organization: {org['Name']}")
        print(f"   API Key: {org.get('APIKey', 'N/A')}")
        print(f"   Timezone: {org.get('Timezone', 'N/A')}")
        print(f"   Edition: {org.get('Edition', 'N/A')}")
        print(f"   Plan: {org.get('PlanType', 'N/A')}")
        print(f"   Country: {org.get('CountryCode', 'N/A')}")
        
        # Check for integrations
        if 'ExternalLinks' in org:
            print(f"\n🔗 External Links Found:")
            for link in org['ExternalLinks']:
                print(f"   - {link}")
        else:
            print("\n✅ No External Links configured")
            
        return org
    else:
        print(f"❌ Failed to get organization: {response.status_code}")
        return None

def check_invoices_recent(token):
    """Check recent invoices for patterns"""
    print("\n" + "="*70)
    print("📄 CHECKING RECENT INVOICES (for automation patterns)")
    print("="*70)
    
    # Get last 10 invoices
    response = requests.get(
        f"{XERO_API_BASE}/Invoices",
        params={'page': 1, 'order': 'Date DESC'},
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
    )
    
    if response.status_code == 200:
        invoices = response.json().get('Invoices', [])
        print(f"\n✅ Found {len(invoices)} recent invoices")
        
        # Check for automation patterns
        automation_indicators = []
        
        for inv in invoices[:10]:
            # Check Reference field for FRED Order IDs
            ref = inv.get('Reference', '')
            if 'Order' in ref or 'FRED' in ref:
                automation_indicators.append(f"Invoice {inv['InvoiceNumber']}: Reference contains '{ref}' (might indicate automation)")
            
            # Check if invoices were created within seconds of each other (batch)
            # Check line item descriptions for patterns
            for item in inv.get('LineItems', []):
                desc = item.get('Description', '')
                if 'FRED' in desc.upper() or 'AUTO' in desc.upper():
                    automation_indicators.append(f"Invoice {inv['InvoiceNumber']}: Line item mentions automation")
        
        if automation_indicators:
            print(f"\n⚠️  POSSIBLE AUTOMATION DETECTED:")
            for indicator in automation_indicators:
                print(f"   {indicator}")
        else:
            print(f"\n✅ No automation patterns detected in recent invoices")
            print(f"   (All invoices appear to be manually created)")
            
        # Show sample
        if invoices:
            inv = invoices[0]
            print(f"\n📋 Most Recent Invoice Sample:")
            print(f"   Number: {inv.get('InvoiceNumber')}")
            print(f"   Date: {inv.get('Date')}")
            print(f"   Contact: {inv.get('Contact', {}).get('Name')}")
            print(f"   Reference: {inv.get('Reference', 'N/A')}")
            print(f"   Status: {inv.get('Status')}")
            print(f"   Total: ${inv.get('Total', 0):.2f}")
            
    else:
        print(f"❌ Failed to get invoices: {response.status_code}")

def check_contacts_recent(token):
    """Check recent contacts for sync patterns"""
    print("\n" + "="*70)
    print("👥 CHECKING RECENT CONTACTS (for sync patterns)")
    print("="*70)
    
    response = requests.get(
        f"{XERO_API_BASE}/Contacts",
        params={'page': 1, 'order': 'UpdatedDateUTC DESC'},
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
    )
    
    if response.status_code == 200:
        contacts = response.json().get('Contacts', [])
        print(f"\n✅ Found {len(contacts)} contacts")
        
        # Check for FRED references
        fred_refs = []
        for contact in contacts[:10]:
            # Check AccountNumber field
            acc_num = contact.get('AccountNumber', '')
            if acc_num and ('FRED' in acc_num.upper() or 'MYOB' in acc_num.upper()):
                fred_refs.append(f"Contact '{contact['Name']}': AccountNumber='{acc_num}'")
            
            # Check ContactNumber
            cont_num = contact.get('ContactNumber', '')
            if cont_num:
                fred_refs.append(f"Contact '{contact['Name']}': ContactNumber='{cont_num}' (may be FRED ID)")
        
        if fred_refs:
            print(f"\n🔗 POSSIBLE FRED INTEGRATION:")
            for ref in fred_refs[:5]:
                print(f"   {ref}")
        else:
            print(f"\n✅ No obvious FRED references in contact records")
            
    else:
        print(f"❌ Failed to get contacts: {response.status_code}")

def check_tracking_categories(token):
    """Check for tracking categories (might indicate FRED integration)"""
    print("\n" + "="*70)
    print("🏷️  CHECKING TRACKING CATEGORIES")
    print("="*70)
    
    response = requests.get(
        f"{XERO_API_BASE}/TrackingCategories",
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
    )
    
    if response.status_code == 200:
        categories = response.json().get('TrackingCategories', [])
        if categories:
            print(f"\n📊 Found {len(categories)} tracking categories:")
            for cat in categories:
                print(f"\n   Category: {cat['Name']}")
                print(f"   Status: {cat.get('Status', 'N/A')}")
                if 'Options' in cat:
                    print(f"   Options: {len(cat['Options'])} values")
                    # Check if FRED is referenced
                    for opt in cat['Options'][:5]:
                        if 'FRED' in opt.get('Name', '').upper():
                            print(f"      ⚠️  Option mentions FRED: {opt['Name']}")
        else:
            print("\n✅ No tracking categories configured")
    else:
        print(f"❌ Failed to get tracking categories: {response.status_code}")

def check_branding_themes(token):
    """Check branding themes"""
    print("\n" + "="*70)
    print("🎨 CHECKING BRANDING THEMES")
    print("="*70)
    
    response = requests.get(
        f"{XERO_API_BASE}/BrandingThemes",
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
    )
    
    if response.status_code == 200:
        themes = response.json().get('BrandingThemes', [])
        print(f"\n✅ Found {len(themes)} branding themes:")
        for theme in themes:
            print(f"\n   Theme: {theme['Name']}")
            print(f"   ID: {theme['BrandingThemeID']}")
            print(f"   Type: {theme.get('Type', 'N/A')}")
    else:
        print(f"❌ Failed to get branding themes: {response.status_code}")

def main():
    print("\n" + "="*70)
    print("🔍 XERO INTEGRATION CHECKER")
    print("   Checking for automations, webhooks, or FRED connections")
    print("="*70)
    
    # Get token
    print("\n🔐 Getting Xero API access token...")
    token = get_access_token()
    
    if not token:
        print("\n❌ Failed to authenticate with Xero")
        return
    
    print("✅ Authenticated successfully")
    
    # Run checks
    check_organisation_info(token)
    check_invoices_recent(token)
    check_contacts_recent(token)
    check_tracking_categories(token)
    check_branding_themes(token)
    
    # Final summary
    print("\n" + "="*70)
    print("📋 SUMMARY")
    print("="*70)
    print("\n🔍 What to look for:")
    print("   1. Invoice References mentioning 'FRED' or 'Order #'")
    print("   2. Contact AccountNumbers matching FRED client IDs")
    print("   3. Tracking Categories that link to FRED")
    print("   4. Batch invoice creation patterns")
    print("   5. External Links in organization settings")
    print("\n💡 If NO automation found:")
    print("   - Invoices are created MANUALLY in Xero web interface")
    print("   - Then manually linked back to FRED")
    print("\n✅ Check complete!")

if __name__ == "__main__":
    main()
