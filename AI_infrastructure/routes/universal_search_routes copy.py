"""
Universal Search Routes - Multi-Platform Search System

FILE: AI_infrastructure/routes/universal_search_routes.py
PURPOSE: Unified search across ALL user-connected platforms in one interface

SEARCH TARGETS:
1. Document Library (Google Drive, OneDrive, Dropbox, SharePoint)
2. Message Threads (ai_infrastructure.sessions.threads)
3. Messages (ai_infrastructure.sessions.messages)
4. Synergy Sessions (ai_infrastructure.synergy_sessions)
5. Supabase Tables (custom user data)
6. Gmail Messages (via API)
7. Slack Messages (via API)
8. Calendar Events (Google/Microsoft)

SEARCH TYPES:
- Full-text search (PostgreSQL GIN indexes)
- Semantic search (multi-provider embeddings)
- Hybrid search (RRF combination)
- Faceted filtering (by source, type, date, author)

ENDPOINTS:
1. POST /api/universal-search/search - Main search endpoint
2. POST /api/universal-search/facets - Get filter options
3. GET /api/universal-search/sources - List available platforms
4. POST /api/universal-search/index-messages - Index messages for search
5. POST /api/universal-search/index-synergy - Index Synergy sessions

LAST MODIFIED: 2025-11-30
"""

from flask import Blueprint, request, jsonify
from AI_infrastructure.auth.user_auth import require_auth  # ✅ FIX: Import standalone decorator
import psycopg2
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests

# Create blueprint
universal_search_bp = Blueprint('universal_search', __name__, url_prefix='/api/universal-search')

# ============================================================================
# HELPER: GET DATABASE CONNECTION
# ============================================================================

def get_db_connection():
    """Get Supabase PostgreSQL connection"""
    from shared.database_utils import get_database_connection
    return get_database_connection('ai_infrastructure')

# ============================================================================
# HELPER: GENERATE EMBEDDING (MULTI-PROVIDER)
# ============================================================================

def generate_embedding(text: str, user_id: int, provider: str = None) -> Optional[List[float]]:
    """
    Generate embedding using user's configured provider
    
    Args:
        text: Text to embed
        user_id: User ID for credential lookup
        provider: Override auto-detection
    
    Returns:
        List[float] or None if failed
    """
    try:
        # Get user's embedding provider credentials
        creds = auth_manager.get_platform_credentials(user_id, provider or 'openai')
        
        if not creds:
            # Try Voyage AI
            creds = auth_manager.get_platform_credentials(user_id, 'voyage')
            provider = 'voyage'
        
        if not creds:
            # Try Cohere
            creds = auth_manager.get_platform_credentials(user_id, 'cohere')
            provider = 'cohere'
        
        if not creds:
            return None
        
        # Generate embedding based on provider
        if provider == 'openai' or (not provider and creds.get('platform') == 'openai'):
            import openai
            client = openai.OpenAI(api_key=creds.get('api_key'))
            response = client.embeddings.create(
                input=text,
                model='text-embedding-ada-002'
            )
            return response.data[0].embedding
        
        elif provider == 'voyage' or creds.get('platform') == 'voyage':
            import voyageai
            vo = voyageai.Client(api_key=creds.get('api_key'))
            result = vo.embed([text], model='voyage-2')
            return result.embeddings[0]
        
        elif provider == 'cohere' or creds.get('platform') == 'cohere':
            import cohere
            co = cohere.Client(creds.get('api_key'))
            response = co.embed(
                texts=[text],
                model='embed-english-v3.0',
                input_type='search_query'
            )
            return response.embeddings[0]
        
        return None
    
    except Exception as e:
        print(f"[UNIVERSAL SEARCH] Embedding generation error: {e}")
        return None

# ============================================================================
# ENDPOINT 1: UNIVERSAL SEARCH
# ============================================================================

