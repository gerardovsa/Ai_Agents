"""
Test Xero Limit Parameter Fixes - December 8, 2025

Tests all bug fixes implemented from Code Archeology analysis:
- Bug #1: Missing limit parameter in xero_get_accounts (FIXED)
- Bug #3: Type conversion for string limit values (FIXED)
- Reduced default limits from 1000 to 100 for better performance

Expected Results:
- All tools accept both int and string limit values
- Default limits are more conservative (50-100 instead of 1000)
- Tools handle API/JSON string inputs correctly
"""

from tools.implementations.xero import (
    xero_get_accounts,
    xero_get_accounts_metadata,
    xero_get_contacts,
    xero_get_payments,
    xero_get_invoices_by_date_range,
    xero_get_contacts_by_date_range,
    xero_get_payments_by_date_range,
    xero_get_bank_transactions_by_date_range
)

print("=" * 80)
print("XERO LIMIT PARAMETER FIXES - COMPREHENSIVE TEST")
print("=" * 80 + "\n")

business_id = 1  # InHouse Print

# Test 1: Bug #1 Fix - xero_get_accounts now has limit parameter
print("Test 1: xero_get_accounts with integer limit (Bug #1 fix)")
print("-" * 80)
result = xero_get_accounts(business_id=business_id, limit=10)
if result.get('success'):
    print(f"✅ SUCCESS - Returned {result.get('account_count', 0)} accounts")
    print(f"   Limit applied: {result.get('limit_applied')}")
    print(f"   Truncated: {result.get('truncated')}")
else:
    print(f"❌ FAILED - Error: {result.get('error', 'Unknown error')[:100]}")
print()

# Test 2: Bug #3 Fix - Type conversion handles string limits
print("Test 2: xero_get_accounts with STRING limit (Bug #3 fix)")
print("-" * 80)
result = xero_get_accounts(business_id=business_id, limit="15")  # Pass string
if result.get('success'):
    print(f"✅ SUCCESS - Accepted string limit and returned {result.get('account_count', 0)} accounts")
    print(f"   Limit applied: {result.get('limit_applied')} (type: {type(result.get('limit_applied')).__name__})")
else:
    print(f"❌ FAILED - Error: {result.get('error', 'Unknown error')[:100]}")
print()

# Test 3: xero_get_contacts with string limit
print("Test 3: xero_get_contacts with STRING limit")
print("-" * 80)
result = xero_get_contacts(business_id=business_id, limit="20")
if result.get('success'):
    print(f"✅ SUCCESS - Returned {result.get('contact_count', 0)} contacts")
    print(f"   Limit applied: {result.get('limit_applied')}")
else:
    print(f"❌ FAILED - Error: {result.get('error', 'Unknown error')[:100]}")
print()

# Test 4: xero_get_payments with reduced default limit (now 100 instead of 50)
print("Test 4: xero_get_payments with default limit (should be 100)")
print("-" * 80)
result = xero_get_payments(business_id=business_id)
if result.get('success'):
    print(f"✅ SUCCESS - Returned {result.get('payment_count', 0)} payments")
    print(f"   Default limit applied: {result.get('limit_applied')}")
    print(f"   Truncated: {result.get('truncated')}")
else:
    print(f"❌ FAILED - Error: {result.get('error', 'Unknown error')[:100]}")
print()

# Test 5: Date range tool with string limit
print("Test 5: xero_get_invoices_by_date_range with STRING limit")
print("-" * 80)
result = xero_get_invoices_by_date_range(
    business_id=business_id,
    from_date="2025-11-01",
    to_date="2025-11-30",
    limit="50"  # String limit
)
if result.get('success'):
    print(f"✅ SUCCESS - Returned {result.get('invoice_count', 0)} invoices")
    print(f"   Date range: {result.get('date_range', {}).get('from')} to {result.get('date_range', {}).get('to')}")
    print(f"   Limit applied: {result.get('limit_applied')}")
else:
    print(f"❌ FAILED - Error: {result.get('error', 'Unknown error')[:100]}")
print()

