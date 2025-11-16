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
from datetime import datetime, timedelta

# Add root and tools to path
root_dir = Path(__file__).parent.parent.parent  # Go up to AI_agents root
tools_dir = root_dir / "tools"
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

# Import db path helpers
sys.path.insert(0, str(root_dir / 'AI_infrastructure'))
from shared.database_utils import (
    get_database_connection,
    get_synergy_sessions_connection,
    is_using_supabase
)

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
        logger.info(f" ToolExecutor initialized with registry ({len(self.registry.tools)} tools)")

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
            logger.debug(f" Credentials injected: user_id={user_id}, has_credentials={bool(credentials)}")
        
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
            logger.info(f"🔧 Executing tool: {tool_name}")
            result = func(**injected_params)
            
            # Check if result is a confirmation request (UNIVERSAL CONFIRMATION SYSTEM)
            if isinstance(result, dict) and result.get('status') == 'confirmation_required':
                logger.info(f"⏸️  Tool {tool_name} requested user confirmation")
                logger.debug(f"   Confirmation details: {result.get('operation_summary', 'N/A')}")
                # Return confirmation request as-is (agent will handle it)
                return result
            
            if stream and hasattr(result, '__iter__'):
                return result  # Return generator for SSE
            else:
                return result
                
        except Exception as e:
            logger.error(f"❌ Tool execution failed for {tool_name}: {e}", exc_info=True)
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
    print(f" ToolExecutor initialized")
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
    print(f"  gmail_send_email with params: {' VALID' if is_valid else f' INVALID: {err}'}")
    
    # Missing required param
    is_valid, err = executor.validate_tool_call("gmail_send_email", {
        "to": "test@example.com"
    })
    print(f"  gmail_send_email without body: {' VALID' if is_valid else f' INVALID: {err}'}")
    
    # Non-existent tool
    is_valid, err = executor.validate_tool_call("fake_tool_12345", {})
    print(f"  fake_tool_12345: {' VALID' if is_valid else f' INVALID: {err}'}")
    
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
    print(f" ToolCallProcessor initialized")
    
    # List tools by platform
    print("\n[PLATFORM TOOLS AVAILABLE]")
    for platform in ["gmail", "slack", "stripe"]:
        tools = executor.list_tools_for_platform(platform)
        print(f"  {platform}: {len(tools)} tools")
        for tool in tools[:2]:
            print(f"    • {tool.get('name')}")
    
    print("\n" + "="*80 + "\n")


# ============================================================
# FLASK ROUTES INTEGRATION
# ============================================================

"""
Flask Routes - V4 with Tool Execution

Integrates ToolExecutor and ToolCallProcessor with Flask endpoints
"""

from flask import Blueprint, request, Response, current_app, g, jsonify, session
import threading
from queue import Empty
import json

# Import infrastructure
from core.agent_state_manager import agent_state_manager
from core.combined_agent_worker import run_agent_worker, run_simple_agent_worker
from utils.file_encoding import process_file_uploads, FileValidationError
from utils.response_helpers import (
    success_response, error_response, list_response, stream_sse_event
)

# Create blueprint
agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')

# In-memory storage for user feedback (temporary - should be Redis in production)
_feedback_storage = {}

# In-memory storage for feedback injection notifications
_feedback_injection_notifications = {}


# ============================================================
# AUTHENTICATION MIDDLEWARE (Fix #9)
# ============================================================

@agent_bp.before_request
def extract_user_from_token():
    """
    Extract user_id from JWT token in Authorization header
    Sets g.user_id for use in route handlers
    
    This middleware runs before EVERY request to agent_bp routes.
    It extracts the user_id from the JWT token and stores it in Flask's g object.
    Routes can then use g.user_id to get the authenticated user's ID.
    """
    # Get Authorization header
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        # No auth header - default to user_id=1 (for CLI/dev mode)
        g.user_id = 1
        return
    
    # Extract token
    token = auth_header.replace('Bearer ', '').strip()
    
    try:
        # Verify token using UserAuthManager
        from auth.user_auth import UserAuthManager
        auth_manager = UserAuthManager()
        user_data = auth_manager.verify_token(token)
        
        if user_data:
            g.user_id = user_data.get('user_id')
            g.user_email = user_data.get('email')
            print(f"🔑 [AUTH] Request authenticated: user_id={g.user_id}, email={g.user_email}")
        else:
            # Invalid token - default to user_id=1
            g.user_id = 1
            print(f"⚠️ [AUTH] Token verification failed - using default user_id=1")
    
    except Exception as e:
        # Error verifying token - default to user_id=1
        g.user_id = 1
        print(f"⚠️ [AUTH] Token verification error: {e} - using default user_id=1")


# ============================================================
# UNIVERSAL TRIPLE AGENT ENDPOINTS
# ============================================================

@agent_bp.route('/agent/<agent_id>/start', methods=['POST'])
def start_agent(agent_id):
    """Universal agent start endpoint"""
    try:
        is_form_data = request.content_type and 'multipart/form-data' in request.content_type
        
        if is_form_data:
            data = request.form  # Set data to form for consistent access
            session_id = request.form.get('session_id')
            prompt = request.form.get('message', '')
            thread_id = request.form.get('thread_id') or session_id  # Extract thread_id from form
            files = request.files.getlist('files')
            if not files:
                return error_response("No files uploaded", 400)
            try:
                content_blocks = process_file_uploads(files)
            except FileValidationError as e:
                return error_response(str(e), 400)
            file_data = content_blocks
        else:
            data = request.json or {}
            session_id = data.get('session_id')
            prompt = data.get('message', '')
            thread_id = data.get('thread_id') or session_id  # Extract thread_id from JSON
            file_data = None
        
        if not prompt:
            return error_response("Missing 'message' in request", 400)
        
        # Create session if not provided
        if not session_id:
            import secrets
            from datetime import datetime
            session_id = f"session_{int(datetime.now().timestamp()*1000)}_{secrets.token_urlsafe(8)}"
        
        # CRITICAL FIX: Read conversation_history from frontend request
        # Frontend sends full conversation history in data.conversation_history
        if is_form_data:
            # For form data, conversation_history might be a JSON string
            conv_history_str = request.form.get('conversation_history', '[]')
            try:
                conversation_history = json.loads(conv_history_str) if isinstance(conv_history_str, str) else []
            except:
                conversation_history = []
        else:
            conversation_history = data.get('conversation_history', [])
        print(f"[START] Received {len(conversation_history)} messages in conversation_history from frontend")
        
        # CRITICAL: Prune conversation IMMEDIATELY if it's too large
        # This prevents re-sending 231K+ tokens that already exceeded the limit
        if len(conversation_history) > 0:
            from core.combined_agent_worker import prune_conversation_for_context_limit
            original_count = len(conversation_history)
            conversation_history = prune_conversation_for_context_limit(
                conversation_history,
                max_estimated_tokens=180000,
                preserve_first_user=True
            )
            if len(conversation_history) < original_count:
                print(f"[START] Pruned conversation: {original_count} -> {len(conversation_history)} messages")
        
        # Get or create agent state (IMPORTANT: This ensures conversation is in agent_state_manager)
        state = agent_state_manager.get_or_create_state(agent_id, session_id, {
            'session_id': session_id,
            'conversation': [],
            'context': {}
        })
        
        # CRITICAL FIX: Always UPDATE state with conversation_history from frontend
        # THEN add the current user message (which isn't in conversation_history yet)
        if conversation_history:
            state['conversation'] = conversation_history
            print(f"[START] Updated state with conversation_history from frontend - {len(conversation_history)} messages")
        else:
            # Start fresh conversation if no history
            state['conversation'] = []
            print(f"[START] No conversation_history from frontend - starting fresh")
        
        # ALWAYS add the current user message (it's not in conversation_history yet)
        user_message = {'role': 'user', 'content': prompt}
        state['conversation'].append(user_message)
        print(f"[START] Added current user message to conversation - {len(state['conversation'])} messages total")
        
        lock = agent_state_manager.get_lock(agent_id, session_id)
        queue = agent_state_manager.get_queue(agent_id, session_id)
        agent_state_manager.update_status(agent_id, session_id, 'processing')
        
        # Acquire lock before starting worker (worker will release it when done)
        lock.acquire()
        
        ai_client = current_app.config.get('AI_CLIENT')
        if ai_client is None:
            from core.unified_ai_client import initialize_ai_client
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from config import Config
            ai_client = initialize_ai_client(str(Config.DB_CONFIG_PATH))
            current_app.config['AI_CLIENT'] = ai_client
        
        # Get user_id from middleware (g.user_id) for OAuth credential injection
        user_id = g.get('user_id', 1)
        print(f"[START] User ID for credential injection: {user_id}")
        
        if file_data:
            print(f"[START] Starting file agent worker for agent {agent_id}, session {session_id[:8]}, thread {thread_id}")
            threading.Thread(
                target=run_agent_worker,
                args=(agent_id, prompt, file_data, lock, session_id, queue, state['conversation'], state['context'], user_id, thread_id),
                daemon=True
            ).start()
        else:
            print(f"[START] Starting simple agent worker for agent {agent_id}, session {session_id[:8]}, thread {thread_id}")
            print(f"[START] Worker args: agent_id={agent_id}, prompt='{prompt[:50]}...', ai_client={ai_client is not None}, user_id={user_id}, thread_id={thread_id}")
            threading.Thread(
                target=run_simple_agent_worker,
                args=(agent_id, prompt, lock, session_id, queue, state['conversation'], ai_client, user_id, thread_id),
                daemon=True
            ).start()
            print(f"[START] Thread started successfully")
        
        return success_response({
            'session_id': session_id,
            'agent_id': agent_id,
            'status': 'processing',
            'files_uploaded': len(file_data) if file_data else 0
        })
    
    except Exception as e:
        return error_response(f"Agent start failed: {str(e)}", 500)


