"""
Comprehensive test suite for all 15 schema fixes (January 18, 2026)
Tests each fix with real SQL against InHouse Print database

First 5 fixes (already verified):
1. Orders.ClientOrderNum (not OrderNumber)
2. JobTickets.ColourStatus (not Orders.ColourStatus)
3. JobTickets.TicketID (not JobID)
4. JobTickets.GSM_ID (not GSMID)
5. Orders.OrderDate (no DateCreated in JobTickets)

Next 10 fixes (new):
6. GSM.DESC (uppercase, not [Desc])
7. Orders.InvoiceNumber
8. Orders.InvoiceDate
9. Orders.UserID
10. Orders.ShippingType
11. JobTickets.CelloYes
12. JobTickets.FrontCelloMatt/Gloss
13. JobTickets.BackCelloMatt/Gloss
14. JobTickets.FoldYes/FoldDesc
15. JobTickets.StitchYes/StitchDesc/DieCut/Drill/Score
"""

import sys
from pathlib import Path

# Add parent directory to path for InHousePrintDB import
db_connector_dir = Path(__file__).resolve().parent / 'UI' / 'modules_external' / 'inhouse-print'
sys.path.insert(0, str(db_connector_dir))

from db_connector import InHousePrintDB

def run_test(test_num: int, test_name: str, query: str) -> bool:
    """Run a single test query and report results"""
    print(f"\n{'='*80}")
    print(f"TEST {test_num}: {test_name}")
    print(f"{'='*80}")
    print(f"Query:\n{query}\n")
    
    try:
        db = InHousePrintDB()
        results = db.execute_query(query)
        
        if results is None or (hasattr(results, 'empty') and results.empty):
            print(f"❌ FAILED: No results returned")
            return False
        
        row_count = len(results) if hasattr(results, '__len__') else 1
        print(f"✅ PASSED: {row_count} rows returned")
        
        # Show first row
        if hasattr(results, 'head'):
            print(f"\nFirst row:\n{results.head(1).to_dict('records')}")
        elif hasattr(results, '__getitem__'):
            print(f"\nFirst row:\n{results[0]}")
        else:
            print(f"\nResult:\n{results}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def main():
    """Run all 15 tests"""
    print("="*80)
    print("COMPREHENSIVE SCHEMA FIX VERIFICATION (15 Tests)")
    print("="*80)
    
    tests = []
    
    # TESTS 1-5: Already verified (re-run for completeness)
    tests.append((
        1,
        "Orders.ClientOrderNum (not OrderNumber)",
        """
        SELECT TOP 5
            o.OrderID,
            o.ClientOrderNum,
            o.ClientName
        FROM Orders o
        WHERE o.ClientOrderNum IS NOT NULL
        ORDER BY o.OrderDate DESC
        """
    ))
    
    tests.append((
        2,
        "JobTickets.ColourStatus (not in Orders)",
        """
        SELECT TOP 5
            jt.TicketID,
            jt.ColourStatus,
            o.ClientName
        FROM JobTickets jt
        JOIN Orders o ON jt.OrderID = o.OrderID
        WHERE jt.ColourStatus IS NOT NULL
        ORDER BY o.OrderDate DESC
        """
    ))
    
    tests.append((
        3,
        "JobTickets.TicketID primary key (not JobID)",
        """
        SELECT TOP 5
            jt.TicketID,
            jt.OrderID,
            jt.QTY
        FROM JobTickets jt
        ORDER BY jt.TicketID DESC
        """
    ))
    
    tests.append((
        4,
        "JobTickets.GSM_ID with underscore (not GSMID)",
        """
        SELECT TOP 5
            jt.TicketID,
            jt.GSM_ID,
            gsm.[DESC] AS GSMDesc
        FROM JobTickets jt
        LEFT JOIN GSM gsm ON jt.GSM_ID = gsm.GSM_ID
        WHERE jt.GSM_ID IS NOT NULL
        ORDER BY jt.TicketID DESC
        """
    ))
    
    tests.append((
        5,
        "Orders.OrderDate (no DateCreated in JobTickets)",
        """
        SELECT TOP 5
            o.OrderID,
            o.OrderDate,
            o.ClientName,
            jt.TicketID
        FROM Orders o
        JOIN JobTickets jt ON o.OrderID = jt.OrderID
        ORDER BY o.OrderDate DESC
        """
    ))
    
    # TESTS 6-15: New fixes
    tests.append((
        6,
        "GSM.[DESC] with square brackets (reserved keyword)",
        """
        SELECT TOP 5
            gsm.GSM_ID,
            gsm.[DESC]
        FROM GSM gsm
        ORDER BY gsm.GSM_ID
        """
    ))
    
    tests.append((
        7,
        "Orders.InvoiceNumber column exists",
        """
        SELECT TOP 5
            o.OrderID,
            o.InvoiceNumber,
            o.ClientName
        FROM Orders o
        WHERE o.InvoiceNumber IS NOT NULL
        ORDER BY o.OrderDate DESC
        """
    ))
    
    tests.append((
        8,
        "Orders.InvoiceDate column exists",
        """
        SELECT TOP 5
            o.OrderID,
            o.InvoiceNumber,
            o.InvoiceDate,
            o.Invoiced
        FROM Orders o
        WHERE o.InvoiceDate IS NOT NULL
        ORDER BY o.OrderDate DESC
        """
    ))
    
    tests.append((
        9,
        "Orders.UserID column exists",
        """
        SELECT TOP 5
            o.OrderID,
            o.UserID,
            o.ClientName
        FROM Orders o
        WHERE o.UserID IS NOT NULL
        ORDER BY o.OrderDate DESC
        """
    ))
    
    tests.append((
        10,
        "Orders.ShippingType column exists",
        """
        SELECT TOP 5
            o.OrderID,
            o.ShippingType,
            o.ClientName
        FROM Orders o
        WHERE o.ShippingType IS NOT NULL
        ORDER BY o.OrderDate DESC
        """
    ))
    
    tests.append((
        11,
        "JobTickets.CelloYes column exists",
        """
        SELECT TOP 5
            jt.TicketID,
            jt.CelloYes,
            o.ClientName
        FROM JobTickets jt
        JOIN Orders o ON jt.OrderID = o.OrderID
        WHERE jt.CelloYes = 1
        ORDER BY o.OrderDate DESC
        """
    ))
    
    tests.append((
        12,
        "JobTickets front celloglaze columns",
        """
        SELECT TOP 5
            jt.TicketID,
            jt.FrontCelloNone,
            jt.FrontCelloMatt,
            jt.FrontCelloGloss,
            o.ClientName
        FROM JobTickets jt
        JOIN Orders o ON jt.OrderID = o.OrderID
        WHERE jt.CelloYes = 1
        ORDER BY o.OrderDate DESC
        """
    ))
    
    tests.append((
        13,
        "JobTickets back celloglaze columns",
        """
        SELECT TOP 5
            jt.TicketID,
            jt.BackCelloNone,
            jt.BackCelloMatt,
            jt.BackCelloGloss,
            o.ClientName
        FROM JobTickets jt
        JOIN Orders o ON jt.OrderID = o.OrderID
        WHERE jt.CelloYes = 1
        ORDER BY o.OrderDate DESC
        """
    ))
    
    tests.append((
        14,
        "JobTickets.FoldYes and FoldDesc",
        """
        SELECT TOP 5
            jt.TicketID,
            jt.FoldYes,
            jt.FoldDesc,
            o.ClientName
        FROM JobTickets jt
        JOIN Orders o ON jt.OrderID = o.OrderID
        WHERE jt.FoldYes = 1
        ORDER BY o.OrderDate DESC
        """
    ))
    
    tests.append((
        15,
        "JobTickets finishing operations (Stitch/DieCut/Drill/Score)",
        """
        SELECT TOP 5
            jt.TicketID,
            jt.StitchYes,
            jt.StitchDesc,
            jt.DieCutYes,
            jt.DieCutDesc,
            jt.DrillYes,
            jt.DrillDesc,
            jt.ScoreYes,
            jt.PerfYes,
            jt.ScorePerfDesc,
            o.ClientName
        FROM JobTickets jt
        JOIN Orders o ON jt.OrderID = o.OrderID
        WHERE jt.StitchYes = 1 OR jt.DieCutYes = 1 OR jt.DrillYes = 1
        ORDER BY o.OrderDate DESC
        """
    ))
    
    # Run all tests
    results = []
    for test_num, test_name, query in tests:
        passed = run_test(test_num, test_name, query)
        results.append((test_num, test_name, passed))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed_count = sum(1 for _, _, passed in results if passed)
    total_count = len(results)
    
    for test_num, test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - Test {test_num}: {test_name}")
    
    print("\n" + "="*80)
    print(f"FINAL RESULT: {passed_count}/{total_count} tests passed ({passed_count/total_count*100:.1f}%)")
    print("="*80)
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! Schema documentation is now 100% accurate for tested fields.")
    else:
        print(f"\n⚠️  {total_count - passed_count} tests failed. Review errors above.")
    
    return passed_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
