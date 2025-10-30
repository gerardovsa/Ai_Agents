"""
AGENT ROUTES V3 - Tool execution with proper credential injection

This routes module:
1. Uses RegistryV3 for tool management
2. Implements proper credential injection workflow (_user_id, _injected_credentials)
3. Supports SSE streaming for long-running operations
4. Maintains backward compatibility with existing agent_routes_V2 API
5. Enhanced error handling and logging

Phase 3 of Agent Routes Rebuild
"""

import json
import logging
from typing import Dict, Any, Optional, List, Generator
from functools import wraps
import sys
from pathlib import Path

# Add root and tools to path
root_dir = Path(__file__).parent.parent.parent  # Go up to AI_agents root
tools_dir = root_dir / "tools"
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

# Import from tools directory
import registry_v3
RegistryV3 = registry_v3.RegistryV3
get_registry = registry_v3.get_registry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes tools with proper credential injection and error handling"""

    def __init__(self, registry: Optional[RegistryV3] = None):
        self.registry = registry or get_registry()
        logger.info(f"✅ ToolExecutor initialized with registry ({len(self.registry.tools)} tools)")

    def validate_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate tool call before execution
        Returns: (is_valid: bool, error_message: Optional[str])
        """
        
        # Check tool exists
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return False, f"Tool not found: {tool_name}"
        
        # Check required parameters
        schema = tool.get("parameters", {})
        for param_name, param_def in schema.items():
            if param_def.get("required") and param_name not in parameters:
                return False, f"Missing required parameter: {param_name}"
        
        return True, None

    def inject_credentials(self, parameters: Dict[str, Any], 
                          user_id: Optional[int] = None,
                          credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add credential injection parameters to tool call
        
        Parameters:
        - parameters: original tool parameters
        - user_id: user database ID for credential lookup
        - credentials: pre-fetched credentials dict
        
        Returns: parameters dict with injected credentials
        """
        
        injected_params = parameters.copy()
        
        if user_id:
            injected_params["_user_id"] = user_id
        
        if credentials:
            injected_params["_injected_credentials"] = credentials
        
        if user_id or credentials:
            logger.debug(f"✅ Credentials injected: user_id={user_id}, has_credentials={bool(credentials)}")
        
        return injected_params

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any],
                    user_id: Optional[int] = None,
                    credentials: Optional[Dict[str, Any]] = None,
                    stream: bool = False) -> Any:
        """
        Execute a tool with credential injection
        
        Parameters:
        - tool_name: name of the tool to execute
        - parameters: tool parameters
        - user_id: optional user ID for credential injection
        - credentials: optional pre-fetched credentials
        - stream: whether to stream results for SSE
        
        Returns: tool result or generator if stream=True
        """
        
        # Validate
        is_valid, error_msg = self.validate_tool_call(tool_name, parameters)
        if not is_valid:
            logger.error(f"Tool validation failed: {error_msg}")
            raise ValueError(error_msg)
        
        # Inject credentials
        injected_params = self.inject_credentials(parameters, user_id, credentials)
        
        # Get function
        func = self.registry.get_tool_function(tool_name)
        if not func:
            raise ValueError(f"Tool implementation not found: {tool_name}")
        
        # Execute
        try:
            logger.info(f"Executing tool: {tool_name}")
            result = func(**injected_params)
            
            if stream and hasattr(result, '__iter__'):
                return result  # Return generator for SSE
            else:
                return result
                
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}", exc_info=True)
            raise

    def stream_tool_result(self, tool_name: str, parameters: Dict[str, Any],
                          user_id: Optional[int] = None,
                          credentials: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
        """
        Stream tool results as SSE events
        
        Yields: JSON strings with format:
        {
            "type": "start|progress|result|error|complete",
            "data": <result_data>,
            "timestamp": <iso_timestamp>
        }
        """
        import datetime
        
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
                for i, item in enumerate(result):
                    yield json.dumps({
                        "type": "progress",
                        "index": i,
                        "data": item,
                        "timestamp": datetime.datetime.utcnow().isoformat()
                    }) + "\n"
            else:
                # Single result
                yield json.dumps({
                    "type": "result",
                    "data": result,
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }) + "\n"
            
            yield json.dumps({
                "type": "complete",
                "timestamp": datetime.datetime.utcnow().isoformat()
            }) + "\n"
            
        except Exception as e:
            logger.error(f"Stream error for {tool_name}: {e}")
            yield json.dumps({
                "type": "error",
                "message": str(e),
                "timestamp": datetime.datetime.utcnow().isoformat()
            }) + "\n"

    def list_tools_for_platform(self, platform: str) -> List[Dict[str, Any]]:
        """Get all tools for a platform with metadata"""
        tool_names = self.registry.list_tools_by_platform(platform)
        return [self.registry.get_tool(name) for name in tool_names if self.registry.get_tool(name)]


class ToolCallProcessor:
    """Processes tool calls from Claude API (tool_use blocks)"""

    def __init__(self, executor: Optional[ToolExecutor] = None):
        self.executor = executor or ToolExecutor()

    def process_tool_call(self, tool_name: str, tool_input: Dict[str, Any],
                         user_id: Optional[int] = None,
                         credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a single tool call from Claude
        Returns: {"status": "success|error", "data": result, "error": error_msg}
        """
        try:
            result = self.executor.execute_tool(
                tool_name,
                tool_input,
                user_id=user_id,
                credentials=credentials
            )
            
            return {
                "status": "success",
                "tool": tool_name,
                "data": result
            }
        except Exception as e:
            logger.error(f"Tool call failed: {tool_name} - {e}")
            return {
                "status": "error",
                "tool": tool_name,
                "error": str(e)
            }

    def process_tool_calls(self, tool_calls: List[Dict[str, Any]],
                          user_id: Optional[int] = None,
                          credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process multiple tool calls
        Returns: {"successful": N, "failed": N, "results": [...]}
        """
        results = []
        successful = 0
        failed = 0
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_input = tool_call.get("input", {})
            
            result = self.process_tool_call(tool_name, tool_input, user_id, credentials)
            results.append(result)
            
            if result["status"] == "success":
                successful += 1
            else:
                failed += 1
        
        return {
            "successful": successful,
            "failed": failed,
            "results": results
        }


# Utility functions for Flask routes integration

def create_tool_executor() -> ToolExecutor:
    """Create and return a ToolExecutor instance"""
    return ToolExecutor()


def create_tool_processor() -> ToolCallProcessor:
    """Create and return a ToolCallProcessor instance"""
    return ToolCallProcessor()


def validate_request_credentials(request_data: Dict[str, Any]) -> tuple[Optional[int], Optional[Dict[str, Any]]]:
    """
    Extract and validate user credentials from Flask request
    Returns: (user_id, credentials_dict)
    """
    
    # Extract from request
    user_id = request_data.get("_user_id")
    credentials = request_data.get("_injected_credentials")
    
    # Optional: validate credentials against database here
    # For now, just pass through
    
    return user_id, credentials


# Test/debugging support
if __name__ == "__main__":
    print("\n" + "="*80)
    print("AGENT ROUTES V3 INITIALIZATION TEST")
    print("="*80 + "\n")
    
    # Initialize executor
    executor = ToolExecutor()
    print(f"✅ ToolExecutor initialized")
    print(f"   Registry: {len(executor.registry.tools)} tools")
    print(f"   Implementations: {len(executor.registry.implementations)} modules")
    
    # Test validation
    print("\n[VALIDATION TESTS]")
    
    # Valid tool
    is_valid, err = executor.validate_tool_call("gmail_send_email", {
        "to": "test@example.com",
        "subject": "Test",
        "body": "Test body"
    })
    print(f"  gmail_send_email with params: {'✅ VALID' if is_valid else f'❌ INVALID: {err}'}")
    
    # Missing required param
    is_valid, err = executor.validate_tool_call("gmail_send_email", {
        "to": "test@example.com"
    })
    print(f"  gmail_send_email without body: {'✅ VALID' if is_valid else f'❌ INVALID: {err}'}")
    
    # Non-existent tool
    is_valid, err = executor.validate_tool_call("fake_tool_12345", {})
    print(f"  fake_tool_12345: {'✅ VALID' if is_valid else f'❌ INVALID: {err}'}")
    
    # Test credential injection
    print("\n[CREDENTIAL INJECTION TESTS]")
    
    params = {"to": "test@example.com", "subject": "Test", "body": "Body"}
    
    # Without credentials
    injected = executor.inject_credentials(params.copy())
    print(f"  Without creds: {len(injected)} params")
    
    # With user_id
    injected = executor.inject_credentials(params.copy(), user_id=123)
    has_user_id = "_user_id" in injected
    print(f"  With user_id=123: {len(injected)} params, has _user_id: {has_user_id}")
    
    # With credentials
    creds = {"access_token": "abc123", "refresh_token": "xyz789"}
    injected = executor.inject_credentials(params.copy(), credentials=creds)
    has_creds = "_injected_credentials" in injected
    print(f"  With credentials: {len(injected)} params, has _injected_credentials: {has_creds}")
    
    # Test tool processor
    print("\n[TOOL PROCESSOR TESTS]")
    
    processor = ToolCallProcessor(executor)
    print(f"✅ ToolCallProcessor initialized")
    
    # List tools by platform
    print("\n[PLATFORM TOOLS AVAILABLE]")
    for platform in ["gmail", "slack", "stripe"]:
        tools = executor.list_tools_for_platform(platform)
        print(f"  {platform}: {len(tools)} tools")
        for tool in tools[:2]:
            print(f"    • {tool.get('name')}")
    
    print("\n" + "="*80 + "\n")