@agent_bp.route('/stream/<agent_id>', methods=['GET'])
def stream_agent(agent_id):
    """
    Universal SSE stream endpoint - MULTI-ROUND STREAMING
    
    ✅ NEW: Uses StreamingAgentWorker for proper multi-round tool use
    Pattern copied from In_House_SQL ToolUseAgent
    
    Query params:
        ?session_id=uuid (required)
    
    agent_id: '1' | '2' | '3' | 'stock_ai' | 'data_agent' | 'single_viewer'
    
    Features:
    - Real-time thinking blocks
    - Character-by-character text streaming
    - Tool execution with results
    - Recursive continuation (unlimited rounds)
    - Proper conversation history
    """
    session_id = request.args.get('session_id')
    
    if not session_id:
        return error_response("Missing session_id", 400)
    
    # Get agent state and conversation history
    state = agent_state_manager.get_or_create_state(agent_id, session_id, {})
    conversation = state.get('conversation', [])
    
    # Debug logging
    print(f"[Stream {agent_id}] Session: {session_id}")
    print(f"[Stream {agent_id}] Conversation length: {len(conversation)}")
    if conversation:
        print(f"[Stream {agent_id}] Last message: {conversation[-1].get('role')} - {str(conversation[-1].get('content', ''))[:100]}")
    
    # CRITICAL FIX: Extract last user message and REMOVE it from conversation history
    # The streaming worker expects:
    #   - conversation_history: PAST messages (NOT including current)
    #   - user_prompt: CURRENT message to process
    # Previously we were passing the current message in BOTH places, causing it to be ignored
    last_message = ''
    conversation_without_current = conversation.copy()
    
    if conversation:
        for idx in range(len(conversation) - 1, -1, -1):
            msg = conversation[idx]
            if msg.get('role') == 'user':
                # Extract text content
                content = msg.get('content', '')
                if isinstance(content, str):
                    last_message = content
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get('type') == 'text':
                            last_message = block.get('text', '')
                            break
                
                # CRITICAL: Remove this message from history (it will be passed as user_prompt)
                conversation_without_current = conversation[:idx]
                print(f"[Stream {agent_id}] 🔧 FIX: Extracted current message, conversation history reduced from {len(conversation)} to {len(conversation_without_current)} messages")
                break
    
    if not last_message:
        error_msg = f"No user message found in conversation. Session: {session_id}, Conv length: {len(conversation)}"
        if conversation:
            error_msg += f", Last role: {conversation[-1].get('role')}"
        print(f"[Stream {agent_id}] ❌ ERROR: {error_msg}")
        return error_response(error_msg, 400)
    
    # Get user_id for credential injection
    user_id = g.get('user_id', 1)
    print(f"[Stream {agent_id}] 👤 User ID for credential injection: {user_id}")
    
    # Load tools from registry
    from tools.registry_v3 import get_registry
    registry = get_registry()
    
    # ✅ DYNAMIC TOOL LOADING: ALWAYS send only meta-tools
    # AI discovers platforms/tools via meta-tool responses (lists of names)
    # When AI calls an actual action tool, we execute it via registry
    # This keeps token count minimal - we NEVER send all 603 tool schemas
    
    meta_tool_names = [
        'list_available_platforms',
        'list_platform_tools',
        'get_tool_schema',      # ✅ Get parameter schema for ONE specific tool
        'search_tools',          # ✅ Search for tools by keyword
        'get_platform_guide',
        'recommend_tools_for_task',
        'get_workflow_steps',
        'execute_tool'           # ✅ Execute ANY tool by name after learning its schema
    ]
    
    all_tools_dict = {t['name']: t for t in registry.get_anthropic_tools()}
    tools = [all_tools_dict[name] for name in meta_tool_names if name in all_tools_dict]
    
    # Get user preferences (nickname, auth platform, communication style)
    from routes.user_preferences_routes import get_user_preferences
    user_prefs = get_user_preferences(user_id) if user_id else None
    
    # Debug: Print raw preferences to see what we're getting
    print(f"[Stream {agent_id}] 🔍 RAW USER PREFS: {user_prefs}")
    
    nickname = user_prefs.get('nickname', '') if user_prefs else ''
    auth_platform = user_prefs.get('auth_platform', 'auto') if user_prefs else 'auto'
    communication_style = user_prefs.get('communication_style', 'professional') if user_prefs else 'professional'
    detail_level = user_prefs.get('detail_level', 'standard') if user_prefs else 'standard'
    
    # Get preferred_tools (this might be stored as JSON string or list)
    preferred_tools_raw = user_prefs.get('preferred_tools', '') if user_prefs else ''
    preferred_tools = []
    if preferred_tools_raw:
        try:
            if isinstance(preferred_tools_raw, str):
                preferred_tools = json.loads(preferred_tools_raw) if preferred_tools_raw else []
            elif isinstance(preferred_tools_raw, list):
                preferred_tools = preferred_tools_raw
        except:
            preferred_tools = []
    
    if nickname:
        print(f"[Stream {agent_id}] 👤 User nickname: {nickname}")
    print(f"[Stream {agent_id}] 🔐 Auth platform: {auth_platform}")
    print(f"[Stream {agent_id}] 💬 Communication style: {communication_style}")
    print(f"[Stream {agent_id}] 📊 Detail level: {detail_level}")
    print(f"[Stream {agent_id}] 📋 Preferred tools: {preferred_tools}")
    
    # Get user location from IP for web_search localization
    from core.ip_location import get_location_dict
    try:
        user_ip = request.remote_addr
        # Only call once - get_location_dict contains location_string
        location_dict = get_location_dict(user_ip)
        location_string = location_dict.get('location_string', 'Brisbane, Queensland, Australia')
        
        # Create comprehensive location + time string for system prompt
        current_time_str = location_dict.get('current_time', 'Unknown time')
        day_of_week = location_dict.get('day_of_week', 'Unknown')
        season = location_dict.get('season', 'Unknown season')
        
        # Extract temperature and weather data
        temp_c = location_dict.get('temperature_c')
        temp_f = location_dict.get('temperature_f')
        weather_condition = location_dict.get('weather_condition', 'Unknown')
        
        # Extract month name from date
        from datetime import datetime
        date_str = location_dict.get('date', '2025-11-06')
        try:
            month_name = datetime.strptime(date_str, '%Y-%m-%d').strftime('%B')
        except:
            month_name = 'November'
        
        # Build comprehensive time context with temperature
        # Format: Location | Day, Date Time Timezone | Month (Season) | Temperature, Weather
        if temp_c is not None:
            temp_str = f"{temp_c}°C ({temp_f}°F), {weather_condition}"
            time_context = f"{location_string} | {day_of_week}, {current_time_str} | {month_name} ({season}) | {temp_str}"
        else:
            time_context = f"{location_string} | {day_of_week}, {current_time_str} | {month_name} ({season})"
        
        print(f"[Stream {agent_id}] 📍 User location: {location_string}")
        print(f"[Stream {agent_id}] 🕐 User local time: {day_of_week}, {current_time_str}")
        print(f"[Stream {agent_id}] 🌍 Season/Month: {month_name} ({season})")
        if temp_c is not None:
            print(f"[Stream {agent_id}] 🌡️  Temperature: {temp_c}°C ({temp_f}°F), {weather_condition}")
    except Exception as e:
        # Fallback to Brisbane if detection fails
        from datetime import datetime
        import pytz
        
        location_string = "Brisbane, Queensland, Australia"
        location_dict = {
            'city': 'Brisbane',
            'region': 'Queensland',
            'country': 'AU',
            'timezone': 'Australia/Brisbane'
        }
        
        # Generate fallback time with month and season
        tz = pytz.timezone('Australia/Brisbane')
        now = datetime.now(tz)
        current_time_str = now.strftime('%Y-%m-%d %I:%M %p %Z')
        day_of_week = now.strftime('%A')
        month_name = now.strftime('%B')
        
        # Determine season (Southern Hemisphere for Brisbane)
        month = now.month
        if month in [12, 1, 2]:
            season = 'Summer'  # Southern Hemisphere
        elif month in [3, 4, 5]:
            season = 'Autumn'
        elif month in [6, 7, 8]:
            season = 'Winter'
        else:
            season = 'Spring'
        
        time_context = f"{location_string} | {day_of_week}, {current_time_str} | {month_name} ({season})"
        
        print(f"[Stream {agent_id}] ⚠️  Location detection failed: {e}, using default: {location_string}")
    
    # ✅ ADD SERVER TOOLS: web_search (with user's actual location)
    # These are executed by Anthropic, not by our registry
    # NOTE: web_fetch removed - not a valid Anthropic server tool type
    server_tools = [
        {
            "type": "web_search_20250305",
            "name": "web_search",
            "user_location": {
                "type": "approximate",
                "city": location_dict['city'],
                "region": location_dict['region'],
                "country": location_dict['country'],
                "timezone": location_dict['timezone']
            },
            "max_uses": 5
        }
    ]
    
    # Combine meta-tools with server tools
    tools = tools + server_tools
    
    print(f"[Stream {agent_id}] 🔷 [Dynamic Loading] Sending {len(tools)} tools ({len(tools) - len(server_tools)} meta-tools + {len(server_tools)} server tools)")
    print(f"[Stream {agent_id}] 🔷 Workflow: discover platforms → list tools (names only) → get schema (ONE tool) → execute")
    print(f"[Stream {agent_id}] 🔷 Server tools: {[t['name'] for t in server_tools]}")
    
    # Get system prompt
    from core.unified_ai_client import UnifiedAIClient
    ai_client = current_app.config.get('AI_CLIENT')
    if ai_client:
        system_prompt = ai_client.get_system_prompt('data_agent_chat')
        
        # Map auth_platform to suite name and build platform-specific instructions
        if auth_platform == 'microsoft':
            mandatory_platform = "Microsoft 365 Suite"
            platform_instructions = """
MANDATORY PLATFORM USE: Microsoft 365 Suite

User is authenticated with Microsoft 365. For any functionality that 
overlaps between Google Workspace and Microsoft 365 (email, documents, 
spreadsheets, calendar, file storage), you MUST use Microsoft 365 tools.

Use Microsoft tools for:
- Email → microsoft_outlook_* (NOT gmail_*)
- Documents → microsoft_word_* (NOT google_docs_*)
- Spreadsheets → microsoft_excel_* (NOT google_sheets_*)
- Storage → microsoft_onedrive_* (NOT google_drive_*)
- Calendar → microsoft_calendar_* (NOT google_calendar_*)
- Notes → microsoft_onenote_* (NOT google_keep_*)
- Forms → microsoft_forms_* (NOT google_forms_*)
- Presentations → microsoft_powerpoint_* (NOT google_slides_*)
- Team Chat → microsoft_teams_* (NOT google_chat_*)
- Tasks → microsoft_todo_* (NOT google_tasks_*)"""
        elif auth_platform == 'google':
            mandatory_platform = "Google Workspace"
            platform_instructions = """
MANDATORY PLATFORM USE: Google Workspace

User is authenticated with Google Workspace. For any functionality that 
overlaps between Google Workspace and Microsoft 365 (email, documents, 
spreadsheets, calendar, file storage), you MUST use Google Workspace tools.

Use Google tools for:
- Email → gmail_* (NOT microsoft_outlook_*)
- Documents → google_docs_* (NOT microsoft_word_*)
- Spreadsheets → google_sheets_* (NOT microsoft_excel_*)
- Storage → google_drive_* (NOT microsoft_onedrive_*)
- Calendar → google_calendar_* (NOT microsoft_calendar_*)
- Forms → google_forms_* (NOT microsoft_forms_*)
- Presentations → google_slides_* (NOT microsoft_powerpoint_*)
- Tasks → google_tasks_* (NOT microsoft_todo_*)
- Meet → google_meet_* (NOT microsoft_teams_*)"""
        else:
            mandatory_platform = "Auto (Check Connected Platforms)"
            platform_instructions = """
PLATFORM USE: Auto-detect

User has not specified a mandatory platform. Check connected platforms and use 
available tools. Prefer the platform the user is authenticated with."""
        
        # Get AI memories for this user (if any)
        ai_memories = []
        if user_prefs and user_prefs.get('ai_memories'):
            try:
                import json
                memories_json = user_prefs.get('ai_memories', '[]')
                ai_memories = json.loads(memories_json) if memories_json else []
            except:
                ai_memories = []
        
        # Build structured user context
        user_context_block = f"""═══════════════════════════════════════════════════════════════
USER CONTEXT

User: {nickname if nickname else 'User'}
Location: {location_string}
Current Time: {day_of_week}, {current_time_str}
Season: {month_name} ({season})"""
        
        # Add weather if available
        if temp_c is not None:
            user_context_block += f"\nWeather: {temp_c}°C ({temp_f}°F), {weather_condition}"
        
        user_context_block += f"""
{platform_instructions}

Additional Preferences (YOU MUST FOLLOW THESE):
- Communication Style: {communication_style}
- Detail Level: {detail_level}"""
        
        # Add preferred_tools as special instructions
        if preferred_tools:
            user_context_block += "\n\nSpecial Instructions (CRITICAL - MUST FOLLOW):"
            for tool_pref in preferred_tools:
                user_context_block += f"\n- {tool_pref}"
        
        # Add AI memories section
        if ai_memories:
            user_context_block += "\n\nKey Memories About This User:"
            for memory in ai_memories[:5]:  # Show max 5 most recent memories
                user_context_block += f"\n- {memory}"
        
        user_context_block += "\n═══════════════════════════════════════════════════════════════\n"
        
        # Debug: Print the formatted user context
        print(f"[Stream {agent_id}] 📋 USER CONTEXT BLOCK:")
        print(user_context_block)
        
        # Inject user context into prompt
        system_prompt = system_prompt.replace('{{USER_LOCATION}}', user_context_block)
        
        # ============================================
        # PROMPT INJECTION SYSTEM (NEW)
        # ============================================
        # Allow users to inject custom prompts from library or quick actions
        # Request parameters: quick_actions, library_prompts, custom_prompt
        try:
            from core.prompt_injection_manager import get_prompt_manager
            
            # Get injection parameters from request
            quick_actions = request.json.get('quick_actions', []) if request.json else []
            library_prompts = request.json.get('library_prompts', []) if request.json else []
            custom_prompt = request.json.get('custom_prompt', None) if request.json else None
            user_custom_prompts = request.json.get('user_custom_prompts', []) if request.json else []
            
            # Apply prompt injections if any provided
            if quick_actions or library_prompts or custom_prompt or user_custom_prompts:
                prompt_manager = get_prompt_manager()
                system_prompt = prompt_manager.inject_prompts(
                    base_prompt=system_prompt,
                    quick_actions=quick_actions,
                    library_prompts=library_prompts,
                    custom_prompt=custom_prompt,
                    user_id=user_id,
                    user_custom_prompts=user_custom_prompts
                )
                
                print(f"[Stream {agent_id}] ⚡ Prompt injections applied:")
                if quick_actions:
                    print(f"  - Quick Actions: {quick_actions}")
                if library_prompts:
                    print(f"  - Library Prompts: {library_prompts}")
                if custom_prompt:
                    print(f"  - Custom Prompt: {custom_prompt[:50]}...")
                if user_custom_prompts:
                    print(f"  - User Custom Prompts: {user_custom_prompts}")
        except Exception as e:
            print(f"[Stream {agent_id}] ⚠️  Error applying prompt injections: {e}")
            # Continue without injections - not critical
    else:
        system_prompt = """You are an AI assistant with access to 604 tools across 20+ platforms via a 3-STEP discovery system.

CRITICAL: NO BULK TOOL SCHEMAS!
- list_platform_tools() returns NAMES ONLY (no parameter schemas)
- get_tool_schema() returns parameters for ONE specific tool
- This prevents sending 200+ tool schemas when you only need 1-2 tools"""
    
    # ============================================
    # SYNERGY CONTEXT INJECTION
    # ============================================
    # Check if this thread is linked to a Synergy project
    # If yes, inject project context into system prompt
    try:
        # Get thread info FROM sessions.db
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # Find thread by session_id (thread_slug = session_id in most cases)
        # Note: id is INTEGER, thread_slug is TEXT (timestamp)
        cursor.execute("""
            SELECT synergy_card_id
            FROM sessions.threads 
            WHERE thread_slug = $1
            LIMIT 1
        """, (str(session_id),))
        
        thread_row = cursor.fetchone()
        conn.close()
        
        if thread_row and thread_row['synergy_card_id']:
            synergy_card_id = thread_row['synergy_card_id']
            
            # Fetch Synergy project details
            conn = get_database_connection('synergy_sessions')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    title, description, project_name, priority, status,
                    tags, documents, next_steps, notes, due_date
                FROM synergy_sessions.synergy_sessions 
                WHERE session_id = ?
            """, (synergy_card_id,))
            
            synergy_row = cursor.fetchone()
            conn.close()
            
            if synergy_row:
                # LOG: Synergy session details
                print(f"[Stream {agent_id}] 🎯 SYNERGY LINKED → Session: {synergy_card_id} | Title: '{synergy_row['title']}' | Priority: {synergy_row['priority']} | Status: {synergy_row['status']}")
                
                # Build Synergy context string
                synergy_context = f"\n\n{'='*80}\n"
                synergy_context += "SYNERGY PROJECT CONTEXT\n"
                synergy_context += f"{'='*80}\n\n"
                synergy_context += f"You are working on a Synergy project:\n\n"
                synergy_context += f"**Project:** {synergy_row['title']}\n"
                if synergy_row['project_name']:
                    synergy_context += f"**Category:** {synergy_row['project_name']}\n"
                if synergy_row['description']:
                    synergy_context += f"**Description:** {synergy_row['description']}\n"
                synergy_context += f"**Priority:** {synergy_row['priority']}\n"
                synergy_context += f"**Status:** {synergy_row['status']}\n"
                
                # Add notes if present
                if synergy_row['notes']:
                    synergy_context += f"\n**Project Notes:**\n{synergy_row['notes']}\n"
                
                # Add next steps if present
                if synergy_row['next_steps']:
                    try:
                        next_steps = json.loads(synergy_row['next_steps']) if isinstance(synergy_row['next_steps'], str) else synergy_row['next_steps']
                        if next_steps and isinstance(next_steps, list) and len(next_steps) > 0:
                            synergy_context += "\n**Next Steps:**\n"
                            for step in next_steps:
                                if isinstance(step, dict):
                                    status_icon = "✅" if step.get('completed') else "⏳"
                                    synergy_context += f"- {status_icon} {step.get('description', 'N/A')}\n"
                    except:
                        pass
                
                # Add documents if present
                if synergy_row['documents']:
                    try:
                        documents = json.loads(synergy_row['documents']) if isinstance(synergy_row['documents'], str) else synergy_row['documents']
                        if documents and isinstance(documents, list) and len(documents) > 0:
                            synergy_context += "\n**Project Documents:**\n"
                            for doc in documents:
                                if isinstance(doc, dict):
                                    synergy_context += f"- {doc.get('title', 'Untitled')} ({doc.get('type', 'file')})\n"
                    except:
                        pass
                
                # Add due date if present
                if synergy_row['due_date']:
                    synergy_context += f"\n**Due Date:** {synergy_row['due_date']}\n"
                
                synergy_context += f"\n{'='*80}\n"
                synergy_context += "Use this context to provide relevant assistance for this specific project.\n"
                synergy_context += f"{'='*80}\n"
                
                # Append to system prompt
                system_prompt += synergy_context
                print(f"[Stream {agent_id}] ✅ Synergy context injected into system prompt")
            else:
                print(f"[Stream {agent_id}] ⚠️  Synergy session {synergy_card_id} not found in synergy_sessions.db")
        else:
            print(f"[Stream {agent_id}] ℹ️  NO SYNERGY LINK - Thread not linked to any Synergy session")
    
    except Exception as e:
        print(f"[Stream {agent_id}] ⚠️  Error checking Synergy context: {e}")
        # Continue without Synergy context - not critical
    
    # Continue with original code
    system_prompt_continued = """

