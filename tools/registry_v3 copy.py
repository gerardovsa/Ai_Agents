"""
REGISTRY V3 - Direct google_workspace loading with proper credential injection

This registry:
1. Loads schemas from tools/schemas/ (with proper UTF-8 encoding)
2. Loads implementations from google_workspace/ (PRIMARY) for Google tools
3. Falls back to tools/implementations/ for other platforms
4. Supports proper credential injection (_user_id, _injected_credentials)
5. Maintains backward compatibility with existing tool definitions

Phase 2 of Agent Routes Rebuild
"""

import json
import importlib
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RegistryV3:
    """Enhanced tool registry with direct google_workspace loading"""

    def __init__(self):
        self.tools = {}
        self.implementations = {}
        self.tools_dir = Path(__file__).parent
        self.root_dir = self.tools_dir.parent
        
        # Add paths to sys.path
        if str(self.root_dir) not in sys.path:
            sys.path.insert(0, str(self.root_dir))
        if str(self.tools_dir) not in sys.path:
            sys.path.insert(0, str(self.tools_dir))
            
        # Load all components
        self._load_schemas()
        self._load_implementations()
        
        logger.info(f" Registry V3 initialized: {len(self.tools)} tools loaded")

    def _load_schemas(self) -> None:
        """Load schemas from tools/schemas/ with UTF-8 encoding"""
        schemas_dir = self.tools_dir / "schemas"
        
        if not schemas_dir.exists():
            logger.warning(f"Schemas directory not found: {schemas_dir}")
            return
        
        schema_files = list(schemas_dir.glob("*.json"))
        logger.info(f"[REGISTRY_V3] Loading {len(schema_files)} schemas from {schemas_dir}")
        
        for schema_file in schema_files:
            try:
                # Use UTF-8 with error handling for problematic files
                with open(schema_file, 'r', encoding='utf-8', errors='replace') as f:
                    schema_data = json.load(f)
                
                # Schema should have a "tools" array
                if "tools" in schema_data:
                    for tool in schema_data["tools"]:
                        tool_name = tool.get("name")
                        if tool_name:
                            self.tools[tool_name] = tool
                            logger.debug(f"  [SCHEMA] Loaded: {tool_name}")
            except Exception as e:
                logger.warning(f"Failed to load schema {schema_file.name}: {e}")
        
        logger.info(f"[SCHEMAS] Loaded {len(self.tools)} tool definitions")

    def _load_implementations(self) -> None:
        """
        Load implementations with priority:
        1. google_workspace/ for Google tools (PRIMARY)
        2. tools/implementations/ for everything else (FALLBACK)
        """
        
        # First, try google_workspace/ for Google tools
        self._load_from_google_workspace()
        
        # Then, fall back to tools/implementations/ for other platforms
        self._load_from_implementations()

    def _load_from_google_workspace(self) -> None:
        """Load from google_workspace/ directory - PRIMARY source for Google tools"""
        google_workspace_dir = self.root_dir / "google_workspace"
        
        if not google_workspace_dir.exists():
            logger.warning(f"google_workspace directory not found: {google_workspace_dir}")
            return
        
        google_modules = [
            "gmail",
            "google_docs",
            "google_forms",
            "google_sheets",
            "google_drive",
            "google_calendar",
            "google_tasks",
            "google_slides",
            "google_meet",
            "google_analytics",
            "google_cloud_run",
            "google_auth_helper"
        ]
        
        logger.info(f"[REGISTRY_V3] Loading from google_workspace/")
        
        for module_name in google_modules:
            try:
                # Import from google_workspace
                module = importlib.import_module(f"google_workspace.{module_name}")
                self.implementations[module_name] = module
                
                # Count available functions
                functions = [name for name in dir(module) 
                           if not name.startswith('_') and callable(getattr(module, name))]
                logger.info(f"   google_workspace.{module_name}: {len(functions)} functions")
                
            except ModuleNotFoundError:
                logger.debug(f"  [WARN] google_workspace.{module_name} not found (optional)")
            except ImportError as e:
                logger.debug(f"  [WARN] Error importing google_workspace.{module_name}: {e}")

    def _load_from_implementations(self) -> None:
        """Load from tools/implementations/ - FALLBACK for non-Google tools"""
        implementations_dir = self.tools_dir / "implementations"
        
        if not implementations_dir.exists():
            logger.warning(f"Implementations directory not found: {implementations_dir}")
            return
        
        impl_files = [f.stem for f in implementations_dir.glob("*.py") 
                     if f.name != "__init__.py" and f.name != "__pycache__"]
        
        logger.info(f"[REGISTRY_V3] Loading from tools/implementations/ ({len(impl_files)} modules)")
        
        # Load SQL database and meta_tools with individual function registration (high priority)
        special_modules = ["sql_database", "meta_tools"]
        for module_name in special_modules:
            if module_name in impl_files:
                try:
                    module = importlib.import_module(f"tools.implementations.{module_name}")
                    
                    # Get all functions from module and register individually
                    functions = []
                    for attr_name in dir(module):
                        if not attr_name.startswith('_'):
                            attr = getattr(module, attr_name)
                            if callable(attr) and attr_name in self.tools:
                                self.implementations[attr_name] = attr
                                functions.append(attr_name)
                    
                    icon = "[DB]" if module_name == "sql_database" else "[TOOLS]"
                    logger.info(f"   {icon}  {module_name}: {len(functions)} functions loaded")
                except Exception as e:
                    logger.warning(f"Failed to load special module {module_name}: {e}")
        
        for module_name in impl_files:
            # Skip if already loaded from google_workspace or special modules
            if module_name in self.implementations or module_name in special_modules:
                logger.debug(f"  ⊘  {module_name}: skipped (already loaded)")
                continue
            
            try:
                # Import from tools.implementations
                module = importlib.import_module(f"tools.implementations.{module_name}")
                self.implementations[module_name] = module
                
                functions = [name for name in dir(module) 
                           if not name.startswith('_') and callable(getattr(module, name))]
                logger.info(f"   tools.implementations.{module_name}: {len(functions)} functions")
                
            except ModuleNotFoundError:
                logger.debug(f"  [WARN] tools.implementations.{module_name} not found")
            except ImportError as e:
                logger.debug(f"  [WARN] Error importing tools.implementations.{module_name}: {e}")

    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get tool definition by name"""
        return self.tools.get(tool_name)

    def get_implementation(self, module_name: str):
        """Get implementation module by name"""
        return self.implementations.get(module_name)

    def list_tools_by_platform(self, platform: str) -> List[str]:
        """List all tools for a specific platform"""
        return [name for name, tool in self.tools.items() 
                if tool.get("platform") == platform]

    def get_tool_function(self, tool_name: str, function_name: str = None):
        """
        Get a function from a tool implementation
        
        Handles two implementation types:
        1. Direct function (meta_tools, sql_database) - stored as function
        2. Module with functions (google_workspace, etc.) - stored as module
        
        If function_name is None, assumes tool_name is a direct function reference
        """
        # Case 1: Direct function lookup (meta_tools, sql_database)
        if tool_name in self.implementations:
            impl = self.implementations[tool_name]
            # If it's a callable function, return it directly
            if callable(impl):
                return impl
        
        # Case 2: Module-based lookup (all other tools)
        # First, try to find the function directly in implementations
        for impl_name, impl_module in self.implementations.items():
            # Skip direct function implementations
            if callable(impl_module):
                continue
            func_name = function_name or tool_name
            if hasattr(impl_module, func_name):
                return getattr(impl_module, func_name)
        
        # Fallback: Extract module name from tool name (e.g., "gmail_send_email" -> "gmail")
        parts = tool_name.split("_")
        for i in range(len(parts), 0, -1):
            potential_module = "_".join(parts[:i])
            if potential_module in self.implementations:
                module = self.implementations[potential_module]
                # Skip direct function implementations
                if callable(module):
                    continue
                func_name = function_name or tool_name
                if hasattr(module, func_name):
                    return getattr(module, func_name)
        
        return None

    def execute_tool(self, **kwargs) -> Any:
        """
        Execute a tool with proper credential injection
        
        FIXED: Removed positional tool_name parameter to avoid conflicts
        
        Supports:
        - tool_name: name of tool to execute (REQUIRED in kwargs)
        - kwargs: all original parameters
        - _user_id: user database ID for credential injection
        - _injected_credentials: pre-fetched credentials dict
        
        Usage:
            registry.execute_tool(tool_name="gmail_send_email", to="user@example.com", ...)
        """
        # Extract tool_name from kwargs (avoids parameter conflict)
        tool_name = kwargs.pop('tool_name', None)
        
        if not tool_name:
            raise ValueError("tool_name is required in kwargs")
        
        func = self.get_tool_function(tool_name)
        if not func:
            raise ValueError(f"Tool not found: {tool_name}")
        
        try:
            return func(**kwargs)
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {e}")
            raise

    def validate_tool_parameters(self, tool_name: str, **kwargs) -> bool:
        """Validate parameters against tool schema"""
        tool = self.get_tool(tool_name)
        if not tool:
            return False
        
        schema = tool.get("parameters", {})
        
        for param_name, param_def in schema.items():
            if param_def.get("required") and param_name not in kwargs:
                logger.warning(f"Missing required parameter: {param_name}")
                return False
        
        return True

    def get_anthropic_tools(self) -> List[Dict[str, Any]]:
        """
        Get all tools formatted for Anthropic Claude API
        
        Returns:
            List of tool definitions in Anthropic format with input_schema
        """
        anthropic_tools = []
        
        for tool_name, tool in self.tools.items():
            # Convert to Anthropic format
            anthropic_tool = {
                "name": tool_name,
                "description": tool.get("description", ""),
            }
            
            # Get parameters - could be in two formats:
            # Format 1 (old): {"param1": {"type": "string", "required": true}}
            # Format 2 (new): {"type": "object", "properties": {...}, "required": [...]}
            parameters = tool.get("parameters", {})
            
            # Detect which format we have
            if parameters and "type" in parameters and parameters.get("type") == "object":
                # Format 2: Already in Anthropic format (has type: "object", properties, required)
                # Just copy it as input_schema, preserving additionalProperties if present
                input_schema = {
                    "type": parameters.get("type", "object"),
                    "properties": parameters.get("properties", {}),
                    "required": parameters.get("required", [])
                }
                
                # Preserve additionalProperties if present (needed for execute_tool proxy)
                if "additionalProperties" in parameters:
                    input_schema["additionalProperties"] = parameters["additionalProperties"]
                
                anthropic_tool["input_schema"] = input_schema
            else:
                # Format 1: Old format - convert to Anthropic format
                properties = {}
                required = []
                
                if parameters:
                    for param_name, param_def in parameters.items():
                        # Handle both string and dict parameter definitions
                        if isinstance(param_def, str):
                            # Simple string description - convert to full object
                            prop = {
                                "type": "string",
                                "description": param_def
                            }
                        elif isinstance(param_def, dict):
                            # Full parameter definition object
                            prop = {
                                "type": param_def.get("type", "string"),
                                "description": param_def.get("description", "")
                            }
                            
                            # Add enum if present
                            if "enum" in param_def:
                                prop["enum"] = param_def["enum"]
                            
                            # Add default if present
                            if "default" in param_def:
                                prop["default"] = param_def["default"]
                            
                            # Add items if present (for array types)
                            if "items" in param_def:
                                prop["items"] = param_def["items"]
                            
                            # Track required parameters
                            if param_def.get("required", False):
                                required.append(param_name)
                        else:
                            # Unknown format - skip
                            logger.warning(f"Unknown parameter format for {tool_name}.{param_name}: {type(param_def)}")
                            continue
                        
                        properties[param_name] = prop
                
                # Add input_schema with converted parameters
                anthropic_tool["input_schema"] = {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            
            anthropic_tools.append(anthropic_tool)
        
        return anthropic_tools


# Singleton instance for module-level access
_registry_instance = None


def get_registry() -> RegistryV3:
    """Get or create the singleton registry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = RegistryV3()
    return _registry_instance


