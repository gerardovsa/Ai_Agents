"""
FILE: AI_infrastructure/routes/module_routes.py
PURPOSE: Module management API routes (discovery, loading, credential checking)

ENDPOINTS:
- GET /api/modules/list - Get all registered modules
- GET /api/modules/available - Get modules user can access (has credentials)
- GET /api/modules/needs-setup - Get modules needing credential configuration
- GET /api/modules/<module_id> - Get specific module info
- GET /api/modules/<module_id>/html - Load module HTML template
- POST /api/modules/<module_id>/enable - Enable module for user
- POST /api/modules/<module_id>/disable - Disable module for user
- GET /api/modules/<module_id>/credentials-status - Check credential status

DEPENDENCIES:
- core.module_registry (ModuleRegistry, get_module_registry)
- auth.user_auth (UserAuthManager)

USED BY:
- frontend/modules/ (UI components)
- frontend/business-ai-platform-v2.html (main UI)

NOTES:
- Modules lazy-loaded on-demand (not all at startup)
- Credential checks cached for performance
- Module permissions checked before loading

LAST MODIFIED: 2025-11-25 - Initial module routes implementation
"""

from flask import Blueprint, jsonify, request, Response
from functools import wraps
import logging

from AI_infrastructure.core.module_registry import get_module_registry
from AI_infrastructure.auth.user_auth import UserAuthManager

logger = logging.getLogger(__name__)

module_bp = Blueprint('module', __name__, url_prefix='/api/modules')


