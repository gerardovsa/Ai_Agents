#!/usr/bin/env python3
"""
supabase_credentials_routes.py - Flask routes for Supabase credentials

Purpose: Provide secure API endpoints to retrieve Supabase credentials for frontend modules
Security: Only returns anon_key to frontend (service_key kept server-side)

Date: November 30, 2025
Project: AI_agents - VSA Veterinary Alerts Module

Integration Instructions:
1. Import in AI_infrastructure/flask_app.py:
   from routes.supabase_credentials_routes import supabase_credentials_bp
   
2. Register blueprint:
   app.register_blueprint(supabase_credentials_bp, url_prefix='/api/credentials')
   
3. Frontend usage:
   fetch('/api/credentials/supabase')
     .then(res => res.json())
     .then(data => {
       const { url, anon_key } = data.credentials;
       // Initialize Supabase client
     });
"""

from flask import Blueprint, jsonify, request
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from get_supabase_credentials import (
    get_supabase_credentials_for_frontend,
    get_supabase_credentials_for_backend
)

# Create blueprint
supabase_credentials_bp = Blueprint('supabase_credentials', __name__)


@supabase_credentials_bp.route('/supabase', methods=['GET'])
def get_supabase_frontend_credentials():
    """
    Get Supabase credentials for frontend use (anon_key only)
    
    Returns:
        JSON response with Supabase URL and anon_key
        
    Example Response:
        {
            "success": true,
            "credentials": {
                "url": "https://wuwmvtslltqhaycyukxk.supabase.co",
                "anon_key": "eyJhbGciOiJ...",
                "project_id": "wuwmvtslltqhaycyukxk",
                "region": "ap-southeast-2"
            }
        }
    """
    try:
        # Get user_id from session/auth (default to 1 for now)
        # TODO: Implement proper authentication
        user_id = request.args.get('user_id', 1, type=int)
        
        # Get frontend-safe credentials
        result = get_supabase_credentials_for_frontend(user_id)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': 'Supabase credentials not found',
                'message': 'Please add Supabase credentials using SUPABASE_CREDENTIALS_INSERT.sql'
            }), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve Supabase credentials'
        }), 500


@supabase_credentials_bp.route('/supabase/backend', methods=['GET'])
def get_supabase_backend_credentials():
    """
    Get Supabase credentials for backend use (includes service_key)
    
    ⚠️ SECURITY WARNING: This endpoint should be protected and only accessible
    from server-side code, not directly from frontend
    
    Returns:
        JSON response with full Supabase credentials including service_key
    """
    try:
        # Get user_id from session/auth (default to 1 for now)
        # TODO: Implement proper authentication and authorization
        user_id = request.args.get('user_id', 1, type=int)
        
        # TODO: Add authentication check here
        # if not is_authenticated() or not has_admin_role():
        #     return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get full credentials including service_key
        result = get_supabase_credentials_for_backend(user_id)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': 'Supabase credentials not found'
            }), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@supabase_credentials_bp.route('/supabase/test', methods=['GET'])
def test_supabase_connection():
    """
    Test Supabase connection using stored credentials
    
    Returns:
        JSON response with connection test results
    """
    try:
        from supabase import create_client
        
        user_id = request.args.get('user_id', 1, type=int)
        
        # Get credentials
        result = get_supabase_credentials_for_backend(user_id)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': 'Credentials not found'
            }), 404
        
        creds = result['credentials']
        
        # Test connection
        supabase = create_client(creds['url'], creds['service_key'])
        
        # Try a simple query (test table access)
        response = supabase.table('veterinary_calls').select('id').limit(1).execute()
        
        return jsonify({
            'success': True,
            'message': 'Supabase connection successful',
            'url': creds['url'],
            'project_id': creds.get('project_id'),
            'test_query': 'SELECT id FROM veterinary_calls LIMIT 1',
            'records_found': len(response.data) if response.data else 0
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to connect to Supabase'
        }), 500


@supabase_credentials_bp.route('/platforms', methods=['GET'])
def list_available_platforms():
    """
    List all available platform credentials for a user
    
    Returns:
        JSON response with list of platforms
    """
    try:
        from shared.database_utils import get_database_connection
        
        user_id = request.args.get('user_id', 1, type=int)
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        query = """
            SELECT 
                platform,
                credential_type,
                is_active,
                metadata,
                updated_at
            FROM ai_infrastructure.user_platform_credentials
            WHERE user_id = %s
            ORDER BY platform, updated_at DESC
        """
        
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        
        platforms = []
        for row in rows:
            platforms.append({
                'platform': row[0],
                'credential_type': row[1],
                'is_active': row[2],
                'metadata': row[3] if row[3] else {},
                'updated_at': row[4].isoformat() if row[4] else None
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'platforms': platforms,
            'count': len(platforms)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== HEALTH CHECK ====================

@supabase_credentials_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'supabase_credentials_routes',
        'endpoints': [
            'GET /api/credentials/supabase',
            'GET /api/credentials/supabase/backend',
            'GET /api/credentials/supabase/test',
            'GET /api/credentials/platforms',
            'GET /api/credentials/health'
        ]
    }), 200


# ==================== ERROR HANDLERS ====================

@supabase_credentials_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@supabase_credentials_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
