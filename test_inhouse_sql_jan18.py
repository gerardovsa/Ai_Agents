"""
Test InHouse Print SQL Execution - Schema Validation
January 18, 2026

Purpose: Run multiple SQL queries to stress-test schema patterns and discover undocumented issues.
"""

import sys
sys.path.insert(0, 'UI/modules_external/inhouse-print')
sys.path.insert(0, 'AI_infrastructure/shared')

from db_connector import InHousePrintDB
import json

def test_sql_queries():
    """Run comprehensive SQL tests to validate schema documentation"""
    
    db = InHousePrintDB()
    
    tests = [
        {
            "name": "Test 1: Orders + Clients JOIN (Basic Pattern)",
            "query": """
                SELECT TOP 10 
                    o.OrderID, 
                    o.OrderNumber, 
                    o.OrderDate, 
                    c.Name AS CustomerName,
                    c.defaultEmail
                FROM Orders o
                LEFT JOIN Clients c ON o.CustomerMYOB_ID = c.ContactID
                ORDER BY o.OrderDate DESC
            """,
            "expected": "SUCCESS - Basic JOIN works"
        },
        {
            "name": "Test 2: JobTickets + PaperSize (Descriptor Column)",
            "query": """
                SELECT TOP 10 
                    jt.JobID, 
                    jt.PaperSizeID, 
                    ps.[Desc] AS PaperSizeDescription
                FROM JobTickets jt
                LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
                WHERE jt.PaperSizeID IS NOT NULL
            """,
            "expected": "SUCCESS - [Desc] requires square brackets"
        },
        {
            "name": "Test 3: ColourStatus Field (Deadline Urgency)",
            "query": """
                SELECT TOP 10 
                    OrderID, 
                    ColourStatus,
                    CASE 
                        WHEN ColourStatus = 1 THEN 'Urgent'
                        WHEN ColourStatus <= 3 THEN 'High Priority'
                        ELSE 'Normal'
                    END AS DeadlinePriority
                FROM Orders
                WHERE ColourStatus IS NOT NULL
                ORDER BY ColourStatus
            """,
            "expected": "SUCCESS - ColourStatus is deadline urgency 1-7, NOT print color"
        },
        {
            "name": "Test 4: Orders.Status Column (Should FAIL)",
            "query": """
                SELECT TOP 10 
                    OrderID, 
                    Status
                FROM Orders
            """,
            "expected": "FAIL - Orders.Status doesn't exist (use Orders.Invoiced bit field)"
        },
        {
            "name": "Test 5: JobTickets.DateCreated Column (Should FAIL)",
            "query": """
                SELECT TOP 10 
                    JobID, 
                    DateCreated
                FROM JobTickets
            """,
            "expected": "FAIL - JobTickets.DateCreated doesn't exist (use Orders.OrderDate with JOIN)"
        },
        {
            "name": "Test 6: BusinessTable (Should FAIL - NEW MISTAKE)",
            "query": """
                SELECT TOP 10 
                    bt.ContactID, 
                    bt.Name
                FROM BusinessTable bt
            """,
            "expected": "FAIL - BusinessTable doesn't exist (use Clients table)"
        },
        {
            "name": "Test 7: Customer Details Query (From Guide)",
            "query": """
                SELECT TOP 20 
                    c.ContactID, 
                    c.Name AS CustomerName, 
                    c.defaultEmail, 
                    c.Phone, 
                    c.AddressLine1,
                    COUNT(o.OrderID) AS TotalOrders
                FROM Clients c
                LEFT JOIN Orders o ON c.ContactID = o.CustomerMYOB_ID
                WHERE c.Name LIKE '%A%'
                GROUP BY c.ContactID, c.Name, c.defaultEmail, c.Phone, c.AddressLine1
                ORDER BY TotalOrders DESC
            """,
            "expected": "SUCCESS - Pattern from schema guide"
        },
        {
            "name": "Test 8: Multiple Reference Table JOINs",
            "query": """
                SELECT TOP 10 
                    jt.JobID,
                    ps.[Desc] AS PaperSize,
                    jt2.[Desc] AS JobType,
                    gsm.[Desc] AS GSM,
                    bt.BindTypeDesc AS BindType
                FROM JobTickets jt
                LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
                LEFT JOIN JobType jt2 ON jt.JobTypeID = jt2.JobTypeID
                LEFT JOIN GSM gsm ON jt.GSMID = gsm.GSMID
                LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindTypeID
                WHERE jt.JobID > 100000
            """,
            "expected": "SUCCESS - Multiple reference table JOINs"
        }
    ]
    
    results = []
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'='*80}")
        print(f"RUNNING TEST {i}: {test['name']}")
        print(f"{'='*80}")
        print(f"QUERY:\n{test['query']}")
        print(f"\nEXPECTED: {test['expected']}")
        print(f"\nRESULT:")
        
        try:
            data = db.execute_query(test['query'])
            
            if data is None or (hasattr(data, 'empty') and data.empty):
                result = {
                    "test": test['name'],
                    "status": "PASS (NO DATA)",
                    "rows": 0,
                    "error": None
                }
                print(f"✅ PASS (NO DATA) - Query executed successfully, returned 0 rows")
            else:
                row_count = len(data) if hasattr(data, '__len__') else 1
                result = {
                    "test": test['name'],
                    "status": "PASS",
                    "rows": row_count,
                    "sample_data": json.loads(data.head(3).to_json(orient='records')) if hasattr(data, 'head') else str(data)[:500],
                    "error": None
                }
                print(f"✅ PASS - Query returned {row_count} rows")
                print(f"Sample data: {json.dumps(result['sample_data'], indent=2)[:500]}")
        
        except Exception as e:
            error_msg = str(e)
            result = {
                "test": test['name'],
                "status": "FAIL",
                "rows": 0,
                "error": error_msg
            }
            print(f"❌ FAIL - Error: {error_msg}")
            
            # Check if this was an expected failure
            if "Should FAIL" in test['expected']:
                print(f"✅ Expected failure confirmed - schema validation working correctly")
        
        results.append(result)
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(1 for r in results if r['status'] in ['PASS', 'PASS (NO DATA)'])
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    expected_fails = sum(1 for i, r in enumerate(results) if r['status'] == 'FAIL' and "Should FAIL" in tests[i]['expected'])
    
    print(f"Total tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Expected failures: {expected_fails}")
    print(f"Unexpected failures: {failed - expected_fails}")
    
    # New schema issues discovered
    print(f"\n{'='*80}")
    print("SCHEMA ISSUES DISCOVERED")
    print(f"{'='*80}")
    
    unexpected_issues = []
    for i, r in enumerate(results):
        if r['status'] == 'FAIL' and "Should FAIL" not in tests[i]['expected']:
            unexpected_issues.append({
                "test": r['test'],
                "error": r['error']
            })
    
    if unexpected_issues:
        print(f"⚠️ Found {len(unexpected_issues)} NEW schema issues:")
        for issue in unexpected_issues:
            print(f"\n  ❌ {issue['test']}")
            print(f"     Error: {issue['error']}")
    else:
        print(f"✅ No new schema issues discovered - documentation is complete!")
    
    return results

if __name__ == "__main__":
    print("InHouse Print SQL Schema Validation Tests")
    print("=" * 80)
    print("Testing schema patterns to discover undocumented issues...")
    print()
    
    results = test_sql_queries()
    
    print(f"\n{'='*80}")
    print("TESTS COMPLETE")
    print(f"{'='*80}")
