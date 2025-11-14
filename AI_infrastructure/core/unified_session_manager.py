"""
Unified Session Manager
Single source of truth for ALL session data across all AI UIs

Replaces:
- agent_states = {}
- agent_sessions = {}  
- active_sessions = {}
- agent_execution_locks = {}

Features:
- SQLite persistence (sessions.db)
- In-memory cache for active sessions
- SSE queue management per session
- Thread-safe execution locks
- Automatic cleanup of inactive sessions
"""

import sqlite3
import threading
from queue import Queue
from datetime import datetime
from typing import Dict, Optional, List, Any
import uuid
import json
import os

# Setup logging
from utils.logger_config import setup_logger, log_db
logger = setup_logger('core.unified_session_manager')


class UnifiedSessionManager:
    """
    Single source of truth for ALL session data
    
    Architecture:
    - SQLite: Long-term persistence (survives server restarts)
    - In-memory: Fast access for active sessions
    - Queues: SSE event streaming per session
    - Locks: Prevent concurrent AI requests per session
    """
    
    def __init__(self, db_path: str = None):
        # Use centralized data folder
        if db_path is None:
            from pathlib import Path
            root_dir = Path(__file__).parent.parent.parent  # AI_agents root
            db_path = str(root_dir / 'data' / 'sessions.db')
        
        self.db_path = db_path
        self.lock = threading.Lock()  # Manager-level lock
        
        # In-memory cache (same pattern as automated_extraction_system.py)
        self.sessions: Dict[str, Dict] = {}      # {session_id: session_data}
        self.queues: Dict[str, Queue] = {}        # {session_id: Queue()}
        self.locks: Dict[str, threading.Lock] = {}  # {session_id: Lock()}
        
        # DO NOT create directory - data folder must already exist
        # Centralized database location: AI_agents/data/
        
        # Initialize database (tables only)
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database with sessions table"""
        import time
        
        # Retry logic to handle WAL race condition with multiple Gunicorn workers
        max_retries = 5
        for attempt in range(max_retries):
            try:
                conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
                
                # Enable WAL mode for better concurrency (multiple readers, one writer)
                # Skip WAL mode on Render - ephemeral filesystem doesn't support it
                is_render = os.getenv('RENDER') == 'true' or 'onrender.com' in os.getenv('RENDER_EXTERNAL_URL', '')
                
                if not is_render:
                    try:
                        conn.execute("PRAGMA journal_mode=WAL")
                        print("✓ [DB] WAL mode enabled (local/persistent filesystem)")
                    except sqlite3.OperationalError as e:
                        print(f"⚠ [DB] WAL mode failed (expected on ephemeral FS): {e}")
                        conn.execute("PRAGMA journal_mode=DELETE")  # Fallback to DELETE mode
                else:
                    print("✓ [DB] Using DELETE journal mode (Render ephemeral filesystem)")
                    conn.execute("PRAGMA journal_mode=DELETE")
                
                # Optimize for performance
                conn.execute("PRAGMA synchronous=NORMAL")  # Faster than FULL, still safe
                conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
                conn.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables
                
                # If we got here, initialization succeeded
                break
                
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    # Another worker is initializing - wait and retry
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    # Either not a lock error, or we've exhausted retries
                    raise
        
        # Create tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                ui_context TEXT NOT NULL,
                agent_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                conversation TEXT,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        log_db(logger, "Database initialized with WAL mode (improved concurrency)")
    
    def create_session(self, ui_context: str, agent_id: Optional[str] = None, session_id: Optional[str] = None, source: str = 'ui') -> str:
        """
        Create new session
        
        Args:
            ui_context: 'stock_chat' | 'data_agent_chat' | 'single_viewer' | 'triple_agent' | 'business_ai_platform'
            agent_id: Optional agent ID (for triple_agent: '1', '2', '3')
            session_id: Optional custom session ID (if not provided, UUID generated)
            source: 'ui' (web interface) or 'cli' (CHAT command) - cli sessions are NOT saved to DB
        
        Returns:
            session_id: UUID string or custom session ID
        """
        with self.lock:
            #  Use provided session_id or generate new UUID
            if not session_id:
                session_id = str(uuid.uuid4())
            
            session_data = {
                'session_id': session_id,
                'ui_context': ui_context,
                'agent_id': agent_id,
                'conversation': [],
                'metadata': {'source': source},  #  Track source
                'created_at': datetime.now().isoformat(),
                'last_active': datetime.now().isoformat()
            }
            
            # Store in cache
            self.sessions[session_id] = session_data
            
            #  ONLY store in DB if NOT from CLI
            if source != 'cli':
                # Use connection timeout for stability
                with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                    conn.execute("""
                        INSERT INTO sessions (session_id, ui_context, agent_id, conversation, metadata)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        session_id,
                        ui_context,
                        agent_id,
                        json.dumps([]),
                        json.dumps({'source': source})
                    ))
                    conn.commit()
                print(f"[SessionManager] Created session: {session_id} (ui_context={ui_context}, agent_id={agent_id}, source={source})")
            else:
                print(f"[SessionManager] Created CLI session (in-memory only): {session_id}")
            
            return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session data (from cache or DB)
        
        Returns:
            session_data: Dict with session info, or None if not found
        """
        with self.lock:
            # Check cache first (fast path)
            if session_id in self.sessions:
                self._update_last_active(session_id)
                return self.sessions[session_id]
            
            # Load from DB (slow path - session not active)
            with sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False) as conn:
                cursor = conn.execute("""
                    SELECT session_id, ui_context, agent_id, conversation, metadata, created_at, last_active
                    FROM sessions
                    WHERE session_id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                if row:
                    session_data = {
                        'session_id': row[0],
                        'ui_context': row[1],
                        'agent_id': row[2],
                        'conversation': json.loads(row[3]),
                        'metadata': json.loads(row[4]),
                        'created_at': row[5],
                        'last_active': row[6]
                    }
                    
                    # Cache it for future access
                    self.sessions[session_id] = session_data
                    self._update_last_active(session_id)
                    
                    print(f"[SessionManager] Loaded session from DB: {session_id}")
                    return session_data
                
                print(f"[SessionManager] Session not found: {session_id}")
                return None
    
    def update_conversation(self, session_id: str, conversation: List[Dict]):
        """
        Update conversation history
        
        Args:
            session_id: Session ID
            conversation: List of message dicts (role, content)
        """
        with self.lock:
            # Update cache
            if session_id in self.sessions:
                self.sessions[session_id]['conversation'] = conversation
                self.sessions[session_id]['last_active'] = datetime.now().isoformat()
                
                #  ONLY update DB if NOT from CLI
                source = self.sessions[session_id].get('metadata', {}).get('source', 'ui')
                if source == 'cli':
                    print(f"[SessionManager] Skipping DB save for CLI session: {session_id}")
                    return
            
            # Update DB (only for UI sessions)
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                conn.execute("""
                    UPDATE sessions
                    SET conversation = ?, last_active = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                """, (json.dumps(conversation), session_id))
                conn.commit()
    
    def update_metadata(self, session_id: str, metadata: Dict):
        """
        Update session metadata
        
        Args:
            session_id: Session ID
            metadata: Metadata dict
        """
        with self.lock:
            # Update cache
            if session_id in self.sessions:
                self.sessions[session_id]['metadata'] = metadata
                self.sessions[session_id]['last_active'] = datetime.now().isoformat()
            
            # Update DB
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                conn.execute("""
                    UPDATE sessions
                    SET metadata = ?, last_active = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                """, (json.dumps(metadata), session_id))
                conn.commit()
    
    def get_queue(self, session_id: str) -> Queue:
        """
        Get SSE queue for session
        Creates new queue if doesn't exist
        
        Returns:
            Queue: Thread-safe queue for SSE events
        """
        with self.lock:
            if session_id not in self.queues:
                self.queues[session_id] = Queue()
                print(f"[SessionManager] Created SSE queue for session: {session_id}")
            return self.queues[session_id]
    
    def get_lock(self, session_id: str) -> threading.Lock:
        """
        Get execution lock for session
        Prevents concurrent AI requests for same session
        
        Returns:
            Lock: Thread-safe lock
        """
        with self.lock:
            if session_id not in self.locks:
                self.locks[session_id] = threading.Lock()
                print(f"[SessionManager] Created execution lock for session: {session_id}")
            return self.locks[session_id]
    
    def cleanup_inactive_sessions(self, max_age_hours: int = 24):
        """
        Remove inactive sessions from cache (NOT from DB)
        
        Args:
            max_age_hours: Sessions inactive longer than this are removed from cache
        """
        with self.lock:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                # Get inactive session IDs
                cursor = conn.execute("""
                    SELECT session_id
                    FROM sessions
                    WHERE last_active < datetime('now', '-' || ? || ' hours')
                """, (max_age_hours,))
                
                inactive_ids = [row[0] for row in cursor.fetchall()]
                
                # Remove from cache only (keep in DB for history)
                removed_count = 0
                for session_id in inactive_ids:
                    if session_id in self.sessions:
                        self.sessions.pop(session_id, None)
                        removed_count += 1
                    self.queues.pop(session_id, None)
                    self.locks.pop(session_id, None)
                
                if removed_count > 0:
                    print(f"[SessionManager] Cleaned up {removed_count} inactive sessions from cache")
    
    def delete_session(self, session_id: str):
        """
        Permanently delete session from cache AND database
        
        Args:
            session_id: Session ID to delete
        """
        with self.lock:
            # Remove from cache
            self.sessions.pop(session_id, None)
            self.queues.pop(session_id, None)
            self.locks.pop(session_id, None)
            
            # Remove from DB
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                conn.commit()
            
            print(f"[SessionManager] Deleted session: {session_id}")
    
    def list_active_sessions(self) -> List[Dict]:
        """
        Get list of all active sessions (in cache)
        
        Returns:
            List of session dicts
        """
        with self.lock:
            return list(self.sessions.values())
    
    def get_session_count(self) -> Dict[str, int]:
        """
        Get session counts
        
        Returns:
            Dict with counts: {'active': int, 'total_db': int}
        """
        with self.lock:
            active_count = len(self.sessions)
            
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM sessions")
                total_count = cursor.fetchone()[0]
            
            return {
                'active': active_count,
                'total_db': total_count
            }
    
    def _update_last_active(self, session_id: str):
        """Update last active timestamp (internal helper)"""
        with sqlite3.connect(self.db_path, timeout=30.0) as conn:
            conn.execute("""
                UPDATE sessions
                SET last_active = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (session_id,))
            conn.commit()


# Global singleton instance
session_manager = UnifiedSessionManager()
