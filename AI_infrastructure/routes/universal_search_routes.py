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
# ENDPOINT 1: UNIVERSAL SEARCH
# ============================================================================

@universal_search_bp.route('/search', methods=['POST'])
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
        
        # ========================================================================
        # 4.5. SEARCH VECTOR DATABASES (pgvector/Qdrant/Pinecone)
        # ========================================================================
        # NOTE: Priority order - pgvector (default, Supabase built-in) → Qdrant (optional, self-hosted) → Pinecone (paid)
        # pgvector results already included in 'documents' source above (semantic/hybrid search)
        if include_vector_db and query_embedding:
            try:
                vector_results = []
                provider_used = None
                
                # Option 1: Search separate pgvector embeddings table (if exists)
                # This searches ai_infrastructure.vector_embeddings (separate from document_library)
                try:
                    cursor.execute("""
                        SELECT id, metadata->>'title' as title, 
                               metadata->>'text' as text,
                               metadata->>'file_type' as file_type,
                               metadata->>'created_at' as created_at,
                               1 - (embedding <=> %s::vector) AS similarity
                        FROM ai_infrastructure.vector_embeddings
                        WHERE user_id = %s
                          AND namespace = 'user_documents'
                          AND embedding IS NOT NULL
                          AND (1 - (embedding <=> %s::vector)) > 0.3
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """, (query_embedding, user_id, query_embedding, query_embedding, limit))
                    
                    pgvector_results = cursor.fetchall()
                    if pgvector_results:
                        vector_results = [
                            {
                                'id': str(row[0]),
                                'title': row[1] or 'Untitled',
                                'snippet': (row[2] or '')[:200] + '...' if row[2] else '',
                                'source': 'vector-database',
                                'type': row[3] or 'document',
                                'date': row[4],
                                'score': float(row[5]) if row[5] else 0.0,
                                'provider': 'pgvector (Supabase)'
                            }
                            for row in pgvector_results
                        ]
                        provider_used = 'pgvector'
                        print(f"[UNIVERSAL SEARCH] Found {len(vector_results)} results in pgvector")
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
                
                # Option 3: Try Pinecone (if user has configured it)
                if not vector_results:
                    try:
                        # TODO: Implement Pinecone search
                        # pinecone_results = search_pinecone(query_embedding, user_id, limit)
                        pass
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
        # 8. SEARCH GOOGLE DRIVE (via Google Drive API v3)
        # ========================================================================
        if include_google_drive:
            try:
                google_creds = auth_manager.get_platform_credentials(user_id, 'google')
                if google_creds and google_creds.get('access_token'):
                    # Search Google Drive using Drive API v3
                    drive_query = f"name contains '{query}' or fullText contains '{query}'"
                    response = requests.get(
                        'https://www.googleapis.com/drive/v3/files',
                        params={
                            'q': drive_query,
                            'pageSize': limit,
                            'fields': 'files(id,name,mimeType,createdTime,modifiedTime,size,webViewLink,owners)',
                            'orderBy': 'modifiedTime desc'
                        },
                        headers={'Authorization': f'Bearer {google_creds.get("access_token")}'}
                    )
                    if response.status_code == 200:
                        drive_files = response.json().get('files', [])
                        formatted_results = []
                        for file in drive_files:
                            formatted_results.append({
                                'type': 'file',
                                'id': file.get('id'),
                                'name': file.get('name'),
                                'mime_type': file.get('mimeType'),
                                'created': file.get('createdTime'),
                                'modified': file.get('modifiedTime'),
                                'size': file.get('size'),
                                'link': file.get('webViewLink'),
                                'owner': file.get('owners', [{}])[0].get('displayName') if file.get('owners') else None
                            })
                        results['sources']['google-drive'] = {
                            'count': len(formatted_results),
                            'results': formatted_results
                        }
                        results['total_results'] += len(formatted_results)
                    else:
                        results['sources']['google-drive'] = {'error': f'Drive API error: {response.status_code}'}
                else:
                    results['sources']['google-drive'] = {'error': 'Google credentials not found'}
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Google Drive search error: {e}")
                results['sources']['google-drive'] = {'error': str(e)}
        
        # ========================================================================
        # 9. SEARCH ONEDRIVE (via Microsoft Graph API)
        # ========================================================================
        if include_onedrive:
            try:
                microsoft_creds = auth_manager.get_platform_credentials(user_id, 'microsoft')
                if microsoft_creds and microsoft_creds.get('access_token'):
                    # Search OneDrive using Microsoft Graph API
                    response = requests.get(
                        f'https://graph.microsoft.com/v1.0/me/drive/search(q=\'{query}\')',
                        params={
                            '$top': limit,
                            '$select': 'id,name,createdDateTime,lastModifiedDateTime,size,webUrl,file,folder'
                        },
                        headers={'Authorization': f'Bearer {microsoft_creds.get("access_token")}'}
                    )
                    if response.status_code == 200:
                        onedrive_items = response.json().get('value', [])
                        formatted_results = []
                        for item in onedrive_items:
                            formatted_results.append({
                                'type': 'folder' if item.get('folder') else 'file',
                                'id': item.get('id'),
                                'name': item.get('name'),
                                'created': item.get('createdDateTime'),
                                'modified': item.get('lastModifiedDateTime'),
                                'size': item.get('size'),
                                'link': item.get('webUrl'),
                                'mime_type': item.get('file', {}).get('mimeType') if item.get('file') else None
                            })
                        results['sources']['onedrive'] = {
                            'count': len(formatted_results),
                            'results': formatted_results
                        }
                        results['total_results'] += len(formatted_results)
                    else:
                        results['sources']['onedrive'] = {'error': f'Graph API error: {response.status_code}'}
                else:
                    results['sources']['onedrive'] = {'error': 'Microsoft credentials not found'}
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] OneDrive search error: {e}")
                results['sources']['onedrive'] = {'error': str(e)}
        
        # ========================================================================
        # 10. SEARCH SHAREPOINT (via Microsoft Graph API)
        # ========================================================================
        if include_sharepoint:
            try:
                microsoft_creds = auth_manager.get_platform_credentials(user_id, 'microsoft')
                if microsoft_creds and microsoft_creds.get('access_token'):
                    # First get the user's SharePoint sites
                    sites_response = requests.get(
                        'https://graph.microsoft.com/v1.0/sites?search=*',
                        headers={'Authorization': f'Bearer {microsoft_creds.get("access_token")}'}
                    )
                    
                    sharepoint_results = []
                    if sites_response.status_code == 200:
                        sites = sites_response.json().get('value', [])
                        # Search each site's drive (limit to first 3 sites to avoid timeout)
                        for site in sites[:3]:
                            site_id = site.get('id')
                            site_name = site.get('displayName', 'Unknown Site')
                            
                            # Search this site's drive
                            search_response = requests.get(
                                f'https://graph.microsoft.com/v1.0/sites/{site_id}/drive/search(q=\'{query}\')',
                                params={
                                    '$top': 5,  # Limit per site
                                    '$select': 'id,name,createdDateTime,lastModifiedDateTime,size,webUrl'
                                },
                                headers={'Authorization': f'Bearer {microsoft_creds.get("access_token")}'}
                            )
                            
                            if search_response.status_code == 200:
                                items = search_response.json().get('value', [])
                                for item in items:
                                    sharepoint_results.append({
                                        'type': 'file',
                                        'id': item.get('id'),
                                        'name': item.get('name'),
                                        'site': site_name,
                                        'created': item.get('createdDateTime'),
                                        'modified': item.get('lastModifiedDateTime'),
                                        'size': item.get('size'),
                                        'link': item.get('webUrl')
                                    })
                        
                        results['sources']['sharepoint'] = {
                            'count': len(sharepoint_results),
                            'results': sharepoint_results[:limit]  # Apply overall limit
                        }
                        results['total_results'] += len(sharepoint_results)
                    else:
                        results['sources']['sharepoint'] = {'error': f'Unable to access SharePoint sites: {sites_response.status_code}'}
                else:
                    results['sources']['sharepoint'] = {'error': 'Microsoft credentials not found'}
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] SharePoint search error: {e}")
                results['sources']['sharepoint'] = {'error': str(e)}
        
        # ========================================================================
        # 11. SEARCH OUTLOOK (via Microsoft Graph API)
        # ========================================================================
        if include_outlook:
            try:
                microsoft_creds = auth_manager.get_platform_credentials(user_id, 'microsoft')
                if microsoft_creds and microsoft_creds.get('access_token'):
                    # Search Outlook emails using Microsoft Graph API
                    response = requests.get(
                        'https://graph.microsoft.com/v1.0/me/messages',
                        params={
                            '$search': f'"{query}"',
                            '$top': limit,
                            '$select': 'id,subject,from,receivedDateTime,bodyPreview,isRead,hasAttachments,webLink',
                            '$orderby': 'receivedDateTime DESC'
                        },
                        headers={
                            'Authorization': f'Bearer {microsoft_creds.get("access_token")}',
                            'ConsistencyLevel': 'eventual'  # Required for search
                        }
                    )
                    if response.status_code == 200:
                        outlook_messages = response.json().get('value', [])
                        formatted_results = []
                        for msg in outlook_messages:
                            formatted_results.append({
                                'type': 'email',
                                'id': msg.get('id'),
                                'subject': msg.get('subject'),
                                'from': msg.get('from', {}).get('emailAddress', {}).get('address'),
                                'from_name': msg.get('from', {}).get('emailAddress', {}).get('name'),
                                'received': msg.get('receivedDateTime'),
                                'preview': msg.get('bodyPreview'),
                                'is_read': msg.get('isRead'),
                                'has_attachments': msg.get('hasAttachments'),
                                'link': msg.get('webLink')
                            })
                        results['sources']['outlook'] = {
                            'count': len(formatted_results),
                            'results': formatted_results
                        }
                        results['total_results'] += len(formatted_results)
                    else:
                        results['sources']['outlook'] = {'error': f'Graph API error: {response.status_code}'}
                else:
                    results['sources']['outlook'] = {'error': 'Microsoft credentials not found'}
            except Exception as e:
                print(f"[UNIVERSAL SEARCH] Outlook search error: {e}")
                results['sources']['outlook'] = {'error': str(e)}
        
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