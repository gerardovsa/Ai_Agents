"""
Module Blueprint Loader - Auto-discovers and registers Flask blueprints from UI modules

This enables plug-and-play Flask routes:
- Drop a module with routes/ folder → Flask routes automatically available
- Module with manifest.json → Frontend UI also auto-registered
- Remove module → Flask routes AND frontend automatically disappear
- No manual blueprint registration required

Architecture:
    Flask App Startup
        ↓
    module_blueprint_loader.load_module_blueprints(app)
        ↓
    Discovers: UI/modules_external/*/routes/
        ↓
    Imports and registers blueprints automatically
        ↓
    Checks for manifest.json → Registers with ModuleRegistry (frontend)

FILE: AI_infrastructure/core/module_blueprint_loader.py
PURPOSE: Auto-discover and register Flask blueprints AND frontend modules
DEPENDENCIES:
- Flask app instance
- UI/modules_external/*/routes/*.py files
- UI/modules_external/*/manifest.json (optional, for frontend integration)

EXPORTS:
- load_module_blueprints(app) - Main function to load all module blueprints

LAST MODIFIED: 2025-12-07 - Added frontend integration via ModuleRegistry
"""

import sys
import importlib.util
import json
from pathlib import Path
from typing import List, Dict, Optional
from flask import Flask, Blueprint

import logging
logger = logging.getLogger(__name__)


