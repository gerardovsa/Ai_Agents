"""
Test script to fetch raw Xero contact data and see all available fields.
Shows complete contact information structure from Xero API.
"""

import sys
import os
import json
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))
sys.path.insert(0, str(Path(__file__).parent / 'UI' / 'modules_external' / 'xero'))

from xero_routes import XeroAPIClient, BUSINESS_CONFIGS

def fetch_xero_contact_sample():
    """Fetch a sample contact from Xero and display all available fields."""
    
    print("\n" + "="*80)
    print("XERO CONTACT DATA STRUCTURE ANALYSIS")
    print("="*80 + "\n")
    
    for business_id in [1, 2, 3]:
        try:
            business_name = BUSINESS_CONFIGS[business_id]['name']
            print(f"\n{'='*80}")
            print(f"BUSINESS: {business_name} (ID: {business_id})")
            print(f"{'='*80}\n")
            
            # Initialize Xero API client
            client = XeroAPIClient(business_id)
            
            # Fetch contacts (limit to 5 for testing)
            print("Fetching contacts from Xero API...")
            data = client.make_request('GET', 'Contacts', params={'page': 1})
            contacts = data.get('Contacts', [])
            
            print(f"✓ Retrieved {len(contacts)} contacts\n")
            
            if contacts:
                # Show first contact's complete structure
                sample_contact = contacts[0]
                
                print(f"📋 SAMPLE CONTACT: {sample_contact.get('Name', 'Unknown')}")
                print(f"{'='*80}\n")
                
                print("COMPLETE RAW DATA STRUCTURE:")
                print("-" * 80)
                print(json.dumps(sample_contact, indent=2, default=str))
                print("\n")
                
                # Extract and display key fields
                print("KEY FIELDS AVAILABLE:")
                print("-" * 80)
                
                fields = {
                    'ContactID': sample_contact.get('ContactID'),
                    'ContactNumber': sample_contact.get('ContactNumber'),
                    'Name': sample_contact.get('Name'),
                    'FirstName': sample_contact.get('FirstName'),
                    'LastName': sample_contact.get('LastName'),
                    'EmailAddress': sample_contact.get('EmailAddress'),
                    'BankAccountDetails': sample_contact.get('BankAccountDetails'),
                    'TaxNumber': sample_contact.get('TaxNumber'),
                    'AccountsReceivableTaxType': sample_contact.get('AccountsReceivableTaxType'),
                    'AccountsPayableTaxType': sample_contact.get('AccountsPayableTaxType'),
                    'IsSupplier': sample_contact.get('IsSupplier'),
                    'IsCustomer': sample_contact.get('IsCustomer'),
                    'DefaultCurrency': sample_contact.get('DefaultCurrency'),
                    'ContactStatus': sample_contact.get('ContactStatus'),
                    'ContactPersons': len(sample_contact.get('ContactPersons', [])),
                    'Addresses': len(sample_contact.get('Addresses', [])),
                    'Phones': len(sample_contact.get('Phones', [])),
                    'UpdatedDateUTC': sample_contact.get('UpdatedDateUTC'),
                    'HasAttachments': sample_contact.get('HasAttachments'),
                    'HasValidationErrors': sample_contact.get('HasValidationErrors')
                }
                
                for field, value in fields.items():
                    print(f"  • {field:30s}: {value}")
                
                # Show phone numbers detail
                if sample_contact.get('Phones'):
                    print("\nPHONE NUMBERS:")
                    print("-" * 80)
                    for phone in sample_contact.get('Phones', []):
                        print(f"  • {phone.get('PhoneType', 'Unknown'):15s}: {phone.get('PhoneNumber', 'N/A')}")
                
                # Show addresses detail
                if sample_contact.get('Addresses'):
                    print("\nADDRESSES:")
                    print("-" * 80)
                    for addr in sample_contact.get('Addresses', []):
                        print(f"  • {addr.get('AddressType', 'Unknown')}:")
                        print(f"      Line1: {addr.get('AddressLine1', 'N/A')}")
                        print(f"      Line2: {addr.get('AddressLine2', 'N/A')}")
                        print(f"      City: {addr.get('City', 'N/A')}")
                        print(f"      Region: {addr.get('Region', 'N/A')}")
                        print(f"      PostalCode: {addr.get('PostalCode', 'N/A')}")
                        print(f"      Country: {addr.get('Country', 'N/A')}")
                
                # Show contact persons detail
                if sample_contact.get('ContactPersons'):
                    print("\nCONTACT PERSONS:")
                    print("-" * 80)
                    for person in sample_contact.get('ContactPersons', []):
                        print(f"  • {person.get('FirstName', '')} {person.get('LastName', '')}")
                        print(f"      Email: {person.get('EmailAddress', 'N/A')}")
                        print(f"      Phone: {person.get('PhoneNumbers', [{}])[0].get('PhoneNumber', 'N/A') if person.get('PhoneNumbers') else 'N/A'}")
                
                # Show summary for next 4 contacts
                print(f"\n\nNEXT 4 CONTACTS SUMMARY:")
                print("-" * 80)
                for i, contact in enumerate(contacts[1:5], 2):
                    print(f"\n{i}. {contact.get('Name', 'Unknown')}")
                    print(f"   ID: {contact.get('ContactID')}")
                    print(f"   Email: {contact.get('EmailAddress', 'N/A')}")
                    print(f"   Phone: {contact.get('Phones', [{}])[0].get('PhoneNumber', 'N/A') if contact.get('Phones') else 'N/A'}")
                    print(f"   Type: {'Customer' if contact.get('IsCustomer') else ''} {'Supplier' if contact.get('IsSupplier') else ''}")
                    print(f"   Status: {contact.get('ContactStatus', 'N/A')}")
                
            else:
                print("⚠ No contacts found for this business")
            
            print("\n")
            
        except Exception as e:
            print(f"❌ ERROR for {business_name}: {e}")
            import traceback
            traceback.print_exc()
            print("\n")
    
    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80 + "\n")


if __name__ == '__main__':
    fetch_xero_contact_sample()
