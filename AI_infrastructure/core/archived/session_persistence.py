"""
Session Persistence - AI_agents Standalone Version
Simplified session management without In_House_SQL dependencies

This module provides:
1. Simple session creation
2. In-memory session storage (no database required)
3. Conversation history management
4. Compatible with agent_routes_v4.py
"""

from typing import Dict, Optional, List
import secrets
from datetime import datetime

# In-memory session storage (survives during Flask runtime)
_sessions = {}


def load_or_create_session(agent_id: str, session_id: Optional[str], ui_context: str) -> Dict:
    """
    Load existing session or create new one
    
    Args:
        agent_id: Agent identifier (1, 2, 3, stock_ai, data_agent, etc.)
        session_id: Session ID from frontend (None = create new)
        ui_context: UI context string (triple_agent, stock_chat, etc.)
    
    Returns:
        Agent state dict with session_id, conversation, and context
    """
    # If no session_id provided, create new one
    if not session_id:
        timestamp = int(datetime.now().timestamp() * 1000)
        session_id = f"session_{timestamp}_{secrets.token_urlsafe(8)}"
        print(f"[SessionPersistence] Created new session: {session_id}")
    
    # Check if session exists
    if session_id in _sessions:
        print(f"[SessionPersistence] Loading existing session: {session_id} ({len(_sessions[session_id]['conversation'])} messages)")
        return _sessions[session_id]
    
    # Create new session state
    state = {
        'session_id': session_id,
        'agent_id': agent_id,
        'ui_context': ui_context,
        'conversation': [],
        'context': {},
        'metadata': {},
        'created_at': datetime.now().isoformat(),
        'last_active': datetime.now().isoformat()
    }
    
    _sessions[session_id] = state
    print(f"[SessionPersistence] Created session state: {session_id} (agent={agent_id})")
    
    return state


def save_conversation(agent_id: str, session_id: str, conversation: List[Dict]):
    """
    Save conversation to session storage
    
    Args:
        agent_id: Agent identifier
        session_id: Session ID
        conversation: Full conversation history
    """
    if session_id not in _sessions:
        print(f"[SessionPersistence] Warning: Session {session_id} not found, creating")
        _sessions[session_id] = {
            'session_id': session_id,
            'agent_id': agent_id,
            'conversation': [],
            'context': {},
            'created_at': datetime.now().isoformat()
        }
    
    _sessions[session_id]['conversation'] = conversation
    _sessions[session_id]['last_active'] = datetime.now().isoformat()
    
    print(f"[SessionPersistence] Saved conversation: {session_id} ({len(conversation)} messages)")


def get_session(session_id: str) -> Optional[Dict]:
    """
    Get session by ID
    
    Args:
        session_id: Session ID
    
    Returns:
        Session dict or None if not found
    """
    return _sessions.get(session_id)


def delete_session(session_id: str) -> bool:
    """
    Delete a session
    
    Args:
        session_id: Session ID
    
    Returns:
        True if deleted, False if not found
    """
    if session_id in _sessions:
        del _sessions[session_id]
        print(f"[SessionPersistence] Deleted session: {session_id}")
        return True
    return False


def get_all_sessions(ui_context: Optional[str] = None) -> List[Dict]:
    """
    Get all sessions, optionally filtered by UI context
    
    Args:
        ui_context: Optional UI context filter
    
    Returns:
        List of session dicts
    """
    if ui_context:
        return [s for s in _sessions.values() if s.get('ui_context') == ui_context]
    return list(_sessions.values())


def clear_all_sessions():
    """Clear all sessions (for testing/debugging)"""
    _sessions.clear()
    print("[SessionPersistence] Cleared all sessions")


# Compatibility aliases for agent_worker.py
create_persistent_session = lambda agent_id, ui_context: load_or_create_session(agent_id, None, ui_context)['session_id']
get_all_sessions_for_ui = get_all_sessions


print("[SessionPersistence] AI_agents standalone module loaded")