SERVER TOOLS (Always Available - No Discovery Needed):
- web_search: Real-time web search for current information (news, pricing, standards, market data)
  Usage: Claude will automatically use this when you need current information
  Location: Brisbane, Queensland, Australia

3-STEP WORKFLOW (For Client Tools):

STEP 1: DISCOVER
- list_available_platforms() → See what platforms exist
- search_tools("email") → Find tools by keyword (fast!)
- list_platform_tools("google_workspace") → See ALL tool names for platform

STEP 2: LEARN (ONE tool at a time)
- get_tool_schema("gmail_send_email") → Get parameters for THIS tool only
  Returns: {parameters: {to: {type, required}, subject: {type, required}, ...}}

STEP 3: EXECUTE
- execute_tool("gmail_send_email", to="john@...", subject="...", body="...")
  → Executes the tool via registry

EXAMPLE (Send email):
   A) search_tools("gmail") OR list_platform_tools("google_workspace")
      → Returns: [{name: "gmail_send_email", description: "Send email"}] (NO params!)
   
   B) get_tool_schema("gmail_send_email")
      → Returns: {parameters: {to: string required, subject: string required, body: string required}}
   
   C) execute_tool("gmail_send_email", to="john@example.com", subject="Hello", body="Test")
      → Returns: {success: true, result: "Email sent"}

