"""
Module Plugin Loader - Auto-discovers and loads tools from UI/external/modules

This loader enables plug-and-play architecture:
- Drop a module folder with schema/ and implementations/ → tools automatically available
- Remove a module folder → tools automatically disappear
- No manual registration required

Architecture:
    UI/external/modules/
    ├── quote-calculator/
    │   ├── schema/calculator_tools.json       ← Tool definitions (AI-readable)
    │   └── implementations/calculator_wrapper.py  ← Tool implementations
    └── stock-management/
        ├── schema/stock_tools.json
        └── implementations/stock_wrapper.py

Usage:
    from tools.plugins.module_plugin_loader import ModulePluginLoader
    loader = ModulePluginLoader()
    plugin_data = loader.get_all_module_tools()
    
    # Returns:
    # {
    #   "tools": [...],  # List of tool schemas
    #   "implementations": {...}  # Dict of function implementations
    # }

FILE: tools/plugins/module_plugin_loader.py
PURPOSE: Auto-discover and load AI tools from UI modules
LAST MODIFIED: 2025-11-04 - Initial creation
"""

import sys
import json
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Callable

class ModulePluginLoader:
    """Loads tools from self-contained UI module folders"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent.parent
        self.modules_dir = self.root_dir / "UI" / "modules_external"
        self.loaded_modules = {}
        
        print(f"[PLUGIN] [Module Plugin] Initialized")
        print(f"   Modules directory: {self.modules_dir}")
    
    def discover_modules_with_tools(self) -> List[str]:
        """
        Find all modules that have schema/ and implementations/ folders
        
        Returns:
            List of module IDs (folder names)
        """
        modules_with_tools = []
        
        if not self.modules_dir.exists():
            print(f"    [Module Plugin] Modules directory not found: {self.modules_dir}")
            return modules_with_tools
        
        for module_dir in self.modules_dir.iterdir():
            if not module_dir.is_dir():
                continue
            
            # Skip hidden folders and node_modules
            if module_dir.name.startswith('.') or module_dir.name == 'node_modules':
                continue
            
            # Check if module has schema/ and implementations/
            schema_dir = module_dir / "schema"
            impl_dir = module_dir / "implementations"
            
            if schema_dir.exists() and impl_dir.exists():
                modules_with_tools.append(module_dir.name)
                print(f"OK [Module Plugin] Discovered module: {module_dir.name}")
        
        return modules_with_tools
    
    def load_module_schemas(self, module_id: str) -> List[Dict[str, Any]]:
        """
        Load all tool schemas from a module's schema/ folder
        
        Args:
            module_id: Module folder name (e.g. 'quote-calculator')
        
        Returns:
            List of tool schemas
        """
        module_dir = self.modules_dir / module_id
        schema_dir = module_dir / "schema"
        
        if not schema_dir.exists():
            return []
        
        all_tools = []
        
        for schema_file in schema_dir.glob("*.json"):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
                    
                    if "tools" in schema_data:
                        tools = schema_data["tools"]
                        all_tools.extend(tools)
                        print(f"     [{module_id}] Loaded schema: {schema_file.name} ({len(tools)} tools)")
                    else:
                        print(f"      [{module_id}] Schema has no 'tools' array: {schema_file.name}")
                        
            except json.JSONDecodeError as e:
                print(f"     [{module_id}] Invalid JSON in {schema_file.name}: {e}")
            except Exception as e:
                print(f"     [{module_id}] Failed to load {schema_file.name}: {e}")
        
        return all_tools
    
    def load_module_implementations(self, module_id: str, tool_names: List[str]) -> Dict[str, Callable]:
        """
        Load tool implementations from a module's implementations/ folder
        
        Args:
            module_id: Module folder name
            tool_names: List of tool names from schemas
        
        Returns:
            Dict mapping tool names to implementation functions
        """
        module_dir = self.modules_dir / module_id
        impl_dir = module_dir / "implementations"
        
        if not impl_dir.exists():
            return {}
        
        implementations = {}
        
        # Add ROOT directory to Python path (for inhouse_modules imports)
        if str(self.root_dir) not in sys.path:
            sys.path.insert(0, str(self.root_dir))
        
        # Add inhouse_modules directory to Python path (for shopify_calculators imports)
        inhouse_modules_dir = self.root_dir / "inhouse_modules"
        if inhouse_modules_dir.exists() and str(inhouse_modules_dir) not in sys.path:
            sys.path.insert(0, str(inhouse_modules_dir))
        
        # Add implementations directory to Python path (temporarily)
        sys.path.insert(0, str(impl_dir))
        
        try:
            # Look for ALL wrapper files (calculator_wrapper.py, query_library_wrapper.py, etc.)
            wrapper_files = list(impl_dir.glob("*_wrapper.py"))
            
            if not wrapper_files:
                print(f"      [{module_id}] No *_wrapper.py found in implementations/")
                return {}
            
            # Load ALL wrapper files (not just the first one)
            for wrapper_file in wrapper_files:
                module_name = wrapper_file.stem
                
                try:
                    # Import the wrapper module
                    spec = importlib.util.spec_from_file_location(module_name, wrapper_file)
                    wrapper_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(wrapper_module)
                    
                    print(f"  🔧 [{module_id}] Loaded wrapper: {wrapper_file.name}")
                    
                    # Map tool names to wrapper functions
                    for tool_name in tool_names:
                        # Skip if already mapped (from previous wrapper)
                        if tool_name in implementations:
                            continue
                        
                        # Try to find function in wrapper module
                        # Tool name format: "quote_calculator_business_cards"
                        # Function name format: "business_cards" or "calculate_business_cards"
                        
                        # Try exact match first
                        if hasattr(wrapper_module, tool_name):
                            implementations[tool_name] = getattr(wrapper_module, tool_name)
                            print(f"    ✓ Mapped: {tool_name} → {tool_name}()")
                            continue
                        
                        # Try removing module prefix
                        # "quote_calculator_business_cards" → "business_cards"
                        if '_' in tool_name:
                            parts = tool_name.split('_')
                            # Try last part
                            func_name = parts[-1]
                            if hasattr(wrapper_module, func_name):
                                implementations[tool_name] = getattr(wrapper_module, func_name)
                                print(f"    ✓ Mapped: {tool_name} → {func_name}()")
                                continue
                            
                            # Try last two parts joined
                            if len(parts) >= 2:
                                func_name = '_'.join(parts[-2:])
                                if hasattr(wrapper_module, func_name):
                                    implementations[tool_name] = getattr(wrapper_module, func_name)
                                    print(f"    ✓ Mapped: {tool_name} → {func_name}()")
                                    continue
                
                except Exception as e:
                    print(f"     [{module_id}] Failed to load {wrapper_file.name}: {e}")
            
            # Report unmapped tools
            for tool_name in tool_names:
                if tool_name not in implementations:
                    print(f"        No implementation found for: {tool_name}")
        
        except Exception as e:
            print(f"     [{module_id}] Failed to load implementations: {e}")
        
        finally:
            # Remove from path
            if str(impl_dir) in sys.path:
                sys.path.remove(str(impl_dir))
        
        return implementations
    
    def load_module_tools(self, module_id: str) -> Dict[str, Any]:
        """
        Load all tools (schemas + implementations) from a specific module
        
        Args:
            module_id: Module folder name
        
        Returns:
            Dict with 'tools' (list) and 'implementations' (dict)
        """
        print(f"\n[LOAD] [Module Plugin] Loading module: {module_id}")
        
        # Load schemas
        tools = self.load_module_schemas(module_id)
        
        if not tools:
            print(f"      [{module_id}] No tools found in schemas")
            return {"tools": [], "implementations": {}}
        
        # Extract tool names
        tool_names = [tool["name"] for tool in tools]
        
        # Load implementations
        implementations = self.load_module_implementations(module_id, tool_names)
        
        result = {
            "tools": tools,
            "implementations": implementations
        }
        
        self.loaded_modules[module_id] = result
        
        print(f"  OK [{module_id}] Loaded {len(tools)} tools, {len(implementations)} implementations")
        
        return result
    
    def get_all_module_tools(self) -> Dict[str, Any]:
        """
        Load tools from all discovered modules
        
        Returns:
            Dict with:
            - 'tools': Combined list of all tool schemas
            - 'implementations': Combined dict of all implementations
            - 'modules': Dict of per-module data
        """
        print(f"\n[DISCOVER] [Module Plugin] Discovering modules...")
        
        all_tools = []
        all_implementations = {}
        modules_data = {}
        
        # Discover modules
        modules = self.discover_modules_with_tools()
        
        if not modules:
            print(f"  ℹ️  No modules with tools found")
            return {
                "tools": [],
                "implementations": {},
                "modules": {}
            }
        
        # Load each module
        for module_id in modules:
            module_data = self.load_module_tools(module_id)
            
            all_tools.extend(module_data["tools"])
            all_implementations.update(module_data["implementations"])
            modules_data[module_id] = module_data
        
        result = {
            "tools": all_tools,
            "implementations": all_implementations,
            "modules": modules_data
        }
        
        print(f"\nOK [Module Plugin] Summary:")
        print(f"   Modules loaded: {len(modules)}")
        print(f"   Total tools: {len(all_tools)}")
        print(f"   Total implementations: {len(all_implementations)}")
        
        return result


# Convenience function for registry
def load_module_plugins() -> Dict[str, Any]:
    """
    Convenience function to load all module plugins
    Used by Registry V3
    """
    loader = ModulePluginLoader()
    return loader.get_all_module_tools()


if __name__ == "__main__":
    # Test the loader
    print("=" * 60)
    print("Testing Module Plugin Loader")
    print("=" * 60)
    
    loader = ModulePluginLoader()
    data = loader.get_all_module_tools()
    
    print("\n" + "=" * 60)
    print("Results:")
    print("=" * 60)
    print(f"Tools loaded: {len(data['tools'])}")
    print(f"Implementations loaded: {len(data['implementations'])}")
    print(f"Modules: {list(data['modules'].keys())}")
    
    if data['tools']:
        print("\nTool names:")
        for tool in data['tools']:
            impl_status = "OK" if tool['name'] in data['implementations'] else "  "
            print(f"  {impl_status} {tool['name']}")

