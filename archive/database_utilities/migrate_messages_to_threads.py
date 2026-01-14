"""
MIGRATION SCRIPT: Link Messages to Threads
===========================================
from shared.database_utils import convert_sql_placeholders

Purpose: Link existing messages to their corresponding threads
- Updates messages.thread_id to reference threads.id
- Handles multiple matching strategies
- Preserves all existing data
- Creates backup before migration

Author: AI Agent
Date: November 8, 2025
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

def backup_database():
    """Create backup before migration"""
    db_path = Path('data/sessions.db')
    backup_path = Path(f'data/sessions_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    
    print(f"📦 Creating backup: {backup_path}")
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup created successfully")
    return backup_path

def analyze_data(conn):
    """Analyze current state before migration"""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("CURRENT STATE ANALYSIS")
    print("="*60)
    
    # Threads without messages
    sql, params = convert_sql_placeholders('''
        SELECT COUNT(*) FROM threads t
        LEFT JOIN messages m ON t.id = m.thread_id
        WHERE m.id IS NULL AND t.user_id = 14
    ''')
    empty_threads = cursor.fetchone()[0]
    print(f"📭 Threads without messages: {empty_threads}")
    
    # Messages without thread_id
    cursor.execute('SELECT COUNT(*) FROM messages WHERE thread_id IS NULL')
    orphan_messages = cursor.fetchone()[0]
    print(f"🔗 Messages without thread_id: {orphan_messages}")
    
    # Total messages
    cursor.execute('SELECT COUNT(*) FROM messages')
    total_messages = cursor.fetchone()[0]
    print(f"💬 Total messages: {total_messages}")
    
    # Unique session_ids
    cursor.execute('SELECT COUNT(DISTINCT session_id) FROM messages WHERE session_id IS NOT NULL')
    unique_sessions = cursor.fetchone()[0]
    print(f"🎯 Unique session_ids: {unique_sessions}")
    
    return {
        'empty_threads': empty_threads,
        'orphan_messages': orphan_messages,
        'total_messages': total_messages,
        'unique_sessions': unique_sessions
    }

def migrate_messages(conn):
    """Main migration logic"""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("MIGRATION PROCESS")
    print("="*60)
    
    # Strategy 1: Exact match (thread_slug = session_id)
    print("\n🔍 Strategy 1: Exact match (thread_slug = session_id)")
    cursor.execute('''
        UPDATE messages
        SET thread_id = (
            SELECT t.id 
            FROM threads t 
            WHERE t.thread_slug = messages.session_id
        )
        WHERE session_id IN (
            SELECT thread_slug FROM threads
        )
        AND thread_id IS NULL
    ''')
    exact_matches = cursor.rowcount
    print(f"✅ Linked {exact_matches} messages via exact match")
    
    # Strategy 2: Timestamp-based matching (extract timestamp from session_id)
    print("\n🔍 Strategy 2: Timestamp-based matching")
    cursor.execute('''
        SELECT id, thread_slug, created_at, name
        FROM threads
        WHERE user_id = 14
        ORDER BY created_at DESC
    ''')
    threads = cursor.fetchall()
    
    timestamp_matches = 0
    for thread_id, thread_slug, created_at, name in threads:
        # Extract timestamp from thread_slug (if numeric)
        if thread_slug.isdigit():
            timestamp_ms = int(thread_slug)
            # Find messages within ±5 minutes of thread creation
            # First find matching message IDs
            cursor.execute('''
                SELECT id FROM messages
                WHERE thread_id IS NULL
                AND session_id LIKE 'session_%'
                AND abs(
                    strftime('%s', created_at) - ?
                ) < 300
                LIMIT 50
            ''', (timestamp_ms // 1000,))

    cursor.execute(sql, params)
            msg_ids = [row[0] for row in cursor.fetchall()]
            
            if msg_ids:
                # Update those messages
                placeholders = ','.join('?' * len(msg_ids))
                cursor.execute(f'''
                    UPDATE messages
                    SET thread_id = ?
                    WHERE id IN ({placeholders})
                ''', [thread_id] + msg_ids)
                matched = cursor.rowcount
                if matched > 0:
                    timestamp_matches += matched
                    print(f"  ✓ Thread '{name}' ({thread_slug}): {matched} messages")
    
    print(f"✅ Linked {timestamp_matches} messages via timestamp matching")
    
    # Strategy 3: User ID + recent messages for new threads
    print("\n🔍 Strategy 3: Recent messages for new threads")
    sql, params = convert_sql_placeholders('''
        SELECT id, thread_slug, created_at, name, user_id
        FROM threads
        WHERE user_id = 14
        AND NOT EXISTS (
            SELECT 1 FROM messages WHERE messages.thread_id = threads.id
        )
        ORDER BY created_at DESC
        LIMIT 5
    ''')
    recent_empty_threads = cursor.fetchall()
    
    recent_matches = 0
    for thread_id, thread_slug, created_at, name, user_id in recent_empty_threads:
        # Get thread creation timestamp
        if thread_slug.isdigit():
            thread_ts = int(thread_slug)
            # Find orphan messages from same user around same time
            cursor.execute('''
                SELECT id, session_id, created_at
                FROM messages
                WHERE thread_id IS NULL
                AND user_id = ?
                AND abs(
                    strftime('%s', created_at) - ?
                ) < 600
                ORDER BY created_at ASC
                LIMIT 10
            ''', (user_id, thread_ts // 1000))

    cursor.execute(sql, params)
            
            orphan_msgs = cursor.fetchall()
            if orphan_msgs:
                msg_ids = [m[0] for m in orphan_msgs]
                cursor.execute(f'''
                    UPDATE messages
                    SET thread_id = ?
                    WHERE id IN ({','.join('?' * len(msg_ids))})
                ''', [thread_id] + msg_ids)
                matched = cursor.rowcount
                recent_matches += matched
                print(f"  ✓ Thread '{name}': {matched} recent messages")
    
    print(f"✅ Linked {recent_matches} messages to recent threads")
    
    conn.commit()
    
    return {
        'exact_matches': exact_matches,
        'timestamp_matches': timestamp_matches,
        'recent_matches': recent_matches,
        'total_linked': exact_matches + timestamp_matches + recent_matches
    }

def verify_migration(conn):
    """Verify migration results"""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("MIGRATION RESULTS")
    print("="*60)
    
    # Threads with messages now
    cursor.execute('''
        SELECT t.thread_slug, t.name, COUNT(m.id) as msg_count
        FROM threads t
        LEFT JOIN messages m ON t.id = m.thread_id
        WHERE t.user_id = 14
        GROUP BY t.id, t.thread_slug, t.name
        HAVING msg_count > 0
        ORDER BY t.created_at DESC
    ''')
    
    threads_with_messages = cursor.fetchall()
    print(f"\n✅ Threads with messages: {len(threads_with_messages)}")
    for slug, name, count in threads_with_messages[:10]:
        print(f"  • {name} ({slug}): {count} messages")
    
    # Remaining orphan messages
    cursor.execute('SELECT COUNT(*) FROM messages WHERE thread_id IS NULL')
    remaining_orphans = cursor.fetchone()[0]
    print(f"\n⚠️  Remaining orphan messages: {remaining_orphans}")
    
    # Sample orphan session_ids
    if remaining_orphans > 0:
        cursor.execute('''
            SELECT DISTINCT session_id, COUNT(*) as count
            FROM messages
            WHERE thread_id IS NULL AND session_id IS NOT NULL
            GROUP BY session_id
            ORDER BY count DESC
            LIMIT 5
        ''')
        print("\n  Top orphan session_ids:")
        for session_id, count in cursor.fetchall():
            print(f"    - {session_id}: {count} messages")
    
    return {
        'threads_with_messages': len(threads_with_messages),
        'remaining_orphans': remaining_orphans
    }

def create_indexes(conn):
    """Create indexes for better query performance"""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("CREATING INDEXES")
    print("="*60)
    
    indexes = [
        ('idx_messages_thread_id', 'CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id)'),
        ('idx_messages_session_id', 'CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id)'),
        ('idx_messages_user_id', 'CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id)'),
        ('idx_messages_created_at', 'CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at)'),
        ('idx_threads_user_id', 'CREATE INDEX IF NOT EXISTS idx_threads_user_id ON threads(user_id)'),
        ('idx_threads_slug', 'CREATE INDEX IF NOT EXISTS idx_threads_slug ON threads(thread_slug)'),
    ]
    
    for idx_name, sql in indexes:
        try:
            cursor.execute(sql)
            print(f"✅ Created index: {idx_name}")
        except sqlite3.Error as e:
            print(f"⚠️  Index {idx_name} already exists or error: {e}")
    
    conn.commit()

def main():
    """Main migration execution"""
    print("="*60)
    print("MESSAGE TO THREAD MIGRATION TOOL")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Backup first
    backup_path = backup_database()
    
    # Connect to database
    conn = sqlite3.connect('data/sessions.db')
    
    try:
        # Analyze current state
        before_state = analyze_data(conn)
        
        # Run migration
        migration_results = migrate_messages(conn)
        
        # Verify results
        after_state = verify_migration(conn)
        
        # Create indexes
        create_indexes(conn)
        
        # Summary
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print(f"✅ Exact matches: {migration_results['exact_matches']}")
        print(f"✅ Timestamp matches: {migration_results['timestamp_matches']}")
        print(f"✅ Recent matches: {migration_results['recent_matches']}")
        print(f"✅ Total linked: {migration_results['total_linked']}")
        print(f"\n📊 Before: {before_state['empty_threads']} empty threads")
        print(f"📊 After: {before_state['empty_threads'] - after_state['threads_with_messages']} empty threads")
        print(f"\n📦 Backup saved: {backup_path}")
        print(f"✅ Migration completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ ERROR during migration: {e}")
        print(f"💾 Database backup available at: {backup_path}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    main()
