"""
Module Blueprint Loader - Auto-discovers and registers Flask blueprints from UI modules

This enables plug-and-play Flask routes:
- Drop a module with routes/ folder → Flask routes automatically available
- Remove module → Flask routes automatically disappear
- No manual blueprint registration required

Architecture:
    Flask App Startup
        ↓
    module_blueprint_loader.load_module_blueprints(app)
        ↓
    Discovers: UI/external/modules/*/routes/
        ↓
    Imports and registers blueprints automatically

FILE: AI_infrastructure/core/module_blueprint_loader.py
PURPOSE: Auto-discover and register Flask blueprints from UI modules
DEPENDENCIES:
- Flask app instance
- UI/external/modules/*/routes/*.py files

EXPORTS:
- load_module_blueprints(app) - Main function to load all module blueprints

LAST MODIFIED: 2025-11-04 - Initial creation
"""

import sys
import importlib.util
from pathlib import Path
from typing import List
from flask import Flask, Blueprint

import logging
logger = logging.getLogger(__name__)


class ModuleBlueprintLoader:
    """Loads Flask blueprints from self-contained UI module folders"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.root_dir = Path(__file__).parent.parent.parent
        self.modules_dir = self.root_dir / "UI" / "external" / "modules"
        self.loaded_blueprints = []
        
        logger.info(f"🔌 [Module Blueprints] Initialized")
        logger.info(f"   Modules directory: {self.modules_dir}")
    
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
        Load and register all module blueprints
        
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
            blueprints = self.load_module_blueprints(module_id)
            
            for blueprint in blueprints:
                self.register_blueprint(blueprint, module_id)
                total_blueprints += 1
        
        logger.info(f"\n✅ [Module Blueprints] Summary:")
        logger.info(f"   Modules loaded: {len(modules)}")
        logger.info(f"   Blueprints registered: {total_blueprints}")
        
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
