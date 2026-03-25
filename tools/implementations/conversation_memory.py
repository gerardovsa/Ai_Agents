"""
Conversation Memory Tools - Vector Search Implementation
=========================================================

Enables AI to search vectorized conversation history, Synergy projects, and documents
using semantic search with pgvector. Provides context retrieval for full message history.

Tools:
- session_conversation_search: Search conversation threads and messages by meaning
- session_conversation_get_thread_messages: Get all messages from a thread
- session_conversation_get_message_context: Get message with surrounding context
- synergy_project_search: Search Synergy projects by meaning
- synergy_docs_search: Search Synergy documents by content
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import openai

# Configure logging
logger = logging.getLogger(__name__)

# OpenAI configuration
openai.api_key = os.getenv('OPENAI_API_KEY')
EMBEDDING_MODEL = "text-embedding-3-small"

# Database connection
def get_db_connection():
    """Get database connection with RealDict cursor"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        cursor_factory=RealDictCursor
    )


def generate_embedding(text: str, user_id: int = None) -> List[float]:
    """
    Generate embedding for text using OpenAI.

    Resolves the API key from the org vault for the given user (if provided)
    and falls back to the OPENAI_API_KEY environment variable.

    Args:
        text: Input text to embed.
        user_id: Optional user ID to resolve per-org vault key (GAP-H3 fix).

    Returns:
        List of embedding floats.
    """
    # GAP-H3 FIX: Resolve key from org vault when user_id is available
    api_key = os.getenv('OPENAI_API_KEY')
    if user_id:
        try:
            from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
            vault_key = resolve_api_key(user_id, 'openai')
            if vault_key:
                api_key = vault_key
        except Exception:
            pass  # Fall through to env-var key

    if not api_key:
        raise ValueError("No OpenAI API key available (set OPENAI_API_KEY or add 'openai' to org vault)")

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


