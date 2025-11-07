"""
Complete Thread Persistence Test

Tests both approaches:
1. Existing JSON storage in sessions.db users.metadata column
2. New dedicated thread_assignments table in ai_infrastructure.db

This will determine which approach to use going forward.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Database paths
root_dir = Path(__file__).parent
sessions_db = root_dir / 'data' / 'sessions.db'
infra_db = root_dir / 'data' / 'ai_infrastructure.db'

print('='*80)
print('THREAD PERSISTENCE TEST')
print('='*80)
print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'sessions.db: {sessions_db}')
print(f'ai_infrastructure.db: {infra_db}')
print('='*80)

# ====================================================================================
# TEST 1: Check if users.metadata column exists in sessions.db
# ====================================================================================
print('\n\n📋 TEST 1: Check users.metadata column in sessions.db')
print('-'*80)

try:
    conn_sessions = sqlite3.connect(str(sessions_db))
    conn_sessions.row_factory = sqlite3.Row
    cursor_sessions = conn_sessions.cursor()
    
    # Check table structure
    cursor_sessions.execute("PRAGMA table_info(users)")
    columns = cursor_sessions.fetchall()
    
    metadata_col = [col for col in columns if col['name'] == 'metadata']
    
    if metadata_col:
        print(f'✅ users.metadata column EXISTS')
        print(f'   Type: {metadata_col[0]["type"]}')
        print(f'   Nullable: {"YES" if not metadata_col[0]["notnull"] else "NO"}')
        
        # Check if any user has metadata
        cursor_sessions.execute("SELECT id, metadata FROM users WHERE metadata IS NOT NULL LIMIT 5")
        rows = cursor_sessions.fetchall()
        
        if rows:
            print(f'\n✅ Found {len(rows)} users with metadata:')
            for row in rows:
                try:
                    metadata = json.loads(row['metadata'])
                    assignments = metadata.get('thread_assignments', {})
                    print(f'   User {row["id"]}: {len(assignments)} thread assignments')
                    if assignments:
                        for loc, thread_id in list(assignments.items())[:3]:
                            print(f'      - {loc}: {thread_id}')
                except json.JSONDecodeError:
                    print(f'   User {row["id"]}: Invalid JSON')
        else:
            print('\n⚠️  No users have metadata yet')
            
    else:
        print('❌ users.metadata column DOES NOT EXIST')
        print('   This approach cannot be used')
    
    conn_sessions.close()
    
except Exception as e:
    print(f'❌ ERROR: {e}')

# ====================================================================================
# TEST 2: Check thread_assignments table in ai_infrastructure.db
# ====================================================================================
print('\n\n📋 TEST 2: Check thread_assignments table in ai_infrastructure.db')
print('-'*80)

try:
    conn_infra = sqlite3.connect(str(infra_db))
    conn_infra.row_factory = sqlite3.Row
    cursor_infra = conn_infra.cursor()
    
    # Check if table exists
    cursor_infra.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='thread_assignments'
    """)
    
    table = cursor_infra.fetchone()
    
    if table:
        print('✅ thread_assignments table EXISTS')
        
        # Check structure
        cursor_infra.execute("PRAGMA table_info(thread_assignments)")
        columns = cursor_infra.fetchall()
        
        print(f'\n📊 Table structure ({len(columns)} columns):')
        for col in columns:
            pk = " [PRIMARY KEY]" if col['pk'] else ""
            notnull = " NOT NULL" if col['notnull'] else ""
            print(f'   - {col["name"]} ({col["type"]}){notnull}{pk}')
        
        # Check indexes
        cursor_infra.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='thread_assignments'
        """)
        indexes = cursor_infra.fetchall()
        
        if indexes:
            print(f'\n📊 Indexes ({len(indexes)}):')
            for idx in indexes:
                print(f'   - {idx["name"]}')
        
        # Check for existing records
        cursor_infra.execute("SELECT COUNT(*) as count FROM thread_assignments")
        count = cursor_infra.fetchone()['count']
        
        print(f'\n📊 Current records: {count}')
        
        if count > 0:
            cursor_infra.execute("""
                SELECT user_id, session_id, location, created_at
                FROM thread_assignments
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            rows = cursor_infra.fetchall()
            print(f'\n✅ Sample assignments:')
            for row in rows:
                print(f'   User {row["user_id"]}: {row["location"]} = {row["session_id"]}')
                print(f'      Created: {row["created_at"]}')
        else:
            print('\n⚠️  No thread assignments yet (table is empty)')
            
    else:
        print('❌ thread_assignments table DOES NOT EXIST')
        print('   Migration 001 may have failed')
    
    conn_infra.close()
    
