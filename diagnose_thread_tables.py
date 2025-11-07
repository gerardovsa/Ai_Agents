"""
Diagnose Thread Storage - What Are We Actually Using?

This script shows:
1. Which tables have data
2. Which user (printing@inhouseprint.com.au) is using
3. What needs to be cleaned up
"""

import sqlite3
from pathlib import Path
import json

db_path = Path(__file__).parent / 'data' / 'sessions.db'
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

print('='*80)
print('THREAD STORAGE DIAGNOSIS')
print('='*80)

# 1. Find the printing user
print('\n[1] FINDING USER: printing@inhouseprint.com.au')
print('-'*80)
cursor = conn.cursor()
cursor.execute("SELECT id, username, email FROM users")
users = cursor.fetchall()

print(f'\nAll users in database:')
for user in users:
    print(f'   ID: {user["id"]} | Username: {user["username"]} | Email: {user["email"]}')

cursor.execute("SELECT id, username, email FROM users WHERE email LIKE '%printing%' OR email LIKE '%inhouse%'")
printing_user = cursor.fetchone()

if printing_user:
    user_id = printing_user['id']
    print(f'\nFOUND printing user:')
    print(f'   ID: {user_id}')
    print(f'   Username: {printing_user["username"]}')
    print(f'   Email: {printing_user["email"]}')
else:
    print('\nWARNING: No printing@inhouseprint.com.au user found!')
    user_id = 1  # Fallback to user 1

# 2. Check THREADS table (CURRENT)
print(f'\n\n[2] THREADS TABLE (CURRENT SYSTEM)')
print('-'*80)
cursor.execute(f"SELECT COUNT(*) as count FROM threads WHERE user_id = ?", (user_id,))
thread_count = cursor.fetchone()['count']

print(f'Total threads for user {user_id}: {thread_count}')

if thread_count > 0:
    cursor.execute(f"""
        SELECT thread_slug, name, location, synergy_card_id, created_at 
        FROM threads 
        WHERE user_id = ?
        ORDER BY created_at DESC 
        LIMIT 10
    """, (user_id,))
    
    threads = cursor.fetchall()
    print(f'\nRecent threads (showing {len(threads)}):')
    for t in threads:
        loc = t['location'] or 'prime'
        synergy = f' -> Synergy: {t["synergy_card_id"]}' if t['synergy_card_id'] else ''
        print(f'   [{loc}] {t["name"][:50]}{synergy}')
        print(f'      ID: {t["thread_slug"][:30]}... | Created: {t["created_at"]}')

# 3. Check SAVED_THREADS table (LEGACY)
print(f'\n\n[3] SAVED_THREADS TABLE (LEGACY SYSTEM)')
print('-'*80)
cursor.execute(f"SELECT COUNT(*) as count FROM saved_threads WHERE user_id = ?", (user_id,))
saved_count = cursor.fetchone()['count']

print(f'Total saved_threads for user {user_id}: {saved_count}')

if saved_count > 0:
    cursor.execute(f"""
        SELECT thread_id, thread_name, location, agent_id, created_at 
        FROM saved_threads 
        WHERE user_id = ?
        ORDER BY created_at DESC 
        LIMIT 10
    """, (user_id,))
    
    saved = cursor.fetchall()
    print(f'\nLegacy threads (showing {len(saved)}):')
    for t in saved:
        loc = t['location'] or t['agent_id'] or 'unknown'
        print(f'   [{loc}] {t["thread_name"][:50]}')
        print(f'      ID: {t["thread_id"][:30]}... | Created: {t["created_at"]}')

# 4. Check SESSIONS table (DIFFERENT PURPOSE)
print(f'\n\n[4] SESSIONS TABLE (BROWSER SESSIONS - NOT THREADS)')
print('-'*80)
cursor.execute(f"SELECT COUNT(*) as count FROM sessions")
session_count = cursor.fetchone()['count']
print(f'Total browser sessions: {session_count}')
print('Note: This table is for browser session management, NOT thread storage')

