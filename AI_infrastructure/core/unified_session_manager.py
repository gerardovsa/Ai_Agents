"""
Unified Session Manager
Single source of truth for ALL session data across all AI UIs

FILE: AI_infrastructure/core/unified_session_manager.py
PURPOSE: Centralized session management with PostgreSQL persistence

Replaces:
- agent_states = {}
- agent_sessions = {}  
- active_sessions = {}
- agent_execution_locks = {}

Features:
- PostgreSQL persistence (Supabase sessions schema)
- In-memory cache for active sessions
- SSE queue management per session
- Thread-safe execution locks
- Automatic cleanup of inactive sessions
"""

import threading
from queue import Queue
from datetime import datetime
from typing import Dict, Optional, List, Any
import uuid
import json
import os
from AI_infrastructure.shared.database_utils import get_database_connection

# Setup logging
from AI_infrastructure.utils.logger_config import setup_logger, log_db
logger = setup_logger('core.unified_session_manager')


class UnifiedSessionManager:
    """
    Single source of truth for ALL session data
    
    Architecture:
    - PostgreSQL (Supabase): Long-term persistence (survives server restarts)
    - In-memory: Fast access for active sessions
    - Queues: SSE event streaming per session
    - Locks: Prevent concurrent AI requests per session
    """
    
    def __init__(self, db_path: str = None):
        # Use centralized data folder
        if db_path is None:
            from AI_infrastructure.utils.db_path_helper import get_sessions_db_path
            db_path = get_sessions_db_path()
        
        self.db_path = db_path
        self.lock = threading.Lock()  # Manager-level lock
        
        # In-memory cache (same pattern as automated_extraction_system.py)
        self.sessions: Dict[str, Dict] = {}      # {session_id: session_data}
        self.queues: Dict[str, Queue] = {}        # {session_id: Queue()}
        self.locks: Dict[str, threading.Lock] = {}  # {session_id: Lock()}
        
        # ENHANCEMENT 1 & 4: Lazy initialization + graceful degradation (Dec 5, 2025)
        self._db_initialized = False
        self._db_available = False
        self._db_error = None
        self._init_attempts = 0
        
        # Ensure data directory exists (CRITICAL for first-time setup)
        from pathlib import Path
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        print("[SessionManager] ✅ Initialized with LAZY loading (DB will connect on first use)")
    
    def _ensure_db_initialized(self):
        """Lazy initialization - connect on first use, not at import time"""
        if self._db_initialized:
            return
        
        with self.lock:
            if self._db_initialized:
                return
            
            try:
                self._init_db()
                self._db_initialized = True
                self._db_available = True
                print("[SessionManager] ✅ Database initialized successfully")
            except Exception as e:
                self._db_initialized = True  # Mark as attempted
                self._db_available = False
                self._db_error = str(e)
                self._init_attempts += 1
                print(f"[SessionManager] ⚠️  Database unavailable (attempt {self._init_attempts}): {e}")
                print(f"[SessionManager] 🔄 Running in MEMORY-ONLY mode (sessions won't persist across restarts)")
    
    def _init_db(self):
        """Initialize PostgreSQL database with sessions table"""
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # PostgreSQL (Supabase) - connection pool already configured
        print("[OK] [DB] Using PostgreSQL (Supabase) - sessions schema")
        
        # Create tables - PostgreSQL syntax
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions.sessions (
                session_id TEXT PRIMARY KEY,
                ui_context TEXT NOT NULL,
                agent_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                conversation TEXT,
                metadata TEXT
            )
        """)
        cursor.close()
        conn.commit()
        conn.close()
        
        log_db(logger, "Database initialized - PostgreSQL sessions table ready")
    
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
        # ENHANCEMENT 1: Ensure DB initialized on first use
        self._ensure_db_initialized()
        
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
            
            # ENHANCEMENT 4: Graceful degradation - only save to DB if available
            if source != 'cli' and self._db_available:
                try:
                    # Use connection timeout for stability
                    conn = get_database_connection('sessions')
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO sessions.sessions (session_id, ui_context, agent_id, conversation, metadata)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        session_id,
                        ui_context,
                        agent_id,
                        json.dumps([]),
                        json.dumps({'source': source})
                    ))
                    cursor.close()
                    conn.commit()
                    conn.close()
                    print(f"[SessionManager] Created session: {session_id} (ui_context={ui_context}, agent_id={agent_id}, source={source})")
                except Exception as e:
                    print(f"[SessionManager] ⚠️  Failed to save session to DB: {e}")
                    print(f"[SessionManager] Session {session_id} running in memory-only mode")
            elif source == 'cli':
                print(f"[SessionManager] Created CLI session (in-memory only): {session_id}")
            else:
                print(f"[SessionManager] Created session (memory-only - DB unavailable): {session_id}")
            
            return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session data (from cache or DB)
        
        Returns:
            session_data: Dict with session info, or None if not found
        """
        # ENHANCEMENT 1: Ensure DB initialized
        self._ensure_db_initialized()
        
        with self.lock:
            # Check cache first (fast path)
            if session_id in self.sessions:
                self._update_last_active(session_id)
                return self.sessions[session_id]
            
            # ENHANCEMENT 4: Skip DB load if unavailable
            if not self._db_available:
                print(f"[SessionManager] Session not in cache and DB unavailable: {session_id}")
                return None
            
            # Load from DB (slow path - session not active)
            try:
                conn = get_database_connection('sessions')
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, ui_context, agent_id, conversation, metadata, created_at, last_active
                    FROM sessions.sessions
                    WHERE session_id = %s
                """, (session_id,))
                
                row = cursor.fetchone()
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"[SessionManager] ⚠️  Failed to load session from DB: {e}")
                return None
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
            conn = get_database_connection('sessions')
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions.sessions
                SET conversation = %s, last_active = CURRENT_TIMESTAMP
                WHERE session_id = %s
            """, (json.dumps(conversation), session_id))
            cursor.close()
            conn.commit()
            conn.close()
    
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
            conn = get_database_connection('sessions')
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions.sessions
                SET metadata = %s, last_active = CURRENT_TIMESTAMP
                WHERE session_id = %s
            """, (json.dumps(metadata), session_id))
            cursor.close()
            conn.commit()
            conn.close()
    
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
            conn = get_database_connection('sessions')
            cursor = conn.cursor()
            # Get inactive session IDs - PostgreSQL syntax for interval
            cursor.execute("""
                SELECT session_id
                FROM sessions.sessions
                WHERE last_active < NOW() - INTERVAL '%s hours'
            """, (max_age_hours,))
            
            inactive_ids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            
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
            conn = get_database_connection('sessions')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions.sessions WHERE session_id = %s", (session_id,))
            cursor.close()
            conn.commit()
            conn.close()
            
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
            
            conn = get_database_connection('sessions')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sessions.sessions")
            total_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            return {
                'active': active_count,
                'total_db': total_count
            }
    
    def _update_last_active(self, session_id: str):
        """Update last active timestamp (internal helper)"""
        # ENHANCEMENT 4: Skip DB update if unavailable
        if not self._db_available:
            return
        
        try:
            conn = get_database_connection('sessions')
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions.sessions
                SET last_active = CURRENT_TIMESTAMP
                WHERE session_id = %s
            """, (session_id,))
            cursor.close()
            conn.commit()
            conn.close()
        except Exception as e:
            # Non-critical - silently fail if DB update fails
            pass
    
    def get_health_status(self) -> Dict:
        """
        ENHANCEMENT 5: Get database health status for monitoring
        
        Returns:
            Dict with health information:
            - db_initialized: bool
            - db_available: bool
            - db_error: Optional[str]
            - init_attempts: int
            - active_sessions: int
            - mode: 'persistent' | 'memory-only'
        """
        return {
            'db_initialized': self._db_initialized,
            'db_available': self._db_available,
            'db_error': self._db_error,
            'init_attempts': self._init_attempts,
            'active_sessions': len(self.sessions),
            'mode': 'persistent' if self._db_available else 'memory-only'
        }


# ENHANCEMENT 1: Lazy singleton pattern (Dec 5, 2025)
# Don't create instance at import time - create on first use
_session_manager_instance = None
_session_manager_lock = threading.Lock()

def get_session_manager() -> UnifiedSessionManager:
    """
    Get or create singleton session manager instance (lazy initialization)
    
    Returns:
        UnifiedSessionManager: Singleton instance
    
    ENHANCEMENT (Dec 5, 2025): Lazy initialization
    - Flask starts instantly even if Supabase down
    - Database connects on first request
    - Thread-safe singleton pattern
    """
    global _session_manager_instance
    if _session_manager_instance is None:
        with _session_manager_lock:
            if _session_manager_instance is None:
                _session_manager_instance = UnifiedSessionManager()
    return _session_manager_instance

# Backward compatibility: Keep module-level variable for existing imports
# This works because Python evaluates get_session_manager() when accessed
session_manager = get_session_manager()