def session_conversation_search(
    query: str,
    user_id: int = None,
    time_filter: str = "all_time",
    search_type: str = "both",
    limit: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """
    Search conversation history using HYBRID search (full-text + semantic vectors)
    
    Uses Supabase functions:
    - Full-text search (search_vector) - Always works, keyword-based
    - Semantic search (embeddings) - Only if embeddings populated
    
    Args:
        query: Natural language search query
        user_id: User ID (for authorization)
        time_filter: Time range filter (last_7_days, last_30_days, last_90_days, last_year, all_time)
        search_type: What to search (threads, messages, both)
        limit: Maximum results to return (default 5, max 20)
        
    Returns:
        Dict with success status, matching threads/messages with similarity scores
    """
    try:
        # Handle credential injection - registry passes _user_id
        if user_id is None and '_user_id' in kwargs:
            user_id = kwargs['_user_id']
        
        if user_id is None:
            return {"success": False, "error": "user_id is required"}
        
        # Cap limit
        limit = min(limit, 20)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        results = {
            "success": True,
            "threads": [],
            "messages": [],
            "total_results": 0,
            "search_method": "hybrid"  # Can be 'full_text_only', 'semantic_only', or 'hybrid'
        }
        
        # Try semantic search first (if embeddings exist)
        has_embeddings = False
        try:
            query_embedding = generate_embedding(query)
            has_embeddings = True
        except Exception as e:
            logger.warning(f"Could not generate embedding: {e}. Falling back to full-text search.")
            results["search_method"] = "full_text_only"
        
        # Search threads
        if search_type in ["threads", "both"]:
            if has_embeddings:
                # Try semantic search first
                try:
                    cur.execute("""
                        SELECT * FROM sessions.search_similar_threads(
                            %s::vector, %s, %s, %s
                        )
                    """, (query_embedding, user_id, 0.7, limit))
                    
                    thread_rows = cur.fetchall()
                    
                    # If no semantic results, fall back to full-text
                    if not thread_rows:
                        raise Exception("No semantic results, trying full-text")
                        
                except Exception as e:
                    logger.info(f"Semantic search failed or returned no results: {e}. Using full-text search.")
                    # Fall back to full-text search using Supabase RPC
                    cur.execute("""
                        SELECT * FROM sessions.search_threads(
                            %s, %s, %s
                        )
                    """, (query, user_id, limit))
                    thread_rows = cur.fetchall()
                    results["search_method"] = "full_text_only"
            else:
                # Use full-text search only
                cur.execute("""
                    SELECT * FROM sessions.search_threads(
                        %s, %s, %s
                    )
                """, (query, user_id, limit))
                thread_rows = cur.fetchall()
            
            for row in thread_rows:
                # Get message count for thread
                thread_id = row.get('id', row.get('thread_id'))
                cur.execute("""
                    SELECT COUNT(*) as count FROM sessions.messages WHERE thread_id = %s
                """, (thread_id,))
                count_result = cur.fetchone()
                message_count = count_result['count'] if count_result else 0
                
                # Get title (different column names for semantic vs full-text)
                title = row.get('name') or row.get('thread_slug') or "Unknown"
                
                # Get score (similarity for semantic, rank for full-text)
                score = row.get('similarity', row.get('rank', 0))
                
                results["threads"].append({
                    "thread_id": thread_id,
                    "title": title,
                    "similarity_score": round(float(score), 3) if score else 0,
                    "message_count": message_count,
                    "tools_used": []  # Can add later if needed
                })
        
        # Search messages
        if search_type in ["messages", "both"]:
            if has_embeddings:
                # Try semantic search first
                try:
                    cur.execute("""
                        SELECT * FROM sessions.search_similar_messages(
                            %s::vector, %s, %s, %s
                        )
                    """, (query_embedding, user_id, 0.7, limit))
                    
                    message_rows = cur.fetchall()
                    
                    # If no semantic results, fall back to full-text
                    if not message_rows:
                        raise Exception("No semantic results, trying full-text")
                        
                except Exception as e:
                    logger.info(f"Semantic message search failed: {e}. Using full-text search.")
                    # Fall back to full-text search
                    cur.execute("""
                        SELECT * FROM sessions.search_messages(
                            %s, %s, %s
                        )
                    """, (query, user_id, limit))
                    message_rows = cur.fetchall()
                    results["search_method"] = "full_text_only"
            else:
                # Use full-text search only
                cur.execute("""
                    SELECT * FROM sessions.search_messages(
                        %s, %s, %s
                    )
                """, (query, user_id, limit))
                message_rows = cur.fetchall()
            
            for row in message_rows:
                # Get thread title
                thread_id = row.get('thread_id')
                cur.execute("""
                    SELECT t.name, t.thread_slug 
                    FROM sessions.threads t 
                    WHERE t.id = %s
                """, (thread_id,))
                thread_info = cur.fetchone()
                thread_title = thread_info['name'] or thread_info['thread_slug'] if thread_info else "Unknown"
                
                # Extract text preview from content (first 200 chars)
                content = row.get('content') or row.get('content_preview', '')
                content_preview = content[:200] if content else ""
                
                # Get score (similarity for semantic, rank for full-text)
                score = row.get('similarity', row.get('rank', 0))
                
                results["messages"].append({
                    "message_id": row['message_id'],
                    "thread_id": thread_id,
                    "thread_title": thread_title,
                    "content_preview": content_preview + "..." if len(content_preview) == 200 else content_preview,
                    "similarity_score": round(float(score), 3) if score else 0,
                    "role": row.get('role', 'unknown'),
                    "timestamp": row['created_at'].isoformat() if row.get('created_at') else None
                })
        
        results["total_results"] = len(results["threads"]) + len(results["messages"])
        
        cur.close()
        conn.close()
        
        logger.info(f"Conversation search: query='{query}', user={user_id}, results={results['total_results']}")
        return results
        
    except Exception as e:
        logger.error(f"Error in session_conversation_search: {e}")
        return {
            "success": False,
            "error": str(e),
            "threads": [],
            "messages": [],
            "total_results": 0
        }


def session_conversation_get_thread_messages(
    thread_id: int,
    user_id: int,
    limit: Optional[int] = None,
    recent_only: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Get all messages from a conversation thread
    
    Args:
        thread_id: Thread ID to retrieve
        user_id: User ID (for authorization)
        limit: Optional limit on messages
        recent_only: If True, return only last 10 messages
        
    Returns:
        Dict with thread info and all messages in chronological order
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verify thread ownership
        cur.execute(
            "SELECT thread_id, slug, created_at FROM sessions.threads WHERE thread_id = %s AND user_id = %s",
            (thread_id, user_id)
        )
        thread = cur.fetchone()
        
        if not thread:
            return {
                "success": False,
                "error": "Thread not found or access denied"
            }
        
        # Count total messages
        cur.execute(
            "SELECT COUNT(*) as count FROM sessions.messages WHERE thread_id = %s",
            (thread_id,)
        )
        message_count = cur.fetchone()['count']
        
        # Build query with optional limit
        order_clause = "ORDER BY created_at ASC"
        limit_clause = ""
        
        if recent_only:
            limit_clause = "LIMIT 10"
            order_clause = "ORDER BY created_at DESC"  # Get recent first, then reverse
        elif limit:
            limit_clause = f"LIMIT {min(limit, 500)}"  # Cap at 500
        
        # Get messages
        message_query = f"""
            SELECT 
                message_id,
                role,
                content,
                tool_name,
                tool_input,
                created_at
            FROM sessions.messages
            WHERE thread_id = %s
            {order_clause}
            {limit_clause}
        """
        
        cur.execute(message_query, (thread_id,))
        message_rows = cur.fetchall()
        
        # Reverse if we got recent_only
        if recent_only:
            message_rows = list(reversed(message_rows))
        
        messages = []
        for row in message_rows:
            # Parse content JSONB
            content = row['content']
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except:
                    pass
            
            msg = {
                "message_id": row['message_id'],
                "role": row['role'],
                "content": content,
                "timestamp": row['created_at'].isoformat() if row['created_at'] else None
            }
            
            # Add tool info if present
            if row['tool_name']:
                msg["tool_calls"] = row['tool_name']
                if row['tool_input']:
                    try:
                        msg["tool_input"] = json.loads(row['tool_input']) if isinstance(row['tool_input'], str) else row['tool_input']
                    except:
                        msg["tool_input"] = row['tool_input']
            
            messages.append(msg)
        
        result = {
            "success": True,
            "thread": {
                "thread_id": thread['thread_id'],
                "title": thread['slug'],
                "message_count": message_count,
                "created_at": thread['created_at'].isoformat() if thread['created_at'] else None
            },
            "messages": messages,
            "truncated": bool(limit or recent_only) and len(messages) < message_count
        }
        
        cur.close()
        conn.close()
        
        logger.info(f"Retrieved thread {thread_id}: {len(messages)} messages (truncated={result['truncated']})")
        return result
        
    except Exception as e:
        logger.error(f"Error in session_conversation_get_thread_messages: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def session_conversation_get_message_context(
    message_id: int,
    user_id: int,
    context_size: int = 3,
    **kwargs
) -> Dict[str, Any]:
    """
    Get a specific message with surrounding context
    
    Args:
        message_id: Message ID to retrieve
        user_id: User ID (for authorization)
        context_size: Number of messages before and after (default 3, max 10)
        
    Returns:
        Dict with target message, messages before/after, and thread info
    """
    try:
        context_size = min(context_size, 10)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get target message and verify ownership
        cur.execute("""
            SELECT 
                m.message_id,
                m.thread_id,
                m.role,
                m.content,
                m.tool_name,
                m.tool_input,
                m.created_at,
                t.slug as thread_title,
                t.user_id
            FROM sessions.messages m
            JOIN sessions.threads t ON m.thread_id = t.thread_id
            WHERE m.message_id = %s
        """, (message_id,))
        
        target = cur.fetchone()
        
        if not target:
            return {
                "success": False,
                "error": "Message not found"
            }
        
        if target['user_id'] != user_id:
            return {
                "success": False,
                "error": "Access denied"
            }
        
        # Get messages before
        cur.execute("""
            SELECT 
                message_id,
                role,
                content,
                tool_name,
                created_at
            FROM sessions.messages
            WHERE thread_id = %s 
                AND created_at < %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (target['thread_id'], target['created_at'], context_size))
        
        before_rows = list(reversed(cur.fetchall()))  # Reverse to chronological
        
        # Get messages after
        cur.execute("""
            SELECT 
                message_id,
                role,
                content,
                tool_name,
                created_at
            FROM sessions.messages
            WHERE thread_id = %s 
                AND created_at > %s
            ORDER BY created_at ASC
            LIMIT %s
        """, (target['thread_id'], target['created_at'], context_size))
        
        after_rows = cur.fetchall()
        
        # Parse all messages
        def parse_message(row):
            content = row['content']
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except:
                    pass
            
            msg = {
                "message_id": row['message_id'],
                "role": row['role'],
                "content": content,
                "timestamp": row['created_at'].isoformat() if row['created_at'] else None
            }
            
            if row.get('tool_name'):
                msg["tool_calls"] = row['tool_name']
            
            return msg
        
        # Parse target message
        target_content = target['content']
        if isinstance(target_content, str):
            try:
                target_content = json.loads(target_content)
            except:
                pass
        
        target_msg = {
            "message_id": target['message_id'],
            "role": target['role'],
            "content": target_content,
            "timestamp": target['created_at'].isoformat() if target['created_at'] else None
        }
        
        if target.get('tool_name'):
            target_msg["tool_calls"] = target['tool_name']
            if target.get('tool_input'):
                try:
                    target_msg["tool_input"] = json.loads(target['tool_input']) if isinstance(target['tool_input'], str) else target['tool_input']
                except:
                    target_msg["tool_input"] = target['tool_input']
        
        result = {
            "success": True,
            "target_message": target_msg,
            "messages_before": [parse_message(row) for row in before_rows],
            "messages_after": [parse_message(row) for row in after_rows],
            "thread_info": {
                "thread_id": target['thread_id'],
                "title": target['thread_title']
            }
        }
        
        cur.close()
        conn.close()
        
        logger.info(f"Retrieved message context: message={message_id}, before={len(result['messages_before'])}, after={len(result['messages_after'])}")
        return result
        
    except Exception as e:
        logger.error(f"Error in session_conversation_get_message_context: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def synergy_project_search(
    query: str,
    user_id: int,
    status_filter: str = "all",
    limit: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """
    Search Synergy projects by meaning using vector embeddings
    
    Args:
        query: Natural language search query
        user_id: User ID (for authorization)
        status_filter: Filter by status (active, in_progress, completed, archived, all)
        limit: Maximum results (default 5, max 20)
        
    Returns:
        Dict with success status and matching projects
    """
    try:
        # Generate query embedding
        query_embedding = generate_embedding(query)
        
        # Build status filter
        status_condition = ""
        if status_filter != "all":
            status_condition = f"AND status = '{status_filter}'"
        
        # Cap limit
        limit = min(limit, 20)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Search Synergy sessions
        search_query = f"""
            SELECT 
                session_id,
                title,
                description,
                status,
                priority,
                next_steps,
                agent_assigned,
                created_at,
                1 - (title_embedding <=> %s::vector) as similarity_score
            FROM synergy_sessions.synergy_sessions
            WHERE user_id = %s 
                AND title_embedding IS NOT NULL
                {status_condition}
            ORDER BY title_embedding <=> %s::vector
            LIMIT %s
        """
        
        cur.execute(search_query, (query_embedding, user_id, query_embedding, limit))
        rows = cur.fetchall()
        
        projects = []
        for row in rows:
            # Count documents
            cur.execute(
                "SELECT COUNT(*) as count FROM synergy_sessions.synergy_internal_docs WHERE session_id = %s",
                (row['session_id'],)
            )
            doc_count = cur.fetchone()['count']
            
            # Parse next_steps
            next_steps = row.get('next_steps')
            if isinstance(next_steps, str):
                try:
                    next_steps = json.loads(next_steps)
                except:
                    next_steps = [next_steps] if next_steps else []
            
            projects.append({
                "session_id": row['session_id'],
                "title": row['title'],
                "description": row['description'],
                "similarity_score": round(float(row['similarity_score']), 3),
                "status": row['status'],
                "priority": row['priority'],
                "documents_count": doc_count,
                "next_steps": next_steps if isinstance(next_steps, list) else [],
                "agent_assigned": row['agent_assigned'],
                "created_at": row['created_at'].isoformat() if row['created_at'] else None
            })
        
        result = {
            "success": True,
            "projects": projects,
            "total_results": len(projects)
        }
        
        cur.close()
        conn.close()
        
        logger.info(f"Synergy project search: query='{query}', user={user_id}, results={len(projects)}")
        return result
        
    except Exception as e:
        logger.error(f"Error in synergy_project_search: {e}")
        return {
            "success": False,
            "error": str(e),
            "projects": [],
            "total_results": 0
        }


def synergy_docs_search(
    query: str,
    user_id: int,
    session_id: Optional[str] = None,
    limit: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """
    Search Synergy internal documents by content
    
    Args:
        query: Natural language search query
        user_id: User ID (for authorization)
        session_id: Optional - search only within specific session
        limit: Maximum results (default 5, max 20)
        
    Returns:
        Dict with success status and matching documents
    """
    try:
        # Generate query embedding
        query_embedding = generate_embedding(query)
        
        # Build session filter
        session_condition = ""
        if session_id:
            session_condition = f"AND d.session_id = '{session_id}'"
        
        # Cap limit
        limit = min(limit, 20)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Search documents
        search_query = f"""
            SELECT 
                d.doc_id,
                d.session_id,
                d.title,
                d.content,
                d.doc_type,
                d.created_at,
                s.title as session_title,
                1 - (d.content_embedding <=> %s::vector) as similarity_score
            FROM synergy_sessions.synergy_internal_docs d
            JOIN synergy_sessions.synergy_sessions s ON d.session_id = s.session_id
            WHERE s.user_id = %s 
                AND d.content_embedding IS NOT NULL
                {session_condition}
            ORDER BY d.content_embedding <=> %s::vector
            LIMIT %s
        """
        
        cur.execute(search_query, (query_embedding, user_id, query_embedding, limit))
        rows = cur.fetchall()
        
        documents = []
        for row in rows:
            # Content preview (first 300 chars)
            content = row.get('content', '')
            content_preview = content[:300] + "..." if len(content) > 300 else content
            
            documents.append({
                "doc_id": row['doc_id'],
                "session_id": row['session_id'],
                "session_title": row['session_title'],
                "title": row['title'],
                "content_preview": content_preview,
                "similarity_score": round(float(row['similarity_score']), 3),
                "doc_type": row['doc_type'],
                "created_at": row['created_at'].isoformat() if row['created_at'] else None
            })
        
        result = {
            "success": True,
            "documents": documents,
            "total_results": len(documents)
        }
        
        cur.close()
        conn.close()
        
        logger.info(f"Synergy docs search: query='{query}', session={session_id}, results={len(documents)}")
        return result
        
    except Exception as e:
        logger.error(f"Error in synergy_docs_search: {e}")
        return {
            "success": False,
            "error": str(e),
            "documents": [],
            "total_results": 0
        }


# Tool exports for AI_infrastructure
TOOLS = {
    "session_conversation_search": session_conversation_search,
    "session_conversation_get_thread_messages": session_conversation_get_thread_messages,
    "session_conversation_get_message_context": session_conversation_get_message_context,
    "synergy_project_search": synergy_project_search,
    "synergy_docs_search": synergy_docs_search
}