# Test/debug support
if __name__ == "__main__":
    print("\n" + "="*80)
    print("REGISTRY V3 INITIALIZATION TEST")
    print("="*80 + "\n")
    
    registry = RegistryV3()
    
    print(f" Registry loaded successfully")
    print(f"   Total tools: {len(registry.tools)}")
    print(f"   Implementations loaded: {len(registry.implementations)}")
    
    print("\n[GOOGLE WORKSPACE IMPLEMENTATIONS]")
    google_impls = {k: v for k, v in registry.implementations.items() 
                   if any(k.startswith(prefix) for prefix in ['gmail', 'google', 'gsheets'])}
    for name in sorted(google_impls.keys()):
        print(f"   {name}")
    
    print("\n[SAMPLE TOOLS BY PLATFORM]")
    platforms = ["gmail", "google_docs", "google_forms", "slack", "stripe"]
    for platform in platforms:
        tools = registry.list_tools_by_platform(platform)
        if tools:
            print(f"  {platform}: {len(tools)} tools")
            for tool in tools[:3]:
                print(f"    • {tool}")
            if len(tools) > 3:
                print(f"    ... and {len(tools)-3} more")
    
    print("\n[CREDENTIAL INJECTION TEST]")
    print("  Checking if implementations support credential injection...")
    
    # Check gmail module for credential injection support
    gmail_impl = registry.get_implementation("gmail")
    if gmail_impl:
        import inspect
        
        # Check a known Gmail function
        if hasattr(gmail_impl, "gmail_send_email"):
            func = getattr(gmail_impl, "gmail_send_email")
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            
            has_kwargs = any(str(sig.parameters[p]).startswith("**") for p in params)
            print(f"  gmail_send_email parameters: {params}")
            print(f"  Supports **kwargs: {has_kwargs} ✓" if has_kwargs else f"  Supports **kwargs: {has_kwargs} ✗")
            
            if has_kwargs:
                print("   Credential injection supported via **kwargs")
    
    print("\n" + "="*80 + "\n")