# Test 6: Contacts by date range with integer limit
print("Test 6: xero_get_contacts_by_date_range with INTEGER limit")
print("-" * 80)
result = xero_get_contacts_by_date_range(
    business_id=business_id,
    from_date="2025-11-01",
    to_date="2025-11-30",
    limit=25  # Integer limit
)
if result.get('success'):
    print(f"✅ SUCCESS - Returned {result.get('contact_count', 0)} contacts")
    print(f"   Limit applied: {result.get('limit_applied')}")
else:
    print(f"❌ FAILED - Error: {result.get('error', 'Unknown error')[:100]}")
print()

# Test 7: Payments by date range with string limit
print("Test 7: xero_get_payments_by_date_range with STRING limit")
print("-" * 80)
result = xero_get_payments_by_date_range(
    business_id=business_id,
    from_date="2025-11-01",
    to_date="2025-11-30",
    limit="30"  # String limit
)
if result.get('success'):
    print(f"✅ SUCCESS - Returned {result.get('payment_count', 0)} payments")
    print(f"   Limit applied: {result.get('limit_applied')}")
else:
    print(f"❌ FAILED - Error: {result.get('error', 'Unknown error')[:100]}")
print()

# Test 8: Bank transactions with default limit (now 100)
print("Test 8: xero_get_bank_transactions_by_date_range with default limit")
print("-" * 80)
result = xero_get_bank_transactions_by_date_range(
    business_id=business_id,
    from_date="2025-11-01",
    to_date="2025-11-30"
)
if result.get('success'):
    print(f"✅ SUCCESS - Returned {result.get('transaction_count', 0)} transactions")
    print(f"   Default limit applied: {result.get('limit_applied')}")
    if 'cash_flow_summary' in result:
        summary = result['cash_flow_summary']
        print(f"   Cash Flow: Spend=${summary.get('total_spend', 0):,.2f}, Receive=${summary.get('total_receive', 0):,.2f}, Net=${summary.get('net_cash_flow', 0):,.2f}")
else:
    print(f"❌ FAILED - Error: {result.get('error', 'Unknown error')[:100]}")
print()

# Test 9: Invalid string limit (should use default)
print("Test 9: xero_get_accounts with INVALID string limit (should use default)")
print("-" * 80)
result = xero_get_accounts(business_id=business_id, limit="invalid")
if result.get('success'):
    print(f"✅ SUCCESS - Handled invalid limit gracefully")
    print(f"   Fallback limit applied: {result.get('limit_applied')} (should be 50)")
    print(f"   Returned {result.get('account_count', 0)} accounts")
else:
    print(f"❌ FAILED - Error: {result.get('error', 'Unknown error')[:100]}")
print()

# Test 10: xero_get_accounts_metadata (scope issue - may fail with 401)
print("Test 10: xero_get_accounts_metadata (may fail due to scope issue)")
print("-" * 80)
result = xero_get_accounts_metadata(business_id=business_id, limit="25")
if result.get('success'):
    print(f"✅ SUCCESS - Returned metadata")
    print(f"   Total accounts: {result.get('summary', {}).get('total_accounts_analyzed', 0)}")
    print(f"   Limit applied: {result.get('summary', {}).get('limit_applied')}")
else:
    error = result.get('error', 'Unknown error')
    if '401' in error or 'Unauthorized' in error:
        print(f"⚠️  EXPECTED FAILURE - 401 Unauthorized (OAuth scope issue)")
        print(f"   Error message: {error[:200]}")
        print(f"   → User action required: Enable 'accounting.settings.read' scope in Xero Developer Portal")
    else:
        print(f"❌ UNEXPECTED FAILURE - Error: {error[:200]}")
print()

print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("Expected outcomes:")
print("✅ Tests 1-9: Should all pass (bug fixes implemented)")
print("⚠️  Test 10: May fail with 401 (requires Xero scope configuration)")
print()
print("Key improvements:")
print("1. All tools accept both integer and string limit values")
print("2. Invalid limits gracefully fallback to defaults")
print("3. More conservative defaults (50-100 instead of 1000)")
print("4. Better error messages for authentication issues")
print("=" * 80)
