"""
Tool Registry - Central execution engine for all platform tools
================================================================

This module provides the core tool execution system that allows AI copilots
to interact with all integrated platforms through standardized tool calls.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config import get_api_key_enhanced
    CONFIG_AVAILABLE = True
except (ImportError, AttributeError):
    CONFIG_AVAILABLE = False
    print("WARNING: config.py not available - using environment variables only")


class ToolRegistry:
    """
    Central registry for all platform tools.
    Handles tool discovery, validation, and execution.
    """
    
    def __init__(self):
        self.tools_dir = Path(__file__).parent
        self.schemas_dir = self.tools_dir / "schemas"
        self.implementations_dir = self.tools_dir / "implementations"
        
        self.tools = {}
        self.implementations = {}
        
        print("[INIT] Initializing Tool Registry...")
        self._load_schemas()
        self._load_implementations()
        print(f"[OK] Tool Registry ready - {len(self.tools)} tools loaded")
    
    def _load_schemas(self):
        """Load all tool schemas from JSON files"""
        if not self.schemas_dir.exists():
            print(f"⚠️ Schemas directory not found: {self.schemas_dir}")
            return
        
        for schema_file in self.schemas_dir.glob("*_tools.json"):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    platform_tools = json.load(f)
                    
                for tool in platform_tools.get('tools', []):
                    tool_name = tool.get('name')
                    if tool_name:
                        self.tools[tool_name] = tool
                        print(f"  [SCHEMA] Loaded: {tool_name}")
            except Exception as e:
                print(f"[ERROR] Failed to load schema {schema_file}: {e}")
    
    def _load_implementations(self):
        """Dynamically import all tool implementations"""
        if not self.implementations_dir.exists():
            print(f"⚠️ Implementations directory not found: {self.implementations_dir}")
            return
        
        for impl_file in self.implementations_dir.glob("*.py"):
            if impl_file.name == "__init__.py":
                continue
            
            try:
                module_name = impl_file.stem
                # Dynamic import
                import importlib.util
                spec = importlib.util.spec_from_file_location(module_name, impl_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                self.implementations[module_name] = module
                print(f"  [IMPL] Loaded: {module_name}")
            except Exception as e:
                print(f"[ERROR] Failed to load implementation {impl_file}: {e}")
    
    def list_tools(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all available tools, optionally filtered by platform.
        
        Args:
            platform: Optional platform name to filter by (e.g., "supabase")
        
        Returns:
            List of tool definitions
        """
        if platform:
            return [
                tool for tool in self.tools.values()
                if tool.get('platform') == platform
            ]
        return list(self.tools.values())
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the schema for a specific tool.
        
        Args:
            tool_name: Name of the tool
        
        Returns:
            Tool schema or None if not found
        """
        return self.tools.get(tool_name)
    
    def validate_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate parameters for a tool call.
        
        Args:
            tool_name: Name of the tool
            parameters: Parameters to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        tool_schema = self.get_tool_schema(tool_name)
        if not tool_schema:
            return False, f"Tool '{tool_name}' not found"
        
        tool_params = tool_schema.get('parameters', {})
        
        # Check required parameters
        for param_name, param_def in tool_params.items():
            if param_def.get('required', False) and param_name not in parameters:
                return False, f"Missing required parameter: {param_name}"
        
        # Check and convert parameter types with automatic coercion
        for param_name, param_value in parameters.items():
            if param_name not in tool_params:
                return False, f"Unknown parameter: {param_name}"
            
            expected_type = tool_params[param_name].get('type')
            actual_type = type(param_value).__name__
            
            # Simple type mapping
            type_map = {
                'string': 'str',
                'integer': 'int',
                'number': ('int', 'float'),
                'boolean': 'bool',
                'object': 'dict',
                'array': 'list'
            }
            
            if expected_type in type_map:
                valid_types = type_map[expected_type]
                
                # Attempt automatic type conversion for common cases
                if expected_type == 'integer' and actual_type == 'str':
                    try:
                        parameters[param_name] = int(param_value)
                        continue
                    except (ValueError, TypeError):
                        return False, f"Parameter '{param_name}' must be integer, cannot convert '{param_value}' to int"
                
                elif expected_type == 'number' and actual_type == 'str':
                    try:
                        parameters[param_name] = float(param_value)
                        continue
                    except (ValueError, TypeError):
                        return False, f"Parameter '{param_name}' must be number, cannot convert '{param_value}' to float"
                
                elif expected_type == 'boolean' and actual_type == 'str':
                    # Convert string to boolean
                    if param_value.lower() in ('true', '1', 'yes'):
                        parameters[param_name] = True
                        continue
                    elif param_value.lower() in ('false', '0', 'no'):
                        parameters[param_name] = False
                        continue
                    else:
                        return False, f"Parameter '{param_name}' must be boolean, cannot convert '{param_value}'"
                
                elif expected_type == 'array' and actual_type == 'str':
                    # Convert JSON string to list
                    try:
                        import json
                        parsed = json.loads(param_value)
                        if isinstance(parsed, list):
                            parameters[param_name] = parsed
                            continue
                        else:
                            return False, f"Parameter '{param_name}' must be array, JSON parsed to {type(parsed).__name__}"
                    except (ValueError, json.JSONDecodeError) as e:
                        return False, f"Parameter '{param_name}' must be array, cannot parse JSON string: {e}"
                
                elif expected_type == 'object' and actual_type == 'str':
                    # Convert JSON string to dict
                    try:
                        import json
                        parsed = json.loads(param_value)
                        if isinstance(parsed, dict):
                            parameters[param_name] = parsed
                            continue
                        else:
                            return False, f"Parameter '{param_name}' must be object, JSON parsed to {type(parsed).__name__}"
                    except (ValueError, json.JSONDecodeError) as e:
                        return False, f"Parameter '{param_name}' must be object, cannot parse JSON string: {e}"
                
                # Check type match (after conversion attempts)
                actual_type = type(parameters[param_name]).__name__
                if isinstance(valid_types, tuple):
                    if actual_type not in valid_types:
                        return False, f"Parameter '{param_name}' must be one of {valid_types}, got {actual_type}"
                elif actual_type != valid_types:
                    return False, f"Parameter '{param_name}' must be {valid_types}, got {actual_type}"
        
        return True, None
    
    def execute_tool(self, tool_name: str, user_id: Optional[int] = None, **parameters) -> Dict[str, Any]:
        """
        Execute a tool with the given parameters.
        
        ✅ NEW: Supports credential injection for Google Workspace tools
        
        Args:
            tool_name: Name of the tool to execute
            user_id: User ID for credential injection (optional)
            **parameters: Tool parameters
        
        Returns:
            Tool execution result
        """
        print(f"[EXEC] Executing tool: {tool_name}")
        if user_id:
            print(f"       User ID: {user_id} (credentials will be injected)")
        print(f"       Parameters: {parameters}")
        
        # Validate tool exists
        tool_schema = self.get_tool_schema(tool_name)
        if not tool_schema:
            return {
                'success': False,
                'error': f"Tool '{tool_name}' not found",
                'available_tools': list(self.tools.keys())
            }
        
        # Validate parameters
        is_valid, error = self.validate_parameters(tool_name, parameters)
        if not is_valid:
            return {
                'success': False,
                'error': f"Parameter validation failed: {error}",
                'tool_schema': tool_schema
            }
        
        # Get implementation
        platform = tool_schema.get('platform')
        impl_module = self.implementations.get(platform)
        
        # ✅ FIX: Try with "_tools" suffix for Microsoft platforms
        if not impl_module and platform.startswith('microsoft_'):
            impl_module = self.implementations.get(f"{platform}_tools")
        
        if not impl_module:
            return {
                'success': False,
                'error': f"Implementation not found for platform: {platform}"
            }
        
        # ✅ CREDENTIAL INJECTION: Inject user credentials for Google and Microsoft tools
        google_platforms = ['gmail', 'google_calendar', 'google_tasks', 
                           'google_forms', 'google_docs', 'google_sheets',
                           'google_slides', 'google_drive']
        
        microsoft_platforms = ['microsoft_calendar', 'microsoft_outlook', 'microsoft_teams',
                              'microsoft_onedrive', 'microsoft_sharepoint', 'microsoft_excel',
                              'microsoft_word', 'microsoft_onenote', 'microsoft_forms',
                              'microsoft_todo']
        
        if platform in google_platforms and user_id:
            print(f"🔑 Injecting Google credentials for user {user_id}")
            parameters['_user_id'] = user_id
            parameters['_injected_credentials'] = True
        elif platform in microsoft_platforms and user_id:
            print(f"🔑 Injecting Microsoft credentials for user {user_id}")
            parameters['_user_id'] = user_id
            parameters['_injected_credentials'] = True
        
        # Execute tool
        try:
            # Get the tool function from the module
            tool_function = getattr(impl_module, tool_name, None)
            if not tool_function:
                return {
                    'success': False,
                    'error': f"Function '{tool_name}' not found in {platform} implementation"
                }
            
            # Execute
            result = tool_function(**parameters)
            
            print(f"[OK] Tool execution successful: {tool_name}")
            return {
                'success': True,
                'tool': tool_name,
                'result': result
            }
            
        except Exception as e:
            print(f"[ERROR] Tool execution failed: {tool_name} - {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'tool': tool_name,
                'parameters': parameters
            }
    
    def get_platform_tools(self, platform: str) -> List[str]:
        """Get all tool names for a specific platform"""
        return [
            name for name, tool in self.tools.items()
            if tool.get('platform') == platform
        ]
    
    def get_all_platforms(self) -> List[str]:
        """Get list of all platforms with tools"""
        platforms = set()
        for tool in self.tools.values():
            platform = tool.get('platform')
            if platform:
                platforms.add(platform)
        return sorted(list(platforms))


# Global registry instance
_registry = None

def get_registry() -> ToolRegistry:
    """Get the global tool registry instance"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


# Convenience functions
def execute_tool(tool_name: str, **parameters) -> Dict[str, Any]:
    """Execute a tool using the global registry"""
    registry = get_registry()
    return registry.execute_tool(tool_name, **parameters)


def list_tools(platform: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all available tools"""
    registry = get_registry()
    return registry.list_tools(platform)


if __name__ == "__main__":
    # Test the registry
    registry = ToolRegistry()
    print("\n[STATUS] Tool Registry Status:")
    print(f"         Total tools: {len(registry.tools)}")
    print(f"         Platforms: {', '.join(registry.get_all_platforms())}")
    print("\n[TOOLS] Available tools:")
    for platform in registry.get_all_platforms():
        tools = registry.get_platform_tools(platform)
        print(f"        {platform}: {len(tools)} tools - {', '.join(tools)}")
