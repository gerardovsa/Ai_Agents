"""
VSA Routes - Veterinary Alerts System API Endpoints

Provides centralized database access for VSA modules:
- Supabase credentials management
- Veterinary calls data access
- Alerts processing
- Follow-up actions

Uses centralized credential system from user_platform_credentials table.
"""

from flask import Blueprint, jsonify, request
from AI_infrastructure.auth.user_auth import UserAuthManager
import sys
import os

# Add root directory to path for imports
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)

from get_supabase_credentials import (
    get_supabase_credentials_for_frontend,
    get_supabase_credentials_for_backend
)

# Create blueprint
vsa_bp = Blueprint('vsa', __name__, url_prefix='/api/vsa')

# Initialize auth manager
auth_manager = UserAuthManager()


@vsa_bp.route('/credentials/supabase', methods=['GET'])
@auth_manager.require_auth
def get_supabase_credentials_endpoint():
    """
    Get Supabase credentials for VSA frontend modules
    
    Returns anon_key (safe for frontend) - NOT service_key
    
    Response:
        {
            'success': True,
            'credentials': {
                'url': 'https://wuwmvtslltqhaycyukxk.supabase.co',
                'anon_key': 'eyJhbGci...',
                'project_id': 'wuwmvtslltqhaycyukxk',
                'region': 'ap-southeast-2'
            }
        }
    
    Security:
        - Requires JWT authentication
        - Only returns anon_key (frontend-safe)
        - Service key stays on backend
        - Uses Supabase Row Level Security
    """
    try:
        # Get user_id from JWT token (injected by @require_auth)
        user_id = request.user_id
        
        # Fetch frontend-safe credentials from database
        result = get_supabase_credentials_for_frontend(user_id)
        
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': 'Supabase credentials not found',
                'message': 'Please configure Supabase credentials in user_platform_credentials table'
            }), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve credentials',
            'message': str(e)
        }), 500


@vsa_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for VSA routes
    
    Returns:
        {
            'success': True,
            'service': 'VSA Routes',
            'status': 'healthy',
            'endpoints': [...]
        }
    """
    return jsonify({
        'success': True,
        'service': 'VSA Routes',
        'status': 'healthy',
        'endpoints': [
            '/api/vsa/credentials/supabase',
            '/api/vsa/health'
        ]
    }), 200


# Future endpoints for backend proxy pattern (if needed)
# Uncomment and implement when switching to Option B

# @vsa_bp.route('/veterinary-calls', methods=['GET'])
# @auth_manager.require_auth
# def get_veterinary_calls():
#     """
#     Get veterinary calls from Supabase (backend proxy)
#     
#     Query Parameters:
#         limit: Max results (default: 500)
#         order_by: Column to order by (default: key_call_date)
#         order: asc/desc (default: desc)
#     """
#     try:
#         user_id = request.user_id
#         
#         # Get backend credentials (includes service_key)
#         creds = get_supabase_credentials_for_backend(user_id)
#         
#         if not creds['success']:
#             return jsonify({'error': 'Credentials not found'}), 500
#         
#         # Import Supabase client
#         from supabase import create_client, Client
#         
#         # Create Supabase client (backend-side)
#         supabase: Client = create_client(
#             creds['credentials']['url'],
#             creds['credentials']['service_key']
#         )
#         
#         # Query parameters
#         limit = request.args.get('limit', 500, type=int)
#         order_by = request.args.get('order_by', 'key_call_date')
#         order = request.args.get('order', 'desc')
#         
#         # Query Supabase
#         response = supabase.table('veterinary_calls') \
#             .select('*') \
#             .order(order_by, desc=(order == 'desc')) \
#             .limit(limit) \
#             .execute()
#         
#         return jsonify({
#             'success': True,
#             'data': response.data,
#             'count': len(response.data)
#         })
#         
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500