CRITICAL RULES:
- NEVER expect list_platform_tools to return parameter schemas (it won't!)
- ALWAYS call get_tool_schema(tool_name) before execute_tool()
- Use search_tools() when you know what you're looking for (faster than listing)
- Think: "What do I need? → Search/list → Learn ONE tool → Execute"

Platforms available: google_workspace, microsoft_365, woocommerce, stripe, slack, github, supabase, and 15+ more.

Use tools in multiple rounds with interleaved thinking to complete complex tasks."""
    
    # ============================================
    # SYNERGY CONTEXT INJECTION (Into conversation)
    # ============================================
    # Check if this thread is linked to a Synergy project
    # If yes, prepend project context to the user's current message
    synergy_context_prefix = ""
    try:
        # Get thread info FROM sessions.db
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # Find thread by session_id (thread_slug = session_id)
        # Note: id is INTEGER, thread_slug is TEXT (timestamp)
        cursor.execute("""
            SELECT synergy_card_id
            FROM sessions.threads 
            WHERE thread_slug = $1
            LIMIT 1
        """, (str(session_id),))
        
        thread_row = cursor.fetchone()
        conn.close()
        
        if thread_row and thread_row['synergy_card_id']:
            synergy_card_id = thread_row['synergy_card_id']
            
            # Fetch Synergy project details
            conn = get_database_connection('synergy_sessions')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    title, description, project_name, priority, status,
                    tags, documents, next_steps, notes, due_date
                FROM synergy_sessions.synergy_sessions 
                WHERE session_id = ?
            """, (synergy_card_id,))
            
            synergy_row = cursor.fetchone()
            conn.close()
            
            if synergy_row:
                # LOG: Synergy session details
                print(f"[Stream {agent_id}] 🎯 SYNERGY LINKED → Session: {synergy_card_id} | Title: '{synergy_row['title']}' | Priority: {synergy_row['priority']} | Status: {synergy_row['status']}")
                
                # Build Synergy context prefix for user message
                synergy_context_prefix = f"[SYNERGY PROJECT CONTEXT]\n"
                synergy_context_prefix += f"Project: {synergy_row['title']}\n"
                if synergy_row['description']:
                    synergy_context_prefix += f"Description: {synergy_row['description']}\n"
                synergy_context_prefix += f"Status: {synergy_row['status']} | Priority: {synergy_row['priority']}\n"
                
                # Add notes if present
                if synergy_row['notes']:
                    synergy_context_prefix += f"Notes: {synergy_row['notes']}\n"
                
                # Add next steps if present
                if synergy_row['next_steps']:
                    try:
                        next_steps = json.loads(synergy_row['next_steps']) if isinstance(synergy_row['next_steps'], str) else synergy_row['next_steps']
                        if next_steps and isinstance(next_steps, list) and len(next_steps) > 0:
                            pending_steps = [s for s in next_steps if isinstance(s, dict) and not s.get('completed')]
                            if pending_steps:
                                synergy_context_prefix += f"Pending Steps: {', '.join([s.get('description', '') for s in pending_steps[:3]])}\n"
                    except:
                        pass
                
                synergy_context_prefix += f"[/SYNERGY CONTEXT]\n\n"
                
                print(f"[Stream {agent_id}] ✅ Synergy context prepended to user message")
            else:
                print(f"[Stream {agent_id}] ⚠️  Synergy session {synergy_card_id} not found in synergy_sessions.db")
        else:
            print(f"[Stream {agent_id}] ℹ️  NO SYNERGY LINK - Thread not linked to any Synergy session")
    
    except Exception as e:
        print(f"[Stream {agent_id}] ⚠️ Error fetching Synergy context: {e}")
        # Continue without Synergy context - not critical
    
    # Prepend Synergy context to user message if present
    user_message_with_context = synergy_context_prefix + last_message if synergy_context_prefix else last_message
    
    # Extract AI preferences from user_prefs (CRITICAL for Extended + Interleaved Thinking)
    ai_model = user_prefs.get('ai_model', 'claude-sonnet-4-5-20250929') if user_prefs else 'claude-sonnet-4-5-20250929'
    ai_temperature = float(user_prefs.get('ai_temperature', 1.0)) if user_prefs else 1.0
    ai_max_tokens = int(user_prefs.get('ai_max_tokens', 16000)) if user_prefs else 16000
    ai_thinking_enabled = bool(user_prefs.get('ai_thinking_enabled', 1)) if user_prefs else True  # Default TRUE
    ai_thinking_budget = int(user_prefs.get('ai_thinking_budget', 10000)) if user_prefs else 10000
    
    print(f"[Stream {agent_id}] 🧠 AI Preferences:")
    print(f"  Model: {ai_model}")
    print(f"  Temperature: {ai_temperature}")
    print(f"  Max Tokens: {ai_max_tokens}")
    print(f"  Extended Thinking: {'Enabled' if ai_thinking_enabled else 'Disabled'}")
    print(f"  Thinking Budget: {ai_thinking_budget} tokens")
    if ai_thinking_enabled:
        print(f"  🎯 Interleaved Thinking: ENABLED (beta: interleaved-thinking-2025-05-14)")
    
    # Import streaming worker
    from core.combined_agent_worker import execute_streaming_request
    
    def generate():
        import json  # CRITICAL: Import json inside nested function to avoid scope issues
        try:
            # Yield start event
            yield stream_sse_event('start', {'session_id': session_id, 'agent_id': agent_id})
            
            # Execute streaming request with multi-round support + AI PREFERENCES
            # CRITICAL: Use conversation_without_current (past messages only)
            # user_prompt contains the current message to process (with Synergy context if applicable)
            for event in execute_streaming_request(
                session_id=session_id,
                user_prompt=user_message_with_context,
                conversation_history=conversation_without_current,
                system_prompt=system_prompt,
                tools=tools,
                user_id=user_id,
                ai_model=ai_model,
                ai_temperature=ai_temperature,
                ai_max_tokens=ai_max_tokens,
                ai_thinking_enabled=ai_thinking_enabled,
                ai_thinking_budget=ai_thinking_budget
            ):
                # Yield SSE event
                event_type = event.get('type', 'unknown')
                yield stream_sse_event(event_type, event)
                
                # AUTO-SAVE: On completion, automatically save thread to database
                if event_type == 'complete':
                    try:
                        # Get final conversation state from agent_state_manager
                        final_state = agent_state_manager.get_state(agent_id, session_id)
                        
                        if final_state and final_state.get('conversation'):
                            # Auto-save thread to database (FIXED: Use sessions.db, not stock db)
                            from utils.database_helpers import execute_sqlite_update, get_sessions_database_path
                            
                            db_path = get_sessions_database_path()
                            thread_id = f"{agent_id}_{session_id}"
                            conversation_json = json.dumps(final_state['conversation'])
                            
                            # Determine location from thread assignments
                            location = 'prime'  # Default
                            try:
                                from routes.thread_assignment_routes import get_db_connection as get_sessions_db
                                conn = get_sessions_db()
                                cursor = conn.cursor()
                                cursor.execute("SELECT metadata FROM ai_infrastructure.users WHERE id = ?", [user_id])
                                row = cursor.fetchone()
                                if row and row['metadata']:
                                    metadata = json.loads(row['metadata'])
                                    assignments = metadata.get('thread_assignments', {})
                                    for loc, tid in assignments.items():
                                        if tid == session_id:
                                            location = loc
                                            break
                                conn.close()
                            except Exception as e:
                                print(f"⚠️ [Auto-Save] Could not determine thread location: {e}")
                            
                            # Update thread's updated_at timestamp (thread already exists from creation)
                            # Don't try to save to non-existent saved_threads table
                            update_query = """
                                UPDATE sessions.threads 
                                SET updated_at = datetime('now')
                                WHERE thread_slug = ?
                            """
                            
                            params = [session_id]
                            
                            execute_sqlite_update(db_path, update_query, params)
                            print(f"✅ [Auto-Save] Thread updated: {thread_id} ({len(final_state['conversation'])} messages)")
                    
                    except Exception as save_error:
                        print(f"⚠️ [Auto-Save] Failed to save thread: {save_error}")
                        import traceback
                        traceback.print_exc()
                
                # Break on complete or error
                if event_type in ['complete', 'error']:
                    break
        
        except Exception as e:
            import traceback
            print(f"[Stream {agent_id}] ERROR: {traceback.format_exc()}")
            yield stream_sse_event('error', {'error': str(e)})
    
    # IMPORTANT: Don't set 'Connection' header - it's a hop-by-hop header forbidden in WSGI (PEP 3333)
    # Waitress/gunicorn will manage connection headers automatically
    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no'
    })


