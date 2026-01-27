"""
Message Manager - Message Operations

Handles all message-related operations including:
- Adding messages to threads
- Retrieving messages
- Message listing and pagination
- Message search
- Message metadata management
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database_utils import get_database_connection, convert_sql_placeholders
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

from .constants import (
    MessageRole,
    MAX_MESSAGES_PER_THREAD,
    TABLE_MESSAGES,
    ERROR_MESSAGE_NOT_FOUND,
    ERROR_THREAD_NOT_FOUND,
    ERROR_PERMISSION_DENIED,
    SUCCESS_MESSAGE_SENT
)

from .models import (
    Message,
    MessageCreate,
    MessageUpdate,
    MessageListParams,
    MessageListResponse
)

from .exceptions import (
    ThreadNotFoundError,
    MessageNotFoundError,
    ThreadPermissionError,
    ThreadArchivedError,
    MaxMessagesReachedError,
    InvalidMessageContentError,
    DatabaseError
)


class MessageManager:
    """
    Message Manager - Handles message operations
    
    Methods:
        add_message() - Add message to thread
        get_message() - Get message by ID
        update_message() - Update message content
        delete_message() - Delete message
        list_messages() - List messages in thread
        get_conversation_history() - Get formatted conversation
        count_messages() - Count messages in thread
        search_messages() - Search message content
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize MessageManager
        
        Args:
            db_path: Path to sessions.db (ignored - kept for backward compatibility)
        """
        # db_path parameter ignored - using Supabase PostgreSQL via connection pool
        pass
    
    def add_message(
        self,
        message_data: MessageCreate,
        check_permissions: bool = True,
        check_duplicates: bool = True
    ) -> Message:
        """
        Add message to thread with optional duplicate detection
        
        Args:
            message_data: MessageCreate model with message details
            check_permissions: Whether to check thread permissions
            check_duplicates: Whether to check for duplicate messages (DEFAULT: True)
        
        Returns:
            Message: Created message object (or existing if duplicate detected)
        
        Raises:
            ThreadNotFoundError: If thread doesn't exist
            ThreadPermissionError: If user lacks permission
            ThreadArchivedError: If thread is archived
            MaxMessagesReachedError: If thread at message limit
            InvalidMessageContentError: If content is invalid
        """
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            try:
                # Verify thread exists and get status
                sql, params = convert_sql_placeholders("""
                    SELECT id, archived, workspace_id, user_id 
                    FROM sessions.threads 
                    WHERE id = %s
                """, (message_data.thread_id,))

                cursor.execute(sql, params)
                thread_row = cursor.fetchone()
                
                if not thread_row:
                    raise ThreadNotFoundError(thread_id=message_data.thread_id)
                
                # Check if thread is archived
                if thread_row['archived'] == 1:
                    raise ThreadArchivedError(message_data.thread_id)
                
                # Check permissions if requested
                if check_permissions:
                    # Owner can always add messages
                    if thread_row['user_id'] != message_data.user_id:
                        # TODO: Check workspace permissions and shares
                        pass
                
                # NEW: Duplicate detection (before message limit check)
                if check_duplicates:
                    normalized_content = self._normalize_content(message_data.content)
                    
                    # Check last 20 messages for duplicates
                    sql, params = convert_sql_placeholders("""
                        SELECT id, content, role, created_at 
                        FROM sessions.messages 
                        WHERE thread_id = %s 
                        ORDER BY created_at DESC 
                        LIMIT 20
                    """, (message_data.thread_id,))

                    cursor.execute(sql, params)
                    recent_messages = cursor.fetchall()
                    
                    for existing_msg in recent_messages:
                        existing_normalized = self._normalize_content(existing_msg['content'])
                        
                        # Check if content matches and role matches
                        if (existing_normalized == normalized_content and 
                            existing_msg['role'] == message_data.role.value):
                            
                            print(f"[DUPLICATE PREVENTED] Message already exists in thread {message_data.thread_id}. "
                                  f"Existing message ID: {existing_msg['id']}, "
                                  f"Created: {existing_msg['created_at']}")
                            
                            # Return existing message instead of creating duplicate
                            return self.get_message(existing_msg['id'])
                
                # Check message limit
                sql, params = convert_sql_placeholders("""
                    SELECT COUNT(*) as count 
                    FROM sessions.messages 
                    WHERE thread_id = %s
                """, (message_data.thread_id,))

                cursor.execute(sql, params)
                message_count = cursor.fetchone()['count']
                
                if message_count >= MAX_MESSAGES_PER_THREAD:
                    raise MaxMessagesReachedError(message_data.thread_id, MAX_MESSAGES_PER_THREAD)
                
                # Validate content
                if not message_data.content or not message_data.content.strip():
                    raise InvalidMessageContentError("Message content cannot be empty")
                
                # Insert message
                now = datetime.now(UTC).isoformat()
                
                # Generate embedding for message content (async background job)
                content_embedding = None
                try:
                    from tools.implementations.conversation_memory import generate_embedding
                    # Only embed substantive content (>20 chars)
                    if message_data.content and len(message_data.content.strip()) > 20:
                        content_embedding = generate_embedding(message_data.content[:8000])  # Limit to 8K chars
                except Exception as e:
                    # Non-blocking: Continue even if embedding fails
                    logger.warning(f"Failed to generate message embedding: {e}")
                
                sql, params = convert_sql_placeholders("""
                    INSERT INTO sessions.messages (
                        thread_id, workspace_id, user_id, role, content,
                        prompt, include, tool_calls, tokens_used, response_time_ms,
                        metadata, created_at, content_embedding
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    message_data.thread_id,
                    message_data.workspace_id,
                    message_data.user_id,
                    message_data.role.value,
                    message_data.content,
                    message_data.prompt,
                    message_data.include,
                    message_data.tool_calls,
                    message_data.tokens_used,
                    message_data.response_time_ms,
                    json.dumps(message_data.metadata) if message_data.metadata else None,
                    now,
                    content_embedding
                ))
                
                cursor.execute(sql, params)
                result = cursor.fetchone()
                message_id = result['id']
                
                # Update thread's updated_at
                sql, params = convert_sql_placeholders("""
                    UPDATE sessions.threads 
                    SET updated_at = %s
                    WHERE id = %s
                """, (now, message_data.thread_id))
                cursor.execute(sql, params)
                
                conn.commit()
                
                # Fetch created message
                return self.get_message(message_id)
                
            except (ThreadNotFoundError, ThreadArchivedError, MaxMessagesReachedError, InvalidMessageContentError):
                raise
            except Exception as e:
                conn.rollback()
                raise DatabaseError("add_message", str(e))
    
    def get_message(
        self,
        message_id: int,
        user_id: Optional[int] = None,
        check_permissions: bool = False
    ) -> Message:
        """
        Get message by ID
        
        Args:
            message_id: Message ID
            user_id: User ID (for permission check)
            check_permissions: Whether to verify thread access
        
        Returns:
            Message: Message object
        
        Raises:
            MessageNotFoundError: If message doesn't exist
            ThreadPermissionError: If user lacks access
        """
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM sessions.messages WHERE id = %s", (message_id,))
            row = cursor.fetchone()
            
            if not row:
                raise MessageNotFoundError(message_id)
            
            # Check permissions if requested
            if check_permissions and user_id:
                # TODO: Check thread permissions via ThreadManager
                pass
            
            # Parse metadata if exists
            metadata = None
            if row['metadata']:
                try:
                    metadata = json.loads(row['metadata'])
                except:
                    metadata = {}
            
            # response_time_ms may not exist in older DBs; handle safely
            response_time_ms = row.get('response_time_ms')

            return Message(
                id=row['id'],
                thread_id=row['thread_id'],
                workspace_id=row['workspace_id'],
                user_id=row['user_id'],
                role=MessageRole(row['role']),
                content=row['content'],
                prompt=row['prompt'],
                include=row['include'],
                tool_calls=row['tool_calls'],
                tokens_used=row['tokens_used'],
                response_time_ms=response_time_ms,
                metadata=metadata,
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
            )
    
    def update_message(
        self,
        message_id: int,
        update_data: MessageUpdate,
        user_id: int
    ) -> Message:
        """
        Update message content or metadata
        
        Args:
            message_id: Message ID to update
            update_data: MessageUpdate model with changes
            user_id: User performing update
        
        Returns:
            Message: Updated message object
        
        Raises:
            MessageNotFoundError: If message doesn't exist
            ThreadPermissionError: If user lacks permission
        """
        # Get existing message
        message = self.get_message(message_id)
        
        # Only owner can edit their messages (or thread owner/admin)
        if message.user_id != user_id:
            # TODO: Check if user is thread owner or admin
            raise ThreadPermissionError(user_id, message.thread_id, "edit")
        
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()

            try:
                updates = []
                params = []

                if update_data.content is not None:
                    updates.append("content = %s")
                    params.append(update_data.content)

                if update_data.metadata is not None:
                    updates.append("metadata = %s")
                    params.append(json.dumps(update_data.metadata))

                # Always update updated_at
                updates.append("updated_at = %s")
                params.append(datetime.now(UTC).isoformat())

                # Build and execute UPDATE statement
                if not updates:
                    # Nothing to update
                    return self.get_message(message_id)

                params.append(message_id)
                update_sql = f"UPDATE sessions.messages SET {', '.join(updates)} WHERE id = %s"
                
                sql, converted_params = convert_sql_placeholders(update_sql, tuple(params))
                cursor.execute(sql, converted_params)
                conn.commit()

                return self.get_message(message_id)
                
            except (MessageNotFoundError, ThreadPermissionError):
                raise
            except Exception as e:
                conn.rollback()
                raise DatabaseError("update_message", str(e))
    
    def delete_message(
        self,
        message_id: int,
        user_id: int
    ) -> dict:
        """
        Delete message (permanently)
        
        Args:
            message_id: Message ID to delete
            user_id: User performing deletion
        
        Returns:
            dict: Success message
        
        Raises:
            MessageNotFoundError: If message doesn't exist
            ThreadPermissionError: If user lacks permission
        """
        # Get existing message
        message = self.get_message(message_id)
        
        # Only owner can delete their messages (or thread owner/admin)
        if message.user_id != user_id:
            # TODO: Check if user is thread owner or admin
            raise ThreadPermissionError(user_id, message.thread_id, "delete")
        
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            try:
                sql, params = convert_sql_placeholders(
                    "DELETE FROM sessions.messages WHERE id = %s",
                    (message_id,)
                )
                cursor.execute(sql, params)
                conn.commit()
                
                return {"success": True, "message": "Message deleted successfully"}
                
            except Exception as e:
                conn.rollback()
                raise DatabaseError("delete_message", str(e))
    
    def list_messages(self, params: MessageListParams) -> MessageListResponse:
        """
        List messages in thread with pagination
        
        Args:
            params: MessageListParams with filters
        
        Returns:
            MessageListResponse: Paginated message list
        
        Raises:
            ThreadNotFoundError: If thread doesn't exist
        """
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            # Verify thread exists
            sql, converted_params = convert_sql_placeholders(
                "SELECT id FROM sessions.threads WHERE id = %s",
                (params.thread_id,)
            )
            cursor.execute(sql, converted_params)
            if not cursor.fetchone():
                raise ThreadNotFoundError(thread_id=params.thread_id)
            
            # Build WHERE clause
            where_clauses = ["thread_id = %s"]
            query_params = [params.thread_id]
            
            if params.role:
                where_clauses.append("role = %s")
                query_params.append(params.role.value)
            
            where_sql = " AND ".join(where_clauses)
            
            # Get total count
            count_sql = f"SELECT COUNT(*) FROM sessions.messages WHERE {where_sql}"
            sql, converted_params = convert_sql_placeholders(count_sql, tuple(query_params))
            cursor.execute(sql, converted_params)
            total = cursor.fetchone()[0]
            
            # Get paginated results (ordered by ID/created_at)
            offset = (params.page - 1) * params.page_size
            
            list_sql = f"""
                SELECT * FROM sessions.messages 
                WHERE {where_sql}
                ORDER BY id ASC
                LIMIT %s OFFSET %s
            """
            sql, converted_params = convert_sql_placeholders(
                list_sql,
                tuple(query_params + [params.page_size, offset])
            )
            cursor.execute(sql, converted_params)
            
            rows = cursor.fetchall()
            
            # Convert to Message objects
            messages = []
            for row in rows:
                message = self.get_message(row['id'])
                messages.append(message)
            
            has_more = (params.page * params.page_size) < total
            
            return MessageListResponse(
                messages=messages,
                total=total,
                page=params.page,
                page_size=params.page_size,
                has_more=has_more
            )
    
    def get_conversation_history(
        self,
        thread_id: int,
        limit: Optional[int] = None,
        format_for_api: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for AI API
        
        Args:
            thread_id: Thread ID
            limit: Maximum number of messages (None = all)
            format_for_api: Format for Anthropic API (role + content only)
        
        Returns:
            List[Dict]: Conversation history
        
        Raises:
            ThreadNotFoundError: If thread doesn't exist
        """
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            # Verify thread exists
            sql, params = convert_sql_placeholders(
                "SELECT id FROM sessions.threads WHERE id = %s",
                (thread_id,)
            )
            cursor.execute(sql, params)
            if not cursor.fetchone():
                raise ThreadNotFoundError(thread_id=thread_id)
            
            # Get messages
            query = "SELECT * FROM sessions.messages WHERE thread_id = %s ORDER BY id ASC"
            query_params = [thread_id]
            
            if limit:
                query += " LIMIT %s"
                query_params.append(limit)
            
            sql, params = convert_sql_placeholders(query, tuple(query_params))
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # Format messages
            conversation = []
            for row in rows:
                if format_for_api:
                    # Anthropic API format (role + content only)
                    conversation.append({
                        "role": row['role'],
                        "content": row['content']
                    })
                else:
                    # Full message data
                    message = self.get_message(row['id'])
                    conversation.append(message.dict())
            
            return conversation
    
    def count_messages(self, thread_id: int, role: Optional[MessageRole] = None) -> int:
        """
        Count messages in thread
        
        Args:
            thread_id: Thread ID
            role: Optional filter by role
        
        Returns:
            int: Message count
        """
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            if role:
                sql, params = convert_sql_placeholders("""
                    SELECT COUNT(*) FROM sessions.messages 
                    WHERE thread_id = %s AND role = %s
                """, (thread_id, role.value))
            else:
                sql, params = convert_sql_placeholders("""
                    SELECT COUNT(*) FROM sessions.messages 
                    WHERE thread_id = %s
                """, (thread_id,))

            cursor.execute(sql, params)
            count = cursor.fetchone()[0]
            
            return count
    
    def search_messages(
        self,
        thread_id: int,
        search_term: str,
        limit: int = 50
    ) -> List[Message]:
        """
        Search message content in thread
        
        Args:
            thread_id: Thread ID to search
            search_term: Text to search for
            limit: Maximum results
        
        Returns:
            List[Message]: Matching messages
        """
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            search_pattern = f"%{search_term}%"
            
            sql, params = convert_sql_placeholders("""
                SELECT * FROM sessions.messages 
                WHERE thread_id = %s AND content LIKE %s
                ORDER BY id DESC
                LIMIT %s
            """, (thread_id, search_pattern, limit))
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                message = self.get_message(row['id'])
                messages.append(message)
            
            return messages
    
    def get_last_message(self, thread_id: int) -> Optional[Message]:
        """
        Get most recent message in thread
        
        Args:
            thread_id: Thread ID
        
        Returns:
            Message or None: Last message if exists
        """
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            sql, params = convert_sql_placeholders("""
                SELECT * FROM sessions.messages 
                WHERE thread_id = %s
                ORDER BY id DESC
                LIMIT 1
            """, (thread_id,))
            
            cursor.execute(sql, params)
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self.get_message(row['id'])
    
    def _normalize_content(self, content: Any) -> str:
        """
        Normalize message content for duplicate detection
        
        Handles different content formats:
        - String: normalize whitespace
        - List/Array: extract text from all items
        - Dict: convert to JSON string
        
        Args:
            content: Message content (string, list, or dict)
        
        Returns:
            str: Normalized content string
        """
        if isinstance(content, str):
            # String format - normalize whitespace
            return ' '.join(content.split())
        
        elif isinstance(content, list):
            # Array format - extract text from all items
            text_parts = []
            for item in content:
                if isinstance(item, dict):
                    # Check for 'text' field in dict
                    if 'text' in item:
                        text_parts.append(item['text'])
                    elif 'type' in item and item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                elif isinstance(item, str):
                    text_parts.append(item)
            
            combined = ' '.join(text_parts)
            return ' '.join(combined.split())
        
        elif isinstance(content, dict):
            # Dict format - convert to JSON string
            return json.dumps(content, sort_keys=True)
        
        else:
            # Unknown format - convert to string
            return str(content)