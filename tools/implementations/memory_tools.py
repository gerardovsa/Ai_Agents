"""
FILE: tools/implementations/memory_tools.py
PURPOSE: AI Memory management tools for persistent user context

DEPENDENCIES:
- sqlite3 - Database operations
- json - JSON parsing for memories
- datetime - Timestamp management

EXPORTS:
- read_user_memories(user_id, category, tags, **kwargs) - Retrieve user memories
- add_user_memory(user_id, content, category, tags, **kwargs) - Add new memory
- update_user_memory(user_id, memory_id, content, **kwargs) - Update existing memory
- delete_user_memory(user_id, memory_id, **kwargs) - Delete memory

USED BY:
- tools/registry_v3.py (tool execution)
- AI agents (Claude) when user asks to remember something

RELATED FILES:
- AI_infrastructure/routes/user_preferences_routes.py (preferences storage)
- tools/schemas/memory_tools.json (tool definitions)

NOTES:
- Memories stored as JSON array in user_preferences.ai_memories column
- Each memory has: id, category, content, created_at, relevance_score, tags
- User isolation via user_id (users can only access their own memories)
- Auto-generates unique memory IDs

LAST MODIFIED: 2025-11-04 - Initial implementation
"""

import sqlite3
import sys
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add AI_infrastructure to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'AI_infrastructure'))
from shared.database_utils import get_database_connection


def get_db_connection():
    """Get database connection (SQLite or Supabase)"""
    conn = get_database_connection('ai_infrastructure')
    if hasattr(conn, 'row_factory'):  # SQLite
        conn.row_factory = sqlite3.Row
    return conn