@agent_bp.route('/agent/<agent_id>/status', methods=['GET'])
def get_agent_status(agent_id):
    """Get agent status"""
    session_id = request.args.get('session_id')
    if not session_id:
        return error_response("Missing session_id", 400)
    
    try:
        state = agent_state_manager.get_or_create_state(agent_id, session_id, {})
        return success_response({
            'status': state['status'],
            'message_count': len(state['conversation'])
        })
    except Exception as e:
        return error_response(str(e), 500)


@agent_bp.route('/agent/<agent_id>/history', methods=['GET'])
def get_agent_history(agent_id):
    """Get conversation history"""
    session_id = request.args.get('session_id')
    if not session_id:
        return error_response("Missing session_id", 400)
    
    try:
        state = agent_state_manager.get_or_create_state(agent_id, session_id, {})
        return list_response(state['conversation'])
    except Exception as e:
        return error_response(str(e), 500)


@agent_bp.route('/agent/<agent_id>/clear', methods=['POST'])
def clear_agent_conversation(agent_id):
    """Clear conversation history"""
    try:
        data = request.json
        session_id = data.get('session_id')
        if not session_id:
            return error_response("Missing session_id", 400)
        agent_state_manager.clear_conversation(agent_id, session_id)
        return success_response(message="Conversation cleared")
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================
# LEGACY ENDPOINTS (Backward compatibility)
# ============================================================

@agent_bp.route('/data-agent/chat', methods=['POST'])
def data_agent_chat():
    """Legacy Data Agent endpoint"""
    try:
        data = request.json or {}
        session_id = data.get('session_id')
        prompt = data.get('prompt') or data.get('message', '')
        
        if not prompt:
            return error_response("Missing 'prompt' in request", 400)
        
        # Create session if not provided  
        if not session_id:
            import secrets
            from datetime import datetime
            session_id = f"session_{int(datetime.now().timestamp()*1000)}_{secrets.token_urlsafe(8)}"
        
        # Simple session state
        state = {
            'session_id': session_id,
            'conversation': []
        }
        
        lock = agent_state_manager.get_lock('data_agent', session_id)
        queue = agent_state_manager.get_queue('data_agent', session_id)
        agent_state_manager.update_status('data_agent', session_id, 'processing')
        
        ai_client = current_app.config.get('AI_CLIENT')
        if ai_client is None:
            from core.unified_ai_client import initialize_ai_client
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from config import Config
            ai_client = initialize_ai_client(str(Config.DB_CONFIG_PATH))
            current_app.config['AI_CLIENT'] = ai_client
        
        # Get user_id from middleware for OAuth credential injection
        user_id = g.get('user_id', 1)
        
        threading.Thread(
            target=run_simple_agent_worker,
            args=('data_agent', prompt, lock, session_id, queue, state['conversation'], ai_client, user_id),
            daemon=True
        ).start()
        
        return success_response({
            'status': 'processing',
            'session_id': session_id
        })
    except Exception as e:
        return error_response(str(e), 500)