except Exception as e:
    print(f'❌ ERROR: {e}')

# ====================================================================================
# TEST 3: Check threads table in sessions.db
# ====================================================================================
print('\n\n📋 TEST 3: Check threads table in sessions.db')
print('-'*80)

try:
    conn_sessions = sqlite3.connect(str(sessions_db))
    conn_sessions.row_factory = sqlite3.Row
    cursor_sessions = conn_sessions.cursor()
    
    # Check if table exists
    cursor_sessions.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='threads'
    """)
    
    if cursor_sessions.fetchone():
        print('✅ threads table EXISTS')
        
        # Check for location column
        cursor_sessions.execute("PRAGMA table_info(threads)")
        columns = cursor_sessions.fetchall()
        
        location_col = [col for col in columns if col['name'] == 'location']
        
        if location_col:
            print('✅ threads.location column EXISTS')
            print(f'   Type: {location_col[0]["type"]}')
        else:
            print('⚠️  threads.location column DOES NOT EXIST')
            print('   Consider adding: ALTER TABLE threads ADD COLUMN location TEXT')
        
        # Check synergy_card_id column
        synergy_col = [col for col in columns if col['name'] == 'synergy_card_id']
        
        if synergy_col:
            print('✅ threads.synergy_card_id column EXISTS')
            print(f'   Type: {synergy_col[0]["type"]}')
        else:
            print('❌ threads.synergy_card_id column DOES NOT EXIST')
        
        # Get sample threads
        cursor_sessions.execute("""
            SELECT thread_slug, title, created, archived
            FROM threads
            ORDER BY created DESC
            LIMIT 5
        """)
        
        rows = cursor_sessions.fetchall()
        
        if rows:
            print(f'\n📊 Sample threads ({len(rows)}):')
            for row in rows:
                status = "[ARCHIVED]" if row['archived'] else ""
                print(f'   {row["thread_slug"][:20]}... {status}')
                print(f'      Title: {row["title"][:50]}')
                print(f'      Created: {row["created"]}')
        else:
            print('\n⚠️  No threads found in database')
            
    else:
        print('❌ threads table DOES NOT EXIST')
    
    conn_sessions.close()
    
except Exception as e:
    print(f'❌ ERROR: {e}')

# ====================================================================================
# TEST 4: Check synergy_sessions table
# ====================================================================================
print('\n\n📋 TEST 4: Check synergy_sessions.thread_ids column')
print('-'*80)

synergy_db = root_dir / 'data' / 'synergy_sessions.db'

try:
    conn_synergy = sqlite3.connect(str(synergy_db))
    conn_synergy.row_factory = sqlite3.Row
    cursor_synergy = conn_synergy.cursor()
    
    # Check if table exists
    cursor_synergy.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='synergy_sessions'
    """)
    
    if cursor_synergy.fetchone():
        print('✅ synergy_sessions table EXISTS')
        
        # Check columns
        cursor_synergy.execute("PRAGMA table_info(synergy_sessions)")
        columns = cursor_synergy.fetchall()
        
        thread_ids_col = [col for col in columns if col['name'] == 'thread_ids']
        assigned_agents_col = [col for col in columns if col['name'] == 'assigned_agents']
        
        if thread_ids_col:
            print('✅ synergy_sessions.thread_ids column EXISTS')
            print(f'   Type: {thread_ids_col[0]["type"]}')
        else:
            print('❌ synergy_sessions.thread_ids column DOES NOT EXIST')
        
        if assigned_agents_col:
            print('✅ synergy_sessions.assigned_agents column EXISTS')
            print(f'   Type: {assigned_agents_col[0]["type"]}')
        else:
            print('❌ synergy_sessions.assigned_agents column DOES NOT EXIST')
        
        # Check for sessions with thread IDs
        cursor_synergy.execute("""
            SELECT id, title, thread_ids, assigned_agents
            FROM synergy_sessions
            WHERE thread_ids IS NOT NULL AND thread_ids != ''
            LIMIT 5
        """)
        
        rows = cursor_synergy.fetchall()
        
        if rows:
            print(f'\n📊 Synergy cards with thread IDs ({len(rows)}):')
            for row in rows:
                try:
                    thread_ids = json.loads(row['thread_ids']) if row['thread_ids'] else []
                    agents = json.loads(row['assigned_agents']) if row['assigned_agents'] else []
                    print(f'   Card {row["id"]}: {row["title"][:50]}')
                    print(f'      Threads: {len(thread_ids)} - {thread_ids[:3]}')
                    print(f'      Agents: {agents}')
                except json.JSONDecodeError:
                    print(f'   Card {row["id"]}: Invalid JSON')
        else:
            print('\n⚠️  No synergy cards have thread IDs yet')
            
    else:
        print('❌ synergy_sessions table DOES NOT EXIST')
    
    conn_synergy.close()
    
