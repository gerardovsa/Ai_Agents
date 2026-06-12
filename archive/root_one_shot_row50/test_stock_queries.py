"""Test script for 6 fixed stock management queries"""
import sys
sys.path.insert(0, 'UI/modules_external/quote-calculator/backend')

from query_library import QueryLibrary

def main():
    lib = QueryLibrary()
    
    print("=" * 80)
    print("TESTING 6 FIXED STOCK MANAGEMENT QUERIES")
    print("=" * 80)
    print()
    
    # Test 1: stock_usage_analytics
    print("1️⃣  Testing stock_usage_analytics (GSM usage from JobTickets)")
    try:
        sql = lib.get_query('stock_usage_analytics', days_back=30, top_n=5)
        print(f"   ✅ SQL Generated ({len(sql)} chars)")
        print(f"   Preview: {sql[:200]}...")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
    
    # Test 2: stock_pricing_profitability
    print("2️⃣  Testing stock_pricing_profitability (Revenue by paper type)")
    try:
        sql = lib.get_query('stock_pricing_profitability', months=3)
        print(f"   ✅ SQL Generated ({len(sql)} chars)")
        print(f"   Preview: {sql[:200]}...")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
    
    # Test 3: client_stock_preferences
    print("3️⃣  Testing client_stock_preferences (Customer paper preferences)")
    try:
        sql = lib.get_query('client_stock_preferences', months=12, min_orders=3)
        print(f"   ✅ SQL Generated ({len(sql)} chars)")
        print(f"   Preview: {sql[:200]}...")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
    
    # Test 4: stock_inventory_master
    print("4️⃣  Testing stock_inventory_master (Available paper types catalog)")
    try:
        sql = lib.get_query('stock_inventory_master', status_filter='all', stock_type='all')
        print(f"   ✅ SQL Generated ({len(sql)} chars)")
        print(f"   Preview: {sql[:200]}...")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
    
    # Test 5: stock_reorder_alerts
    print("5️⃣  Testing stock_reorder_alerts (Returns empty - inventory not tracked)")
    try:
        sql = lib.get_query('stock_reorder_alerts', urgency='all')
        print(f"   ✅ SQL Generated ({len(sql)} chars)")
        print(f"   Preview: {sql[:200]}...")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
    
    # Test 6: stock_cost_trends
    print("6️⃣  Testing stock_cost_trends (Returns empty - cost history not tracked)")
    try:
        sql = lib.get_query('stock_cost_trends', stock_type='all', months=24)
        print(f"   ✅ SQL Generated ({len(sql)} chars)")
        print(f"   Preview: {sql[:200]}...")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
    
    # Get validation status
    print("=" * 80)
    print("VALIDATION STATUS REPORT")
    print("=" * 80)
    
    try:
        status = lib.get_query_status_report()
        print(f"Total Queries: {status['total_queries']}")
        print(f"Validated Queries: {status['validated_queries']}")
        print(f"Validation Rate: {status['validation_rate']}")
        print()
        
        # Expected: 58 total (52 previously + 6 stock queries)
        if status['validated_queries'] >= 58:
            print("✅ SUCCESS: All 58+ queries validated (52 previous + 6 stock queries)")
        else:
            print(f"⚠️  PARTIAL: {status['validated_queries']} validated, expected 58+")
    except Exception as e:
        print(f"❌ Error getting status: {e}")
    
    print("=" * 80)

if __name__ == '__main__':
    main()
