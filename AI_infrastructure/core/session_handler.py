"""
Session Handler - Manages session storage and retrieval
Part of V4 Modular Architecture

Responsibilities:
- Load/save conversation sessions
- Session validation
- Conversation history management
- Session metadata tracking
"""

from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime
import sys
from pathlib import Path

# Add paths - need to add parent before importing config
ai_infra_dir = Path(__file__).parent.parent
if str(ai_infra_dir) not in sys.path:
    sys.path.insert(0, str(ai_infra_dir))

# Add tools directory for config access
tools_dir = ai_infra_dir.parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from AI_infrastructure.utils.logger import get_logger
from AI_infrastructure.config.constants import MAX_CONVERSATION_LENGTH

logger = get_logger(__name__)


class SessionHandler:
    """
    Handles session storage and retrieval for conversations.
    
    Features:
    - In-memory session storage (for sync mode)
    - Session creation and validation
    - Conversation history management
    - Automatic session ID generation
    
    Note: For async mode with persistence, use UnifiedSessionManager instead.
    This is a lightweight handler for synchronous operations.
    
    Usage:
        handler = SessionHandler()
        
        # Create new session
        session = handler.create_session(user_id=1)
        
        # Load session
        session_data = handler.load_session(session['session_id'])
        
        # Save conversation
        handler.save_session(session_id, conversation)
    """

    def __init__(self):
        """Initialize session handler with in-memory storage."""
        self.sessions = {}  # In-memory storage: {session_id: session_data}
        logger.info("💾 SessionHandler initialized (in-memory mode)")

    def create_session(self, user_id: Optional[int] = None, 
                      ui_context: str = 'agent_v4') -> Dict[str, Any]:
        """
        Create a new session.
        
        Args:
            user_id: Optional user ID
            ui_context: UI context identifier
            
        Returns:
            Session dict with structure:
            {
                "session_id": "uuid",
                "user_id": int or None,
                "ui_context": str,
                "conversation": [],
                "created_at": iso_timestamp,
                "updated_at": iso_timestamp,
                "metadata": {}
            }
            
        Example:
            session = handler.create_session(user_id=1)
            print(f"Created session: {session['session_id']}")
        """
        session_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        session = {
            'session_id': session_id,
            'user_id': user_id,
            'ui_context': ui_context,
            'conversation': [],
            'created_at': timestamp,
            'updated_at': timestamp,
            'metadata': {}
        }
        
        self.sessions[session_id] = session
        
        logger.info(f"Session created: {session_id[:8]}... (user={user_id})")
        logger.debug(f"Session context: {ui_context}")
        
        return session

    def load_session(self, session_id: str, create_if_missing: bool = False,
                    user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Load a session by ID.
        
        Args:
            session_id: Session UUID
            create_if_missing: Create new session if not found
            user_id: User ID for new session (if create_if_missing=True)
            
        Returns:
            Session dict or new session if create_if_missing=True
            
        Raises:
            KeyError: If session not found and create_if_missing=False
            
        Example:
            try:
                session = handler.load_session(session_id)
                print(f"Loaded {len(session['conversation'])} messages")
            except KeyError:
                print("Session not found")
        """
        logger.debug(f"📂 Loading session: {session_id[:8]}...")
        
        if session_id in self.sessions:
            session = self.sessions[session_id]
            logger.info(f"Session loaded: {session_id[:8]}... ({len(session['conversation'])} messages)")
            return session
        
        if create_if_missing:
            logger.info(f"ℹ️ Session not found, creating new: {session_id[:8]}...")
            session = self.create_session(user_id=user_id)
            # Override generated ID with requested ID
            old_id = session['session_id']
            session['session_id'] = session_id
            self.sessions[session_id] = session
            del self.sessions[old_id]
            return session
        
        logger.error(f" Session not found: {session_id[:8]}...")
        raise KeyError(f"Session not found: {session_id}")

    def save_session(self, session_id: str, conversation: List[Dict[str, Any]],
                    metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Save session conversation and metadata.
        
        Args:
            session_id: Session UUID
            conversation: Updated conversation history
            metadata: Optional metadata dict to merge
            
        Raises:
            KeyError: If session not found
            
        Example:
            conversation.append({
                "role": "user",
                "content": "Hello"
            })
            handler.save_session(session_id, conversation)
        """
        logger.debug(f"💾 Saving session: {session_id[:8]}...")
        
        if session_id not in self.sessions:
            logger.error(f" Cannot save: Session not found: {session_id[:8]}...")
            raise KeyError(f"Session not found: {session_id}")
        
        session = self.sessions[session_id]
        
        # Update conversation (truncate if too long)
        if len(conversation) > MAX_CONVERSATION_LENGTH:
            logger.warning(f"⚠️ Truncating conversation: {len(conversation)} → {MAX_CONVERSATION_LENGTH}")
            conversation = conversation[-MAX_CONVERSATION_LENGTH:]
        
        session['conversation'] = conversation
        session['updated_at'] = datetime.utcnow().isoformat()
        
        # Merge metadata
        if metadata:
            session['metadata'].update(metadata)
            logger.debug(f"📝 Updated metadata: {list(metadata.keys())}")
        
        logger.info(f"Session saved: {session_id[:8]}... ({len(conversation)} messages)")

    def get_conversation(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session UUID
            
        Returns:
            List of message dicts
            
        Raises:
            KeyError: If session not found
            
        Example:
            conversation = handler.get_conversation(session_id)
            for msg in conversation:
                print(f"{msg['role']}: {msg['content'][:50]}...")
        """
        logger.debug(f"📖 Getting conversation: {session_id[:8]}...")
        
        session = self.load_session(session_id)
        conversation = session['conversation']
        
        logger.debug(f"Retrieved {len(conversation)} messages")
        return conversation

    def delete_session(self, session_id: str) -> None:
        """
        Delete a session.
        
        Args:
            session_id: Session UUID
            
        Example:
            handler.delete_session(session_id)
            print("Session deleted")
        """
        logger.info(f"🗑️ Deleting session: {session_id[:8]}...")
        
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session deleted: {session_id[:8]}...")
        else:
            logger.warning(f"⚠️ Session not found for deletion: {session_id[:8]}...")

    def list_sessions(self, user_id: Optional[int] = None) -> List[str]:
        """
        List all session IDs, optionally filtered by user.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of session IDs
            
        Example:
            sessions = handler.list_sessions(user_id=1)
            print(f"User has {len(sessions)} sessions")
        """
        logger.debug(f"📋 Listing sessions (user_id={user_id})")
        
        if user_id is None:
            session_ids = list(self.sessions.keys())
        else:
            session_ids = [
                sid for sid, session in self.sessions.items()
                if session.get('user_id') == user_id
            ]
        
        logger.debug(f"Found {len(session_ids)} sessions")
        return session_ids

    def get_session_count(self) -> int:
        """
        Get total number of sessions.
        
        Returns:
            Count of sessions
            
        Example:
            count = handler.get_session_count()
            print(f"Total sessions: {count}")
        """
        count = len(self.sessions)
        logger.debug(f"📊 Total sessions: {count}")
        return count


# Export
__all__ = ['SessionHandler']
