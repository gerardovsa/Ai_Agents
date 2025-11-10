"""
Fix Corrupted Sessions Database
Repairs or rebuilds the sessions.db database when it becomes corrupted
"""

import sqlite3
import os
import shutil
from datetime import datetime

# Database paths
DB_PATH = 'data/sessions.db'
BACKUP_PATH = f'data/sessions_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
TEMP_PATH = 'data/sessions_temp.db'

def backup_database():
    """Create backup of corrupted database"""
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f'✅ Backup created: {BACKUP_PATH}')
        return True
    return False

def check_database_integrity():
    """Check if database is corrupted"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('PRAGMA integrity_check')
        result = cursor.fetchone()
        conn.close()
        
        if result[0] == 'ok':
            print('✅ Database integrity check: OK')
            return True
        else:
            print(f'❌ Database integrity check failed: {result[0]}')
            return False
    except sqlite3.DatabaseError as e:
        print(f'❌ Database error: {e}')
        return False

def dump_and_restore():
    """Dump database to SQL and restore to new file"""
    print('\n🔧 Attempting to dump and restore database...')
    
    try:
        # Connect to corrupted database
        old_conn = sqlite3.connect(DB_PATH)
        
        # Create new database
        new_conn = sqlite3.connect(TEMP_PATH)
        
        # Dump schema and data
        for line in old_conn.iterdump():
            try:
                new_conn.execute(line)
            except sqlite3.Error as e:
                print(f'⚠️  Skipped line due to error: {e}')
        
        new_conn.commit()
        old_conn.close()
        new_conn.close()
        
        # Replace old database with new one
        os.replace(TEMP_PATH, DB_PATH)
        print('✅ Database successfully rebuilt')
        return True
        
    except Exception as e:
        print(f'❌ Failed to dump and restore: {e}')
        return False

def rebuild_from_scratch():
    """Rebuild database with fresh schema"""
    print('\n🔧 Rebuilding database from scratch...')
    
    try:
        # Remove corrupted database
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        
        # Create new database with schema
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Threads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_slug TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                title TEXT DEFAULT 'Untitled Thread',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                archived INTEGER DEFAULT 0,
                tags TEXT DEFAULT '[]',
                synergy_card_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_time REAL,
                FOREIGN KEY (thread_id) REFERENCES threads (id) ON DELETE CASCADE
            )
        ''')
        
        # Thread assignments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS thread_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                thread_slug TEXT NOT NULL,
                location TEXT NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, thread_slug),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Users table (if doesn't exist)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print('✅ Database rebuilt successfully')
        print('⚠️  Note: All previous threads and messages have been lost')
        return True
        
    except Exception as e:
        print(f'❌ Failed to rebuild database: {e}')
        return False

def main():
    print('=' * 60)
    print('DATABASE CORRUPTION FIX UTILITY')
    print('=' * 60)
    
    if not os.path.exists(DB_PATH):
        print(f'❌ Database not found: {DB_PATH}')
        return
    
    # Step 1: Backup
    print('\n[STEP 1] Creating backup...')
    backup_database()
    
    # Step 2: Check integrity
    print('\n[STEP 2] Checking database integrity...')
    if check_database_integrity():
        print('✅ Database is healthy. No repair needed.')
        return
    
    # Step 3: Try dump and restore
    print('\n[STEP 3] Attempting repair...')
    if dump_and_restore():
        if check_database_integrity():
            print('\n✅ SUCCESS! Database repaired and verified.')
            return
    
    # Step 4: Rebuild from scratch
    print('\n[STEP 4] Repair failed. Rebuilding from scratch...')
    choice = input('⚠️  This will DELETE all data. Continue? (yes/no): ')
    
    if choice.lower() == 'yes':
        if rebuild_from_scratch():
            print('\n✅ SUCCESS! Database rebuilt.')
            print(f'📁 Backup of old data saved at: {BACKUP_PATH}')
        else:
            print('\n❌ FAILED! Manual intervention required.')
    else:
        print('\n❌ Operation cancelled.')

if __name__ == '__main__':
    main()
