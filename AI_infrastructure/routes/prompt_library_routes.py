"""
Prompt Library Routes - API endpoints for managing prompt injections

Endpoints:
- GET  /api/prompts/quick-actions - List quick action prompts
- GET  /api/prompts/library - List library prompts  
- GET  /api/prompts/user-custom - List user's custom prompts
- POST /api/prompts/user-custom - Create user custom prompt
- POST /api/prompts/preferences - Save prompt preference
- GET  /api/prompts/preferences/:name - Get saved preference
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging

from core.prompt_injection_manager import get_prompt_manager

logger = logging.getLogger(__name__)

prompt_routes = Blueprint('prompt_routes', __name__, url_prefix='/api/prompts')


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get user_id from JWT token or session
        # For now, we'll extract from request context
        user_id = request.headers.get('X-User-ID', 1)  # Default to user 1 for testing
        request.user_id = int(user_id)
        return f(*args, **kwargs)
    return decorated_function


@prompt_routes.route('/quick-actions', methods=['GET'])
def list_quick_actions():
    """
    List all quick action prompts
    
    Query params:
        category: Optional category filter (development, analysis, style, data, business, creative)
    
    Response:
        {
            "success": true,
            "quick_actions": [
                {
                    "key": "expert_coder",
                    "name": "Expert Coder",
                    "icon": "⚡",
                    "category": "development"
                },
                ...
            ]
        }
    """
    try:
        category = request.args.get('category', None)
        prompt_manager = get_prompt_manager()
        
        actions = prompt_manager.list_quick_actions(category=category)
        
        return jsonify({
            'success': True,
            'quick_actions': actions,
            'count': len(actions)
        })
    
    except Exception as e:
        logger.error(f"Error listing quick actions: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@prompt_routes.route('/library', methods=['GET'])
def list_library_prompts():
    """
    List all library prompts
    
    Query params:
        category: Optional category filter (development, data, creative)
    
    Response:
        {
            "success": true,
            "library_prompts": [
                {
                    "key": "system_architect",
                    "name": "System Architect",
                    "category": "development"
                },
                ...
            ]
        }
    """
    try:
        category = request.args.get('category', None)
        prompt_manager = get_prompt_manager()
        
        prompts = prompt_manager.list_library_prompts(category=category)
        
        return jsonify({
            'success': True,
            'library_prompts': prompts,
            'count': len(prompts)
        })
    
    except Exception as e:
        logger.error(f"Error listing library prompts: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@prompt_routes.route('/user-custom', methods=['GET'])
@require_auth
def list_user_custom_prompts():
    """
    List user's custom prompts
    
    Response:
        {
            "success": true,
            "custom_prompts": [
                {
                    "id": 1,
                    "name": "My Custom Prompt",
                    "category": "development",
                    "is_quick_action": false,
                    "created_at": "2025-11-12T10:00:00"
                },
                ...
            ]
        }
    """
    try:
        user_id = request.user_id
        prompt_manager = get_prompt_manager()
        
        prompts = prompt_manager.list_user_custom_prompts(user_id)
        
        return jsonify({
            'success': True,
            'custom_prompts': prompts,
            'count': len(prompts)
        })
    
    except Exception as e:
        logger.error(f"Error listing user custom prompts: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@prompt_routes.route('/user-custom', methods=['POST'])
@require_auth
def create_user_custom_prompt():
    """
    Create a user custom prompt
    
    Request body:
        {
            "name": "My Custom Prompt",
            "prompt_text": "Focus on X and Y...",
            "category": "development",
            "is_quick_action": false
        }
    
    Response:
        {
            "success": true,
            "prompt_id": 1,
            "message": "Custom prompt created"
        }
    """
    try:
        user_id = request.user_id
        data = request.json
        
        name = data.get('name')
        prompt_text = data.get('prompt_text')
        category = data.get('category', None)
        is_quick_action = data.get('is_quick_action', False)
        
        if not name or not prompt_text:
            return jsonify({
                'success': False,
                'error': 'name and prompt_text are required'
            }), 400
        
        prompt_manager = get_prompt_manager()
        prompt_id = prompt_manager.save_user_custom_prompt(
            user_id=user_id,
            name=name,
            prompt_text=prompt_text,
            category=category,
            is_quick_action=is_quick_action
        )
        
        return jsonify({
            'success': True,
            'prompt_id': prompt_id,
            'message': 'Custom prompt created'
        })
    
    except Exception as e:
        logger.error(f"Error creating user custom prompt: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@prompt_routes.route('/preferences', methods=['POST'])
@require_auth
def save_prompt_preference():
    """
    Save a prompt preference combination
    
    Request body:
        {
            "preference_name": "My Coding Setup",
            "quick_actions": ["expert_coder", "debugger"],
            "library_prompts": ["system_architect"],
            "custom_prompt": "Focus on TypeScript"
        }
    
    Response:
        {
            "success": true,
            "preference_id": 1,
            "message": "Prompt preference saved"
        }
    """
    try:
        user_id = request.user_id
        data = request.json
        
        preference_name = data.get('preference_name')
        quick_actions = data.get('quick_actions', [])
        library_prompts = data.get('library_prompts', [])
        custom_prompt = data.get('custom_prompt', None)
        
        if not preference_name:
            return jsonify({
                'success': False,
                'error': 'preference_name is required'
            }), 400
        
        prompt_manager = get_prompt_manager()
        pref_id = prompt_manager.save_prompt_preference(
            user_id=user_id,
            preference_name=preference_name,
            quick_actions=quick_actions,
            library_prompts=library_prompts,
            custom_prompt=custom_prompt
        )
        
        return jsonify({
            'success': True,
            'preference_id': pref_id,
            'message': 'Prompt preference saved'
        })
    
    except Exception as e:
        logger.error(f"Error saving prompt preference: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@prompt_routes.route('/preferences/<preference_name>', methods=['GET'])
@require_auth
def get_prompt_preference(preference_name):
    """
    Get a saved prompt preference
    
    Response:
        {
            "success": true,
            "preference": {
                "quick_actions": ["expert_coder"],
                "library_prompts": ["system_architect"],
                "custom_prompt": "Focus on TypeScript"
            }
        }
    """
    try:
        user_id = request.user_id
        prompt_manager = get_prompt_manager()
        
        preference = prompt_manager.get_prompt_preference(user_id, preference_name)
        
        if preference:
            return jsonify({
                'success': True,
                'preference': preference
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Preference not found'
            }), 404
    
    except Exception as e:
        logger.error(f"Error getting prompt preference: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@prompt_routes.route('/categories', methods=['GET'])
def list_categories():
    """
    List all available categories
    
    Response:
        {
            "success": true,
            "categories": [
                {
                    "id": "development",
                    "name": "Development",
                    "description": "Coding, debugging, code review"
                },
                ...
            ]
        }
    """
    categories = [
        {
            'id': 'development',
            'name': 'Development',
            'description': 'Coding, debugging, architecture, code review'
        },
        {
            'id': 'analysis',
            'name': 'Analysis',
            'description': 'Detailed analysis, step-by-step reasoning, critical thinking'
        },
        {
            'id': 'data',
            'name': 'Data & SQL',
            'description': 'SQL queries, data analysis, business intelligence'
        },
        {
            'id': 'style',
            'name': 'Communication Style',
            'description': 'Concise, ELI5, professional, technical'
        },
        {
            'id': 'business',
            'name': 'Business & Operations',
            'description': 'Quote assistance, efficiency optimization, operations'
        },
        {
            'id': 'creative',
            'name': 'Creative & Content',
            'description': 'Writing, email composition, technical documentation'
        }
    ]
    
    return jsonify({
        'success': True,
        'categories': categories
    })


# ==================== NEW DATABASE-BACKED ROUTES ====================

import sqlite3
from pathlib import Path
from shared.database_utils import get_database_connection, is_using_supabase, convert_sql_placeholders
from datetime import datetime
import psycopg2.extras

def get_db_connection():
    """Get database connection to ai_infrastructure.db"""
    root_dir = Path(__file__).parent.parent.parent
    conn = get_database_connection('ai_infrastructure')
    
    # Set row factory based on database type
    if is_using_supabase():
        # PostgreSQL: use RealDictCursor
        # Note: We need to return a cursor, not set row_factory
        pass  # Handled per-query
    else:
        # SQLite: use Row factory
        conn.row_factory = sqlite3.Row
    
    return conn


@prompt_routes.route('/library/db', methods=['GET'])
@require_auth
def list_prompts_from_db():
    """
    List all prompts from database for the authenticated user
    
    Query params:
    - category: Filter by category
    - type: Filter by type (quick_action, full_prompt)
    - visibility: Filter by visibility
    - search: Search in name, description, tags
    """
    try:
        user_id = request.user_id
        
        # Get query params
        category = request.args.get('category')
        prompt_type = request.args.get('type')
        visibility = request.args.get('visibility')
        search = request.args.get('search')
        
        # Build SQL query
        query = """
            SELECT 
                id, user_id, workspace_id, name, category, type,
                description, prompt_text, tags, visibility,
                usage_count, created_at, updated_at
            FROM ai_infrastructure.prompt_library
            WHERE user_id = %s
        """
        params = [user_id]
        
        # Add filters
        if category:
            query += " AND category = %s"
            params.append(category)
        
        if prompt_type:
            query += " AND type = %s"
            params.append(prompt_type)
        
        if visibility:
            query += " AND visibility = %s"
            params.append(visibility)
        
        if search:
            query += " AND (name LIKE %s OR description LIKE %s OR tags LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        query += " ORDER BY name ASC"
        
        # Execute query
        conn = get_db_connection()
        
        # Convert placeholders for PostgreSQL
        query, params = convert_sql_placeholders(query, tuple(params))
        
        # DatabaseConnection wrapper handles cursor type automatically
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to dict
        prompts = []
        for row in rows:
            prompts.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'workspace_id': row['workspace_id'],
                'name': row['name'],
                'category': row['category'],
                'type': row['type'],
                'description': row['description'],
                'prompt_text': row['prompt_text'],
                'tags': row['tags'],
                'visibility': row['visibility'],
                'usage_count': row['usage_count'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        
        conn.close()
        
        logger.info(f"Listed {len(prompts)} prompts for user {user_id}")
        
        return jsonify({
            'success': True,
            'prompts': prompts,
            'count': len(prompts)
        })
        
    except Exception as e:
        logger.error(f"Error in list_prompts_from_db: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@prompt_routes.route('/library/db', methods=['POST'])
@require_auth
def create_prompt_in_db():
    """Create a new prompt in database"""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'name is required'
            }), 400
        
        if not data.get('category'):
            return jsonify({
                'success': False,
                'error': 'category is required'
            }), 400
        
        if not data.get('prompt_text'):
            return jsonify({
                'success': False,
                'error': 'prompt_text is required'
            }), 400
        
        # Insert into database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ai_infrastructure.prompt_library 
            (user_id, workspace_id, name, category, type, description, 
             prompt_text, tags, visibility, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            data.get('workspace_id'),
            data.get('name'),
            data.get('category'),
            data.get('type', 'quick_action'),
            data.get('description'),
            data.get('prompt_text'),
            data.get('tags'),
            data.get('visibility', 'private'),
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat()
        ))
        
        prompt_id = cursor.lastrowid
        conn.commit()
        
        # Fetch the created prompt
        cursor.execute("""
            SELECT 
                id, user_id, workspace_id, name, category, type,
                description, prompt_text, tags, visibility,
                usage_count, created_at, updated_at
            FROM ai_infrastructure.prompt_library
            WHERE id = %s
        """, (prompt_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        prompt = {
            'id': row['id'],
            'user_id': row['user_id'],
            'workspace_id': row['workspace_id'],
            'name': row['name'],
            'category': row['category'],
            'type': row['type'],
            'description': row['description'],
            'prompt_text': row['prompt_text'],
            'tags': row['tags'],
            'visibility': row['visibility'],
            'usage_count': row['usage_count'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
        
        logger.info(f"Created prompt {prompt_id} for user {user_id}")
        
        return jsonify({
            'success': True,
            'prompt': prompt
        }), 201
        
    except Exception as e:
        logger.error(f"Error in create_prompt_in_db: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@prompt_routes.route('/library/db/<int:prompt_id>', methods=['PUT'])
@require_auth
def update_prompt_in_db(prompt_id):
    """Update an existing prompt in database"""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        # Verify ownership
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id FROM ai_infrastructure.prompt_library WHERE id = %s
        """, (prompt_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Prompt not found'
            }), 404
        
        if row['user_id'] != user_id:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        # Update prompt
        cursor.execute("""
            UPDATE ai_infrastructure.prompt_library
            SET 
                name = COALESCE( %s, name),
                category = COALESCE( %s, category),
                type = COALESCE( %s, type),
                description = COALESCE( %s, description),
                prompt_text = COALESCE( %s, prompt_text),
                tags = COALESCE( %s, tags),
                visibility = COALESCE( %s, visibility), updated_at = %s
            WHERE id = %s
        """, (
            data.get('name'),
            data.get('category'),
            data.get('type'),
            data.get('description'),
            data.get('prompt_text'),
            data.get('tags'),
            data.get('visibility'),
            datetime.utcnow().isoformat(),
            prompt_id
        ))
        
        conn.commit()
        
        # Fetch updated prompt
        cursor.execute("""
            SELECT 
                id, user_id, workspace_id, name, category, type,
                description, prompt_text, tags, visibility,
                usage_count, created_at, updated_at
            FROM ai_infrastructure.prompt_library
            WHERE id = %s
        """, (prompt_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        prompt = {
            'id': row['id'],
            'user_id': row['user_id'],
            'workspace_id': row['workspace_id'],
            'name': row['name'],
            'category': row['category'],
            'type': row['type'],
            'description': row['description'],
            'prompt_text': row['prompt_text'],
            'tags': row['tags'],
            'visibility': row['visibility'],
            'usage_count': row['usage_count'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
        
        logger.info(f"Updated prompt {prompt_id} for user {user_id}")
        
        return jsonify({
            'success': True,
            'prompt': prompt
        })
        
    except Exception as e:
        logger.error(f"Error in update_prompt_in_db: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@prompt_routes.route('/library/db/<int:prompt_id>', methods=['DELETE'])
@require_auth
def delete_prompt_from_db(prompt_id):
    """Delete a prompt from database"""
    try:
        user_id = request.user_id
        
        # Verify ownership
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id FROM ai_infrastructure.prompt_library WHERE id = %s
        """, (prompt_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Prompt not found'
            }), 404
        
        if row['user_id'] != user_id:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        # Delete prompt
        cursor.execute("""
            DELETE FROM ai_infrastructure.prompt_library WHERE id = %s
        """, (prompt_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted prompt {prompt_id} for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Prompt deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in delete_prompt_from_db: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
