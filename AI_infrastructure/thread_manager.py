"""
Enhanced Thread Manager API
Implements AnythingLLM-style thread/message management with database persistence

CRITICAL FIX (Nov 12, 2025): KEEP thinking blocks in saved messages
When thinking is enabled, Anthropic API REQUIRES assistant messages to start with thinking blocks.
Stripping them causes 400 errors on subsequent turns.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import re
from pathlib import Path
from AI_infrastructure.shared.database_utils import get_database_connection


def strip_thinking_blocks_from_content(content: Any) -> Any:
    """
    DISABLED (Nov 12, 2025): No longer strip thinking blocks
    
    Thinking blocks MUST be preserved for Anthropic API when thinking is enabled.
    This function now just returns content unchanged.
    """
    # CRITICAL: Do NOT strip thinking blocks - they're required by Anthropic API
    return content


def prepare_content_for_storage(content: Any) -> Any:
    """
    Prepare assistant message content for database storage
    
    UPDATED (Nov 12, 2025 - Per Anthropic SDK Documentation):
    Per official Anthropic docs:
    "When continuing conversations with tool use, thinking blocks are cached and count as input tokens when read from cache"
    "Thinking blocks must be explicitly preserved and returned with the tool results"
    "The signature field contains encrypted thinking and verifies authenticity"
    
    - Keep: thinking blocks (REQUIRED for extended thinking with tools)
    - Keep: redacted_thinking blocks (REQUIRED for safety compliance)
    - Keep: text blocks (main response)
    - Keep: tool_use blocks (transparency)
    - Remove: tool_result blocks (go in user messages)
    
    Returns:
        Filtered content with thinking, text, and tool_use blocks
    """
    if isinstance(content, str):
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                filtered = [
                    block for block in parsed
                    if block.get('type') in ('thinking', 'redacted_thinking', 'text', 'tool_use')
                ]
                return json.dumps(filtered)
            return content
        except (json.JSONDecodeError, TypeError):
            return content
    elif isinstance(content, list):
        return [
            block for block in content
            if block.get('type') in ('thinking', 'redacted_thinking', 'text', 'tool_use')
        ]
    return content


# CORRECT: Use data/sessions.db (not AI_infrastructure/data/sessions.db)
root_dir = Path(__file__).parent.parent
DB_PATH = str(root_dir / 'data' / 'sessions.db')

class ThreadManager:
    """Manages workspace threads and messages with database persistence"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
    
    def _get_connection(self):
        """Get database connection"""
        conn = get_database_connection()
        conn.row_factory = sqlite3.Row  # Enable dictionary-like access
        return conn
    
    def _generate_slug(self, text: str) -> str:
        """Generate URL-safe slug from text"""
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:50]  # Limit to 50 chars
    
    def _get_workspace_by_slug(self, workspace_slug: str) -> Optional[Dict]:
        """
        Look up workspace from ai_infrastructure.db
        
        Args:
            workspace_slug: Workspace slug (e.g., 'team-alpha-workspace-2')
        
        Returns:
            Dict with workspace details including id (INTEGER) or None if not found
        """
        import sqlite3
        from pathlib import Path
        
        from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path
        db_path = get_ai_infrastructure_db_path()
        
        conn = get_database_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, user_id, name, description, created_at, metadata
                FROM workspaces
                WHERE id = %s
            """, (workspace_slug,))  # workspace_slug is actually workspace_id as TEXT currently
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()
    
    # ==================== WORKSPACE MANAGEMENT ====================
    
    def create_workspace(self, name: str, description: str = "", metadata: Dict = None) -> Dict:
        """
        Create a new workspace
        
        Args:
            name: Workspace name
            description: Optional description
            metadata: Optional metadata dict
            
        Returns:
            Dict with workspace details
        """
        slug = self._generate_slug(name)
        timestamp = datetime.now().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO workspaces (slug, name, description, created_at, updated_at, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (slug, name, description, timestamp, timestamp, json.dumps(metadata or {})))
            
            workspace_id = cursor.lastrowid
            conn.commit()
            
            return {
                'id': workspace_id,
                'slug': slug,
                'name': name,
                'description': description,
                'created_at': timestamp,
                'updated_at': timestamp,
                'metadata': metadata or {}
            }
        finally:
            conn.close()
    
    def get_workspace(self, slug: str) -> Optional[Dict]:
        """Get workspace by slug"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM workspaces WHERE slug = %s', (slug,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'slug': row['slug'],
                    'name': row['name'],
                    'description': row['description'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                }
            return None
        finally:
            conn.close()
    
    def list_workspaces(self) -> List[Dict]:
        """List all workspaces"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM workspaces ORDER BY updated_at DESC')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # ==================== THREAD MANAGEMENT ====================
    
    def create_thread(self, workspace_slug: str, name: str, user_id: int = None, metadata: Dict = None) -> Dict:
        """
        Create a new thread in a workspace
        
        Args:
            workspace_slug: Workspace slug
            name: Thread name
            user_id: Optional user ID
            metadata: Optional metadata dict
            
        Returns:
            Dict with thread details
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get workspace ID
            workspace = self.get_workspace(workspace_slug)
            if not workspace:
                raise ValueError(f"Workspace '{workspace_slug}' not found")
            
            workspace_id = workspace['id']
            thread_slug = self._generate_slug(name) + f"-{int(datetime.now().timestamp())}"
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO threads (thread_slug, workspace_id, user_id, name, created_at, updated_at, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (thread_slug, workspace_id, user_id, name, timestamp, timestamp, json.dumps(metadata or {})))
            
            thread_id = cursor.lastrowid
            conn.commit()
            
            return {
                'id': thread_id,
                'thread_slug': thread_slug,
                'workspace_id': workspace_id,
                'workspace_slug': workspace_slug,
                'user_id': user_id,
                'name': name,
                'created_at': timestamp,
                'updated_at': timestamp,
                'metadata': metadata or {},
                'message_count': 0
            }
        finally:
            conn.close()
    
    def get_thread(self, workspace_slug: str, thread_slug: str) -> Optional[Dict]:
        """Get thread by slug"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT t.*, w.slug as workspace_slug, 
                       (SELECT COUNT(*) FROM messages WHERE thread_id = t.id) as message_count
                FROM threads t
                JOIN workspaces w ON t.workspace_id = w.id
                WHERE w.slug = %s AND t.thread_slug = %s
            ''', (workspace_slug, thread_slug))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()
    
    def list_threads(self, workspace_slug: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """List threads in a workspace"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM v_thread_summary 
                WHERE workspace_name = (SELECT name FROM workspaces WHERE slug = %s)
                ORDER BY updated_at DESC
                LIMIT %s OFFSET %s
            ''', (workspace_slug, limit, offset))
            
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def update_thread(self, workspace_slug: str, thread_slug: str, name: str = None, metadata: Dict = None) -> Dict:
        """Update thread details"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            thread = self.get_thread(workspace_slug, thread_slug)
            if not thread:
                raise ValueError(f"Thread '{thread_slug}' not found")
            
            timestamp = datetime.now().isoformat()
            updates = ['updated_at = ?']
            params = [timestamp]
            
            if name:
                updates.append('name = ?')
                params.append(name)
            
            if metadata:
                updates.append('metadata = ?')
                params.append(json.dumps(metadata))
            
            params.append(thread['id'])
            
            cursor.execute(f'''
                UPDATE threads 
                SET {', '.join(updates)}
                WHERE id = %s
            ''', params)
            
            conn.commit()
            return self.get_thread(workspace_slug, thread_slug)
        finally:
            conn.close()
    
    def delete_thread(self, workspace_slug: str, thread_slug: str) -> bool:
        """Delete thread and all its messages"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            thread = self.get_thread(workspace_slug, thread_slug)
            if not thread:
                return False
            
            # Delete all messages first (foreign key constraint)
            cursor.execute('DELETE FROM messages WHERE thread_id = %s', (thread['id'],))
            
            # Delete thread
            cursor.execute('DELETE FROM threads WHERE id = %s', (thread['id'],))
            
            conn.commit()
            return True
        finally:
            conn.close()
    
    # ==================== MESSAGE MANAGEMENT ====================
    
    def add_message(
        self,
        workspace_slug: str,
        thread_slug: str,
        role: str,
        content: str,
        prompt: str = None,
        user_id: int = None,
        include: bool = True,
        tool_calls: List[Dict] = None,
        tokens_used: int = None,
        response_time_ms: int = None,
        metadata: Dict = None
    ) -> Dict:
        """
        Add a message to a thread
        
        Args:
            workspace_slug: Workspace slug
            thread_slug: Thread slug
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            prompt: Original prompt (for assistant responses)
            user_id: Optional user ID
            include: Whether to include in LLM context
            tool_calls: Optional tool call details
            tokens_used: Token count
            response_time_ms: Response latency
            metadata: Optional metadata
            
        Returns:
            Dict with message details
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Look up thread from sessions.db (thread already has workspace_id)
            cursor.execute("""
                SELECT id, thread_slug, name, workspace_id FROM threads
                WHERE thread_slug = %s
            """, (thread_slug,))
            
            thread_row = cursor.fetchone()
            if not thread_row:
                raise ValueError(f"Thread '{thread_slug}' not found in sessions.db")
            
            thread_id = thread_row[0]
            workspace_id = thread_row[3]  # Get workspace_id from thread (INTEGER)
            
            timestamp = datetime.now().isoformat()
            
            # ✅ BEST PRACTICE: Prepare content for storage
            # Keep only text + tool_use blocks (ChatGPT/Claude.ai pattern)
            if role == 'assistant':
                content = prepare_content_for_storage(content)
            
            # Do not persist response_time_ms in messages table; keep for logs only
            cursor.execute('''
                INSERT INTO messages (
                    workspace_id, thread_id, role, content, prompt,
                    user_id, include, tool_calls, tokens_used,
                    created_at, updated_at, metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                workspace_id, thread_id, role, content, prompt,
                user_id, 1 if include else 0, json.dumps(tool_calls or []),
                tokens_used, timestamp, timestamp,
                json.dumps(metadata or {})
            ))
            
            message_id = cursor.lastrowid
            
            # Update thread's updated_at timestamp
            cursor.execute('''
                UPDATE threads SET updated_at = %s WHERE id = %s
            ''', (timestamp, thread_id))
            
            conn.commit()
            
            # Log response time (do not store in DB)
            if response_time_ms is not None:
                try:
                    print(f"[TIMING] thread_id={thread_slug} message_id={message_id} response_time_ms={response_time_ms}")
                except Exception:
                    pass

            return {
                'id': message_id,
                'workspace_id': workspace_id,
                'thread_id': thread_id,
                'role': role,
                'content': content,
                'prompt': prompt,
                'include': include,
                'tool_calls': tool_calls or [],
                'tokens_used': tokens_used,
                'response_time_ms': response_time_ms,
                'created_at': timestamp,
                'metadata': metadata or {}
            }
        finally:
            conn.close()
    
    def get_messages(
        self,
        workspace_slug: str,
        thread_slug: str,
        include_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        Get messages from a thread
        
        Args:
            workspace_slug: Workspace slug
            thread_slug: Thread slug
            include_only: If True, only return messages with include=1
            limit: Maximum messages to return
            offset: Pagination offset
            
        Returns:
            List of message dicts
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            thread = self.get_thread(workspace_slug, thread_slug)
            if not thread:
                return []
            
            query = '''
                SELECT * FROM messages 
                WHERE thread_id = %s
            '''
            
            params = [thread['id']]
            
            if include_only:
                query += ' AND include = 1'
            
            query += ' ORDER BY created_at ASC LIMIT %s OFFSET %s'
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            
            messages = []
            for row in cursor.fetchall():
                msg = dict(row)
                # Parse JSON fields
                msg['tool_calls'] = json.loads(msg['tool_calls']) if msg['tool_calls'] else []
                msg['metadata'] = json.loads(msg['metadata']) if msg['metadata'] else {}
                messages.append(msg)
            
            return messages
        finally:
            conn.close()
    
    def update_message_feedback(self, message_id: int, feedback_score: int) -> bool:
        """
        Update message feedback score
        
        Args:
            message_id: Message ID
            feedback_score: 1 (thumbs up), 0 (thumbs down), NULL (no rating)
            
        Returns:
            True if updated successfully
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE messages 
                SET feedback_score = %s, updated_at = %s
                WHERE id = %s
            ''', (feedback_score if feedback_score in [0, 1] else None, datetime.now().isoformat(), message_id))
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def hide_messages(self, message_ids: List[int]) -> int:
        """
        Hide messages from LLM context (mark include=0)
        
        Args:
            message_ids: List of message IDs to hide
            
        Returns:
            Number of messages hidden
        """
        if not message_ids:
            return 0
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            placeholders = ','.join(['%s' for _ in message_ids])
            cursor.execute(f'''
                UPDATE messages 
                SET include = 0, updated_at = %s
                WHERE id IN ({placeholders})
            ''', [datetime.now().isoformat()] + message_ids)
            
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def reset_thread_context(self, workspace_slug: str, thread_slug: str) -> int:
        """
        Reset thread context by marking all messages as include=0
        (AnythingLLM reset pattern)
        
        Args:
            workspace_slug: Workspace slug
            thread_slug: Thread slug
            
        Returns:
            Number of messages marked as excluded
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            thread = self.get_thread(workspace_slug, thread_slug)
            if not thread:
                return 0
            
            cursor.execute('''
                UPDATE messages 
                SET include = 0, updated_at = %s
                WHERE thread_id = %s
            ''', (datetime.now().isoformat(), thread['id']))
            
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def get_thread_statistics(self, workspace_slug: str, thread_slug: str) -> Dict:
        """Get comprehensive statistics for a thread"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            thread = self.get_thread(workspace_slug, thread_slug)
            if not thread:
                return {}
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_messages,
                    SUM(CASE WHEN include = 1 THEN 1 ELSE 0 END) as active_messages,
                    SUM(CASE WHEN role = 'user' THEN 1 ELSE 0 END) as user_messages,
                    SUM(CASE WHEN role = 'assistant' THEN 1 ELSE 0 END) as assistant_messages,
                    SUM(tokens_used) as total_tokens,
                    AVG(response_time_ms) as avg_response_time,
                    SUM(CASE WHEN feedback_score = 1 THEN 1 ELSE 0 END) as thumbs_up,
                    SUM(CASE WHEN feedback_score = 0 THEN 1 ELSE 0 END) as thumbs_down
                FROM messages
                WHERE thread_id = %s
            ''', (thread['id'],))
            
            stats = dict(cursor.fetchone())
            stats['thread_name'] = thread['name']
            stats['thread_slug'] = thread['thread_slug']
            stats['created_at'] = thread['created_at']
            stats['updated_at'] = thread['updated_at']
            
            return stats
        finally:
            conn.close()

# ==================== FLASK API ROUTES ====================

def create_thread_api_routes(app, thread_manager: ThreadManager):
    """Add thread management routes to Flask app"""
    
    from flask import request, jsonify
    
    @app.route('/api/threads/workspaces', methods=['GET'])
    def list_workspaces():
        """List all workspaces"""
        try:
            workspaces = thread_manager.list_workspaces()
            return jsonify({'workspaces': workspaces}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/threads/<workspace_slug>/threads', methods=['GET'])
    def list_threads(workspace_slug):
        """List threads in workspace"""
        try:
            limit = request.args.get('limit', 50, type=int)
            offset = request.args.get('offset', 0, type=int)
            
            threads = thread_manager.list_threads(workspace_slug, limit, offset)
            return jsonify({'threads': threads}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/threads/<workspace_slug>/threads', methods=['POST'])
    def create_thread(workspace_slug):
        """Create new thread"""
        try:
            data = request.json
            thread = thread_manager.create_thread(
                workspace_slug,
                data.get('name', 'New Thread'),
                data.get('user_id'),
                data.get('metadata')
            )
            return jsonify(thread), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/threads/<workspace_slug>/threads/<thread_slug>', methods=['GET'])
    def get_thread(workspace_slug, thread_slug):
        """Get thread details"""
        try:
            thread = thread_manager.get_thread(workspace_slug, thread_slug)
            if not thread:
                return jsonify({'error': 'Thread not found'}), 404
            return jsonify(thread), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/threads/<workspace_slug>/threads/<thread_slug>', methods=['DELETE'])
    def delete_thread(workspace_slug, thread_slug):
        """Delete thread"""
        try:
            success = thread_manager.delete_thread(workspace_slug, thread_slug)
            if not success:
                return jsonify({'error': 'Thread not found'}), 404
            return jsonify({'message': 'Thread deleted'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/threads/<workspace_slug>/threads/<thread_slug>/messages', methods=['GET'])
    def get_messages(workspace_slug, thread_slug):
        """Get thread messages"""
        try:
            include_only = request.args.get('include_only', 'true').lower() == 'true'
            limit = request.args.get('limit', 100, type=int)
            offset = request.args.get('offset', 0, type=int)
            
            messages = thread_manager.get_messages(
                workspace_slug, thread_slug, include_only, limit, offset
            )
            return jsonify({'messages': messages}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/threads/<workspace_slug>/threads/<thread_slug>/messages', methods=['POST'])
    def add_message(workspace_slug, thread_slug):
        """Add message to thread"""
        try:
            data = request.json
            message = thread_manager.add_message(
                workspace_slug, thread_slug,
                data.get('role', 'user'),
                data.get('content'),
                data.get('prompt'),
                data.get('user_id'),
                data.get('include', True),
                data.get('tool_calls'),
                data.get('tokens_used'),
                data.get('response_time_ms'),
                data.get('metadata')
            )
            return jsonify(message), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/threads/<workspace_slug>/threads/<thread_slug>/reset', methods=['POST'])
    def reset_thread(workspace_slug, thread_slug):
        """Reset thread context (hide all messages)"""
        try:
            count = thread_manager.reset_thread_context(workspace_slug, thread_slug)
            return jsonify({'message': f'Reset {count} messages'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/threads/<workspace_slug>/threads/<thread_slug>/stats', methods=['GET'])
    def get_thread_stats(workspace_slug, thread_slug):
        """Get thread statistics"""
        try:
            stats = thread_manager.get_thread_statistics(workspace_slug, thread_slug)
            if not stats:
                return jsonify({'error': 'Thread not found'}), 404
            return jsonify(stats), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/threads/messages/<int:message_id>/feedback', methods=['POST'])
    def update_feedback(message_id):
        """Update message feedback"""
        try:
            data = request.json
            score = data.get('score')  # 1, 0, or null
            success = thread_manager.update_message_feedback(message_id, score)
            if not success:
                return jsonify({'error': 'Message not found'}), 404
            return jsonify({'message': 'Feedback updated'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Test the thread manager
    tm = ThreadManager()
    
    # Create default workspace if needed
    try:
        workspace = tm.get_workspace('default')
        if not workspace:
            workspace = tm.create_workspace('Default Workspace', 'Main workspace for general use')
            print(f" Created workspace: {workspace}")
    except Exception as e:
        print(f" Error: {e}")
