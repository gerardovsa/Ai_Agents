"""
Dev Tools API Routes
====================

Flask blueprint for development-only endpoints used by the Module Creator & Verifier UI.

IMPORTANT: These endpoints are for development use only and should NOT be exposed in production.

Endpoints:
    POST /api/dev-tools/validate-manifest - Validate module manifest structure
    POST /api/dev-tools/create-module - Generate module folder and files
    POST /api/dev-tools/save-manifest - Save manifest to existing module
    GET  /api/dev-tools/templates - List available manifest templates
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from flask import Blueprint, request, jsonify
from typing import Dict, Any, List

# Create blueprint
dev_tools_bp = Blueprint('dev_tools', __name__, url_prefix='/api/dev-tools')

# Define paths
BASE_DIR = Path(__file__).parent.parent.parent  # AI_agents root
MODULES_DIR = BASE_DIR / 'UI' / 'modules_external'
TEMPLATES_DIR = BASE_DIR / 'dev-tools' / 'templates'

# ================================================================
# VALIDATION
# ================================================================

def validate_manifest(manifest: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate module manifest structure.
    
    Args:
        manifest: Module manifest dictionary
        
    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []
    
    # Required fields
    required_fields = ['id', 'name', 'version', 'description']
    for field in required_fields:
        if field not in manifest or not manifest[field]:
            errors.append(f"Missing required field: {field}")
    
    # ID validation (alphanumeric + underscores/hyphens)
    if 'id' in manifest:
        module_id = manifest['id']
        if not module_id.replace('_', '').replace('-', '').isalnum():
            errors.append(f"Invalid module ID: {module_id}. Use only letters, numbers, underscores, and hyphens.")
        if module_id.startswith('_') or module_id.startswith('-'):
            errors.append(f"Module ID cannot start with underscore or hyphen: {module_id}")
    
    # Version validation (semver format)
    if 'version' in manifest:
        version = manifest['version']
        parts = version.split('.')
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            errors.append(f"Invalid version format: {version}. Use semantic versioning (e.g., 1.0.0)")
    
    # Files validation
    if 'files' in manifest:
        files = manifest['files']
        if not isinstance(files, dict):
            errors.append("'files' must be an object")
        else:
            valid_file_types = ['html', 'js', 'css', 'routes']
            for key in files.keys():
                if key not in valid_file_types:
                    errors.append(f"Invalid file type: {key}. Use: {', '.join(valid_file_types)}")
    
    # Features validation
    if 'features' in manifest:
        features = manifest['features']
        if not isinstance(features, dict):
            errors.append("'features' must be an object")
        else:
            valid_features = ['requires_auth', 'show_in_sidebar', 'auto_load', 'main_tab']
            for key in features.keys():
                if key not in valid_features:
                    errors.append(f"Invalid feature: {key}. Use: {', '.join(valid_features)}")
    
    # Platforms validation
    if 'required_platforms' in manifest:
        platforms = manifest['required_platforms']
        if not isinstance(platforms, list):
            errors.append("'required_platforms' must be an array")
    
    return len(errors) == 0, errors


@dev_tools_bp.route('/validate-manifest', methods=['POST'])
def validate_manifest_endpoint():
    """
    POST /api/dev-tools/validate-manifest
    
    Validate module manifest JSON structure.
    
    Request Body:
        {
            "id": "my_module",
            "name": "My Module",
            "version": "1.0.0",
            "description": "Module description",
            "files": { "html": true, "js": true, "css": true, "routes": false },
            "features": { "requires_auth": true, "show_in_sidebar": true },
            "required_platforms": ["xero", "shopify"]
        }
    
    Response:
        {
            "valid": true,
            "errors": [],
            "message": "Manifest is valid"
        }
    """
    try:
        manifest = request.get_json()
        
        if not manifest:
            return jsonify({
                'valid': False,
                'errors': ['No manifest data provided'],
                'message': 'Request body is empty'
            }), 400
        
        is_valid, errors = validate_manifest(manifest)
        
        return jsonify({
            'valid': is_valid,
            'errors': errors,
            'message': 'Manifest is valid' if is_valid else f'Found {len(errors)} validation error(s)'
        })
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'errors': [str(e)],
            'message': 'Validation failed'
        }), 500


# ================================================================
# MODULE CREATION
# ================================================================

def generate_module_files(module_id: str, manifest: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate module file templates.
    
    Args:
        module_id: Module ID (used for filenames)
        manifest: Module manifest data
        
    Returns:
        Dictionary of filename -> content
    """
    files = {}
    
    # Generate manifest.json
    files['manifest.json'] = json.dumps(manifest, indent=2)
    
    # Generate HTML template
    if manifest.get('files', {}).get('html', False):
        files[f'{module_id}.html'] = f"""<!-- {manifest['name']} Module -->
<div id="{module_id}-module" class="module-container">
    <div class="module-header">
        <h2><i class="{manifest.get('icon', 'fas fa-cube')}"></i> {manifest['name']}</h2>
        <p class="module-description">{manifest['description']}</p>
    </div>
    
    <div class="module-content">
        <!-- Module content goes here -->
        <p>Welcome to {manifest['name']}!</p>
    </div>
</div>

<style>
.module-container {{
    padding: 20px;
}}

.module-header {{
    margin-bottom: 20px;
}}

.module-header h2 {{
    font-size: 24px;
    margin-bottom: 8px;
}}

.module-description {{
    color: #666;
    font-size: 14px;
}}

.module-content {{
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}
</style>
"""
    
    # Generate JavaScript template
    if manifest.get('files', {}).get('js', False):
        files[f'{module_id}.js'] = f"""/**
 * {manifest['name']} Module
 * Version: {manifest['version']}
 * 
 * {manifest['description']}
 */

class {to_camel_case(module_id)}Module {{
    constructor() {{
        this.API_BASE = 'http://localhost:5001';
        this.moduleId = '{module_id}';
        this.init();
    }}
    
    async init() {{
        console.log('[{module_id}] Initializing module...');
        
        try {{
            await this.loadData();
            this.bindEvents();
            console.log('[{module_id}] Module initialized successfully');
        }} catch (error) {{
            console.error('[{module_id}] Initialization failed:', error);
        }}
    }}
    
    async loadData() {{
        // Load module data from API
        try {{
            const response = await fetch(`${{this.API_BASE}}/api/modules/${{this.moduleId}}`);
            if (!response.ok) throw new Error('Failed to load module data');
            
            const data = await response.json();
            console.log('[{module_id}] Data loaded:', data);
            return data;
        }} catch (error) {{
            console.error('[{module_id}] Failed to load data:', error);
            throw error;
        }}
    }}
    
    bindEvents() {{
        // Bind UI event listeners
        console.log('[{module_id}] Binding events...');
        
        // Example: Button click
        // document.querySelector('#my-button').addEventListener('click', () => {{
        //     this.handleAction();
        // }});
    }}
    
    async handleAction() {{
        // Handle user actions
        console.log('[{module_id}] Action triggered');
    }}
}}

// Initialize module when DOM is ready
document.addEventListener('DOMContentLoaded', () => {{
    window.{to_camel_case(module_id)} = new {to_camel_case(module_id)}Module();
}});
"""
    
    # Generate CSS template
    if manifest.get('files', {}).get('css', False):
        files[f'{module_id}.css'] = f"""/**
 * {manifest['name']} Module Styles
 * Version: {manifest['version']}
 */

/* Module Container */
#{module_id}-module {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

/* Module Header */
#{module_id}-module .module-header {{
    /* Add your styles */
}}

/* Module Content */
#{module_id}-module .module-content {{
    /* Add your styles */
}}

/* Buttons */
#{module_id}-module .btn-primary {{
    background: #0066cc;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.3s;
}}

#{module_id}-module .btn-primary:hover {{
    background: #0052a3;
}}
"""
    
    # Generate Flask routes template
    if manifest.get('files', {}).get('routes', False):
        files[f'routes/{module_id}_routes.py'] = f"""\"\"\"
{manifest['name']} Module Routes
{manifest['description']}
\"\"\"

from flask import Blueprint, jsonify, request
from typing import Dict, Any

# Create blueprint
{module_id}_bp = Blueprint('{module_id}', __name__, url_prefix='/api/{module_id}')


@{module_id}_bp.route('/data', methods=['GET'])
def get_data():
    \"\"\"
    GET /api/{module_id}/data
    
    Returns module data.
    \"\"\"
    try:
        # TODO: Implement data retrieval
        data = {{
            'module_id': '{module_id}',
            'name': '{manifest['name']}',
            'version': '{manifest['version']}',
            'data': []
        }}
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({{'error': str(e)}}), 500


@{module_id}_bp.route('/action', methods=['POST'])
def perform_action():
    \"\"\"
    POST /api/{module_id}/action
    
    Performs a module action.
    \"\"\"
    try:
        payload = request.get_json()
        
        # TODO: Implement action logic
        result = {{
            'success': True,
            'message': 'Action completed successfully',
            'data': payload
        }}
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({{'error': str(e)}}), 500
"""
    
    return files


