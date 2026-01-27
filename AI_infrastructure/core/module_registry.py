"""
FILE: AI_infrastructure/core/module_registry.py
PURPOSE: Self-registering module system with automatic credential discovery

ARCHITECTURE:
- Modules self-register their credential requirements via manifest files
- ModuleRegistry auto-discovers all modules in modules/ directory
- Credentials auto-injected at runtime (similar to tool execution)
- UI dynamically generates forms/settings from module manifests

PATTERN: Mirrors tool registry architecture for consistency
- modules/ folder contains module implementations
- Each module has manifest.json describing requirements
- Registry loads all manifests at startup
- Credential requirements extracted from manifests
- UI automatically generates credential forms

DEPENDENCIES:
- shared.database_utils (PostgreSQL connection)
- auth.user_auth (credential storage/retrieval)
- auth.platform_credential_schemas (validation)

EXPORTS:
- ModuleRegistry (singleton) - Load and manage all modules
- get_module_registry() - Get singleton instance
- Module dataclass - Module metadata container

USED BY:
- AI_infrastructure/flask_app.py (initialize at startup)
- AI_infrastructure/routes/module_routes.py (module management API)
- frontend/modules/ (UI components)

NOTES:
- Modules are lazy-loaded (only load when needed)
- Credentials fetched on-demand (not at init)
- Module dependencies tracked (load order management)
- Hot-reload support for development

LAST MODIFIED: 2025-11-25 - Initial module registry implementation
"""

import os
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from pathlib import Path

# ✅ NEW: Import deployment configuration for environment-based module filtering
from AI_infrastructure.config.deployment_config import is_module_enabled

logger = logging.getLogger(__name__)


@dataclass
class ModuleManifest:
    """Module metadata from manifest.json"""
    id: str  # Unique module identifier (e.g., "vector_database")
    name: str  # Display name (e.g., "Vector Database")
    version: str  # Semantic version (e.g., "1.0.0")
    description: str  # Brief description
    icon: str  # Font Awesome icon class (e.g., "fa-database")
    color: str  # Hex color for UI (e.g., "#8b5cf6")
    
    # File paths (relative to module directory)
    html_file: Optional[str] = None  # UI template
    js_file: Optional[str] = None  # Controller logic
    css_file: Optional[str] = None  # Styling
    
    # Full file paths (from project root)
    htmlPath: Optional[str] = None  # Full path to HTML file
    scriptPath: Optional[str] = None  # Full path to JS file
    stylePath: Optional[str] = None  # Full path to CSS file
    
    # Credential requirements (auto-discovered)
    required_platforms: List[str] = field(default_factory=list)  # e.g., ["pinecone", "openai"]
    optional_platforms: List[str] = field(default_factory=list)  # e.g., ["assemblyai"]
    
    # Module behavior
    sidebar_position: str = "right"  # "left" or "right"
    sidebar_width: int = 450  # Default width in pixels
    auto_load: bool = False  # Load at startup vs on-demand
    requires_auth: bool = True  # Require user authentication
    show_in_sidebar: bool = True  # Show module button in sidebar navigation
    
    # UI configuration
    floating_toggle: bool = False  # Show floating toggle button
    floating_toggle_position: str = "right"  # Position of floating toggle
    floating_toggle_default_top: int = 280  # Default top position in pixels
    main_tab: bool = False  # Show as main tab (not sidebar)
    main_tab_id: Optional[str] = None  # Main tab identifier
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)  # Other module IDs this depends on
    api_routes: List[str] = field(default_factory=list)  # API endpoints this module uses
    
    # Raw dependencies object (for V4 framework) - includes utilities, modules, frameworks
    raw_dependencies: Optional[Dict[str, Any]] = None  # Full dependencies from manifest.json
    
    # Feature flags
    features: Dict[str, bool] = field(default_factory=dict)  # Feature toggles
    
    # Thread card integration (for ThreadCardRegistry)
    thread_card_integration: Optional[Dict[str, Any]] = None  # Badge/drag-drop/realtime config
    
    # Loading configuration (for Modern Framework V4 detection)
    loading: Optional[Dict[str, Any]] = None  # Loading strategy, priority, framework version (e.g., {"framework": "v4"})
    
    # Module directory path
    module_path: str = ""  # Absolute path to module directory


