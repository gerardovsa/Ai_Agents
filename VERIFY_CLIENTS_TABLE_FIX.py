import sys
sys.path.insert(0, '.')
from tools.implementations.inhouse_query import inhouse_search_database, inhouse_execute_query
import json

print("=" * 80)
print("COMPREHENSIVE INHOUSE DATABASE FIX VERIFICATION")
print("=" * 80)

# Test 1: Search across all tables (including Clients)
print("\n\n1️⃣  SEARCH TEST: 'business cards' across Orders, JobTickets, Clients")
print("-" * 80)
result1 = inhouse_search_database(
    search_text='business cards',
    limit_per_table=3
)
print(f"✅ Success: {result1['success']}")
print(f"✅ Total matches: {result1['total_matches']}")
print(f"✅ Tables searched: {result1['searched_tables']}")
for table, rows in result1.get('results', {}).items():
    if isinstance(rows, dict) and 'error' in rows:
        print(f"❌ {table}: ERROR - {rows['error']}")
    else:
        print(f"✅ {table}: {len(rows)} matches")

# Test 2: Search Clients table by email
print("\n\n2️⃣  CLIENTS EMAIL SEARCH: '@bigpond.com'")
print("-" * 80)
result2 = inhouse_search_database(
    search_text='%@bigpond.com',
    tables=['Clients'],
    limit_per_table=5
)
print(f"✅ Success: {result2['success']}")
print(f"✅ Total matches: {result2['total_matches']}")
if result2['total_matches'] > 0:
    sample = result2['results']['Clients'][0]
    print(f"✅ Sample customer: {sample['Name']} ({sample['defaultEmail']})")

# Test 3: Search Clients by name
print("\n\n3️⃣  CLIENTS NAME SEARCH: 'Megan'")
print("-" * 80)
result3 = inhouse_search_database(
    search_text='megan',
    tables=['Clients'],
    limit_per_table=5
)
print(f"✅ Success: {result3['success']}")
print(f"✅ Total matches: {result3['total_matches']}")
if result3['total_matches'] > 0:
    for client in result3['results']['Clients']:
        print(f"   - {client['Name']} ({client.get('defaultEmail', 'no email')})")

# Test 4: Join Orders to Clients
print("\n\n4️⃣  ORDERS + CLIENTS JOIN TEST")
print("-" * 80)
result4 = inhouse_execute_query(
    """SELECT TOP 5 
        o.OrderID,
        o.ClientName AS OrderClientName,
        c.Name AS ClientsName,
        c.defaultEmail,
        c.Phone
    FROM Orders o
    LEFT JOIN Clients c ON o.CustomerMYOB_ID = c.ContactID
    WHERE o.OrderDate > DATEADD(month, -1, GETDATE())
    ORDER BY o.OrderDate DESC"""
)
print(f"✅ Success: {result4['success']}")
print(f"✅ Rows returned: {result4['row_count']}")
if result4['success'] and result4['row_count'] > 0:
    sample = result4['rows'][0]
    print(f"✅ Sample: Order #{sample['OrderID']} - {sample['OrderClientName']}")
    print(f"   Email: {sample.get('defaultEmail', 'N/A')}")
    print(f"   Phone: {sample.get('Phone', 'N/A')}")

# Test 5: Verify column names
print("\n\n5️⃣  CLIENTS TABLE SCHEMA VERIFICATION")
print("-" * 80)
result5 = inhouse_execute_query(
    """SELECT COLUMN_NAME 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'Clients' 
    ORDER BY ORDINAL_POSITION"""
)
actual_columns = [row['COLUMN_NAME'] for row in result5['rows']]
expected_columns = ['ContactID', 'Name', 'AddressLine1', 'AddressCity', 
                   'PostalCode', 'Phone', 'BusinessID', 'LastSyncTime', 'defaultEmail']

print(f"✅ Actual columns: {', '.join(actual_columns)}")
print(f"✅ Expected columns: {', '.join(expected_columns)}")
print(f"✅ Match: {actual_columns == expected_columns}")

# Final summary
print("\n\n" + "=" * 80)
print("📊 VERIFICATION SUMMARY")
print("=" * 80)
all_tests = [
    ("Multi-table search (Orders, JobTickets, Clients)", result1['success']),
    ("Clients email search", result2['success']),
    ("Clients name search", result3['success']),
    ("Orders + Clients JOIN", result4['success']),
    ("Schema verification", actual_columns == expected_columns)
]

passed = sum(1 for _, success in all_tests if success)
total = len(all_tests)

for test_name, success in all_tests:
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")

print(f"\n{'✅' if passed == total else '⚠️'} TOTAL: {passed}/{total} tests passed")

if passed == total:
    print("\n🎉 ALL TESTS PASSED - Clients table fix is complete!")
else:
    print(f"\n⚠️ {total - passed} test(s) failed - review errors above")

print("=" * 80)
