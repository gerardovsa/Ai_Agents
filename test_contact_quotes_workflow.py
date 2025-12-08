"""
Test Contact + Quotes Workflow
Demonstrates how to:
1. Get contact details by ID
2. Get all quotes for that contact
"""

from tools.implementations.xero import xero_get_contacts, xero_get_contact_by_id
from tools.implementations.xero_quotes import xero_list_quotes

print('\n' + '='*80)
print('XERO CONTACT + QUOTES WORKFLOW TEST')
print('='*80 + '\n')

# Step 1: Find a contact (limit to 5 for demo)
print('Step 1: Getting contacts list...')
contacts_result = xero_get_contacts(business_id=1, limit=5)

if contacts_result['success']:
    print(f"✅ Found {contacts_result['contact_count']} contacts")
    
    if contacts_result['contacts']:
        # Pick the first contact
        first_contact = contacts_result['contacts'][0]
        contact_id = first_contact['contact_id']
        contact_name = first_contact['name']
        
        print(f"\n📋 Selected Contact: {contact_name}")
        print(f"   Contact ID: {contact_id}")
        
        # Step 2: Get detailed contact information
        print(f"\nStep 2: Getting detailed contact information...")
        contact_detail = xero_get_contact_by_id(business_id=1, contact_id=contact_id)
        
        if contact_detail['success']:
            print(f"✅ Contact Details Retrieved")
            contact_data = contact_detail['contact']
            print(f"   Name: {contact_data['name']}")
            print(f"   Email: {contact_data['email']}")
            print(f"   Customer: {contact_data['is_customer']}")
            print(f"   Supplier: {contact_data['is_supplier']}")
            print(f"   Status: {contact_data['status']}")
            
            if contact_data['phones']:
                print(f"   Phones: {len(contact_data['phones'])} phone number(s)")
            
            if contact_data['addresses']:
                print(f"   Addresses: {len(contact_data['addresses'])} address(es)")
            
            if contact_data['contact_persons']:
                print(f"   Contact Persons: {len(contact_data['contact_persons'])} person(s)")
            
            # Step 3: Get quotes for this contact
            print(f"\nStep 3: Getting quotes for {contact_name}...")
            quotes_result = xero_list_quotes(
                business_id=1, 
                contact_id=contact_id,
                page_size=10  # Limit to 10 quotes for demo
            )
            
            if quotes_result['success']:
                quote_count = quotes_result['pagination']['returned_count']
                print(f"✅ Found {quote_count} quote(s) for this contact")
                
                if quotes_result['quotes']:
                    print(f"\n📊 Recent Quotes:")
                    for i, quote in enumerate(quotes_result['quotes'][:5], 1):
                        print(f"\n   Quote #{i}:")
                        print(f"      Number: {quote['quote_number']}")
                        print(f"      Status: {quote['status']}")
                        print(f"      Date: {quote['date']}")
                        print(f"      Total: ${quote['total']:.2f}" if quote['total'] else "      Total: N/A")
                        if quote['title']:
                            print(f"      Title: {quote['title']}")
                else:
                    print(f"   ℹ️  No quotes found for this contact")
            else:
                print(f"❌ Error getting quotes: {quotes_result['error']}")
        else:
            print(f"❌ Error getting contact details: {contact_detail['error']}")
    else:
        print("ℹ️  No contacts found")
else:
    print(f"❌ Error getting contacts: {contacts_result['error']}")

print('\n' + '='*80)
print('WORKFLOW COMPLETE')
print('='*80 + '\n')

print('💡 USAGE SUMMARY:')
print('   1. xero_get_contacts() - List contacts with optional search')
print('   2. xero_get_contact_by_id() - Get full contact details')
print('   3. xero_list_quotes(contact_id=...) - Get all quotes for contact')
print('\n   You can also filter quotes by date range and status!')
print('='*80 + '\n')
