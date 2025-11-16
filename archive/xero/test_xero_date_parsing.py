"""
Test Xero tool date parsing fix
Tests that dates are properly parsed from /Date(timestamp)/ format to YYYY-MM-DD
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

from tools.implementations.xero import xero_get_invoices

print("Testing Xero date parsing fix...")
print("=" * 80)

# Test with unpaid invoices
result = xero_get_invoices(
    business_id=1,
    status='AUTHORISED'
)

if result['success']:
    print(f"✅ Successfully retrieved {result['invoice_count']} invoices")
    print(f"   Business: {result['business_name']}")
    
    # Check first few invoices for date formatting
    print("\nSample invoices with date formatting:")
    for i, invoice in enumerate(result['invoices'][:5]):
        print(f"\n{i+1}. Invoice #{invoice['invoice_number']}")
        print(f"   Date: {invoice['date']} (should be YYYY-MM-DD format)")
        print(f"   Due Date: {invoice['due_date']} (should be YYYY-MM-DD format)")
        print(f"   Status: {invoice['status']}")
        print(f"   Amount Due: ${invoice['amount_due']:.2f}")
        
        # Validate date format
        if invoice['date']:
            if len(invoice['date']) == 10 and invoice['date'][4] == '-' and invoice['date'][7] == '-':
                print(f"   ✅ Date format is correct")
            else:
                print(f"   ❌ Date format is WRONG: {invoice['date']}")
        
        if invoice['due_date']:
            if len(invoice['due_date']) == 10 and invoice['due_date'][4] == '-' and invoice['due_date'][7] == '-':
                print(f"   ✅ Due date format is correct")
            else:
                print(f"   ❌ Due date format is WRONG: {invoice['due_date']}")
    
    print("\n" + "=" * 80)
    print("Date parsing test complete!")
    
else:
    print(f"❌ Error: {result.get('error')}")
    if result.get('traceback'):
        print(f"\nTraceback:\n{result['traceback']}")
