"""
Synergy Internal Docs Global Search Endpoint
Gap #8 Fix: Provides global search across all internal docs (Docs/Sheets)

Created: December 9, 2025
Purpose: Enable searching by title, content, session across all synergy files
"""

from flask import Blueprint, request, jsonify
from shared.database_utils import get_synergy_sessions_connection, convert_sql_placeholders
import json

synergy_search_bp = Blueprint('synergy_search', __name__)


@synergy_search_bp.route('/internal-docs/search', methods=['GET'])
def search_internal_docs():
    """
    Global search across all Synergy Internal Docs (Gap #8 solution).
    
    Query Parameters:
    - q (required): Search query string
    - doc_type (optional): Filter by doc_type ('richtext' or 'spreadsheet')
    - session_id (optional): Filter by session_id
    - limit (optional): Max results (default 50)
    
    Returns:
    {
        'success': True,
        'results': [
            {
                'doc_id': 'doc_xxx',
                'title': 'Document Title',
                'doc_type': 'richtext',
                'session_id': 'sess_xxx',
                'session_title': 'Session Title',
                'slug': 'document-title',
                'share_url': 'https://...',
                'created_at': '2025-12-09T10:00:00',
                'updated_at': '2025-12-09T10:30:00',
                'version': 3,
                'match_field': 'title'  # or 'content'
            }
        ],
        'query': 'search term',
        'count': 10
    }
    """
    cursor = None
    conn = None
    
    try:
        # Parse query parameters
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Missing required parameter: q (search query)'}), 400
        
        doc_type_filter = request.args.get('doc_type', '').strip()
        session_id_filter = request.args.get('session_id', '').strip()
        limit = int(request.args.get('limit', '50'))
        
        conn = get_synergy_sessions_connection()
        cursor = conn.cursor()
        
        # Build search query (searches title and content fields)
        # Using ILIKE for case-insensitive search (PostgreSQL)
        search_pattern = f'%{query}%'
        
        params = []
        where_clauses = ['(d.title ILIKE %s OR d.content ILIKE %s)']
        params.extend([search_pattern, search_pattern])
        
        # Add optional filters
        if doc_type_filter:
            where_clauses.append('d.doc_type = %s')
            params.append(doc_type_filter)
        
        if session_id_filter:
            where_clauses.append('d.session_id = %s')
            params.append(session_id_filter)
        
        where_sql = ' AND '.join(where_clauses)
        params.append(limit)
        
        # Execute search with JOIN to get session title
        sql = f"""
            SELECT 
                d.doc_id,
                d.title,
                d.doc_type,
                d.session_id,
                s.title as session_title,
                d.slug,
                d.share_url,
                d.created_at,
                d.updated_at,
                d.version,
                CASE 
                    WHEN d.title ILIKE %s THEN 'title'
                    ELSE 'content'
                END as match_field
            FROM synergy_sessions.synergy_internal_docs d
            LEFT JOIN synergy_sessions.synergy_sessions s 
                ON d.session_id = s.session_id
            WHERE {where_sql}
            ORDER BY 
                CASE WHEN d.title ILIKE %s THEN 1 ELSE 2 END,
                d.updated_at DESC
            LIMIT %s
        """
        
        # Add search_pattern twice more for match_field and ORDER BY
        final_params = [search_pattern] + params[:2] + params[2:] + [search_pattern]
        
        cursor.execute(sql, final_params)
        rows = cursor.fetchall()
        
        # Format results
        results = []
        for row in rows:
            results.append({
                'doc_id': row['doc_id'],
                'title': row['title'],
                'doc_type': row['doc_type'],
                'session_id': row['session_id'],
                'session_title': row['session_title'] or 'Untitled Session',
                'slug': row['slug'] or '',
                'share_url': row['share_url'] or '',
                'created_at': str(row['created_at']) if row['created_at'] else '',
                'updated_at': str(row['updated_at']) if row['updated_at'] else '',
                'version': row['version'] or 1,
                'match_field': row['match_field']
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'query': query,
            'count': len(results),
            'filters': {
                'doc_type': doc_type_filter or None,
                'session_id': session_id_filter or None
            }
        })
    
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    except Exception as e:
        print(f'[SYNERGY SEARCH ERROR] {str(e)}')
        return jsonify({'error': f'Search failed: {str(e)}'}), 500
    finally:
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


@synergy_search_bp.route('/internal-docs/recent', methods=['GET'])
def get_recent_internal_docs():
    """
    Get recently updated internal docs across all sessions.
    
    Query Parameters:
    - limit (optional): Max results (default 20)
    - doc_type (optional): Filter by doc_type
    
    Returns: Same format as search endpoint
    """
    cursor = None
    conn = None
    
    try:
        limit = int(request.args.get('limit', '20'))
        doc_type_filter = request.args.get('doc_type', '').strip()
        
        conn = get_synergy_sessions_connection()
        cursor = conn.cursor()
        
        params = []
        where_clause = ''
        
        if doc_type_filter:
            where_clause = 'WHERE d.doc_type = %s'
            params.append(doc_type_filter)
        
        params.append(limit)
        
        sql = f"""
            SELECT 
                d.doc_id,
                d.title,
                d.doc_type,
                d.session_id,
                s.title as session_title,
                d.slug,
                d.share_url,
                d.created_at,
                d.updated_at,
                d.version
            FROM synergy_sessions.synergy_internal_docs d
            LEFT JOIN synergy_sessions.synergy_sessions s 
                ON d.session_id = s.session_id
            {where_clause}
            ORDER BY d.updated_at DESC
            LIMIT %s
        """
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'doc_id': row['doc_id'],
                'title': row['title'],
                'doc_type': row['doc_type'],
                'session_id': row['session_id'],
                'session_title': row['session_title'] or 'Untitled Session',
                'slug': row['slug'] or '',
                'share_url': row['share_url'] or '',
                'created_at': str(row['created_at']) if row['created_at'] else '',
                'updated_at': str(row['updated_at']) if row['updated_at'] else '',
                'version': row['version'] or 1
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
    
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    except Exception as e:
        print(f'[SYNERGY RECENT ERROR] {str(e)}')
        return jsonify({'error': f'Failed to fetch recent docs: {str(e)}'}), 500
    finally:
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
