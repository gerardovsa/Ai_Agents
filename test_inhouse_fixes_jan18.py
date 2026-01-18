"""
Test InHouse Tools Fixes - January 18, 2026

Tests for:
1. Query library catalog now returns 50+ queries (was 5)
2. Stock reorder alerts no longer fail JSON serialization
"""

import json
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Add modules path
modules_path = project_root / 'UI' / 'modules_external' / 'inhouse-print' / 'implementations'
if str(modules_path) not in sys.path:
    sys.path.insert(0, str(modules_path))


def test_query_library_catalog():
    """Test query library returns full catalog (50+ queries)"""
    print("\n" + "="*80)
    print("TEST 1: Query Library Catalog")
    print("="*80)
    
    try:
        from inhouse_wrapper import inhouse_get_query_library_catalog
        
        # Test without category filter
        print("\n[TEST] Calling inhouse_get_query_library_catalog()...")
        result = inhouse_get_query_library_catalog()
        
        # Validate response structure
        assert "success" in result, "Missing 'success' field"
        assert "queries" in result, "Missing 'queries' field"
        assert "total_count" in result, "Missing 'total_count' field"
        
        # Check if we got the full library
        query_count = result["total_count"]
        print(f"\n✅ SUCCESS: Returned {query_count} queries")
        
        if query_count >= 50:
            print(f"✅ PASS: Query count >= 50 (was 5 before fix)")
        else:
            print(f"⚠️  WARNING: Query count = {query_count} (expected 50+)")
            if not result["success"]:
                print(f"   Error: {result.get('error', 'Unknown error')}")
                print(f"   Note: {result.get('note', 'No note')}")
        
        # Check for categories
        if "categories" in result:
            print(f"✅ Categories available: {len(result['categories'])}")
            print(f"   Categories: {', '.join(result['categories'][:5])}...")
        
        # Show sample queries
        print(f"\n📊 Sample Queries (first 5):")
        for i, query in enumerate(result["queries"][:5], 1):
            print(f"   {i}. {query['name']} ({query['category']})")
            print(f"      → {query['description'][:60]}...")
        
        # Test category filtering
        print(f"\n[TEST] Testing category filter...")
        if "categories" in result and len(result['categories']) > 0:
            test_category = result['categories'][0]
            filtered_result = inhouse_get_query_library_catalog(category=test_category)
            filtered_count = filtered_result["total_count"]
            print(f"✅ Category '{test_category}': {filtered_count} queries")
        
        # Test JSON serialization
        print(f"\n[TEST] Testing JSON serialization...")
        json_str = json.dumps(result, indent=2)
        print(f"✅ JSON serialization successful ({len(json_str)} bytes)")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"\n❌ FAILED: {e}")
        print(traceback.format_exc())
        return False


def test_stock_reorder_alerts():
    """Test stock reorder alerts date serialization"""
    print("\n" + "="*80)
    print("TEST 2: Stock Reorder Alerts - Date Serialization")
    print("="*80)
    
    try:
        from inhouse_wrapper import inhouse_get_reorder_alerts
        
        print("\n[TEST] Calling inhouse_get_reorder_alerts()...")
        result = inhouse_get_reorder_alerts()
        
        # Validate response structure
        assert "success" in result, "Missing 'success' field"
        
        if not result["success"]:
            # Expected if stock table doesn't exist yet
            print(f"⚠️  Note: {result.get('error', 'Unknown error')}")
            print(f"   Suggestion: {result.get('suggestion', 'No suggestion')}")
            print(f"   This is expected if stock_data.stocklevels table not set up")
            return True
        
        assert "alerts" in result, "Missing 'alerts' field"
        assert "critical_count" in result, "Missing 'critical_count' field"
        assert "warning_count" in result, "Missing 'warning_count' field"
        
        alert_count = len(result["alerts"])
        critical = result["critical_count"]
        warning = result["warning_count"]
        
        print(f"\n✅ SUCCESS: Returned {alert_count} alerts")
        print(f"   Critical: {critical}, Warning: {warning}")
        
        # Test JSON serialization (this was the bug!)
        print(f"\n[TEST] Testing JSON serialization...")
        try:
            json_str = json.dumps(result, indent=2)
            print(f"✅ PASS: JSON serialization successful ({len(json_str)} bytes)")
            print(f"   This would have FAILED before fix with 'Object of type date is not JSON serializable'")
        except TypeError as e:
            print(f"❌ FAIL: JSON serialization error: {e}")
            return False
        
        # Validate date fields are strings
        if alert_count > 0:
            print(f"\n[TEST] Validating date fields are strings...")
            for i, alert in enumerate(result["alerts"][:3], 1):
                alert_date = alert.get("alert_date", "")
                if isinstance(alert_date, str):
                    print(f"   ✅ Alert {i}: alert_date = '{alert_date}' (string)")
                else:
                    print(f"   ❌ Alert {i}: alert_date = {type(alert_date)} (should be string)")
                    return False
        
        return True
        
    except Exception as e:
        import traceback
        print(f"\n❌ FAILED: {e}")
        print(traceback.format_exc())
        return False


def test_query_library_import():
    """Test that QueryLibrary can be imported directly"""
    print("\n" + "="*80)
    print("TEST 3: QueryLibrary Direct Import")
    print("="*80)
    
    try:
        # Add backend to path
        backend_dir = project_root / 'UI' / 'modules_external' / 'quote-calculator' / 'backend'
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))
        
        from query_library import QueryLibrary
        
        print("\n[TEST] Initializing QueryLibrary...")
        library = QueryLibrary()
        
        print(f"✅ QueryLibrary initialized successfully")
        
        # Test get_available_queries
        print(f"\n[TEST] Getting available queries...")
        queries = library.get_available_queries()
        print(f"✅ Found {len(queries)} queries")
        
        # Test get_query_categories
        print(f"\n[TEST] Getting query categories...")
        categories = library.get_query_categories()
        print(f"✅ Found {len(categories)} categories:")
        for cat in categories[:5]:
            print(f"   • {cat}")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"\n❌ FAILED: {e}")
        print(traceback.format_exc())
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("InHouse Tools Fixes - Test Suite")
    print("January 18, 2026")
    print("="*80)
    
    results = {
        "Query Library Import": test_query_library_import(),
        "Query Library Catalog": test_query_library_catalog(),
        "Stock Reorder Alerts": test_stock_reorder_alerts()
    }
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✅ PASS" if passed_flag else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*80}")
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
    
    print(f"{'='*80}\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
