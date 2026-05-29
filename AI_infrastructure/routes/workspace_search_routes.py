"""
Workspace Search and Message Retrieval Routes

REST API endpoints for searching workspace messages and transcriptions,
and retrieving messages/transcriptions with flexible filtering.

Routes:
- POST   /api/v1/workspace/search            - Simple keyword search
- POST   /api/v1/workspace/semantic-search   - AI-powered semantic search  
- POST   /api/v1/workspace/messages          - Get messages with filters
- POST   /api/v1/workspace/transcriptions    - Get transcriptions with filters

LAST MODIFIED: 2025-12-08
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from flask import Blueprint, request, jsonify
from typing import Dict, Any

# Import tool implementations
from tools.implementations.workspace_search import (
    workspace_simple_search,
    workspace_semantic_search,
    workspace_get_messages,
    workspace_get_transcriptions
)

# Import real authentication decorator
from AI_infrastructure.auth.user_auth import require_auth

# Create Blueprint
workspace_search_bp = Blueprint('workspace_search', __name__)


def get_user_workspaces(user_id: int) -> list:
    """
    Get list of workspace IDs the user has access to
    
    Args:
        user_id: User ID from session
        
    Returns:
        List of workspace IDs
    """
    # TODO: Implement proper workspace access check
    # For now, return None (searches all workspaces)
    return None


@workspace_search_bp.route('/api/v1/workspace/search', methods=['POST'])
@require_auth
def simple_search():
    """
    Fast keyword search across messages and transcriptions
    
    Request Body:
        {
            "search_query": "database performance",
            "workspace_ids": [1, 2, 3],  // Optional
            "user_id": 5,                 // Optional
            "search_messages": true,      // Optional, default: true
            "search_transcriptions": true, // Optional, default: true
            "limit": 50                   // Optional, default: 50
        }
        
    Response:
        {
            "success": true,
            "results": {
                "messages": [...],
                "transcriptions": [...]
            },
            "total_count": 45,
            "query": "database performance",
            "search_type": "simple"
        }
    """
    try:
        data = request.get_json()
        
        # Validate required parameters
        if not data or 'search_query' not in data:
            return jsonify({
                'success': False,
                'error': 'search_query is required'
            }), 400
        
        # Extract user ID from validated JWT token (set by @require_auth decorator)
        user_id = request.user.get('user_id') if hasattr(request, 'user') else None
        
        # Get workspace filter (optional)
        workspace_ids = data.get('workspace_ids')
        
        # Call tool implementation
        result = workspace_simple_search(
            search_query=data['search_query'],
            workspace_ids=workspace_ids,
            user_id=user_id,
            search_messages=data.get('search_messages', True),
            search_transcriptions=data.get('search_transcriptions', True),
            limit=data.get('limit', 50)
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Search failed: {str(e)}"
        }), 500


@workspace_search_bp.route('/api/v1/workspace/semantic-search', methods=['POST'])
@require_auth
def semantic_search():
    """
    AI-powered semantic search using embeddings
    
    Request Body:
        {
            "search_query": "Tell me about pricing discussions",
            "workspace_ids": [1, 2, 3],   // Optional
            "user_id": 5,                  // Optional
            "similarity_threshold": 0.7,   // Optional, default: 0.7
            "limit": 20                    // Optional, default: 20
        }
        
    Response:
        {
            "success": true,
            "results": [
                {
                    "id": 12345,
                    "content": "...",
                    "similarity_score": 0.89,
                    "workspace_name": "Engineering",
                    "user_name": "sarah",
                    "created_at": "2025-12-01T10:30:00"
                }
            ],
            "total_count": 15,
            "query": "pricing discussions",
            "search_type": "semantic"
        }
    """
    try:
        data = request.get_json()
        
        # Validate required parameters
        if not data or 'search_query' not in data:
            return jsonify({
                'success': False,
                'error': 'search_query is required'
            }), 400
        
        # Extract user from JWT (set by @require_auth) — not request body (prevents spoofing)
        user_id = request.user.get('user_id') if hasattr(request, 'user') else None
        
        # Get workspace filter
        workspace_ids = data.get('workspace_ids')
        
        # Call tool implementation
        result = workspace_semantic_search(
            search_query=data['search_query'],
            workspace_ids=workspace_ids,
            user_id=user_id,
            similarity_threshold=data.get('similarity_threshold', 0.7),
            limit=data.get('limit', 20)
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            # If semantic search fails, suggest fallback
            status_code = 503 if 'pgvector' in result.get('error', '') else 400
            return jsonify(result), status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Semantic search failed: {str(e)}",
            'fallback': 'Use /api/v1/workspace/search for keyword-based search'
        }), 500


@workspace_search_bp.route('/api/v1/workspace/messages', methods=['POST'])
@require_auth
def get_messages():
    """
    Retrieve messages with flexible filtering
    
    Request Body:
        {
            "workspace_ids": [1, 2, 3],   // Optional
            "thread_id": 42,               // Optional
            "session_id": 789,             // Optional
            "user_id": 5,                  // Optional
            "role": "assistant",           // Optional: user, assistant, system
            "date_from": "2025-12-01",     // Optional: YYYY-MM-DD
            "date_to": "2025-12-07",       // Optional: YYYY-MM-DD
            "limit": 100,                  // Optional, default: 100
            "offset": 0                    // Optional, default: 0
        }
        
    Response:
        {
            "success": true,
            "messages": [...],
            "total_count": 87,
            "returned_count": 50,
            "limit": 100,
            "offset": 0,
            "has_more": true
        }
    """
    try:
        data = request.get_json() or {}
        
        # Call tool implementation
        result = workspace_get_messages(
            workspace_ids=data.get('workspace_ids'),
            thread_id=data.get('thread_id'),
            session_id=data.get('session_id'),
            user_id=data.get('user_id'),
            role=data.get('role'),
            date_from=data.get('date_from'),
            date_to=data.get('date_to'),
            limit=data.get('limit', 100),
            offset=data.get('offset', 0)
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Message retrieval failed: {str(e)}"
        }), 500


@workspace_search_bp.route('/api/v1/workspace/transcriptions', methods=['POST'])
@require_auth
def get_transcriptions():
    """
    Retrieve transcriptions with flexible filtering
    
    Request Body:
        {
            "workspace_ids": [1, 2, 3],        // Optional
            "session_id": 789,                  // Optional
            "user_id": 5,                       // Optional
            "transcription_mode": "whisper",    // Optional: web_speech, whisper, hybrid
            "date_from": "2025-12-01",          // Optional: YYYY-MM-DD
            "date_to": "2025-12-07",            // Optional: YYYY-MM-DD
            "min_duration": 120,                // Optional: seconds
            "max_duration": 600,                // Optional: seconds
            "limit": 50,                        // Optional, default: 50
            "offset": 0                         // Optional, default: 0
        }
        
    Response:
        {
            "success": true,
            "transcriptions": [...],
            "total_count": 23,
            "returned_count": 20,
            "limit": 50,
            "offset": 0,
            "has_more": false
        }
    """
    try:
        data = request.get_json() or {}
        
        # Call tool implementation
        result = workspace_get_transcriptions(
            workspace_ids=data.get('workspace_ids'),
            session_id=data.get('session_id'),
            user_id=data.get('user_id'),
            transcription_mode=data.get('transcription_mode'),
            date_from=data.get('date_from'),
            date_to=data.get('date_to'),
            min_duration=data.get('min_duration'),
            max_duration=data.get('max_duration'),
            limit=data.get('limit', 50),
            offset=data.get('offset', 0)
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Transcription retrieval failed: {str(e)}"
        }), 500


@workspace_search_bp.route('/api/workspace/global-search', methods=['POST'])
@require_auth
def global_workspace_search():
    """
    🌍 Global Search Across All User Workspaces
    
    Search across ALL workspaces and threads a user has access to.
    Returns hierarchical results: workspaces → threads → messages
    
    Request Body:
    {
        "query": "search term",
        "mode": "simple" | "semantic",
        "user_id": 123  # Optional, extracted from session
    }
    
    Response:
    {
        "success": true,
        "total_results": 42,
        "workspaces": [
            {
                "id": 1,
                "name": "MustCare",
                "slug": "mustcare",
                "hit_count": 15,
                "threads": [
                    {
                        "id": 123,
                        "name": "Appointment System",
                        "slug": "appointment-system",
                        "message_count": 5,
                        "last_message_at": "2025-12-09T10:30:00Z",
                        "messages": [
                            {
                                "id": 456,
                                "role": "user",
                                "content": "How do I schedule...",
                                "created_at": "2025-12-09T10:25:00Z",
                                "similarity": 0.89  # Only for semantic search
                            }
                        ]
                    }
                ]
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        query = data.get('query', '').strip()
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter is required'
            }), 400
        
        mode = data.get('mode', 'simple').lower()
        if mode not in ['simple', 'semantic']:
            mode = 'simple'
        
        # Extract user from JWT (set by @require_auth) — not request body (prevents spoofing)
        user_id = request.user.get('user_id') if hasattr(request, 'user') else None
        
        # Get connection
        from tools.implementations.workspace_search import get_database_connection
        conn = get_database_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        try:
            if mode == 'simple':
                # Simple keyword search across all workspaces
                sql = """
                    SELECT 
                        w.id as workspace_id,
                        w.name as workspace_name,
                        w.slug as workspace_slug,
                        t.id as thread_id,
                        t.name as thread_name,
                        t.slug as thread_slug,
                        t.updated_at as last_message_at,
                        m.id as message_id,
                        m.role,
                        m.content,
                        m.created_at
                    FROM workspace_chats.messages m
                    JOIN workspace_chats.workspaces w ON m.workspace_id = w.id
                    LEFT JOIN workspace_chats.threads t ON m.thread_id = t.id
                    WHERE m.content ILIKE %s
                """
                
                params = [f'%{query}%']
                
                if user_id:
                    sql += " AND m.user_id = %s"
                    params.append(user_id)
                
                sql += " ORDER BY w.name, t.name, m.created_at DESC LIMIT 200"
                
                cursor.execute(sql, params)
                
            else:  # semantic search
                # Generate embedding for query
                from tools.implementations.workspace_search import generate_embedding
                
                embedding = generate_embedding(query, user_id=user_id)
                if not embedding:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to generate embedding for query'
                    }), 500
                
                # Semantic search across all workspaces
                sql = """
                    SELECT 
                        w.id as workspace_id,
                        w.name as workspace_name,
                        w.slug as workspace_slug,
                        t.id as thread_id,
                        t.name as thread_name,
                        t.slug as thread_slug,
                        t.updated_at as last_message_at,
                        m.id as message_id,
                        m.role,
                        m.content,
                        m.created_at,
                        1 - (m.embedding_vector <=> %s::vector) as similarity
                    FROM workspace_chats.messages m
                    JOIN workspace_chats.workspaces w ON m.workspace_id = w.id
                    LEFT JOIN workspace_chats.threads t ON m.thread_id = t.id
                    WHERE m.embedding_vector IS NOT NULL
                      AND 1 - (m.embedding_vector <=> %s::vector) > 0.6
                """
                
                params = [embedding, embedding]
                
                if user_id:
                    sql += " AND m.user_id = %s"
                    params.append(user_id)
                
                sql += " ORDER BY similarity DESC LIMIT 200"
                
                cursor.execute(sql, params)
            
            rows = cursor.fetchall()
            
            # Group results by workspace and thread
            workspaces_dict = {}
            
            for row in rows:
                workspace_id = row[0]
                workspace_name = row[1]
                workspace_slug = row[2]
                thread_id = row[3]
                thread_name = row[4] or "Main Chat"
                thread_slug = row[5] or "main"
                last_message_at = row[6]
                message_id = row[7]
                role = row[8]
                content = row[9]
                created_at = row[10]
                similarity = row[11] if mode == 'semantic' else None
                
                # Initialize workspace if not exists
                if workspace_id not in workspaces_dict:
                    workspaces_dict[workspace_id] = {
                        'id': workspace_id,
                        'name': workspace_name,
                        'slug': workspace_slug,
                        'hit_count': 0,
                        'threads': {}
                    }
                
                # Initialize thread if not exists
                if thread_id not in workspaces_dict[workspace_id]['threads']:
                    workspaces_dict[workspace_id]['threads'][thread_id] = {
                        'id': thread_id,
                        'name': thread_name,
                        'slug': thread_slug,
                        'last_message_at': str(last_message_at) if last_message_at else None,
                        'message_count': 0,
                        'messages': []
                    }
                
                # Add message to thread
                message_obj = {
                    'id': message_id,
                    'role': role,
                    'content': content,
                    'created_at': str(created_at) if created_at else None
                }
                
                if similarity is not None:
                    message_obj['similarity'] = float(similarity)
                
                workspaces_dict[workspace_id]['threads'][thread_id]['messages'].append(message_obj)
                workspaces_dict[workspace_id]['threads'][thread_id]['message_count'] += 1
                workspaces_dict[workspace_id]['hit_count'] += 1
            
            # Convert to list format
            workspaces_list = []
            total_results = 0
            
            for workspace_id, workspace_data in workspaces_dict.items():
                threads_list = []
                
                for thread_id, thread_data in workspace_data['threads'].items():
                    threads_list.append(thread_data)
                    total_results += thread_data['message_count']
                
                workspace_data['threads'] = threads_list
                workspaces_list.append(workspace_data)
            
            # Sort workspaces by hit count (descending)
            workspaces_list.sort(key=lambda x: x['hit_count'], reverse=True)
            
            return jsonify({
                'success': True,
                'total_results': total_results,
                'workspaces': workspaces_list,
                'query': query,
                'mode': mode
            }), 200
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        import traceback
        print(f"❌ Global search error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f"Global search failed: {str(e)}"
        }), 500


# Export blueprint
__all__ = ['workspace_search_bp']
