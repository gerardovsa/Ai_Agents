"""
REGISTRY V3 - Direct google_workspace loading with proper credential injection
This registry:
1. Loads schemas from tools/schemas/ (with proper UTF-8 encoding)
2. Loads implementations from google_workspace/ (PRIMARY) for Google tools
3. Falls back to tools/implementations/ for other platforms
4. Supports proper credential injection (_user_id, _injected_credentials)
5. Maintains backward compatibility with existing tool definitions
Phase 2 of Agent Routes Rebuild

FIXED: Parameter conflict in execute_tool() method - now only accepts **kwargs
FIXED: Microsoft tools class instance extraction - detects and uses global instances
"""
import json
import importlib
import sys
import time
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
        
        # User feedback injection tracking
        self.tool_call_count = 0
        self.last_feedback_check = 0
        self.feedback_check_interval = 1  # Check EVERY tool call (changed from 3)
        
        # Tool Intelligence Logger (Nov 27, 2025)
        # Silent learning system that tracks patterns and generates AI observations
        self.intelligence_logger = None
        try:
            from AI_infrastructure.core.tool_intelligence_logger import ToolIntelligenceLogger
            self.intelligence_logger = ToolIntelligenceLogger()
            logger.info("[INTELLIGENCE] Tool Intelligence Logger initialized")
        except Exception as e:
            logger.warning(f"[INTELLIGENCE] Could not initialize Tool Intelligence Logger: {e}")
        
        # Add paths to sys.path
        if str(self.root_dir) not in sys.path:
            sys.path.insert(0, str(self.root_dir))
        if str(self.tools_dir) not in sys.path:
            sys.path.insert(0, str(self.tools_dir))
        
        # Add UI module paths for Xero, Shopify, etc.
        ui_modules_dir = self.root_dir / "UI" / "external" / "modules"
        if ui_modules_dir.exists():
            for module_dir in ui_modules_dir.iterdir():
                if module_dir.is_dir():
                    module_path = str(module_dir)
                    if module_path not in sys.path:
                        sys.path.insert(0, module_path)
            
        # Load all components
        self._load_schemas()
        self._load_implementations()
        
        # AUTO-LOAD MODULE PLUGINS (Quote Calculator, Stock Management, etc.)
        self._load_module_plugins()
        
        logger.info(f"[OK] Registry V3 initialized: {len(self.tools)} tools loaded")

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
                
                # Get top-level platform field (if present)
                schema_platform = schema_data.get("platform")
                
                # Schema should have a "tools" array
                if "tools" in schema_data:
                    for tool in schema_data["tools"]:
                        tool_name = tool.get("name")
                        if tool_name:
                            # CRITICAL FIX: Apply schema-level platform to tools
                            if schema_platform:
                                # If tool doesn't have platform field, use schema-level
                                if "platform" not in tool:
                                    tool["platform"] = schema_platform
                                    logger.debug(f"  [SCHEMA] Set platform={schema_platform} for {tool_name}")
                                # If tool has DIFFERENT platform than schema-level, override with schema-level
                                # This fixes cases where individual tools have wrong platform (e.g., google_sheets tools marked as google_docs)
                                elif tool["platform"] != schema_platform:
                                    old_platform = tool["platform"]
                                    tool["platform"] = schema_platform
                                    logger.debug(f"  [SCHEMA] Overrode platform {old_platform} -> {schema_platform} for {tool_name}")
                            
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

    def _extract_class_instance(self, module, module_name: str):
        """
        Extract class instance from a module that uses the class pattern.
        
        Microsoft tools follow this pattern:
        1. Define a class (e.g., MicrosoftOutlookTools)
        2. Create a global instance at the bottom (e.g., microsoft_outlook_tools = MicrosoftOutlookTools())
        3. Export module-level functions with microsoft_* prefix
        
        For Microsoft tools, we need to return the MODULE (not the instance) because
        the actual tool functions are exported at module level with correct naming.
        
        For other tools (like ngrok, cloudconvert), we return the instance.
        """
        # Special case: Microsoft tools need MODULE (not instance) for correct function names
        if module_name.startswith('microsoft_'):
            logger.debug(f"       Microsoft tool: returning MODULE (not instance) for {module_name}")
            return module
        
        # For non-Microsoft tools: Look for a global instance with the module name (lowercase)
        instance_name = module_name.lower()
        if hasattr(module, instance_name):
            instance = getattr(module, instance_name)
            # Verify it's an instance (not a class or function)
            if not isinstance(instance, type) and hasattr(instance, '__class__'):
                logger.debug(f"       Found class instance: {instance_name}")
                return instance
        
        # Fallback: Return the module itself
        return module

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
                    logger.info(f"  {icon}  {module_name}: {len(functions)} functions loaded")
                except Exception as e:
                    logger.warning(f"Failed to load special module {module_name}: {e}")
        
        for module_name in impl_files:
            # Skip if already loaded from google_workspace or special modules
            if module_name in self.implementations or module_name in special_modules:
                logger.debug(f"  [OK]  {module_name}: skipped (already loaded)")
                continue
            
            try:
                # Import from tools.implementations
                module = importlib.import_module(f"tools.implementations.{module_name}")
                
                # CRITICAL FIX: Extract class instance for Microsoft tools
                # Microsoft tools have classes with global instances at the bottom
                implementation = self._extract_class_instance(module, module_name)
                
                self.implementations[module_name] = implementation
                
                # Count available functions (from instance or module)
                functions = [name for name in dir(implementation) 
                           if not name.startswith('_') and callable(getattr(implementation, name))]
                
                # Add indicator if we extracted an instance
                instance_indicator = " [instance]" if implementation is not module else ""
                logger.info(f"   tools.implementations.{module_name}: {len(functions)} functions{instance_indicator}")
                
            except ModuleNotFoundError:
                logger.debug(f"  [WARN] tools.implementations.{module_name} not found")
            except ImportError as e:
                logger.debug(f"  [WARN] Error importing tools.implementations.{module_name}: {e}")

    def _load_module_plugins(self) -> None:
        """
        Auto-discover and load tools from UI/external/modules
        
        This enables plug-and-play architecture:
        - Drop a module folder with schema/ and implementations/    tools automatically available
        - Remove a module folder    tools automatically disappear
        - No manual registration required
        
        Module structure:
            UI/external/modules/
            +-- quote-calculator/
                +-- schema/calculator_tools.json       <- Tool definitions
                +-- implementations/calculator_wrapper.py  <- Tool implementations
        """
        try:
            from tools.plugins.module_plugin_loader import load_module_plugins
            
            logger.info("[REGISTRY_V3] Loading module plugins...")
            
            plugin_data = load_module_plugins()
            
            # Add plugin tools to registry
            for tool in plugin_data["tools"]:
                tool_name = tool["name"]
                self.tools[tool_name] = tool
                logger.debug(f"  [PLUGIN] Plugin tool: {tool_name}")
            
            # Add plugin implementations
            for tool_name, impl_func in plugin_data["implementations"].items():
                self.implementations[tool_name] = impl_func
                logger.debug(f"  [PLUGIN] Plugin implementation: {tool_name}")
            
            if plugin_data["tools"]:
                logger.info(f"[PLUGINS] Loaded {len(plugin_data['tools'])} tools from {len(plugin_data['modules'])} modules")
            else:
                logger.debug("[PLUGINS] No module plugins found (this is optional)")
            
        except ImportError as e:
            logger.debug(f"[PLUGINS] Module plugin loader not available: {e}")
        except Exception as e:
            logger.warning(f"[PLUGINS] Failed to load module plugins: {e}")
            logger.debug("  (Module plugins are optional - registry will continue)")

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
        
        Handles three implementation types:
        1. Direct function (meta_tools, sql_database) - stored as function
        2. Module with functions (google_workspace, etc.) - stored as module
        3. Class instance with methods (Microsoft tools) - stored as instance
        
        If function_name is None, assumes tool_name is a direct function reference
        """
        # Case 1: Direct function lookup (meta_tools, sql_database)
        if tool_name in self.implementations:
            impl = self.implementations[tool_name]
            # If it's a callable function, return it directly
            if callable(impl):
                return impl
        
        # Case 2 & 3: Module-based or instance-based lookup
        # First, try to find the function directly in implementations
        for impl_name, impl_module in self.implementations.items():
            # Skip direct function implementations
            if callable(impl_module):
                continue
            func_name = function_name or tool_name
            if hasattr(impl_module, func_name):
                attr = getattr(impl_module, func_name)
                # If it's a method from a class instance, return it
                if callable(attr):
                    logger.debug(f"  Found {tool_name} in {impl_name}")
                    return attr
        
        # Fallback: Extract module name from tool name (e.g., "gmail_send_email" -> "gmail")
        parts = tool_name.split("_")
        for i in range(len(parts), 0, -1):
            potential_module = "_".join(parts[:i])
            if potential_module in self.implementations:
                impl = self.implementations[potential_module]
                # Skip direct function implementations
                if callable(impl):
                    continue
                func_name = function_name or tool_name
                if hasattr(impl, func_name):
                    attr = getattr(impl, func_name)
                    if callable(attr):
                        logger.debug(f"  Found {tool_name} -> {potential_module}.{func_name}")
                        return attr
        
        logger.error(f"  Tool function not found: {tool_name}")
        return None

    def execute_tool(self, **kwargs) -> Any:
        """
        Execute a tool with proper credential injection + passive user feedback injection
        
        ============================================================================
        CRITICAL WARNING - DO NOT MODIFY THIS METHOD WITHOUT UNDERSTANDING IMPACT
        ============================================================================
        
        This method is intentionally SIMPLE and delegates type conversion to
        individual tool implementations. Here's why:
        
        1. TYPE CONVERSION MUST HAPPEN IN IMPLEMENTATIONS
           - Some tools need strings (IDs, dates, text)
           - Some tools need integers (counts, limits, page numbers)
           - Some tools need mixed types
           - Automatic conversion here breaks tools that NEED strings
        
        2. META-TOOLS WILL BREAK
           - execute_tool() and get_tool_schema() are meta-tools
           - They expect string tool names, not converted values
           - Auto-conversion breaks their error messages
        
        3. THE CORRECT PATTERN
           - Wrapper functions convert types: microsoft_word_insert_table(**kwargs)
           - Or method validates: if isinstance(max_results, str): max_results = int(...)
           - Schema defines types: "type": "integer"
           - AI sends everything as strings from JSON
        
        4. EXAMPLES OF CORRECT FIXES
           
           BAD (breaks meta-tools):
           ```python
           # In this method
           if param_type == "integer":
               kwargs[param_name] = int(param_value)
           ```
           
           GOOD (in wrapper):
           ```python
           # In tools/implementations/microsoft_word_tools.py
           def microsoft_word_insert_table(**kwargs):
               if 'rows' in kwargs and isinstance(kwargs['rows'], str):
                   kwargs['rows'] = int(kwargs['rows'])
               return microsoft_word_tools.word_insert_table(**kwargs)
           ```
           
           GOOD (in method):
           ```python
           # In tools/implementations/microsoft_outlook_tools.py
           def outlook_list_messages(self, max_results: int = 50, **kwargs):
               if isinstance(max_results, str):
                   max_results = int(max_results)
               # ... rest of method
           ```
        
        5. IF YOU MUST MODIFY
           - Test ALL 611 tools
           - Test meta-tools (execute_tool, get_tool_schema)
           - Test with string AND integer parameters
           - Check error messages don't show "gmail_send_email" for unrelated tools
        
        6. USER FEEDBACK INJECTION (NOV 2025)
           - Every 3rd tool call, checks frontend textarea for user guidance
           - If found, appends to tool result as "_user_feedback" field
           - Allows user to inject instructions mid-execution (STOP, change direction, etc.)
           - Minimal overhead: ~100-200ms every 3 calls (~34% avg overhead vs 100% if every call)
        
        ============================================================================
        
        Parameters:
            tool_name (in kwargs): Name of tool to execute (REQUIRED)
            **kwargs: All tool parameters plus:
                - _user_id: Database user ID for OAuth credential injection
                - _injected_credentials: Pre-fetched credentials dict
                - _session_id: Session ID for feedback fetching
        
        Returns:
            Result from the executed tool (possibly with "_user_feedback" appended)
        
        Raises:
            ValueError: If tool_name missing or tool not found
            Exception: Any exception from the tool execution
        
        Usage:
            registry.execute_tool(
                tool_name="gmail_send_email",
                to="user@example.com",
                subject="Test",
                body="Hello",
                _user_id=1,
                _session_id="abc123"
            )
        """
        # Extract tool_name from kwargs (avoids parameter conflict with tool parameters)
        tool_name = kwargs.pop('tool_name', None)
        
        if not tool_name:
            raise ValueError("tool_name is required in kwargs")
        
        # CHECK TOOL PERMISSION (Phase 3 - User Management)
        user_id = kwargs.get('_user_id')
        if user_id:
            try:
                from AI_infrastructure.auth.permission_checker import get_permission_checker
                checker = get_permission_checker()
                checker.check_tool_permission(user_id, tool_name)
            except ImportError:
                # Permission checker not available, allow execution
                logger.warning("[PERMISSION] Permission checker not available, allowing tool execution")
            except Exception as e:
                # Permission denied - raise error to stop execution
                logger.error(f"[PERMISSION] Tool '{tool_name}' denied for user {user_id}: {e}")
                raise PermissionError(f"Permission denied for tool '{tool_name}': {e}")
        
        # Increment tool call counter
        self.tool_call_count += 1
        
        # Check if we should fetch user feedback (every Nth call)
        should_check_feedback = (
            self.tool_call_count - self.last_feedback_check >= self.feedback_check_interval
        )
        
        user_feedback = None
        if should_check_feedback:
            user_feedback = self._fetch_user_feedback(kwargs.get('_session_id'))
            self.last_feedback_check = self.tool_call_count
            if user_feedback:
                logger.info(f"[FEEDBACK] Injected user feedback at tool call #{self.tool_call_count}: {user_feedback[:50]}...")
        
        # Get the tool function (wrapper or class method)
        func = self.get_tool_function(tool_name)
        if not func:
            raise ValueError(f"Tool not found: {tool_name}")
        
        # Execute the tool with all remaining kwargs
        # Type conversion happens in the tool implementation, NOT here!
        start_time = time.time()
        try:
            result = func(**kwargs)
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Inject user feedback into result if present
            if user_feedback:
                result = self._inject_feedback_into_result(result, user_feedback)
            
            # Log tool intelligence (silent, non-blocking)
            # NOTE: This runs AFTER tool execution, never blocks user workflow
            if self.intelligence_logger and user_id:
                try:
                    # Extract metadata from kwargs
                    user_request = kwargs.get('_user_request', 'Direct tool call')
                    thread_id = kwargs.get('_thread_id')
                    session_id = kwargs.get('_session_id')
                    workflow_context = kwargs.get('_workflow_context')
                    
                    # Remove internal parameters before logging
                    tool_parameters = {k: v for k, v in kwargs.items() if not k.startswith('_')}
                    
                    self.intelligence_logger.log_tool_execution(
                        tool_name=tool_name,
                        tool_result=result,
                        user_request=user_request,
                        user_id=user_id,
                        thread_id=thread_id,
                        session_id=session_id,
                        workflow_context=workflow_context,
                        execution_time_ms=execution_time_ms,
                        tool_parameters=tool_parameters
                    )
                except Exception as log_error:
                    # Never break tool execution due to logging failure
                    logger.debug(f"[INTELLIGENCE] Logging failed for {tool_name}: {log_error}")
            
            return result
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Error executing {tool_name}: {e}")
            
            # Log intelligence even for errors (helps learn from failures)
            if self.intelligence_logger and user_id:
                try:
                    error_result = {'success': False, 'error': str(e)}
                    self.intelligence_logger.log_tool_execution(
                        tool_name=tool_name,
                        tool_result=error_result,
                        user_request=kwargs.get('_user_request', 'Direct tool call'),
                        user_id=user_id,
                        thread_id=kwargs.get('_thread_id'),
                        session_id=kwargs.get('_session_id'),
                        workflow_context=kwargs.get('_workflow_context'),
                        execution_time_ms=execution_time_ms,
                        tool_parameters={k: v for k, v in kwargs.items() if not k.startswith('_')}
                    )
                except Exception as log_error:
                    logger.debug(f"[INTELLIGENCE] Error logging failed for {tool_name}: {log_error}")
            
            raise

    def _fetch_user_feedback(self, session_id: Optional[str]) -> Optional[str]:
        """
        Fetch user feedback from backend storage
        
        User clicks SEND button → Frontend POSTs to /submit → Stored in _feedback_storage
        This method checks if feedback exists for this session.
        
        Fast check (~20ms) - doesn't wait or poll, just checks if data exists.
        
        Args:
            session_id: Session ID to identify the user
        
        Returns:
            User feedback text or None if no feedback
        """
        if not session_id:
            return None
        
        try:
            import requests
            
            # Quick check - GET request (~20ms)
            response = requests.get(
                f'http://localhost:5001/api/agent/user-feedback/check/{session_id}',
                timeout=0.1  # 100ms max - don't block tool execution
            )
            
            if response.ok:
                data = response.json()
                if data.get('has_feedback'):
                    feedback = data.get('feedback', '').strip()
                    if feedback:
                        logger.info(f"[FEEDBACK] Retrieved: {feedback[:50]}...")
                        return feedback
            
            return None
        except Exception as e:
            logger.debug(f"[FEEDBACK] No feedback available: {e}")
            return None

    def _inject_feedback_into_result(self, result: Any, feedback: str) -> Any:
        """
        Inject user feedback into tool result
        
        Supports multiple result types:
        - Dict: Adds "_user_feedback" key
        - List: Appends feedback object
        - String: Appends feedback as text
        - Other: Wraps in dict with feedback
        
        CRITICAL: Feedback is injected so AI MUST acknowledge it in next response
        
        Args:
            result: Original tool result
            feedback: User feedback text
        
        Returns:
            Result with feedback injected
        """
        if not feedback:
            return result
        
        # IMPORTANT: Format feedback with clear instruction for AI to acknowledge
        feedback_message = (
            f"🔔 USER FEEDBACK RECEIVED: {feedback}\n\n"
            f"⚠️ CRITICAL: You MUST acknowledge this feedback in your NEXT response to the user. "
            f"Start your response with: '✅ Received your feedback: [brief summary]' then adjust your behavior accordingly."
        )
        
        if isinstance(result, dict):
            # Add as new key (don't overwrite existing data)
            result['_user_feedback'] = feedback_message
            result['_feedback_requires_acknowledgment'] = True
            return result
        elif isinstance(result, list):
            # Append as last item
            result.append({
                '_user_feedback': feedback_message,
                '_feedback_requires_acknowledgment': True
            })
            return result
        elif isinstance(result, str):
            # Append to string
            return f"{result}\n\n[{feedback_message}]"
        else:
            # Wrap in dict
            return {
                '_original_result': result,
                '_user_feedback': feedback_message,
                '_feedback_requires_acknowledgment': True
            }

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
                # Copy only the fields Anthropic API supports (type, properties, required)
                # DO NOT copy additionalProperties - Anthropic's validator rejects it as custom field
                input_schema = {
                    "type": parameters.get("type", "object"),
                    "properties": parameters.get("properties", {}),
                    "required": parameters.get("required", [])
                }
                
                # NOTE: additionalProperties is NOT supported by Anthropic's JSON Schema validator
                # It gets rejected as "tools.X.custom.input_schema: JSON schema is invalid"
                # The execute_tool function handles dynamic params without needing this field
                
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
    
    print("\n[MICROSOFT IMPLEMENTATIONS]")
    microsoft_impls = {k: v for k, v in registry.implementations.items() 
                      if k.startswith('microsoft_')}
    for name in sorted(microsoft_impls.keys()):
        impl = microsoft_impls[name]
        instance_type = type(impl).__name__
        print(f"   {name} ({instance_type})")
    
    print("\n[SAMPLE TOOLS BY PLATFORM]")
    platforms = ["gmail", "google_docs", "microsoft_outlook", "microsoft_calendar", "slack"]
    for platform in platforms:
        tools = registry.list_tools_by_platform(platform)
        if tools:
            print(f"  {platform}: {len(tools)} tools")
            for tool in tools[:3]:
                print(f"    - {tool}")
            if len(tools) > 3:
                print(f"    ... and {len(tools)-3} more")
    
    print("\n[TOOL FUNCTION LOOKUP TEST]")
    test_tools = [
        "microsoft_outlook_send_email",
        "microsoft_calendar_create_event",
        "gmail_send_email"
    ]
    for tool_name in test_tools:
        func = registry.get_tool_function(tool_name)
        if func:
            print(f"   {tool_name}: {type(func).__name__}")
        else:
            print(f"     {tool_name}: NOT FOUND")
    
    print("\n[EXECUTE_TOOL TEST]")
    print("  Testing parameter handling...")
    try:
        # This should work without parameter conflict
        result = registry.execute_tool(tool_name="test_tool", param1="value1")
        print("     Should have failed (test_tool doesn't exist)")
    except ValueError as e:
        if "Tool not found" in str(e):
            print(f"   Correctly handles missing tool")
        else:
            print(f"     Unexpected error: {e}")
    except TypeError as e:
        print(f"     Parameter conflict error (BUG): {e}")
    
    print("\n" + "="*80 + "\n")