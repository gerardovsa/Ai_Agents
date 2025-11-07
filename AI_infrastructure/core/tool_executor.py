"""
Tool Executor - Validates and executes tools with credential injection
Part of V4 Modular Architecture

Responsibilities:
- Validate tool calls before execution
- Inject user credentials (_user_id, _injected_credentials)
- Execute tools from ToolRegistry
- Handle errors gracefully with detailed logging
- Support streaming results for SSE
"""

from typing import Dict, Any, Optional, List, Generator
import datetime
import json
import sys
from pathlib import Path

# Add paths first
root_dir = Path(__file__).parent.parent.parent  # Go up to AI_agents root
tools_dir = root_dir / "tools"
ai_infra_dir = Path(__file__).parent.parent  # AI_infrastructure directory

if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))
if str(ai_infra_dir) not in sys.path:
    sys.path.insert(0, str(ai_infra_dir))

# Import V4 logging (after path is set)
from utils.logger import get_logger

import registry_v3
RegistryV3 = registry_v3.RegistryV3
get_registry = registry_v3.get_registry

# Initialize logger
logger = get_logger(__name__)


class ToolExecutor:
    """
    Executes tools with proper credential injection and error handling.
    
    Features:
    - Validates tool calls before execution
    - Injects user credentials for OAuth-protected tools
    - Comprehensive logging at DEBUG and INFO levels
    - Supports streaming results for long-running operations
    - Graceful error handling with detailed context
    
    Usage:
        executor = ToolExecutor()
        result = executor.execute_tool(
            "gmail_send_email",
            {"to": "user@example.com", "subject": "Test"},
            user_id=1
        )
    """

    def __init__(self, registry: Optional[RegistryV3] = None):
        """
        Initialize ToolExecutor with registry.
        
        Args:
            registry: Optional ToolRegistry instance (creates new if not provided)
        """
        self.registry = registry or get_registry()
        logger.info(f"🔧 ToolExecutor initialized: {len(self.registry.tools)} tools available")


    def validate_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate tool call before execution.
        
        Checks:
        1. Tool exists in registry
        2. Required parameters are present
        3. Parameter types match schema (future enhancement)
        
        Args:
            tool_name: Name of the tool to validate
            parameters: Dictionary of parameters
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
            
        Example:
            is_valid, error = executor.validate_tool_call("gmail_send_email", {
                "to": "user@example.com",
                "subject": "Test"
            })
            if not is_valid:
                print(f"Validation failed: {error}")
        """
        logger.debug(f"🔍 Validating: {tool_name} with {len(parameters)} params")
        
        # Check tool exists
        tool = self.registry.get_tool(tool_name)
        if not tool:
            error_msg = f"Tool not found: {tool_name}"
            logger.error(f" {error_msg}")
            return False, error_msg
        
        # Check required parameters
        schema = tool.get("parameters", {})
        missing_params = []
        
        for param_name, param_def in schema.items():
            if param_def.get("required") and param_name not in parameters:
                missing_params.append(param_name)
        
        if missing_params:
            error_msg = f"Missing required parameters: {', '.join(missing_params)}"
            logger.error(f" {error_msg}")
            return False, error_msg
        
        logger.debug(f"Validation passed: {tool_name}")
        return True, None

    def inject_credentials(self, parameters: Dict[str, Any], 
                          user_id: Optional[int] = None,
                          credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add credential injection parameters to tool call.
        
        Credential injection enables tools to access user-specific OAuth credentials
        without passing them explicitly in the API call.
        
        Injected parameters:
        - _user_id: Database ID for credential lookup
        - _injected_credentials: Pre-fetched credentials dict
        
        Args:
            parameters: Original tool parameters
            user_id: User database ID for credential lookup
            credentials: Pre-fetched credentials dict (access_token, refresh_token, etc.)
            
        Returns:
            Parameters dict with injected credentials
            
        Example:
            params = {"to": "user@example.com"}
            injected = executor.inject_credentials(params, user_id=1)
            # injected = {"to": "user@example.com", "_user_id": 1}
        """
        logger.debug(f"🔐 Injecting credentials for user {user_id}")
        
        injected_params = parameters.copy()
        
        if user_id is not None:
            injected_params["_user_id"] = user_id
            logger.debug(f"Injected _user_id: {user_id}")
        
        if credentials:
            injected_params["_injected_credentials"] = credentials
            logger.debug(f"Injected credentials: {list(credentials.keys())}")
        
        return injected_params

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any],
                    user_id: Optional[int] = None,
                    credentials: Optional[Dict[str, Any]] = None,
                    stream: bool = False) -> Any:
        """
        Execute a tool with credential injection.
        
        Workflow:
        1. Validate tool call
        2. Inject credentials
        3. Get tool function from registry
        4. Execute with error handling
        5. Return result or generator (if stream=True)
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            user_id: Optional user ID for credential injection
            credentials: Optional pre-fetched credentials
            stream: Whether to stream results for SSE
            
        Returns:
            Tool result or generator if stream=True
            
        Raises:
            ValueError: If tool validation fails or tool not found
            Exception: If tool execution fails
            
        Example:
            result = executor.execute_tool(
                "gmail_list_messages",
                {"max_results": 10},
                user_id=1
            )
        """
        logger.info(f"⚙️ Executing tool: {tool_name}")
        logger.debug(f"Parameters: {list(parameters.keys())}")
        
        try:
            # Validate
            is_valid, error_msg = self.validate_tool_call(tool_name, parameters)
            if not is_valid:
                logger.error(f" Validation failed: {error_msg}")
                raise ValueError(error_msg)
            
            # Inject credentials
            injected_params = self.inject_credentials(parameters, user_id, credentials)
            
            # Get function
            func = self.registry.get_tool_function(tool_name)
            if not func:
                error_msg = f"Tool implementation not found: {tool_name}"
                logger.error(f" {error_msg}")
                raise ValueError(error_msg)
            
            logger.debug(f"📦 Retrieved function: {func.__name__}")
            
            # Execute
            result = func(**injected_params)
            
            logger.info(f"Execution successful: {tool_name}")
            logger.debug(f"Result type: {type(result).__name__}")
            
            if stream and hasattr(result, '__iter__'):
                logger.debug("🌊 Returning generator for streaming")
                return result  # Return generator for SSE
            else:
                return result
                
        except Exception as e:
            logger.error(f" Execution failed: {tool_name} - {e}", exc_info=True)
            raise

    def stream_tool_result(self, tool_name: str, parameters: Dict[str, Any],
                          user_id: Optional[int] = None,
                          credentials: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
        """
        Stream tool results as SSE events.
        
        Event types:
        - start: Tool execution started
        - progress: Intermediate results (if tool yields)
        - result: Final result (if tool returns)
        - complete: Execution finished successfully
        - error: Execution failed
        
        Args:
            tool_name: Name of the tool
            parameters: Tool parameters
            user_id: Optional user ID
            credentials: Optional credentials
            
        Yields:
            JSON strings with format:
            {
                "type": "start|progress|result|error|complete",
                "data": <result_data>,
                "timestamp": <iso_timestamp>
            }
            
        Example:
            for event in executor.stream_tool_result("long_running_tool", params):
                print(event)  # Each line is a JSON event
        """
        logger.info(f"🌊 Starting stream: {tool_name}")
        
        try:
            # Execute tool
            result = self.execute_tool(tool_name, parameters, user_id, credentials, stream=True)
            
            yield json.dumps({
                "type": "start",
                "tool": tool_name,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }) + "\n"
            
            # If result is iterable, stream each item
            if hasattr(result, '__iter__') and not isinstance(result, (str, dict)):
                logger.debug("🔄 Streaming iterable results")
                for i, item in enumerate(result):
                    yield json.dumps({
                        "type": "progress",
                        "index": i,
                        "data": item,
                        "timestamp": datetime.datetime.utcnow().isoformat()
                    }) + "\n"
                    logger.debug(f"📦 Yielded progress event {i}")
            else:
                # Single result
                logger.debug("📦 Yielding single result")
                yield json.dumps({
                    "type": "result",
                    "data": result,
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }) + "\n"
            
            yield json.dumps({
                "type": "complete",
                "timestamp": datetime.datetime.utcnow().isoformat()
            }) + "\n"
            
            logger.info(f"Stream complete: {tool_name}")
            
        except Exception as e:
            logger.error(f" Stream error: {tool_name} - {e}", exc_info=True)
            yield json.dumps({
                "type": "error",
                "message": str(e),
                "timestamp": datetime.datetime.utcnow().isoformat()
            }) + "\n"

    def list_tools_for_platform(self, platform: str) -> List[Dict[str, Any]]:
        """
        Get all tools for a platform with metadata.
        
        Args:
            platform: Platform name (e.g., 'google', 'microsoft')
            
        Returns:
            List of tool metadata dicts
            
        Example:
            tools = executor.list_tools_for_platform('google')
            print(f"Found {len(tools)} Google tools")
        """
        logger.debug(f"📋 Listing tools for platform: {platform}")
        
        tool_names = self.registry.list_tools_by_platform(platform)
        tools = [self.registry.get_tool(name) for name in tool_names if self.registry.get_tool(name)]
        
        logger.debug(f"Found {len(tools)} tools for {platform}")
        return tools


# Export
__all__ = ['ToolExecutor']
