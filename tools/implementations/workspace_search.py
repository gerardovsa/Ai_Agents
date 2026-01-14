"""
Workspace Search and Message Retrieval Tools

Provides 4 comprehensive tools for searching and retrieving workspace data:
1. workspace_simple_search - Fast full-text search across messages and transcriptions
2. workspace_semantic_search - AI-powered semantic search using embeddings
3. workspace_get_messages - Retrieve messages by various filters
4. workspace_get_transcriptions - Retrieve transcriptions by various filters

Author: AI Agent
Date: December 2025
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

# Import OpenAI for embeddings (semantic search)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI not available - semantic search will be disabled")


def get_database_connection(schema_name: str = "workspace_chats"):
    """
    Get Supabase PostgreSQL database connection
    
    Args:
        schema_name: PostgreSQL schema to use (default: workspace_chats)
        
    Returns:
        psycopg2 connection object
        
    Raises:
        Exception if connection fails
    """
    try:
        conn = psycopg2.connect(
            host=os.environ.get("SUPABASE_HOST"),
            database=os.environ.get("SUPABASE_DATABASE", "postgres"),
            user=os.environ.get("SUPABASE_USER"),
            password=os.environ.get("SUPABASE_PASSWORD"),
            port=os.environ.get("SUPABASE_PORT", "5432"),
            options=f"-c search_path={schema_name}"
        )
        return conn
    except Exception as e:
        raise Exception(f"Database connection failed: {str(e)}")


def generate_embedding(text: str) -> List[float]:
    """
    Generate OpenAI embedding for text (1536 dimensions)
    
    Args:
        text: Text to embed
        
    Returns:
        List of 1536 floats representing the embedding vector
        
    Raises:
        Exception if OpenAI API fails
    """
    if not OPENAI_AVAILABLE:
        raise Exception("OpenAI library not installed - cannot generate embeddings")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY environment variable not set")
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        raise Exception(f"Embedding generation failed: {str(e)}")


def workspace_simple_search(
    search_query: str,
    workspace_ids: Optional[List[int]] = None,
    user_id: Optional[int] = None,
    search_messages: bool = True,
    search_transcriptions: bool = True,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Fast full-text search across workspace messages and transcriptions
    
    Uses PostgreSQL ILIKE for simple keyword matching. Fast and reliable,
    but doesn't understand semantic meaning.
    
    Args:
        search_query: Text to search for (supports % wildcards)
        workspace_ids: List of workspace IDs to search (None = all workspaces)
        user_id: Filter by specific user ID (None = all users)
        search_messages: Include messages in search (default: True)
        search_transcriptions: Include transcriptions in search (default: True)
        limit: Maximum results to return (default: 50, max: 200)
        
    Returns:
        {
            'success': True,
            'results': {
                'messages': [...],
                'transcriptions': [...]
            },
            'total_count': 45,
            'query': 'database performance',
            'search_type': 'simple'
        }
        
    Example:
        workspace_simple_search(
            search_query="database performance",
            workspace_ids=[1, 2, 3],
            limit=20
        )
    """
    try:
        # Validate inputs
        if not search_query or not search_query.strip():
            return {
                'success': False,
                'error': 'search_query is required and cannot be empty'
            }
        
        limit = min(max(1, limit), 200)  # Clamp between 1-200
        results = {'messages': [], 'transcriptions': []}
        total_count = 0
        
        conn = get_database_connection("workspace_chats")
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Search messages
        if search_messages:
            query = """
                SELECT 
                    m.id,
                    m.workspace_id,
                    m.thread_id,
                    m.session_id,
                    m.role,
                    m.content,
                    m.user_id,
                    m.created_at,
                    w.name as workspace_name,
                    u.username as user_name
                FROM messages m
                LEFT JOIN workspaces w ON m.workspace_id = w.id
                LEFT JOIN users u ON m.user_id = u.id
                WHERE m.content ILIKE %s
            """
            params = [f"%{search_query}%"]
            
            if workspace_ids:
                query += " AND m.workspace_id = ANY(%s)"
                params.append(workspace_ids)
            
            if user_id:
                query += " AND m.user_id = %s"
                params.append(user_id)
            
            query += " ORDER BY m.created_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            messages = cursor.fetchall()
            results['messages'] = [dict(row) for row in messages]
            total_count += len(results['messages'])
        
        # Search transcriptions
        if search_transcriptions and total_count < limit:
            remaining = limit - total_count
            query = """
                SELECT 
                    t.transcription_id,
                    t.text,
                    t.whisper_text,
                    t.transcription_mode,
                    t.duration,
                    t.user_id,
                    t.workspace_id,
                    t.session_id,
                    t.created_at,
                    w.name as workspace_name,
                    u.username as user_name
                FROM transcriptions t
                LEFT JOIN workspaces w ON t.workspace_id = w.id
                LEFT JOIN users u ON t.user_id = u.id
                WHERE t.deleted_at IS NULL
                AND (t.text ILIKE %s OR t.whisper_text ILIKE %s)
            """
            params = [f"%{search_query}%", f"%{search_query}%"]
            
            if workspace_ids:
                query += " AND t.workspace_id = ANY(%s)"
                params.append(workspace_ids)
            
            if user_id:
                query += " AND t.user_id = %s"
                params.append(user_id)
            
            query += " ORDER BY t.created_at DESC LIMIT %s"
            params.append(remaining)
            
            cursor.execute(query, params)
            transcriptions = cursor.fetchall()
            results['transcriptions'] = [dict(row) for row in transcriptions]
            total_count += len(results['transcriptions'])
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'results': results,
            'total_count': total_count,
            'query': search_query,
            'search_type': 'simple',
            'workspaces_searched': workspace_ids or 'all',
            'user_filter': user_id or 'all'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Simple search failed: {str(e)}",
            'query': search_query
        }


