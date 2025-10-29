"""
Test InHouse Print Database Integration
========================================
Tests the InHouse Print database connection and query execution
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("INHOUSE PRINT DATABASE INTEGRATION TEST")
print("=" * 70)

# Test 1: Import modules
print("\n[TEST 1] Importing modules...")
try:
    # Add AI_infrastructure to path for auth imports
    sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))
    
    from tools.implementations.inhouse_db_connector import InHousePrintDB
    from tools.implementations.inhouse_query_library import InHousePrintQueryLibrary
    from auth.credential_injector import get_inhouse_print_db_credentials
    print("[PASS] All modules imported successfully")
except Exception as e:
    print(f"[FAIL] Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Get credentials
print("\n[TEST 2] Getting database credentials...")
try:
    creds = get_inhouse_print_db_credentials(user_id=1)
    print(f"✅ Credentials retrieved:")
    print(f"   Server: {creds['server']}")
    print(f"   Database: {creds['database']}")
    print(f"   Driver: {creds['driver']}")
except Exception as e:
    print(f"❌ Credential retrieval failed: {e}")
    sys.exit(1)

# Test 3: Connect to database
print("\n[TEST 3] Connecting to database...")
try:
    db = InHousePrintDB(**creds)
    result = db.connect(**creds)
    
    if result['success']:
        print(f"✅ Database connection successful")
        print(f"   Message: {result['message']}")
    else:
        print(f"❌ Connection failed: {result['error']}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Connection error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Execute simple query
print("\n[TEST 4] Executing simple query...")
try:
    result = db.execute_query("SELECT TOP 5 * FROM Orders ORDER BY OrderDate DESC")
    
    if result['success']:
        print(f"✅ Query executed successfully")
        print(f"   Rows returned: {result['rows']}")
        print(f"   Columns: {', '.join(result['columns'])}")
        
        if result['rows'] > 0:
            print("\n   Sample data (first row):")
            first_row = result['data'][0]
            for key, value in list(first_row.items())[:5]:  # Show first 5 columns
                print(f"      {key}: {value}")
    else:
        print(f"❌ Query failed: {result['error']}")
except Exception as e:
    print(f"❌ Query execution error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Get business summary
print("\n[TEST 5] Getting business summary...")
try:
    result = db.get_business_summary()
    
    if result['success']:
        print(f"✅ Business summary retrieved:")
        metrics = result['metrics']
        print(f"   Total Orders: {metrics.get('total_orders', 0)}")
        print(f"   Active Orders: {metrics.get('active_orders', 0)}")
        print(f"   Total Clients: {metrics.get('total_clients', 0)}")
        print(f"   Recent Revenue: ${metrics.get('recent_revenue', 0):,.2f}")
    else:
        print(f"❌ Business summary failed: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"❌ Business summary error: {e}")

# Test 6: Query Library - Get available queries
print("\n[TEST 6] Testing Query Library...")
try:
    query_lib = InHousePrintQueryLibrary(**creds)
    result = query_lib.get_available_queries()
    
    if result['success']:
        print(f"✅ Query library initialized")
        print(f"   Available queries: {result['count']}")
        print(f"   Categories: {', '.join(result['categories'])}")
        
        print("\n   Query catalog:")
        for query in result['queries'][:3]:  # Show first 3 queries
            print(f"      - {query['name']} ({query['category']})")
            print(f"        {query['description']}")
    else:
        print(f"❌ Query library failed: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"❌ Query library error: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Execute pre-built query
print("\n[TEST 7] Executing pre-built query (recent_orders)...")
try:
    result = query_lib.execute_query('recent_orders', {'days': 7, 'limit': 5})
    
    if result['success']:
        print(f"✅ Pre-built query executed")
        print(f"   Query: {result['query_name']}")
        print(f"   Rows returned: {result['rows']}")
        print(f"   Parameters used: {result['parameters_used']}")
        
        if result['rows'] > 0:
            print("\n   Recent orders:")
            for order in result['data'][:3]:  # Show first 3
                print(f"      Order #{order.get('OrderID')}: {order.get('ClientName')} - ${order.get('TotalCost', 0):,.2f}")
    else:
        print(f"❌ Pre-built query failed: {result['error']}")
except Exception as e:
    print(f"❌ Pre-built query error: {e}")
    import traceback
    traceback.print_exc()

# Test 8: Check tool schemas
print("\n[TEST 8] Checking tool schemas...")
try:
    schemas_dir = Path(__file__).parent / 'tools' / 'schemas'
    inhouse_schemas = list(schemas_dir.glob('inhouse_*.json'))
    
    print(f"✅ Found {len(inhouse_schemas)} InHouse Print tool schemas:")
    for schema_file in inhouse_schemas:
        print(f"   - {schema_file.name}")
except Exception as e:
    print(f"❌ Schema check failed: {e}")

# Test 9: Tool Registry Integration
print("\n[TEST 9] Testing Tool Registry integration...")
try:
    from tools.registry import ToolRegistry
    
    registry = ToolRegistry()
    inhouse_tools = [name for name in registry.tools.keys() if name.startswith('inhouse_')]
    
    print(f"✅ Tool Registry loaded {len(registry.tools)} total tools")
    print(f"   InHouse Print tools registered: {len(inhouse_tools)}")
    
    if inhouse_tools:
        print(f"   InHouse tools:")
        for tool_name in inhouse_tools:
            print(f"      - {tool_name}")
    else:
        print("   ⚠️ No InHouse Print tools found in registry")
        print("   Tip: Ensure schemas are in tools/schemas/ directory")
except Exception as e:
    print(f"❌ Tool Registry test failed: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
print("\n[CLEANUP] Closing connections...")
try:
    db.close()
    query_lib.close()
    print("✅ Connections closed")
except Exception as e:
    print(f"⚠️ Cleanup warning: {e}")

print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("✅ Integration tests complete!")
print("\nNext steps:")
print("1. Start Flask server: cd AI_infrastructure; python flask_app.py")
print("2. Test via UI: http://localhost:5001")
print("3. Try asking: 'Show me recent orders from InHouse Print database'")
print("=" * 70)
