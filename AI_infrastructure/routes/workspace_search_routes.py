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
from functools import wraps
from typing import Dict, Any

# Import tool implementations
from tools.implementations.workspace_search import (
    workspace_simple_search,
    workspace_semantic_search,
    workspace_get_messages,
    workspace_get_transcriptions
)

# Create Blueprint
workspace_search_bp = Blueprint('workspace_search', __name__)


def require_auth(f):
    """
    Decorator to require authentication for routes
    Checks for valid session or API key
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For now, just pass through - implement proper auth as needed
        # In production, check session['user_id'] or validate API key
        return f(*args, **kwargs)
    return decorated_function


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
        
        # Get user from session (implement proper session handling)
        # user_id = session.get('user_id')
        user_id = data.get('user_id')  # For now, allow from request
        
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
        
        # Get user from session
        user_id = data.get('user_id')
        
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


# Export blueprint
__all__ = ['workspace_search_bp']
