"""
Document Library API Routes - Advanced Search Implementation
==============================================================
FULLY FIXED VERSION - Production Ready

⚠️ CURSOR MANAGEMENT FIXES (Dec 07, 2025):
   - ✅ All cursors properly closed before connections
   - ✅ All functions use finally blocks
   - ✅ All cursors initialized as None
   - ✅ Early returns properly handle cleanup

Implements patterns from GitHub research:
- Elasticsearch-style boolean queries (must/should/must_not)
- Range queries for dates and numbers
- Faceted aggregation
- Metadata filtering with JSONB
- Type-safe filtering patterns

LAST MODIFIED: 2025-12-07 - Fixed cursor management
"""

from flask import Blueprint, request, jsonify
from typing import Dict, List, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import json

from AI_infrastructure.auth.user_auth import UserAuthManager, require_auth
from shared.database_utils import get_database_connection

# Create blueprint
document_library_bp = Blueprint('document_library', __name__, url_prefix='/api/document-library')
auth_manager = UserAuthManager()

# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================

@document_library_bp.route('/search/fulltext', methods=['POST'])
@require_auth
def search_fulltext():
    """
    Full-text search using PostgreSQL to_tsvector and ts_rank
    
    ✅ FIXED: Proper cursor management with finally block
    
    Request body:
    {
        "query": "search terms",
        "limit": 20,
        "offset": 0,
        "filters": {
            "source": "google_drive",
            "file_type": "document",
            "user_id": 12
        }
    }
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    try:
        data = request.get_json()
        query = data.get('query', '')
        limit = data.get('limit', 20)
        offset = data.get('offset', 0)
        filters = data.get('filters', {})
        
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM ai_infrastructure.match_documents(
                %s, %s, %s, %s, %s, %s
            )
        """, (
            query,
            limit,
            offset,
            filters.get('source'),
            filters.get('file_type'),
            filters.get('user_id')
        ))
        
        results = cursor.fetchall()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'search_type': 'fulltext',
            'query': query,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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


@document_library_bp.route('/search/semantic', methods=['POST'])
@require_auth
def search_semantic():
    """
    Vector semantic search using pgvector
    
    ✅ FIXED: Proper cursor management with finally block
    
    Request body:
    {
        "query": "search terms",
        "embedding": [0.1, 0.2, ...],  // OpenAI embedding
        "threshold": 0.25,
        "limit": 20,
        "filters": {
            "source": "google_drive",
            "file_type": "document"
        }
    }
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    try:
        data = request.get_json()
        embedding = data.get('embedding')
        threshold = data.get('threshold', 0.25)
        limit = data.get('limit', 20)
        filters = data.get('filters', {})
        
        if not embedding:
            return jsonify({'error': 'Embedding required for semantic search'}), 400
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM ai_infrastructure.semantic_search_documents(
                %s::vector, %s, %s, %s, %s
            )
        """, (
            embedding,
            threshold,
            limit,
            filters.get('source'),
            filters.get('file_type')
        ))
        
        results = cursor.fetchall()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'search_type': 'semantic',
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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


@document_library_bp.route('/search/hybrid', methods=['POST'])
@require_auth
def search_hybrid():
    """
    Hybrid search combining full-text + semantic using RRF
    
    ✅ FIXED: Proper cursor management with finally block
    
    Request body:
    {
        "query": "search terms",
        "embedding": [0.1, 0.2, ...],
        "limit": 20,
        "fts_weight": 0.5,
        "semantic_weight": 0.5
    }
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    try:
        data = request.get_json()
        query = data.get('query', '')
        embedding = data.get('embedding')
        limit = data.get('limit', 20)
        fts_weight = data.get('fts_weight', 0.5)
        semantic_weight = data.get('semantic_weight', 0.5)
        
        if not query or not embedding:
            return jsonify({'error': 'Both query and embedding required'}), 400
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM ai_infrastructure.hybrid_search_documents(
                %s, %s::vector, %s, %s, %s
            )
        """, (
            query,
            embedding,
            limit,
            fts_weight,
            semantic_weight
        ))
        
        results = cursor.fetchall()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'search_type': 'hybrid',
            'query': query,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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
