"""
Universal Search Routes - Multi-Platform Search System

FILE: AI_infrastructure/routes/universal_search_routes.py
PURPOSE: Unified search across ALL user-connected platforms in one interface
FULLY FIXED VERSION - Production Ready

⚠️ CURSOR MANAGEMENT FIXES (Dec 07, 2025):
   - ✅ All cursors properly closed before connections
   - ✅ All functions use finally blocks
   - ✅ All cursors initialized as None
   - ✅ Guaranteed cleanup on exceptions

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

LAST MODIFIED: 2025-12-07 - Fixed cursor management
"""

from flask import Blueprint, request, jsonify
from AI_infrastructure.auth.user_auth import require_auth, UserAuthManager
import psycopg2
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests

# Create blueprint
universal_search_bp = Blueprint('universal_search', __name__, url_prefix='/api/universal-search')

# Initialize auth manager for credential access
auth_manager = UserAuthManager()

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
# HELPER: REGISTRY-DISPATCHED SEARCH (4-tier creds + schema validation)
# ============================================================================
#
# Per the Option A refactor (2026-07-28), the 8 platform sources (Gmail, Google
# Drive, Outlook, OneDrive, SharePoint, Slack, Google Calendar, Microsoft
# Calendar) all funnel through the same shape:
#
#   1. resolve_credentials(user_id, '<platform_key>')   (org_credentials_loader)
#   2. registry.execute_tool(tool_name='<tool>', query=..., top_k=limit, ...)
#   3. map result['matches'] (or provider-specific shape) -> universal_search dict
#
# This replaces the prior OAuth-direct branches (GAP-V1 pattern from
# CLAUDE.md §13.4). One helper, many callers.

def _search_via_registry(user_id: int, platform_key: str, tool_name: str,
                          query: str, limit: int,
                          result_key: str = 'matches',
                          result_adapter=None,
                          extra_kwargs: Optional[Dict[str, Any]] = None,
                          ) -> List[Dict[str, Any]]:
    """Run a search-style tool through the registry.

    Args:
        user_id: RLS-scoped user id (request.user.get('user_id')).
        platform_key: 4-tier resolver key — e.g. 'google_workspace',
            'microsoft_365', 'slack'.
        tool_name: Registered tool name in the registry, e.g.
            'gmail_search_messages'.
        query: User's search string.
        limit: Max results the source should return.
        result_key: The dict key holding the list inside the tool result.
            Most platform search tools return {'success': True, 'matches': [...]}
            or similar. Default 'matches'.
        result_adapter: Optional callable(match) -> result_dict. If None, a
            generic shape is produced from id/title/text/score.
        extra_kwargs: Optional kwargs merged into the registry call.

    Returns:
        List of normalized result dicts. Empty list if no creds, no match,
        or any silent skip condition. NEVER raises — errors are swallowed
        by the caller.
    """
    try:
        from AI_infrastructure.shared.org_credentials_loader import resolve_credentials
        creds = resolve_credentials(user_id, platform_key)
        if not creds:
            return []
        from tools.registry_v3 import RegistryV3
        registry = RegistryV3()
        kwargs = dict(
            tool_name=tool_name,
            query=query,
            top_k=limit,
            _user_id=user_id,
            _injected_credentials=True,
        )
        if extra_kwargs:
            kwargs.update(extra_kwargs)
        result = registry.execute_tool(**kwargs)
        if not result or not result.get('success'):
            return []
        items = result.get(result_key) or []
        if result_adapter is not None:
            return [result_adapter(m) for m in items if m]
        # Generic shape: extract common fields if present, else pass through.
        out: List[Dict[str, Any]] = []
        for m in items:
            if not isinstance(m, dict):
                continue
            out.append({
                'id': m.get('id') or m.get('message_id') or m.get('file_id'),
                'title': (m.get('title') or m.get('subject') or m.get('name')
                          or m.get('filename') or ''),
                'text': (m.get('text') or m.get('snippet') or m.get('body')
                         or m.get('bodyPreview') or m.get('description') or ''),
                'score': float(m.get('score', 0.0) or 0.0),
                'date': (m.get('date') or m.get('receivedDateTime')
                         or m.get('createdTime') or m.get('start', {}).get('dateTime')),
                'link': (m.get('link') or m.get('webViewLink')
                         or m.get('webUrl') or m.get('permalink')),
                'metadata': m.get('metadata') or {},
                'provider': platform_key,
            })
        return out
    except Exception as e:
        # Silent skip with print — same pattern as the Pinecone branch.
        print(f"[UNIVERSAL SEARCH] {platform_key}.{tool_name} failed: {e}")
        return []