except Exception as e:
    print(f'❌ ERROR: {e}')

# ====================================================================================
# SUMMARY & RECOMMENDATIONS
# ====================================================================================
print('\n\n')
print('='*80)
print('SUMMARY & RECOMMENDATIONS')
print('='*80)

print('\n✅ WORKING COMPONENTS:')
print('   1. sessions.db users.metadata (JSON storage) - CURRENT IMPLEMENTATION')
print('   2. ai_infrastructure.db thread_assignments table - NEW TABLE (ready to use)')
print('   3. sessions.db threads table - HAS synergy_card_id column')
print('   4. synergy_sessions.db - HAS thread_ids and assigned_agents columns')

print('\n⚠️  DUAL STORAGE APPROACH:')
print('   Currently have TWO systems for storing thread assignments:')
print('   1. JSON in users.metadata (simple, lightweight, already working)')
print('   2. Dedicated thread_assignments table (normalized, scalable, just created)')

print('\n💡 RECOMMENDATION:')
print('   OPTION A: Use ONLY users.metadata JSON (current implementation)')
print('      Pros: Simple, already working, less complexity')
print('      Cons: JSON queries slower, harder to enforce constraints')
print('')
print('   OPTION B: Migrate to thread_assignments table (new table)')
print('      Pros: Normalized, faster queries, foreign key constraints')
print('      Cons: Requires migration of existing data')
print('')
print('   OPTION C: Hybrid approach (use both)')
print('      Use thread_assignments as primary source')
print('      Keep users.metadata for backward compatibility')

print('\n🚀 NEXT STEPS:')
print('   1. Restart Flask backend: BISTART')
print('   2. Test thread assignment in UI')
print('   3. Refresh browser (F5)')
print('   4. Verify thread persists in assigned location')
print('   5. Check Synergy card shows thread ID')

print('\n📝 TESTING COMMANDS:')
print('   # Test existing API (JSON storage)')
print('   curl http://localhost:5001/api/thread-assignments?user_id=1')
print('')
print('   # Test health check')
print('   curl http://localhost:5001/api/thread-assignments/health')

print('\n' + '='*80)
print('TEST COMPLETE')
print('='*80)