def workspace_semantic_search(
    search_query: str,
    workspace_ids: Optional[List[int]] = None,
    user_id: Optional[int] = None,
    similarity_threshold: float = 0.7,
    limit: int = 20
) -> Dict[str, Any]:
    """
    AI-powered semantic search using vector embeddings
    
    Understands meaning and context, not just exact keywords. 
    Searches for "database performance" will find results about 
    "SQL optimization" and "query speed" even without exact matches.
    
    REQUIREMENTS:
    - pgvector extension enabled on PostgreSQL
    - embedding_vector column populated with embeddings
    - OPENAI_API_KEY environment variable set
    
    Args:
        search_query: Text describing what you're looking for
        workspace_ids: List of workspace IDs to search (None = all workspaces)
        user_id: Filter by specific user ID (None = all users)
        similarity_threshold: Minimum similarity score 0.0-1.0 (default: 0.7)
        limit: Maximum results to return (default: 20, max: 100)
        
    Returns:
        {
            'success': True,
            'results': [
                {
                    'id': 12345,
                    'content': 'Message text...',
                    'similarity_score': 0.89,
                    'workspace_name': 'Engineering',
                    'user_name': 'sarah',
                    'created_at': '2025-12-01T10:30:00'
                }
            ],
            'total_count': 15,
            'query': 'database performance issues',
            'search_type': 'semantic',
            'similarity_threshold': 0.7
        }
        
    Example:
        workspace_semantic_search(
            search_query="Tell me about pricing strategy discussions",
            workspace_ids=[1, 2],
            similarity_threshold=0.75,
            limit=10
        )
    """
    try:
        # Validate inputs
        if not search_query or not search_query.strip():
            return {
                'success': False,
                'error': 'search_query is required and cannot be empty'
            }
        
        if not OPENAI_AVAILABLE:
            return {
                'success': False,
                'error': 'OpenAI library not installed - use workspace_simple_search instead',
                'fallback': 'workspace_simple_search'
            }
        
        limit = min(max(1, limit), 100)  # Clamp between 1-100
        similarity_threshold = max(0.0, min(1.0, similarity_threshold))  # Clamp 0-1
        
        # Generate embedding for search query
        query_embedding = generate_embedding(search_query)
        
        conn = get_database_connection("workspace_chats")
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Semantic search query using pgvector
        query = """
            SELECT 
                m.id,
                m.workspace_id,
                m.thread_id,
                m.session_id,
                m.role,
                m.content,
                m.user_id,
                m.created_at,
                w.name as workspace_name,
                u.username as user_name,
                1 - (m.embedding_vector <=> %s::vector) as similarity_score
            FROM messages m
            LEFT JOIN workspaces w ON m.workspace_id = w.id
            LEFT JOIN users u ON m.user_id = u.id
            WHERE m.embedding_vector IS NOT NULL
            AND 1 - (m.embedding_vector <=> %s::vector) >= %s
        """
        params = [query_embedding, query_embedding, similarity_threshold]
        
        if workspace_ids:
            query += " AND m.workspace_id = ANY(%s)"
            params.append(workspace_ids)
        
        if user_id:
            query += " AND m.user_id = %s"
            params.append(user_id)
        
        query += " ORDER BY similarity_score DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        results_list = [dict(row) for row in results]
        
        return {
            'success': True,
            'results': results_list,
            'total_count': len(results_list),
            'query': search_query,
            'search_type': 'semantic',
            'similarity_threshold': similarity_threshold,
            'workspaces_searched': workspace_ids or 'all',
            'user_filter': user_id or 'all',
            'note': 'Results ranked by semantic similarity, not chronological order'
        }
        
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful error messages
        if "vector" in error_msg.lower():
            return {
                'success': False,
                'error': 'pgvector extension not enabled or embedding_vector column not configured',
                'suggestion': 'Run migration script to enable pgvector and populate embeddings',
                'fallback': 'Use workspace_simple_search for keyword-based search'
            }
        
        return {
            'success': False,
            'error': f"Semantic search failed: {error_msg}",
            'query': search_query,
            'fallback': 'Use workspace_simple_search for keyword-based search'
        }