def _search_calendar_via_registry(user_id: int, platform_key: str,
                                  list_tool: str, query: str, limit: int,
                                  time_min: Optional[str] = None,
                                  time_max: Optional[str] = None,
                                  ) -> List[Dict[str, Any]]:
    """Calendar sources have no dedicated search tool — only list_events.

    Strategy: pull a recent window via list_events, then filter by substring
    match on summary/description/subject. Capped at `limit` survivors.
    """
    try:
        from AI_infrastructure.shared.org_credentials_loader import resolve_credentials
        creds = resolve_credentials(user_id, platform_key)
        if not creds:
            return []
        from tools.registry_v3 import RegistryV3
        registry = RegistryV3()
        kwargs: Dict[str, Any] = dict(
            tool_name=list_tool,
            max_results=min(limit * 4, 100),  # Pull more, then filter.
            _user_id=user_id,
            _injected_credentials=True,
        )
        if time_min:
            kwargs['time_min'] = time_min
        if time_max:
            kwargs['time_max'] = time_max
        result = registry.execute_tool(**kwargs)
        if not result or not result.get('success'):
            return []
        events = (result.get('events')
                  or result.get('items')
                  or result.get('matches')
                  or [])
        if not isinstance(events, list):
            return []
        needle = (query or '').strip().lower()
        if needle:
            events = [
                e for e in events
                if needle in (str((e or {}).get('summary') or '')).lower()
                or needle in (str((e or {}).get('description') or '')).lower()
                or needle in (str((e or {}).get('subject') or '')).lower()
            ]
        out: List[Dict[str, Any]] = []
        for e in events[:limit]:
            start = (e or {}).get('start') or {}
            out.append({
                'id': (e or {}).get('id'),
                'title': (e or {}).get('summary') or (e or {}).get('subject') or '',
                'text': (e or {}).get('description') or '',
                'score': 1.0,  # No native score — events are equal-weight.
                'date': start.get('dateTime') or start.get('date'),
                'link': (e or {}).get('htmlLink') or (e or {}).get('webLink'),
                'metadata': e,
                'provider': platform_key,
            })
        return out
    except Exception as e:
        print(f"[UNIVERSAL SEARCH] {platform_key} calendar failed: {e}")
        return []


# ============================================================================
# HELPER: RESULT DEDUP
# ============================================================================
#
# When the same content exists in multiple sources (e.g., a contract as a
# Gmail attachment AND a Drive file), naive fan-out returns duplicates. We
# bucket by content-hash, pick the highest-score winner per bucket, and emit
# `merged_from` so the AI can cite every source that contributed.

# Provider priority for tie-breaking (lower index = higher priority).
# Tuned by hand-off brief §3; user can override by reordering.
DEFAULT_PROVIDER_PRIORITY = [
    'pgvector',
    'pinecone',
    'qdrant',
    'documents',  # Internal document library
    'vector-database',
    'threads',
    'messages',
    'synergy',
    'google_drive', 'google-drive',
    'gmail',
    'onedrive',
    'outlook',
    'sharepoint',
    'google_calendar', 'microsoft_calendar',
    'slack',
    'xero',
    'inhouseprint',
]


def _result_dedup_key(item: Dict[str, Any]) -> str:
    """Compute a content-hash key for dedup.

    Primary: SHA1 of lowercased + whitespace-stripped text.
    Fallback (no text): SHA1 of (title + provider).
    """
    import hashlib
    text = (item.get('text') or item.get('snippet') or '').strip().lower()
    text = ' '.join(text.split())
    if text:
        payload = text
    else:
        payload = f"{(item.get('title') or '').strip().lower()}|{item.get('provider') or ''}"
    return hashlib.sha1(payload.encode('utf-8')).hexdigest()


def _dedup_results(results: List[Dict[str, Any]],
                   priority: Optional[List[str]] = None,
                   ) -> List[Dict[str, Any]]:
    """Merge duplicate results, keeping the highest-score winner per content.

    Each surviving result gains a `merged_from` list with one entry per
    duplicate that was collapsed into it: `[{provider, id}, ...]`.

    Args:
        results: List of result dicts (must have at least `text`/`title` and
            `provider`).
        priority: Provider priority order for tie-breaking. Lower index wins.

    Returns:
        New list with duplicates removed. Empty list for empty input.
    """
    if not results:
        return []
    prio = priority or DEFAULT_PROVIDER_PRIORITY
    prio_index = {p: i for i, p in enumerate(prio)}

    buckets: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []  # Preserve first-seen order
    for item in results:
        key = _result_dedup_key(item)
        if key not in buckets:
            buckets[key] = {
                'winner': dict(item),
                'merged_from': [],
            }
            order.append(key)
            continue
        # Duplicate — track it on the bucket, but do NOT yet demote the winner.
        existing = buckets[key]['winner']
        incoming_prio = prio_index.get(item.get('provider'), 9999)
        winner_prio = prio_index.get(existing.get('provider'), 9999)
        incoming_score = float(item.get('score', 0.0) or 0.0)
        winner_score = float(existing.get('score', 0.0) or 0.0)
        if (incoming_score > winner_score
                or (incoming_score == winner_score and incoming_prio < winner_prio)):
            # Incoming wins — record the old winner as a merge source.
            buckets[key]['merged_from'].append({
                'provider': existing.get('provider'),
                'id': existing.get('id'),
            })
            buckets[key]['winner'] = dict(item)
        else:
            buckets[key]['merged_from'].append({
                'provider': item.get('provider'),
                'id': item.get('id'),
            })

    out: List[Dict[str, Any]] = []
    for key in order:
        winner = dict(buckets[key]['winner'])
        merged_from = buckets[key]['merged_from']
        if merged_from:
            winner['merged_from'] = merged_from
        out.append(winner)
    return out


# ============================================================================
# ENDPOINT 1: UNIVERSAL SEARCH
# ============================================================================