def require_auth(f):
    """Decorator to require user authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get user_id from request (JWT token, session, etc.)
        user_id = request.args.get('user_id') or request.json.get('user_id') if request.is_json else None
        
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({'error': 'Invalid user_id'}), 400
        
        # Inject user_id into kwargs
        kwargs['user_id'] = user_id
        return f(*args, **kwargs)
    
    return decorated_function


@module_bp.route('/list', methods=['GET'])
def list_modules():
    """
    Get all registered modules (no auth required - public list)
    
    Returns:
        {
            'modules': [
                {
                    'id': 'vector_database',
                    'name': 'Vector Database',
                    'description': '...',
                    'icon': 'fa-database',
                    'color': '#8b5cf6',
                    'version': '1.0.0',
                    'required_platforms': ['pinecone', 'openai'],
                    'optional_platforms': []
                }
            ],
            'count': 5
        }
    """
    try:
        registry = get_module_registry()
        modules = registry.get_all_modules()
        
        module_list = [{
            'id': m.id,
            'name': m.name,
            'description': m.description,
            'icon': m.icon,
            'color': m.color,
            'version': m.version,
            'required_platforms': m.required_platforms,
            'optional_platforms': m.optional_platforms,
            'sidebar_position': m.sidebar_position,
            'sidebar_width': m.sidebar_width,
            'requires_auth': m.requires_auth,
            'features': m.features
        } for m in modules]
        
        return jsonify({
            'modules': module_list,
            'count': len(module_list)
        })
    
    except Exception as e:
        logger.error(f"Failed to list modules: {e}")
        return jsonify({'error': str(e)}), 500


@module_bp.route('/available', methods=['GET'])
def get_available_modules():
    """
    Get modules user can access (has required credentials)
    
    Query params:
        user_id: User ID
    
    Returns:
        {
            'modules': [
                {
                    'id': 'vector_database',
                    'name': 'Vector Database',
                    'description': '...',
                    'icon': 'fa-database',
                    'color': '#8b5cf6',
                    'version': '1.0.0',
                    'has_optional': true,
                    'available_optional': ['assemblyai']
                }
            ],
            'count': 3
        }
    """
    try:
        # Get user_id from query params (optional for development)
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            # Development mode: return all modules if no user_id
            registry = get_module_registry()
            all_modules = registry.get_all_modules()
            return jsonify({
                'modules': [{
                    'id': m.id,
                    'name': m.name,
                    'description': m.description,
                    'icon': m.icon,
                    'color': m.color,
                    'version': m.version,
                    'available': True,  # Assume available in dev mode
                    'has_optional': len(m.optional_platforms) > 0,
                    'available_optional': m.optional_platforms
                } for m in all_modules],
                'count': len(all_modules)
            })
        
        registry = get_module_registry()
        available = registry.get_available_modules(user_id)
        
        return jsonify({
            'modules': available,
            'count': len(available)
        })
    
    except Exception as e:
        logger.error(f"Failed to get available modules: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@module_bp.route('/needs-setup', methods=['GET'])
@require_auth
def get_modules_needing_setup(user_id: int):
    """
    Get modules that need credential configuration
    
    Query params:
        user_id: User ID
    
    Returns:
        {
            'modules': [
                {
                    'id': 'vector_database',
                    'name': 'Vector Database',
                    'description': '...',
                    'icon': 'fa-database',
                    'color': '#8b5cf6',
                    'missing_required': ['pinecone', 'openai'],
                    'setup_guide': '/docs/modules/vector_database/setup'
                }
            ],
            'count': 2
        }
    """
    try:
        registry = get_module_registry()
        needing_setup = registry.get_modules_needing_credentials(user_id)
        
        return jsonify({
            'modules': needing_setup,
            'count': len(needing_setup)
        })
    
    except Exception as e:
        logger.error(f"Failed to get modules needing setup for user {user_id}: {e}")
        return jsonify({'error': str(e)}), 500


@module_bp.route('/<module_id>', methods=['GET'])
def get_module_info(module_id: str):
    """
    Get specific module info
    
    Path params:
        module_id: Module ID
    
    Returns:
        {
            'id': 'vector_database',
            'name': 'Vector Database',
            'description': '...',
            'icon': 'fa-database',
            'color': '#8b5cf6',
            'version': '1.0.0',
            'required_platforms': ['pinecone', 'openai'],
            'optional_platforms': [],
            'sidebar_position': 'right',
            'sidebar_width': 450,
            'dependencies': [],
            'api_routes': ['/api/vector-db/*'],
            'features': {...}
        }
    """
    try:
        registry = get_module_registry()
        module = registry.get_module(module_id)
        
        if not module:
            return jsonify({'error': f"Module {module_id} not found"}), 404
        
        return jsonify({
            'id': module.id,
            'name': module.name,
            'description': module.description,
            'icon': module.icon,
            'color': module.color,
            'version': module.version,
            'required_platforms': module.required_platforms,
            'optional_platforms': module.optional_platforms,
            'sidebar_position': module.sidebar_position,
            'sidebar_width': module.sidebar_width,
            'auto_load': module.auto_load,
            'requires_auth': module.requires_auth,
            'dependencies': module.dependencies,
            'api_routes': module.api_routes,
            'features': module.features
        })
    
    except Exception as e:
        logger.error(f"Failed to get module info for {module_id}: {e}")
        return jsonify({'error': str(e)}), 500


@module_bp.route('/<module_id>/html', methods=['GET'])
def get_module_html(module_id: str):
    """
    Load module HTML template
    
    Path params:
        module_id: Module ID
    
    Returns:
        HTML content (text/html)
    """
    try:
        registry = get_module_registry()
        html = registry.get_module_html(module_id)
        
        if not html:
            return jsonify({'error': f"HTML not found for module {module_id}"}), 404
        
        return Response(html, mimetype='text/html')
    
    except Exception as e:
        logger.error(f"Failed to load HTML for {module_id}: {e}")
        return jsonify({'error': str(e)}), 500


@module_bp.route('/<module_id>/credentials-status', methods=['GET'])
@require_auth
def check_credentials_status(module_id: str, user_id: int):
    """
    Check credential status for module
    
    Path params:
        module_id: Module ID
    
    Query params:
        user_id: User ID
    
    Returns:
        {
            'has_required': true,
            'has_optional': false,
            'missing_required': [],
            'available_optional': [],
            'credential_forms': {...}  # Form definitions from manifest
        }
    """
    try:
        registry = get_module_registry()
        module = registry.get_module(module_id)
        
        if not module:
            return jsonify({'error': f"Module {module_id} not found"}), 404
        
        # Check credential status
        cred_status = registry.check_user_credentials(user_id, module_id)
        
        # Load manifest to get credential form definitions
        import json
        from pathlib import Path
        
        manifest_path = Path(module.module_path) / "manifest.json"
        credential_forms = {}
        
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
                credential_forms = manifest_data.get('credential_forms', {})
        
        return jsonify({
            **cred_status,
            'credential_forms': credential_forms
        })
    
    except Exception as e:
        logger.error(f"Failed to check credentials for {module_id}, user {user_id}: {e}")
        return jsonify({'error': str(e)}), 500


@module_bp.route('/<module_id>/enable', methods=['POST'])
@require_auth
def enable_module(module_id: str, user_id: int):
    """
    Enable module for user
    
    Path params:
        module_id: Module ID
    
    Body:
        {
            'user_id': 1
        }
    
    Returns:
        {
            'success': true,
            'message': 'Module enabled'
        }
    """
    try:
        registry = get_module_registry()
        module = registry.get_module(module_id)
        
        if not module:
            return jsonify({'error': f"Module {module_id} not found"}), 404
        
        # Check if user has required credentials
        cred_status = registry.check_user_credentials(user_id, module_id)
        
        if not cred_status['has_required']:
            return jsonify({
                'error': 'Missing required credentials',
                'missing_required': cred_status['missing_required']
            }), 400
        
        # TODO: Store user module preference in database
        # For now, just return success
        
        return jsonify({
            'success': True,
            'message': f"Module {module.name} enabled"
        })
    
    except Exception as e:
        logger.error(f"Failed to enable module {module_id} for user {user_id}: {e}")
        return jsonify({'error': str(e)}), 500


@module_bp.route('/<module_id>/disable', methods=['POST'])
@require_auth
def disable_module(module_id: str, user_id: int):
    """
    Disable module for user
    
    Path params:
        module_id: Module ID
    
    Body:
        {
            'user_id': 1
        }
    
    Returns:
        {
            'success': true,
            'message': 'Module disabled'
        }
    """
    try:
        registry = get_module_registry()
        module = registry.get_module(module_id)
        
        if not module:
            return jsonify({'error': f"Module {module_id} not found"}), 404
        
        # TODO: Store user module preference in database
        # For now, just return success
        
        return jsonify({
            'success': True,
            'message': f"Module {module.name} disabled"
        })
    
    except Exception as e:
        logger.error(f"Failed to disable module {module_id} for user {user_id}: {e}")
        return jsonify({'error': str(e)}), 500


@module_bp.route('/load-order', methods=['GET'])
def get_load_order():
    """
    Get module load order based on dependencies
    
    Returns:
        {
            'load_order': ['base_module', 'vector_database', 'analytics']
        }
    """
    try:
        registry = get_module_registry()
        load_order = registry.get_load_order()
        
        return jsonify({
            'load_order': load_order
        })
    
    except Exception as e:
        logger.error(f"Failed to get load order: {e}")
        return jsonify({'error': str(e)}), 500