class ModuleBlueprintLoader:
    """Loads Flask blueprints from self-contained UI module folders AND registers frontend modules"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.root_dir = Path(__file__).parent.parent.parent
        self.modules_dir = self.root_dir / "UI" / "modules_external"
        self.loaded_blueprints = []
        self.registered_modules = []  # Track modules registered with ModuleRegistry
        
        logger.info(f"🔌 [Module Blueprints] Initialized")
        logger.info(f"   Modules directory: {self.modules_dir}")
    
    def load_manifest(self, module_id: str) -> Optional[Dict]:
        """
        Load manifest.json for a module (if exists)
        
        Args:
            module_id: Module folder name
            
        Returns:
            Manifest dict or None if not found
        """
        manifest_path = self.modules_dir / module_id / "manifest.json"
        
        if not manifest_path.exists():
            return None
            
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                return manifest
        except Exception as e:
            logger.warning(f"  ⚠️  [{module_id}] Failed to load manifest.json: {e}")
            return None
    
    def discover_modules_with_routes(self) -> List[str]:
        """
        Find all modules that have a routes/ folder
        
        Returns:
            List of module IDs (folder names)
        """
        modules_with_routes = []
        
        if not self.modules_dir.exists():
            logger.warning(f"⚠️  [Module Blueprints] Modules directory not found: {self.modules_dir}")
            return modules_with_routes
        
        for module_dir in self.modules_dir.iterdir():
            if not module_dir.is_dir():
                continue
            
            # Skip hidden folders
            if module_dir.name.startswith('.') or module_dir.name == 'node_modules':
                continue
            
            # Check if module has routes/ folder
            routes_dir = module_dir / "routes"
            
            if routes_dir.exists() and routes_dir.is_dir():
                modules_with_routes.append(module_dir.name)
                logger.debug(f"✅ [Module Blueprints] Discovered: {module_dir.name}")
        
        return modules_with_routes
    
    def load_module_blueprints(self, module_id: str) -> List[Blueprint]:
        """
        Load all Flask blueprints from a module's routes/ folder
        
        Args:
            module_id: Module folder name (e.g. 'quote-calculator')
        
        Returns:
            List of Flask Blueprint instances
        """
        module_dir = self.modules_dir / module_id
        routes_dir = module_dir / "routes"
        
        if not routes_dir.exists():
            return []
        
        blueprints = []
        
        logger.info(f"📦 [Module Blueprints] Loading: {module_id}")
        
        # Add routes directory to Python path (temporarily)
        sys.path.insert(0, str(routes_dir))
        
        try:
            # Look for Python files in routes/
            route_files = [f for f in routes_dir.glob("*.py") 
                          if f.name != "__init__.py" and not f.name.startswith("_")]
            
            if not route_files:
                logger.warning(f"  ⚠️  [{module_id}] No route files found in routes/")
                return []
            
            for route_file in route_files:
                try:
                    # Import the route module
                    module_name = route_file.stem
                    spec = importlib.util.spec_from_file_location(module_name, route_file)
                    route_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(route_module)
                    
                    logger.info(f"  📄 [{module_id}] Loaded: {route_file.name}")
                    
                    # Find all Blueprint objects in the module
                    for attr_name in dir(route_module):
                        attr = getattr(route_module, attr_name)
                        
                        # Check if it's a Blueprint instance
                        if isinstance(attr, Blueprint):
                            blueprints.append(attr)
                            logger.info(f"    ✓ Found blueprint: {attr.name} (prefix: {attr.url_prefix or '/'})")
                
                except Exception as e:
                    logger.error(f"  ❌ [{module_id}] Failed to load {route_file.name}: {e}")
        
        finally:
            # Remove from path
            if str(routes_dir) in sys.path:
                sys.path.remove(str(routes_dir))
        
        return blueprints
    
    def register_with_module_registry(self, module_id: str, manifest: Dict) -> None:
        """
        Register module with ModuleRegistry for frontend integration
        
        This ensures modules with routes/ folders also get proper frontend UI
        integration (tab containers, sidebar buttons, etc.)
        
        Args:
            module_id: Module folder name
            manifest: Module manifest dict
        """
        try:
            from AI_infrastructure.core.module_registry import get_module_registry, ModuleManifest
            
            registry = get_module_registry()
            
            # Check if module already registered (avoid duplicates)
            if module_id in registry.modules:
                logger.debug(f"  ℹ️  [{module_id}] Already registered with ModuleRegistry")
                return
            
            # Extract file paths (support both root-level and files.* object)
            files_obj = manifest.get('files', {})
            paths_obj = manifest.get('paths', {})
            
            js_file = manifest.get('js_file') or files_obj.get('js')
            css_file = manifest.get('css_file') or files_obj.get('css')
            html_file = manifest.get('html_file') or files_obj.get('html')
            
            scriptPath = manifest.get('scriptPath') or paths_obj.get('script') or paths_obj.get('js')
            stylePath = manifest.get('stylePath') or paths_obj.get('style') or paths_obj.get('css')
            htmlPath = manifest.get('htmlPath') or paths_obj.get('html')
            
            # Extract capabilities for dashboard/sidebar integration
            capabilities = manifest.get('capabilities', {})
            dashboard_cap = capabilities.get('dashboard', {})
            sidebar_cap = capabilities.get('sidebar', {})
            
            # Determine main_tab settings
            main_tab = dashboard_cap.get('enabled', False)
            main_tab_id = dashboard_cap.get('tab_id') or manifest.get('id')
            
            # Extract dependencies
            dependencies_raw = manifest.get('dependencies', [])
            raw_dependencies_obj = dependencies_raw if isinstance(dependencies_raw, dict) else None
            
            if isinstance(dependencies_raw, dict):
                module_deps = dependencies_raw.get('modules', [])
            elif isinstance(dependencies_raw, list):
                module_deps = dependencies_raw
            else:
                module_deps = []
            
            # Create ModuleManifest object
            module_path = self.modules_dir / module_id
            module_manifest = ModuleManifest(
                id=manifest['id'],
                name=manifest['name'],
                version=manifest.get('version', '1.0.0'),
                description=manifest.get('description', ''),
                icon=manifest.get('icon', 'fa-puzzle-piece'),
                color=manifest.get('color', manifest.get('colors', {}).get('primary', '#6B7280')),
                html_file=html_file,
                js_file=js_file,
                css_file=css_file,
                htmlPath=htmlPath,
                scriptPath=scriptPath,
                stylePath=stylePath,
                required_platforms=manifest.get('required_platforms', []),
                optional_platforms=manifest.get('optional_platforms', []),
                sidebar_position=sidebar_cap.get('side', 'right'),
                sidebar_width=int(sidebar_cap.get('width', '450px').replace('px', '')),
                auto_load=manifest.get('auto_load', False),
                requires_auth=manifest.get('requires_auth', True),
                show_in_sidebar=sidebar_cap.get('enabled', True),
                floating_toggle=sidebar_cap.get('toggle_button', {}).get('enabled', False),
                floating_toggle_position=sidebar_cap.get('toggle_button', {}).get('position', 'right'),
                floating_toggle_default_top=sidebar_cap.get('toggle_button', {}).get('default_top', 280),
                main_tab=main_tab,
                main_tab_id=main_tab_id,
                dependencies=module_deps,
                raw_dependencies=raw_dependencies_obj,
                api_routes=manifest.get('api_routes', []),
                features=manifest.get('features', {}),
                thread_card_integration=manifest.get('thread_card_integration'),
                loading=manifest.get('loading'),
                module_path=str(module_path)
            )
            
            # Register module directly with registry
            registry.modules[module_id] = module_manifest
            registry.module_paths[module_id] = str(module_path)
            registry.dependency_graph[module_id] = set(module_manifest.dependencies)
            
            self.registered_modules.append(module_id)
            logger.info(f"  ✅ [{module_id}] Registered with ModuleRegistry (frontend integration enabled)")
            
        except Exception as e:
            logger.warning(f"  ⚠️  [{module_id}] Failed to register with ModuleRegistry: {e}")
            logger.debug(f"       Error details: {e}", exc_info=True)
            # Non-fatal - backend routes still work
    
    def register_blueprint(self, blueprint: Blueprint, module_id: str) -> None:
        """
        Register a blueprint with the Flask app
        
        Args:
            blueprint: Flask Blueprint instance
            module_id: Module ID (for logging)
        """
        try:
            self.app.register_blueprint(blueprint)
            self.loaded_blueprints.append({
                "module_id": module_id,
                "blueprint_name": blueprint.name,
                "url_prefix": blueprint.url_prefix or "/"
            })
            logger.info(f"  ✅ [{module_id}] Registered: {blueprint.name}")
            
        except Exception as e:
            logger.error(f"  ❌ [{module_id}] Failed to register blueprint {blueprint.name}: {e}")
    
    def load_all(self) -> int:
        """
        Load and register all module blueprints + frontend integration
        
        Returns:
            Number of blueprints loaded
        """
        logger.info("\n🔍 [Module Blueprints] Discovering modules...")
        
        modules = self.discover_modules_with_routes()
        
        if not modules:
            logger.info("  ℹ️  No modules with routes found")
            return 0
        
        total_blueprints = 0
        
        for module_id in modules:
            # Load manifest (if exists)
            manifest = self.load_manifest(module_id)
            
            # Load and register Flask blueprints (backend)
            blueprints = self.load_module_blueprints(module_id)
            
            for blueprint in blueprints:
                self.register_blueprint(blueprint, module_id)
                total_blueprints += 1
            
            # If module has manifest, register with ModuleRegistry (frontend)
            if manifest:
                self.register_with_module_registry(module_id, manifest)
        
        logger.info(f"\n✅ [Module Blueprints] Summary:")
        logger.info(f"   Modules loaded: {len(modules)}")
        logger.info(f"   Blueprints registered (backend): {total_blueprints}")
        logger.info(f"   Modules registered (frontend): {len(self.registered_modules)}")
        
        return total_blueprints
    
    def get_loaded_blueprints(self) -> List[dict]:
        """Get list of loaded blueprints with metadata"""
        return self.loaded_blueprints


# ==================== CONVENIENCE FUNCTION ====================

def load_module_blueprints(app: Flask) -> int:
    """
    Convenience function to load all module blueprints
    
    Usage in Flask app:
        from AI_infrastructure.core.module_blueprint_loader import load_module_blueprints
        
        app = Flask(__name__)
        # ... configure app ...
        
        # Auto-load module blueprints
        load_module_blueprints(app)
    
    Args:
        app: Flask application instance
    
    Returns:
        Number of blueprints loaded
    """
    loader = ModuleBlueprintLoader(app)
    return loader.load_all()


# ==================== TESTING ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Module Blueprint Loader")
    print("=" * 60)
    
    # Create a test Flask app
    from flask import Flask
    app = Flask(__name__)
    
    # Load module blueprints
    loader = ModuleBlueprintLoader(app)
    count = loader.load_all()
    
    print("\n" + "=" * 60)
    print("Results:")
    print("=" * 60)
    print(f"Blueprints loaded: {count}")
    
    if loader.loaded_blueprints:
        print("\nLoaded blueprints:")
        for bp in loader.loaded_blueprints:
            print(f"  • {bp['blueprint_name']} (from {bp['module_id']})")
            print(f"    URL prefix: {bp['url_prefix']}")
    
    print("\nFlask routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.methods} {rule.rule} → {rule.endpoint}")
