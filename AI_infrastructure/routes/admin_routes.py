"""
Admin routes for cache management and diagnostics
Added: January 21, 2026 - Fix meta-tools cache issue on Render
"""
from flask import Blueprint, jsonify, request
from tools.registry_v3 import get_registry
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def require_admin_key(f):
    """Decorator to require ADMIN_API_KEY for admin endpoints"""
    @wraps(f)
    def decorated(*args, **kwargs):
        import os
        admin_key = os.getenv('ADMIN_API_KEY')
        
        # If no admin key set, block all admin endpoints
        if not admin_key:
            return jsonify({'error': 'Admin API not configured'}), 403
        
        # Check request header or query param
        provided_key = request.headers.get('X-Admin-Key') or request.args.get('admin_key')
        
        if provided_key != admin_key:
            return jsonify({'error': 'Invalid admin key'}), 401
        
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/cache/invalidate', methods=['POST'])
@require_admin_key
def invalidate_cache():
    """
    Invalidate Registry V3 tool cache
    
    Usage:
        curl -X POST https://your-app.onrender.com/api/admin/cache/invalidate \
             -H "X-Admin-Key: your_secret_key"
    
    Or with query param:
        https://your-app.onrender.com/api/admin/cache/invalidate?admin_key=your_secret_key
    """
    try:
        registry = get_registry()
        success = registry.invalidate_cache()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Tool registry cache invalidated',
                'action_required': 'Restart Flask server to reload fresh tools'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Redis not available - cache not used',
                'current_tools': len(registry.tools)
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/cache/status', methods=['GET'])
@require_admin_key
def cache_status():
    """
    Get cache status and tool count
    
    Usage:
        curl https://your-app.onrender.com/api/admin/cache/status \
             -H "X-Admin-Key: your_secret_key"
    """
    try:
        registry = get_registry()
        
        # Check meta-tools
        meta_tools = [
            'search_tools',
            'list_platform_tools',
            'list_available_platforms',
            'get_tool_schema',
            'execute_tool'
        ]
        
        meta_status = {
            tool: tool in registry.tools
            for tool in meta_tools
        }
        
        return jsonify({
            'success': True,
            'total_tools': len(registry.tools),
            'meta_tools': meta_status,
            'meta_tools_available': all(meta_status.values()),
            'redis_enabled': registry.redis_manager is not None and registry.redis_manager.connected
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/tools/reload', methods=['POST'])
@require_admin_key
def reload_tools():
    """
    Force reload tools from disk (bypasses cache)
    
    Usage:
        curl -X POST https://your-app.onrender.com/api/admin/tools/reload \
             -H "X-Admin-Key: your_secret_key"
    """
    try:
        # Invalidate cache first
        registry = get_registry()
        registry.invalidate_cache()
        
        # Reload schemas from disk
        registry._load_schemas()
        registry._load_implementations()
        registry._load_module_plugins()
        
        # Save new cache
        registry._save_to_cache()
        
        # Check meta-tools
        meta_tools = ['search_tools', 'list_platform_tools', 'list_available_platforms', 'get_tool_schema', 'execute_tool']
        meta_status = {tool: tool in registry.tools for tool in meta_tools}
        
        return jsonify({
            'success': True,
            'message': 'Tools reloaded from disk',
            'total_tools': len(registry.tools),
            'meta_tools': meta_status,
            'meta_tools_available': all(meta_status.values())
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