class ModuleRegistry:
    """
    Self-registering module system with automatic credential discovery
    
    Pattern: Similar to ToolRegistry - modules auto-register via manifest files
    
    Usage:
        registry = ModuleRegistry()
        await registry.initialize()  # Scan modules/ directory
        
        # Get module info
        module = registry.get_module("vector_database")
        
        # Check if user has required credentials
        has_creds = registry.check_user_credentials(user_id=1, module_id="vector_database")
        
        # Get modules available to user
        available = registry.get_available_modules(user_id=1)
    """
    
    _instance = None  # Singleton instance
    
    def __new__(cls):
        """Singleton pattern - only one registry instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize module registry"""
        if self._initialized:
            return
        
        self.modules: Dict[str, ModuleManifest] = {}  # module_id → manifest
        self.module_paths: Dict[str, str] = {}  # module_id → directory path
        self.dependency_graph: Dict[str, Set[str]] = {}  # module_id → dependencies
        self._modules_loaded = False  # Track if async initialize() was called
        
        self._initialized = True
        logger.info("ModuleRegistry initialized (singleton)")
    
    def initialize(self, modules_directory: str = None):
        """
        Scan modules directory and load all module manifests
        
        Args:
            modules_directory: Path to modules folder (default: frontend/modules AND UI/modules_internal)
        
        Process:
            1. Scan modules/ directory for subdirectories
            2. Load manifest.json from each subdirectory
            3. Validate manifest schema
            4. Build dependency graph
            5. Register module
        """
        base_dir = Path(__file__).parent.parent.parent  # Go up to AI_agents root
        
        # Scan MULTIPLE module directories
        module_search_paths = []
        
        if modules_directory is None:
            # Default: Scan both frontend/modules AND UI/modules_internal
            module_search_paths.append(base_dir / "frontend" / "modules")
            module_search_paths.append(base_dir / "UI" / "modules_internal")
        else:
            module_search_paths.append(Path(modules_directory))
        
        all_module_dirs = []
        for search_path in module_search_paths:
            if search_path.exists():
                logger.info(f"Scanning modules directory: {search_path}")
                # Skip non-module directories (files, __pycache__, etc.)
                module_dirs = [
                    d for d in search_path.iterdir() 
                    if d.is_dir() 
                    and not d.name.startswith('.')  # Skip hidden dirs
                    and not d.name.startswith('__')  # Skip __pycache__
                ]
                all_module_dirs.extend(module_dirs)
                logger.info(f"  Found {len(module_dirs)} module directories")
            else:
                logger.warning(f"Modules directory not found: {search_path}")
        
        logger.info(f"Total module directories to process: {len(all_module_dirs)}")
        
        # Process all collected module directories
        module_dirs = all_module_dirs
        
        for module_dir in module_dirs:
            manifest_path = module_dir / "manifest.json"
            
            if not manifest_path.exists():
                # Only warn if it looks like it should be a module (has tools/ or implementations/)
                if (module_dir / "tools").exists() or (module_dir / "implementations").exists():
                    logger.warning(f"No manifest.json found in {module_dir.name} (has tools/implementations)")
                else:
                    logger.debug(f"Skipping non-module directory: {module_dir.name}")
                continue
            
            try:
                # Load manifest
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest_data = json.load(f)
                
                logger.debug(f"Processing module: {manifest_data.get('id', 'unknown')}")
                
                # Extract dependencies (handle both dict and list formats)
                dependencies_raw = manifest_data.get('dependencies', [])
                
                # Store raw dependencies for V4 framework (includes utilities, modules, frameworks)
                raw_dependencies_obj = dependencies_raw if isinstance(dependencies_raw, dict) else None
                
                if isinstance(dependencies_raw, dict):
                    # Modern format: {"utilities": [...], "frameworks": [...], "modules": [...]}
                    module_deps_raw = dependencies_raw.get('modules', [])
                elif isinstance(dependencies_raw, list):
                    # Legacy format: ["module1", "module2"] OR [{"type": "...", "name": "..."}]
                    module_deps_raw = dependencies_raw
                else:
                    module_deps_raw = []
                
                # Normalize dependencies to list of strings (extract 'name' from dict objects)
                module_dependencies = []
                for dep in module_deps_raw:
                    if isinstance(dep, str):
                        module_dependencies.append(dep)
                    elif isinstance(dep, dict) and 'name' in dep:
                        # Old format: {"type": "framework", "name": "sidebar-manager", ...}
                        module_dependencies.append(dep['name'])
                    # Ignore invalid dependency formats
                
                # Extract api_routes (handle both dict and list formats)
                api_routes_raw = manifest_data.get('api_routes', manifest_data.get('api_endpoints', []))
                if isinstance(api_routes_raw, dict):
                    # Modern format: {"jobs": {...}, "stages": {...}} - flatten to list of endpoint paths
                    api_routes_list = []
                    for category, endpoints in api_routes_raw.items():
                        if isinstance(endpoints, dict):
                            api_routes_list.extend(endpoints.values())
                        elif isinstance(endpoints, list):
                            api_routes_list.extend(endpoints)
                elif isinstance(api_routes_raw, list):
                    # Legacy format: ["/api/endpoint1", "/api/endpoint2"]
                    api_routes_list = api_routes_raw
                else:
                    api_routes_list = []
                
                # Extract file paths (support both root-level and files.* object)
                files_obj = manifest_data.get('files', {})
                paths_obj = manifest_data.get('paths', {})
                
                # Debug logging for inhouse-kanban
                if manifest_data['id'] == 'inhouse-kanban':
                    print(f"[DEBUG] inhouse-kanban files_obj: {files_obj}")
                    print(f"[DEBUG] inhouse-kanban paths_obj: {paths_obj}")
                
                js_file = manifest_data.get('js_file') or files_obj.get('js')
                css_file = manifest_data.get('css_file') or files_obj.get('css')
                html_file = manifest_data.get('html_file') or files_obj.get('html')
                
                scriptPath = manifest_data.get('scriptPath') or paths_obj.get('script')
                stylePath = manifest_data.get('stylePath') or paths_obj.get('style')
                htmlPath = manifest_data.get('htmlPath') or paths_obj.get('html') or paths_obj.get('sidebar_html')
                
                # Debug logging for inhouse-kanban
                if manifest_data['id'] == 'inhouse-kanban':
                    print(f"[DEBUG] inhouse-kanban js_file: {js_file}")
                    print(f"[DEBUG] inhouse-kanban scriptPath: {scriptPath}")
                
                # Create ModuleManifest object
                manifest = ModuleManifest(
                    id=manifest_data['id'],
                    name=manifest_data['name'],
                    version=manifest_data.get('version', '1.0.0'),
                    description=manifest_data.get('description', ''),
                    icon=manifest_data.get('icon', 'fa-puzzle-piece'),
                    color=manifest_data.get('color', '#6B7280'),
                    html_file=html_file,
                    js_file=js_file,
                    css_file=css_file,
                    htmlPath=htmlPath,
                    scriptPath=scriptPath,
                    stylePath=stylePath,
                    required_platforms=manifest_data.get('required_platforms', []),
                    optional_platforms=manifest_data.get('optional_platforms', []),
                    sidebar_position=manifest_data.get('sidebar_position', 'right'),
                    sidebar_width=manifest_data.get('sidebar_width', 450),
                    auto_load=manifest_data.get('auto_load', False),
                    requires_auth=manifest_data.get('requires_auth', True),
                    show_in_sidebar=manifest_data.get('show_in_sidebar', True),
                    floating_toggle=manifest_data.get('floating_toggle', False),
                    floating_toggle_position=manifest_data.get('floating_toggle_position', 'right'),
                    floating_toggle_default_top=manifest_data.get('floating_toggle_default_top', 280),
                    main_tab=manifest_data.get('main_tab', False),
                    main_tab_id=manifest_data.get('main_tab_id'),
                    dependencies=module_dependencies,  # ✅ FIX: Use extracted module dependencies
                    raw_dependencies=raw_dependencies_obj,  # ✅ NEW: Full dependencies object for V4 framework
                    api_routes=api_routes_list,  # ✅ FIX: Use extracted API routes list
                    features=manifest_data.get('features', {}),
                    thread_card_integration=manifest_data.get('thread_card_integration'),
                    loading=manifest_data.get('loading'),  # ✅ Loading config for Modern Framework V4 detection
                    module_path=str(module_dir)
                )
                
                # ✅ NEW: Environment-based module filtering (Dec 16, 2025)
                # Check if module should be enabled in current deployment environment
                if not is_module_enabled(manifest.id):
                    logger.info(f"⏸️  Skipping module '{manifest.id}' (disabled for this environment)")
                    continue  # Skip registration - module will not be available
                
                # Register module
                self.modules[manifest.id] = manifest
                self.module_paths[manifest.id] = str(module_dir)
                
                # Build dependency graph
                self.dependency_graph[manifest.id] = set(manifest.dependencies)
                
                logger.info(f"Registered module: {manifest.id} (v{manifest.version})")
                
                # Log credential requirements
                if manifest.required_platforms:
                    logger.info(f"  Required platforms: {', '.join(manifest.required_platforms)}")
                if manifest.optional_platforms:
                    logger.info(f"  Optional platforms: {', '.join(manifest.optional_platforms)}")
                
            except Exception as e:
                import traceback
                logger.error(f"Failed to load module from {module_dir.name}: {e}")
                logger.debug(f"Traceback:\n{traceback.format_exc()}")
                continue
        
        logger.info(f"Module registry scan complete: {len(self.modules)} total modules")
        # ✅ FIX: Don't set _modules_loaded = True here, so initialize() can be called multiple times
        # This allows flask_app.py to scan multiple directories (frontend/, UI/external/, UI/modules/)
        # self._modules_loaded = True  # REMOVED
    
    def _ensure_initialized(self):
        """Ensure modules are loaded (lazy initialization)"""
        if not self._modules_loaded:
            # ONLY scan UI/modules_external (external plug-and-play modules)
            # UI/modules_internal and frontend/modules are hardcoded in HTML and NOT managed by module registry
            base_dir = Path(__file__).parent.parent.parent  # Go up to AI_agents root
            
            external_dir = base_dir / "UI" / "modules_external"
            if external_dir.exists():
                logger.info(f"[ModuleRegistry] Scanning external modules: {external_dir}")
                self.initialize(str(external_dir))
            else:
                logger.warning(f"[ModuleRegistry] modules_external directory not found: {external_dir}")
    
    def get_module(self, module_id: str) -> Optional[ModuleManifest]:
        """Get module manifest by ID"""
        self._ensure_initialized()  # Lazy load
        return self.modules.get(module_id)
    
    def get_all_modules(self) -> List[ModuleManifest]:
        """Get all registered modules"""
        self._ensure_initialized()  # Lazy load
        return list(self.modules.values())
    
    def check_user_credentials(self, user_id: int, module_id: str) -> Dict[str, Any]:
        """
        Check if user has required credentials for module
        
        Args:
            user_id: User ID
            module_id: Module ID
        
        Returns:
            {
                'has_required': bool,  # All required platforms configured
                'has_optional': bool,  # Any optional platforms configured
                'missing_required': List[str],  # Missing required platforms
                'available_optional': List[str]  # Configured optional platforms
            }
        """
        from AI_infrastructure.auth.user_auth import UserAuthManager
        
        module = self.get_module(module_id)
        if not module:
            logger.warning(f"Module {module_id} not found in registry")
            return {
                'has_required': False,
                'has_optional': False,
                'missing_required': [],
                'available_optional': [],
                'error': f"Module {module_id} not found"
            }
        
        logger.debug(f"Checking credentials for module {module_id}, user {user_id}")
        logger.debug(f"  Required platforms: {module.required_platforms}")
        logger.debug(f"  Optional platforms: {module.optional_platforms}")
        
        auth_manager = UserAuthManager()
        
        # Check required platforms
        missing_required = []
        for platform in module.required_platforms:
            creds = auth_manager.get_platform_credentials(user_id, platform)
            if not creds:
                logger.debug(f"  Missing credentials for required platform: {platform}")
                missing_required.append(platform)
            else:
                logger.debug(f"  Found credentials for required platform: {platform}")
        
        # Check optional platforms
        available_optional = []
        for platform in module.optional_platforms:
            creds = auth_manager.get_platform_credentials(user_id, platform)
            if creds:
                logger.debug(f"  Found credentials for optional platform: {platform}")
                available_optional.append(platform)
            else:
                logger.debug(f"  No credentials for optional platform: {platform}")
        
        return {
            'has_required': len(missing_required) == 0,
            'has_optional': len(available_optional) > 0,
            'missing_required': missing_required,
            'available_optional': available_optional
        }
    
    def get_available_modules(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get modules available to user (has required credentials)
        
        Args:
            user_id: User ID
        
        Returns:
            List of module info dicts with credential status
        """
        available = []
        
        for module in self.modules.values():
            cred_status = self.check_user_credentials(user_id, module.id)
            
            if cred_status['has_required']:
                available.append({
                    'id': module.id,
                    'name': module.name,
                    'description': module.description,
                    'icon': module.icon,
                    'color': module.color,
                    'version': module.version,
                    'has_optional': cred_status['has_optional'],
                    'available_optional': cred_status['available_optional']
                })
        
        return available
    
    def get_modules_needing_credentials(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get modules that need credentials configured
        
        Args:
            user_id: User ID
        
        Returns:
            List of module info dicts with missing credential details
        """
        needing_creds = []
        
        for module in self.modules.values():
            cred_status = self.check_user_credentials(user_id, module.id)
            
            if not cred_status['has_required']:
                needing_creds.append({
                    'id': module.id,
                    'name': module.name,
                    'description': module.description,
                    'icon': module.icon,
                    'color': module.color,
                    'missing_required': cred_status['missing_required'],
                    'setup_guide': f"/docs/modules/{module.id}/setup"
                })
        
        return needing_creds
    
    def get_load_order(self) -> List[str]:
        """
        Get module load order based on dependencies
        
        Returns:
            List of module IDs in dependency order (dependencies first)
        
        Uses topological sort to resolve dependency graph
        """
        # Simple topological sort implementation
        visited = set()
        load_order = []
        
        def visit(module_id: str):
            if module_id in visited:
                return
            visited.add(module_id)
            
            # Visit dependencies first
            for dep_id in self.dependency_graph.get(module_id, set()):
                if dep_id in self.modules:  # Only if dependency exists
                    visit(dep_id)
            
            load_order.append(module_id)
        
        # Visit all modules
        for module_id in self.modules.keys():
            visit(module_id)
        
        return load_order
    
    def get_module_html(self, module_id: str) -> Optional[str]:
        """
        Load module HTML template
        
        Args:
            module_id: Module ID
        
        Returns:
            HTML content or None if not found
        """
        module = self.get_module(module_id)
        if not module or not module.html_file:
            return None
        
        html_path = Path(module.module_path) / module.html_file
        
        if not html_path.exists():
            logger.warning(f"HTML file not found: {html_path}")
            return None
        
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load HTML for {module_id}: {e}")
            return None
    
    def get_required_platforms_for_user(self, user_id: int) -> Set[str]:
        """
        Get all platforms required by modules user wants to use
        
        Args:
            user_id: User ID
        
        Returns:
            Set of platform names
        """
        # TODO: Track which modules user has enabled in user preferences
        # For now, return all required platforms from all modules
        
        all_platforms = set()
        for module in self.modules.values():
            all_platforms.update(module.required_platforms)
        
        return all_platforms


# Singleton getter
def get_module_registry() -> ModuleRegistry:
    """Get singleton ModuleRegistry instance"""
    return ModuleRegistry()
