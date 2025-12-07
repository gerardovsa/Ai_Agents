"""
FILE: AI_infrastructure/routes/search_routes.py
PURPOSE: Supabase full-text and semantic search API endpoints

DEPENDENCIES:
- flask - Blueprint routing
- psycopg2 - PostgreSQL database operations
- openai - Generate embeddings for semantic search

EXPORTS:
- search_bp - Flask Blueprint with search endpoints

USED BY:
- AI_infrastructure/flask_app.py (register blueprint)
- UI (frontend search bar)

NOTES:
- Full-text search uses PostgreSQL tsvector/GIN indexes
- Semantic search uses pgvector embeddings (1536 dimensions)
- All search functions created by supabase_search_core.sql

LAST MODIFIED: 2025-11-25 - Initial creation
"""

from flask import Blueprint, request, jsonify
from shared.database_utils import get_database_connection
import logging

logger = logging.getLogger(__name__)

search_bp = Blueprint('search', __name__)


@search_bp.route('/api/search/unified', methods=['GET'])
def unified_search():
    """
    Search across all tables (threads, messages, synergy sessions, docs)
    
    Query params:
        q: Search query (required)
        user_id: User ID for filtering (default: 1)
        limit: Max results (default: 50)
    
    Returns:
        {
            "success": true,
            "query": "search terms",
            "results": [
                {
                    "source": "thread",
                    "id": 123,
                    "title": "Thread title",
                    "content_preview": "First 100 chars...",
                    "rank": 0.85,
                    "created_at": "2025-11-25T10:30:00Z"
                }
            ],
            "count": 42
        }
    """
    conn = None
    try:
        query = request.args.get('q', '').strip()
        user_id = request.args.get('user_id', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter "q" is required'
            }), 400
        
        if limit > 200:
            limit = 200  # Cap at 200 for performance
        
        conn = get_database_connection('sessions')  # Function is in public schema
        cursor = conn.cursor()
        
        # Call unified search function
        cursor.execute("""
            SELECT * FROM public.unified_search(%s, %s, %s)
        """, (query, user_id, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'source': row['source'] if isinstance(row, dict) else row[0],
                'id': row['id'] if isinstance(row, dict) else row[1],
                'title': row['title'] if isinstance(row, dict) else row[2],
                'content_preview': row['content_preview'] if isinstance(row, dict) else row[3],
                'rank': float(row['rank']) if isinstance(row, dict) else float(row[4]),
                'created_at': row['created_at'].isoformat() if isinstance(row, dict) else row[5].isoformat()
            })
        
        logger.info(f"Unified search '{query}' returned {len(results)} results")
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error in unified search: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()


@search_bp.route('/api/search/threads', methods=['GET'])
def search_threads():
    """
    Search threads only
    
    Query params:
        q: Search query (required)
        user_id: User ID for filtering (default: 1)
        limit: Max results (default: 50)
    
    Returns:
        {
            "success": true,
            "results": [...]
        }
    """
    conn = None
    try:
        query = request.args.get('q', '').strip()
        user_id = request.args.get('user_id', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter "q" is required'
            }), 400
        
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM sessions.search_threads(%s, %s, %s)
        """, (query, user_id, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'] if isinstance(row, dict) else row[0],
                'thread_slug': row['thread_slug'] if isinstance(row, dict) else row[1],
                'name': row['name'] if isinstance(row, dict) else row[2],
                'rank': float(row['rank']) if isinstance(row, dict) else float(row[3])
            })
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error searching threads: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()


@search_bp.route('/api/search/messages', methods=['GET'])
def search_messages():
    """Search messages only"""
    conn = None
    try:
        query = request.args.get('q', '').strip()
        user_id = request.args.get('user_id', 1, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter "q" is required'
            }), 400
        
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM sessions.search_messages(%s, %s, %s)
        """, (query, user_id, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'message_id': row['message_id'] if isinstance(row, dict) else row[0],
                'thread_id': row['thread_id'] if isinstance(row, dict) else row[1],
                'role': row['role'] if isinstance(row, dict) else row[2],
                'content': row['content'] if isinstance(row, dict) else row[3],
                'created_at': row['created_at'].isoformat() if isinstance(row, dict) else row[4].isoformat(),
                'rank': float(row['rank']) if isinstance(row, dict) else float(row[5])
            })
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()