def read_user_memories(
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Read user's memories from database
    
    Args:
        category: Optional filter by category (preferences, personal, work, health, etc.)
        tags: Optional filter by tags
        **kwargs: _user_id injected by credential system
    
    Returns:
        Dict with success status and memories array
    
    Example:
        {
            "success": True,
            "memories": [
                {
                    "id": "mem_12345",
                    "category": "preferences",
                    "content": "Prefers detailed technical explanations",
                    "created_at": "2025-11-04T10:30:00Z",
                    "relevance_score": 0.95,
                    "tags": ["communication", "work"]
                }
            ],
            "count": 1
        }
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            return {
                'success': False,
                'error': 'User ID required',
                'memories': [],
                'count': 0
            }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get memories JSON from database
        cursor.execute("""
            SELECT ai_memories
            FROM user_preferences
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row or not row['ai_memories']:
            return {
                'success': True,
                'memories': [],
                'count': 0,
                'message': 'No memories found'
            }
        
        # Parse memories JSON
        memories = json.loads(row['ai_memories'])
        
        # Filter by category if provided
        if category:
            memories = [m for m in memories if m.get('category') == category]
        
        # Filter by tags if provided
        if tags:
            memories = [m for m in memories if any(tag in m.get('tags', []) for tag in tags)]
        
        return {
            'success': True,
            'memories': memories,
            'count': len(memories),
            'message': f'Retrieved {len(memories)} memories'
        }
        
    except json.JSONDecodeError:
        return {
            'success': False,
            'error': 'Invalid memory data format',
            'memories': [],
            'count': 0
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to read memories: {str(e)}',
            'memories': [],
            'count': 0
        }


def add_user_memory(
    content: str,
    category: str = 'general',
    tags: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Add a new memory for the user
    
    Args:
        content: Memory content (what to remember)
        category: Memory category (preferences, personal, work, health, general)
        tags: List of tags for categorization
        **kwargs: _user_id injected by credential system
    
    Returns:
        Dict with success status and created memory
    
    Example:
        {
            "success": True,
            "memory": {
                "id": "mem_12345",
                "category": "preferences",
                "content": "Prefers detailed technical explanations",
                "created_at": "2025-11-04T10:30:00Z",
                "relevance_score": 1.0,
                "tags": ["communication", "work"]
            },
            "message": "Memory added successfully"
        }
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            return {
                'success': False,
                'error': 'User ID required'
            }
        
        if not content or not content.strip():
            return {
                'success': False,
                'error': 'Memory content cannot be empty'
            }
        
        # Validate category
        valid_categories = ['preferences', 'personal', 'work', 'health', 'general']
        if category not in valid_categories:
            category = 'general'
        
        # Create new memory object
        memory_id = f"mem_{uuid.uuid4().hex[:12]}"
        new_memory = {
            'id': memory_id,
            'category': category,
            'content': content.strip(),
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'relevance_score': 1.0,  # New memories start at max relevance
            'tags': tags or []
        }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get existing memories
        cursor.execute("""
            SELECT ai_memories
            FROM user_preferences
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        
        if row and row['ai_memories']:
            memories = json.loads(row['ai_memories'])
        else:
            memories = []
        
        # Add new memory
        memories.append(new_memory)
        
        # Update database
        cursor.execute("""
            UPDATE user_preferences
            SET ai_memories = ?,
                memory_updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (json.dumps(memories), user_id))
        
        # If user has no preferences row yet, create it
        if not row:
            cursor.execute("""
                INSERT INTO user_preferences
                (user_id, ai_memories, memory_updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (user_id, json.dumps(memories)))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'memory': new_memory,
            'total_memories': len(memories),
            'message': f"Memory added successfully. You now have {len(memories)} memories stored."
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to add memory: {str(e)}'
        }


def update_user_memory(
    memory_id: str,
    content: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Update an existing memory
    
    Args:
        memory_id: ID of memory to update
        content: New memory content
        **kwargs: _user_id injected by credential system
    
    Returns:
        Dict with success status and updated memory
    
    Example:
        {
            "success": True,
            "memory": {...},
            "message": "Memory updated successfully"
        }
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            return {
                'success': False,
                'error': 'User ID required'
            }
        
        if not content or not content.strip():
            return {
                'success': False,
                'error': 'Memory content cannot be empty'
            }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get existing memories
        cursor.execute("""
            SELECT ai_memories
            FROM user_preferences
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        
        if not row or not row['ai_memories']:
            conn.close()
            return {
                'success': False,
                'error': 'No memories found'
            }
        
        memories = json.loads(row['ai_memories'])
        
        # Find and update memory
        memory_found = False
        for memory in memories:
            if memory['id'] == memory_id:
                memory['content'] = content.strip()
                memory['updated_at'] = datetime.utcnow().isoformat() + 'Z'
                memory_found = True
                updated_memory = memory
                break
        
        if not memory_found:
            conn.close()
            return {
                'success': False,
                'error': f'Memory with ID {memory_id} not found'
            }
        
        # Update database
        cursor.execute("""
            UPDATE user_preferences
            SET ai_memories = ?,
                memory_updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (json.dumps(memories), user_id))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'memory': updated_memory,
            'message': 'Memory updated successfully'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to update memory: {str(e)}'
        }


def delete_user_memory(
    memory_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Delete a memory
    
    Args:
        memory_id: ID of memory to delete
        **kwargs: _user_id injected by credential system
    
    Returns:
        Dict with success status
    
    Example:
        {
            "success": True,
            "message": "Memory deleted successfully",
            "remaining_memories": 5
        }
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            return {
                'success': False,
                'error': 'User ID required'
            }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get existing memories
        cursor.execute("""
            SELECT ai_memories
            FROM user_preferences
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        
        if not row or not row['ai_memories']:
            conn.close()
            return {
                'success': False,
                'error': 'No memories found'
            }
        
        memories = json.loads(row['ai_memories'])
        
        # Filter out the memory to delete
        original_count = len(memories)
        memories = [m for m in memories if m['id'] != memory_id]
        
        if len(memories) == original_count:
            conn.close()
            return {
                'success': False,
                'error': f'Memory with ID {memory_id} not found'
            }
        
        # Update database
        cursor.execute("""
            UPDATE user_preferences
            SET ai_memories = ?,
                memory_updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (json.dumps(memories), user_id))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': 'Memory deleted successfully',
            'remaining_memories': len(memories)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to delete memory: {str(e)}'
        }