@agent_bp.route('/single-viewer/chat', methods=['POST'])
def single_viewer_chat():
    """Legacy Single Viewer endpoint"""
    try:
        data = request.json or {}
        session_id = data.get('session_id')
        prompt = data.get('prompt') or data.get('message', '')
        
        if not prompt:
            return error_response("Missing 'prompt' or 'message' in request", 400)
        
        # Create session if not provided
        if not session_id:
            import secrets
            from datetime import datetime
            session_id = f"session_{int(datetime.now().timestamp()*1000)}_{secrets.token_urlsafe(8)}"
        
        # Simple session state
        state = {
            'session_id': session_id,
            'conversation': []
        }
        
        lock = agent_state_manager.get_lock('single_viewer', session_id)
        queue = agent_state_manager.get_queue('single_viewer', session_id)
        agent_state_manager.update_status('single_viewer', session_id, 'processing')
        
        ai_client = current_app.config.get('AI_CLIENT')
        if ai_client is None:
            from core.unified_ai_client import initialize_ai_client
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from config import Config
            ai_client = initialize_ai_client(str(Config.DB_CONFIG_PATH))
            current_app.config['AI_CLIENT'] = ai_client
        
        # Get user_id from middleware for OAuth credential injection
        user_id = g.get('user_id', 1)
        
        threading.Thread(
            target=run_simple_agent_worker,
            args=('single_viewer', prompt, lock, session_id, queue, state['conversation'], ai_client, user_id),
            daemon=True
        ).start()
        
        return success_response({
            'status': 'processing',
            'session_id': session_id
        })
    except Exception as e:
        return error_response(str(e), 500)


@agent_bp.route('/api/agent/chat-with-document', methods=['POST'])
@agent_bp.route('/chat-with-document', methods=['POST'])
def agent_chat_with_document():
    """
    Chat with document endpoint - Synchronous response
    Accepts multipart/form-data with files and message
    Returns AI response after processing
    """
    try:
        # Get form data
        agent_id = request.form.get('agent_id', 'data_agent')
        message = request.form.get('message', '')
        route = request.form.get('route', 'agent')  # 'agent' = tools + thinking
        
        files = request.files.getlist('files')
        if not files:
            return error_response("No files uploaded", 400)
        
        # Validate and process files
        try:
            content_blocks = process_file_uploads(files)
        except FileValidationError as e:
            return error_response(str(e), 400)
        
        print(f"[CHAT-WITH-DOCUMENT] Processing {len(files)} files for agent {agent_id}")
        print(f"[CHAT-WITH-DOCUMENT] Message: {message[:100]}..." if message else "[CHAT-WITH-DOCUMENT] No message provided")
        
        # Get user_id from middleware (g.user_id) for OAuth credential injection
        user_id = g.get('user_id', 1)
        
        # Create temporary session for synchronous processing
        import secrets
        from datetime import datetime
        session_id = f"doc_session_{int(datetime.now().timestamp()*1000)}_{secrets.token_urlsafe(8)}"
        
        # Initialize AI client
        ai_client = current_app.config.get('AI_CLIENT')
        if ai_client is None:
            from core.unified_ai_client import initialize_ai_client
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from config import Config
            ai_client = initialize_ai_client(str(Config.DB_CONFIG_PATH))
            current_app.config['AI_CLIENT'] = ai_client
        
        # Build content blocks array (files + text)
        full_content = []
        
        # Add files first
        for block in content_blocks:
            full_content.append(block)
        
        # Add text message last
        if message:
            full_content.append({'type': 'text', 'text': message})
        else:
            full_content.append({'type': 'text', 'text': 'Analyze these documents and provide key information.'})
        
        # Build messages array
        messages = [{
            'role': 'user',
            'content': full_content
        }]
        
        # Get system prompt based on agent
        if agent_id == 'data_agent':
            system_prompt = """You are a data analysis assistant. You help users understand documents, images, and PDFs by extracting key information, answering questions, and providing insights."""
        else:
            system_prompt = """You are a helpful AI assistant with access to tools and extended thinking. You can analyze documents, answer questions, and perform actions using available tools."""
        
        print(f"[CHAT-WITH-DOCUMENT] Calling Claude API with {len(content_blocks)} files...")
        
        # Call Claude API synchronously
        try:
            response = ai_client.client.messages.create(
                model=ai_client.default_model,
                max_tokens=4096,
                system=system_prompt,
                messages=messages
            )
            
            # Extract text response
            ai_response = ""
            for block in response.content:
                if block.type == 'text':
                    ai_response += block.text
            
            print(f"[CHAT-WITH-DOCUMENT] Response received: {len(ai_response)} chars")
            
            return success_response({
                'response': ai_response,
                'session_id': session_id,
                'files_processed': len(files)
            })
            
        except Exception as e:
            print(f"[CHAT-WITH-DOCUMENT] Claude API error: {e}")
            return error_response(f"Document processing failed: {str(e)}", 500)
            
    except Exception as e:
        print(f"[CHAT-WITH-DOCUMENT] Error: {e}")
        return error_response(str(e), 500)


@agent_bp.route('/chat-with-document-stream', methods=['POST'])
def agent_chat_with_document_stream():
    """Legacy document chat endpoint - streaming version"""
    try:
        session_id = request.form.get('session_id')
        prompt = request.form.get('prompt', '')
        
        files = request.files.getlist('files')
        if not files:
            return error_response("No files uploaded", 400)
        
        try:
            content_blocks = process_file_uploads(files)
        except FileValidationError as e:
            return error_response(str(e), 400)
        
        state = agent_state_manager.get_or_create_state(
            agent_id='data_agent',
            session_id=session_id,
            context={'ui_context': 'data_agent_chat'}
        )
        session_id = state['session_id']
        
        lock = agent_state_manager.get_lock('data_agent', session_id)
        queue = agent_state_manager.get_queue('data_agent', session_id)
        agent_state_manager.update_status('data_agent', session_id, 'processing')
        
        threading.Thread(
            target=run_agent_worker,
            args=('data_agent', prompt, content_blocks, lock, session_id, queue, state['conversation'], state['context']),
            daemon=True
        ).start()
        
        return success_response({
            'status': 'processing',
            'session_id': session_id,
            'files_uploaded': len(content_blocks)
        })
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================
# SIMPLE CHAT ENDPOINT (for CHAT.ps1 CLI)
# ============================================================

