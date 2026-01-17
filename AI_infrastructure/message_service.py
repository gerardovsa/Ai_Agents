"""
FILE: AI_infrastructure/message_service.py
PURPOSE: Database service for realtime message persistence
AUTHOR: AI Agent
DATE: 2025-12-16

FEATURES:
- Save direct and broadcast messages to PostgreSQL
- Retrieve message history with pagination
- Mark messages as delivered/read
- Clean up old messages (30+ days)
- Full-text search on messages

DEPENDENCIES:
- psycopg2 for PostgreSQL connection
- config.py for database credentials
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor


class MessageService:
    """Service for managing realtime messages in database"""
    
    def __init__(self, db_connection=None):
        """
        Initialize message service
        
        Args:
            db_connection: Existing database connection (optional)
        """
        self.db_conn = db_connection
        self.own_connection = False
        
        if not self.db_conn:
            self.own_connection = True
            self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            # Use shared database connection utilities (already handles Supabase)
            from shared.supabase_client import get_supabase_config
            
            config = get_supabase_config()
            self.db_conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                database=config['database'],
                user=config['user'],
                password=config['password']
            )
            print(f"[MESSAGE SERVICE] Connected to database")
        except Exception as e:
            print(f"[MESSAGE SERVICE ERROR] Failed to connect: {e}")
            self.db_conn = None
    
    def save_message(
        self,
        sender_user_id: int,
        message_text: str,
        message_type: str = 'direct',
        recipient_user_id: Optional[int] = None,
        room: str = 'synergy_board',
        metadata: Optional[Dict] = None
    ) -> Optional[int]:
        """
        Save message to database
        
        Args:
            sender_user_id: User ID of sender
            message_text: Message content
            message_type: 'direct' or 'broadcast'
            recipient_user_id: User ID of recipient (for direct messages)
            room: Room/channel name
            metadata: Additional metadata (e.g., {'source': 'socket.io'})
        
        Returns:
            message_id if successful, None otherwise
        """
        if not self.db_conn:
            print("[MESSAGE SERVICE] No database connection")
            return None
        
        cursor = None
        try:
            cursor = self.db_conn.cursor()
            
            # Prepare metadata
            meta = metadata or {}
            meta['source'] = meta.get('source', 'socket.io')
            meta['timestamp'] = datetime.now().isoformat()
            
            # Insert message
            cursor.execute("""
                INSERT INTO realtime_messages (
                    sender_user_id,
                    recipient_user_id,
                    message_type,
                    message_text,
                    room,
                    message_metadata,
                    delivered_to,
                    read_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING message_id
            """, (
                sender_user_id,
                recipient_user_id,
                message_type,
                message_text,
                room,
                json.dumps(meta),
                [],  # delivered_to (empty array initially)
                []   # read_by (empty array initially)
            ))
            
            message_id = cursor.fetchone()[0]
            self.db_conn.commit()
            
            print(f"[MESSAGE SERVICE] Saved message {message_id}: {message_type} from user {sender_user_id}")
            return message_id
            
        except Exception as e:
            print(f"[MESSAGE SERVICE ERROR] save_message failed: {e}")
            if self.db_conn:
                self.db_conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
    
    def mark_delivered(self, message_id: int, user_id: int) -> bool:
        """
        Mark message as delivered to user
        
        Args:
            message_id: ID of message
            user_id: User ID who received message
        
        Returns:
            True if successful, False otherwise
        """
        if not self.db_conn:
            return False
        
        cursor = None
        try:
            cursor = self.db_conn.cursor()
            
            cursor.execute("""
                UPDATE realtime_messages
                SET delivered_to = array_append(delivered_to, %s)
                WHERE message_id = %s
                AND NOT (%s = ANY(delivered_to))
            """, (user_id, message_id, user_id))
            
            self.db_conn.commit()
            return True
            
        except Exception as e:
            print(f"[MESSAGE SERVICE ERROR] mark_delivered failed: {e}")
            if self.db_conn:
                self.db_conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
    
    def mark_read(self, message_id: int, user_id: int) -> bool:
        """
        Mark message as read by user
        
        Args:
            message_id: ID of message
            user_id: User ID who read message
        
        Returns:
            True if successful, False otherwise
        """
        if not self.db_conn:
            return False
        
        cursor = None
        try:
            cursor = self.db_conn.cursor()
            
            cursor.execute("""
                UPDATE realtime_messages
                SET read_by = array_append(read_by, %s)
                WHERE message_id = %s
                AND NOT (%s = ANY(read_by))
            """, (user_id, message_id, user_id))
            
            self.db_conn.commit()
            return True
            
        except Exception as e:
            print(f"[MESSAGE SERVICE ERROR] mark_read failed: {e}")
            if self.db_conn:
                self.db_conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
    
    def get_message_history(
        self,
        user_id: int,
        message_type: Optional[str] = None,
        room: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """
        Get message history for user
        
        Args:
            user_id: User ID to get messages for
            message_type: Filter by 'direct' or 'broadcast' (optional)
            room: Filter by room name (optional)
            limit: Maximum messages to return
            offset: Pagination offset
        
        Returns:
            List of message dictionaries
        """
        if not self.db_conn:
            return []
        
        cursor = None
        try:
            cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            
            # Build query with filters
            conditions = ["(sender_user_id = %s OR recipient_user_id = %s)"]
            params = [user_id, user_id]
            
            if message_type:
                conditions.append("message_type = %s")
                params.append(message_type)
            
            if room:
                conditions.append("room = %s")
                params.append(room)
            
            where_clause = " AND ".join(conditions)
            
            cursor.execute(f"""
                SELECT 
                    message_id,
                    sender_user_id,
                    recipient_user_id,
                    message_type,
                    message_text,
                    room,
                    delivered_to,
                    read_by,
                    message_metadata,
                    created_at
                FROM realtime_messages
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, params + [limit, offset])
            
            messages = cursor.fetchall()
            return [dict(msg) for msg in messages]
            
        except Exception as e:
            print(f"[MESSAGE SERVICE ERROR] get_message_history failed: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def search_messages(
        self,
        user_id: int,
        search_query: str,
        room: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Full-text search messages
        
        Args:
            user_id: User ID to search messages for
            search_query: Search terms
            room: Filter by room (optional)
            limit: Maximum results (enforced max: 100)
        
        Returns:
            List of matching messages
        """
        if not self.db_conn:
            return []
        
        # ✅ PERFORMANCE OPTIMIZATION (Dec 2025): Enforce max limit to prevent OOM
        limit = min(limit, 100)  # Max 100 results per search
        
        cursor = None
        try:
            cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            
            conditions = ["(sender_user_id = %s OR recipient_user_id = %s)"]
            params = [user_id, user_id]
            
            if room:
                conditions.append("room = %s")
                params.append(room)
            
            conditions.append("to_tsvector('english', message_text) @@ plainto_tsquery('english', %s)")
            params.append(search_query)
            
            where_clause = " AND ".join(conditions)
            
            cursor.execute(f"""
                SELECT 
                    message_id,
                    sender_user_id,
                    message_type,
                    message_text,
                    created_at,
                    ts_rank(
                        to_tsvector('english', message_text),
                        plainto_tsquery('english', %s)
                    ) AS relevance
                FROM realtime_messages
                WHERE {where_clause}
                ORDER BY relevance DESC, created_at DESC
                LIMIT %s
            """, [search_query] + params + [limit])
            
            messages = cursor.fetchall()
            return [dict(msg) for msg in messages]
            
        except Exception as e:
            print(f"[MESSAGE SERVICE ERROR] search_messages failed: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def cleanup_old_messages(self, days: int = 30) -> int:
        """
        Delete messages older than specified days
        
        Args:
            days: Delete messages older than this many days
        
        Returns:
            Number of messages deleted
        """
        if not self.db_conn:
            return 0
        
        cursor = None
        try:
            cursor = self.db_conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute("""
                DELETE FROM realtime_messages
                WHERE created_at < %s
            """, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            self.db_conn.commit()
            
            print(f"[MESSAGE SERVICE] Cleaned up {deleted_count} messages older than {days} days")
            return deleted_count
            
        except Exception as e:
            print(f"[MESSAGE SERVICE ERROR] cleanup_old_messages failed: {e}")
            if self.db_conn:
                self.db_conn.rollback()
            return 0
        finally:
            if cursor:
                cursor.close()
    
    def close(self):
        """Close database connection if owned by this service"""
        if self.own_connection and self.db_conn:
            self.db_conn.close()
            print("[MESSAGE SERVICE] Database connection closed")


# Singleton instance
_message_service_instance = None


def get_message_service(db_connection=None) -> MessageService:
    """
    Get singleton MessageService instance
    
    Args:
        db_connection: Existing database connection (optional)
    
    Returns:
        MessageService instance
    """
    global _message_service_instance
    
    if _message_service_instance is None:
        _message_service_instance = MessageService(db_connection)
    
    return _message_service_instance
