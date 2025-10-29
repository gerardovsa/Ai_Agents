"""
Session Database Manager
========================

SQLite database for storing complete conversation sessions with:
- Full message history with timestamps
- Activity logs (timestamped events)
- Active vs archived documents
- Session metadata
- Fast queries, no API limits

This is the MAIN database. Google Tasks are just for Kanban visualization.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import contextmanager


class SessionDatabase:
    """
    Manages SQLite database for session storage
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default: data/sessions.db in project root
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / 'data'
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / 'sessions.db')
        
        self.db_path = db_path
        self._init_database()
        print(f"📁 Session database: {db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT,
                    status TEXT DEFAULT 'active',
                    project_name TEXT,
                    kanban_column TEXT DEFAULT 'in_progress',
                    priority TEXT DEFAULT 'medium',
                    created_at TEXT NOT NULL,
                    last_active TEXT NOT NULL,
                    tags TEXT,
                    google_task_id TEXT,
                    google_event_id TEXT,
                    due_date TEXT,
                    last_synced_at TEXT,
                    
                    INDEX idx_user_status (user_id, status),
                    INDEX idx_project (project_name),
                    INDEX idx_kanban (kanban_column),
                    INDEX idx_google_task (google_task_id),
                    INDEX idx_google_event (google_event_id)
                )
            """)
            
            # Messages table (conversation history)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tools_used TEXT,
                    timestamp TEXT NOT NULL,
                    
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                        ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_time 
                ON messages(session_id, timestamp)
            """)
            
            # Activity log (timestamped events)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    metadata TEXT,
                    timestamp TEXT NOT NULL,
                    
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                        ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_activity_time 
                ON activity_log(session_id, timestamp)
            """)
            
            # Documents (active and archived)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    doc_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    archived_at TEXT,
                    
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                        ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_doc_status 
                ON documents(session_id, status)
            """)
            
            # Next steps / action items
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS next_steps (
                    step_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    description TEXT NOT NULL,
                    completed BOOLEAN DEFAULT 0,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                        ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            print("✅ Database schema initialized")
    
    def create_session(self, session_id: str, user_id: str, title: str,
                      project_name: str = None, tags: List[str] = None) -> None:
        """Create new session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            tags_json = json.dumps(tags) if tags else None
            
            cursor.execute("""
                INSERT INTO sessions (
                    session_id, user_id, title, project_name, 
                    tags, created_at, last_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, user_id, title, project_name, tags_json, now, now))
            
            # Log creation
            self._log_activity(
                cursor, session_id, 'session_created',
                f'Session "{title}" created'
            )
            
            conn.commit()
            print(f"✅ Session saved to database: {session_id}")
    
    def add_message(self, session_id: str, role: str, content: str,
                   tools_used: List[str] = None) -> int:
        """Add message to session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            tools_json = json.dumps(tools_used) if tools_used else None
            
            cursor.execute("""
                INSERT INTO messages (
                    session_id, role, content, tools_used, timestamp
                ) VALUES (?, ?, ?, ?, ?)
            """, (session_id, role, content, tools_json, now))
            
            message_id = cursor.lastrowid
            
            # Update last_active
            cursor.execute("""
                UPDATE sessions SET last_active = ? WHERE session_id = ?
            """, (now, session_id))
            
            # Log activity
            self._log_activity(
                cursor, session_id, 'message_added',
                f'{role.title()} message added'
            )
            
            conn.commit()
            return message_id
    
    def add_document(self, session_id: str, doc_type: str, title: str,
                    url: str = None) -> int:
        """Add document to session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO documents (
                    session_id, doc_type, title, url, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (session_id, doc_type, title, url, now))
            
            doc_id = cursor.lastrowid
            
            # Log activity
            self._log_activity(
                cursor, session_id, 'document_created',
                f'{doc_type.title()} created: {title}',
                {'url': url}
            )
            
            conn.commit()
            return doc_id
    
    def archive_document(self, doc_id: int) -> None:
        """Archive a document"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute("""
                UPDATE documents 
                SET status = 'archived', archived_at = ?
                WHERE doc_id = ?
            """, (now, doc_id))
            
            # Get session_id for logging
            cursor.execute("SELECT session_id, title FROM documents WHERE doc_id = ?", (doc_id,))
            row = cursor.fetchone()
            
            if row:
                self._log_activity(
                    cursor, row['session_id'], 'document_archived',
                    f'Document archived: {row["title"]}'
                )
            
            conn.commit()
    
    def add_next_step(self, session_id: str, description: str) -> int:
        """Add next step to session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO next_steps (session_id, description, created_at)
                VALUES (?, ?, ?)
            """, (session_id, description, now))
            
            step_id = cursor.lastrowid
            
            self._log_activity(
                cursor, session_id, 'next_step_added',
                f'Next step: {description}'
            )
            
            conn.commit()
            return step_id
    
    def complete_next_step(self, step_id: int) -> None:
        """Mark next step as completed"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute("""
                UPDATE next_steps 
                SET completed = 1, completed_at = ?
                WHERE step_id = ?
            """, (now, step_id))
            
            # Get session_id for logging
            cursor.execute("SELECT session_id, description FROM next_steps WHERE step_id = ?", (step_id,))
            row = cursor.fetchone()
            
            if row:
                self._log_activity(
                    cursor, row['session_id'], 'next_step_completed',
                    f'Completed: {row["description"]}'
                )
            
            conn.commit()
    
    def _log_activity(self, cursor, session_id: str, event_type: str,
                     description: str, metadata: Dict = None) -> None:
        """Internal: Log activity"""
        now = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO activity_log (
                session_id, event_type, description, metadata, timestamp
            ) VALUES (?, ?, ?, ?, ?)
        """, (session_id, event_type, description, metadata_json, now))
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session with all related data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get session
            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            session_row = cursor.fetchone()
            
            if not session_row:
                return None
            
            session = dict(session_row)
            session['tags'] = json.loads(session['tags']) if session['tags'] else []
            
            # Get messages
            cursor.execute("""
                SELECT * FROM messages 
                WHERE session_id = ? 
                ORDER BY timestamp ASC
            """, (session_id,))
            session['messages'] = [dict(row) for row in cursor.fetchall()]
            
            # Get activity log
            cursor.execute("""
                SELECT * FROM activity_log 
                WHERE session_id = ? 
                ORDER BY timestamp DESC
                LIMIT 50
            """, (session_id,))
            session['activity_log'] = [dict(row) for row in cursor.fetchall()]
            
            # Get active documents
            cursor.execute("""
                SELECT * FROM documents 
                WHERE session_id = ? AND status = 'active'
                ORDER BY created_at DESC
            """, (session_id,))
            session['active_documents'] = [dict(row) for row in cursor.fetchall()]
            
            # Get archived documents
            cursor.execute("""
                SELECT * FROM documents 
                WHERE session_id = ? AND status = 'archived'
                ORDER BY archived_at DESC
            """, (session_id,))
            session['archived_documents'] = [dict(row) for row in cursor.fetchall()]
            
            # Get next steps
            cursor.execute("""
                SELECT * FROM next_steps 
                WHERE session_id = ? AND completed = 0
                ORDER BY created_at ASC
            """, (session_id,))
            session['next_steps'] = [dict(row) for row in cursor.fetchall()]
            
            return session
    
    def get_user_sessions(self, user_id: str, status: str = None,
                         kanban_column: str = None) -> List[Dict]:
        """Get user's sessions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM sessions WHERE user_id = ?"
            params = [user_id]
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if kanban_column:
                query += " AND kanban_column = ?"
                params.append(kanban_column)
            
            query += " ORDER BY last_active DESC"
            
            cursor.execute(query, params)
            sessions = [dict(row) for row in cursor.fetchall()]
            
            # Parse tags
            for session in sessions:
                session['tags'] = json.loads(session['tags']) if session['tags'] else []
            
            return sessions
    
    def update_session_column(self, session_id: str, column: str) -> None:
        """Move session to different Kanban column"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE sessions 
                SET kanban_column = ?,
                    status = CASE WHEN ? = 'done' THEN 'completed' ELSE status END
                WHERE session_id = ?
            """, (column, column, session_id))
            
            self._log_activity(
                cursor, session_id, 'kanban_moved',
                f'Moved to {column} column'
            )
            
            conn.commit()
    
    def link_google_task(self, session_id: str, task_id: str) -> None:
        """Link Google Task to session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE sessions 
                SET google_task_id = ?
                WHERE session_id = ?
            """, (task_id, session_id))
            
            self._log_activity(
                cursor, session_id, 'task_linked',
                f'Linked to Google Task: {task_id}'
            )
            
            conn.commit()
    
    def get_session_summary(self, session_id: str) -> Dict:
        """Get lightweight summary for Google Task card"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get basic info
            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            session = dict(cursor.fetchone())
            
            # Get message count
            cursor.execute("SELECT COUNT(*) as count FROM messages WHERE session_id = ?", (session_id,))
            session['message_count'] = cursor.fetchone()['count']
            
            # Get pending next steps count
            cursor.execute("SELECT COUNT(*) as count FROM next_steps WHERE session_id = ? AND completed = 0", (session_id,))
            session['pending_steps'] = cursor.fetchone()['count']
            
            # Get active docs count
            cursor.execute("SELECT COUNT(*) as count FROM documents WHERE session_id = ? AND status = 'active'", (session_id,))
            session['active_docs'] = cursor.fetchone()['count']
            
            # Get latest activity (last 3)
            cursor.execute("""
                SELECT event_type, description, timestamp 
                FROM activity_log 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 3
            """, (session_id,))
            session['recent_activity'] = [dict(row) for row in cursor.fetchall()]
            
            return session


# Singleton instance
_db_instance = None

def get_session_db() -> SessionDatabase:
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = SessionDatabase()
    return _db_instance