# 5. Check MESSAGES table
print(f'\n\n[5] MESSAGES TABLE (MESSAGE STORAGE)')
print('-'*80)
cursor.execute(f"SELECT COUNT(*) as count FROM messages WHERE user_id = ?", (user_id,))
msg_count = cursor.fetchone()['count']
print(f'Total messages for user {user_id}: {msg_count}')

# Get message breakdown by thread
cursor.execute(f"""
    SELECT 
        m.thread_id,
        t.name as thread_name,
        COUNT(*) as msg_count
    FROM messages m
    LEFT JOIN threads t ON m.thread_id = t.id
    WHERE m.user_id = ?
    GROUP BY m.thread_id
    ORDER BY msg_count DESC
    LIMIT 5
""", (user_id,))

msg_breakdown = cursor.fetchall()
if msg_breakdown:
    print(f'\nMessage breakdown by thread (top 5):')
    for row in msg_breakdown:
        thread_name = row['thread_name'] or 'Unknown thread'
        print(f'   Thread {row["thread_id"]}: {row["msg_count"]} messages - "{thread_name[:40]}"')

# 6. Check thread assignments (in users.metadata)
print(f'\n\n[6] THREAD ASSIGNMENTS (users.metadata JSON)')
print('-'*80)
cursor.execute(f"SELECT metadata FROM users WHERE id = ?", (user_id,))
row = cursor.fetchone()

if row and row['metadata']:
    try:
        metadata = json.loads(row['metadata'])
        assignments = metadata.get('thread_assignments', {})
        
        print(f'Thread assignments: {len(assignments)}')
        if assignments:
            for loc, thread_id in assignments.items():
                print(f'   {loc}: {thread_id}')
        else:
            print('   (No thread assignments)')
    except json.JSONDecodeError:
        print('   ERROR: Invalid JSON in metadata')
else:
    print('   (No metadata found)')

# 7. RECOMMENDATION
print('\n\n' + '='*80)
print('WHAT ARE WE ACTUALLY USING?')
print('='*80)

print(f'\n✅ ACTIVE TABLES (Current System):')
print(f'   - threads table: {thread_count} threads')
print(f'   - messages table: {msg_count} messages')
print(f'   - users.metadata: Thread assignments (agent locations)')

print(f'\n⚠️  LEGACY TABLE (Old System):')
print(f'   - saved_threads table: {saved_count} threads (SHOULD BE DELETED)')

print(f'\n🔧 OTHER TABLES (Different Purpose):')
print(f'   - sessions table: Browser session management (NOT thread storage)')
print(f'   - api_sessions table: API session tracking')
print(f'   - workspaces table: Workspace management')

# 8. CLEANUP RECOMMENDATION
print('\n\n' + '='*80)
print('CLEANUP RECOMMENDATION')
print('='*80)

if saved_count > 0:
    print(f'\n❌ DELETE saved_threads table ({saved_count} legacy threads)')
    print(f'   Reason: Old system, replaced by threads table')
    print(f'   Action: Run cleanup script to delete this table')
else:
    print(f'\n✅ saved_threads table is already empty (good!)')

if thread_count == 0:
    print(f'\n⚠️  WARNING: No threads in threads table for user {user_id}!')
    print(f'   Possible reasons:')
    print(f'   1. User ID is wrong (check which user is logged in)')
    print(f'   2. Threads were never saved to database')
    print(f'   3. Database was cleared')
else:
    print(f'\n✅ threads table has {thread_count} threads (good!)')

print('\n' + '='*80)
print('NEXT STEPS')
print('='*80)

if saved_count > 0:
    print('\n1. DELETE saved_threads table:')
    print('   python cleanup_legacy_threads.py')

if thread_count == 0:
    print('\n2. CHECK which user is logged in:')
    print('   - Open browser DevTools (F12)')
    print('   - Check localStorage or cookies for user_id')
    print('   - Frontend may be using wrong user_id')

print('\n3. TEST thread loading:')
print('   curl "http://localhost:5001/api/threads/list?user_id=' + str(user_id) + '"')

conn.close()

print('\n' + '='*80)
print('DIAGNOSIS COMPLETE')
print('='*80)