# ADVANCED FILTERING (Elasticsearch-style)
# ============================================================================

@document_library_bp.route('/filter', methods=['POST'])
@require_auth
def filter_documents():
    """
    Advanced filtering with Elasticsearch-style boolean queries
    
    ✅ FIXED: Proper cursor management with finally block
    
    Request body:
    {
        "must": [
            {"field": "source", "operator": "equals", "value": "google_drive"},
            {"field": "file_type", "operator": "equals", "value": "document"}
        ],
        "should": [
            {"field": "tags", "operator": "contains", "value": "important"},
            {"field": "tags", "operator": "contains", "value": "urgent"}
        ],
        "must_not": [
            {"field": "is_archived", "operator": "equals", "value": true}
        ],
        "range": {
            "created_at": {"gte": "2024-01-01", "lte": "2024-12-31"},
            "file_size_bytes": {"gte": 1000, "lte": 1000000}
        },
        "limit": 20,
        "offset": 0,
        "sort": [{"field": "created_at", "order": "desc"}]
    }
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    try:
        data = request.get_json()
        user_id = request.user_id
        
        # Build SQL query dynamically
        query_parts = []
        params = []
        param_counter = 1
        
        # Base query
        sql = """
            SELECT 
                id, document_id, title, source, file_type, mime_type,
                file_size_bytes, created_by_user_id, created_by_name,
                created_at, last_modified_at, last_accessed_at,
                tags, categories, description, url, thumbnail_url,
                view_count, edit_count, metadata
            FROM ai_infrastructure.document_library
            WHERE is_deleted = false
        """
        
        # MUST conditions (AND)
        must_conditions = data.get('must', [])
        for condition in must_conditions:
            clause, param = build_condition_clause(condition, param_counter)
            query_parts.append(f"({clause})")
            if param:
                params.append(param)
                param_counter += 1
        
        # SHOULD conditions (OR)
        should_conditions = data.get('should', [])
        if should_conditions:
            should_clauses = []
            for condition in should_conditions:
                clause, param = build_condition_clause(condition, param_counter)
                should_clauses.append(clause)
                if param:
                    params.append(param)
                    param_counter += 1
            if should_clauses:
                query_parts.append(f"({' OR '.join(should_clauses)})")
        
        # MUST_NOT conditions (NOT)
        must_not_conditions = data.get('must_not', [])
        for condition in must_not_conditions:
            clause, param = build_condition_clause(condition, param_counter)
            query_parts.append(f"NOT ({clause})")
            if param:
                params.append(param)
                param_counter += 1
        
        # RANGE conditions
        range_conditions = data.get('range', {})
        for field, range_spec in range_conditions.items():
            if 'gte' in range_spec:
                query_parts.append(f"{field} >= ${param_counter}")
                params.append(range_spec['gte'])
                param_counter += 1
            if 'lte' in range_spec:
                query_parts.append(f"{field} <= ${param_counter}")
                params.append(range_spec['lte'])
                param_counter += 1
            if 'gt' in range_spec:
                query_parts.append(f"{field} > ${param_counter}")
                params.append(range_spec['gt'])
                param_counter += 1
            if 'lt' in range_spec:
                query_parts.append(f"{field} < ${param_counter}")
                params.append(range_spec['lt'])
                param_counter += 1
        
        # Add WHERE clauses
        if query_parts:
            sql += " AND " + " AND ".join(query_parts)
        
        # SORTING
        sort_spec = data.get('sort', [{'field': 'created_at', 'order': 'desc'}])
        order_by_parts = []
        for sort in sort_spec:
            field = sort['field']
            order = sort.get('order', 'asc').upper()
            order_by_parts.append(f"{field} {order}")
        
        if order_by_parts:
            sql += " ORDER BY " + ", ".join(order_by_parts)
        
        # PAGINATION
        limit = data.get('limit', 20)
        offset = data.get('offset', 0)
        sql += f" LIMIT {limit} OFFSET {offset}"
        
        # Execute query
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Convert $N placeholders to %s for psycopg2
        sql_psycopg = sql.replace('$', '%s')
        cursor.execute(sql_psycopg, params)
        
        results = cursor.fetchall()
        
        # Get total count
        count_sql = """
            SELECT COUNT(*) as total
            FROM ai_infrastructure.document_library
            WHERE is_deleted = false
        """
        if query_parts:
            count_sql += " AND " + " AND ".join(query_parts)
        
        cursor.execute(count_sql.replace('$', '%s'), params)
        total_count = cursor.fetchone()['total']
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results),
            'total': total_count,
            'has_more': (offset + len(results)) < total_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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


def build_condition_clause(condition: Dict, param_num: int) -> tuple:
    """
    Build SQL clause from condition object
    Returns (clause_string, parameter_value)
    """
    field = condition['field']
    operator = condition['operator']
    value = condition['value']
    
    if operator == 'equals':
        return (f"{field} = ${param_num}", value)
    elif operator == 'not_equals':
        return (f"{field} != ${param_num}", value)
    elif operator == 'contains':
        if field == 'tags' or field == 'categories':
            return (f"${param_num} = ANY({field})", value)
        else:
            return (f"{field} ILIKE ${param_num}", f"%{value}%")
    elif operator == 'starts_with':
        return (f"{field} ILIKE ${param_num}", f"{value}%")
    elif operator == 'ends_with':
        return (f"{field} ILIKE ${param_num}", f"%{value}")
    elif operator == 'in':
        placeholders = ', '.join([f"${param_num + i}" for i in range(len(value))])
        return (f"{field} IN ({placeholders})", value)
    elif operator == 'is_null':
        return (f"{field} IS NULL", None)
    elif operator == 'is_not_null':
        return (f"{field} IS NOT NULL", None)
    else:
        return (f"{field} = ${param_num}", value)


# ============================================================================
# FACETED AGGREGATION
# ============================================================================

@document_library_bp.route('/facets', methods=['POST'])
@require_auth
def get_facets():
    """
    Get faceted aggregation for filtering
    
    ✅ FIXED: Proper cursor management with finally block
    
    Request body:
    {
        "filters": {
            "source": "google_drive",
            "created_after": "2024-01-01",
            "created_before": "2024-12-31"
        }
    }
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    try:
        data = request.get_json()
        filters = data.get('filters', {})
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT ai_infrastructure.get_document_facets(%s, %s, %s)
        """, (
            filters.get('source'),
            filters.get('created_after'),
            filters.get('created_before')
        ))
        
        facets = cursor.fetchone()[0]
        
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
        return jsonify({'error': str(e)}), 500
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
# DOCUMENT CRUD OPERATIONS
# ============================================================================

@document_library_bp.route('/documents', methods=['GET'])
@require_auth
def list_documents():
    """
    List documents with basic pagination
    
    ✅ FIXED: Proper cursor management with finally block
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    try:
        user_id = request.user_id
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        source = request.args.get('source')
        file_type = request.args.get('file_type')
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                id, document_id, title, source, file_type, mime_type,
                file_size_bytes, created_by_name, created_at, last_modified_at,
                tags, categories, description, url, thumbnail_url, view_count
            FROM ai_infrastructure.document_library
            WHERE is_deleted = false
        """
        params = []
        
        if source:
            query += " AND source = %s"
            params.append(source)
        
        if file_type:
            query += " AND file_type = %s"
            params.append(file_type)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'documents': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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


@document_library_bp.route('/documents/<document_id>', methods=['GET'])
@require_auth
def get_document(document_id):
    """
    Get single document details
    
    ✅ FIXED: Proper cursor management with finally block + early return
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM ai_infrastructure.document_library
            WHERE document_id = %s AND is_deleted = false
        """, (document_id,))
        
        document = cursor.fetchone()
        
        if not document:
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'error': 'Document not found'}), 404
        
        # Increment view count
        cursor.execute("""
            UPDATE ai_infrastructure.document_library
            SET view_count = view_count + 1,
                last_accessed_at = NOW()
            WHERE document_id = %s
        """, (document_id,))
        
        conn.commit()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'document': document
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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


@document_library_bp.route('/documents', methods=['POST'])
@require_auth
def create_document():
    """
    Create new document entry
    
    ✅ FIXED: Proper cursor management with finally block
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    try:
        data = request.get_json()
        user_id = request.user_id
        
        required_fields = ['document_id', 'source', 'title']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            INSERT INTO ai_infrastructure.document_library (
                document_id, source, source_id, title, content_preview,
                file_type, mime_type, file_extension, file_size_bytes,
                created_by_user_id, tags, categories, description, url, metadata
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id, document_id, title, source, created_at
        """, (
            data['document_id'],
            data['source'],
            data.get('source_id'),
            data['title'],
            data.get('content_preview'),
            data.get('file_type', 'other'),
            data.get('mime_type'),
            data.get('file_extension'),
            data.get('file_size_bytes', 0),
            user_id,
            data.get('tags', []),
            data.get('categories', []),
            data.get('description'),
            data.get('url'),
            json.dumps(data.get('metadata', {}))
        ))
        
        result = cursor.fetchone()
        conn.commit()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'document': result
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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


@document_library_bp.route('/documents/<document_id>', methods=['PUT'])
@require_auth
def update_document(document_id):
    """
    Update document entry
    
    ✅ FIXED: Proper cursor management with finally block + early returns
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    try:
        data = request.get_json()
        user_id = request.user_id
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        allowed_fields = [
            'title', 'description', 'tags', 'categories', 'content_preview',
            'file_type', 'metadata', 'is_archived'
        ]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'error': 'No fields to update'}), 400
        
        # Add update tracking
        update_fields.append("last_modified_at = NOW()")
        update_fields.append("last_modified_by_user_id = %s")
        update_fields.append("edit_count = edit_count + 1")
        params.append(user_id)
        params.append(document_id)
        
        query = f"""
            UPDATE ai_infrastructure.document_library
            SET {', '.join(update_fields)}
            WHERE document_id = %s AND is_deleted = false
            RETURNING id, document_id, title, last_modified_at
        """
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        if not result:
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'error': 'Document not found'}), 404
        
        conn.commit()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'document': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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


