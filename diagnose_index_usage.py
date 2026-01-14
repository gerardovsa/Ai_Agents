#!/usr/bin/env python3
"""
Diagnose Index Usage - Check if migration 017 indexes are being used
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment
env_file = Path('.env')
load_dotenv(env_file)

db_url = os.getenv('SUPABASE_DB_URL_POOLER')
if not db_url:
    print('ERROR: No SUPABASE_DB_URL_POOLER found')
    sys.exit(1)

conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
cursor = conn.cursor()

print('=' * 80)
print('DIAGNOSTIC: Checking Index Usage for Migration 017')
print('=' * 80)

# Check if indexes exist
print('\n1. Verify indexes exist:')
cursor.execute("""
    SELECT schemaname, tablename, indexname, indexdef
    FROM pg_indexes
    WHERE schemaname = 'sessions'
    AND indexname IN ('idx_messages_thread_created', 'idx_threads_slug', 'idx_messages_created')
    ORDER BY tablename, indexname
""")
indexes = cursor.fetchall()

if indexes:
    for idx in indexes:
        print(f'   ✅ {idx["indexname"]}')
        print(f'      Table: {idx["tablename"]}')
        print(f'      Definition: {idx["indexdef"][:80]}...')
        print()
else:
    print('   ❌ NO INDEXES FOUND!')
    print('   Migration 017 may not have been applied to production!')

# Check table statistics
print('2. Table statistics (for query planner):')
cursor.execute("""
    SELECT 
        schemaname,
        relname as tablename,
        n_live_tup as row_count,
        n_dead_tup as dead_rows,
        last_analyze,
        last_autoanalyze
    FROM pg_stat_user_tables
    WHERE schemaname = 'sessions'
    AND relname IN ('messages', 'threads')
    ORDER BY relname
""")
stats = cursor.fetchall()

for stat in stats:
    print(f'   Table: {stat["tablename"]}')
    print(f'      Rows: {stat["row_count"]:,}')
    print(f'      Last analyzed: {stat["last_analyze"] or "Never"}')
    print()

# Check index usage statistics
print('3. Index usage statistics:')
cursor.execute("""
    SELECT 
        schemaname,
        relname as tablename,
        indexrelname as indexname,
        idx_scan as scans,
        idx_tup_read as tuples_read,
        idx_tup_fetch as tuples_fetched
    FROM pg_stat_user_indexes
    WHERE schemaname = 'sessions'
    AND indexrelname IN ('idx_messages_thread_created', 'idx_threads_slug', 'idx_messages_created')
    ORDER BY relname, indexrelname
""")
usage = cursor.fetchall()

if usage:
    for idx in usage:
        scans = idx["scans"] or 0
        status = "✅ USED" if scans > 0 else "❌ NOT USED"
        print(f'   {status} {idx["indexname"]}')
        print(f'      Scans: {scans:,}')
        print(f'      Tuples read: {idx["tuples_read"] or 0:,}')
        print()
else:
    print('   ⚠️  No usage statistics available')

# Check query execution plan
print('4. Query execution plan (EXPLAIN ANALYZE):')
print('   Testing actual slow query from logs...')
print()

try:
    cursor.execute("""
        EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
        SELECT 
            m.id, m.role, m.content, m.tool_calls, 
            m.tokens_used, m.created_at, m.metadata
        FROM sessions.messages m
        JOIN sessions.threads t ON m.thread_id = t.id
        WHERE t.thread_slug = '1767546560644'
        ORDER BY m.created_at ASC
    """)
    plan = cursor.fetchall()
    
    for row in plan:
        line = row["QUERY PLAN"]
        # Highlight important parts
        if 'Seq Scan' in line:
            print(f'   ❌ {line}')
        elif 'Index Scan' in line or 'Index Only Scan' in line:
            print(f'   ✅ {line}')
        else:
            print(f'      {line}')
            
except Exception as e:
    print(f'   ERROR: {e}')

print()
print('=' * 80)
print('DIAGNOSIS COMPLETE')
print('=' * 80)
print()

# Recommendations
print('RECOMMENDATIONS:')
print()

if not indexes:
    print('❌ CRITICAL: Indexes not found!')
    print('   ACTION: Re-run migration 017 on production database')
    print()
elif usage and all(idx["scans"] == 0 for idx in usage):
    print('⚠️  WARNING: Indexes exist but are not being used!')
    print('   POSSIBLE CAUSES:')
    print('   1. Query planner statistics are stale → Run ANALYZE')
    print('   2. Queries are using different columns → Check WHERE clause')
    print('   3. Tables are too small for indexes to be beneficial')
    print()
else:
    print('✅ Indexes are being used by query planner')
    print('   If queries are still slow, consider:')
    print('   1. Increasing connection pool size (maxconn)')
    print('   2. Adding query result caching')
    print('   3. Optimizing large JSON content retrieval')
    print()

cursor.close()
conn.close()