@agent_bp.route('/chat', methods=['POST'])
def simple_chat():
    """
    Simple chat endpoint for CLI usage (CHAT.ps1)
    Routes to proper agent worker with user credentials
    
    POST /api/agent/chat
    {
        "message": "Create a Google Doc titled 'Test'",
        "source": "cli",
        "context": {"tools_enabled": true}
    }
    
    Returns:
    {
        "response": "AI response text",
        "tool_calls": [{"name": "tool_name", "success": true}]
    }
    """
    from flask import request, current_app, jsonify
    from auth.user_auth import UserAuthManager
    import threading
    import secrets
    from datetime import datetime
    from queue import Queue, Empty
    from core.combined_agent_worker import agent_worker
    
    try:
        # Get user from JWT token (if provided)
        auth_header = request.headers.get('Authorization', '')
        user_id = None
        user_email = None
        
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '').strip()
            try:
                auth_manager = UserAuthManager()
                user_data = auth_manager.verify_token(token)
                if user_data:
                    user_id = user_data.get('user_id')
                    user_email = user_data.get('email')
                    print(f"🔑 Chat request from user_id={user_id} ({user_email})")
            except Exception as e:
                print(f"⚠️ Token verification failed: {e}")
        
        # If no user_id, default to user_id=1
        if not user_id:
            user_id = 1
            user_email = "gerardo@vetsuccessacademy.com"
            print(f"🔑 Chat request using default user_id={user_id} ({user_email})")
        
        data = request.json or {}
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Missing message'}), 400
        
        # ========================================================================
        # LOG: What's included in the user's message request
        # ========================================================================
        print("\n" + "="*80)
        print("📨 [USER MESSAGE RECEIVED]")
        print("="*80)
        print(f"   User ID: {user_id}")
        print(f"   Email: {user_email}")
        print(f"   Message Length: {len(message)} characters")
        print(f"   Message Preview: {message[:100]}{'...' if len(message) > 100 else ''}")
        print(f"\n   Request Data Keys: {list(data.keys())}")
        
        # Log all included data fields
        if 'context' in data:
            print(f"   ✅ Context Included: {data['context']}")
        if 'conversation_history' in data:
            history = data.get('conversation_history', [])
            print(f"   ✅ Conversation History: {len(history)} messages")
        if 'thread_id' in data:
            print(f"   ✅ Thread ID: {data['thread_id']}")
        if 'source' in data:
            print(f"   ✅ Source: {data['source']}")
        if 'attachments' in data:
            attachments = data.get('attachments', [])
            print(f"   ✅ Attachments: {len(attachments)} files")
            for att in attachments:
                print(f"      - {att.get('name', 'unknown')} ({att.get('type', 'unknown')})")
        if 'model' in data:
            print(f"   ✅ Model Override: {data['model']}")
        if 'tools_enabled' in data:
            print(f"   ✅ Tools Enabled: {data['tools_enabled']}")
        
        # Log request headers
        print(f"\n   Request Headers:")
        print(f"      Content-Type: {request.headers.get('Content-Type', 'not set')}")
        print(f"      User-Agent: {request.headers.get('User-Agent', 'not set')[:50]}...")
        print(f"      Authorization: {'Present (Bearer)' if auth_header else 'Not provided'}")
        print("="*80 + "\n")
        
        # Generate session ID
        session_id = f"cli_{int(datetime.now().timestamp()*1000)}_{secrets.token_urlsafe(8)}"
        
        # Initialize AI client
        ai_client = current_app.config.get('AI_CLIENT')
        if ai_client is None:
            from core.unified_ai_client import initialize_ai_client
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from config import Config
            ai_client = initialize_ai_client(str(Config.DB_CONFIG_PATH))
            current_app.config['AI_CLIENT'] = ai_client
        
        # Prepare response containers
        response_text = None
        tool_calls_list = []
        error_message = None
        start_time = datetime.now()
        
        # Create queue for agent response
        response_queue = Queue()
        
        def collect_response():
            """Collect response from agent worker"""
            nonlocal response_text, tool_calls_list, error_message
            
            try:
                # Track timing
                request_start = datetime.now()
                
                # Run agent worker (blocking call with user_id for credential injection)
                result = agent_worker(
                    message=message,
                    session_id=session_id,
                    user_id=user_id,  # CRITICAL: Pass user_id for OAuth credential lookup
                    conversation_history=[],
                    ai_client=ai_client,
                    attachments=data.get('attachments')  # Pass file attachments
                )
                
                # Calculate response time
                response_time_ms = int((datetime.now() - request_start).total_seconds() * 1000)
                
                response_text = result.get('response', '')
                tool_calls_list = result.get('tool_calls', [])
                
                # Save messages to database with metadata
                try:
                    from thread_manager import ThreadManager
                    from utils.database_helpers import get_sessions_database_path
                    
                    thread_id = data.get('thread_id') or session_id
                    thread_mgr = ThreadManager(get_sessions_database_path())
                    
                    # Save user message
                    thread_mgr.add_message(
                        workspace_slug='default',
                        thread_slug=thread_id,
                        role='user',
                        content=message,
                        prompt=message,
                        user_id=user_id,
                        include=True,
                        tool_calls=None,
                        tokens_used=None,
                        response_time_ms=None,
                        metadata={}
                    )
                    
                    # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
                    estimated_tokens = int(len(response_text) / 4)
                    
                    # Save assistant message with metadata
                    thread_mgr.add_message(
                        workspace_slug='default',
                        thread_slug=thread_id,
                        role='assistant',
                        content=response_text,
                        prompt=None,
                        user_id=user_id,
                        include=True,
                        tool_calls=tool_calls_list,
                        tokens_used=estimated_tokens,
                        response_time_ms=response_time_ms,
                        metadata={
                            'model': 'claude-sonnet-4-5-20250929',
                            'session_id': session_id,
                            'source': 'cli'
                        }
                    )
                    
                    print(f"💾 [Message Save] Saved to thread {thread_id} - {response_time_ms}ms, ~{estimated_tokens} tokens")
                    
                except Exception as save_error:
                    print(f"⚠️ [Message Save] Failed to save messages: {save_error}")
                    import traceback
                    traceback.print_exc()
                
                response_text = result.get('response', '')
                tool_calls_list = result.get('tool_calls', [])
                
                # ========================================================================
                # LOG: What's being sent back to the user
                # ========================================================================
                print("\n" + "="*80)
                print("📤 [AGENT RESPONSE GENERATED]")
                print("="*80)
                print(f"   Session ID: {session_id}")
                print(f"   User ID: {user_id}")
                print(f"   Response Length: {len(response_text)} characters")
                print(f"   Response Preview: {response_text[:150]}{'...' if len(response_text) > 150 else ''}")
                print(f"   Tool Calls Made: {len(tool_calls_list)}")
                
                if tool_calls_list:
                    print(f"\n   Tools Used:")
                    for i, tool_call in enumerate(tool_calls_list, 1):
                        tool_name = tool_call.get('name', 'unknown')
                        tool_success = tool_call.get('success', False)
                        tool_status = "✅ Success" if tool_success else "❌ Failed"
                        print(f"      {i}. {tool_name} - {tool_status}")
                        if 'error' in tool_call:
                            print(f"         Error: {tool_call['error']}")
                
                print("="*80 + "\n")
                
                response_queue.put({'success': True})
                
            except Exception as e:
                error_message = str(e)
                response_queue.put({'success': False, 'error': error_message})
        
        # Run agent in thread
        worker_thread = threading.Thread(target=collect_response, daemon=True)
        worker_thread.start()
        worker_thread.join(timeout=120)  # 2 minute timeout
        
        # Check result
        try:
            result = response_queue.get(timeout=1)
            if not result.get('success'):
                return jsonify({'error': result.get('error', 'Unknown error')}), 500
        except Empty:
            return jsonify({'error': 'Request timeout'}), 504
        
        return jsonify({
            'response': response_text or 'No response generated',
            'tool_calls': tool_calls_list,
            'session_id': session_id,
            'user_id': user_id
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============================================================
# QUOTE ENDPOINT (InHouse Print Context)
# ============================================================

@agent_bp.route('/quote', methods=['POST'])
def quote_chat():
    """
    Quote-specific chat endpoint with InHouse Print context
    Routes to Viki agent worker with SQL and calculator tools
    
    POST /api/agent/quote
    {
        "message": "Quote for 1000 business cards",
        "source": "web",
        "context": {"tools_enabled": true}
    }
    
    Returns:
    {
        "response": "AI response with quote details",
        "tool_calls": [{"name": "inhouse_calculate_quote", "success": true}]
    }
    """
    from flask import request, current_app, jsonify
    from auth.user_auth import UserAuthManager
    import threading
    import secrets
    from datetime import datetime
    from queue import Queue, Empty
    from core.combined_agent_worker import agent_worker
    
    try:
        # Get user from JWT token (if provided)
        auth_header = request.headers.get('Authorization', '')
        user_id = None
        user_email = None
        
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '').strip()
            try:
                auth_manager = UserAuthManager()
                user_data = auth_manager.verify_token(token)
                if user_data:
                    user_id = user_data.get('user_id')
                    user_email = user_data.get('email')
                    print(f"🔑 Quote request from user_id={user_id} ({user_email})")
            except Exception as e:
                print(f"⚠️ Token verification failed: {e}")
        
        # If no user_id, default to user_id=1
        if not user_id:
            user_id = 1
            user_email = "gerardo@vetsuccessacademy.com"
            print(f"🔑 Quote request using default user_id={user_id} ({user_email})")
        
        data = request.json or {}
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Missing message'}), 400
        
        # Generate session ID
        session_id = f"quote_{int(datetime.now().timestamp()*1000)}_{secrets.token_urlsafe(8)}"
        
        # Initialize AI client
        ai_client = current_app.config.get('AI_CLIENT')
        if ai_client is None:
            from core.unified_ai_client import initialize_ai_client
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from config import Config
            ai_client = initialize_ai_client(str(Config.DB_CONFIG_PATH))
            current_app.config['AI_CLIENT'] = ai_client
        
        # Prepare response containers
        response_text = None
        tool_calls_list = []
        error_message = None
        
        # Create queue for agent response
        response_queue = Queue()
        
        def collect_response():
            """Collect response from agent worker with quote context"""
            nonlocal response_text, tool_calls_list, error_message
            
            try:
                # Run agent worker with quote_agent context (routes to Viki prompt)
                result = agent_worker(
                    message=message,
                    session_id=session_id,
                    user_id=user_id,
                    conversation_history=[],
                    ai_client=ai_client,
                    context='quote_agent'  # CRITICAL: Routes to Viki InHouse prompt
                )
                
                response_text = result.get('response', '')
                tool_calls_list = result.get('tool_calls', [])
                
                response_queue.put({'success': True})
                
            except Exception as e:
                error_message = str(e)
                response_queue.put({'success': False, 'error': error_message})
        
        # Run agent in thread
        worker_thread = threading.Thread(target=collect_response, daemon=True)
        worker_thread.start()
        worker_thread.join(timeout=120)  # 2 minute timeout
        
        # Check result
        try:
            result = response_queue.get(timeout=1)
            if not result.get('success'):
                return jsonify({'error': result.get('error', 'Unknown error')}), 500
        except Empty:
            return jsonify({'error': 'Request timeout'}), 504
        
        return jsonify({
            'response': response_text or 'No response generated',
            'tool_calls': tool_calls_list,
            'session_id': session_id,
            'user_id': user_id,
            'context': 'quote_agent'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============================================================
# TOOLS ENDPOINT
# ============================================================

@agent_bp.route('/tools', methods=['GET'])
def get_tools():
    """
    Get COMPLETE list of available tools from ALL sources
    
    Returns:
    {
        "total_tools": 641,
        "sources": {
            "registry_v3": 584,
            "tool_use_agent": 57,
            "server_tools": 1  (web_search)
        },
        "capabilities": {
            "extended_thinking": true,
            "interleaved_thinking": true,
            "web_search": true
        },
        "platforms": ["google", "microsoft", "woocommerce", ...],
        "tools": [...]
    }
    """
    try:
        # Get registry tools (584)
        registry = get_registry()
        registry_tools = []
        for tool_name, tool_info in registry.tools.items():
            registry_tools.append({
                "name": tool_name,
                "description": tool_info.get("description", ""),
                "category": tool_info.get("category", "general"),
                "platform": tool_info.get("platform", "other"),
                "source": "registry_v3",
                "parameters": tool_info.get("input_schema", {})
            })
        
        # Get ToolUseAgent tools (57) if available - OPTIONAL quote calculator tools
        tool_use_agent_tools = []
        try:
            import sys
            import os
            calculator_module_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'UI', 'external', 'modules', 'calculator-module', 'ORIGINAL'
            )
            sys.path.insert(0, calculator_module_path)
            from tool_use_agent import ToolUseAgent
            
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'database-config.json')
            agent = ToolUseAgent(config_path)
            agent_tool_defs = agent._get_tool_definitions()
            
            for tool_def in agent_tool_defs:
                tool_use_agent_tools.append({
                    "name": tool_def.get("name", ""),
                    "description": tool_def.get("description", ""),
                    "category": "printing_business",
                    "platform": "in_house_print",
                    "source": "tool_use_agent",
                    "parameters": tool_def.get("input_schema", {})
                })
            
            logger.info(f"✅ Loaded {len(tool_use_agent_tools)} ToolUseAgent quote calculator tools")
        except Exception as e:
            # This is OPTIONAL - system has calculator tools in registry_v3
            logger.debug(f"Quote Calculator ToolUseAgent not available (optional): {e}")
        
        # Server tools
        server_tools = [{
            "name": "web_search",
            "description": "Search the web for current information (pricing, contacts, specs, market data)",
            "category": "search",
            "platform": "anthropic",
            "source": "server_tool",
            "type": "web_search_20250305",
            "location": "Brisbane, Queensland, Australia"
        }]
        
        # Merge all tools
        all_tools = registry_tools + tool_use_agent_tools + server_tools
        
        # Group by platform
        platforms = {}
        for tool in all_tools:
            platform = tool.get("platform", "other")
            if platform not in platforms:
                platforms[platform] = []
            platforms[platform].append(tool["name"])
        
        return success_response({
            "total_tools": len(all_tools),
            "sources": {
                "registry_v3": len(registry_tools),
                "tool_use_agent": len(tool_use_agent_tools),
                "server_tools": len(server_tools)
            },
            "capabilities": {
                "extended_thinking": True,
                "interleaved_thinking": True,
                "web_search": True,
                "web_fetch": False,
                "document_processing": True,
                "thinking_budget_tokens": 5000
            },
            "platforms": list(platforms.keys()),
            "platform_counts": {k: len(v) for k, v in platforms.items()},
            "tools": all_tools
        })
    except Exception as e:
        return error_response(f"Failed to load tools: {str(e)}", 500)


# ============================================================
# USER FEEDBACK AREA API ENDPOINTS (FEATURE 2)
# ============================================================
# Feature 2: User sends instructions mid-execution (non-blocking)
# User clicks SEND → Stored → Auto-injected by execute_tool()
# Different from Feature 1 (user_interaction) where AI asks user
# ============================================================

@agent_bp.route('/user-feedback/submit', methods=['POST'])
def submit_user_feedback():
    """
    Store user feedback when SEND button clicked
    
    Flow:
    1. User types in textarea: "Focus on legal emails"
    2. User clicks SEND button
    3. Frontend POSTs here
    4. Stored in _feedback_storage
    5. execute_tool() checks on next tool call
    6. Injects into tool result
    7. AI sees feedback and adjusts
    8. Feedback deleted after injection
    
    Returns:
        JSON success response
    """
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        instructions = data.get('instructions', '').strip()
        
        if not session_id:
            return jsonify({
                "success": False,
                "error": "session_id required"
            }), 400
        
        if not instructions:
            return jsonify({
                "success": False,
                "error": "instructions cannot be empty"
            }), 400
        
        # Store feedback (will be read by execute_tool() on next call)
        feedback_key = f"user_feedback_{session_id}"
        _feedback_storage[feedback_key] = {
            'instructions': instructions,
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        
        logger.info(f"[USER FEEDBACK] Stored for session {session_id}: {instructions[:50]}...")
        
        return jsonify({
            "success": True,
            "data": {
                "received": True,
                "message": "Feedback stored - will inject on next tool call",
                "instructions_length": len(instructions),
                "timestamp": datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"[USER FEEDBACK] Error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@agent_bp.route('/user-feedback/check/<session_id>', methods=['GET'])
def check_user_feedback(session_id):
    """
    Check if user feedback exists (called by execute_tool())
    
    Fast check (~20ms) - returns immediately with yes/no.
    If feedback exists, returns it and deletes from storage.
    Also stores notification that feedback was injected for UI polling.
    
    Args:
        session_id: Session identifier
    
    Returns:
        JSON with has_feedback boolean and feedback text
    """
    try:
        feedback_key = f"user_feedback_{session_id}"
        
        if feedback_key in _feedback_storage:
            # Get and delete (one-time read)
            feedback_data = _feedback_storage.pop(feedback_key)
            instructions = feedback_data.get('instructions', '').strip()
            
            logger.info(f"[USER FEEDBACK] Checked session {session_id}: Found feedback")
            
            # Store injection notification for UI to poll
            notification_key = f"feedback_injected_{session_id}"
            _feedback_injection_notifications[notification_key] = {
                'injected': True,
                'feedback': instructions,
                'timestamp': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(seconds=60)).isoformat()
            }
            
            return jsonify({
                "has_feedback": True,
                "feedback": instructions,
                "timestamp": feedback_data.get('timestamp')
            }), 200
        
        # No feedback
        return jsonify({
            "has_feedback": False,
            "feedback": ""
        }), 200
        
    except Exception as e:
        logger.error(f"[USER FEEDBACK] Check error: {e}", exc_info=True)
        return jsonify({
            "has_feedback": False,
            "feedback": "",
            "error": str(e)
        }), 500


@agent_bp.route('/user-feedback/injection-status/<session_id>', methods=['GET'])
def get_feedback_injection_status(session_id):
    """
    Poll for feedback injection notification (called by frontend after SEND)
    
    Frontend polls this every 500ms after clicking SEND to detect when
    AI has picked up and injected the feedback into tool execution.
    
    Once notification is read, it's deleted (one-time notification).
    Notifications auto-expire after 30 seconds.
    
    Args:
        session_id: Session identifier
    
    Returns:
        JSON with:
        - injected: boolean (true if feedback was injected into execute_tool)
        - feedback: string (the feedback that was injected)
        - timestamp: when injection occurred
    """
    try:
        notification_key = f"feedback_injected_{session_id}"
        
        # Clean up expired notifications first
        _cleanup_expired_notifications()
        
        if notification_key in _feedback_injection_notifications:
            # Get and delete (one-time read)
            notification = _feedback_injection_notifications.pop(notification_key)
            
            logger.info(f"[FEEDBACK NOTIFICATION] Session {session_id}: Notifying UI of injection")
            
            return jsonify({
                "injected": True,
                "feedback": notification.get('feedback', ''),
                "timestamp": notification.get('timestamp'),
                "message": "AI received your feedback and is adjusting its work!"
            }), 200
        
        # No injection yet
        return jsonify({
            "injected": False,
            "message": "Waiting for AI to pick up feedback..."
        }), 200
        
    except Exception as e:
        logger.error(f"[FEEDBACK NOTIFICATION] Error: {e}", exc_info=True)
        return jsonify({
            "injected": False,
            "error": str(e)
        }), 500


def _cleanup_expired_notifications():
    """Remove expired feedback injection notifications"""
    now = datetime.now()
    expired_keys = [
        key for key, value in _feedback_injection_notifications.items()
        if datetime.fromisoformat(value['expires_at']) < now
    ]
    for key in expired_keys:
        _feedback_injection_notifications.pop(key, None)


# ============================================================
# DEPRECATED ENDPOINT - REMOVED
# ============================================================
# The /chat endpoint has been removed. Use /agent/<agent_id>/start instead.
# This provides full support for tools, web search, file uploads, and streaming.