@universal_search_bp.route('/search', methods=['POST'])
@require_auth  # ✅ FIX: Use standalone decorator
def universal_search():
    """
    Search across ALL user-connected platforms
    
    Body:
        query (str): Search query
        sources (list): Filter by sources (optional)
        search_type (str): 'fulltext', 'semantic', 'hybrid'
        limit (int): Max results per source
        include_documents (bool): Search document library
        include_messages (bool): Search message threads
        include_synergy (bool): Search Synergy sessions
        include_supabase (bool): Search Supabase tables
        include_gmail (bool): Search Gmail (via API)
        include_slack (bool): Search Slack (via API)
    
    Returns:
        JSON with results grouped by source
    """
    try:
        user_id = request.user_id
        data = request.get_json()
        
        query = data.get('query', '')
        sources = data.get('sources', [])  # Empty = all sources
        search_type = data.get('search_type', 'hybrid')  # 'fulltext', 'semantic', 'hybrid'
        limit = data.get('limit', 10)
        
        # What to search (default: all enabled)
        include_documents = data.get('include_documents', True)
        include_messages = data.get('include_messages', True)
        include_synergy = data.get('include_synergy', True)
        include_supabase = data.get('include_supabase', False)
        include_gmail = data.get('include_gmail', False)
        include_slack = data.get('include_slack', False)
        
        results = {
            'query': query,
            'search_type': search_type,
            'total_results': 0,
            'sources': {}
        }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate embedding if semantic/hybrid search
        query_embedding = None
        if search_type in ['semantic', 'hybrid']:
            query_embedding = generate_embedding(query, user_id)
        
        # ========================================================================
        # 1. SEARCH DOCUMENT LIBRARY
        # ========================================================================
        if include_documents:
            try:
                if search_type == 'fulltext':
                    cursor.execute("""
                        SELECT document_id, title, source, file_type, url, created_at,
                               ts_rank(fts_tokens, websearch_to_tsquery('english', %s)) AS rank
                        FROM ai_infrastructure.document_library
                        WHERE fts_tokens @@ websearch_to_tsquery('english', %s)
                          AND owner_user_id = %s
                          AND is_deleted = false
                        ORDER BY rank DESC
                        LIMIT %s
                    """, (query, query, user_id, limit))
                
                elif search_type == 'semantic' and query_embedding:
                    cursor.execute("""
                        SELECT document_id, title, source, file_type, url, created_at,
                               1 - (embedding <=> %s::vector) AS similarity
                        FROM ai_infrastructure.document_library
                        WHERE owner_user_id = %s
                          AND embedding IS NOT NULL
                          AND is_deleted = false
                          AND (1 - (embedding <=> %s::vector)) > 0.3
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """, (query_embedding, user_id, query_embedding, query_embedding, limit))
                
                elif search_type == 'hybrid' and query_embedding:
                    # Use hybrid_search_documents_multi function
                    cursor.execute("""
                        SELECT * FROM ai_infrastructure.hybrid_search_documents_multi(
                            %s, %s::vector, %s, 0.5, 0.5, 0.3, 'pgvector'
                        ) WHERE owner_user_id = %s
                    """, (query, query_embedding, limit, user_id))
                
                docs = cursor.fetchall()
                results['sources']['documents'] = {
                    'count': len(docs),
                    'results': [
                        {
                            'id': row[0],
                            'title': row[1],
                            'source': row[2],
                            'type': row[3],
                            'url': row[4],
                            'date': row[5].isoformat() if row[5] else None,
                            'score': float(row[6]) if len(row) > 6 else None
                        }
                        for row in docs
                    ]
                }
                results['total_results'] += len(docs)
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Document search error: {e}")
                results['sources']['documents'] = {'error': str(e)}
        
        # ========================================================================
        # 2. SEARCH MESSAGE THREADS
        # ========================================================================
        if include_messages:
            try:
                if search_type == 'fulltext':
                    cursor.execute("""
                        SELECT t.thread_slug, t.title, t.created_at, t.message_count,
                               ts_rank(t.fts_tokens, websearch_to_tsquery('english', %s)) AS rank
                        FROM sessions.threads t
                        WHERE t.fts_tokens @@ websearch_to_tsquery('english', %s)
                          AND t.user_id = %s
                        ORDER BY rank DESC
                        LIMIT %s
                    """, (query, query, user_id, limit))
                
                elif search_type == 'semantic' and query_embedding:
                    cursor.execute("""
                        SELECT thread_slug, title, created_at, message_count,
                               1 - (embedding <=> %s::vector) AS similarity
                        FROM sessions.threads
                        WHERE user_id = %s
                          AND embedding IS NOT NULL
                          AND (1 - (embedding <=> %s::vector)) > 0.3
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """, (query_embedding, user_id, query_embedding, query_embedding, limit))
                
                threads = cursor.fetchall()
                results['sources']['threads'] = {
                    'count': len(threads),
                    'results': [
                        {
                            'id': row[0],
                            'title': row[1],
                            'date': row[2].isoformat() if row[2] else None,
                            'message_count': row[3],
                            'score': float(row[4]) if len(row) > 4 else None,
                            'url': f'/thread/{row[0]}'
                        }
                        for row in threads
                    ]
                }
                results['total_results'] += len(threads)
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Thread search error: {e}")
                results['sources']['threads'] = {'error': str(e)}
        
        # ========================================================================
        # 3. SEARCH MESSAGES
        # ========================================================================
        if include_messages:
            try:
                if search_type == 'fulltext':
                    cursor.execute("""
                        SELECT m.id, m.thread_id, m.content, m.role, m.created_at, t.thread_slug,
                               ts_rank(m.fts_tokens, websearch_to_tsquery('english', %s)) AS rank
                        FROM sessions.messages m
                        JOIN sessions.threads t ON m.thread_id = t.id
                        WHERE m.fts_tokens @@ websearch_to_tsquery('english', %s)
                          AND t.user_id = %s
                        ORDER BY rank DESC
                        LIMIT %s
                    """, (query, query, user_id, limit))
                
                elif search_type == 'semantic' and query_embedding:
                    cursor.execute("""
                        SELECT m.id, m.thread_id, m.content, m.role, m.created_at, t.thread_slug,
                               1 - (m.embedding <=> %s::vector) AS similarity
                        FROM sessions.messages m
                        JOIN sessions.threads t ON m.thread_id = t.id
                        WHERE t.user_id = %s
                          AND m.embedding IS NOT NULL
                          AND (1 - (m.embedding <=> %s::vector)) > 0.3
                        ORDER BY m.embedding <=> %s::vector
                        LIMIT %s
                    """, (query_embedding, user_id, query_embedding, query_embedding, limit))
                
                messages = cursor.fetchall()
                results['sources']['messages'] = {
                    'count': len(messages),
                    'results': [
                        {
                            'id': row[0],
                            'thread_id': row[1],
                            'content': row[2][:200] + '...' if len(row[2]) > 200 else row[2],
                            'role': row[3],
                            'date': row[4].isoformat() if row[4] else None,
                            'thread_slug': row[5],
                            'score': float(row[6]) if len(row) > 6 else None,
                            'url': f'/thread/{row[5]}'
                        }
                        for row in messages
                    ]
                }
                results['total_results'] += len(messages)
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Message search error: {e}")
                results['sources']['messages'] = {'error': str(e)}
        
        # ========================================================================
        # 4. SEARCH SYNERGY SESSIONS
        # ========================================================================
        if include_synergy:
            try:
                if search_type == 'fulltext':
                    cursor.execute("""
                        SELECT session_id, title, created_at, agent_count,
                               ts_rank(fts_tokens, websearch_to_tsquery('english', %s)) AS rank
                        FROM synergy_sessions.sessions
                        WHERE fts_tokens @@ websearch_to_tsquery('english', %s)
                          AND user_id = %s
                        ORDER BY rank DESC
                        LIMIT %s
                    """, (query, query, user_id, limit))
                
                elif search_type == 'semantic' and query_embedding:
                    cursor.execute("""
                        SELECT session_id, title, created_at, agent_count,
                               1 - (embedding <=> %s::vector) AS similarity
                        FROM synergy_sessions.sessions
                        WHERE user_id = %s
                          AND embedding IS NOT NULL
                          AND (1 - (embedding <=> %s::vector)) > 0.3
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """, (query_embedding, user_id, query_embedding, query_embedding, limit))
                
                synergy = cursor.fetchall()
                results['sources']['synergy'] = {
                    'count': len(synergy),
                    'results': [
                        {
                            'id': row[0],
                            'title': row[1],
                            'date': row[2].isoformat() if row[2] else None,
                            'agent_count': row[3],
                            'score': float(row[4]) if len(row) > 4 else None,
                            'url': f'/synergy/{row[0]}'
                        }
                        for row in synergy
                    ]
                }
                results['total_results'] += len(synergy)
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Synergy search error: {e}")
                results['sources']['synergy'] = {'error': str(e)}
        
        cursor.close()
        conn.close()
        
        # ========================================================================
        # 5. SEARCH GMAIL (via API)
        # ========================================================================
        if include_gmail:
            try:
                gmail_creds = auth_manager.get_platform_credentials(user_id, 'google')
                if gmail_creds:
                    # Call Gmail API
                    response = requests.get(
                        'https://gmail.googleapis.com/gmail/v1/users/me/messages',
                        params={'q': query, 'maxResults': limit},
                        headers={'Authorization': f'Bearer {gmail_creds.get("access_token")}'}
                    )
                    if response.status_code == 200:
                        gmail_messages = response.json().get('messages', [])
                        results['sources']['gmail'] = {
                            'count': len(gmail_messages),
                            'results': gmail_messages[:limit]
                        }
                        results['total_results'] += len(gmail_messages)
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Gmail search error: {e}")
                results['sources']['gmail'] = {'error': str(e)}
        
        # ========================================================================
        # 6. SEARCH SLACK (via API)
        # ========================================================================
        if include_slack:
            try:
                slack_creds = auth_manager.get_platform_credentials(user_id, 'slack')
                if slack_creds:
                    # Call Slack API
                    response = requests.get(
                        'https://slack.com/api/search.messages',
                        params={'query': query, 'count': limit},
                        headers={'Authorization': f'Bearer {slack_creds.get("access_token")}'}
                    )
                    if response.status_code == 200:
                        slack_messages = response.json().get('messages', {}).get('matches', [])
                        results['sources']['slack'] = {
                            'count': len(slack_messages),
                            'results': slack_messages[:limit]
                        }
                        results['total_results'] += len(slack_messages)
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Slack search error: {e}")
                results['sources']['slack'] = {'error': str(e)}
        
        return jsonify({
            'success': True,
            **results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# ENDPOINT 2: GET FACETS (FOR FILTER UI)
# ============================================================================

@universal_search_bp.route('/facets', methods=['GET'])
@require_auth  # ✅ FIX: Use standalone decorator
def get_search_facets():
    """
    Get aggregated facets for filter UI
    
    Returns:
        JSON with counts by source, type, date range
    """
    try:
        user_id = request.user_id
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        facets = {}
        
        # Document sources
        cursor.execute("""
            SELECT source, COUNT(*) 
            FROM ai_infrastructure.document_library
            WHERE owner_user_id = %s AND is_deleted = false
            GROUP BY source
        """, (user_id,))
        facets['document_sources'] = dict(cursor.fetchall())
        
        # Document types
        cursor.execute("""
            SELECT file_type, COUNT(*) 
            FROM ai_infrastructure.document_library
            WHERE owner_user_id = %s AND is_deleted = false
            GROUP BY file_type
        """, (user_id,))
        facets['document_types'] = dict(cursor.fetchall())
        
        # Thread count
        cursor.execute("""
            SELECT COUNT(*) FROM sessions.threads WHERE user_id = %s
        """, (user_id,))
        facets['thread_count'] = cursor.fetchone()[0]
        
        # Message count
        cursor.execute("""
            SELECT COUNT(*) FROM sessions.messages m
            JOIN sessions.threads t ON m.thread_id = t.id
            WHERE t.user_id = %s
        """, (user_id,))
        facets['message_count'] = cursor.fetchone()[0]
        
        # Synergy count
        cursor.execute("""
            SELECT COUNT(*) FROM synergy_sessions.sessions WHERE user_id = %s
        """, (user_id,))
        facets['synergy_count'] = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'facets': facets
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# ENDPOINT 3: LIST AVAILABLE SOURCES
# ============================================================================

@universal_search_bp.route('/sources', methods=['GET'])
@require_auth  # ✅ FIX: Use standalone decorator
def get_available_sources():
    """
    List all platforms user has connected
    
    Returns:
        JSON with available search sources
    """
    try:
        user_id = request.user_id
        
        # Check which platforms user has credentials for
        platforms = [
            'google_drive', 'onedrive', 'dropbox', 'sharepoint',
            'gmail', 'slack', 'confluence', 'notion'
        ]
        
        available_sources = []
        
        for platform in platforms:
            creds = auth_manager.get_platform_credentials(user_id, platform)
            if creds:
                available_sources.append({
                    'platform': platform,
                    'enabled': True,
                    'credential_status': 'active'
                })
        
        # Always available (internal)
        available_sources.extend([
            {'platform': 'threads', 'enabled': True, 'credential_status': 'internal'},
            {'platform': 'messages', 'enabled': True, 'credential_status': 'internal'},
            {'platform': 'synergy', 'enabled': True, 'credential_status': 'internal'},
            {'platform': 'documents', 'enabled': True, 'credential_status': 'internal'}
        ])
        
        return jsonify({
            'success': True,
            'sources': available_sources
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# ENDPOINT 4: INDEX MESSAGES FOR SEARCH
# ============================================================================

@universal_search_bp.route('/index-messages', methods=['POST'])
@require_auth  # ✅ FIX: Use standalone decorator
def index_messages_for_search():
    """
    Generate embeddings and FTS tokens for existing messages
    
    Body:
        thread_id (int): Optional - Index specific thread only
        force_reindex (bool): Re-index even if already indexed
    
    Returns:
        JSON with indexing results
    """
    try:
        user_id = request.user_id
        data = request.get_json()
        
        thread_id = data.get('thread_id')
        force_reindex = data.get('force_reindex', False)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get messages to index
        if thread_id:
            cursor.execute("""
                SELECT m.id, m.content
                FROM sessions.messages m
                JOIN sessions.threads t ON m.thread_id = t.id
                WHERE t.user_id = %s AND t.id = %s
            """, (user_id, thread_id))
        else:
            cursor.execute("""
                SELECT m.id, m.content
                FROM sessions.messages m
                JOIN sessions.threads t ON m.thread_id = t.id
                WHERE t.user_id = %s
            """, (user_id,))
        
        messages = cursor.fetchall()
        indexed_count = 0
        
        for msg_id, content in messages:
            if not content or len(content.strip()) < 10:
                continue
            
            # Generate embedding
            embedding = generate_embedding(content, user_id)
            
            if embedding:
                # Update message with embedding and FTS tokens
                cursor.execute("""
                    UPDATE sessions.messages
                    SET embedding = %s::vector,
                        fts_tokens = to_tsvector('english', %s)
                    WHERE id = %s
                """, (embedding, content, msg_id))
                indexed_count += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'indexed_count': indexed_count,
            'total_messages': len(messages)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# ENDPOINT 5: INDEX SYNERGY SESSIONS
# ============================================================================

@universal_search_bp.route('/index-synergy', methods=['POST'])
@require_auth  # ✅ FIX: Use standalone decorator
def index_synergy_for_search():
    """
    Generate embeddings and FTS tokens for Synergy sessions
    
    Returns:
        JSON with indexing results
    """
    try:
        user_id = request.user_id
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get Synergy sessions
        cursor.execute("""
            SELECT session_id, title, description
            FROM synergy_sessions.sessions
            WHERE user_id = %s
        """, (user_id,))
        
        sessions = cursor.fetchall()
        indexed_count = 0
        
        for session_id, title, description in sessions:
            content = f"{title or ''} {description or ''}"
            
            if len(content.strip()) < 10:
                continue
            
            # Generate embedding
            embedding = generate_embedding(content, user_id)
            
            if embedding:
                cursor.execute("""
                    UPDATE synergy_sessions.sessions
                    SET embedding = %s::vector,
                        fts_tokens = to_tsvector('english', %s)
                    WHERE session_id = %s
                """, (embedding, content, session_id))
                indexed_count += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'indexed_count': indexed_count,
            'total_sessions': len(sessions)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# EXPORT BLUEPRINT
# ============================================================================

print('[UNIVERSAL SEARCH] Routes loaded: 5 endpoints')