def to_camel_case(snake_str: str) -> str:
    """Convert snake_case to CamelCase."""
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)


@dev_tools_bp.route('/create-module', methods=['POST'])
def create_module():
    """
    POST /api/dev-tools/create-module
    
    Generate module folder structure and files.
    
    Request Body:
        {
            "id": "my_module",
            "name": "My Module",
            "version": "1.0.0",
            "description": "Module description",
            "files": { "html": true, "js": true, "css": true, "routes": false },
            "features": { "requires_auth": true },
            "required_platforms": []
        }
    
    Response:
        {
            "success": true,
            "module_id": "my_module",
            "path": "C:/Users/gpoli/GIT/AI_agents/UI/modules_external/my_module",
            "files_created": ["manifest.json", "my_module.html", "my_module.js", "my_module.css"],
            "message": "Module created successfully"
        }
    """
    try:
        manifest = request.get_json()
        
        if not manifest:
            return jsonify({
                'success': False,
                'error': 'No manifest data provided'
            }), 400
        
        # Validate manifest
        is_valid, errors = validate_manifest(manifest)
        if not is_valid:
            return jsonify({
                'success': False,
                'errors': errors,
                'message': 'Manifest validation failed'
            }), 400
        
        module_id = manifest['id']
        module_path = MODULES_DIR / module_id
        
        # Check if module already exists
        if module_path.exists():
            return jsonify({
                'success': False,
                'error': f'Module already exists: {module_id}',
                'path': str(module_path)
            }), 409
        
        # Create module directory
        module_path.mkdir(parents=True, exist_ok=True)
        
        # Generate files
        files = generate_module_files(module_id, manifest)
        files_created = []
        
        for filename, content in files.items():
            # Handle routes subfolder
            if '/' in filename:
                file_path = module_path / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                file_path = module_path / filename
            
            # Write file
            file_path.write_text(content, encoding='utf-8')
            files_created.append(filename)
        
        return jsonify({
            'success': True,
            'module_id': module_id,
            'path': str(module_path),
            'files_created': files_created,
            'message': f'Module "{manifest["name"]}" created successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Module creation failed'
        }), 500