@universal_search_bp.route('/search', methods=['GET', 'POST'])
@require_auth
def universal_search():
    """
    Search across ALL user-connected platforms
    
    ✅ FIXED: Proper cursor management with finally block
    
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
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    try:
        # Get user_id from request.user (set by @require_auth decorator)
        user_id = request.user.get('user_id')
        
        # Handle both GET and POST
        if request.method == 'GET':
            query = request.args.get('query', '')
            sources = request.args.get('sources', '').split(',') if request.args.get('sources') else []
            search_type = request.args.get('search_type', 'hybrid')
            limit = int(request.args.get('limit', 10))
        else:
            data = request.get_json() or {}
            query = data.get('query', '')
            sources = data.get('sources', [])
            search_type = data.get('search_type', 'hybrid')
            limit = data.get('limit', 10)
        
        # What to search (default: all enabled unless sources specified)
        if request.method == 'GET':
            # For GET, sources come from query params (array)
            include_documents = 'documents' in sources or not sources
            include_messages = 'messages' in sources or not sources
            include_synergy = 'synergy' in sources or not sources
            include_vector_db = 'vector-database' in sources
            include_supabase = False
            include_gmail = 'gmail' in sources
            include_slack = 'slack' in sources
            include_xero = 'xero' in sources
            include_inhouseprint = 'inhouseprint' in sources
            include_google_drive = 'google-drive' in sources
            include_onedrive = 'onedrive' in sources
            include_sharepoint = 'sharepoint' in sources
            include_outlook = 'outlook' in sources
            include_google_calendar = 'google-calendar' in sources
            include_microsoft_calendar = 'microsoft-calendar' in sources
        else:
            # For POST, use data payload
            include_documents = data.get('include_documents', True)
            include_messages = data.get('include_messages', True)
            include_synergy = data.get('include_synergy', True)
            include_vector_db = data.get('include_vector_db', 'vector-database' in sources)
            include_supabase = data.get('include_supabase', False)
            include_gmail = data.get('include_gmail', 'gmail' in sources)
            include_slack = data.get('include_slack', 'slack' in sources)
            include_xero = data.get('include_xero', 'xero' in sources)
            include_inhouseprint = data.get('include_inhouseprint', 'inhouseprint' in sources)
            include_google_drive = data.get('include_google_drive', 'google-drive' in sources)
            include_onedrive = data.get('include_onedrive', 'onedrive' in sources)
            include_sharepoint = data.get('include_sharepoint', 'sharepoint' in sources)
            include_outlook = data.get('include_outlook', 'outlook' in sources)
            include_google_calendar = data.get('include_google_calendar', 'google-calendar' in sources)
            include_microsoft_calendar = data.get('include_microsoft_calendar', 'microsoft-calendar' in sources)
        
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
                        SELECT t.thread_slug, t.name, t.created_at, 
                               (SELECT COUNT(*) FROM sessions.messages WHERE thread_id = t.id) as message_count,
                               ts_rank(t.fts_tokens, websearch_to_tsquery('english', %s)) AS rank
                        FROM sessions.threads t
                        WHERE t.fts_tokens @@ websearch_to_tsquery('english', %s)
                          AND t.user_id = %s
                        ORDER BY rank DESC
                        LIMIT %s
                    """, (query, query, user_id, limit))
                
                elif search_type == 'semantic' and query_embedding:
                    cursor.execute("""
                        SELECT thread_slug, name, created_at,
                               (SELECT COUNT(*) FROM sessions.messages WHERE thread_id = t.id) as message_count,
                               1 - (embedding <=> %s::vector) AS similarity
                        FROM sessions.threads t
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
                        SELECT session_id, title, created_at,
                               (SELECT COUNT(*) FROM synergy_sessions.agents WHERE session_id = s.session_id) as agent_count,
                               ts_rank(fts_tokens, websearch_to_tsquery('english', %s)) AS rank
                        FROM synergy_sessions.sessions s
                        WHERE fts_tokens @@ websearch_to_tsquery('english', %s)
                          AND user_id = %s
                        ORDER BY rank DESC
                        LIMIT %s
                    """, (query, query, user_id, limit))
                
                elif search_type == 'semantic' and query_embedding:
                    cursor.execute("""
                        SELECT session_id, title, created_at,
                               (SELECT COUNT(*) FROM synergy_sessions.agents WHERE session_id = s.session_id) as agent_count,
                               1 - (embedding <=> %s::vector) AS similarity
                        FROM synergy_sessions.sessions s
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
                            'type': 'session',
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
                
                # Also search Synergy Internal Docs (Google Docs/Sheets within Synergy)
                try:
                    search_pattern = f'%{query}%'
                    cursor.execute("""
                        SELECT 
                            d.doc_id,
                            d.title,
                            d.doc_type,
                            d.session_id,
                            s.title as session_title,
                            d.slug,
                            d.created_at,
                            d.updated_at,
                            CASE 
                                WHEN d.title ILIKE %s THEN 'title'
                                ELSE 'content'
                            END as match_field
                        FROM synergy_sessions.synergy_internal_docs d
                        LEFT JOIN synergy_sessions.synergy_sessions s 
                            ON d.session_id = s.session_id
                        WHERE (d.title ILIKE %s OR d.content ILIKE %s)
                        ORDER BY 
                            CASE WHEN d.title ILIKE %s THEN 1 ELSE 2 END,
                            d.updated_at DESC
                        LIMIT %s
                    """, (search_pattern, search_pattern, search_pattern, search_pattern, limit))
                    
                    synergy_docs = cursor.fetchall()
                    if synergy_docs:
                        # Append docs to synergy results
                        for row in synergy_docs:
                            results['sources']['synergy']['results'].append({
                                'type': 'document',
                                'id': row[0],
                                'doc_id': row[0],
                                'title': row[1],
                                'doc_type': row[2],  # 'richtext' or 'spreadsheet'
                                'session_id': row[3],
                                'session_title': row[4] or 'Untitled Session',
                                'slug': row[5],
                                'date': row[6].isoformat() if row[6] else None,
                                'updated': row[7].isoformat() if row[7] else None,
                                'match_field': row[8],
                                'url': f'/synergy/{row[3]}/doc/{row[0]}'
                            })
                        results['sources']['synergy']['count'] += len(synergy_docs)
                        results['total_results'] += len(synergy_docs)
                except Exception as doc_error:
                    print(f"[UNIVERSAL SEARCH] Synergy docs search error: {doc_error}")
                    # Don't fail entire synergy search if docs search fails
                
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Synergy search error: {e}")
                results['sources']['synergy'] = {'error': str(e)}
        
        # ========================================================================
        # 4.5. SEARCH VECTOR DATABASES (pgvector/Qdrant/Pinecone)
        # ========================================================================
        # NOTE: Priority order - pgvector (default, Supabase built-in) → Qdrant (optional, self-hosted) → Pinecone (paid)
        # pgvector results already included in 'documents' source above (semantic/hybrid search)
        if include_vector_db and query_embedding:
            try:
                vector_results = []
                provider_used = None
                
                # Option 1: Search pgvector (ai_infrastructure.org_vector_documents)
                # BUGFIX (2026-07-28): The legacy SQL pointed at
                # ai_infrastructure.vector_embeddings, which has been empty
                # since the migration-044 org_vector_documents refactor — every
                # pgvector search silently returned zero rows. Now we read the
                # real table, filter by org_id (not user_id, since pgvector is
                # org-scoped via the org_isolation_select RLS policy), and use
                # the dedicated content/filename/file_type columns instead of
                # extracting them out of metadata JSONB.
                try:
                    # Look up the user's org_id. pgvector data is org-scoped
                    # (not user-scoped) — see migration 044 and the
                    # ai_infrastructure.org_vector_documents table.
                    cursor.execute(
                        "SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s",
                        (user_id,),
                    )
                    org_row = cursor.fetchone()
                    user_org_id = org_row[0] if org_row else None

                    if user_org_id is not None:
                        cursor.execute("""
                            SELECT d.id::TEXT,
                                   d.filename         AS title,
                                   d.content          AS text,
                                   d.file_type,
                                   d.created_at,
                                   1 - (d.embedding <=> %s::vector) AS similarity
                            FROM ai_infrastructure.org_vector_documents d
                            WHERE d.org_id = %s
                              AND d.embedding IS NOT NULL
                              AND (1 - (d.embedding <=> %s::vector)) > 0.3
                            ORDER BY d.embedding <=> %s::vector
                            LIMIT %s
                        """, (query_embedding, user_org_id, query_embedding, query_embedding, limit))

                        pgvector_results = cursor.fetchall()
                        if pgvector_results:
                            vector_results = [
                                {
                                    'id':       str(row[0]),
                                    'title':    row[1] or 'Untitled',
                                    'snippet':  ((row[2] or '')[:200] + '...') if row[2] else '',
                                    'source':   'vector-database',
                                    'type':     row[3] or 'document',
                                    'date':     row[4],
                                    'score':    float(row[5]) if row[5] else 0.0,
                                    'provider': 'pgvector (Supabase)'
                                }
                                for row in pgvector_results
                            ]
                            provider_used = 'pgvector'
                            print(f"[UNIVERSAL SEARCH] Found {len(vector_results)} results in pgvector (org {user_org_id})")
                except Exception as pgvector_err:
                    print(f"[UNIVERSAL SEARCH] pgvector search skipped: {pgvector_err}")
                
                # Option 2: Try Qdrant (if user has configured it)
                if not vector_results:
                    try:
                        from AI_infrastructure.routes.qdrant_routes import get_qdrant_client
                        qdrant_client = get_qdrant_client(user_id)
                        if qdrant_client:
                            search_results = qdrant_client.search(
                                collection_name="user_documents",
                                query_vector=query_embedding,
                                limit=limit
                            )
                            vector_results = [
                                {
                                    'id': str(hit.id),
                                    'title': hit.payload.get('title', 'Untitled'),
                                    'snippet': (hit.payload.get('text', '') or '')[:200] + '...',
                                    'source': 'vector-database',
                                    'type': hit.payload.get('file_type', 'document'),
                                    'date': hit.payload.get('created_at'),
                                    'score': float(hit.score),
                                    'provider': 'Qdrant (Self-hosted)'
                                }
                                for hit in search_results
                            ]
                            provider_used = 'Qdrant'
                            print(f"[UNIVERSAL SEARCH] Found {len(vector_results)} results in Qdrant")
                    except Exception as qdrant_err:
                        print(f"[UNIVERSAL SEARCH] Qdrant search failed: {qdrant_err}")
                
                # Option 3: Try Pinecone (if user has configured it via the org vault).
                # BUGFIX (2026-07-28): the legacy TODO stub did nothing — users
                # with Pinecone credentials configured got zero results.
                # Now we resolve credentials via the 4-tier loader, and if
                # Pinecone is configured, dispatch through the registry so
                # schema validation + provider routing happen in one place.
                if not vector_results:
                    try:
                        from AI_infrastructure.shared.org_credentials_loader import resolve_credentials
                        pinecone_creds = resolve_credentials(user_id, 'pinecone')
                        if pinecone_creds:
                            from tools.registry_v3 import RegistryV3
                            registry = RegistryV3()
                            result = registry.execute_tool(
                                tool_name='pinecone_query_vectors',
                                query_vector=query_embedding,
                                top_k=limit,
                                _user_id=user_id,
                                _injected_credentials=True,
                            )
                            if result.get('success') and result.get('matches'):
                                matches = result['matches'] or []
                                vector_results = [
                                    {
                                        'id':       m.get('id'),
                                        'title':    ((m.get('metadata') or {}).get('filename')
                                                     or (m.get('metadata') or {}).get('title')
                                                     or 'Untitled'),
                                        'snippet':  ((m.get('metadata') or {}).get('text') or '')[:200] + '...',
                                        'source':   'vector-database',
                                        'type':     (m.get('metadata') or {}).get('file_type') or 'document',
                                        'date':     (m.get('metadata') or {}).get('created_at'),
                                        'score':    float(m.get('score', 0.0) or 0.0),
                                        'provider': 'pinecone',
                                    }
                                    for m in matches
                                ]
                                provider_used = 'pinecone'
                                print(f"[UNIVERSAL SEARCH] Found {len(vector_results)} results in Pinecone")
                        # No credentials → silently skip (matches the Qdrant behaviour above).
                    except Exception as pinecone_err:
                        print(f"[UNIVERSAL SEARCH] Pinecone search failed: {pinecone_err}")
                
                # Return results
                if vector_results:
                    results['sources']['vector-database'] = {
                        'count': len(vector_results),
                        'results': vector_results,
                        'provider': provider_used
                    }
                    results['total_results'] += len(vector_results)
                else:
                    results['sources']['vector-database'] = {
                        'count': 0,
                        'results': [],
                        'message': 'No additional vector embeddings found (document library already uses pgvector)',
                        'note': 'pgvector is active in "Documents" source for semantic search'
                    }
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Vector DB search error: {e}")
                results['sources']['vector-database'] = {'error': str(e)}
        
        # ========================================================================
        # 5. SEARCH GMAIL (registry-dispatched)
        # ========================================================================
        if include_gmail:
            try:
                # 4-tier resolver → registry.execute_tool → matches
                gmail_matches = _search_via_registry(
                    user_id=user_id,
                    platform_key='google_workspace',
                    tool_name='gmail_search_messages',
                    query=query,
                    limit=limit,
                    result_key='messages',
                    result_adapter=lambda m: {
                        'id': m.get('id') or m.get('message_id'),
                        'title': (m.get('subject') or m.get('snippet') or '(no subject)'),
                        'text': (m.get('snippet') or m.get('body') or ''),
                        'score': float(m.get('score', 0.0) or 0.0),
                        'date': m.get('date') or m.get('internal_date'),
                        'link': None,
                        'metadata': m,
                        'provider': 'gmail',
                    },
                )
                if not gmail_matches and results['sources'].get('gmail') is None:
                    # Resolve returned None OR zero matches — distinguish by checking creds.
                    try:
                        from AI_infrastructure.shared.org_credentials_loader import resolve_credentials
                        if not resolve_credentials(user_id, 'google_workspace'):
                            results['sources']['gmail'] = {'error': 'Gmail not connected'}
                        else:
                            results['sources']['gmail'] = {
                                'count': 0, 'results': [], 'message': 'No matches',
                            }
                    except Exception:
                        results['sources']['gmail'] = {'error': 'Gmail not connected'}
                else:
                    results['sources']['gmail'] = {
                        'count': len(gmail_matches),
                        'results': gmail_matches,
                    }
                    results['total_results'] += len(gmail_matches)
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Gmail search error: {e}")
                results['sources']['gmail'] = {'error': str(e)}
        
        # ========================================================================
        # 6. SEARCH SLACK (registry-dispatched)
        # ========================================================================
        if include_slack:
            try:
                slack_matches = _search_via_registry(
                    user_id=user_id,
                    platform_key='slack',
                    tool_name='slack_search_messages',
                    query=query,
                    limit=limit,
                    result_key='messages',
                    result_adapter=lambda m: {
                        'id': m.get('ts') or m.get('id'),
                        'title': (m.get('text') or '')[:120],
                        'text': m.get('text') or '',
                        'score': float(m.get('score', 0.0) or 0.0),
                        'date': None,
                        'link': m.get('permalink'),
                        'metadata': m,
                        'provider': 'slack',
                    },
                )
                if slack_matches:
                    results['sources']['slack'] = {
                        'count': len(slack_matches),
                        'results': slack_matches,
                    }
                    results['total_results'] += len(slack_matches)
                else:
                    try:
                        from AI_infrastructure.shared.org_credentials_loader import resolve_credentials
                        if not resolve_credentials(user_id, 'slack'):
                            results['sources']['slack'] = {'error': 'Slack not connected'}
                        else:
                            results['sources']['slack'] = {
                                'count': 0, 'results': [], 'message': 'No matches',
                            }
                    except Exception:
                        results['sources']['slack'] = {'error': 'Slack not connected'}
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Slack search error: {e}")
                results['sources']['slack'] = {'error': str(e)}
        
        # ========================================================================
        # 6. SEARCH XERO (Accounting Data)
        # ========================================================================
        if include_xero:
            try:
                from UI.modules_external.xero.xero_routes import XeroAPIClient
                
                xero_results = []
                # Search across all 3 businesses
                for business_id in [1, 2, 3]:  # 1=Print, 2=Publishing, 3=Signs
                    try:
                        xero_client = XeroAPIClient(business_id=business_id, user_id=user_id)
                        xero_client.get_access_token()  # Initialize token
                        
                        business_name = xero_client.config['name']
                        
                        # Search invoices
                        invoices = xero_client.make_request(
                            'GET', 
                            'Invoices',
                            params={'where': f'Contact.Name.Contains("{query}") OR InvoiceNumber.Contains("{query}")'}
                        )
                        if invoices and 'Invoices' in invoices:
                            for inv in invoices['Invoices'][:5]:  # Top 5 per business
                                xero_results.append({
                                    'type': 'invoice',
                                    'business': business_name,
                                    'business_id': business_id,
                                    'invoice_number': inv.get('InvoiceNumber'),
                                    'contact': inv.get('Contact', {}).get('Name'),
                                    'total': inv.get('Total'),
                                    'date': inv.get('Date'),
                                    'status': inv.get('Status'),
                                    'due_date': inv.get('DueDate')
                                })
                        
                        # Search contacts
                        contacts = xero_client.make_request(
                            'GET',
                            'Contacts',
                            params={'where': f'Name.Contains("{query}") OR EmailAddress.Contains("{query}")'}
                        )
                        if contacts and 'Contacts' in contacts:
                            for contact in contacts['Contacts'][:5]:
                                xero_results.append({
                                    'type': 'contact',
                                    'business': business_name,
                                    'business_id': business_id,
                                    'name': contact.get('Name'),
                                    'email': contact.get('EmailAddress'),
                                    'phone': contact.get('Phones', [{}])[0].get('PhoneNumber') if contact.get('Phones') else None,
                                    'is_customer': contact.get('IsCustomer'),
                                    'is_supplier': contact.get('IsSupplier')
                                })
                        
                    except Exception as business_error:
                        print(f"[XERO] Search error for business {business_id}: {business_error}")
                        continue
                
                results['sources']['xero'] = {
                    'count': len(xero_results),
                    'results': xero_results[:limit]
                }
                results['total_results'] += len(xero_results)
                
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Xero search error: {e}")
                results['sources']['xero'] = {'error': str(e)}
        
        # ========================================================================
        # 7. SEARCH INHOUSEPRINT (SQL Server Database)
        # ========================================================================
        if include_inhouseprint:
            inhouse_cursor = None  # ✅ Initialize cursor before try
            inhouse_conn = None    # ✅ Initialize connection before try
            try:
                import pymssql
                
                # Connect to InHousePrint SQL Server
                inhouse_conn = pymssql.connect(
                    server='3.25.76.138',
                    port=1433,
                    user='sa',
                    password='Jack2011',
                    database='InHousePrint',
                    timeout=10
                )
                inhouse_cursor = inhouse_conn.cursor(as_dict=True)
                
                inhouse_results = []
                
                # Search PublishingProject table
                inhouse_cursor.execute("""
                    SELECT TOP 20
                        p.ID,
                        p.ProjectName,
                        p.Description,
                        p.StartDate,
                        p.DeadlineDate,
                        p.Status,
                        c.CompanyName,
                        c.ContactName,
                        c.Email
                    FROM PublishingProject p
                    LEFT JOIN Clients c ON p.ClientID = c.ID
                    WHERE 
                        p.ProjectName LIKE %s OR
                        p.Description LIKE %s OR
                        c.CompanyName LIKE %s OR
                        c.ContactName LIKE %s
                    ORDER BY p.StartDate DESC
                """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
                
                projects = inhouse_cursor.fetchall()
                for proj in projects:
                    inhouse_results.append({
                        'type': 'project',
                        'id': proj['ID'],
                        'project_name': proj['ProjectName'],
                        'description': proj['Description'],
                        'client': proj['CompanyName'],
                        'contact': proj['ContactName'],
                        'email': proj['Email'],
                        'start_date': proj['StartDate'].isoformat() if proj['StartDate'] else None,
                        'deadline': proj['DeadlineDate'].isoformat() if proj['DeadlineDate'] else None,
                        'status': proj['Status']
                    })
                
                # Search Clients table
                inhouse_cursor.execute("""
                    SELECT TOP 20
                        ID,
                        CompanyName,
                        ContactName,
                        Email,
                        Phone,
                        Address
                    FROM Clients
                    WHERE 
                        CompanyName LIKE %s OR
                        ContactName LIKE %s OR
                        Email LIKE %s
                    ORDER BY CompanyName
                """, (f'%{query}%', f'%{query}%', f'%{query}%'))
                
                clients = inhouse_cursor.fetchall()
                for client in clients:
                    inhouse_results.append({
                        'type': 'client',
                        'id': client['ID'],
                        'company': client['CompanyName'],
                        'contact': client['ContactName'],
                        'email': client['Email'],
                        'phone': client['Phone'],
                        'address': client['Address']
                    })
                
                results['sources']['inhouseprint'] = {
                    'count': len(inhouse_results),
                    'results': inhouse_results[:limit]
                }
                results['total_results'] += len(inhouse_results)
                
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] InHousePrint search error: {e}")
                results['sources']['inhouseprint'] = {'error': str(e)}
            finally:
                # ✅ Guaranteed cleanup
                if inhouse_cursor:
                    try:
                        inhouse_cursor.close()
                    except:
                        pass
                if inhouse_conn:
                    try:
                        inhouse_conn.close()
                    except:
                        pass
        
        # ========================================================================
        # 8. SEARCH GOOGLE DRIVE (registry-dispatched)
        # ========================================================================
        if include_google_drive:
            try:
                drive_matches = _search_via_registry(
                    user_id=user_id,
                    platform_key='google_workspace',
                    tool_name='google_drive_search_files',
                    query=query,
                    limit=limit,
                    result_key='files',
                    result_adapter=lambda f: {
                        'id': f.get('id'),
                        'title': f.get('name') or '(untitled)',
                        'text': f.get('description') or f.get('name') or '',
                        'score': float(f.get('score', 0.0) or 0.0),
                        'date': f.get('modifiedTime') or f.get('createdTime'),
                        'link': f.get('webViewLink'),
                        'metadata': {
                            'mime_type': f.get('mimeType'),
                            'size': f.get('size'),
                            'owner': ((f.get('owners') or [{}])[0].get('displayName')
                                      if f.get('owners') else None),
                        },
                        'provider': 'google-drive',
                    },
                )
                if drive_matches:
                    results['sources']['google-drive'] = {
                        'count': len(drive_matches),
                        'results': drive_matches,
                    }
                    results['total_results'] += len(drive_matches)
                else:
                    try:
                        from AI_infrastructure.shared.org_credentials_loader import resolve_credentials
                        if not resolve_credentials(user_id, 'google_workspace'):
                            results['sources']['google-drive'] = {'error': 'Google Drive not connected'}
                        else:
                            results['sources']['google-drive'] = {
                                'count': 0, 'results': [], 'message': 'No matches',
                            }
                    except Exception:
                        results['sources']['google-drive'] = {'error': 'Google Drive not connected'}
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Google Drive search error: {e}")
                results['sources']['google-drive'] = {'error': str(e)}
        
        # ========================================================================
        # 9. SEARCH ONEDRIVE (registry-dispatched)
        # ========================================================================
        if include_onedrive:
            try:
                onedrive_matches = _search_via_registry(
                    user_id=user_id,
                    platform_key='microsoft_365',
                    tool_name='microsoft_onedrive_search_files',
                    query=query,
                    limit=limit,
                    result_key='items',
                    result_adapter=lambda f: {
                        'id': f.get('id'),
                        'title': f.get('name') or '(untitled)',
                        'text': f.get('description') or f.get('name') or '',
                        'score': float(f.get('score', 0.0) or 0.0),
                        'date': f.get('lastModifiedDateTime') or f.get('createdDateTime'),
                        'link': f.get('webUrl'),
                        'metadata': {
                            'type': 'folder' if f.get('folder') else 'file',
                            'size': f.get('size'),
                            'mime_type': (f.get('file') or {}).get('mimeType'),
                        },
                        'provider': 'onedrive',
                    },
                )
                if onedrive_matches:
                    results['sources']['onedrive'] = {
                        'count': len(onedrive_matches),
                        'results': onedrive_matches,
                    }
                    results['total_results'] += len(onedrive_matches)
                else:
                    try:
                        from AI_infrastructure.shared.org_credentials_loader import resolve_credentials
                        if not resolve_credentials(user_id, 'microsoft_365'):
                            results['sources']['onedrive'] = {'error': 'OneDrive not connected'}
                        else:
                            results['sources']['onedrive'] = {
                                'count': 0, 'results': [], 'message': 'No matches',
                            }
                    except Exception:
                        results['sources']['onedrive'] = {'error': 'OneDrive not connected'}
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] OneDrive search error: {e}")
                results['sources']['onedrive'] = {'error': str(e)}
        
        # ========================================================================
        # 10. SEARCH SHAREPOINT (registry-dispatched)
        # ========================================================================
        if include_sharepoint:
            try:
                sharepoint_matches = _search_via_registry(
                    user_id=user_id,
                    platform_key='microsoft_365',
                    tool_name='microsoft_sharepoint_search_content',
                    query=query,
                    limit=limit,
                    result_key='matches',
                    result_adapter=lambda f: {
                        'id': f.get('id') or f.get('driveItemId'),
                        'title': f.get('name') or f.get('title') or '(untitled)',
                        'text': f.get('summary') or f.get('name') or '',
                        'score': float(f.get('score', 0.0) or 0.0),
                        'date': f.get('lastModifiedDateTime') or f.get('createdDateTime'),
                        'link': f.get('webUrl'),
                        'metadata': {
                            'site': f.get('siteName') or f.get('siteDisplayName'),
                            'size': f.get('size'),
                        },
                        'provider': 'sharepoint',
                    },
                )
                if sharepoint_matches:
                    results['sources']['sharepoint'] = {
                        'count': len(sharepoint_matches),
                        'results': sharepoint_matches,
                    }
                    results['total_results'] += len(sharepoint_matches)
                else:
                    try:
                        from AI_infrastructure.shared.org_credentials_loader import resolve_credentials
                        if not resolve_credentials(user_id, 'microsoft_365'):
                            results['sources']['sharepoint'] = {'error': 'SharePoint not connected'}
                        else:
                            results['sources']['sharepoint'] = {
                                'count': 0, 'results': [], 'message': 'No matches',
                            }
                    except Exception:
                        results['sources']['sharepoint'] = {'error': 'SharePoint not connected'}
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] SharePoint search error: {e}")
                results['sources']['sharepoint'] = {'error': str(e)}
        
        # ========================================================================
        # 11. SEARCH OUTLOOK (registry-dispatched)
        # ========================================================================
        if include_outlook:
            try:
                outlook_matches = _search_via_registry(
                    user_id=user_id,
                    platform_key='microsoft_365',
                    tool_name='microsoft_outlook_search_messages',
                    query=query,
                    limit=limit,
                    result_key='messages',
                    result_adapter=lambda m: {
                        'id': m.get('id') or m.get('message_id'),
                        'title': m.get('subject') or '(no subject)',
                        'text': m.get('bodyPreview') or m.get('snippet') or '',
                        'score': float(m.get('score', 0.0) or 0.0),
                        'date': m.get('receivedDateTime'),
                        'link': m.get('webLink'),
                        'metadata': {
                            'from': ((m.get('from') or {}).get('emailAddress') or {}).get('address'),
                            'is_read': m.get('isRead'),
                            'has_attachments': m.get('hasAttachments'),
                        },
                        'provider': 'outlook',
                    },
                )
                if outlook_matches:
                    results['sources']['outlook'] = {
                        'count': len(outlook_matches),
                        'results': outlook_matches,
                    }
                    results['total_results'] += len(outlook_matches)
                else:
                    try:
                        from AI_infrastructure.shared.org_credentials_loader import resolve_credentials
                        if not resolve_credentials(user_id, 'microsoft_365'):
                            results['sources']['outlook'] = {'error': 'Outlook not connected'}
                        else:
                            results['sources']['outlook'] = {
                                'count': 0, 'results': [], 'message': 'No matches',
                            }
                    except Exception:
                        results['sources']['outlook'] = {'error': 'Outlook not connected'}
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Outlook search error: {e}")
                results['sources']['outlook'] = {'error': str(e)}

        # ========================================================================
        # 12. SEARCH GOOGLE CALENDAR (list-then-filter; no native search tool)
        # ========================================================================
        if include_google_calendar:
            try:
                gcal_matches = _search_calendar_via_registry(
                    user_id=user_id,
                    platform_key='google_workspace',
                    list_tool='google_calendar_list_events',
                    query=query,
                    limit=limit,
                )
                if gcal_matches:
                    results['sources']['google-calendar'] = {
                        'count': len(gcal_matches),
                        'results': gcal_matches,
                    }
                    results['total_results'] += len(gcal_matches)
                else:
                    try:
                        from AI_infrastructure.shared.org_credentials_loader import resolve_credentials
                        if not resolve_credentials(user_id, 'google_workspace'):
                            results['sources']['google-calendar'] = {'error': 'Google Calendar not connected'}
                        else:
                            results['sources']['google-calendar'] = {
                                'count': 0, 'results': [], 'message': 'No matches',
                            }
                    except Exception:
                        results['sources']['google-calendar'] = {'error': 'Google Calendar not connected'}
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Google Calendar search error: {e}")
                results['sources']['google-calendar'] = {'error': str(e)}

        # ========================================================================
        # 13. SEARCH MICROSOFT CALENDAR (list-then-filter; no native search tool)
        # ========================================================================
        if include_microsoft_calendar:
            try:
                mcal_matches = _search_calendar_via_registry(
                    user_id=user_id,
                    platform_key='microsoft_365',
                    list_tool='microsoft_calendar_list_events',
                    query=query,
                    limit=limit,
                )
                if mcal_matches:
                    results['sources']['microsoft-calendar'] = {
                        'count': len(mcal_matches),
                        'results': mcal_matches,
                    }
                    results['total_results'] += len(mcal_matches)
                else:
                    try:
                        from AI_infrastructure.shared.org_credentials_loader import resolve_credentials
                        if not resolve_credentials(user_id, 'microsoft_365'):
                            results['sources']['microsoft-calendar'] = {'error': 'Microsoft Calendar not connected'}
                        else:
                            results['sources']['microsoft-calendar'] = {
                                'count': 0, 'results': [], 'message': 'No matches',
                            }
                    except Exception:
                        results['sources']['microsoft-calendar'] = {'error': 'Microsoft Calendar not connected'}
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Microsoft Calendar search error: {e}")
                results['sources']['microsoft-calendar'] = {'error': str(e)}

        # ========================================================================
        # 14. CROSS-SOURCE DEDUP (content-hash + merged_from)
        # ========================================================================
        # Flatten every successful source into one list, dedup by content-hash,
        # then write the survivors back into a synthetic 'merged' source. The
        # per-source buckets are preserved so the UI can still show per-source
        # facets; the merged list is the canonical answer for the AI.
        try:
            all_hits: List[Dict[str, Any]] = []
            for src_key, src_blob in (results.get('sources') or {}).items():
                if not isinstance(src_blob, dict):
                    continue
                items = src_blob.get('results')
                if not isinstance(items, list) or not items:
                    continue
                # Only dedup registry-shaped dicts (have provider field).
                for it in items:
                    if isinstance(it, dict) and it.get('provider'):
                        all_hits.append(it)
            if all_hits:
                deduped = _dedup_results(all_hits)
                results['sources']['merged'] = {
                    'count': len(deduped),
                    'results': deduped,
                    'note': 'Cross-source dedup; merged_from lists collapses.',
                }
        except Exception as dedup_err:
            print(f"[UNIVERSAL SEARCH] dedup skipped: {dedup_err}")

        return jsonify({
            'success': True,
            **results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        # ✅ Guaranteed cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass

# ============================================================================
# ENDPOINT 2: GET FACETS (FOR FILTER UI)
# ============================================================================

@universal_search_bp.route('/facets', methods=['GET'])
@require_auth
def get_search_facets():
    """
    Get aggregated facets for filter UI
    
    ✅ FIXED: Proper cursor management with finally block
    
    Returns:
        JSON with counts by source, type, date range
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
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
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'facets': facets
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        # ✅ Guaranteed cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass

# ============================================================================
# ENDPOINT 3: LIST AVAILABLE SOURCES
# ============================================================================

@universal_search_bp.route('/sources', methods=['GET'])
@require_auth
def get_available_sources():
    """
    List all platforms user has connected
    
    ✅ NO DATABASE OPERATIONS - No cursor management needed
    
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
@require_auth
def index_messages_for_search():
    """
    Generate embeddings and FTS tokens for existing messages
    
    ✅ FIXED: Proper cursor management with finally block
    
    Body:
        thread_id (int): Optional - Index specific thread only
        force_reindex (bool): Re-index even if already indexed
    
    Returns:
        JSON with indexing results
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
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
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
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
    finally:
        # ✅ Guaranteed cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass

# ============================================================================
# ENDPOINT 5: INDEX SYNERGY SESSIONS
# ============================================================================

@universal_search_bp.route('/index-synergy', methods=['POST'])
@require_auth
def index_synergy_for_search():
    """
    Generate embeddings and FTS tokens for Synergy sessions
    
    ✅ FIXED: Proper cursor management with finally block
    
    Returns:
        JSON with indexing results
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
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
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
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
    finally:
        # ✅ Guaranteed cleanup
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass

# ============================================================================
# EXPORT BLUEPRINT
# ============================================================================

print('✅ Universal Search routes loaded')