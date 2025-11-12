"""
Render Cloud Management API Routes
Provides endpoints for Render service management via UI module
"""

from flask import Blueprint, jsonify, request
import sys
import os

# Add paths for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(os.path.dirname(__file__))
root_dir = os.path.dirname(parent_dir)

sys.path.insert(0, parent_dir)
sys.path.insert(0, root_dir)

try:
    # Try AI_infrastructure import first
    sys.path.insert(0, os.path.join(parent_dir, 'core'))
    from registry_v3 import RegistryV3 as Registry
    print("✅ [Render Routes] Loaded registry_v3 from core")
except ImportError:
    try:
        # Try tools import
        from tools.registry_v3 import RegistryV3 as Registry
        print("✅ [Render Routes] Loaded registry_v3 from tools")
    except ImportError:
        print("⚠️  [Render Routes] Warning: Could not import tool registry")
        Registry = None

# Import authentication
from auth.user_auth import require_auth

render_bp = Blueprint('render', __name__, url_prefix='/api/render')

# Initialize registry (will be initialized on first use if needed)
registry = None

def get_registry():
    """Lazy load registry"""
    global registry
    if registry is None and Registry:
        registry = Registry()
        print(f"✅ [Render Routes] Registry initialized with {len(registry.tools) if hasattr(registry, 'tools') else '?'} tools")
    return registry

@render_bp.route('/services', methods=['GET'])
@require_auth
def list_services():
    """List all Render services with optional filtering"""
    reg = get_registry()
    if not reg:
        return jsonify({'success': False, 'error': 'Tool registry not available'}), 500
    
    try:
        # Get authenticated user ID from JWT
        user_id = request.user.get('user_id')
        
        service_type = request.args.get('type')
        status = request.args.get('status')
        
        result = reg.execute_tool(
            tool_name='render_list_services',
            service_type=service_type,
            status=status,
            _user_id=user_id
        )
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        print(f"❌ Error listing services: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@render_bp.route('/logs', methods=['GET'])
@require_auth
def get_logs():
    """Get service logs with filtering"""
    reg = get_registry()
    if not reg:
        return jsonify({'success': False, 'error': 'Tool registry not available'}), 500
    
    # Get authenticated user ID from JWT
    user_id = request.user.get('user_id')
    
    service_id = request.args.get('service_id')
    tail = int(request.args.get('tail', 100))
    text_filter = request.args.get('filter')
    
    if not service_id:
        return jsonify({'success': False, 'error': 'service_id required'}), 400
    
    try:
        result = reg.execute_tool(
            tool_name='render_get_service_logs',
            service_id=service_id,
            tail=tail,
            text_filter=text_filter,
            _user_id=user_id
        )
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        print(f"❌ Error getting logs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@render_bp.route('/deploys', methods=['GET'])
@require_auth
def list_deploys():
    """Get deployment history for a service"""
    reg = get_registry()
    if not reg:
        return jsonify({'success': False, 'error': 'Tool registry not available'}), 500
    
    # Get authenticated user ID from JWT
    user_id = request.user.get('user_id')
    
    service_id = request.args.get('service_id')
    limit = int(request.args.get('limit', 10))
    
    if not service_id:
        return jsonify({'success': False, 'error': 'service_id required'}), 400
    
    try:
        result = reg.execute_tool(
            tool_name='render_get_deploys',
            service_id=service_id,
            limit=limit,
            _user_id=user_id
        )
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        print(f"❌ Error listing deploys: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@render_bp.route('/deploy', methods=['POST'])
@require_auth
def deploy_service():
    """Trigger a service deployment"""
    reg = get_registry()
    if not reg:
        return jsonify({'success': False, 'error': 'Tool registry not available'}), 500
    
    # Get authenticated user ID from JWT
    user_id = request.user.get('user_id')
    
    data = request.json
    
    if not data or 'service_id' not in data:
        return jsonify({'success': False, 'error': 'service_id required'}), 400
    
    try:
        result = reg.execute_tool(
            tool_name='render_deploy_service',
            service_id=data['service_id'],
            commit_sha=data.get('commit_sha'),
            image_url=data.get('image_url'),
            wait=data.get('wait', True),
            _user_id=user_id
        )
        return jsonify(result)
    except Exception as e:
        print(f"❌ Error deploying service: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@render_bp.route('/restart', methods=['POST'])
@require_auth
def restart_service():
    """Restart a service (triggers redeploy)"""
    reg = get_registry()
    if not reg:
        return jsonify({'success': False, 'error': 'Tool registry not available'}), 500
    
    # Get authenticated user ID from JWT
    user_id = request.user.get('user_id')
    
    data = request.json
    
    if not data or 'service_id' not in data:
        return jsonify({'success': False, 'error': 'service_id required'}), 400
    
    try:
        result = reg.execute_tool(
            tool_name='render_restart_service',
            service_id=data['service_id'],
            _user_id=user_id
        )
        return jsonify(result)
    except Exception as e:
        print(f"❌ Error restarting service: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@render_bp.route('/metrics', methods=['GET'])
@require_auth
def get_metrics():
    """Get service metrics (CPU, memory, requests)"""
    reg = get_registry()
    if not reg:
        return jsonify({'success': False, 'error': 'Tool registry not available'}), 500
    
    # Get authenticated user ID from JWT
    user_id = request.user.get('user_id')
    
    service_id = request.args.get('service_id')
    
    if not service_id:
        return jsonify({'success': False, 'error': 'service_id required'}), 400
    
    try:
        result = reg.execute_tool(
            tool_name='render_get_service_metrics',
            service_id=service_id,
            _user_id=user_id
        )
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        print(f"❌ Error getting metrics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Module loaded message
print("✅ [Render Routes] Blueprint created - will initialize registry on first API call")