@search_bp.route('/api/search/semantic', methods=['POST'])
def semantic_search():
    """
    Semantic similarity search using embeddings
    
    Request body:
        {
            "query": "text to search for",
            "table": "threads|messages|synergy|docs",
            "user_id": 1,
            "threshold": 0.7,
            "limit": 10
        }
    
    Returns similar results based on embedding distance
    """
    conn = None
    try:
        data = request.get_json()
        query_text = data.get('query', '').strip()
        table = data.get('table', 'threads')
        user_id = data.get('user_id', 1)
        threshold = data.get('threshold', 0.7)
        limit = data.get('limit', 10)
        
        if not query_text:
            return jsonify({
                'success': False,
                'error': 'Query text is required'
            }), 400
        
        # Generate embedding for query
        try:
            from config import get_api_key_enhanced
            import openai
            
            api_key = get_api_key_enhanced('openai')
            if not api_key:
                return jsonify({
                    'success': False,
                    'error': 'OpenAI API key not configured'
                }), 500
            
            client = openai.OpenAI(api_key=api_key)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=query_text[:8000]
            )
            
            query_embedding = response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return jsonify({
                'success': False,
                'error': f'Failed to generate embedding: {str(e)}'
            }), 500
        
        # Call appropriate similarity search function
        if table == 'threads':
            conn = get_database_connection('sessions')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sessions.search_similar_threads(%s::vector, %s, %s, %s)
            """, (query_embedding, user_id, threshold, limit))
        elif table == 'messages':
            conn = get_database_connection('sessions')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sessions.search_similar_messages(%s::vector, %s, %s, %s)
            """, (query_embedding, user_id, threshold, limit))
        elif table == 'synergy':
            conn = get_database_connection('synergy_sessions')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM synergy_sessions.search_similar_sessions(%s::vector, %s, %s, %s)
            """, (query_embedding, user_id, threshold, limit))
        elif table == 'docs':
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM ai_infrastructure.search_similar_docs(%s::vector, %s, %s)
            """, (query_embedding, threshold, limit))
        else:
            return jsonify({
                'success': False,
                'error': f'Invalid table: {table}'
            }), 400
        
        results = []
        for row in cursor.fetchall():
            # Convert to dict (format varies by table)
            result = {}
            if isinstance(row, dict):
                result = dict(row)
            else:
                # Generic conversion for tuple results
                result = {
                    'similarity': float(row[-1])  # Last column is always similarity
                }
            
            results.append(result)
        
        return jsonify({
            'success': True,
            'query': query_text,
            'table': table,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()


@search_bp.route('/api/search/stats', methods=['GET'])
def search_stats():
    """
    Get search system statistics
    
    Returns:
        {
            "success": true,
            "stats": {
                "threads": {"total": 100, "with_embeddings": 80},
                "messages": {"total": 500, "with_embeddings": 400},
                ...
            }
        }
    """
    conn = None
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        stats = {}
        
        # Threads stats
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(name_embedding) as with_embeddings
            FROM sessions.threads
            WHERE user_id = %s
        """, (user_id,))
        row = cursor.fetchone()
        stats['threads'] = {
            'total': row['total'] if isinstance(row, dict) else row[0],
            'with_embeddings': row['with_embeddings'] if isinstance(row, dict) else row[1]
        }
        
        # Messages stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(m.content_embedding) as with_embeddings
            FROM sessions.messages m
            JOIN sessions.threads t ON m.thread_id = t.id
            WHERE t.user_id = %s
        """, (user_id,))
        row = cursor.fetchone()
        stats['messages'] = {
            'total': row['total'] if isinstance(row, dict) else row[0],
            'with_embeddings': row['with_embeddings'] if isinstance(row, dict) else row[1]
        }
        
        conn.close()
        
        # Synergy sessions stats
        conn = get_database_connection('synergy_sessions')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(title_embedding) as with_embeddings
            FROM synergy_sessions.sessions
            WHERE user_id = %s
        """, (user_id,))
        row = cursor.fetchone()
        stats['synergy_sessions'] = {
            'total': row['total'] if isinstance(row, dict) else row[0],
            'with_embeddings': row['with_embeddings'] if isinstance(row, dict) else row[1]
        }
        
        conn.close()
        
        # Internal docs stats
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(content_embedding) as with_embeddings
            FROM ai_infrastructure.internal_docs
        """)
        row = cursor.fetchone()
        stats['internal_docs'] = {
            'total': row['total'] if isinstance(row, dict) else row[0],
            'with_embeddings': row['with_embeddings'] if isinstance(row, dict) else row[1]
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting search stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()
