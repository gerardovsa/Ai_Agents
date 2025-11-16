"""
Test Xero Metadata Tools
Tests the new metadata and range-based tools for understanding data scale
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env.master'
if env_path.exists():
    load_dotenv(env_path)

from tools.implementations.xero import (
    xero_get_data_metadata,
    xero_get_contacts_by_date_range,
    xero_get_invoices_by_date_range,
    xero_get_payments_by_date_range
)
import json

print("=" * 80)
print("XERO METADATA TOOLS TEST")
print("=" * 80)

# Test 1: Get metadata overview
print("\n1. Testing xero_get_data_metadata()...")
print("-" * 80)

metadata = xero_get_data_metadata(business_id=1)

if metadata['success']:
    print("SUCCESS - Retrieved metadata")
    print(f"\nBusiness: {metadata['business_name']}")
    
    summary = metadata['summary']
    
    print("\nCONTACTS:")
    print(f"  Total: {summary['contacts']['total']:,}")
    print(f"  Date Range: {summary['contacts']['earliest_date']} to {summary['contacts']['latest_date']}")
    print(f"  Size Estimate: {summary['contacts']['estimated_size_kb']:,.2f} KB")
    print(f"  Recent Activity:")
    for period, count in list(summary['contacts']['by_period'].items())[:8]:
        print(f"    {period}: {count:,} contacts")
    
    print("\nINVOICES:")
    print(f"  Total: {summary['invoices']['total']:,}")
    print(f"  Date Range: {summary['invoices']['earliest_date']} to {summary['invoices']['latest_date']}")
    print(f"  Size Estimate: {summary['invoices']['estimated_size_kb']:,.2f} KB")
    print(f"  Recent Activity:")
    for period, count in list(summary['invoices']['by_period'].items())[:8]:
        print(f"    {period}: {count:,} invoices")
    
    print("\nPAYMENTS:")
    print(f"  Total: {summary['payments']['total']:,}")
    print(f"  Date Range: {summary['payments']['earliest_date']} to {summary['payments']['latest_date']}")
    print(f"  Size Estimate: {summary['payments']['estimated_size_kb']:,.2f} KB")
    print(f"  Recent Activity:")
    for period, count in list(summary['payments']['by_period'].items())[:8]:
        print(f"    {period}: {count:,} payments")
    
    print("\nBANK TRANSACTIONS:")
    print(f"  Total: {summary['bank_transactions']['total']:,}")
    print(f"  Date Range: {summary['bank_transactions']['earliest_date']} to {summary['bank_transactions']['latest_date']}")
    print(f"  Size Estimate: {summary['bank_transactions']['estimated_size_kb']:,.2f} KB")
    
    print("\nRECOMMENDATIONS:")
    for entity, recommendation in metadata['recommendations'].items():
        print(f"  {entity}: {recommendation}")
    
else:
    print(f"ERROR: {metadata.get('error')}")
    if metadata.get('traceback'):
        print(f"\n{metadata['traceback']}")

# Test 2: Get contacts by date range (last 3 months)
print("\n\n2. Testing xero_get_contacts_by_date_range() - Last 3 Months...")
print("-" * 80)

from datetime import datetime, timedelta
three_months_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
today = datetime.now().strftime('%Y-%m-%d')

contacts_result = xero_get_contacts_by_date_range(
    business_id=1,
    from_date=three_months_ago,
    to_date=today,
    limit=50  # Just get 50 for testing
)

if contacts_result['success']:
    print("SUCCESS - Retrieved contacts by date range")
    print(f"\nDate Range: {contacts_result['date_range']['from']} to {contacts_result['date_range']['to']}")
    print(f"Contacts Found: {contacts_result['contact_count']:,}")
    print(f"Truncated: {contacts_result['truncated']}")
    print(f"Size Estimate: {contacts_result['estimated_size_kb']} KB")
    
    print("\nSample Contacts:")
    for i, contact in enumerate(contacts_result['contacts'][:5], 1):
        print(f"  {i}. {contact['name']}")
        print(f"     Updated: {contact['updated_date']}")
        print(f"     Customer: {contact['is_customer']}, Supplier: {contact['is_supplier']}")
else:
    print(f"ERROR: {contacts_result.get('error')}")

# Test 3: Get invoices by date range (last 1 month)
print("\n\n3. Testing xero_get_invoices_by_date_range() - Last Month...")
print("-" * 80)

one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

invoices_result = xero_get_invoices_by_date_range(
    business_id=1,
    from_date=one_month_ago,
    to_date=today,
    status='AUTHORISED',
    limit=50
)

if invoices_result['success']:
    print("SUCCESS - Retrieved invoices by date range")
    print(f"\nDate Range: {invoices_result['date_range']['from']} to {invoices_result['date_range']['to']}")
    print(f"Status Filter: {invoices_result['status_filter']}")
    print(f"Invoices Found: {invoices_result['invoice_count']:,}")
    print(f"Truncated: {invoices_result['truncated']}")
    print(f"Size Estimate: {invoices_result['estimated_size_kb']} KB")
    
    print("\nSample Invoices:")
    for i, invoice in enumerate(invoices_result['invoices'][:5], 1):
        print(f"  {i}. {invoice['invoice_number']} - {invoice['contact_name']}")
        print(f"     Date: {invoice['date']}, Due: {invoice['due_date']}")
        print(f"     Amount: ${invoice['amount_due']:,.2f}")
else:
    print(f"ERROR: {invoices_result.get('error')}")

# Test 4: Get payments by date range (last 2 weeks)
print("\n\n4. Testing xero_get_payments_by_date_range() - Last 2 Weeks...")
print("-" * 80)

two_weeks_ago = (datetime.now() - timedelta(weeks=2)).strftime('%Y-%m-%d')

payments_result = xero_get_payments_by_date_range(
    business_id=1,
    from_date=two_weeks_ago,
    to_date=today,
    limit=50
)

if payments_result['success']:
    print("SUCCESS - Retrieved payments by date range")
    print(f"\nDate Range: {payments_result['date_range']['from']} to {payments_result['date_range']['to']}")
    print(f"Payments Found: {payments_result['payment_count']:,}")
    print(f"Truncated: {payments_result['truncated']}")
    print(f"Size Estimate: {payments_result['estimated_size_kb']} KB")
    
    print("\nSample Payments:")
    for i, payment in enumerate(payments_result['payments'][:5], 1):
        print(f"  {i}. Invoice {payment['invoice_number']}")
        print(f"     Date: {payment['date']}")
        print(f"     Amount: ${payment['amount']:,.2f}")
else:
    print(f"ERROR: {payments_result.get('error')}")

print("\n" + "=" * 80)
print("METADATA TOOLS TEST COMPLETE")
print("=" * 80)

# Save results to file
results = {
    "metadata": metadata,
    "contacts_by_range": contacts_result,
    "invoices_by_range": invoices_result,
    "payments_by_range": payments_result
}

with open('xero_metadata_test_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to: xero_metadata_test_results.json")
