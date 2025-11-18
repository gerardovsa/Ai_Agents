"""
Agent State Manager
Manages agent execution state for Triple Agent and other AI agents

Replaces OLD Flask's get_or_create_agent_state() pattern with centralized state management
"""

import threading
from queue import Queue
from datetime import datetime
from typing import Dict, Any, Optional


class AgentStateManager:
    """
    Centralized agent state management
    
    Each agent (identified by agent_id + session_id) has:
    - Isolated queue for SSE streaming
    - Execution lock for thread safety
    - Conversation history
    - Status (idle/running)
    - Context (triple_agent, single_viewer, stock_ai)
    """
    
    def __init__(self):
        self.states: Dict[str, Dict[str, Any]] = {}
        self.locks: Dict[str, threading.Lock] = {}
        self._state_lock = threading.Lock()  # Protects states dict
        
        # Agent name mapping
        self.agent_names = {
            '1': 'Data Navigator',
            '2': 'Query Expert',
            '3': 'Calculator',
            'stock_ai': 'Stock AI Assistant',
            'single_viewer': 'Single Agent'
        }
    
    def _get_key(self, agent_id: str, thread_id: str) -> str:
        """
        Generate unique key for agent state
        
        CRITICAL: Uses thread_id (not session_id) for proper message isolation
        This ensures state keys match database thread IDs
        """
        return f"{agent_id}_{thread_id}"
    
    def get_or_create_state(self, agent_id: str, thread_id: str, context: str = 'multi_agent') -> Dict[str, Any]:
        """
        Get or create agent state (thread-safe)
        
        CRITICAL CHANGE (Nov 18, 2025): Now uses thread_id instead of session_id
        This ensures proper message isolation - messages saved to thread_id will
        match the state lookup key.
        
        Args:
            agent_id: Agent identifier (1, 2, 3, etc.)
            thread_id: Thread identifier (used for both state key and database persistence)
            context: Legacy parameter (not used) - defaults to 'multi_agent'
        
        Returns:
            Agent state dictionary with queue, conversation, status, etc.
            
        Note:
            - Previously used session_id, now uses thread_id for consistency
            - session_id === thread_id in current architecture (enforced in agent_routes_v4.py)
        """
        key = self._get_key(agent_id, thread_id)
        
        with self._state_lock:
            if key not in self.states:
                self.states[key] = {
                    'agent_id': agent_id,
                    'agent_name': self.agent_names.get(agent_id, f'Agent {agent_id}'),
                    'session_id': session_id,
                    'status': 'idle',
                    'conversation': [],
                    'queue': Queue(),
                    'last_activity': datetime.now(),
                    'context': context,
                    'created_at': datetime.now(),
                    'location': 'prime',  # NEW: Track thread location for Prime/Agent assignment
                    'user_id': None  # NEW: Track user_id for auto-save
                }
                self.locks[key] = threading.Lock()
                
                print(f"[AgentState] Created state for {self.agent_names.get(agent_id, agent_id)} (session: {session_id[:8]}...)")
            
            return self.states[key]
    
    def get_state(self, agent_id: str, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get agent state if exists (uses thread_id for isolation)"""
        key = self._get_key(agent_id, thread_id)
        return self.states.get(key)
    
    def get_lock(self, agent_id: str, thread_id: str) -> threading.Lock:
        """
        Get execution lock for agent (thread safety)
        
        Args:
            agent_id: Agent identifier
            thread_id: Thread identifier (ensures lock matches thread isolation)
        
        Returns:
            threading.Lock for this specific agent/thread
        """
        key = self._get_key(agent_id, thread_id)
        
        with self._state_lock:
            if key not in self.locks:
                self.locks[key] = threading.Lock()
            
            return self.locks[key]
    
    def update_status(self, agent_id: str, thread_id: str, status: str):
        """Update agent status (idle, running, error)"""
        state = self.get_state(agent_id, thread_id)
        if state:
            state['status'] = status
            state['last_activity'] = datetime.now()
    
    def add_message(self, agent_id: str, thread_id: str, role: str, content: Any):
        """Add message to conversation history"""
        state = self.get_state(agent_id, thread_id)
        if state:
            state['conversation'].append({
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat()
            })
            state['last_activity'] = datetime.now()
    
    def clear_conversation(self, agent_id: str, thread_id: str) -> bool:
        """
        Clear conversation history
        
        Returns:
            True if cleared, False if agent is running
        """
        state = self.get_state(agent_id, thread_id)
        if not state:
            return True
        
        if state['status'] == 'running':
            return False
        
        state['conversation'] = []
        state['last_activity'] = datetime.now()
        return True
    
    def get_queue(self, agent_id: str, thread_id: str) -> Queue:
        """Get SSE queue for agent"""
        state = self.get_or_create_state(agent_id, thread_id)
        return state['queue']
    
    def set_thread_location(self, agent_id: str, thread_id: str, location: str, user_id: Optional[int] = None):
        """
        Set thread location for Prime/Agent assignment tracking
        
        Args:
            agent_id: Agent identifier
            thread_id: Thread identifier
            location: Thread location (prime, agent-1, agent-2, etc.)
            user_id: User ID (optional)
        """
        state = self.get_state(agent_id, thread_id)
        if state:
            state['location'] = location
            if user_id is not None:
                state['user_id'] = user_id
            state['last_activity'] = datetime.now()
            print(f"[AgentState] Updated location: {thread_id[:8]}... -> {location}")
    
    def cleanup_old_states(self, max_age_hours: int = 24):
        """
        Remove old inactive states (memory management)
        
        Args:
            max_age_hours: Remove states older than this
        """
        now = datetime.now()
        keys_to_remove = []
        
        with self._state_lock:
            for key, state in self.states.items():
                age = (now - state['last_activity']).total_seconds() / 3600
                if age > max_age_hours and state['status'] == 'idle':
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.states[key]
                if key in self.locks:
                    del self.locks[key]
                print(f"[AgentState] Cleaned up old state: {key}")
        
        return len(keys_to_remove)


# Global instance
agent_state_manager = AgentStateManager()