def workspace_get_messages(
    workspace_ids: Optional[List[int]] = None,
    thread_id: Optional[int] = None,
    session_id: Optional[int] = None,
    user_id: Optional[int] = None,
    role: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Retrieve workspace messages with flexible filtering
    
    Use this tool to get messages by thread, session, user, date range,
    or any combination of filters. Useful for context retrieval and
    conversation history.
    
    Args:
        workspace_ids: List of workspace IDs (None = all workspaces)
        thread_id: Specific thread ID
        session_id: Specific session ID
        user_id: Filter by user ID
        role: Filter by role ('user', 'assistant', 'system')
        date_from: Start date YYYY-MM-DD (inclusive)
        date_to: End date YYYY-MM-DD (inclusive)
        limit: Maximum results (default: 100, max: 500)
        offset: Skip N results for pagination (default: 0)
        
    Returns:
        {
            'success': True,
            'messages': [
                {
                    'id': 12345,
                    'workspace_id': 1,
                    'thread_id': 42,
                    'session_id': 789,
                    'role': 'user',
                    'content': 'Message text...',
                    'user_id': 5,
                    'created_at': '2025-12-01T10:30:00',
                    'workspace_name': 'Engineering',
                    'user_name': 'sarah'
                }
            ],
            'total_count': 87,
            'limit': 100,
            'offset': 0,
            'filters_applied': {...}
        }
        
    Examples:
        # Get recent messages from specific workspace
        workspace_get_messages(workspace_ids=[1], limit=50)
        
        # Get entire thread conversation
        workspace_get_messages(thread_id=42)
        
        # Get messages from user in date range
        workspace_get_messages(
            user_id=5,
            date_from="2025-12-01",
            date_to="2025-12-07"
        )
        
        # Get all assistant responses in workspace
        workspace_get_messages(workspace_ids=[1], role="assistant")
    """
    try:
        limit = min(max(1, limit), 500)  # Clamp between 1-500
        offset = max(0, offset)
        
        conn = get_database_connection("workspace_chats")
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build dynamic query
        query = """
            SELECT 
                m.id,
                m.workspace_id,
                m.thread_id,
                m.session_id,
                m.role,
                m.content,
                m.user_id,
                m.created_at,
                m.metadata,
                w.name as workspace_name,
                u.username as user_name
            FROM messages m
            LEFT JOIN workspaces w ON m.workspace_id = w.id
            LEFT JOIN users u ON m.user_id = u.id
            WHERE 1=1
        """
        params = []
        filters_applied = {}
        
        if workspace_ids:
            query += " AND m.workspace_id = ANY(%s)"
            params.append(workspace_ids)
            filters_applied['workspace_ids'] = workspace_ids
        
        if thread_id:
            query += " AND m.thread_id = %s"
            params.append(thread_id)
            filters_applied['thread_id'] = thread_id
        
        if session_id:
            query += " AND m.session_id = %s"
            params.append(session_id)
            filters_applied['session_id'] = session_id
        
        if user_id:
            query += " AND m.user_id = %s"
            params.append(user_id)
            filters_applied['user_id'] = user_id
        
        if role:
            query += " AND m.role = %s"
            params.append(role)
            filters_applied['role'] = role
        
        if date_from:
            query += " AND m.created_at >= %s"
            params.append(date_from)
            filters_applied['date_from'] = date_from
        
        if date_to:
            query += " AND m.created_at <= %s"
            params.append(date_to + " 23:59:59")
            filters_applied['date_to'] = date_to
        
        # Get total count
        count_query = query.replace(
            "SELECT m.id, m.workspace_id, m.thread_id, m.session_id, m.role, m.content, m.user_id, m.created_at, m.metadata, w.name as workspace_name, u.username as user_name",
            "SELECT COUNT(*)"
        )
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()['count']
        
        # Get paginated results
        query += " ORDER BY m.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        messages = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'messages': [dict(row) for row in messages],
            'total_count': total_count,
            'returned_count': len(messages),
            'limit': limit,
            'offset': offset,
            'filters_applied': filters_applied,
            'has_more': offset + len(messages) < total_count
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Message retrieval failed: {str(e)}",
            'filters_applied': locals()
        }


def workspace_get_transcriptions(
    workspace_ids: Optional[List[int]] = None,
    session_id: Optional[int] = None,
    user_id: Optional[int] = None,
    transcription_mode: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Retrieve transcriptions with flexible filtering
    
    Use this tool to get transcriptions by workspace, session, user,
    date range, duration, or transcription mode. Excludes deleted transcriptions.
    
    Args:
        workspace_ids: List of workspace IDs (None = all workspaces)
        session_id: Specific session ID
        user_id: Filter by user ID
        transcription_mode: Filter by mode ('web_speech', 'whisper', 'hybrid')
        date_from: Start date YYYY-MM-DD (inclusive)
        date_to: End date YYYY-MM-DD (inclusive)
        min_duration: Minimum duration in seconds
        max_duration: Maximum duration in seconds
        limit: Maximum results (default: 50, max: 200)
        offset: Skip N results for pagination (default: 0)
        
    Returns:
        {
            'success': True,
            'transcriptions': [
                {
                    'transcription_id': 12345,
                    'text': 'Web Speech transcription...',
                    'whisper_text': 'Whisper AI transcription...',
                    'transcription_mode': 'hybrid',
                    'duration': 45,
                    'user_id': 5,
                    'workspace_id': 1,
                    'session_id': 789,
                    'created_at': '2025-12-01T10:30:00',
                    'workspace_name': 'Engineering',
                    'user_name': 'sarah'
                }
            ],
            'total_count': 23,
            'limit': 50,
            'offset': 0,
            'filters_applied': {...}
        }
        
    Examples:
        # Get recent transcriptions from workspace
        workspace_get_transcriptions(workspace_ids=[1], limit=20)
        
        # Get all transcriptions from session
        workspace_get_transcriptions(session_id=789)
        
        # Get long transcriptions (over 2 minutes)
        workspace_get_transcriptions(min_duration=120)
        
        # Get Whisper AI transcriptions from date range
        workspace_get_transcriptions(
            transcription_mode="whisper",
            date_from="2025-12-01",
            date_to="2025-12-07"
        )
    """
    try:
        limit = min(max(1, limit), 200)  # Clamp between 1-200
        offset = max(0, offset)
        
        conn = get_database_connection("valorai_chrome_extension")
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build dynamic query
        query = """
            SELECT 
                t.transcription_id,
                t.text,
                t.whisper_text,
                t.transcription_mode,
                t.duration,
                t.user_id,
                t.workspace_id,
                t.session_id,
                t.created_at,
                w.name as workspace_name,
                u.username as user_name
            FROM transcriptions t
            LEFT JOIN workspace_chats.workspaces w ON t.workspace_id = w.id
            LEFT JOIN workspace_chats.users u ON t.user_id = u.id
            WHERE t.deleted_at IS NULL
        """
        params = []
        filters_applied = {}
        
        if workspace_ids:
            query += " AND t.workspace_id = ANY(%s)"
            params.append(workspace_ids)
            filters_applied['workspace_ids'] = workspace_ids
        
        if session_id:
            query += " AND t.session_id = %s"
            params.append(session_id)
            filters_applied['session_id'] = session_id
        
        if user_id:
            query += " AND t.user_id = %s"
            params.append(user_id)
            filters_applied['user_id'] = user_id
        
        if transcription_mode:
            query += " AND t.transcription_mode = %s"
            params.append(transcription_mode)
            filters_applied['transcription_mode'] = transcription_mode
        
        if date_from:
            query += " AND t.created_at >= %s"
            params.append(date_from)
            filters_applied['date_from'] = date_from
        
        if date_to:
            query += " AND t.created_at <= %s"
            params.append(date_to + " 23:59:59")
            filters_applied['date_to'] = date_to
        
        if min_duration:
            query += " AND t.duration >= %s"
            params.append(min_duration)
            filters_applied['min_duration'] = min_duration
        
        if max_duration:
            query += " AND t.duration <= %s"
            params.append(max_duration)
            filters_applied['max_duration'] = max_duration
        
        # Get total count
        count_query = query.replace(
            "SELECT t.transcription_id, t.text, t.whisper_text, t.transcription_mode, t.duration, t.user_id, t.workspace_id, t.session_id, t.created_at, w.name as workspace_name, u.username as user_name",
            "SELECT COUNT(*)"
        )
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()['count']
        
        # Get paginated results
        query += " ORDER BY t.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        transcriptions = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'transcriptions': [dict(row) for row in transcriptions],
            'total_count': total_count,
            'returned_count': len(transcriptions),
            'limit': limit,
            'offset': offset,
            'filters_applied': filters_applied,
            'has_more': offset + len(transcriptions) < total_count
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Transcription retrieval failed: {str(e)}",
            'filters_applied': locals()
        }


# Export all functions
__all__ = [
    'workspace_simple_search',
    'workspace_semantic_search',
    'workspace_get_messages',
    'workspace_get_transcriptions'
]
