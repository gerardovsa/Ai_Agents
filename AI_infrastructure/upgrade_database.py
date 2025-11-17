"""
Database Schema Upgrade Script
Enhances the sessions.db structure to support comprehensive thread/message management
Based on AnythingLLM message management patterns
"""

import sqlite3
import json
from datetime import datetime
import os
from pathlib import Path

# CORRECT: Use data/sessions.db (not AI_infrastructure/data/sessions.db)
root_dir = Path(__file__).parent.parent
DB_PATH = str(root_dir / 'data' / 'sessions.db')

def upgrade_database():
    """Upgrade database schema to support enhanced thread/message management"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔧 Starting database upgrade...")
    print(f"📂 Database: {DB_PATH}")
    
    # ========== CREATE WORKSPACES TABLE ==========
    print("\n📦 Creating workspaces table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workspaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,  -- JSON: {default_llm, temperature, etc}
            UNIQUE(slug)
        )
    ''')
    
    # ========== CREATE THREADS TABLE ==========
    print("🧵 Creating threads table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_slug TEXT UNIQUE NOT NULL,
            workspace_id INTEGER,
            user_id INTEGER,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,  -- JSON: {tags, pinned, etc}
            FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    # ========== CREATE MESSAGES TABLE (Enhanced) ==========
    print("💬 Creating messages table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id INTEGER NOT NULL,
            thread_id INTEGER,
            session_id TEXT,  -- Links to sessions.session_id
            role TEXT NOT NULL,  -- 'user', 'assistant', 'system'
            content TEXT NOT NULL,  -- The actual message text
            prompt TEXT,  -- Original user prompt (for assistant responses)
            response_data TEXT,  -- JSON: full response with metadata
            user_id INTEGER,
            api_session_id TEXT,  -- For API-based sessions
            include BOOLEAN DEFAULT 1,  -- Include in LLM context (1=yes, 0=no/hidden)
            feedback_score INTEGER,  -- 1=thumbs up, 0=thumbs down, NULL=no rating
            tool_calls TEXT,  -- JSON: [{tool_name, args, result}]
            tokens_used INTEGER,  -- Token count for this message
            response_time_ms INTEGER,  -- Response latency in milliseconds
            embedding_vector TEXT,  -- JSON: vector embedding (optional)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,  -- JSON: {edited, source, etc}
            FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
            FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    # ========== CREATE USERS TABLE ==========
    print("👤 Creating users table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            role TEXT DEFAULT 'user',  -- 'admin', 'user', 'readonly'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT  -- JSON: {preferences, settings}
        )
    ''')
    
    # ========== CREATE API_SESSIONS TABLE ==========
    print("🔑 Creating api_sessions table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_session_id TEXT UNIQUE NOT NULL,
            workspace_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,  -- JSON: {ip_address, user_agent, etc}
            FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
        )
    ''')
    
    # ========== CREATE INDEXES FOR PERFORMANCE ==========
    print("⚡ Creating indexes...")
    
    indexes = [
        ('idx_messages_workspace', 'messages', 'workspace_id'),
        ('idx_messages_thread', 'messages', 'thread_id'),
        ('idx_messages_session', 'messages', 'session_id'),
        ('idx_messages_role', 'messages', 'role'),
        ('idx_messages_include', 'messages', 'include'),
        ('idx_messages_created', 'messages', 'created_at'),
        ('idx_threads_workspace', 'threads', 'workspace_id'),
        ('idx_threads_slug', 'threads', 'thread_slug'),
        ('idx_sessions_session_id', 'sessions', 'session_id'),
    ]
    
    for index_name, table_name, column_name in indexes:
        try:
            cursor.execute(f'''
                CREATE INDEX IF NOT EXISTS {index_name}
                ON {table_name}({column_name})
            ''')
            print(f"   Index {index_name} created")
        except Exception as e:
            print(f"  ⚠️  Index {index_name} already exists or error: {e}")
    
    # ========== MIGRATE EXISTING DATA ==========
    print("\n📊 Migrating existing sessions data...")
    
    # Check if default workspace exists
    cursor.execute("SELECT id FROM workspaces WHERE slug = 'default'")
    workspace = cursor.fetchone()
    
    if not workspace:
        print("  Creating default workspace...")
        cursor.execute('''
            INSERT INTO workspaces (slug, name, description)
            VALUES ('default', 'Default Workspace', 'Automatically created workspace for existing sessions')
        ''')
        workspace_id = cursor.lastrowid
        print(f"   Default workspace created (ID: {workspace_id})")
    else:
        workspace_id = workspace[0]
        print(f"   Using existing default workspace (ID: {workspace_id})")
    
    # Migrate existing sessions to messages
    cursor.execute("SELECT session_id, conversation, created_at FROM sessions WHERE conversation IS NOT NULL")
    sessions_to_migrate = cursor.fetchall()
    
    migrated_count = 0
    for session_id, conversation_json, created_at in sessions_to_migrate:
        try:
            if conversation_json:
                conversation = json.loads(conversation_json)
                if isinstance(conversation, list):
                    for msg in conversation:
                        if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                            # Convert content to string if it's a list or other type
                            content = msg['content']
                            if isinstance(content, (list, dict)):
                                content = json.dumps(content)
                            elif not isinstance(content, str):
                                content = str(content)
                            
                            cursor.execute('''
                                INSERT OR IGNORE INTO messages 
                                (workspace_id, session_id, role, content, created_at)
                                VALUES (%s, %s, %s, %s, %s)
                            ''', (workspace_id, session_id, msg['role'], content, created_at))
                            migrated_count += 1
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"  ⚠️  Could not migrate session {session_id}: {e}")
    
    print(f"   Migrated {migrated_count} messages from {len(sessions_to_migrate)} sessions")
    
    # ========== CREATE VIEWS FOR EASY QUERYING ==========
    print("\n👁️  Creating views...")
    
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS v_messages_with_context AS
        SELECT 
            m.id,
            m.role,
            m.content,
            m.include,
            m.feedback_score,
            m.created_at,
            t.name as thread_name,
            t.thread_slug,
            w.name as workspace_name,
            w.slug as workspace_slug,
            u.username,
            m.tokens_used,
            m.response_time_ms
        FROM messages m
        LEFT JOIN threads t ON m.thread_id = t.id
        LEFT JOIN workspaces w ON m.workspace_id = w.id
        LEFT JOIN users u ON m.user_id = u.id
        ORDER BY m.created_at DESC
    ''')
    print("   View v_messages_with_context created")
    
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS v_thread_summary AS
        SELECT 
            t.id,
            t.thread_slug,
            t.name,
            t.created_at,
            t.updated_at,
            w.name as workspace_name,
            COUNT(m.id) as message_count,
            SUM(CASE WHEN m.include = 1 THEN 1 ELSE 0 END) as active_messages,
            SUM(m.tokens_used) as total_tokens,
            MAX(m.created_at) as last_message_at
        FROM threads t
        LEFT JOIN workspaces w ON t.workspace_id = w.id
        LEFT JOIN messages m ON t.id = m.thread_id
        GROUP BY t.id, t.thread_slug, t.name, t.created_at, t.updated_at, w.name
        ORDER BY t.updated_at DESC
    ''')
    print("   View v_thread_summary created")
    
    conn.commit()
    conn.close()
    
    print("\n Database upgrade complete!")
    print("\n📊 New Structure:")
    print("  - workspaces: Organize threads into workspaces")
    print("  - threads: Conversation threads with metadata")
    print("  - messages: Individual messages with full tracking")
    print("  - users: User management")
    print("  - api_sessions: API session tracking")
    print("\n🎯 Key Features:")
    print("  - Message include/exclude (hide from LLM context)")
    print("  - Feedback scoring (thumbs up/down)")
    print("  - Tool call tracking")
    print("  - Token usage tracking")
    print("  - Response time metrics")
    print("  - Full migration from old sessions")

def verify_upgrade():
    """Verify the upgrade was successful"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n🔍 Verifying upgrade...")
    
    tables = ['workspaces', 'threads', 'messages', 'users', 'api_sessions']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   {table}: {count} rows")
    
    conn.close()

if __name__ == '__main__':
    try:
        # Backup database first
        import shutil
        backup_path = DB_PATH.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        shutil.copy2(DB_PATH, backup_path)
        print(f"💾 Database backed up to: {backup_path}")
        
        upgrade_database()
        verify_upgrade()
        
        print("\n✨ All done! Your database is now ready for enhanced thread management.")
        
    except Exception as e:
        print(f"\n Upgrade failed: {e}")
        import traceback
        traceback.print_exc()
