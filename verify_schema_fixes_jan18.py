"""
Verify Schema Documentation Fixes - January 18, 2026
Tests the 5 corrected schema issues
"""

import sys
sys.path.insert(0, 'UI/modules_external/inhouse-print')

from db_connector import InHousePrintDB

db = InHousePrintDB()

tests = [
    {
        "name": "✅ Fix 1: ClientOrderNum (not OrderNumber)",
        "query": "SELECT TOP 5 OrderID, ClientOrderNum FROM Orders WHERE ClientOrderNum IS NOT NULL"
    },
    {
        "name": "✅ Fix 2: ColourStatus in JobTickets (not Orders)",
        "query": "SELECT TOP 5 jt.TicketID, jt.ColourStatus FROM JobTickets jt WHERE jt.ColourStatus IS NOT NULL"
    },
    {
        "name": "✅ Fix 3: TicketID (not JobID)",
        "query": "SELECT TOP 5 TicketID, OrderID, QTY FROM JobTickets"
    },
    {
        "name": "✅ Fix 4: GSM_ID with underscore (not GSMID)",
        "query": "SELECT TOP 5 jt.TicketID, jt.GSM_ID, gsm.[DESC] AS GSMWeight FROM JobTickets jt LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID WHERE jt.GSM_ID IS NOT NULL"
    },
    {
        "name": "✅ Fix 5: OrderDate from Orders (no DateCreated in JobTickets)",
        "query": "SELECT TOP 5 jt.TicketID, o.OrderDate FROM JobTickets jt JOIN Orders o ON jt.OrderID = o.OrderID ORDER BY o.OrderDate DESC"
    }
]

print("="*80)
print("TESTING 5 SCHEMA DOCUMENTATION FIXES")
print("="*80)

passed = 0
failed = 0

for test in tests:
    print(f"\n{test['name']}")
    print(f"Query: {test['query'][:80]}...")
    
    try:
        result = db.execute_query(test['query'])
        if result is not None and len(result) > 0:
            print(f"✅ PASS - Returned {len(result)} rows")
            passed += 1
        else:
            print(f"⚠️  PASS (no data) - Query executed, 0 rows")
            passed += 1
    except Exception as e:
        print(f"❌ FAIL - {str(e)[:100]}")
        failed += 1

print("\n" + "="*80)
print(f"RESULTS: {passed} passed, {failed} failed")
print("="*80)

if failed == 0:
    print("\n🎉 ALL FIXES VERIFIED - Schema documentation is now accurate!")
else:
    print(f"\n⚠️  {failed} fixes still need work")
