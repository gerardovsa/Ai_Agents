r"""
Unit tests for UnifiedSessionManager

Run:
    cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder
    python -m pytest AI_infrastructure/tests/test_session_manager.py -v
"""

import pytest
import os
import tempfile
from queue import Queue
from threading import Lock

import sys
# Add core directory to path (not parent directory)
core_path = os.path.join(os.path.dirname(__file__), '..', 'core')
sys.path.insert(0, core_path)

from unified_session_manager import UnifiedSessionManager


class TestSessionManager:
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, 'test_sessions.db')
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)
    
    
    @pytest.fixture
    def manager(self, temp_db):
        """Create session manager with temp database"""
        return UnifiedSessionManager(db_path=temp_db)
    
    
    def test_create_session(self, manager):
        """Test creating a new session"""
        session_id = manager.create_session('stock_chat')
        
        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) == 36  # UUID format
        
        # Verify session exists
        session = manager.get_session(session_id)
        assert session is not None
        assert session['ui_context'] == 'stock_chat'
        assert session['agent_id'] is None
        assert session['conversation'] == []
    
    
    def test_create_session_with_agent_id(self, manager):
        """Test creating session with agent_id (for Triple Agent)"""
        session_id = manager.create_session('triple_agent', agent_id='2')
        
        session = manager.get_session(session_id)
        assert session['ui_context'] == 'triple_agent'
        assert session['agent_id'] == '2'
    
    
    def test_get_nonexistent_session(self, manager):
        """Test retrieving non-existent session"""
        session = manager.get_session('nonexistent-uuid')
        assert session is None
    
    
    def test_update_conversation(self, manager):
        """Test updating conversation"""
        session_id = manager.create_session('data_agent_chat')
        
        conversation = [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi there!'}
        ]
        
        success = manager.update_conversation(session_id, conversation)
        assert success is True
        
        # Verify update
        session = manager.get_session(session_id)
        assert session['conversation'] == conversation
    
    
    def test_get_queue(self, manager):
        """Test getting SSE queue for session"""
        session_id = manager.create_session('stock_chat')
        
        queue = manager.get_queue(session_id)
        assert isinstance(queue, Queue)
        
        # Test putting/getting from queue
        queue.put({'type': 'test', 'data': 'hello'})
        event = queue.get()
        assert event['type'] == 'test'
        assert event['data'] == 'hello'
    
    
    def test_get_lock(self, manager):
        """Test getting execution lock for session"""
        session_id = manager.create_session('stock_chat')
        
        lock = manager.get_lock(session_id)
        assert isinstance(lock, Lock)
        
        # Test acquiring lock
        acquired = lock.acquire(blocking=False)
        assert acquired is True
        lock.release()
    
    
    def test_cleanup_inactive_sessions(self, manager):
        """Test cleaning up old sessions"""
        # Create session
        session_id = manager.create_session('stock_chat')
        
        # Artificially age the session in database
        import sqlite3
        conn = sqlite3.connect(manager.db_path)
        conn.execute("""
            UPDATE sessions 
            SET updated_at = datetime('now', '-8 hours')
            WHERE session_id = ?
        """, (session_id,))
        conn.commit()
        conn.close()
        
        # Run cleanup (remove sessions older than 7 hours)
        removed = manager.cleanup_inactive_sessions(hours=7)
        
        # Verify session was removed
        session = manager.get_session(session_id)
        assert session is None
    
    
    def test_persistence(self, temp_db):
        """Test session persistence across manager instances"""
        # Create session with first manager
        manager1 = UnifiedSessionManager(db_path=temp_db)
        session_id = manager1.create_session('stock_chat')
        manager1.update_conversation(session_id, [
            {'role': 'user', 'content': 'Test message'}
        ])
        
        # Create second manager (should load from database)
        manager2 = UnifiedSessionManager(db_path=temp_db)
        session = manager2.get_session(session_id)
        
        assert session is not None
        assert session['ui_context'] == 'stock_chat'
        assert len(session['conversation']) == 1
        assert session['conversation'][0]['content'] == 'Test message'
    
    
    def test_multiple_sessions(self, manager):
        """Test managing multiple concurrent sessions"""
        session_ids = []
        
        # Create 5 sessions
        for i in range(5):
            session_id = manager.create_session(
                ui_context='stock_chat' if i % 2 == 0 else 'data_agent_chat',
                agent_id=str(i) if i % 3 == 0 else None
            )
            session_ids.append(session_id)
        
        # Verify all sessions exist
        for session_id in session_ids:
            session = manager.get_session(session_id)
            assert session is not None
        
        # Verify each has independent queue
        queues = [manager.get_queue(sid) for sid in session_ids]
        assert len(set(id(q) for q in queues)) == 5  # All unique objects
    
    
    def test_conversation_ordering(self, manager):
        """Test conversation messages maintain order"""
        session_id = manager.create_session('stock_chat')
        
        conversation = []
        for i in range(10):
            conversation.append({
                'role': 'user' if i % 2 == 0 else 'assistant',
                'content': f'Message {i}'
            })
        
        manager.update_conversation(session_id, conversation)
        
        # Retrieve and verify order
        session = manager.get_session(session_id)
        for i, msg in enumerate(session['conversation']):
            assert msg['content'] == f'Message {i}'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
