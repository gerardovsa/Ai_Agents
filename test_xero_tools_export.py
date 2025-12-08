"""
Test Xero Contact + Quotes Tools - Export Results to File
Executes the workflow and exports detailed results to test_results.txt
"""

import sys
from datetime import datetime
from tools.implementations.xero import xero_get_contacts, xero_get_contact_by_id
from tools.implementations.xero_quotes import xero_list_quotes

# Output file
OUTPUT_FILE = r"C:\Users\gpoli\GIT\AI_agents\UI\modules_external\xero\test_results\test_results.txt"

def write_header(f):
    """Write test header"""
    f.write("="*100 + "\n")
    f.write("XERO CONTACT + QUOTES TOOLS - TEST RESULTS\n")
    f.write("="*100 + "\n")
    f.write(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Python: {sys.version}\n")
    f.write("="*100 + "\n\n")

def write_section(f, title):
    """Write section header"""
    f.write("\n" + "="*100 + "\n")
    f.write(f"{title}\n")
    f.write("="*100 + "\n\n")

def format_json(data, indent=0):
    """Format dict/list as readable text"""
    lines = []
    prefix = "  " * indent
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.extend(format_json(value, indent + 1))
            else:
                lines.append(f"{prefix}{key}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data, 1):
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}[{i}]:")
                lines.extend(format_json(item, indent + 1))
            else:
                lines.append(f"{prefix}[{i}]: {item}")
    else:
        lines.append(f"{prefix}{data}")
    
    return lines

print(f"\n🔍 Running Xero tools tests and exporting to:\n   {OUTPUT_FILE}\n")

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    write_header(f)
    
    # TEST 1: Get contacts list
    write_section(f, "TEST 1: xero_get_contacts - List contacts with search")
    f.write("Tool: xero_get_contacts\n")
    f.write("Parameters:\n")
    f.write("  - business_id: 1\n")
    f.write("  - search: None\n")
    f.write("  - limit: 5\n\n")
    
    f.write("Executing...\n\n")
    
    try:
        contacts_result = xero_get_contacts(business_id=1, limit=5)
        
        f.write("RESULT:\n")
        f.write("-" * 100 + "\n")
        
        if contacts_result.get('success'):
            f.write(f"✅ SUCCESS\n\n")
            f.write(f"Business: {contacts_result.get('business_name')}\n")
            f.write(f"Contact Count: {contacts_result.get('contact_count')}\n")
            f.write(f"Truncated: {contacts_result.get('truncated')}\n")
            f.write(f"Limit Applied: {contacts_result.get('limit_applied')}\n\n")
            
            f.write("CONTACTS:\n")
            for i, contact in enumerate(contacts_result.get('contacts', []), 1):
                f.write(f"\nContact {i}:\n")
                for line in format_json(contact, 1):
                    f.write(line + "\n")
            
            # Save first contact for next test
            if contacts_result.get('contacts'):
                test_contact = contacts_result['contacts'][0]
                test_contact_id = test_contact['contact_id']
                test_contact_name = test_contact['name']
        else:
            f.write(f"❌ FAILED\n")
            f.write(f"Error: {contacts_result.get('error')}\n")
            test_contact_id = None
            test_contact_name = None
    except Exception as e:
        f.write(f"❌ EXCEPTION: {str(e)}\n")
        test_contact_id = None
        test_contact_name = None
    
    # TEST 2: Get contact details
    if test_contact_id:
        write_section(f, "TEST 2: xero_get_contact_by_id - Get detailed contact information")
        f.write("Tool: xero_get_contact_by_id\n")
        f.write("Parameters:\n")
        f.write(f"  - business_id: 1\n")
        f.write(f"  - contact_id: {test_contact_id}\n\n")
        
        f.write("Executing...\n\n")
        
        try:
            contact_detail = xero_get_contact_by_id(business_id=1, contact_id=test_contact_id)
            
            f.write("RESULT:\n")
            f.write("-" * 100 + "\n")
            
            if contact_detail.get('success'):
                f.write(f"✅ SUCCESS\n\n")
                f.write(f"Business: {contact_detail.get('business_name')}\n\n")
                
                f.write("CONTACT DETAILS:\n")
                contact_data = contact_detail.get('contact', {})
                
                f.write(f"\nBasic Information:\n")
                f.write(f"  Contact ID: {contact_data.get('contact_id')}\n")
                f.write(f"  Contact Number: {contact_data.get('contact_number')}\n")
                f.write(f"  Name: {contact_data.get('name')}\n")
                f.write(f"  Email: {contact_data.get('email')}\n")
                f.write(f"  Status: {contact_data.get('status')}\n")
                f.write(f"  Is Customer: {contact_data.get('is_customer')}\n")
                f.write(f"  Is Supplier: {contact_data.get('is_supplier')}\n")
                
                if contact_data.get('addresses'):
                    f.write(f"\nAddresses ({len(contact_data['addresses'])}):\n")
                    for i, addr in enumerate(contact_data['addresses'], 1):
                        f.write(f"  Address {i}:\n")
                        for line in format_json(addr, 2):
                            f.write(line + "\n")
                
                if contact_data.get('phones'):
                    f.write(f"\nPhones ({len(contact_data['phones'])}):\n")
                    for i, phone in enumerate(contact_data['phones'], 1):
                        f.write(f"  Phone {i}:\n")
                        for line in format_json(phone, 2):
                            f.write(line + "\n")
                
                if contact_data.get('contact_persons'):
                    f.write(f"\nContact Persons ({len(contact_data['contact_persons'])}):\n")
                    for i, person in enumerate(contact_data['contact_persons'], 1):
                        f.write(f"  Person {i}:\n")
                        for line in format_json(person, 2):
                            f.write(line + "\n")
                
                f.write(f"\nAdditional Information:\n")
                f.write(f"  Tax Number: {contact_data.get('tax_number')}\n")
                f.write(f"  Account Number: {contact_data.get('account_number')}\n")
                f.write(f"  Default Currency: {contact_data.get('default_currency')}\n")
                f.write(f"  Website: {contact_data.get('website')}\n")
                
                f.write(f"\nRelated Data Tools:\n")
                related_tools = contact_detail.get('related_data_tools', {})
                for line in format_json(related_tools, 1):
                    f.write(line + "\n")
            else:
                f.write(f"❌ FAILED\n")
                f.write(f"Error: {contact_detail.get('error')}\n")
        except Exception as e:
            f.write(f"❌ EXCEPTION: {str(e)}\n")
    
    # TEST 3: Get quotes for contact
    if test_contact_id:
        write_section(f, "TEST 3: xero_list_quotes - Get quotes for contact")
        f.write("Tool: xero_list_quotes\n")
        f.write("Parameters:\n")
        f.write(f"  - business_id: 1\n")
        f.write(f"  - contact_id: {test_contact_id}\n")
        f.write(f"  - page_size: 10\n\n")
        
        f.write("Executing...\n\n")
        
        try:
            quotes_result = xero_list_quotes(
                business_id=1,
                contact_id=test_contact_id,
                page_size=10
            )
            
            f.write("RESULT:\n")
            f.write("-" * 100 + "\n")
            
            if quotes_result.get('success'):
                f.write(f"✅ SUCCESS\n\n")
                f.write(f"Business: {quotes_result.get('business_name')}\n\n")
                
                pagination = quotes_result.get('pagination', {})
                f.write("PAGINATION:\n")
                f.write(f"  Page: {pagination.get('page')}\n")
                f.write(f"  Page Size: {pagination.get('page_size')}\n")
                f.write(f"  Total Count: {pagination.get('total_count')}\n")
                f.write(f"  Returned Count: {pagination.get('returned_count')}\n")
                f.write(f"  Total Pages: {pagination.get('total_pages')}\n\n")
                
                filters = quotes_result.get('filters', {})
                f.write("FILTERS APPLIED:\n")
                for line in format_json(filters, 1):
                    f.write(line + "\n")
                
                quotes = quotes_result.get('quotes', [])
                f.write(f"\nQUOTES ({len(quotes)}):\n")
                
                if quotes:
                    for i, quote in enumerate(quotes[:5], 1):  # Show first 5
                        f.write(f"\nQuote {i}:\n")
                        f.write(f"  Quote ID: {quote.get('quote_id')}\n")
                        f.write(f"  Quote Number: {quote.get('quote_number')}\n")
                        f.write(f"  Status: {quote.get('status')}\n")
                        f.write(f"  Date: {quote.get('date')}\n")
                        f.write(f"  Expiry Date: {quote.get('expiry_date')}\n")
                        f.write(f"  Title: {quote.get('title')}\n")
                        f.write(f"  Sub Total: ${quote.get('sub_total', 0):.2f}\n" if quote.get('sub_total') else f"  Sub Total: N/A\n")
                        f.write(f"  Total Tax: ${quote.get('total_tax', 0):.2f}\n" if quote.get('total_tax') else f"  Total Tax: N/A\n")
                        f.write(f"  Total: ${quote.get('total', 0):.2f}\n" if quote.get('total') else f"  Total: N/A\n")
                        f.write(f"  Branding Theme ID: {quote.get('branding_theme_id')}\n")
                        f.write(f"  Updated: {quote.get('updated_date_utc')}\n")
                    
                    if len(quotes) > 5:
                        f.write(f"\n... and {len(quotes) - 5} more quotes\n")
                else:
                    f.write("  (No quotes found for this contact)\n")
            else:
                f.write(f"❌ FAILED\n")
                f.write(f"Error: {quotes_result.get('error')}\n")
        except Exception as e:
            f.write(f"❌ EXCEPTION: {str(e)}\n")
    
    # SUMMARY
    write_section(f, "TEST SUMMARY")
    f.write("Tools Tested:\n")
    f.write("  1. ✅ xero_get_contacts - List contacts\n")
    f.write("  2. ✅ xero_get_contact_by_id - Get detailed contact info\n")
    f.write("  3. ✅ xero_list_quotes - Get quotes for contact\n\n")
    
    f.write("Complete Workflow:\n")
    f.write("  Step 1: Search/list contacts → Get contact_id\n")
    f.write("  Step 2: Get full contact details → See addresses, phones, etc.\n")
    f.write("  Step 3: Get all quotes for contact → Filter by contact_id\n\n")
    
    f.write("="*100 + "\n")
    f.write("END OF TEST RESULTS\n")
    f.write("="*100 + "\n")

print(f"\n✅ Test results exported to:\n   {OUTPUT_FILE}\n")
print("📋 Review the file to see detailed tool execution results!")
