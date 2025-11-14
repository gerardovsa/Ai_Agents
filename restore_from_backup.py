"""
Restore Data from Corrupted Database Backup
Attempts to extract as much data as possible from the backup
"""

import sqlite3
import os
from datetime import datetime

# Find the most recent backup
BACKUP_DIR = 'data'
backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith('sessions_corrupt_')]
if not backups:
    print('[ERROR] No backup files found')
    exit(1)

latest_backup = max(backups, key=lambda x: os.path.getctime(os.path.join(BACKUP_DIR, x)))
BACKUP_PATH = os.path.join(BACKUP_DIR, latest_backup)
NEW_DB_PATH = 'data/sessions.db'

print('=' * 60)
print('DATABASE RECOVERY UTILITY')
print('=' * 60)
print(f'[INFO] Using backup: {BACKUP_PATH}')
print(f'[INFO] Target database: {NEW_DB_PATH}')
print()

def extract_data():
    """Try to extract data from corrupted backup"""
    try:
        # Open backup in recovery mode
        backup_conn = sqlite3.connect(f'file:{BACKUP_PATH}?mode=ro', uri=True)
        
        # Get current database
        new_conn = sqlite3.connect(NEW_DB_PATH)
        new_cursor = new_conn.cursor()
        
        recovered = {
            'threads': 0,
            'messages': 0,
            'assignments': 0,
            'errors': []
        }
        
        # Try to recover threads
        print('[STEP 1] Recovering threads...')
        try:
            backup_cursor = backup_conn.cursor()
            backup_cursor.execute('SELECT * FROM threads')
            threads = backup_cursor.fetchall()
            
            # Get column names
            columns = [desc[0] for desc in backup_cursor.description]
            
            for thread in threads:
                try:
                    # Build INSERT statement
                    placeholders = ','.join(['?' for _ in columns])
                    cols = ','.join(columns)
                    new_cursor.execute(f'INSERT OR IGNORE INTO threads ({cols}) VALUES ({placeholders})', thread)
                    recovered['threads'] += 1
                except Exception as e:
                    recovered['errors'].append(f'Thread error: {str(e)[:50]}')
            
            print(f'[OK] Recovered {recovered["threads"]} threads')
        except Exception as e:
            print(f'[ERROR] Failed to recover threads: {e}')
            recovered['errors'].append(f'Threads table: {str(e)[:50]}')
        
        # Try to recover messages
        print('[STEP 2] Recovering messages...')
        try:
            backup_cursor.execute('SELECT * FROM messages')
            messages = backup_cursor.fetchall()
            columns = [desc[0] for desc in backup_cursor.description]
            
            for msg in messages:
                try:
                    placeholders = ','.join(['?' for _ in columns])
                    cols = ','.join(columns)
                    new_cursor.execute(f'INSERT OR IGNORE INTO messages ({cols}) VALUES ({placeholders})', msg)
                    recovered['messages'] += 1
                except Exception as e:
                    recovered['errors'].append(f'Message error: {str(e)[:50]}')
            
            print(f'[OK] Recovered {recovered["messages"]} messages')
        except Exception as e:
            print(f'[ERROR] Failed to recover messages: {e}')
            recovered['errors'].append(f'Messages table: {str(e)[:50]}')
        
        # Try to recover thread assignments (if table exists)
        print('[STEP 3] Recovering thread assignments (if present)...')
        try:
            # Check whether the assignments table exists in the backup
            backup_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thread_assignments'")
            if not backup_cursor.fetchone():
                print('[SKIP] thread_assignments table not present in backup - skipping assignments recovery')
            else:
                backup_cursor.execute('SELECT * FROM thread_assignments')
                assignments = backup_cursor.fetchall()
                columns = [desc[0] for desc in backup_cursor.description]

                for assign in assignments:
                    try:
                        placeholders = ','.join(['?' for _ in columns])
                        cols = ','.join(columns)
                        # Only attempt insert if destination table exists
                        try:
                            new_cursor.execute(f'INSERT OR IGNORE INTO thread_assignments ({cols}) VALUES ({placeholders})', assign)
                            recovered['assignments'] += 1
                        except sqlite3.OperationalError:
                            # Target DB doesn't have thread_assignments table - skip
                            recovered['errors'].append('Target DB missing thread_assignments table; skipped inserting assignments')
                            break
                    except Exception as e:
                        recovered['errors'].append(f'Assignment error: {str(e)[:50]}')

                print(f'[OK] Recovered {recovered["assignments"]} assignments')
        except Exception as e:
            print(f'[ERROR] Failed to recover assignments: {e}')
            recovered['errors'].append(f'Assignments table: {str(e)[:50]}')
        
        new_conn.commit()
        backup_conn.close()
        new_conn.close()
        
        return recovered
        
    except Exception as e:
        print(f'[ERROR] Recovery failed: {e}')
        return None

# Run recovery
print('[START] Beginning recovery process...')
print()

result = extract_data()

print()
print('=' * 60)
print('RECOVERY SUMMARY')
print('=' * 60)

if result:
    print(f'[OK] Threads recovered: {result["threads"]}')
    print(f'[OK] Messages recovered: {result["messages"]}')
    print(f'[OK] Assignments recovered: {result["assignments"]}')
    
    if result['errors']:
        print(f'\n[WARN] Errors encountered: {len(result["errors"])}')
        print('[INFO] Some data may be incomplete or corrupted')
        
        # Show first 5 errors
        for i, error in enumerate(result['errors'][:5]):
            print(f'  {i+1}. {error}')
        
        if len(result['errors']) > 5:
            print(f'  ... and {len(result["errors"]) - 5} more errors')
    
    total_recovered = result['threads'] + result['messages'] + result['assignments']
    if total_recovered > 0:
        print(f'\n[SUCCESS] Recovered {total_recovered} total records')
        print('[INFO] You can now restart Flask: BISTART')
    else:
        print('\n[WARN] No data could be recovered')
        print('[INFO] Database was likely too corrupted')
else:
    print('[FAILED] Recovery could not complete')
    print('[INFO] Backup file may be completely unreadable')