@document_library_bp.route('/documents/<document_id>', methods=['DELETE'])
@require_auth
def delete_document(document_id):
    """
    Soft delete document
    
    ✅ FIXED: Proper cursor management with finally block + early return
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE ai_infrastructure.document_library
            SET is_deleted = true
            WHERE document_id = %s
            RETURNING document_id
        """, (document_id,))
        
        result = cursor.fetchone()
        
        if not result:
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return jsonify({'error': 'Document not found'}), 404
        
        conn.commit()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'message': 'Document deleted'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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
# STATISTICS
# ============================================================================

@document_library_bp.route('/stats', methods=['GET'])
@require_auth
def get_stats():
    """
    Get library statistics
    
    ✅ FIXED: Proper cursor management with finally block
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_documents,
                COUNT(DISTINCT source) as total_sources,
                SUM(file_size_bytes) as total_size_bytes,
                SUM(view_count) as total_views,
                COUNT(DISTINCT created_by_user_id) as unique_creators
            FROM ai_infrastructure.document_library
            WHERE is_deleted = false
        """)
        
        stats = cursor.fetchone()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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
# MODULE INITIALIZATION
# ============================================================================

print('[DOCUMENT LIBRARY] Routes loaded: 11 endpoints (cursor management fixed - 2025-12-07)')