@dev_tools_bp.route('/save-manifest', methods=['POST'])
def save_manifest():
    """
    POST /api/dev-tools/save-manifest
    
    Save/update manifest.json for existing module.
    
    Request Body:
        {
            "module_id": "my_module",
            "manifest": { ... }
        }
    
    Response:
        {
            "success": true,
            "module_id": "my_module",
            "backup_path": "C:/Users/.../my_module/manifest.json.backup.20231206_143022",
            "message": "Manifest saved successfully"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'module_id' not in data or 'manifest' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing module_id or manifest in request'
            }), 400
        
        module_id = data['module_id']
        manifest = data['manifest']
        
        # Validate manifest
        is_valid, errors = validate_manifest(manifest)
        if not is_valid:
            return jsonify({
                'success': False,
                'errors': errors,
                'message': 'Manifest validation failed'
            }), 400
        
        module_path = MODULES_DIR / module_id
        
        # Check if module exists
        if not module_path.exists():
            return jsonify({
                'success': False,
                'error': f'Module not found: {module_id}',
                'path': str(module_path)
            }), 404
        
        manifest_file = module_path / 'manifest.json'
        
        # Backup existing manifest
        backup_path = None
        if manifest_file.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = module_path / f'manifest.json.backup.{timestamp}'
            shutil.copy(manifest_file, backup_path)
        
        # Save new manifest
        manifest_file.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        
        return jsonify({
            'success': True,
            'module_id': module_id,
            'backup_path': str(backup_path) if backup_path else None,
            'message': 'Manifest saved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Save failed'
        }), 500


# ================================================================
# TEMPLATES
# ================================================================

@dev_tools_bp.route('/templates', methods=['GET'])
def get_templates():
    """
    GET /api/dev-tools/templates
    
    List available manifest templates.
    
    Response:
        {
            "templates": [
                {
                    "id": "basic",
                    "name": "Basic Module",
                    "description": "Minimal module template",
                    "manifest": { ... }
                }
            ]
        }
    """
    templates = [
        {
            'id': 'basic',
            'name': 'Basic Module',
            'description': 'Minimal module with HTML and JavaScript',
            'manifest': {
                'id': '',
                'name': '',
                'version': '1.0.0',
                'description': '',
                'icon': 'fas fa-cube',
                'files': {
                    'html': True,
                    'js': True,
                    'css': False,
                    'routes': False
                },
                'features': {
                    'requires_auth': True,
                    'show_in_sidebar': True,
                    'auto_load': False,
                    'main_tab': False
                },
                'required_platforms': []
            }
        },
        {
            'id': 'full',
            'name': 'Full Module',
            'description': 'Complete module with all file types',
            'manifest': {
                'id': '',
                'name': '',
                'version': '1.0.0',
                'description': '',
                'icon': 'fas fa-cube',
                'files': {
                    'html': True,
                    'js': True,
                    'css': True,
                    'routes': True
                },
                'features': {
                    'requires_auth': True,
                    'show_in_sidebar': True,
                    'auto_load': False,
                    'main_tab': False
                },
                'required_platforms': []
            }
        },
        {
            'id': 'api',
            'name': 'API Module',
            'description': 'Backend-focused module with Flask routes',
            'manifest': {
                'id': '',
                'name': '',
                'version': '1.0.0',
                'description': '',
                'icon': 'fas fa-server',
                'files': {
                    'html': False,
                    'js': False,
                    'css': False,
                    'routes': True
                },
                'features': {
                    'requires_auth': True,
                    'show_in_sidebar': False,
                    'auto_load': False,
                    'main_tab': False
                },
                'required_platforms': []
            }
        }
    ]
    
    return jsonify({'templates': templates})
