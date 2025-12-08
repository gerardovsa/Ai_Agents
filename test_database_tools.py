"""
Test Supabase and Fred Query Tools
"""

import sys
sys.path.insert(0, '.')

from tools.implementations.supabase_query import supabase_execute_query, supabase_search_database
from tools.implementations.fred_query import fred_execute_query, fred_search_database

print("="*70)
print("  TESTING SUPABASE POSTGRESQL TOOLS")
print("="*70)

# Test 1: Simple SELECT
print("\n[Test 1] Simple SELECT query")
result = supabase_execute_query(
    'ai_infrastructure',
    'SELECT id, username, email FROM users LIMIT 3'
)
print(f"✅ SUCCESS" if result.get('success') else f"❌ FAILED: {result.get('error')}")
print(f"Rows returned: {result.get('row_count')}")
if result.get('rows'):
    print(f"Sample: {result['rows'][0]}")

# Test 2: Parameterized query with ILIKE
print("\n[Test 2] Parameterized query with ILIKE (case-insensitive)")
result = supabase_execute_query(
    'ai_infrastructure',
    'SELECT id, username, email FROM users WHERE email ILIKE %s LIMIT 5',
    ['%@ai-platform.local']
)
print(f"✅ SUCCESS" if result.get('success') else f"❌ FAILED: {result.get('error')}")
print(f"Rows returned: {result.get('row_count')}")

# Test 3: Test LIMIT syntax (PostgreSQL)
print("\n[Test 3] LIMIT syntax (PostgreSQL style)")
result = supabase_execute_query(
    'ai_infrastructure',
    'SELECT COUNT(*) as total_users FROM users'
)
print(f"✅ SUCCESS" if result.get('success') else f"❌ FAILED: {result.get('error')}")
if result.get('rows'):
    print(f"Total users in database: {result['rows'][0]}")

# Test 4: Test invalid schema
print("\n[Test 4] Invalid schema (error handling)")
result = supabase_execute_query(
    'invalid_schema',
    'SELECT * FROM users'
)
print(f"✅ ERROR HANDLED" if not result.get('success') else "❌ Should have failed")
print(f"Error: {result.get('error')}")

# Test 5: Read-only enforcement
print("\n[Test 5] Read-only enforcement (UPDATE blocked)")
result = supabase_execute_query(
    'ai_infrastructure',
    'UPDATE users SET role = %s WHERE id = %s',
    ['admin', 999],
    read_only=True
)
print(f"✅ BLOCKED" if not result.get('success') else "❌ Should have been blocked")
print(f"Error: {result.get('error')}")

# Test 6: Search database
print("\n[Test 6] Search database (find user by email)")
result = supabase_search_database(
    search_text='user_1@ai-platform.local'
)
print(f"✅ SUCCESS" if result.get('success') else f"❌ FAILED: {result.get('error')}")
print(f"Total matches: {result.get('total_matches')}")
print(f"Tables searched: {result.get('searched_tables')}")

# Test 7: JOIN query (threads + messages)
print("\n[Test 7] JOIN query (threads + messages)")
result = supabase_execute_query(
    'sessions',
    '''
        SELECT 
            t.thread_slug, t.name, t.created_at,
            COUNT(m.id) as message_count
        FROM threads t
        LEFT JOIN messages m ON t.id = m.thread_id
        GROUP BY t.thread_slug, t.name, t.created_at
        ORDER BY t.created_at DESC
        LIMIT 5
    '''
)
print(f"✅ SUCCESS" if result.get('success') else f"❌ FAILED: {result.get('error')}")
print(f"Rows returned: {result.get('row_count')}")

print("\n" + "="*70)
print("  TESTING FRED SQL SERVER TOOLS")
print("="*70)

# Test 8: Fred simple SELECT with TOP
print("\n[Test 8] Fred SELECT with TOP (SQL Server syntax)")
result = fred_execute_query(
    query='SELECT TOP 5 OrderID, ClientName, OrderDate FROM Orders ORDER BY OrderDate DESC'
)
print(f"✅ SUCCESS" if result.get('success') else f"❌ FAILED: {result.get('error')}")
print(f"Rows returned: {result.get('row_count')}")
if result.get('rows'):
    print(f"Sample order: {result['rows'][0]}")

# Test 9: Fred parameterized query with LIKE
print("\n[Test 9] Fred parameterized LIKE search (SQL Server)")
result = fred_execute_query(
    query='SELECT TOP 10 OrderID, ClientName FROM Orders WHERE ClientName LIKE ? ORDER BY OrderDate DESC',
    params=['%King%']
)
print(f"✅ SUCCESS" if result.get('success') else f"❌ FAILED: {result.get('error')}")
print(f"Rows returned: {result.get('row_count')}")

# Test 10: Fred JOIN query
print("\n[Test 10] Fred JOIN query (Orders + JobTickets)")
result = fred_execute_query(
    query='''
        SELECT TOP 5
            o.OrderID, o.ClientName,
            jt.TicketID, jt.ShortJobDesc, jt.Cost
        FROM Orders o
        INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
        ORDER BY o.OrderDate DESC
    '''
)
print(f"✅ SUCCESS" if result.get('success') else f"❌ FAILED: {result.get('error')}")
print(f"Rows returned: {result.get('row_count')}")

# Test 11: Fred search database
print("\n[Test 11] Fred search database")
result = fred_search_database(
    search_text='Printing'
)
print(f"✅ SUCCESS" if result.get('success') else f"❌ FAILED: {result.get('error')}")
print(f"Total matches: {result.get('total_matches')}")
print(f"Tables searched: {result.get('searched_tables')}")

# Test 12: Fred read-only enforcement
print("\n[Test 12] Fred read-only enforcement")
result = fred_execute_query(
    query='UPDATE Orders SET Urgent = 1 WHERE OrderID = 12345',
    read_only=True
)
print(f"✅ BLOCKED" if not result.get('success') else "❌ Should have been blocked")
print(f"Error: {result.get('error')}")

# Test 13: Fred invalid column (common mistake)
print("\n[Test 13] Fred invalid column 'Status' (should fail with helpful hint)")
result = fred_execute_query(
    query='SELECT OrderID, Status FROM Orders'
)
print(f"✅ ERROR WITH HINT" if not result.get('success') else "❌ Should have failed")
print(f"Error: {result.get('error')}")
print(f"Hint: {result.get('hint')}")

print("\n" + "="*70)
print("  TEST SUMMARY")
print("="*70)
print("\nAll tests completed! Check results above.")
