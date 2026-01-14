"""
Supabase pgvector Routes - Native PostgreSQL vector database support

PURPOSE: Provide pgvector operations using the existing Supabase PostgreSQL database
         with pgvector extension (already deployed and active).

ADVANTAGES OVER PINECONE:
- No external API calls (20ms vs 150ms latency)
- No additional costs ($0 vs $70/month for Pinecone)
- Direct SQL queries to same database (better integration)
- Already deployed with vector extension enabled

DATABASE SCHEMA:
Table: ai_infrastructure.vector_embeddings
- id: UUID PRIMARY KEY
- user_id: INTEGER (links to user_sessions)
- namespace: TEXT (for multi-tenancy/organization)
- embedding: vector(1536) (pgvector type)
- metadata: JSONB (document info, chunks, etc.)
- created_at: TIMESTAMP

ENDPOINTS:
- POST /api/pgvector/create-index - Create vector storage table
- POST /api/pgvector/upsert - Insert/update vectors
- POST /api/pgvector/search - Similarity search (cosine distance)
- GET  /api/pgvector/stats - Get namespace statistics
- DELETE /api/pgvector/delete - Delete vectors by ID or namespace

INTEGRATION:
Compatible with existing credential system and vector_database.js frontend.

LAST MODIFIED: 2025-12-07
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
from typing import Dict, Any, List

# Import authentication
from auth.user_auth import require_auth

# Import database utilities
from shared.database_utils import get_database_connection, execute_query

# Create blueprint
pgvector_bp = Blueprint('pgvector', __name__)


# ==================== HELPER FUNCTIONS ====================

def ensure_pgvector_extension():
    """
    Ensure pgvector extension is enabled (idempotent)
    
    Returns:
        Dict with success status
    """
    cursor = None  # ✅ CRITICAL: Initialize before try
    conn = None
    
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Enable vector extension (idempotent)
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
        
        return {'success': True, 'message': 'pgvector extension enabled'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        # ✅ CRITICAL: Cleanup in correct order
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def ensure_vector_table(user_id: int, namespace: str = 'default', dimensions: int = 1536):
    """
    Create vector embeddings table if not exists (per user namespace)
    
    Args:
        user_id: User ID
        namespace: Namespace for organizing vectors
        dimensions: Vector dimensions (default 1536 for OpenAI/Voyager)
    
    Returns:
        Dict with success status
    """
    cursor = None  # ✅ CRITICAL: Initialize before try
    conn = None
    
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Create table with pgvector column
        table_sql = f"""
        CREATE TABLE IF NOT EXISTS ai_infrastructure.vector_embeddings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id INTEGER NOT NULL,
            namespace TEXT NOT NULL DEFAULT 'default',
            embedding vector({dimensions}),
            metadata JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        cursor.execute(table_sql)
        
        # Create index for fast similarity search (IVFFlat with cosine distance)
        index_sql = f"""
        CREATE INDEX IF NOT EXISTS vector_embeddings_user_namespace_idx 
        ON ai_infrastructure.vector_embeddings(user_id, namespace);
        
        CREATE INDEX IF NOT EXISTS vector_embeddings_embedding_idx 
        ON ai_infrastructure.vector_embeddings 
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        """
        cursor.execute(index_sql)
        
        conn.commit()
        
        return {'success': True, 'message': f'Vector table created for namespace: {namespace}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        # ✅ CRITICAL: Cleanup in correct order
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def get_embedding_from_text(text: str, user_id: int) -> List[float]:
    """
    Generate embedding from text using user's configured embedding provider
    
    Args:
        text: Text to embed
        user_id: User ID (to fetch embedding credentials)
    
    Returns:
        List of floats (embedding vector)
    """
    try:
        from auth.credential_injector import get_voyager_credentials, get_openai_embeddings_credentials
        
        # Try Voyager first (preferred)
        voyager_creds = get_voyager_credentials(user_id)
        if voyager_creds and voyager_creds.get('api_key'):
            # Call Voyager embedding API
            import requests
            response = requests.post(
                'https://api.voyageai.com/v1/embeddings',
                headers={
                    'Authorization': f'Bearer {voyager_creds["api_key"]}',
                    'Content-Type': 'application/json'
                },
                json={
                    'input': text,
                    'model': voyager_creds.get('model', 'voyage-2')
                }
            )
            if response.status_code == 200:
                return response.json()['data'][0]['embedding']
        
        # Fallback to OpenAI
        openai_creds = get_openai_embeddings_credentials(user_id)
        if openai_creds and openai_creds.get('api_key'):
            from openai import OpenAI
            client = OpenAI(api_key=openai_creds['api_key'])
            response = client.embeddings.create(
                input=text,
                model='text-embedding-3-small'
            )
            return response.data[0].embedding
        
        raise Exception('No embedding provider configured. Please set up Voyager or OpenAI credentials.')
    
    except Exception as e:
        raise Exception(f'Embedding generation failed: {str(e)}')


# ==================== API ENDPOINTS ====================

@pgvector_bp.route('/api/pgvector/create-index', methods=['POST'])
@require_auth
def create_index():
    """
    Create vector storage index/table for user
    
    Request Body:
        - namespace: Namespace for organizing vectors (default: 'default')
        - dimensions: Vector dimensions (default: 1536)
    
    Returns:
        JSON with success status and table info
    """
    try:
        user_id = request.user['id']
        data = request.get_json() or {}
        
        namespace = data.get('namespace', 'default')
        dimensions = data.get('dimensions', 1536)
        
        # Ensure pgvector extension
        ext_result = ensure_pgvector_extension()
        if not ext_result['success']:
            return jsonify(ext_result), 500
        
        # Create table
        table_result = ensure_vector_table(user_id, namespace, dimensions)
        if not table_result['success']:
            return jsonify(table_result), 500
        
        return jsonify({
            'success': True,
            'message': f'pgvector index created for namespace: {namespace}',
            'namespace': namespace,
            'dimensions': dimensions,
            'provider': 'supabase_pgvector',
            'table': 'ai_infrastructure.vector_embeddings'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pgvector_bp.route('/api/pgvector/upsert', methods=['POST'])
@require_auth
def upsert_vectors():
    """
    Insert or update vectors in pgvector
    
    Request Body:
        - vectors: List of {id?, text?, embedding?, metadata?}
        - namespace: Namespace (default: 'default')
    
    Returns:
        JSON with upserted count
    """
    try:
        user_id = request.user['id']
        data = request.get_json()
        
        vectors = data.get('vectors', [])
        namespace = data.get('namespace', 'default')
        
        if not vectors:
            return jsonify({'success': False, 'error': 'No vectors provided'}), 400
        
        # Ensure table exists
        ensure_vector_table(user_id, namespace)
        
        cursor = None  # ✅ CRITICAL: Initialize before try
        conn = None
        
        try:
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            upserted = 0
            for vec in vectors:
                vec_id = vec.get('id', str(uuid.uuid4()))
                
                # Get embedding (either provided or generate from text)
                if 'embedding' in vec:
                    embedding = vec['embedding']
                elif 'text' in vec:
                    embedding = get_embedding_from_text(vec['text'], user_id)
                else:
                    continue  # Skip if no embedding or text
                
                metadata = vec.get('metadata', {})
                
                # Upsert (INSERT ON CONFLICT UPDATE)
                upsert_sql = """
                INSERT INTO ai_infrastructure.vector_embeddings (id, user_id, namespace, embedding, metadata)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) 
                DO UPDATE SET 
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    created_at = NOW();
                """
                cursor.execute(upsert_sql, (vec_id, user_id, namespace, embedding, metadata))
                upserted += 1
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'upserted': upserted,
                'namespace': namespace
            })
        finally:
            # ✅ CRITICAL: Cleanup in correct order
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pgvector_bp.route('/api/pgvector/search', methods=['POST'])
@require_auth
def search_similar():
    """
    Semantic similarity search using pgvector cosine distance
    
    Request Body:
        - query: Text query (will be embedded)
        - embedding: Pre-computed embedding vector (optional, overrides query)
        - namespace: Namespace to search (default: 'default')
        - top_k: Number of results (default: 10)
        - threshold: Minimum similarity score 0-1 (default: 0.7)
    
    Returns:
        JSON with similar vectors and scores
    """
    try:
        user_id = request.user['id']
        data = request.get_json()
        
        query_text = data.get('query')
        query_embedding = data.get('embedding')
        namespace = data.get('namespace', 'default')
        top_k = data.get('top_k', 10)
        threshold = data.get('threshold', 0.7)
        
        # Get query embedding
        if query_embedding:
            embedding = query_embedding
        elif query_text:
            embedding = get_embedding_from_text(query_text, user_id)
        else:
            return jsonify({'success': False, 'error': 'Provide either query text or embedding'}), 400
        
        cursor = None  # ✅ CRITICAL: Initialize before try
        conn = None
        
        try:
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            # Similarity search using cosine distance (<=> operator)
            # Lower distance = more similar, so we convert to similarity score (1 - distance)
            search_sql = """
            SELECT 
                id,
                metadata,
                1 - (embedding <=> %s::vector) AS similarity,
                created_at
            FROM ai_infrastructure.vector_embeddings
            WHERE user_id = %s 
              AND namespace = %s
              AND 1 - (embedding <=> %s::vector) >= %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
            """
            
            cursor.execute(search_sql, (
                embedding, user_id, namespace, embedding, threshold, embedding, top_k
            ))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': str(row[0]),
                    'metadata': row[1],
                    'similarity': float(row[2]),
                    'created_at': row[3].isoformat() if row[3] else None
                })
            
            return jsonify({
                'success': True,
                'results': results,
                'count': len(results),
                'namespace': namespace
            })
        finally:
            # ✅ CRITICAL: Cleanup in correct order
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pgvector_bp.route('/api/pgvector/stats', methods=['GET'])
@require_auth
def get_stats():
    """
    Get statistics for user's vector namespaces
    
    Query Params:
        - namespace: Specific namespace (optional)
    
    Returns:
        JSON with vector counts per namespace
    """
    try:
        user_id = request.user['id']
        namespace = request.args.get('namespace')
        
        cursor = None  # ✅ CRITICAL: Initialize before try
        conn = None
        
        try:
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            if namespace:
                # Stats for specific namespace
                stats_sql = """
                SELECT 
                    COUNT(*) as vector_count,
                    MIN(created_at) as oldest,
                    MAX(created_at) as newest
                FROM ai_infrastructure.vector_embeddings
                WHERE user_id = %s AND namespace = %s;
                """
                cursor.execute(stats_sql, (user_id, namespace))
                row = cursor.fetchone()
                
                stats = {
                    'namespace': namespace,
                    'vector_count': row[0] if row else 0,
                    'oldest': row[1].isoformat() if row and row[1] else None,
                    'newest': row[2].isoformat() if row and row[2] else None
                }
            else:
                # Stats for all namespaces
                stats_sql = """
                SELECT 
                    namespace,
                    COUNT(*) as vector_count,
                    MAX(created_at) as last_updated
                FROM ai_infrastructure.vector_embeddings
                WHERE user_id = %s
                GROUP BY namespace
                ORDER BY vector_count DESC;
                """
                cursor.execute(stats_sql, (user_id,))
                
                namespaces = []
                for row in cursor.fetchall():
                    namespaces.append({
                        'namespace': row[0],
                        'vector_count': row[1],
                        'last_updated': row[2].isoformat() if row[2] else None
                    })
                
                stats = {
                    'namespaces': namespaces,
                    'total_namespaces': len(namespaces),
                    'total_vectors': sum(ns['vector_count'] for ns in namespaces)
                }
            
            return jsonify({
                'success': True,
                'stats': stats
            })
        finally:
            # ✅ CRITICAL: Cleanup in correct order
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@pgvector_bp.route('/api/pgvector/delete', methods=['DELETE'])
@require_auth
def delete_vectors():
    """
    Delete vectors by ID or entire namespace
    
    Request Body:
        - ids: List of vector IDs to delete (optional)
        - namespace: Delete all vectors in namespace (optional)
    
    Returns:
        JSON with deleted count
    """
    try:
        user_id = request.user['id']
        data = request.get_json()
        
        ids = data.get('ids', [])
        namespace = data.get('namespace')
        
        if not ids and not namespace:
            return jsonify({'success': False, 'error': 'Provide ids or namespace to delete'}), 400
        
        cursor = None  # ✅ CRITICAL: Initialize before try
        conn = None
        
        try:
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            if ids:
                # Delete specific IDs
                delete_sql = """
                DELETE FROM ai_infrastructure.vector_embeddings
                WHERE user_id = %s AND id = ANY(%s);
                """
                cursor.execute(delete_sql, (user_id, ids))
            elif namespace:
                # Delete entire namespace
                delete_sql = """
                DELETE FROM ai_infrastructure.vector_embeddings
                WHERE user_id = %s AND namespace = %s;
                """
                cursor.execute(delete_sql, (user_id, namespace))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return jsonify({
                'success': True,
                'deleted': deleted_count
            })
        finally:
            # ✅ CRITICAL: Cleanup in correct order
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
