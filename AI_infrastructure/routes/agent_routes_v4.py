"""
AGENT ROUTES V3 - FIXED: Database as Source of Truth

KEY ARCHITECTURAL CHANGES:
1. Frontend sends ONLY current message (not full conversation history)
2. Backend loads conversation from database (authoritative source)
3. Backend appends user message → processes → saves AI response
4. Backend returns complete conversation to frontend

RETAINED FEATURES (ALL):
- User preferences injection (nickname, auth_platform, communication_style, detail_level, preferred_tools, AI memories)
- Location detection and weather (temperature, season, time context)
- Comprehensive context injection (Synergy Sessions, Workflow Automation, Internal Documentation)
- Prompt injection system (quick_actions, library_prompts, custom_prompt)
- All detailed print statements for debugging
- Conversation pruning for context limits
- File upload handling details
- Auto-save with rich metadata
- Thread isolation fixes
- All careful validation and error handling
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


# ============================================================
# NEW: DATABASE CONVERSATION LOADER (Source of Truth)
# ============================================================

def load_conversation_from_database(thread_slug: str, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Load conversation history from database with optional pagination.
    This is the AUTHORITATIVE source of truth for all conversations.
    
    Args:
        thread_slug: Thread identifier
        limit: Max messages to return (None = all messages)
        offset: Number of messages to skip (for pagination)
    """
    print(f"\n{'='*80}")
    print(f"[DB LOAD] Loading conversation from database")
    print(f"{'='*80}")
    print(f"[DB LOAD] Thread Slug: {thread_slug}")
    if limit:
        print(f"[DB LOAD] Pagination: limit={limit}, offset={offset}")
    
    try:
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            # Get thread ID from thread_slug
            cursor.execute("""
                SELECT id FROM sessions.threads 
                WHERE thread_slug = %s
            """, (thread_slug,))
            
            thread_row = cursor.fetchone()
            
            if not thread_row:
                print(f"[DB LOAD] ℹ️  Thread not found in database - this is a NEW conversation")
                print(f"{'='*80}\n")
                return []  # Empty conversation for new threads
            
            thread_id = thread_row[0] if isinstance(thread_row, tuple) else thread_row['id']
            print(f"[DB LOAD] Thread ID: {thread_id}")
            
            # Get messages for this thread (with optional pagination)
            if limit:
                # Paginated query - get MOST RECENT messages first
                cursor.execute("""
                    SELECT role, content, created_at, model, tokens_used
                    FROM sessions.messages 
                    WHERE thread_id = %s 
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, (thread_id, limit, offset))
            else:
                # Get ALL messages (ordered by creation time)
                cursor.execute("""
                    SELECT role, content, created_at, model, tokens_used
                    FROM sessions.messages 
                    WHERE thread_id = %s 
                    ORDER BY created_at ASC
                """, (thread_id,))
            
            rows = cursor.fetchall()
            print(f"[DB LOAD] Found {len(rows)} messages in database")
            
            messages = []
            for idx, row in enumerate(rows):
                if isinstance(row, tuple):
                    role, content, created_at, model, tokens_used = row
                else:
                    role = row['role']
                    content = row['content']
                    created_at = row['created_at']
                    model = row.get('model')
                    tokens_used = row.get('tokens_used')
                
                # Parse JSONB content
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except Exception as e:
                        print(f"[DB LOAD] ⚠️  Message {idx} content parse failed: {e}")
                        content = [{'type': 'text', 'text': content}]
                
                messages.append({
                    'role': role,
                    'content': content
                })
                
                content_preview = str(content)[:100] if isinstance(content, str) else f"{len(content)} blocks"
                print(f"[DB LOAD]   [{idx}] {role}: {content_preview}...")
            
            print(f"[DB LOAD] ✅ Loaded {len(messages)} messages from database")
            print(f"{'='*80}\n")
            
            return messages
        
    except Exception as e:
        print(f"[DB LOAD] ❌ ERROR loading conversation: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*80}\n")
        return []


def save_message_to_database(thread_slug: str, role: str, content: Any, 
                             user_id: Optional[int] = None,
                             model: Optional[str] = None,
                             tokens_used: Optional[int] = None,
                             metadata: Optional[Dict] = None) -> bool:
    """
    Save a single message to the database immediately with transaction management.
    """
    print(f"[DB SAVE] 💾 Saving {role} message to database...")
    print(f"[DB SAVE] Thread slug: {thread_slug}")
    print(f"[DB SAVE] User ID: {user_id}")
    
    conn = None
    cursor = None
    
    try:
        from psycopg2.extras import Json
        
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            # Begin explicit transaction
            cursor.execute("BEGIN")
            
            # Step 1: Check if thread exists
            cursor.execute("""
                SELECT id FROM sessions.threads 
                WHERE thread_slug = %s
            """, (thread_slug,))
            
            thread_row = cursor.fetchone()
            
            if not thread_row:
                # Thread doesn't exist - create it first
                print(f"[DB SAVE] Thread doesn't exist - creating thread {thread_slug}")
                
                cursor.execute("""
                    INSERT INTO sessions.threads 
                    (thread_slug, user_id, name, created_at, updated_at)
                    VALUES (%s, %s, %s, NOW(), NOW())
                    RETURNING id
                """, (thread_slug, user_id or 1, 'New Chat'))
                
                thread_row = cursor.fetchone()
                print(f"[DB SAVE] ✅ Thread created: {thread_slug}")
            
            thread_id = thread_row[0] if isinstance(thread_row, tuple) else thread_row['id']
            print(f"[DB SAVE] Thread ID: {thread_id}")
            
            # Step 2: Format content for JSONB storage
            try:
                if isinstance(content, (list, dict)):
                    content_value = Json(content)
                elif isinstance(content, str):
                    if not content.strip().startswith(('[', '{')):
                        content_value = Json([{'type': 'text', 'text': content}])
                    else:
                        try:
                            parsed = json.loads(content)
                            content_value = Json(parsed)
                        except:
                            content_value = Json([{'type': 'text', 'text': content}])
                else:
                    content_value = Json([{'type': 'text', 'text': str(content)}])
                
                print(f"[DB SAVE] Content formatted as JSONB")
            except Exception as json_error:
                print(f"[DB SAVE] ⚠️ JSON formatting failed, using string fallback: {json_error}")
                content_value = Json([{'type': 'text', 'text': str(content)}])
            
            # Step 3: Prepare metadata
            try:
                metadata_val = json.dumps(metadata) if metadata else None
            except Exception as meta_error:
                print(f"[DB SAVE] ⚠️ Metadata serialization failed: {meta_error}")
                metadata_val = None
            
            # Step 4: Insert message
            cursor.execute("""
                INSERT INTO sessions.messages 
                (thread_id, session_id, role, content, user_id, model, tokens_used, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                RETURNING id
            """, (thread_id, thread_slug, role, content_value, user_id, model, tokens_used, metadata_val))
            
            message_row = cursor.fetchone()
            message_id = message_row[0] if isinstance(message_row, tuple) else message_row['id']
            
            # Commit transaction
            cursor.execute("COMMIT")
            print(f"[DB SAVE] ✅ Transaction committed")
            
            # Verify message was saved
            cursor.execute("""
                SELECT id FROM sessions.messages 
                WHERE id = %s
            """, (message_id,))
            
            if cursor.fetchone():
                print(f"[DB SAVE] ✅ Verified: Message exists in database (ID: {message_id})")
            else:
                print(f"[DB SAVE] ⚠️ WARNING: Message not found after save!")
                return False
            
            print(f"[DB SAVE] ✅ Saved {role} message to database (message ID: {message_id})")
            return True
        
    except Exception as e:
        # Rollback on error
        if cursor:
            try:
                cursor.execute("ROLLBACK")
                print(f"[DB SAVE] 🔄 Transaction rolled back")
            except:
                pass
        
        print(f"\n{'='*80}")
        print(f"[DB SAVE] ❌❌❌ CRITICAL ERROR: Failed to save message!")
        print(f"{'='*80}")
        print(f"[DB SAVE] Error type: {type(e).__name__}")
        print(f"[DB SAVE] Error: {e}")
        print(f"[DB SAVE] Thread slug: {thread_slug}")
        print(f"[DB SAVE] Role: {role}")
        print(f"[DB SAVE] User ID: {user_id}")
        print(f"[DB SAVE] Content type: {type(content)}")
        import traceback
        print(f"[DB SAVE] Traceback:")
        traceback.print_exc()
        print(f"{'='*80}\n")
        return False


# ============================================================
# TOOL EXECUTOR (Unchanged)
# ============================================================

class ToolExecutor:
    """Executes tools with proper credential injection and error handling"""

    def __init__(self, registry: Optional[RegistryV3] = None):
        self.registry = registry or get_registry()
        logger.info(f"✅ ToolExecutor initialized with registry ({len(self.registry.tools)} tools)")

    def validate_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate tool call before execution"""
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return False, f"Tool not found: {tool_name}"
        
        schema = tool.get("parameters", {})
        for param_name, param_def in schema.items():
            if param_def.get("required") and param_name not in parameters:
                return False, f"Missing required parameter: {param_name}"
        
        return True, None

    def inject_credentials(self, parameters: Dict[str, Any], 
                          user_id: Optional[int] = None,
                          credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add credential injection parameters to tool call"""
        injected_params = parameters.copy()
        
        if user_id:
            injected_params["_user_id"] = user_id
        
        if credentials:
            injected_params["_injected_credentials"] = credentials
        
        if user_id or credentials:
            logger.debug(f"🔐 Credentials injected: user_id={user_id}, has_credentials={bool(credentials)}")
        
        return injected_params

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any],
                    user_id: Optional[int] = None,
                    credentials: Optional[Dict[str, Any]] = None,
                    stream: bool = False) -> Any:
        """Execute a tool with credential injection"""
        is_valid, error_msg = self.validate_tool_call(tool_name, parameters)
        if not is_valid:
            logger.error(f"Tool validation failed: {error_msg}")
            raise ValueError(error_msg)
        
        injected_params = self.inject_credentials(parameters, user_id, credentials)
        
        func = self.registry.get_tool_function(tool_name)
        if not func:
            raise ValueError(f"Tool implementation not found: {tool_name}")
        
        try:
            logger.info(f"🔧 Executing tool: {tool_name}")
            result = func(**injected_params)
            
            if isinstance(result, dict) and result.get('status') == 'confirmation_required':
                logger.info(f"⏸️  Tool {tool_name} requested user confirmation")
                return result
            
            if stream and hasattr(result, '__iter__'):
                return result
            else:
                return result
                
        except Exception as e:
            logger.error(f"❌ Tool execution failed for {tool_name}: {e}", exc_info=True)
            raise

    def list_tools_for_platform(self, platform: str) -> List[Dict[str, Any]]:
        """Get all tools for a platform with metadata"""
        tool_names = self.registry.list_tools_by_platform(platform)
        return [self.registry.get_tool(name) for name in tool_names if self.registry.get_tool(name)]


class ToolCallProcessor:
    """Processes tool calls from Claude API"""

    def __init__(self, executor: Optional[ToolExecutor] = None):
        self.executor = executor or ToolExecutor()

    def process_tool_call(self, tool_name: str, tool_input: Dict[str, Any],
                         user_id: Optional[int] = None,
                         credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a single tool call from Claude"""
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
        """Process multiple tool calls"""
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


def create_tool_executor() -> ToolExecutor:
    """Create and return a ToolExecutor instance"""
    return ToolExecutor()


def create_tool_processor() -> ToolCallProcessor:
    """Create and return a ToolCallProcessor instance"""
    return ToolCallProcessor()


def validate_request_credentials(request_data: Dict[str, Any]) -> tuple[Optional[int], Optional[Dict[str, Any]]]:
    """Extract and validate user credentials from Flask request"""
    user_id = request_data.get("_user_id")
    credentials = request_data.get("_injected_credentials")
    return user_id, credentials


# ============================================================
# FLASK ROUTES INTEGRATION
# ============================================================

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
import sys

# Create blueprint
agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')

# In-memory storage for user feedback
_feedback_storage = {}
_feedback_injection_notifications = {}


# ============================================================
# AUTHENTICATION MIDDLEWARE
# ============================================================

@agent_bp.before_request
def extract_user_from_token():
    """Extract user_id from JWT token in Authorization header"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        g.user_id = 1
        return
    
    token = auth_header.replace('Bearer ', '').strip()
    
    try:
        from auth.user_auth import UserAuthManager
        auth_manager = UserAuthManager()
        user_data = auth_manager.verify_token(token)
        
        if user_data:
            g.user_id = user_data.get('user_id')
            g.user_email = user_data.get('email')
            print(f"🔑 [AUTH] Request authenticated: user_id={g.user_id}, email={g.user_email}")
        else:
            g.user_id = 1
            print(f"⚠️ [AUTH] Token verification failed - using default user_id=1")
    
    except Exception as e:
        g.user_id = 1
        print(f"⚠️ [AUTH] Token verification error: {e} - using default user_id=1")


# ============================================================
# FIXED: START ENDPOINT (Database as Source of Truth)
# ============================================================

@agent_bp.route('/agent/<agent_id>/start', methods=['POST'])
def start_agent(agent_id):
    """
    FIXED: Database as source of truth
    """
    print(f"\n{'='*80}")
    print(f"[START] Agent {agent_id} - Request received (DATABASE AS SOURCE OF TRUTH)")
    print(f"{'='*80}")
    
    try:
        # Detect content type
        is_form_data = request.content_type and 'multipart/form-data' in request.content_type
        
        if is_form_data:
            print(f"[START] Processing as multipart/form-data")
            data = request.form
            thread_slug = request.form.get('thread_slug') or request.form.get('thread_id')
            message = request.form.get('message', '')
            files = request.files.getlist('files')
            
            if not files:
                return error_response("No files uploaded", 400)
            
            try:
                content_blocks = process_file_uploads(files)
            except FileValidationError as e:
                return error_response(str(e), 400)
            
            file_data = content_blocks
        else:
            print(f"[START] Processing as JSON")
            data = request.json or {}
            thread_slug = data.get('thread_slug') or data.get('thread_id')
            message = data.get('message', '')
            file_data = None
        
        # ============================================
        # VALIDATION
        # ============================================
        if not thread_slug:
            return error_response("Missing 'thread_slug' in request", 400)
        
        if not message:
            return error_response("Missing 'message' in request", 400)
        
        print(f"[START] thread_slug: {thread_slug}")
        print(f"[START] message length: {len(message)} chars")
        print(f"[START] message preview: {message[:100]}...")
        
        # ============================================
        # STEP 1: LOAD CONVERSATION FROM DATABASE
        # ============================================
        print(f"\n[START] 📂 STEP 1: Loading conversation from database...")
        conversation = load_conversation_from_database(thread_slug)
        original_length = len(conversation)
        print(f"[START] ✅ Loaded {original_length} messages from database")
        
        # ============================================
        # STEP 2: PRUNE CONVERSATION IF TOO LARGE
        # ============================================
        if len(conversation) > 0:
            from core.combined_agent_worker import prune_conversation_for_context_limit
            conversation = prune_conversation_for_context_limit(
                conversation,
                max_estimated_tokens=180000,
                preserve_first_user=True
            )
            if len(conversation) < original_length:
                print(f"[START] 🔧 Pruned conversation: {original_length} → {len(conversation)} messages")
        
        # ============================================
        # STEP 3: APPEND USER MESSAGE (in memory)
        # ============================================
        print(f"\n[START] 📝 STEP 3: Appending user message to conversation...")
        user_message_content = message
        if file_data:
            user_message_content = file_data + [{'type': 'text', 'text': message}]
        
        user_message = {
            'role': 'user',
            'content': user_message_content
        }
        conversation.append(user_message)
        print(f"[START] ✅ User message appended (conversation now has {len(conversation)} messages)")
        
        # ============================================
        # STEP 4: SAVE USER MESSAGE (thread creation handled inside save_message)
        # ============================================
        print(f"\n[START] 💾 STEP 4: Saving user message to database...")
        user_id = g.get('user_id', 1)
        
        print(f"[START] 🔍 DEBUG: About to save user message...")
        print(f"[START] 🔍 DEBUG: thread_slug = {thread_slug}")
        print(f"[START] 🔍 DEBUG: user_id = {user_id}")
        print(f"[START] 🔍 DEBUG: content type = {type(user_message_content)}")
        print(f"[START] 🔍 DEBUG: content preview = {str(user_message_content)[:200]}")
        
        # Try saving with retry logic
        max_retries = 3
        save_success = False
        
        for attempt in range(max_retries):
            save_success = save_message_to_database(
                thread_slug=thread_slug,
                role='user',
                content=user_message_content,
                user_id=user_id,
                metadata={'source': 'web_ui', 'has_files': bool(file_data)}
            )
            
            if save_success:
                print(f"[START] ✅✅✅ SUCCESS: User message saved to database (attempt {attempt + 1})")
                break
            else:
                print(f"[START] ⚠️ Save attempt {attempt + 1}/{max_retries} failed")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff
        
        print(f"[START] 🔍 DEBUG: Final save_success = {save_success}")
        
        if not save_success:
            print(f"[START] ❌❌❌ CRITICAL: Failed to save user message after {max_retries} attempts!")
            print(f"[START] ❌ Cannot continue without saving user message!")
            return error_response(
                f"Failed to save message to database after {max_retries} attempts. Please try again.",
                500
            )
        
        # ============================================
        # STEP 5: UPDATE STATE MANAGER (for worker)
        # ============================================
        print(f"\n[START] 🔄 STEP 5: Updating state manager for worker...")
        state = agent_state_manager.get_or_create_state(agent_id, thread_slug)
        state['conversation'] = conversation
        print(f"[START] ✅ State updated (conversation: {len(conversation)} messages)")
        
        # ============================================
        # STEP 6: START AI WORKER THREAD
        # ============================================
        print(f"\n[START] 🤖 STEP 6: Starting AI worker thread...")
        
        lock = agent_state_manager.get_lock(agent_id, thread_slug)
        queue = agent_state_manager.get_queue(agent_id, thread_slug)
        agent_state_manager.update_status(agent_id, thread_slug, 'processing')
        
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
        
        if file_data:
            threading.Thread(
                target=run_agent_worker,
                args=(agent_id, message, file_data, lock, thread_slug, queue, 
                      state['conversation'], state['context'], user_id, thread_slug),
                daemon=True
            ).start()
        else:
            threading.Thread(
                target=run_simple_agent_worker,
                args=(agent_id, message, lock, thread_slug, queue, 
                      state['conversation'], ai_client, user_id, thread_slug),
                daemon=True
            ).start()
        
        print(f"[START] ✅ AI worker thread started")
        print(f"{'='*80}\n")
        
        # ============================================
        # STEP 7: RETURN SUCCESS (with conversation)
        # ============================================
        response_data = {
            'session_id': thread_slug,
            'thread_slug': thread_slug,
            'agent_id': agent_id,
            'status': 'processing',
            'conversation': conversation,  # ✅ Return authoritative conversation
            'message': 'Backend loaded conversation from database - use this as source of truth'
        }
        
        print(f"[START] 📤 Returning response with {len(conversation)} messages")
        return success_response(response_data)
    
    except Exception as e:
        import traceback
        print(f"\n{'='*80}")
        print(f"❌ [START ERROR] Unhandled exception")
        print(f"{'='*80}")
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        print(f"{'='*80}\n")
        return error_response(f"Agent start failed: {str(e)}", 500)


# ============================================================
# FIXED: STREAM ENDPOINT (Database as Source of Truth)
# ============================================================

@agent_bp.route('/stream/<agent_id>', methods=['GET'])
def stream_agent(agent_id):
    """
    FIXED: Database as source of truth for streaming
    
    Loads conversation from DB instead of trusting frontend state
    """
    thread_slug = request.args.get('thread_slug') or request.args.get('session_id')
    
    if not thread_slug:
        return error_response("Missing thread_slug or session_id", 400)
    
    if not thread_slug.strip():
        return error_response("thread_slug cannot be empty", 400)
    
    print(f"\n{'='*80}")
    print(f"[STREAM] Agent {agent_id} stream started (DATABASE AS SOURCE OF TRUTH)")
    print(f"{'='*80}")
    print(f"[STREAM] Thread Slug: {thread_slug}")
    
    # ============================================
    # LOAD CONVERSATION FROM DATABASE
    # ============================================
    conversation = load_conversation_from_database(thread_slug)
    print(f"[STREAM] Loaded {len(conversation)} messages from database")
    
    if not conversation:
        error_msg = f"No messages found in database for thread {thread_slug}"
        print(f"[STREAM] ❌ ERROR: {error_msg}")
        return error_response(error_msg, 400)
    
    # Extract last user message
    last_message = ''
    conversation_without_current = conversation.copy()
    
    for idx in range(len(conversation) - 1, -1, -1):
        msg = conversation[idx]
        if msg.get('role') == 'user':
            content = msg.get('content', '')
            if isinstance(content, str):
                last_message = content
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        last_message = block.get('text', '')
                        break
            
            conversation_without_current = conversation[:idx]
            print(f"[STREAM] Extracted current message, history reduced to {len(conversation_without_current)} messages")
            break
    
    if not last_message:
        return error_response(f"No user message found in conversation", 400)
    
    # Get user_id and preferences
    user_id = g.get('user_id', 1)
    print(f"[STREAM] 👤 User ID: {user_id}")
    
    # ============================================
    # LOAD TOOLS (Dynamic Loading)
    # ============================================
    from tools.registry_v3 import get_registry
    registry = get_registry()
    
    meta_tool_names = [
        'list_available_platforms',
        'list_platform_tools',
        'get_tool_schema',
        'search_tools',
        'get_platform_guide',
        'recommend_tools_for_task',
        'get_workflow_steps',
        'execute_tool'
    ]
    
    all_tools_dict = {t['name']: t for t in registry.get_anthropic_tools()}
    tools = [all_tools_dict[name] for name in meta_tool_names if name in all_tools_dict]
    
    # ============================================
    # USER PREFERENCES INJECTION (Retained)
    # ============================================
    from routes.user_preferences_routes import get_user_preferences
    user_prefs = get_user_preferences(user_id) if user_id else None
    
    print(f"[STREAM] 🔍 RAW USER PREFS: {user_prefs}")
    
    nickname = user_prefs.get('nickname', '') if user_prefs else ''
    auth_platform = user_prefs.get('auth_platform', 'auto') if user_prefs else 'auto'
    communication_style = user_prefs.get('communication_style', 'professional') if user_prefs else 'professional'
    detail_level = user_prefs.get('detail_level', 'standard') if user_prefs else 'standard'
    
    # Get preferred_tools
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
        print(f"[STREAM] 👤 User nickname: {nickname}")
    print(f"[STREAM] 🔐 Auth platform: {auth_platform}")
    print(f"[STREAM] 💬 Communication style: {communication_style}")
    print(f"[STREAM] 📊 Detail level: {detail_level}")
    print(f"[STREAM] 📋 Preferred tools: {preferred_tools}")
    
    # ============================================
    # LOCATION DETECTION AND WEATHER (Retained)
    # ============================================
    from core.ip_location import get_location_dict
    try:
        user_ip = request.remote_addr
        location_dict = get_location_dict(user_ip)
        location_string = location_dict.get('location_string', 'Brisbane, Queensland, Australia')
        
        current_time_str = location_dict.get('current_time', 'Unknown time')
        day_of_week = location_dict.get('day_of_week', 'Unknown')
        season = location_dict.get('season', 'Unknown season')
        
        temp_c = location_dict.get('temperature_c')
        temp_f = location_dict.get('temperature_f')
        weather_condition = location_dict.get('weather_condition', 'Unknown')
        
        from datetime import datetime
        date_str = location_dict.get('date', '2025-11-06')
        try:
            month_name = datetime.strptime(date_str, '%Y-%m-%d').strftime('%B')
        except:
            month_name = 'November'
        
        if temp_c is not None:
            temp_str = f"{temp_c}°C ({temp_f}°F), {weather_condition}"
            time_context = f"{location_string} | {day_of_week}, {current_time_str} | {month_name} ({season}) | {temp_str}"
        else:
            time_context = f"{location_string} | {day_of_week}, {current_time_str} | {month_name} ({season})"
        
        print(f"[STREAM] 📍 Location: {location_string}")
        print(f"[STREAM] 🕐 Local time: {day_of_week}, {current_time_str}")
        print(f"[STREAM] 🌍 Season/Month: {month_name} ({season})")
        if temp_c is not None:
            print(f"[STREAM] 🌡️  Temperature: {temp_c}°C ({temp_f}°F), {weather_condition}")
    except Exception as e:
        from datetime import datetime
        import pytz
        
        location_string = "Brisbane, Queensland, Australia"
        location_dict = {
            'city': 'Brisbane',
            'region': 'Queensland',
            'country': 'AU',
            'timezone': 'Australia/Brisbane'
        }
        
        tz = pytz.timezone('Australia/Brisbane')
        now = datetime.now(tz)
        current_time_str = now.strftime('%Y-%m-%d %I:%M %p %Z')
        day_of_week = now.strftime('%A')
        month_name = now.strftime('%B')
        
        month = now.month
        if month in [12, 1, 2]:
            season = 'Summer'
        elif month in [3, 4, 5]:
            season = 'Autumn'
        elif month in [6, 7, 8]:
            season = 'Winter'
        else:
            season = 'Spring'
        
        time_context = f"{location_string} | {day_of_week}, {current_time_str} | {month_name} ({season})"
        print(f"[STREAM] ⚠️  Location detection failed: {e}, using default")
    
    # ============================================
    # SERVER TOOLS (web_search with location)
    # ============================================
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
    
    tools = tools + server_tools
    print(f"[STREAM] 🔷 Total tools: {len(tools)} ({len(tools) - len(server_tools)} meta + {len(server_tools)} server)")
    
    # ============================================
    # SYSTEM PROMPT WITH ALL INJECTIONS (Retained)
    # ============================================
    from core.unified_ai_client import UnifiedAIClient
    ai_client = current_app.config.get('AI_CLIENT')
    if ai_client:
        system_prompt = ai_client.get_system_prompt('data_agent_chat')
        print(f"[STREAM] 🔍 DEBUG: System prompt after get_system_prompt: {len(system_prompt):,} characters")
        
        # Platform instructions based on auth_platform
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
- Calendar → microsoft_calendar_* (NOT google_calendar_*)"""
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
- Calendar → google_calendar_* (NOT microsoft_calendar_*)"""
        else:
            mandatory_platform = "Auto (Check Connected Platforms)"
            platform_instructions = """
PLATFORM USE: Auto-detect

User has not specified a mandatory platform. Check connected platforms and use 
available tools. Prefer the platform the user is authenticated with."""
        
        # Get AI memories
        ai_memories = []
        if user_prefs and user_prefs.get('ai_memories'):
            try:
                memories_json = user_prefs.get('ai_memories', '[]')
                ai_memories = json.loads(memories_json) if memories_json else []
            except:
                ai_memories = []
        
        # Build user context block
        user_context_block = f"""═══════════════════════════════════════════════════════════════
USER CONTEXT

User: {nickname if nickname else 'User'}
Location: {location_string}
Current Time: {day_of_week}, {current_time_str}
Season: {month_name} ({season})"""
        
        if temp_c is not None:
            user_context_block += f"\nWeather: {temp_c}°C ({temp_f}°F), {weather_condition}"
        
        user_context_block += f"""
{platform_instructions}

Additional Preferences (YOU MUST FOLLOW THESE):
- Communication Style: {communication_style}
- Detail Level: {detail_level}"""
        
        if preferred_tools:
            user_context_block += "\n\nSpecial Instructions (CRITICAL - MUST FOLLOW):"
            for tool_pref in preferred_tools:
                user_context_block += f"\n- {tool_pref}"
        
        if ai_memories:
            user_context_block += "\n\nKey Memories About This User:"
            for memory in ai_memories[:5]:
                user_context_block += f"\n- {memory}"
        
        user_context_block += "\n═══════════════════════════════════════════════════════════════\n"
        
        print(f"[STREAM] 📋 USER CONTEXT BLOCK:")
        print(user_context_block)
        
        system_prompt = system_prompt.replace('{{USER_LOCATION}}', user_context_block)
        
        # ============================================
        # PROMPT INJECTION SYSTEM - SINGLE-USE ONLY (Fixed)
        # ============================================
        # CRITICAL: Prompt library selections should apply ONCE (to this message only)
        # NOT persist across entire thread - that makes them "sticky"
        try:
            from core.prompt_injection_manager import get_prompt_manager
            
            # Get prompt parameters (sent ONLY when user explicitly selects prompts)
            quick_actions_str = request.args.get('quick_actions', '')
            library_prompts_str = request.args.get('library_prompts', '')
            custom_prompt = request.args.get('custom_prompt', None)
            
            if quick_actions_str or library_prompts_str or custom_prompt:
                print(f"[STREAM] 📥 SINGLE-USE Prompt injection (for THIS message only):")
                print(f"  - quick_actions: '{quick_actions_str}'")
                print(f"  - library_prompts: '{library_prompts_str}'")
                print(f"  - custom_prompt: '{custom_prompt[:50] if custom_prompt else None}'")
                print(f"[STREAM] ℹ️  These prompts will NOT persist to next message")
            
            quick_actions = [qa.strip() for qa in quick_actions_str.split(',') if qa.strip()] if quick_actions_str else []
            library_prompts = [lp.strip() for lp in library_prompts_str.split(',') if lp.strip()] if library_prompts_str else []
            
            if quick_actions or library_prompts or custom_prompt:
                prompt_manager = get_prompt_manager()
                
                # Inject AFTER base system prompt (appended context, not embedded)
                # This makes the injection clearly temporary and message-specific
                system_prompt = prompt_manager.inject_prompts(
                    base_prompt=system_prompt,
                    quick_actions=quick_actions,
                    library_prompts=library_prompts,
                    custom_prompt=custom_prompt,
                    user_id=user_id
                )
                
                print(f"[STREAM] ⚡ SINGLE-USE prompt injections applied (THIS MESSAGE ONLY)")
                print(f"[STREAM] 🔍 DEBUG: System prompt after injection: {len(system_prompt):,} characters")
        except Exception as e:
            print(f"[STREAM] ⚠️  Error applying prompt injections: {e}")
    else:
        system_prompt = """You are an AI assistant with access to 604 tools across 20+ platforms."""
        print(f"[STREAM] 🔍 DEBUG: System prompt (fallback): {len(system_prompt):,} characters")
    
    # ============================================
    # COMPREHENSIVE CONTEXT INJECTION (Retained)
    # ============================================
    conn = None
    try:
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                synergy_card_id,
                workflow_slug, workflow_title,
                automation_slug, automation_title,
                internal_doc_slug, internal_doc_title
            FROM sessions.threads 
            WHERE thread_slug = %s
            LIMIT 1
        """, (str(thread_slug),))
        
        thread_row = cursor.fetchone()
        
        if thread_row:
            context_sections = []
            
            # Synergy Session Context
            if thread_row['synergy_card_id']:
                synergy_card_id = thread_row['synergy_card_id']
                
                with get_database_connection('synergy_sessions') as conn2:
                    cursor2 = conn2.cursor()
                    
                    cursor2.execute("""
                        SELECT 
                            title, description, project_name, priority, status,
                            tags, documents, next_steps, notes, due_date
                        FROM synergy_sessions.synergy_sessions 
                        WHERE session_id = %s
                    """, (synergy_card_id,))
                    
                    synergy_row = cursor2.fetchone()
                
                if synergy_row:
                    print(f"[STREAM] 🎯 SYNERGY LINKED → {synergy_card_id} | '{synergy_row['title']}'")
                    
                    synergy_context = f"\n\n{'='*80}\n"
                    synergy_context += "🎯 SYNERGY PROJECT CONTEXT\n"
                    synergy_context += f"{'='*80}\n\n"
                    synergy_context += f"You are working on a Synergy project:\n\n"
                    synergy_context += f"**Project:** {synergy_row['title']}\n"
                    if synergy_row['project_name']:
                        synergy_context += f"**Category:** {synergy_row['project_name']}\n"
                    if synergy_row['description']:
                        synergy_context += f"**Description:** {synergy_row['description']}\n"
                    synergy_context += f"**Priority:** {synergy_row['priority']}\n"
                    synergy_context += f"**Status:** {synergy_row['status']}\n"
                    
                    if synergy_row['notes']:
                        synergy_context += f"\n**Notes:** {synergy_row['notes']}\n"
                    
                    if synergy_row['next_steps']:
                        try:
                            next_steps = json.loads(synergy_row['next_steps']) if isinstance(synergy_row['next_steps'], str) else synergy_row['next_steps']
                            if next_steps and isinstance(next_steps, list):
                                synergy_context += "\n**Next Steps:**\n"
                                for step in next_steps:
                                    if isinstance(step, dict):
                                        icon = "✅" if step.get('completed') else "⏳"
                                        synergy_context += f"- {icon} {step.get('description', 'N/A')}\n"
                        except:
                            pass
                    
                    if synergy_row['due_date']:
                        synergy_context += f"\n**Due Date:** {synergy_row['due_date']}\n"
                    
                    synergy_context += f"\n**Available Tools:**\n"
                    synergy_context += f"- synergy_get_session('{synergy_card_id}') - Get full project details\n"
                    synergy_context += f"- synergy_update_session('{synergy_card_id}', ...) - Update project status, notes, next steps\n"
                    synergy_context += f"- synergy_list_sessions() - List all Synergy projects\n"
                    synergy_context += f"- synergy_create_session(...) - Create new Synergy project\n"
                    synergy_context += f"- synergy_delete_session('{synergy_card_id}') - Archive this project\n"
                    
                    synergy_context += f"\n**What You Can Do:**\n"
                    synergy_context += f"- Help user complete next steps (show progress, mark items done)\n"
                    synergy_context += f"- Update project status when milestones are reached\n"
                    synergy_context += f"- Add notes or insights relevant to the project\n"
                    synergy_context += f"- Suggest action items based on project goals\n"
                    synergy_context += f"- Track project progress and remind about due dates\n"
                    synergy_context += f"- Create related Synergy projects if needed\n"
                    
                    context_sections.append(synergy_context)
            
            # Workflow Automation Context (ENHANCED)
            if thread_row['workflow_slug']:
                workflow_slug = thread_row['workflow_slug']
                workflow_title = thread_row['workflow_title'] or workflow_slug
                
                print(f"[STREAM] ⚙️ WORKFLOW LINKED → {workflow_slug}")
                
                workflow_context = f"\n\n{'='*80}\n"
                workflow_context += "⚙️ WORKFLOW AUTOMATION CONTEXT\n"
                workflow_context += f"{'='*80}\n\n"
                workflow_context += f"This thread is linked to a workflow automation:\n\n"
                workflow_context += f"**Workflow:** {workflow_title}\n"
                workflow_context += f"**Slug:** {workflow_slug}\n"
                
                workflow_context += f"\n**Available Tools:**\n"
                workflow_context += f"- automation_get_workflow_by_slug('{workflow_slug}') - Get workflow details\n"
                workflow_context += f"- automation_execute_workflow('{workflow_slug}', input_data) - Execute workflow\n"
                workflow_context += f"- automation_get_execution_history('{workflow_slug}') - View past runs\n"
                workflow_context += f"- automation_schedule_workflow('{workflow_slug}', cron) - Schedule workflow\n"
                
                workflow_context += f"\n**What You Can Do:**\n"
                workflow_context += f"- Explain what this workflow does to the user\n"
                workflow_context += f"- Offer to execute the workflow if appropriate\n"
                workflow_context += f"- Show execution history when asked\n"
                workflow_context += f"- Help modify workflow parameters\n"
                
                context_sections.append(workflow_context)
            
            # Automation Slug Context (ENHANCED)
            if thread_row['automation_slug']:
                automation_slug = thread_row['automation_slug']
                automation_title = thread_row['automation_title'] or automation_slug
                
                print(f"[STREAM] 🤖 AUTOMATION LINKED → {automation_slug}")
                
                automation_context = f"\n\n{'='*80}\n"
                automation_context += "🤖 VISUAL AUTOMATION CONTEXT\n"
                automation_context += f"{'='*80}\n\n"
                automation_context += f"This thread is linked to a visual automation:\n\n"
                automation_context += f"**Automation:** {automation_title}\n"
                automation_context += f"**Slug:** {automation_slug}\n"
                
                automation_context += f"\n**Available Tools:**\n"
                automation_context += f"- automation_get_workflow_by_slug('{automation_slug}') - Get automation details\n"
                automation_context += f"- automation_execute_workflow('{automation_slug}', input_data) - Execute automation\n"
                automation_context += f"- automation_get_execution_history('{automation_slug}') - View execution history\n"
                automation_context += f"- automation_deactivate_workflow('{automation_slug}') - Deactivate automation\n"
                
                automation_context += f"\n**What You Can Do:**\n"
                automation_context += f"- Explain the automation's trigger and actions\n"
                automation_context += f"- Show when it last ran\n"
                automation_context += f"- Offer to execute it manually for testing\n"
                automation_context += f"- Help configure schedule if needed\n"
                
                context_sections.append(automation_context)
            
            # Internal Documentation Context (ENHANCED)
            if thread_row['internal_doc_slug']:
                doc_slug = thread_row['internal_doc_slug']
                doc_title = thread_row['internal_doc_title'] or doc_slug
                
                print(f"[STREAM] 📄 INTERNAL DOC LINKED → {doc_slug}")
                
                doc_context = f"\n\n{'='*80}\n"
                doc_context += "📄 INTERNAL DOCUMENTATION CONTEXT\n"
                doc_context += f"{'='*80}\n\n"
                doc_context += f"This thread has access to internal documentation:\n\n"
                doc_context += f"**Document:** {doc_title}\n"
                doc_context += f"**Slug:** {doc_slug}\n"
                
                doc_context += f"\n**Available Tools:**\n"
                doc_context += f"- internal_docs_get_by_slug('{doc_slug}') - Get full document content\n"
                doc_context += f"- internal_docs_search('{doc_slug}', query) - Search within document\n"
                
                doc_context += f"\n**What You Can Do:**\n"
                doc_context += f"- Reference information from this document in your responses\n"
                doc_context += f"- Answer questions using document content\n"
                doc_context += f"- Summarize key points when relevant\n"
                doc_context += f"- Quote specific sections if helpful\n"
                
                context_sections.append(doc_context)
            
            # Inject all contexts
            if context_sections:
                for context in context_sections:
                    system_prompt += context
                    system_prompt += f"{'='*80}\n"
                
                print(f"[STREAM] ✅ Context injection: {len(context_sections)} sections")
                print(f"[STREAM] 🔍 DEBUG: System prompt after context injection: {len(system_prompt):,} characters")
    
    except Exception as e:
        print(f"[STREAM] ⚠️ Error injecting context: {e}")
    finally:
        if conn:
            conn.close()
            print(f"[STREAM] 🔒 Context injection connection closed")
    
    # Append system prompt continuation
    system_prompt_continued = """

SERVER TOOLS (Always Available):
- web_search: Real-time web search for current information

3-STEP WORKFLOW (For Client Tools):

🔍 STEP 1: DISCOVER (Call ONCE per task, then MOVE ON!)
- list_available_platforms() → See all platforms
- search_tools("email") → Find tools matching keyword
- recommend_tools_for_task("send email") → Get recommended tools

⚠️  CRITICAL: After calling ANY discovery tool ONCE, immediately proceed to STEP 2 or 3!
⚠️  NEVER call the same discovery tool twice - you already have the results!

📚 STEP 2: LEARN (Get tool parameters)
- get_tool_schema("gmail_send_email") → Returns: {parameters, description, examples}

⚡ STEP 3: EXECUTE (Run the tool)
- execute_tool("gmail_send_email", to="user@example.com", subject="Hello", body="Message")

ANTI-LOOP RULES (MANDATORY):
1. 🛑 Don't call search_tools() with the SAME query 3+ times (pointless repetition)
2. ✅ Progressive refinement IS allowed - try different search terms:
   Example: search_tools("database sql") → search_tools("postgres") → Success!
3. ✅ After finding tools → Immediately call get_tool_schema() or execute_tool()
4. ❌ Repeating IDENTICAL searches wastes time and will be blocked
5. 🔄 If no results, try different keywords - don't repeat the same query

Example of CORRECT workflow (progressive refinement):
Round 1: search_tools("database sql") → 0 results (too specific)
Round 2: search_tools("postgres") → Found postgres_execute_query
Round 3: get_tool_schema("postgres_execute_query") → Got parameters
Round 4: execute_tool("postgres_execute_query", ...)

Example of WRONG workflow (infinite loop - will be blocked):
Round 1: search_tools("email") → Found 24 tools
Round 2: search_tools("email") ← ❌ SAME QUERY (pointless repetition)
Round 3: search_tools("email") ← 🛑 BLOCKED (infinite loop detected)

Use tools in multiple rounds with interleaved thinking."""
    
    print(f"[STREAM] 🔍 DEBUG: System prompt BEFORE final append: {len(system_prompt):,} characters")
    print(f"[STREAM] 🔍 DEBUG: system_prompt_continued size: {len(system_prompt_continued):,} characters")
    system_prompt += system_prompt_continued
    print(f"[STREAM] ✅ System prompt complete: {len(system_prompt):,} characters")
    
    # Extract AI preferences
    ai_model = user_prefs.get('ai_model', 'claude-sonnet-4-5-20250929') if user_prefs else 'claude-sonnet-4-5-20250929'
    ai_temperature = float(user_prefs.get('ai_temperature', 1.0)) if user_prefs else 1.0
    ai_max_tokens = int(user_prefs.get('ai_max_tokens', 16000)) if user_prefs else 16000
    ai_thinking_enabled = bool(user_prefs.get('ai_thinking_enabled', 1)) if user_prefs else True
    ai_thinking_budget = int(user_prefs.get('ai_thinking_budget', 10000)) if user_prefs else 10000
    
    print(f"[STREAM] 🧠 AI Preferences:")
    print(f"  Model: {ai_model}")
    print(f"  Temperature: {ai_temperature}")
    print(f"  Max Tokens: {ai_max_tokens}")
    print(f"  Extended Thinking: {'Enabled' if ai_thinking_enabled else 'Disabled'}")
    print(f"  Thinking Budget: {ai_thinking_budget} tokens")
    
    # ============================================
    # START STREAMING
    # ============================================
    from core.combined_agent_worker import execute_streaming_request
    
    def generate():
        """Generator with flush and close signal to prevent incomplete chunked encoding"""
        def flush_stream():
            """Force flush SSE stream to prevent buffering"""
            try:
                sys.stdout.flush()
            except:
                pass
        
        try:
            yield stream_sse_event('start', {'session_id': thread_slug, 'agent_id': agent_id})
            flush_stream()
            
            for event in execute_streaming_request(
                session_id=thread_slug,
                user_prompt=last_message,
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
                event_type = event.get('type', 'unknown')
                yield stream_sse_event(event_type, event)
                flush_stream()  # Force immediate streaming
                
                # REMOVED (Nov 23, 2025): Auto-save on completion is now IMMEDIATE in combined_agent_worker.py
                # Messages are saved immediately after generation to prevent orphaned tool_use blocks
                # This redundant save-on-complete caused duplicate saves and race conditions
                if event_type == 'complete' and False:  # Disabled - keeping code for reference
                    try:
                        conversation_full = event.get('conversation_history', [])
                        
                        if conversation_full:
                            print(f"[STREAM SAVE] Got {len(conversation_full)} messages from complete event")
                            
                            with get_database_connection('sessions') as conn:
                                cursor = conn.cursor()
                                
                                cursor.execute("""
                                    SELECT id FROM sessions.threads 
                                    WHERE thread_slug = %s
                                """, (thread_slug,))
                                
                                thread_row = cursor.fetchone()
                                if thread_row:
                                    db_thread_id = thread_row[0] if isinstance(thread_row, tuple) else thread_row['id']
                                    
                                    cursor.execute("""
                                        SELECT COUNT(*) FROM sessions.messages 
                                        WHERE thread_id = %s
                                    """, (db_thread_id,))
                                    
                                    count_row = cursor.fetchone()
                                    existing_count = count_row[0] if isinstance(count_row, tuple) else count_row['count']
                                    
                                    messages_to_save = conversation_full[existing_count:]
                                    
                                    if messages_to_save:
                                        print(f"[STREAM SAVE] Saving {len(messages_to_save)} new messages")
                                        
                                        from psycopg2.extras import Json
                                        
                                        for message in messages_to_save:
                                            content = message.get('content', '')
                                            
                                            if isinstance(content, (list, dict)):
                                                content_value = Json(content)
                                            elif isinstance(content, str):
                                                if not content.strip().startswith(('[', '{')):
                                                    content_value = Json([{'type': 'text', 'text': content}])
                                                else:
                                                    try:
                                                        parsed = json.loads(content)
                                                        content_value = Json(parsed)
                                                    except:
                                                        content_value = Json([{'type': 'text', 'text': content}])
                                            else:
                                                content_value = Json([{'type': 'text', 'text': str(content)}])
                                            
                                            model_val = event.get('model', ai_model) if event else ai_model
                                            tokens_val = message.get('tokens_used', None)
                                            tool_calls_data = message.get('tool_calls', [])
                                            tool_calls_val = json.dumps(tool_calls_data) if tool_calls_data else None
                                            
                                            metadata = {}
                                            if message.get('thinking_budget'):
                                                metadata['thinking_budget'] = message.get('thinking_budget')
                                            if message.get('round'):
                                                metadata['round'] = message.get('round')
                                            metadata_val = json.dumps(metadata) if metadata else None
                                            
                                            cursor.execute("""
                                                INSERT INTO sessions.messages 
                                                (thread_id, session_id, role, content, user_id, model, tokens_used, tool_calls, metadata, created_at)
                                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                                            """, (db_thread_id, thread_slug, message['role'], content_value, user_id, model_val, tokens_val, tool_calls_val, metadata_val))
                                        
                                        conn.commit()
                                        print(f"[STREAM SAVE] ✅ Saved {len(messages_to_save)} messages")
                                    
                                    cursor.execute("""
                                        UPDATE sessions.threads 
                                        SET updated_at = CURRENT_TIMESTAMP
                                        WHERE thread_slug = %s
                                    """, (thread_slug,))
                                    
                                    conn.commit()
                    
                    except Exception as save_error:
                        print(f"[STREAM SAVE] ❌ Failed to save: {save_error}")
                        import traceback
                        traceback.print_exc()
                
                if event_type in ['complete', 'error']:
                    break
        
        except Exception as e:
            import traceback
            print(f"[STREAM ERROR] {traceback.format_exc()}")
            yield stream_sse_event('error', {'error': str(e)})
            flush_stream()
        
        finally:
            # CRITICAL: Always send close signal to prevent ERR_INCOMPLETE_CHUNKED_ENCODING
            print(f"[STREAM] Sending close signal for thread {thread_slug}")
            yield "event: close\ndata: {}\n\n"
            flush_stream()
    
    # Add timeout protection and better error handling for SSE streams
    response = Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
        'Connection': 'keep-alive',
        'X-Stream-Timeout': '300'  # 5 minute timeout hint
    })
    
    return response


# ============================================================
# REST OF ENDPOINTS (Unchanged)
# ============================================================

@agent_bp.route('/agent/<agent_id>/status', methods=['GET'])
def get_agent_status(agent_id):
    """Get agent status"""
    session_id = request.args.get('session_id')
    if not session_id:
        return error_response("Missing session_id", 400)
    
    try:
        thread_slug = session_id
        state = agent_state_manager.get_or_create_state(agent_id, thread_slug)
        return success_response({
            'status': state['status'],
            'message_count': len(state['conversation'])
        })
    except Exception as e:
        return error_response(str(e), 500)


@agent_bp.route('/agent/<agent_id>/history', methods=['GET'])
def get_agent_history(agent_id):
    """Get conversation history FROM DATABASE"""
    thread_slug = request.args.get('thread_slug') or request.args.get('session_id')
    if not thread_slug:
        return error_response("Missing thread_slug", 400)
    
    try:
        # Load from database (source of truth)
        conversation = load_conversation_from_database(thread_slug)
        return list_response(conversation)
    except Exception as e:
        return error_response(str(e), 500)


@agent_bp.route('/agent/<agent_id>/clear', methods=['POST'])
def clear_agent_conversation(agent_id):
    """Clear conversation history"""
    try:
        data = request.json
        thread_slug = data.get('thread_slug') or data.get('session_id')
        if not thread_slug:
            return error_response("Missing thread_slug", 400)
        
        agent_state_manager.clear_conversation(agent_id, thread_slug)
        return success_response(message="Conversation cleared")
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================
# LEGACY ENDPOINTS (Retained for backward compatibility)
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
        
        if not session_id:
            import secrets
            from datetime import datetime
            session_id = f"session_{int(datetime.now().timestamp()*1000)}_{secrets.token_urlsafe(8)}"
        
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
        
        if not session_id:
            import secrets
            from datetime import datetime
            session_id = f"session_{int(datetime.now().timestamp()*1000)}_{secrets.token_urlsafe(8)}"
        
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
    """Chat with document endpoint - Synchronous response"""
    try:
        agent_id = request.form.get('agent_id', 'data_agent')
        message = request.form.get('message', '')
        
        files = request.files.getlist('files')
        if not files:
            return error_response("No files uploaded", 400)
        
        try:
            content_blocks = process_file_uploads(files)
        except FileValidationError as e:
            return error_response(str(e), 400)
        
        print(f"[CHAT-WITH-DOCUMENT] Processing {len(files)} files")
        
        user_id = g.get('user_id', 1)
        
        import secrets
        from datetime import datetime
        session_id = f"doc_session_{int(datetime.now().timestamp()*1000)}_{secrets.token_urlsafe(8)}"
        
        ai_client = current_app.config.get('AI_CLIENT')
        if ai_client is None:
            from core.unified_ai_client import initialize_ai_client
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from config import Config
            ai_client = initialize_ai_client(str(Config.DB_CONFIG_PATH))
            current_app.config['AI_CLIENT'] = ai_client
        
        full_content = []
        for block in content_blocks:
            full_content.append(block)
        
        if message:
            full_content.append({'type': 'text', 'text': message})
        else:
            full_content.append({'type': 'text', 'text': 'Analyze these documents and provide key information.'})
        
        messages = [{
            'role': 'user',
            'content': full_content
        }]
        
        system_prompt = """You are a data analysis assistant. You help users understand documents, images, and PDFs by extracting key information, answering questions, and providing insights."""
        
        print(f"[CHAT-WITH-DOCUMENT] Calling Claude API...")
        
        try:
            response = ai_client.client.messages.create(
                model=ai_client.default_model,
                max_tokens=4096,
                system=system_prompt,
                messages=messages
            )
            
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


@agent_bp.route('/chat', methods=['POST'])
def simple_chat():
    """Simple chat endpoint for CLI usage"""
    from flask import request, current_app, jsonify
    from auth.user_auth import UserAuthManager
    import threading
    import secrets
    from datetime import datetime
    from queue import Queue, Empty
    from core.combined_agent_worker import agent_worker
    
    try:
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
        
        if not user_id:
            user_id = 1
            user_email = "gerardo@vetsuccessacademy.com"
            print(f"🔑 Chat request using default user_id={user_id}")
        
        data = request.json or {}
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Missing message'}), 400
        
        print(f"\n{'='*80}")
        print(f"📨 [USER MESSAGE RECEIVED]")
        print(f"{'='*80}")
        print(f"   User ID: {user_id}")
        print(f"   Message: {message[:100]}...")
        print(f"{'='*80}\n")
        
        session_id = f"cli_{int(datetime.now().timestamp()*1000)}_{secrets.token_urlsafe(8)}"
        
        ai_client = current_app.config.get('AI_CLIENT')
        if ai_client is None:
            from core.unified_ai_client import initialize_ai_client
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from config import Config
            ai_client = initialize_ai_client(str(Config.DB_CONFIG_PATH))
            current_app.config['AI_CLIENT'] = ai_client
        
        response_text = None
        tool_calls_list = []
        error_message = None
        response_queue = Queue()
        
        def collect_response():
            nonlocal response_text, tool_calls_list, error_message
            
            try:
                request_start = datetime.now()
                
                result = agent_worker(
                    message=message,
                    session_id=session_id,
                    user_id=user_id,
                    conversation_history=[],
                    ai_client=ai_client,
                    attachments=data.get('attachments')
                )
                
                response_time_ms = int((datetime.now() - request_start).total_seconds() * 1000)
                
                response_text = result.get('response', '')
                tool_calls_list = result.get('tool_calls', [])
                
                try:
                    from thread_manager import ThreadManager
                    
                    thread_id = data.get('thread_id') or session_id
                    thread_mgr = ThreadManager()
                    
                    # CRITICAL FIX: Format user message content as JSON array
                    user_content = json.dumps([{'type': 'text', 'text': message}])
                    
                    thread_mgr.add_message(
                        workspace_slug='default',
                        thread_slug=thread_id,
                        role='user',
                        content=user_content,
                        prompt=message,
                        user_id=user_id,
                        include=True,
                        tool_calls=None,
                        tokens_used=None,
                        response_time_ms=None,
                        metadata={}
                    )
                    
                    estimated_tokens = int(len(response_text) / 4)
                    content_to_save = result.get('content_blocks', response_text)
                    if isinstance(content_to_save, str):
                        content_to_save = [{'type': 'text', 'text': response_text}]
                    
                    # CRITICAL FIX: Convert content to JSON string for database storage
                    content_json = json.dumps(content_to_save) if isinstance(content_to_save, list) else content_to_save
                    
                    thread_mgr.add_message(
                        workspace_slug='default',
                        thread_slug=thread_id,
                        role='assistant',
                        content=content_json,
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
                    
                    print(f"💾 Saved to thread {thread_id}")
                    
                except Exception as save_error:
                    print(f"⚠️ Failed to save messages: {save_error}")
                
                response_queue.put({'success': True})
                
            except Exception as e:
                error_message = str(e)
                response_queue.put({'success': False, 'error': error_message})
        
        worker_thread = threading.Thread(target=collect_response, daemon=True)
        worker_thread.start()
        worker_thread.join(timeout=120)
        
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


@agent_bp.route('/quote', methods=['POST'])
def quote_chat():
    """Quote-specific chat endpoint with InHouse Print context"""
    from flask import request, current_app, jsonify
    from auth.user_auth import UserAuthManager
    import threading
    import secrets
    from datetime import datetime
    from queue import Queue, Empty
    from core.combined_agent_worker import agent_worker
    
    try:
        auth_header = request.headers.get('Authorization', '')
        user_id = None
        
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '').strip()
            try:
                auth_manager = UserAuthManager()
                user_data = auth_manager.verify_token(token)
                if user_data:
                    user_id = user_data.get('user_id')
            except:
                pass
        
        if not user_id:
            user_id = 1
        
        data = request.json or {}
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Missing message'}), 400
        
        session_id = f"quote_{int(datetime.now().timestamp()*1000)}_{secrets.token_urlsafe(8)}"
        
        ai_client = current_app.config.get('AI_CLIENT')
        if ai_client is None:
            from core.unified_ai_client import initialize_ai_client
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from config import Config
            ai_client = initialize_ai_client(str(Config.DB_CONFIG_PATH))
            current_app.config['AI_CLIENT'] = ai_client
        
        response_text = None
        tool_calls_list = []
        error_message = None
        response_queue = Queue()
        
        def collect_response():
            nonlocal response_text, tool_calls_list, error_message
            
            try:
                result = agent_worker(
                    message=message,
                    session_id=session_id,
                    user_id=user_id,
                    conversation_history=[],
                    ai_client=ai_client,
                    context='quote_agent'
                )
                
                response_text = result.get('response', '')
                tool_calls_list = result.get('tool_calls', [])
                
                response_queue.put({'success': True})
                
            except Exception as e:
                error_message = str(e)
                response_queue.put({'success': False, 'error': error_message})
        
        worker_thread = threading.Thread(target=collect_response, daemon=True)
        worker_thread.start()
        worker_thread.join(timeout=120)
        
        try:
            result = response_queue.get(timeout=1)
            if not result.get('success'):
                return jsonify({'error': result.get('error')}), 500
        except Empty:
            return jsonify({'error': 'Request timeout'}), 504
        
        return jsonify({
            'response': response_text,
            'tool_calls': tool_calls_list,
            'session_id': session_id,
            'user_id': user_id,
            'context': 'quote_agent'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@agent_bp.route('/tools', methods=['GET'])
def get_tools():
    """Get complete list of available tools"""
    try:
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
        
        server_tools = [{
            "name": "web_search",
            "description": "Search the web for current information",
            "category": "search",
            "platform": "anthropic",
            "source": "server_tool",
            "type": "web_search_20250305"
        }]
        
        all_tools = registry_tools + server_tools
        
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
                "server_tools": len(server_tools)
            },
            "capabilities": {
                "extended_thinking": True,
                "interleaved_thinking": True,
                "web_search": True,
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
# USER FEEDBACK ENDPOINTS (Retained)
# ============================================================

@agent_bp.route('/user-feedback/submit', methods=['POST'])
def submit_user_feedback():
    """Store user feedback when SEND button clicked"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        instructions = data.get('instructions', '').strip()
        
        if not session_id:
            return jsonify({"success": False, "error": "session_id required"}), 400
        
        if not instructions:
            return jsonify({"success": False, "error": "instructions cannot be empty"}), 400
        
        feedback_key = f"user_feedback_{session_id}"
        _feedback_storage[feedback_key] = {
            'instructions': instructions,
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        
        logger.info(f"[USER FEEDBACK] Stored for session {session_id}")
        
        return jsonify({
            "success": True,
            "data": {
                "received": True,
                "message": "Feedback stored - will inject on next tool call"
            }
        }), 200
        
    except Exception as e:
        logger.error(f"[USER FEEDBACK] Error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@agent_bp.route('/user-feedback/check/<session_id>', methods=['GET'])
def check_user_feedback(session_id):
    """Check if user feedback exists"""
    try:
        feedback_key = f"user_feedback_{session_id}"
        
        if feedback_key in _feedback_storage:
            feedback_data = _feedback_storage.pop(feedback_key)
            instructions = feedback_data.get('instructions', '').strip()
            
            logger.info(f"[USER FEEDBACK] Checked session {session_id}: Found feedback")
            
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
        
        return jsonify({"has_feedback": False, "feedback": ""}), 200
        
    except Exception as e:
        logger.error(f"[USER FEEDBACK] Check error: {e}", exc_info=True)
        return jsonify({"has_feedback": False, "error": str(e)}), 500


@agent_bp.route('/user-feedback/injection-status/<session_id>', methods=['GET'])
def get_feedback_injection_status(session_id):
    """Poll for feedback injection notification"""
    try:
        notification_key = f"feedback_injected_{session_id}"
        
        _cleanup_expired_notifications()
        
        if notification_key in _feedback_injection_notifications:
            notification = _feedback_injection_notifications.pop(notification_key)
            
            logger.info(f"[FEEDBACK NOTIFICATION] Session {session_id}: Notifying UI")
            
            return jsonify({
                "injected": True,
                "feedback": notification.get('feedback', ''),
                "timestamp": notification.get('timestamp'),
                "message": "AI received your feedback!"
            }), 200
        
        return jsonify({"injected": False, "message": "Waiting..."}), 200
        
    except Exception as e:
        logger.error(f"[FEEDBACK NOTIFICATION] Error: {e}", exc_info=True)
        return jsonify({"injected": False, "error": str(e)}), 500


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
# TEST/DEBUG SUPPORT
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("AGENT ROUTES V3 - FIXED: DATABASE AS SOURCE OF TRUTH")
    print("="*80 + "\n")
    
    executor = ToolExecutor()
    print(f"✅ ToolExecutor initialized")
    print(f"   Registry: {len(executor.registry.tools)} tools")
    
    print(f"\n✅ All features retained:")
    print(f"   - User preferences injection")
    print(f"   - Location detection & weather")
    print(f"   - Context injection (Synergy, Workflow, Docs)")
    print(f"   - Prompt injection system")
    print(f"   - Conversation pruning")
    print(f"   - File upload handling")
    print(f"   - Auto-save with metadata")
    print(f"   - Thread isolation")
    print(f"   - Validation & error handling")
    
    print(f"\n✅ NEW: Database as source of truth")
    print(f"   - Frontend sends ONLY current message")
    print(f"   - Backend loads conversation from DB")
    print(f"   - Backend saves user message → processes → saves AI response")
    print(f"   - Backend returns complete authoritative conversation")
    
    print("\n" + "="*80 + "\n")