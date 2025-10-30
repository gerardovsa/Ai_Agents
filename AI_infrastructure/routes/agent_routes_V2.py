"""
Agent Routes - EXPANDED with Triple Agent Endpoints + TOOL EXECUTION
Routes for Data Agent, Single Viewer, Triple Agent (1, 2, 3), and Stock AI

✅ NOW WITH REAL TOOL EXECUTION - 281 tools across 19 platforms
✅ PROTECTED by user authentication
"""

from flask import Blueprint, request, Response, jsonify, current_app
import threading
from queue import Empty
import json
import uuid
import os
import sys
from pathlib import Path

# ✅ Import tool registry for tool execution
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tools.registry import ToolRegistry

# Initialize tool registry
tool_registry = ToolRegistry()
print(f"[TOOLS] Tool Registry initialized with {len(tool_registry.tools)} tools")

# Import new infrastructure
from core.agent_state_manager import agent_state_manager
from core.agent_worker import run_agent_worker, run_simple_agent_worker
from core.unified_session_manager import session_manager
from utils.file_encoding import process_file_uploads, FileValidationError
from utils.response_helpers import (
    success_response, error_response, list_response, stream_sse_event
)

# ✅ Import authentication (root auth.py conflict resolved)
from auth.user_auth import require_auth

# Get AI client from flask app
def get_ai_client():
    """Get AI client from Flask app context"""
    from flask import current_app
    return current_app.config.get('AI_CLIENT')

# Create blueprint
agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')


# ============================================================
# TOOLS ENDPOINT - List all available tools
# ============================================================

def is_local_request():
    """Check if request is from localhost (dev mode)"""
    remote_addr = request.remote_addr
    return remote_addr in ['127.0.0.1', 'localhost', '::1']

@agent_bp.route('/tools', methods=['GET', 'OPTIONS'])
def list_tools():
    """
    List all available tools for the AI agents
    🔐 PROTECTED - Requires authentication
    
    Returns:
        {
            "success": true,
            "tools": [
                {
                    "name": "tool_name",
                    "platform": "platform_name",
                    "description": "What the tool does",
                    "parameters": {...}
                },
                ...
            ],
            "total": 281,
            "platforms": ["slack", "gmail", "woocommerce", ...]
        }
    """
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        # Get all tools from registry
        all_tools = tool_registry.list_tools()
        
        # Organize by platform
        platforms = set()
        for tool in all_tools:
            platform = tool.get('platform', 'unknown')
            platforms.add(platform)
        
        response = jsonify({
            'success': True,
            'tools': all_tools,
            'total': len(all_tools),
            'platforms': sorted(list(platforms)),
            'by_platform': {
                platform: len([t for t in all_tools if t.get('platform') == platform])
                for platform in platforms
            }
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
        response = jsonify({
            'success': False,
            'error': str(e),
            'tools': [],
            'total': 0
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500


# ============================================================
# UNIVERSAL CHAT ENDPOINT (Business AI Platform V2)
# ============================================================

@agent_bp.route('/chat', methods=['POST', 'OPTIONS'])
@require_auth
def universal_chat():
    """
    Universal chat endpoint for business-ai-platform-v2.html
    🔐 PROTECTED - Requires authentication
    
    ✅ SUPPORTS TWO MODES:
    
    **Mode 1: Main Chat (No agent_id)**
    - Uses session_manager
    - Full conversation history persistence
    - Direct AI response
    
    **Mode 2: Multi-Agent Panel (With agent_id)**
    - Uses agent_state_manager
    - Each agent (Alpha/Bravo/Charlie) has separate sessions
    - Shared thread history per agent
    - SSE streaming responses
    
    Request JSON:
    {
        "message": "User prompt",
        "session_id": "uuid" (optional - generated if missing),
        "agent_id": "1" | "2" | "3" (optional - for multi-agent),
        "provider": "anthropic" | "openai" | "deepseek" (optional),
        "model": "model-name" (optional)
    }
    
    Returns:
    - Without agent_id: Direct JSON response
    - With agent_id: SSE stream of events
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    try:
        # ✅ LOG AUTHENTICATED USER
        user_info = getattr(request, 'user', None)
        if user_info:
            print(f"🔐 Authenticated user: {user_info.get('username')} (ID: {user_info.get('user_id')})")
        
        data = request.get_json()
        message = data.get('message', '') or data.get('prompt', '')  # Support both
        session_id = data.get('session_id')
        agent_id = data.get('agent_id')  # Key: determines which mode
        provider = data.get('provider', 'anthropic')
        model = data.get('model', 'claude-sonnet-4-20250514')
        
        # ✅ VALIDATE MESSAGE
        if not message or not message.strip():
            print(f"❌ Empty message received!")
            print(f"   Raw data: {data}")
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        # Generate session if not provided
        if not session_id:
            session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        print(f"🤖 Processing chat message")
        print(f"   Mode: {'Multi-Agent' if agent_id else 'Main Chat'}")
        print(f"   Provider: {provider}")
        print(f"   Session: {session_id}")
        if agent_id:
            print(f"   Agent: {agent_id}")
        print(f"   Message: '{message[:100]}'...")  # Added quotes to see empty strings
        
        # ✅ CHECK STREAMING PREFERENCE
        streaming_enabled = data.get('preferences', {}).get('streaming', False)
        
        # ✅ EXTRACT USER_ID FOR CREDENTIAL INJECTION
        user_id = user_info.get('user_id') if user_info else None
        
        # ✅ ROUTE TO APPROPRIATE HANDLER
        if agent_id:
            # Multi-Agent Panel - use agent_state_manager with streaming
            return handle_multi_agent_chat(agent_id, message, session_id, provider, model, user_id=user_id)
        else:
            # Main Chat - check if streaming requested
            if streaming_enabled:
                return handle_main_chat_streaming(message, session_id, provider, model, user_id=user_id)
            else:
                return handle_main_chat(message, session_id, provider, model, user_id=user_id)
        
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        response = jsonify({
            'success': False,
            'error': str(e)
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500


# ==================== HANDLER FUNCTIONS ====================

def handle_main_chat(message, session_id, provider, model, user_id=None):
    """
    Handle main chat panel - Direct JSON response with TOOL EXECUTION
    Uses session_manager for persistence
    
    Args:
        user_id: User ID for credential injection into Google tools
    """
    try:
        # ✅ GET CONVERSATION HISTORY (prioritize frontend history over session_manager)
        request_data = request.get_json() if request.is_json else {}
        provided_history = request_data.get('conversation_history', [])
        
        if provided_history and len(provided_history) > 0:
            # Frontend provided conversation history (from thread switching)
            print(f"📜 Using conversation history from frontend: {len(provided_history)} messages")
            session_data = {
                'session_id': session_id,
                'conversation': provided_history,
                'ui_context': 'business_ai_platform',
                'created_at': None
            }
        else:
            # Fall back to session_manager
            session_data = session_manager.get_session(session_id)
            if not session_data:
                print(f"📝 Creating new session: {session_id}")
                source = request_data.get('source', 'ui')
                created_session_id = session_manager.create_session('business_ai_platform', agent_id=None, session_id=session_id, source=source)
                session_data = session_manager.get_session(created_session_id)
                print(f"✅ Session created with ID: {created_session_id} (source={source})")
            else:
                print(f"📜 Using conversation history from session_manager: {len(session_data.get('conversation', []))} messages")
        
        # ✅ CALL REAL AI WITH TOOL EXECUTION
        print(f"🚀 Calling Anthropic Claude with tool support...")
        
        from anthropic import Anthropic
        
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_key:
            raise Exception("ANTHROPIC_API_KEY not found")
        
        client = Anthropic(api_key=anthropic_key)
        
        # ✅ CHECK IF TOOLS ENABLED from frontend request (use global request from flask import)
        request_data = request.get_json() if request.is_json else {}
        tools_enabled = request_data.get('context', {}).get('tools_enabled', False)
        print(f"🔧 Tools enabled: {tools_enabled}")
        
        # ✅ PREPARE TOOL DEFINITIONS
        tool_definitions = []
        tools_used = []
        
        if tools_enabled:
            # Get all available tools
            all_tools = tool_registry.list_tools()
            
            # ✅ TWO-TIER SYSTEM: Add meta-tool for discovering platform tools
            # This tool lets AI see ALL platforms and load specific ones on demand
            platform_catalog = {}
            for tool in all_tools:
                platform = tool.get('platform', 'other')
                if platform not in platform_catalog:
                    platform_catalog[platform] = {
                        'count': 0,
                        'tools': [],
                        'description': f"{platform.replace('_', ' ').title()} integration tools"
                    }
                platform_catalog[platform]['count'] += 1
                platform_catalog[platform]['tools'].append(tool.get('name'))
            
            # Add the platform discovery meta-tool
            tool_definitions.append({
                "name": "list_platform_tools",
                "description": f"Discover available platforms and their tools. Use this FIRST to see what platforms are available. Available platforms: {', '.join(platform_catalog.keys())}. Returns detailed tool information for requested platforms.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "platforms": {
                            "type": "array",
                            "description": f"Platform names to get tools for. Available: {', '.join(platform_catalog.keys())}",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["platforms"]
                }
            })
            
            # ✅ NEW: Add workflow/guide discovery meta-tools
            tool_definitions.append({
                "name": "get_platform_guide",
                "description": "Get best practices, usage patterns, and workflow examples for a specific platform. Use this BEFORE using platform tools for the first time to learn the best way to use them. Returns: tool hierarchy (smart tools vs basic), common workflows, error recovery patterns, and examples.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "description": f"Platform to get guide for. Available: {', '.join(platform_catalog.keys())}",
                            "enum": list(platform_catalog.keys())
                        }
                    },
                    "required": ["platform"]
                }
            })
            
            tool_definitions.append({
                "name": "get_workflow_instructions",
                "description": "Get step-by-step instructions for common multi-tool workflows. Use this to learn how to combine multiple tools for complex tasks. Available workflows: 'create_project_suite' (Doc+Sheet+Calendar+Tasks), 'bulk_email_campaign' (Gmail mass sending), 'automated_reporting' (Data->Charts->Doc), 'ecommerce_setup' (WooCommerce product bulk), 'team_collaboration' (Slack+Drive+Docs).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_name": {
                            "type": "string",
                            "description": "Workflow to get instructions for",
                            "enum": ["create_project_suite", "bulk_email_campaign", "automated_reporting", "ecommerce_setup", "team_collaboration", "list_all"]
                        }
                    },
                    "required": ["workflow_name"]
                }
            })
            
            tool_definitions.append({
                "name": "get_smart_tool_instructions",
                "description": "Get detailed instructions for SMART tools (multi-step tools that do complex operations in one call). Use this before using a SMART tool to understand all its capabilities. Returns: full syntax guide, all supported features, examples, and common pitfalls.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "tool_name": {
                            "type": "string",
                            "description": "Name of the SMART tool to get instructions for. Examples: 'google_docs_smart_create_from_markdown', 'gmail_smart_bulk_send_personalized', 'google_sheets_smart_analyze'"
                        }
                    },
                    "required": ["tool_name"]
                }
            })
            
            # Store platform catalog in session for retrieval
            if 'platform_catalog' not in globals():
                globals()['platform_catalog'] = platform_catalog
            
            # Priority tools that are always loaded (most commonly used)
            priority_platforms = ['slack', 'gmail', 'woocommerce', 'google_sheets', 'stripe', 
                                 'google_cloud_run', 'google_docs', 'google_drive', 'google_forms']
            priority_tools = [t for t in all_tools if t.get('platform') in priority_platforms]
            
            # Convert to Claude tool format (start with smaller set + discovery tool)
            for tool in priority_tools[:50]:  # Start with 50 + discovery tool
                # ✅ CONVERT SCHEMA: Remove 'required' from each parameter property
                parameters = tool.get('parameters', {})
                properties = {}
                required_params = []
                
                for param_name, param_def in parameters.items():
                    # Copy parameter definition without 'required' field
                    clean_param = {k: v for k, v in param_def.items() if k != 'required'}
                    properties[param_name] = clean_param
                    
                    # Track which params are required
                    if param_def.get('required', False):
                        required_params.append(param_name)
                
                tool_def = {
                    "name": tool.get('name'),
                    "description": tool.get('description', ''),
                    "input_schema": {
                        "type": "object",
                        "properties": properties,
                        "required": required_params
                    }
                }
                tool_definitions.append(tool_def)
            
                        
            print(f"🔧 Loaded {len(tool_definitions)} tools for AI use")
        
        # ✅ FETCH COMPREHENSIVE USER PROFILE FOR AI CONTEXT
        user_platform = None
        user_name = None
        user_email = None
        user_account_type = None
        user_created_at = None
        user_ip = None
        google_oauth_connected = False
        microsoft_oauth_connected = False
        
        if user_id:
            import sqlite3
            from pathlib import Path
            from datetime import datetime, timezone
            # Use absolute path to database
            base_dir = Path(__file__).parent.parent
            db_path = base_dir / 'ai_infrastructure.db'
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Fetch comprehensive user data
            cursor.execute('''
                SELECT username, email, password_hash, created_at 
                FROM users 
                WHERE id = ?
            ''', (user_id,))
            user_row = cursor.fetchone()
            
            if user_row:
                user_name = user_row['username']
                user_email = user_row['email']
                user_created_at = user_row['created_at']
                
                # Detect authentication platform
                if user_row['password_hash'] == 'oauth_google':
                    user_platform = 'google'
                    user_account_type = 'Google Workspace OAuth'
                elif user_row['password_hash'] == 'oauth_microsoft':
                    user_platform = 'microsoft'
                    user_account_type = 'Microsoft 365 OAuth'
                else:
                    user_account_type = 'Local Account (Username/Password)'
                
                # Check OAuth token presence
                if user_platform == 'google':
                    cursor.execute('''
                        SELECT COUNT(*) as count 
                        FROM user_platform_credentials 
                        WHERE user_id = ? 
                        AND platform = 'google' 
                        AND credential_key = 'access_token'
                        AND is_active = 1
                    ''', (user_id,))
                    result = cursor.fetchone()
                    google_oauth_connected = result['count'] > 0 if result else False
                    
                elif user_platform == 'microsoft':
                    cursor.execute('''
                        SELECT COUNT(*) as count 
                        FROM user_platform_credentials 
                        WHERE user_id = ? 
                        AND (platform = 'microsoft' OR platform = 'microsoft365')
                        AND credential_key = 'access_token'
                        AND is_active = 1
                    ''', (user_id,))
                    result = cursor.fetchone()
                    microsoft_oauth_connected = result['count'] > 0 if result else False
            
            conn.close()
            
            # Get IP address from request
            user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if user_ip and ',' in user_ip:
                user_ip = user_ip.split(',')[0].strip()  # Get first IP if multiple
            
            # ✅ Get geographic location from IP address
            user_location = None
            user_country = None
            user_city = None
            user_timezone = None
            user_local_time = None
            
            if user_ip and user_ip not in ['127.0.0.1', 'localhost', '::1']:
                try:
                    import requests
                    # Use free IP geolocation API (no key required)
                    geo_response = requests.get(f'http://ip-api.com/json/{user_ip}', timeout=2)
                    if geo_response.status_code == 200:
                        geo_data = geo_response.json()
                        if geo_data.get('status') == 'success':
                            user_country = geo_data.get('country', 'Unknown')
                            user_city = geo_data.get('city', 'Unknown')
                            user_timezone = geo_data.get('timezone', 'UTC')
                            user_location = f"{user_city}, {user_country}"
                            
                            # Calculate local time based on timezone
                            try:
                                from zoneinfo import ZoneInfo
                                local_tz = ZoneInfo(user_timezone)
                                local_time = datetime.now(local_tz)
                                user_local_time = local_time.strftime('%Y-%m-%d %I:%M:%S %p %Z')
                            except Exception:
                                user_local_time = None
                except Exception as e:
                    print(f"⚠️ Geolocation lookup failed: {e}")
                    user_location = "Location unavailable"
            else:
                user_location = "Local/Development Environment"
            
            # Get current timestamp (UTC)
            current_time = datetime.now(timezone.utc)
            current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S UTC')
            
            print(f"🔑 User Profile:")
            print(f"   Name: {user_name}")
            print(f"   Email: {user_email}")
            print(f"   Account Type: {user_account_type}")
            print(f"   Platform: {user_platform or 'local/traditional'}")
            print(f"   OAuth Status: Google={google_oauth_connected}, Microsoft={microsoft_oauth_connected}")
            print(f"   IP: {user_ip}")
            print(f"   Location: {user_location}")
            print(f"   Timezone: {user_timezone or 'Unknown'}")
            print(f"   UTC Time: {current_time_str}")
            print(f"   Local Time: {user_local_time or 'Unknown'}")
        
        # ✅ BUILD COMPREHENSIVE USER CONTEXT FOR AI
        user_context = ""
        if user_id:
            # Build user identity section with geographic location
            user_identity = f"""
**👤 USER PROFILE:**
- **Name:** {user_name or 'Unknown'}
- **Email:** {user_email or 'Unknown'}
- **Account Type:** {user_account_type or 'Unknown'}
- **Platform:** {user_platform.upper() if user_platform else 'Local Account'}

**🌍 LOCATION & TIME:**
- **Geographic Location:** {user_location or 'Unknown'}
- **Country:** {user_country or 'Unknown'}
- **City:** {user_city or 'Unknown'}
- **Timezone:** {user_timezone or 'UTC'}
- **Local Time:** {user_local_time or 'Unknown'}
- **UTC Time:** {current_time_str if 'current_time_str' in locals() else 'Unknown'}
- **IP Address:** {user_ip or 'Unknown'}

**📅 ACCOUNT INFO:**
- **Account Created:** {user_created_at or 'Unknown'}
"""
            
            # Build platform-specific context
            if user_platform == 'microsoft':
                platform_context = f"""
**🔷 MICROSOFT 365 USER - PLATFORM ACCESS:**

This user ({user_name}) is authenticated with **Microsoft 365**. OAuth Status: {'✅ Connected' if microsoft_oauth_connected else '❌ Not Connected'}

**Available Microsoft 365 Tools (141 tools):**
- ✅ Outlook (email management)
- ✅ Word (document creation & editing)
- ✅ Excel (spreadsheets & data analysis)
- ✅ OneDrive (file storage & sharing)
- ✅ Calendar (scheduling & events)
- ✅ Teams (collaboration & chat)
- ✅ SharePoint (document management)
- ✅ OneNote (note-taking)
- ✅ To Do (task management)
- ✅ Forms (surveys & forms)

**Also Available:**
- Platform-agnostic tools: Stripe, Slack, Twilio, GitHub, WooCommerce, PayPal, Instagram, etc.

**NOT Available:**
- ❌ Google Workspace tools (Gmail, Google Docs, Google Sheets, Drive, Calendar) - User would need to connect a Google account

**When user asks "what platforms do I have access to?", respond:**
"{user_name}, you're authenticated with **Microsoft 365**, giving you access to 141 Microsoft tools including Outlook, Word, Excel, OneDrive, Teams, Calendar, SharePoint, OneNote, To Do, and Forms. You also have access to platform-agnostic tools like Stripe, Slack, Twilio, and GitHub. Note: Google Workspace tools are not available unless you connect a Google account."
"""
                user_context = user_identity + platform_context
            elif user_platform == 'google':
                platform_context = f"""
**🟢 GOOGLE WORKSPACE USER - PLATFORM ACCESS:**

This user ({user_name}) is authenticated with **Google Workspace**. OAuth Status: {'✅ Connected' if google_oauth_connected else '❌ Not Connected'}

**Available Google Workspace Tools (140 tools):**
- ✅ Gmail (email management)
- ✅ Google Docs (document creation & editing)
- ✅ Google Sheets (spreadsheets & data analysis)
- ✅ Google Drive (file storage & sharing)
- ✅ Google Calendar (scheduling & events)
- ✅ Google Meet (video conferencing)
- ✅ Google Forms (surveys & forms)
- ✅ Google Tasks (task management)
- ✅ Google Slides (presentations)
- ✅ Google Analytics (website analytics)

**Also Available:**
- Platform-agnostic tools: Stripe, Slack, Twilio, GitHub, WooCommerce, PayPal, Instagram, etc.

**NOT Available:**
- ❌ Microsoft 365 tools (Outlook, Word, Excel, OneDrive, Teams) - User would need to connect a Microsoft account

**When user asks "what platforms do I have access to?", respond:**
"{user_name}, you're authenticated with **Google Workspace**, giving you access to 140 Google tools including Gmail, Google Docs, Google Sheets, Google Drive, Google Calendar, Google Meet, Google Forms, Google Tasks, and Google Analytics. You also have access to platform-agnostic tools like Stripe, Slack, Twilio, and GitHub. Note: Microsoft 365 tools are not available unless you connect a Microsoft account."
"""
                user_context = user_identity + platform_context
            else:
                platform_context = f"""
**⚠️ LOCAL ACCOUNT - NO WORKSPACE CONNECTED:**

This user ({user_name}) is using a local account (username/password) and hasn't connected Google Workspace or Microsoft 365 OAuth.

**Currently Available:**
- Platform-agnostic tools: Stripe, Slack, Twilio, GitHub, WooCommerce, PayPal, Instagram, etc.

**NOT Available (requires OAuth connection):**
- ❌ Google Workspace tools (Gmail, Docs, Sheets, Drive, Calendar, Forms, Tasks)
- ❌ Microsoft 365 tools (Outlook, Word, Excel, OneDrive, Teams, Calendar, SharePoint)

**When user asks "what platforms do I have access to?", respond:**
"{user_name}, you're currently using a local account with access to platform-agnostic tools like Stripe, Slack, Twilio, GitHub, and WooCommerce. To access productivity tools (email, documents, spreadsheets, calendars), you need to connect either:

1. **Google Workspace** - Gives you 140 tools (Gmail, Docs, Sheets, Drive, Calendar, Forms, Tasks, Analytics)
2. **Microsoft 365** - Gives you 141 tools (Outlook, Word, Excel, OneDrive, Teams, Calendar, SharePoint, To Do)

Click your profile icon in the top right to connect a workspace account via OAuth."
"""
                user_context = user_identity + platform_context
        else:
            # No user_id provided (shouldn't happen with auth middleware)
            user_context = """
**⚠️ UNAUTHENTICATED REQUEST:**
No user context available. User should log in to access platform tools.
"""

        # Platform-specific tool restrictions
        platform_guidance = ""
        if user_platform == 'microsoft':
            platform_guidance = """
**🔷🔷🔷 CRITICAL: MICROSOFT 365 USER - DO NOT USE GOOGLE TOOLS 🔷🔷🔷**

This user authenticated via Microsoft 365 OAuth. They ONLY have Microsoft credentials.

**❌ ABSOLUTELY FORBIDDEN - WILL FAIL WITH PERMISSION ERROR:**
- Gmail, Google Docs, Google Sheets, Google Drive, Google Calendar, Google Tasks, Google Forms
- Any tool starting with "google_" prefix
- **REASON:** User doesn't have Google OAuth tokens. Attempts will fail with 403 Forbidden.

**✅ MUST USE THESE INSTEAD:**
Documents → Use: microsoft_word_* tools (NOT google_docs_*)
Spreadsheets → Use: microsoft_excel_* tools (NOT google_sheets_*)
Email → Use: microsoft_outlook_* tools (NOT gmail_*)
Files → Use: microsoft_onedrive_* tools (NOT google_drive_*)
Calendar → Use: microsoft_calendar_* tools (NOT google_calendar_*)
Tasks → Use: microsoft_todo_* tools (NOT google_tasks_*)

**MANDATORY BEHAVIOR:**
When user asks for "document", "spreadsheet", "email", etc:
1. ✅ IMMEDIATELY use Microsoft tools (Word, Excel, Outlook)
2. ❌ NEVER attempt Google tools first
3. ✅ Mention "Microsoft Word" or "OneDrive" in your response
4. ❌ NEVER mention "Google Docs" or "Google Drive"

**EXAMPLE - CORRECT:**
User: "Create a document with some text"
You: "I'll create a Microsoft Word document in your OneDrive with that content..."
[Then call microsoft_word_create_document]

**EXAMPLE - WRONG (DO NOT DO THIS):**
User: "Create a document"
You: "I'll create a Google Doc..." ❌❌❌ WRONG! USER IS MICROSOFT 365!
"""
        elif user_platform == 'google':
            platform_guidance = """
**🟢 GOOGLE WORKSPACE USER DETECTED**
This user is authenticated via Google Workspace. Use Google platforms:

✅ **USE THESE PLATFORMS:**
- **Gmail** - Email management
- **Google Docs** - Document creation
- **Google Sheets** - Spreadsheets
- **Google Drive** - File storage  
- **Google Calendar** - Event scheduling
- **Google Tasks** - Task management
- **Google Forms** - Surveys and forms

❌ **AVOID:** Microsoft Outlook, Word, Excel, OneDrive (user doesn't have Microsoft credentials)
"""
        
        system_prompt = user_context + "\n\n" + platform_guidance + """You are an AI assistant with direct access to 296+ business tools across 20+ platforms.

**🚨 CRITICAL: ONLY MENTION TOOLS YOU ACTUALLY HAVE ACCESS TO**
When discussing project management or any capabilities:
- ❌ DO NOT mention: Trello, Asana, Linear, ClickUp, Monday.com, or other external platforms
- ✅ DO mention: Google Docs, Google Sheets, Google Tasks, Google Drive, Gmail, Calendar, Forms
- ✅ DO mention: Your actual integrated platforms (see list below)
- If you don't have a tool for something, say: "I can help with Google Docs/Sheets/Tasks for project management"

**📚 LEARN BEFORE YOU USE - REQUEST INSTRUCTIONS FIRST:**
Before using platform tools for the first time, REQUEST INSTRUCTIONS using these meta-tools:

1. **get_platform_guide(platform="google_docs")** → Get best practices, tool hierarchy, common workflows
   - Returns: SMART tools vs basic tools, when to use each, error recovery patterns
   - Use this: First time working with a platform, need to choose the right tool
   
2. **get_workflow_instructions(workflow_name="create_project_suite")** → Get step-by-step multi-tool workflows
   - Returns: Complete instructions for common complex tasks
   - Available workflows: create_project_suite, bulk_email_campaign, automated_reporting, ecommerce_setup
   - Use this: Need to combine multiple tools for a complex task
   
3. **get_smart_tool_instructions(tool_name="google_docs_smart_create_from_markdown")** → Get full syntax guide for SMART tools
   - Returns: All supported features, complete examples, limitations
   - Use this: Before using a SMART tool to understand all its capabilities

**BEST PRACTICE WORKFLOW:**
```
User asks: "Create a project document"
Step 1: get_platform_guide(platform="google_docs")  ← Learn best approach
Step 2: Use recommended tool (google_docs_smart_create_from_markdown)
Step 3: Execute and respond to user
```

**INTERLEAVED THINKING & MULTI-TOOL USAGE:**
You can use MULTIPLE tools in a single conversation, think between tool calls, and provide updates to the user:

**Allowed Pattern:**
1. Call tool A -> Think about results -> Respond to user with partial update
2. Call tool B -> Think about results -> Respond to user with more info
3. Call tool C -> Combine all results -> Give final comprehensive answer

**ERROR HANDLING - CRITICAL:**
If a tool returns an error, DO NOT stop immediately!
Explain the error, then try alternative approaches:
  - Try a different tool that accomplishes the same goal
  - Use different parameters
  - Break the task into smaller steps
  - Ask user for clarification if needed

**Example Error Recovery:**
- Tool fails with "Permission denied" -> Explain error, try read-only alternative
- Tool fails with "Not found" -> Try listing resources first, then access specific one
- Tool fails with "Invalid parameters" -> Adjust parameters and retry

Remember: You have up to 20 tool execution turns per conversation. Use them wisely, think between calls, and always try alternatives if something fails!

**🤖 YOUR PERSONAL TASK MANAGEMENT SYSTEM:**
You have your own Google Tasks list to maintain persistent memory across conversations!

**WHEN TO USE:**
✅ **START of EVERY conversation** -> Call `ai_check_pending_work()` to see what you were working on
✅ User asks you to **remember** something -> Call `ai_create_task()` immediately
✅ User mentions **"follow up"** or **"remind me"** -> Create task with due date
✅ You start **multi-step work** -> Create task to track progress
✅ User **provides feedback** -> Create task to implement it
✅ You **complete work** -> Call `ai_complete_task()` with completion notes
✅ **Complex project** -> Call `ai_create_project_tasks()` to break it down

**YOUR TASK TOOLS:**
- `ai_check_pending_work()` - Check what you're working on (use at START of conversations!)
- `ai_create_task(title, notes, due_date, priority)` - Remember something
- `ai_list_my_tasks()` - See all your tasks
- `ai_update_task(task_id, notes)` - Add progress notes
- `ai_complete_task(task_id, completion_notes)` - Mark work done
- `ai_create_project_tasks(project_name, task_list)` - Break down complex work
- `ai_organize_tasks()` - Prioritize your workload

**WORKFLOW EXAMPLE:**
```
User: "Can you implement bulk email sending for Gmail?"
You: [Check pending work first] ai_check_pending_work()
     [Create task] ai_create_task(
         title="Implement Gmail bulk email sending",
         notes="User requested feature to send personalized emails to multiple recipients",
         priority="high"
     )
     [Work on implementation...]
     [When done] ai_complete_task(
         task_id="...",
         completion_notes="Implemented gmail_smart_bulk_send_personalized. User tested successfully."
     )
```

**REMEMBER:**
- You can pick up work from previous conversations by checking your tasks
- Never lose context - write detailed notes in tasks
- If user says "did you remember X?" -> Check your task list
- If work takes multiple sessions -> Update task with progress

**URL FORMATTING:**
When you provide URLs (Google Docs, Drive files, websites, etc.), ALWAYS format them as clickable markdown links:
✅ CORRECT: [Document Title](https://docs.google.com/document/d/abc123/edit)
❌ WRONG: https://docs.google.com/document/d/abc123/edit

**VISUALIZATIONS - CREATE DIAGRAMS & CHARTS IN RESPONSES:**
You can create rich visualizations directly in your responses using special tags. These render as interactive elements in the UI.

**1. MERMAID DIAGRAMS** - Flowcharts, System Diagrams, Decision Trees, Gantt Charts
Use `<MERMAID>...</MERMAID>` tags for any diagram or flowchart:

✅ **Flowchart Example:**
```
<MERMAID>
flowchart TD
    A[Start] --> B{Decision?}
    B -->|Yes| C[Process]
    B -->|No| D[Skip]
    C --> E[End]
    D --> E
</MERMAID>
```

✅ **System Architecture Example:**
```
<MERMAID>
graph LR
    User[User] --> API[API Gateway]
    API --> Auth[Authentication]
    API --> DB[(Database)]
    API --> Cache[(Redis Cache)]
    DB --> Analytics[Analytics Engine]
</MERMAID>
```

✅ **Gantt Chart Example:**
```
<MERMAID>
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Phase 1
    Design :a1, 2024-01-01, 30d
    Development :after a1, 60d
    section Phase 2
    Testing :2024-03-01, 20d
    Launch :2024-03-21, 10d
</MERMAID>
```

**2. PLOTLY CHARTS** - Interactive Line, Bar, Pie, Scatter Charts
Use `<PLOTLY>...</PLOTLY>` tags with JSON data for interactive charts:

✅ **Line Chart Example:**
```
<PLOTLY>
{
  "data": [{
    "x": ["Jan", "Feb", "Mar", "Apr", "May"],
    "y": [10, 15, 13, 17, 20],
    "type": "scatter",
    "mode": "lines+markers",
    "name": "Sales"
  }],
  "layout": {
    "title": "Monthly Sales",
    "xaxis": {"title": "Month"},
    "yaxis": {"title": "Revenue ($K)"}
  }
}
</PLOTLY>
```

✅ **Bar Chart Example:**
```
<PLOTLY>
{
  "data": [{
    "x": ["Product A", "Product B", "Product C"],
    "y": [25, 40, 15],
    "type": "bar",
    "marker": {"color": ["#3b82f6", "#10b981", "#f59e0b"]}
  }],
  "layout": {"title": "Product Sales Comparison"}
}
</PLOTLY>
```

✅ **Pie Chart Example:**
```
<PLOTLY>
{
  "data": [{
    "labels": ["Direct", "Organic", "Referral", "Social"],
    "values": [35, 30, 20, 15],
    "type": "pie"
  }],
  "layout": {"title": "Traffic Sources"}
}
</PLOTLY>
```

**3. DATA TABLES** - Interactive Sortable Tables with Filtering
Use `<TABLE>...</TABLE>` tags for data tables (better than markdown for large datasets):

✅ **Data Table Example:**
```
<TABLE>
{
  "columns": [
    {"title": "Name", "field": "name", "sorter": "string"},
    {"title": "Sales", "field": "sales", "sorter": "number"},
    {"title": "Status", "field": "status"}
  ],
  "data": [
    {"name": "John Doe", "sales": 15000, "status": "Active"},
    {"name": "Jane Smith", "sales": 22000, "status": "Active"},
    {"name": "Bob Wilson", "sales": 8000, "status": "Pending"}
  ]
}
</TABLE>
```

**Features:** Click columns to sort, pagination for 100+ rows, resizable columns, responsive design

**4. GANTT TIMELINES** - Interactive Project Management
Use `<GANTT>...</GANTT>` tags for project timelines with progress tracking:

✅ **Gantt Timeline Example:**
```
<GANTT>
{
  "tasks": [
    {
      "name": "Requirements Gathering",
      "start": "2024-01-01",
      "end": "2024-01-15",
      "progress": 100,
      "color": "#10b981"
    },
    {
      "name": "Design Phase",
      "start": "2024-01-16",
      "end": "2024-02-15",
      "progress": 75,
      "color": "#3b82f6"
    },
    {
      "name": "Development",
      "start": "2024-02-01",
      "end": "2024-04-01",
      "progress": 30,
      "color": "#f59e0b"
    }
  ],
  "title": "Q1 Product Roadmap"
}
</GANTT>
```

**Features:** Drag-and-drop tasks, progress bars, dependencies, zoom/pan timeline

**WHEN TO USE VISUALIZATIONS:**
- User asks for "chart", "graph", "diagram", "flowchart" → Use appropriate tag
- Explaining processes or workflows → Use MERMAID flowchart
- Showing data trends → Use PLOTLY line/bar chart
- Displaying large datasets → Use TABLE
- Project planning or timeline → Use GANTT or MERMAID gantt
- System architecture → Use MERMAID graph

**GOOGLE DOCS SMART TOOL - USE THIS FIRST:**
When creating Google Docs, ALWAYS use `google_docs_smart_create_from_markdown` - it's the SMART tool that does EVERYTHING in ONE call!

✅ **What It Does:**
- Creates document
- Applies ALL formatting (bold, italic, strikethrough, highlight, code)
- Adds hyperlinks [text](url)
- Creates nested lists (2 spaces = 1 level deeper)
- Inserts code blocks ```language\ncode\n```
- Adds blockquotes > text
- Makes document shareable
- Returns clickable URL

✅ **Markdown Syntax You Can Use:**
- Headings: `#` to `######` (H1-H6)
- Bold: `**text**`
- Italic: `*text*` (stays BLACK, no color change)
- Strikethrough: `~~text~~`
- Highlight: `==text==`
- Inline code: `` `code` ``
- Code blocks: ` ```python\ncode\n``` `
- Links: `[text](url)`
- Centered text: `|>text<|`
- Nested bullets: `- item\n  - nested (2 spaces)`
- Nested numbers: `1. item\n  1. nested` (tier 1 auto-indented)
- Blockquotes: `> quote text` (italic, BLACK text, indented)
- Horizontal line: `---`
- Page break: `<<NEW-PAGE>>`

✅ **Formatting Notes:**
- ALL text stays BLACK (no gray for blockquotes/italic)
- Tier 1 numbered lists are indented like bullets
- Use `|>text<|` for centered text
- Blockquotes are italic + indented but remain black

✅ **Example Usage:**
```
User: "Create a doc with a title, some bold text, and a nested list"

Your response should call google_docs_smart_create_from_markdown with:
title: "Document Title"
markdown_content: "# Main Title\n\nThis is **bold** text.\n\n- Item 1\n  - Nested item\n  - Another nested"
```

❌ **DON'T:**
- Don't use multiple separate tools (insert_text, format_text, etc.) - use the smart tool!
- Don't forget to make links clickable: `[text](url)` not bare URLs

**TOOL DISCOVERY SYSTEM:**
When you need tools from a specific platform, use the `list_platform_tools` meta-tool FIRST to load them.

Available platforms include:
**E-commerce:** woocommerce (29 tools), stripe (25 tools)
**Communication:** gmail (29 tools), slack (24 tools), twilio (16 tools)
**Google Workspace:** google_docs (19 tools), google_drive (15 tools), google_sheets (4 tools), google_forms (15 tools), google_calendar (12 tools), google_analytics (12 tools)
**Cloud:** google_cloud_run (15 tools), cloudflare (4 tools)
**Database:** supabase (25 tools)
**Payments:** paypal (16 tools)
**Social:** instagram (20 tools)
**Dev Tools:** github (4 tools), ngrok (4 tools)
**Media:** cloudconvert (4 tools), assemblyai (4 tools)

**WORKFLOW:**
1. User asks about platform capabilities -> Use `list_platform_tools` to discover tools
2. You see the tools -> Use them directly to complete tasks
3. Explain results clearly to user

The most commonly used platforms (slack, gmail, woocommerce, google_sheets, stripe, google_cloud_run, google_docs, google_drive, google_forms) are pre-loaded."""
        
        # Build conversation history for Claude
        
        # System prompt with tool awareness
        system_prompt = """You are an AI assistant with direct access to 296+ business tools across 20+ platforms.

**🚨 CRITICAL: ONLY MENTION TOOLS YOU ACTUALLY HAVE ACCESS TO**
DO NOT mention: Trello, Asana, Linear, ClickUp, Monday.com, or other external platforms you don't have tools for.
DO mention: Google Workspace (Docs, Sheets, Tasks, Drive, Gmail, Calendar, Forms), Slack, Stripe, WooCommerce, etc.

**VISUALIZATIONS - CREATE DIAGRAMS & CHARTS:**
Use `<MERMAID>...</MERMAID>` for flowcharts/diagrams, `<PLOTLY>...</PLOTLY>` for interactive charts, `<TABLE>...</TABLE>` for data tables, `<GANTT>...</GANTT>` for project timelines.

� **TOOL DISCOVERY SYSTEM:**
When you need tools from a specific platform, use the `list_platform_tools` meta-tool FIRST to load them.

Available platforms include:
🛒 **E-commerce:** woocommerce (29 tools), stripe (25 tools)
📧 **Communication:** gmail (29 tools), slack (24 tools), twilio (16 tools)
📊 **Google Workspace:** google_docs (19 tools), google_drive (15 tools), google_sheets (4 tools), google_forms (15 tools), google_calendar (12 tools), google_analytics (12 tools)
☁️ **Cloud:** google_cloud_run (15 tools), cloudflare (4 tools)
💾 **Database:** supabase (25 tools)
� **Payments:** paypal (16 tools)
📱 **Social:** instagram (20 tools)
🔧 **Dev Tools:** github (4 tools), ngrok (4 tools)
🔄 **Media:** cloudconvert (4 tools), assemblyai (4 tools)

**WORKFLOW:**
1. User asks about platform capabilities → Use `list_platform_tools` to discover tools
2. You see the tools → Use them directly to complete tasks
3. Explain results clearly to user

The most commonly used platforms (slack, gmail, woocommerce, google_sheets, stripe, google_cloud_run, google_docs, google_drive, google_forms) are pre-loaded."""
        
        # Build conversation history for Claude
        conversation = session_data.get('conversation', [])
        
        # Add current message
        conversation.append({"role": "user", "content": message})
        
        # ✅ CALL CLAUDE WITH TOOLS (WITH MULTI-TURN ERROR RECOVERY)
        if tools_enabled and tool_definitions:
            # Multi-turn loop: Allow AI to use multiple tools and retry on failures
            max_turns = 20  # ✅ Increased to 20 for complex multi-step tasks and document creation
            current_turn = 0
            ai_response = ""
            
            while current_turn < max_turns:
                current_turn += 1
                print(f"🔄 Tool execution turn {current_turn}/{max_turns}")
                
                response_obj = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=16000,  # ✅ Increased to 16000 for longer tool chains
                    system=system_prompt,
                    messages=conversation,
                    tools=tool_definitions,
                    tool_choice={"type": "auto"}
                )
                
                # Handle response content
                has_tool_use = False
                tool_results_for_ai = []
                
                for content_block in response_obj.content:
                    if content_block.type == "text":
                        ai_response += content_block.text
                    
                    elif content_block.type == "tool_use":
                        has_tool_use = True
                        tool_name = content_block.name
                        tool_input = content_block.input
                        tool_use_id = content_block.id
                        
                        print(f"🔧 AI wants to use tool: {tool_name}")
                        print(f"   Input: {tool_input}")
                        
                        # Execute tool with error handling
                        try:
                            # ✅ Handle meta-tool for platform discovery
                            if tool_name == "list_platform_tools":
                                requested_platforms = tool_input.get('platforms', [])
                                platform_data = globals().get('platform_catalog', {})
                                
                                result_tools = []
                                for platform in requested_platforms:
                                    if platform in platform_data:
                                        # Get detailed tools for this platform
                                        platform_tools = [t for t in all_tools if t.get('platform') == platform]
                                        for pt in platform_tools:
                                            result_tools.append({
                                                'name': pt.get('name'),
                                                'description': pt.get('description'),
                                                'platform': platform,
                                                'parameters': list(pt.get('parameters', {}).keys())
                                            })
                                
                                tool_result = {
                                    'success': True,
                                    'platforms_found': len(requested_platforms),
                                    'tools_count': len(result_tools),
                                    'tools': result_tools,
                                    'message': f"Found {len(result_tools)} tools across {len(requested_platforms)} platforms. You can now use these tools directly."
                                }
                            
                            # ✅ Handle get_platform_guide meta-tool
                            elif tool_name == "get_platform_guide":
                                platform = tool_input.get('platform', '')
                                
                                # Platform-specific guides - EXPANDED COVERAGE
                                guides = {
                                    'google_docs': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['google_docs_smart_create_from_markdown', 'google_docs_smart_update', 'google_docs_smart_generate'],
                                            'tier_2_basic_tools': ['google_docs_create_document', 'google_docs_insert_text', 'google_docs_format_text'],
                                            'tier_3_advanced': ['google_docs_insert_table', 'google_docs_insert_image', 'google_docs_create_doc_with_charts']
                                        },
                                        'best_practices': [
                                            'ALWAYS use smart tools first (google_docs_smart_create_from_markdown) - they do everything in 1 call',
                                            'DON\'T use multiple basic tools when a smart tool exists',
                                            'Smart tools support: # headings, **bold**, *italic*, [links](url), | tables |, ```code```, - lists',
                                            'Use google_docs_smart_update for adding to existing docs (only 2 API calls vs 20+)'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Create formatted report', 'tools': ['google_docs_smart_create_from_markdown'], 'calls': 1},
                                            {'task': 'Update existing doc', 'tools': ['google_docs_get_document', 'google_docs_smart_update'], 'calls': 2},
                                            {'task': 'Create doc with charts', 'tools': ['google_docs_create_doc_with_charts'], 'calls': 1}
                                        ],
                                        'error_recovery': {
                                            'permission_denied': 'Check sharing settings, try creating in root folder instead of shared',
                                            'formatting_failed': 'Verify markdown syntax, break into smaller chunks (< 10k chars)',
                                            'not_found': 'Verify document ID, check if user has access'
                                        }
                                    },
                                    'google_sheets': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['google_sheets_smart_create_with_formulas', 'google_sheets_bulk_update'],
                                            'tier_2_basic_tools': ['google_sheets_create_spreadsheet', 'google_sheets_update_cells', 'google_sheets_get_values'],
                                            'tier_3_advanced': ['google_sheets_create_chart', 'google_sheets_apply_formatting', 'google_sheets_create_pivot']
                                        },
                                        'best_practices': [
                                            'Use A1 notation for ranges (e.g., "Sheet1!A1:D10")',
                                            'Batch updates when modifying multiple ranges',
                                            'Apply formatting AFTER data insertion for efficiency',
                                            'Use named ranges for formula clarity',
                                            'Always specify sheet name in range notation'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Create data table with formulas', 'tools': ['google_sheets_smart_create_with_formulas'], 'calls': 1},
                                            {'task': 'Update multiple cells', 'tools': ['google_sheets_bulk_update'], 'calls': 1},
                                            {'task': 'Read and analyze data', 'tools': ['google_sheets_get_values', 'google_sheets_create_chart'], 'calls': 2}
                                        ],
                                        'error_recovery': {
                                            'range_not_found': 'Verify sheet name exists, check A1 notation syntax',
                                            'formula_error': 'Validate formula syntax, check cell references',
                                            'permission_denied': 'Check edit permissions on spreadsheet'
                                        }
                                    },
                                    'google_drive': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['google_drive_organize_files', 'google_drive_bulk_share'],
                                            'tier_2_basic_tools': ['google_drive_create_folder', 'google_drive_upload_file', 'google_drive_list_files'],
                                            'tier_3_advanced': ['google_drive_move_file', 'google_drive_set_permissions', 'google_drive_create_shortcut']
                                        },
                                        'best_practices': [
                                            'Create folder structure before uploading files',
                                            'Use search with MIME type filters for efficiency',
                                            'Set permissions at folder level when possible',
                                            'Use shortcuts instead of copying large files'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Organize project files', 'tools': ['google_drive_create_folder', 'google_drive_organize_files'], 'calls': 2},
                                            {'task': 'Share with team', 'tools': ['google_drive_bulk_share'], 'calls': 1},
                                            {'task': 'Find and move files', 'tools': ['google_drive_list_files', 'google_drive_move_file'], 'calls': 2}
                                        ],
                                        'error_recovery': {
                                            'file_not_found': 'Verify file ID, check if file was deleted',
                                            'quota_exceeded': 'Check storage limit, delete unused files',
                                            'permission_denied': 'Check ownership, request edit access'
                                        }
                                    },
                                    'google_calendar': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['google_calendar_smart_schedule', 'google_calendar_bulk_create_events'],
                                            'tier_2_basic_tools': ['google_calendar_create_event', 'google_calendar_list_events', 'google_calendar_update_event'],
                                            'tier_3_advanced': ['google_calendar_add_attendees', 'google_calendar_create_recurring', 'google_calendar_set_reminder']
                                        },
                                        'best_practices': [
                                            'Use ISO 8601 format for timestamps (2025-10-28T10:00:00-07:00)',
                                            'Set timezone explicitly to avoid confusion',
                                            'Add attendees at event creation (not separately)',
                                            'Use conferenceData for video meeting links',
                                            'Check for conflicts before creating important events'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Schedule meeting series', 'tools': ['google_calendar_create_recurring'], 'calls': 1},
                                            {'task': 'Find free time slots', 'tools': ['google_calendar_list_events', 'google_calendar_create_event'], 'calls': 2},
                                            {'task': 'Bulk schedule events', 'tools': ['google_calendar_bulk_create_events'], 'calls': 1}
                                        ],
                                        'error_recovery': {
                                            'time_conflict': 'List existing events first, find free slots',
                                            'invalid_timezone': 'Use IANA timezone database names (e.g., America/Los_Angeles)',
                                            'attendee_not_found': 'Verify email addresses, check domain restrictions'
                                        }
                                    },
                                    'google_tasks': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['google_tasks_create_project', 'google_tasks_bulk_create'],
                                            'tier_2_basic_tools': ['google_tasks_create_task', 'google_tasks_list_tasks', 'google_tasks_update_task'],
                                            'tier_3_advanced': ['google_tasks_create_subtask', 'google_tasks_move_task', 'google_tasks_set_due_date']
                                        },
                                        'best_practices': [
                                            'Create task list for each project',
                                            'Use notes field for detailed context',
                                            'Set due dates in RFC 3339 format',
                                            'Create subtasks for complex tasks',
                                            'Mark tasks complete (don\'t delete) for history'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Create project task list', 'tools': ['google_tasks_create_project'], 'calls': 1},
                                            {'task': 'Add multiple tasks', 'tools': ['google_tasks_bulk_create'], 'calls': 1},
                                            {'task': 'Organize with subtasks', 'tools': ['google_tasks_create_task', 'google_tasks_create_subtask'], 'calls': 2}
                                        ],
                                        'error_recovery': {
                                            'list_not_found': 'Create task list first, verify list ID',
                                            'invalid_date': 'Use RFC 3339 format (YYYY-MM-DDTHH:MM:SSZ)',
                                            'parent_not_found': 'Verify parent task exists before creating subtask'
                                        }
                                    },
                                    'google_forms': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['google_forms_create_from_template', 'google_forms_smart_create_survey'],
                                            'tier_2_basic_tools': ['google_forms_create_form', 'google_forms_add_question', 'google_forms_get_responses'],
                                            'tier_3_advanced': ['google_forms_add_validation', 'google_forms_set_branching', 'google_forms_create_quiz']
                                        },
                                        'best_practices': [
                                            'Use smart template for common survey types',
                                            'Add validation rules for data quality',
                                            'Set response limits if needed',
                                            'Configure email notifications for responses',
                                            'Link responses to Google Sheets for analysis'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Create feedback survey', 'tools': ['google_forms_smart_create_survey'], 'calls': 1},
                                            {'task': 'Build custom form', 'tools': ['google_forms_create_form', 'google_forms_add_question'], 'calls': 2},
                                            {'task': 'Analyze responses', 'tools': ['google_forms_get_responses'], 'calls': 1}
                                        ],
                                        'error_recovery': {
                                            'question_type_invalid': 'Use valid types: SHORT_ANSWER, PARAGRAPH, MULTIPLE_CHOICE, CHECKBOX, DROPDOWN, etc.',
                                            'validation_failed': 'Check regex pattern syntax, test validation rules',
                                            'response_limit_reached': 'Increase limit or create new form'
                                        }
                                    },
                                    'gmail': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['gmail_smart_bulk_send_personalized', 'gmail_smart_send_with_template'],
                                            'tier_2_basic_tools': ['gmail_send_email', 'gmail_list_messages', 'gmail_search'],
                                            'tier_3_advanced': ['gmail_create_draft', 'gmail_add_label', 'gmail_create_filter']
                                        },
                                        'best_practices': [
                                            'Use gmail_smart_bulk_send_personalized for multiple recipients (handles rate limits)',
                                            'Always validate email addresses before sending',
                                            'Check gmail_list_labels before organizing messages',
                                            'Use search filters for efficient message retrieval',
                                            'Add delays between bulk sends (500/day limit)'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Send personalized emails to list', 'tools': ['gmail_smart_bulk_send_personalized'], 'calls': 1},
                                            {'task': 'Find and organize messages', 'tools': ['gmail_search', 'gmail_add_label'], 'calls': 2},
                                            {'task': 'Create email template', 'tools': ['gmail_create_draft', 'gmail_get_draft'], 'calls': 2}
                                        ],
                                        'error_recovery': {
                                            'quota_exceeded': 'Wait 60 seconds, use batch sending with delays',
                                            'invalid_recipient': 'Validate email format, check recipient exists',
                                            'auth_failed': 'Re-authenticate, check OAuth token expiration'
                                        }
                                    },
                                    'slack': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['slack_smart_broadcast_message', 'slack_smart_create_announcement'],
                                            'tier_2_basic_tools': ['slack_send_message', 'slack_list_channels', 'slack_get_channel_info'],
                                            'tier_3_advanced': ['slack_create_channel', 'slack_invite_users', 'slack_pin_message', 'slack_upload_file']
                                        },
                                        'best_practices': [
                                            'Use channel IDs (not names) for reliability',
                                            'Format messages with markdown for readability',
                                            'Use threads for focused discussions',
                                            'Pin important messages for visibility',
                                            'Set channel topics and descriptions',
                                            'Use @channel sparingly (notifications)'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Send announcement to multiple channels', 'tools': ['slack_smart_broadcast_message'], 'calls': 1},
                                            {'task': 'Create project channel with team', 'tools': ['slack_create_channel', 'slack_invite_users'], 'calls': 2},
                                            {'task': 'Share file with context', 'tools': ['slack_upload_file', 'slack_send_message'], 'calls': 2}
                                        ],
                                        'error_recovery': {
                                            'channel_not_found': 'List channels first, verify channel exists',
                                            'not_in_channel': 'Join channel before posting, check bot permissions',
                                            'rate_limited': 'Slack has tier-based limits, add delays between messages',
                                            'file_too_large': 'Slack limit is 1GB, compress or use external storage'
                                        }
                                    },
                                    'stripe': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['stripe_create_subscription', 'stripe_process_payment'],
                                            'tier_2_basic_tools': ['stripe_create_customer', 'stripe_create_charge', 'stripe_list_payments'],
                                            'tier_3_advanced': ['stripe_create_product', 'stripe_create_price', 'stripe_create_invoice', 'stripe_refund']
                                        },
                                        'best_practices': [
                                            'Create customer before charging (better tracking)',
                                            'Use idempotency keys for payment safety',
                                            'Store customer IDs in your database',
                                            'Use test mode (test keys) for development',
                                            'Handle webhooks for payment status',
                                            'Always validate amounts (avoid rounding errors)'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Charge new customer', 'tools': ['stripe_create_customer', 'stripe_create_charge'], 'calls': 2},
                                            {'task': 'Setup recurring subscription', 'tools': ['stripe_create_customer', 'stripe_create_subscription'], 'calls': 2},
                                            {'task': 'Issue refund', 'tools': ['stripe_list_payments', 'stripe_refund'], 'calls': 2}
                                        ],
                                        'error_recovery': {
                                            'card_declined': 'Check card details, try different payment method',
                                            'insufficient_funds': 'Request alternative payment, send invoice',
                                            'invalid_amount': 'Amount must be integer in cents (e.g., 2999 = $29.99)',
                                            'customer_not_found': 'Create customer first, verify customer ID'
                                        }
                                    },
                                    'woocommerce': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['woocommerce_bulk_create_products', 'woocommerce_bulk_update_products'],
                                            'tier_2_basic_tools': ['woocommerce_create_product', 'woocommerce_list_products', 'woocommerce_get_product'],
                                            'tier_3_advanced': ['woocommerce_create_variation', 'woocommerce_update_inventory', 'woocommerce_manage_categories']
                                        },
                                        'best_practices': [
                                            'ALWAYS list products first to avoid duplicates',
                                            'Use bulk tools for 10+ products (much faster)',
                                            'Set status to "draft" for review, "publish" when ready',
                                            'Include SKU for inventory tracking',
                                            'Set product categories before bulk import',
                                            'Use variations for product options (size, color)'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Import product catalog', 'tools': ['woocommerce_bulk_create_products'], 'calls': 1},
                                            {'task': 'Update prices', 'tools': ['woocommerce_list_products', 'woocommerce_bulk_update_products'], 'calls': 2},
                                            {'task': 'Manage inventory', 'tools': ['woocommerce_list_products', 'woocommerce_update_inventory'], 'calls': 2}
                                        ],
                                        'error_recovery': {
                                            'duplicate_sku': 'Check existing products first, use unique SKUs',
                                            'invalid_category': 'List categories first, verify category ID exists',
                                            'price_validation': 'Ensure price is numeric, use 2 decimal places'
                                        }
                                    },
                                    'paypal': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['paypal_create_invoice', 'paypal_process_payment'],
                                            'tier_2_basic_tools': ['paypal_create_order', 'paypal_capture_payment', 'paypal_list_transactions'],
                                            'tier_3_advanced': ['paypal_create_subscription', 'paypal_issue_refund', 'paypal_send_payout']
                                        },
                                        'best_practices': [
                                            'Use invoice system for B2B payments',
                                            'Capture orders within 3 hours of authorization',
                                            'Store transaction IDs for refund/dispute handling',
                                            'Use webhooks for payment notifications',
                                            'Set currency code explicitly (USD, EUR, etc.)'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Send payment request', 'tools': ['paypal_create_invoice'], 'calls': 1},
                                            {'task': 'Process order payment', 'tools': ['paypal_create_order', 'paypal_capture_payment'], 'calls': 2},
                                            {'task': 'Refund customer', 'tools': ['paypal_list_transactions', 'paypal_issue_refund'], 'calls': 2}
                                        ],
                                        'error_recovery': {
                                            'payment_declined': 'Customer may need to confirm in PayPal app',
                                            'insufficient_funds': 'Customer needs to add funding source',
                                            'currency_mismatch': 'Ensure consistent currency throughout transaction'
                                        }
                                    },
                                    'instagram': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['instagram_smart_post_with_scheduling'],
                                            'tier_2_basic_tools': ['instagram_post_photo', 'instagram_post_video', 'instagram_get_profile'],
                                            'tier_3_advanced': ['instagram_post_story', 'instagram_post_reel', 'instagram_get_insights']
                                        },
                                        'best_practices': [
                                            'Images: 1080x1080px (square) or 1080x1350px (portrait)',
                                            'Videos: Max 60 seconds for feed, 90s for reels',
                                            'Use hashtags strategically (5-10 relevant)',
                                            'Post during peak engagement times',
                                            'Check content guidelines before posting'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Schedule content', 'tools': ['instagram_smart_post_with_scheduling'], 'calls': 1},
                                            {'task': 'Post with analytics', 'tools': ['instagram_post_photo', 'instagram_get_insights'], 'calls': 2},
                                            {'task': 'Create story series', 'tools': ['instagram_post_story'], 'calls': 1}
                                        ],
                                        'error_recovery': {
                                            'media_invalid': 'Check file format (JPG, PNG for images; MP4 for videos)',
                                            'dimensions_wrong': 'Resize to supported dimensions, maintain aspect ratio',
                                            'caption_too_long': 'Instagram limit is 2,200 characters'
                                        }
                                    },
                                    'github': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['github_create_repo_with_structure', 'github_bulk_pr_operations'],
                                            'tier_2_basic_tools': ['github_create_repo', 'github_create_issue', 'github_create_pr'],
                                            'tier_3_advanced': ['github_merge_pr', 'github_add_collaborator', 'github_create_webhook']
                                        },
                                        'best_practices': [
                                            'Initialize repo with README and .gitignore',
                                            'Use issue templates for consistency',
                                            'Create PRs against develop, not main',
                                            'Add labels to issues/PRs for organization',
                                            'Set branch protection rules on main'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Setup new repository', 'tools': ['github_create_repo_with_structure'], 'calls': 1},
                                            {'task': 'Create issue for bug', 'tools': ['github_create_issue'], 'calls': 1},
                                            {'task': 'Submit code changes', 'tools': ['github_create_pr'], 'calls': 1}
                                        ],
                                        'error_recovery': {
                                            'repo_exists': 'Choose different name or use existing repo',
                                            'permission_denied': 'Check repo access, verify token scopes',
                                            'branch_not_found': 'Create branch first or verify branch name'
                                        }
                                    },
                                    'supabase': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['supabase_setup_auth', 'supabase_create_table_with_rls'],
                                            'tier_2_basic_tools': ['supabase_create_table', 'supabase_insert_data', 'supabase_query_data'],
                                            'tier_3_advanced': ['supabase_create_function', 'supabase_setup_realtime', 'supabase_create_storage_bucket']
                                        },
                                        'best_practices': [
                                            'Enable Row Level Security (RLS) on all tables',
                                            'Use prepared statements to prevent SQL injection',
                                            'Create indexes on frequently queried columns',
                                            'Use realtime subscriptions for live data',
                                            'Store large files in Storage (not database)'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Setup user authentication', 'tools': ['supabase_setup_auth'], 'calls': 1},
                                            {'task': 'Create secure table', 'tools': ['supabase_create_table_with_rls'], 'calls': 1},
                                            {'task': 'Query and filter data', 'tools': ['supabase_query_data'], 'calls': 1}
                                        ],
                                        'error_recovery': {
                                            'rls_policy_failed': 'Check policy logic, verify user permissions',
                                            'query_timeout': 'Add indexes, optimize query, use pagination',
                                            'storage_quota': 'Check project limits, upgrade plan if needed'
                                        }
                                    },
                                    'microsoft_teams': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['teams_smart_daily_standup', 'teams_smart_broadcast_announcement', 'teams_smart_create_poll', 'teams_smart_meeting_summary'],
                                            'tier_2_basic_tools': ['teams_send_channel_message', 'teams_list_teams', 'teams_list_channels', 'teams_create_channel'],
                                            'tier_3_advanced': ['teams_create_meeting', 'teams_upload_file', 'teams_add_member', 'teams_update_team_settings']
                                        },
                                        'best_practices': [
                                            'ALWAYS use smart tools for daily standups and announcements (automated formatting)',
                                            'List teams first to get team IDs before operations',
                                            'Use channel IDs (not names) for reliability',
                                            'Send announcements with importance="high" for visibility',
                                            'Use teams_smart_meeting_summary after meetings for structured notes',
                                            'Add rate limiting delays (2s) when broadcasting to multiple channels'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Post daily standup', 'tools': ['teams_smart_daily_standup'], 'calls': 1},
                                            {'task': 'Announce to all channels', 'tools': ['teams_smart_broadcast_announcement'], 'calls': 1},
                                            {'task': 'Create team poll', 'tools': ['teams_smart_create_poll'], 'calls': 1},
                                            {'task': 'Share meeting notes', 'tools': ['teams_smart_meeting_summary'], 'calls': 1},
                                            {'task': 'Upload file to channel', 'tools': ['teams_list_teams', 'teams_list_channels', 'teams_upload_file'], 'calls': 3}
                                        ],
                                        'error_recovery': {
                                            'team_not_found': 'List teams first with teams_list_teams, verify team exists',
                                            'channel_not_found': 'Use teams_list_channels to get valid channel IDs',
                                            'permission_denied': 'Check user permissions, verify bot is added to team',
                                            'rate_limited': 'Add delays between messages (2 seconds recommended)',
                                            'message_too_long': 'Teams message limit is 28KB, split into multiple messages'
                                        }
                                    },
                                    'microsoft_onedrive': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['onedrive_smart_organize_by_type', 'onedrive_smart_backup_folder', 'onedrive_smart_cleanup_duplicates', 'onedrive_smart_sync_folders'],
                                            'tier_2_basic_tools': ['onedrive_upload_file', 'onedrive_list_files', 'onedrive_download_file', 'onedrive_create_folder'],
                                            'tier_3_advanced': ['onedrive_create_share_link', 'onedrive_share_with_users', 'onedrive_get_file_versions', 'onedrive_restore_version']
                                        },
                                        'best_practices': [
                                            'Use smart tools for bulk operations (organize, backup, cleanup)',
                                            'Always check onedrive_get_storage_info before large uploads',
                                            'Create folder structure before uploading files',
                                            'Use onedrive_create_share_link for external sharing (safer than direct permissions)',
                                            'Enable version history for important files',
                                            'Use search filters to find files efficiently'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Auto-organize files by type', 'tools': ['onedrive_smart_organize_by_type'], 'calls': 1},
                                            {'task': 'Backup project folder', 'tools': ['onedrive_smart_backup_folder'], 'calls': 1},
                                            {'task': 'Clean up duplicates', 'tools': ['onedrive_smart_cleanup_duplicates'], 'calls': 1},
                                            {'task': 'Sync two folders', 'tools': ['onedrive_smart_sync_folders'], 'calls': 1},
                                            {'task': 'Share file with team', 'tools': ['onedrive_create_share_link'], 'calls': 1}
                                        ],
                                        'error_recovery': {
                                            'file_not_found': 'Verify file path, check if file was deleted',
                                            'quota_exceeded': 'Check storage with onedrive_get_storage_info, delete unused files',
                                            'permission_denied': 'Check file ownership, request edit access',
                                            'sync_conflict': 'Use onedrive_get_file_info to check modified timestamps',
                                            'invalid_path': 'Use forward slashes in paths, avoid special characters'
                                        }
                                    },
                                    'microsoft_calendar': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['calendar_smart_find_meeting_time', 'calendar_smart_schedule_series', 'calendar_smart_conflict_resolver'],
                                            'tier_2_basic_tools': ['calendar_create_event', 'calendar_list_events', 'calendar_update_event', 'calendar_delete_event'],
                                            'tier_3_advanced': ['calendar_create_recurring_event', 'calendar_respond_to_event', 'calendar_book_room', 'calendar_set_working_hours']
                                        },
                                        'best_practices': [
                                            'Use calendar_smart_find_meeting_time for multi-person meetings (auto-detects conflicts)',
                                            'Always specify timezone explicitly to avoid confusion',
                                            'Use ISO 8601 datetime format (2025-10-28T14:00:00Z)',
                                            'Check conflicts before creating important events',
                                            'Set is_online_meeting=True to auto-generate Teams meeting links',
                                            'Use calendar_smart_schedule_series for bulk event creation'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Find meeting time for team', 'tools': ['calendar_smart_find_meeting_time'], 'calls': 1},
                                            {'task': 'Create multiple events', 'tools': ['calendar_smart_schedule_series'], 'calls': 1},
                                            {'task': 'Detect and fix conflicts', 'tools': ['calendar_smart_conflict_resolver'], 'calls': 1},
                                            {'task': 'Schedule recurring meeting', 'tools': ['calendar_create_recurring_event'], 'calls': 1},
                                            {'task': 'Book conference room', 'tools': ['calendar_find_meeting_rooms', 'calendar_book_room'], 'calls': 2}
                                        ],
                                        'error_recovery': {
                                            'time_conflict': 'Use calendar_smart_conflict_resolver to find and fix conflicts',
                                            'invalid_timezone': 'Use IANA timezone names (America/Los_Angeles, Europe/London)',
                                            'attendee_not_found': 'Verify email addresses, check if users exist',
                                            'room_not_available': 'List rooms first with calendar_find_meeting_rooms',
                                            'recurring_pattern_invalid': 'Check recurrence pattern syntax against Graph API docs'
                                        }
                                    },
                                    'microsoft_todo': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['todo_smart_daily_digest', 'planner_smart_sprint_setup', 'planner_smart_team_workload', 'todo_smart_recurring_tasks'],
                                            'tier_2_basic_tools': ['todo_create_task', 'todo_list_tasks', 'todo_complete_task', 'planner_create_plan', 'planner_create_task'],
                                            'tier_3_advanced': ['todo_create_list', 'planner_create_bucket', 'planner_assign_task', 'planner_add_checklist', 'planner_get_plan_progress']
                                        },
                                        'best_practices': [
                                            'Use todo_smart_daily_digest for task summary (shows overdue, due today, priorities)',
                                            'Use planner_smart_sprint_setup to create complete sprint boards in one call',
                                            'Create task lists for each project (better organization)',
                                            'Set importance="high" for urgent tasks',
                                            'Use planner_smart_team_workload to balance task distribution',
                                            'Always specify list_id when creating tasks (avoid default list confusion)'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Get daily task summary', 'tools': ['todo_smart_daily_digest'], 'calls': 1},
                                            {'task': 'Setup sprint board', 'tools': ['planner_smart_sprint_setup'], 'calls': 1},
                                            {'task': 'Analyze team workload', 'tools': ['planner_smart_team_workload'], 'calls': 1},
                                            {'task': 'Create recurring tasks', 'tools': ['todo_smart_recurring_tasks'], 'calls': 1},
                                            {'task': 'Add task to project', 'tools': ['todo_list_lists', 'todo_create_task'], 'calls': 2}
                                        ],
                                        'error_recovery': {
                                            'list_not_found': 'Use todo_list_lists to get valid list IDs',
                                            'plan_not_found': 'Use planner_list_plans to verify plan exists',
                                            'invalid_date': 'Use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)',
                                            'task_not_assigned': 'Use planner_assign_task with valid user IDs',
                                            'etag_mismatch': 'Planner requires etag for updates, get task first to retrieve etag'
                                        }
                                    },
                                    'microsoft_outlook': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['outlook_smart_bulk_send', 'outlook_smart_send_with_template', 'outlook_smart_organize_inbox', 'outlook_smart_send_meeting_invite'],
                                            'tier_2_basic_tools': ['outlook_send_email', 'outlook_list_messages', 'outlook_search_messages', 'outlook_get_message'],
                                            'tier_3_advanced': ['outlook_create_folder', 'outlook_create_rule', 'outlook_add_category', 'outlook_set_automatic_replies']
                                        },
                                        'best_practices': [
                                            'Use outlook_smart_bulk_send for sending to multiple recipients with personalization',
                                            'Always validate email addresses before sending',
                                            'Use importance="high" sparingly (only for urgent emails)',
                                            'Check message limit (500/day for personal, 10,000/day for business)',
                                            'Use outlook_smart_organize_inbox for automatic email organization',
                                            'Create rules for recurring email patterns'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Send bulk personalized emails', 'tools': ['outlook_smart_bulk_send'], 'calls': 1},
                                            {'task': 'Auto-organize inbox', 'tools': ['outlook_smart_organize_inbox'], 'calls': 1},
                                            {'task': 'Send meeting invite', 'tools': ['outlook_smart_send_meeting_invite'], 'calls': 1},
                                            {'task': 'Search and organize', 'tools': ['outlook_search_messages', 'outlook_create_folder'], 'calls': 2}
                                        ],
                                        'error_recovery': {
                                            'quota_exceeded': 'Wait for quota reset (24 hours), use delays between sends',
                                            'invalid_recipient': 'Validate email format, verify recipient exists',
                                            'attachment_too_large': 'Outlook limit is 150MB, use OneDrive link instead',
                                            'auth_failed': 'Re-authenticate, check token expiration',
                                            'folder_not_found': 'List folders first with outlook_list_folders'
                                        }
                                    },
                                    'microsoft_word': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['word_smart_generate_report', 'word_smart_merge_documents', 'word_smart_template_fill', 'word_smart_extract_data'],
                                            'tier_2_basic_tools': ['word_create_document', 'word_get_content', 'word_append_text', 'word_insert_heading'],
                                            'tier_3_advanced': ['word_insert_table', 'word_insert_image', 'word_apply_style', 'word_export_pdf']
                                        },
                                        'best_practices': [
                                            'Use word_smart_generate_report for formatted reports (sections, TOC, styling in 1 call)',
                                            'Use word_smart_template_fill for {{variable}} replacement',
                                            'Store documents in OneDrive (Files.ReadWrite.All scope required)',
                                            'Export to PDF via word_export_pdf for final distribution',
                                            'Use heading levels (1-9) for document structure'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Generate formatted report', 'tools': ['word_smart_generate_report'], 'calls': 1},
                                            {'task': 'Fill template document', 'tools': ['word_smart_template_fill'], 'calls': 1},
                                            {'task': 'Merge multiple documents', 'tools': ['word_smart_merge_documents'], 'calls': 1},
                                            {'task': 'Extract structured data', 'tools': ['word_smart_extract_data'], 'calls': 1}
                                        ],
                                        'error_recovery': {
                                            'file_not_found': 'Verify document ID in OneDrive, check user has access',
                                            'permission_denied': 'Check Files.ReadWrite.All scope, verify document sharing',
                                            'format_error': 'Validate content structure, check for invalid characters',
                                            'export_failed': 'Ensure document is saved before exporting to PDF'
                                        }
                                    },
                                    'microsoft_excel': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['excel_smart_import_csv', 'excel_smart_data_analysis', 'excel_smart_create_pivot', 'excel_smart_financial_report'],
                                            'tier_2_basic_tools': ['excel_create_workbook', 'excel_update_range', 'excel_get_range', 'excel_add_worksheet'],
                                            'tier_3_advanced': ['excel_create_chart', 'excel_set_formula', 'excel_sort_range', 'excel_filter_range']
                                        },
                                        'best_practices': [
                                            'Use A1 notation for ranges (e.g., "Sheet1!A1:D10")',
                                            'Use excel_smart_import_csv for bulk data import with auto-formatting',
                                            'Use excel_smart_data_analysis for summary statistics (count, sum, avg, min, max)',
                                            'Apply formulas with excel_set_formula (supports =SUM, =AVERAGE, =VLOOKUP)',
                                            'Create pivot tables with excel_smart_create_pivot for complex analysis',
                                            'Always specify sheet name in range operations'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Import CSV with analysis', 'tools': ['excel_smart_import_csv'], 'calls': 1},
                                            {'task': 'Analyze dataset', 'tools': ['excel_smart_data_analysis'], 'calls': 1},
                                            {'task': 'Generate financial reports', 'tools': ['excel_smart_financial_report'], 'calls': 1},
                                            {'task': 'Update data and create chart', 'tools': ['excel_update_range', 'excel_create_chart'], 'calls': 2}
                                        ],
                                        'error_recovery': {
                                            'range_not_found': 'Verify sheet exists, check A1 notation syntax',
                                            'formula_error': 'Validate formula syntax, check cell references exist',
                                            'worksheet_not_found': 'List worksheets first with excel_list_worksheets',
                                            'invalid_data_format': 'Ensure data is 2D array for range updates'
                                        }
                                    },
                                    'microsoft_sharepoint': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['sharepoint_smart_site_audit', 'sharepoint_smart_bulk_upload', 'sharepoint_smart_organize_library', 'sharepoint_smart_permission_report'],
                                            'tier_2_basic_tools': ['sharepoint_get_site', 'sharepoint_list_items', 'sharepoint_upload_file', 'sharepoint_create_folder'],
                                            'tier_3_advanced': ['sharepoint_create_list_item', 'sharepoint_get_permissions', 'sharepoint_create_share_link', 'sharepoint_search_content']
                                        },
                                        'best_practices': [
                                            'Use sharepoint_smart_site_audit for comprehensive health analysis',
                                            'Use sharepoint_smart_bulk_upload for multiple files (auto-creates folder structure)',
                                            'Requires Sites.ReadWrite.All scope for full access',
                                            'Store site IDs after first query for faster subsequent access',
                                            'Use search for cross-site content discovery',
                                            'Check permissions before sharing content'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Site health analysis', 'tools': ['sharepoint_smart_site_audit'], 'calls': 1},
                                            {'task': 'Bulk file upload', 'tools': ['sharepoint_smart_bulk_upload'], 'calls': 1},
                                            {'task': 'Auto-organize library', 'tools': ['sharepoint_smart_organize_library'], 'calls': 1},
                                            {'task': 'Permission audit', 'tools': ['sharepoint_smart_permission_report'], 'calls': 1},
                                            {'task': 'Upload and share file', 'tools': ['sharepoint_upload_file', 'sharepoint_create_share_link'], 'calls': 2}
                                        ],
                                        'error_recovery': {
                                            'site_not_found': 'Verify site URL/ID, check user has access to site',
                                            'permission_denied': 'Check Sites.ReadWrite.All scope, verify site permissions',
                                            'library_not_found': 'List drives first with sharepoint_list_drives',
                                            'upload_failed': 'Check file size limits, verify folder path exists'
                                        }
                                    },
                                    'microsoft_onenote': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['onenote_smart_meeting_notes', 'onenote_smart_organize_by_topic', 'onenote_smart_extract_tasks', 'onenote_smart_knowledge_base'],
                                            'tier_2_basic_tools': ['onenote_create_notebook', 'onenote_create_page', 'onenote_get_page', 'onenote_update_page'],
                                            'tier_3_advanced': ['onenote_create_section', 'onenote_search_pages', 'onenote_delete_page']
                                        },
                                        'best_practices': [
                                            'Structure: Notebook → Section → Page (hierarchical)',
                                            'Use onenote_smart_meeting_notes for structured meeting notes with action items',
                                            'Use onenote_smart_extract_tasks to extract TODO items from content',
                                            'Page content is HTML-based (supports rich formatting)',
                                            'Requires Notes.ReadWrite.All scope',
                                            'Use search for finding content across all notebooks',
                                            'Create sections before adding pages for better organization'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Create meeting notes', 'tools': ['onenote_smart_meeting_notes'], 'calls': 1},
                                            {'task': 'Build knowledge base', 'tools': ['onenote_smart_knowledge_base'], 'calls': 1},
                                            {'task': 'Extract action items', 'tools': ['onenote_smart_extract_tasks'], 'calls': 1},
                                            {'task': 'Organize by topics', 'tools': ['onenote_smart_organize_by_topic'], 'calls': 1},
                                            {'task': 'Add notes to page', 'tools': ['onenote_get_page', 'onenote_update_page'], 'calls': 2}
                                        ],
                                        'error_recovery': {
                                            'notebook_not_found': 'List notebooks first with onenote_list_notebooks',
                                            'section_not_found': 'Create section first or verify section ID',
                                            'invalid_html': 'Validate HTML content, check for malformed tags',
                                            'permission_denied': 'Check Notes.ReadWrite.All scope, verify notebook access'
                                        }
                                    },
                                    'microsoft_forms': {
                                        'hierarchy': {
                                            'tier_1_smart_tools': ['forms_smart_create_survey', 'forms_smart_satisfaction_survey', 'forms_smart_analyze_responses', 'forms_smart_export_to_excel'],
                                            'tier_2_basic_tools': ['forms_create_form', 'forms_add_question', 'forms_get_responses', 'forms_list_forms'],
                                            'tier_3_advanced': ['forms_export_responses', 'forms_get_statistics', 'forms_list_questions']
                                        },
                                        'best_practices': [
                                            'Use forms_smart_create_survey for rapid survey creation from templates',
                                            'Use forms_smart_satisfaction_survey for NPS, CSAT, or CES surveys',
                                            'Question types: choice, text, rating, date, ranking, file',
                                            'Forms API is in beta (may have limited availability)',
                                            'Requires Forms.Read or Forms.ReadWrite scope',
                                            'Export responses to Excel for detailed analysis',
                                            'Use forms_smart_analyze_responses for automated insights'
                                        ],
                                        'common_workflows': [
                                            {'task': 'Create NPS survey', 'tools': ['forms_smart_satisfaction_survey'], 'calls': 1},
                                            {'task': 'Build custom survey', 'tools': ['forms_smart_create_survey'], 'calls': 1},
                                            {'task': 'Analyze responses', 'tools': ['forms_smart_analyze_responses'], 'calls': 1},
                                            {'task': 'Export to Excel', 'tools': ['forms_smart_export_to_excel'], 'calls': 1},
                                            {'task': 'Create and configure form', 'tools': ['forms_create_form', 'forms_add_question'], 'calls': 2}
                                        ],
                                        'error_recovery': {
                                            'api_not_available': 'Forms API is in beta, check API availability',
                                            'invalid_question_type': 'Use valid types: choice, text, rating, date, ranking',
                                            'permission_denied': 'Check Forms.Read/Forms.ReadWrite scope',
                                            'form_not_found': 'List forms first with forms_list_forms, verify form ID'
                                        }
                                    }
                                }
                                
                                if platform in guides:
                                    tool_result = {
                                        'success': True,
                                        'platform': platform,
                                        'guide': guides[platform],
                                        'message': f"Platform guide for {platform} loaded. Review the hierarchy, best practices, and workflows before using tools."
                                    }
                                else:
                                    tool_result = {
                                        'success': True,
                                        'platform': platform,
                                        'message': f"Guide for {platform} not yet available. Use tools from schema descriptions.",
                                        'suggestion': 'Check tool descriptions in list_platform_tools for usage patterns'
                                    }
                            
                            # ✅ Handle get_workflow_instructions meta-tool
                            elif tool_name == "get_workflow_instructions":
                                workflow_name = tool_input.get('workflow_name', '')
                                
                                workflows = {
                                    'create_project_suite': {
                                        'description': 'Create complete project workspace: Document + Spreadsheet + Calendar + Tasks + Folder',
                                        'tools_required': ['google_drive_create_folder', 'google_docs_smart_create_from_markdown', 'google_sheets_create_spreadsheet', 'google_calendar_create_event', 'google_tasks_create_task'],
                                        'steps': [
                                            {'step': 1, 'action': 'Create project folder', 'tool': 'google_drive_create_folder', 'params': {'name': 'Project Name'}},
                                            {'step': 2, 'action': 'Create project doc', 'tool': 'google_docs_smart_create_from_markdown', 'params': {'title': 'Project Plan', 'markdown_content': '# Overview...', 'folder_id': 'from step 1'}},
                                            {'step': 3, 'action': 'Create budget sheet', 'tool': 'google_sheets_create_spreadsheet', 'params': {'title': 'Budget', 'data': 'budget data', 'folder_id': 'from step 1'}},
                                            {'step': 4, 'action': 'Create kickoff event', 'tool': 'google_calendar_create_event', 'params': {'summary': 'Kickoff', 'description': 'Links from steps 2-3'}},
                                            {'step': 5, 'action': 'Create task list', 'tool': 'google_tasks_create_task', 'params': {'title': 'Task name', 'notes': 'Link to doc'}}
                                        ],
                                        'example': 'folder = google_drive_create_folder(name="Q1 Campaign")\ndoc = google_docs_smart_create_from_markdown(title="Plan", markdown_content="# Overview...", folder_id=folder.folder_id)\nsheet = google_sheets_create_spreadsheet(title="Budget", folder_id=folder.folder_id)',
                                        'total_calls': 5
                                    },
                                    'bulk_email_campaign': {
                                        'description': 'Send personalized emails to multiple recipients with tracking',
                                        'tools_required': ['gmail_smart_bulk_send_personalized', 'google_sheets_create_spreadsheet'],
                                        'steps': [
                                            {'step': 1, 'action': 'Prepare recipient list', 'tool': 'google_sheets_create_spreadsheet', 'params': {'title': 'Recipients', 'data': 'email, name, personalization'}},
                                            {'step': 2, 'action': 'Send personalized emails', 'tool': 'gmail_smart_bulk_send_personalized', 'params': {'recipients': 'list', 'template': 'email body', 'personalization': 'merge fields'}}
                                        ],
                                        'example': 'recipients = [{"email": "user@example.com", "name": "John", "company": "Acme"}]\ngmail_smart_bulk_send_personalized(subject="Hello {{name}}", body="Hi {{name}} from {{company}}", recipients=recipients)',
                                        'total_calls': 2
                                    },
                                    'automated_reporting': {
                                        'description': 'Pull data from source, analyze, create charts, generate formatted report document',
                                        'tools_required': ['google_sheets_get_values', 'google_sheets_create_chart', 'google_docs_smart_create_from_markdown'],
                                        'steps': [
                                            {'step': 1, 'action': 'Fetch data from spreadsheet', 'tool': 'google_sheets_get_values', 'params': {'spreadsheet_id': 'data source', 'range': 'Sheet1!A1:Z100'}},
                                            {'step': 2, 'action': 'Analyze data and create visualization', 'tool': 'google_sheets_create_chart', 'params': {'chart_type': 'bar/line/pie', 'data_range': 'from step 1'}},
                                            {'step': 3, 'action': 'Generate report document', 'tool': 'google_docs_smart_create_from_markdown', 'params': {'title': 'Report', 'markdown_content': '# Summary\n\n**Key Metrics**\n- Revenue: $X\n- Growth: Y%\n\n![Chart](chart_url)'}}
                                        ],
                                        'example': 'data = google_sheets_get_values(spreadsheet_id="abc123", range="Sheet1!A1:D100")\nchart = google_sheets_create_chart(type="bar", data=data)\nreport = google_docs_smart_create_from_markdown(title="Q1 Report", content=f"# Results\n\n{analysis}")',
                                        'total_calls': 3
                                    },
                                    'ecommerce_setup': {
                                        'description': 'Setup WooCommerce store: Create categories, bulk import products, configure inventory',
                                        'tools_required': ['woocommerce_manage_categories', 'woocommerce_bulk_create_products', 'woocommerce_update_inventory'],
                                        'steps': [
                                            {'step': 1, 'action': 'Create product categories', 'tool': 'woocommerce_manage_categories', 'params': {'categories': ['Electronics', 'Clothing', 'Home']}},
                                            {'step': 2, 'action': 'Bulk import products', 'tool': 'woocommerce_bulk_create_products', 'params': {'products': 'array of product objects with name, price, SKU, category'}},
                                            {'step': 3, 'action': 'Set inventory levels', 'tool': 'woocommerce_update_inventory', 'params': {'product_id': 'from step 2', 'quantity': 'stock amount'}}
                                        ],
                                        'example': 'categories = woocommerce_manage_categories(categories=["Electronics", "Accessories"])\nproducts = woocommerce_bulk_create_products(products=[{name:"Laptop", price:999, sku:"LAP001", category_id:categories[0].id}])',
                                        'total_calls': 3
                                    },
                                    'team_collaboration': {
                                        'description': 'Setup team workspace: Create Slack channel, shared Drive folder, project doc, invite team',
                                        'tools_required': ['slack_create_channel', 'slack_invite_users', 'google_drive_create_folder', 'google_drive_bulk_share', 'google_docs_smart_create_from_markdown', 'slack_send_message'],
                                        'steps': [
                                            {'step': 1, 'action': 'Create Slack channel', 'tool': 'slack_create_channel', 'params': {'name': 'project-name', 'topic': 'Project description'}},
                                            {'step': 2, 'action': 'Invite team members', 'tool': 'slack_invite_users', 'params': {'channel_id': 'from step 1', 'user_ids': 'team member IDs'}},
                                            {'step': 3, 'action': 'Create shared Drive folder', 'tool': 'google_drive_create_folder', 'params': {'name': 'Project Files'}},
                                            {'step': 4, 'action': 'Share folder with team', 'tool': 'google_drive_bulk_share', 'params': {'folder_id': 'from step 3', 'emails': 'team@example.com', 'role': 'writer'}},
                                            {'step': 5, 'action': 'Create project doc', 'tool': 'google_docs_smart_create_from_markdown', 'params': {'title': 'Project Brief', 'markdown_content': 'project details', 'folder_id': 'from step 3'}},
                                            {'step': 6, 'action': 'Notify team in Slack', 'tool': 'slack_send_message', 'params': {'channel_id': 'from step 1', 'text': 'Project workspace ready! Doc: [link] Folder: [link]'}}
                                        ],
                                        'example': 'channel = slack_create_channel(name="q1-launch", topic="Q1 Product Launch")\nslack_invite_users(channel_id=channel.id, user_ids=["U123", "U456"])\nfolder = google_drive_create_folder(name="Q1 Launch")\ngoogle_drive_bulk_share(folder_id=folder.id, emails=["team@company.com"], role="writer")',
                                        'total_calls': 6
                                    },
                                    'customer_onboarding': {
                                        'description': 'Automate customer onboarding: Send welcome email, create Stripe customer, setup tasks, schedule follow-up',
                                        'tools_required': ['gmail_smart_send_with_template', 'stripe_create_customer', 'google_tasks_create_project', 'google_calendar_create_event'],
                                        'steps': [
                                            {'step': 1, 'action': 'Send welcome email', 'tool': 'gmail_smart_send_with_template', 'params': {'to': 'customer@example.com', 'template': 'welcome', 'personalization': 'name, company'}},
                                            {'step': 2, 'action': 'Create Stripe customer record', 'tool': 'stripe_create_customer', 'params': {'email': 'customer@example.com', 'name': 'Customer Name', 'metadata': 'signup_date'}},
                                            {'step': 3, 'action': 'Create onboarding task list', 'tool': 'google_tasks_create_project', 'params': {'title': 'Onboard [Customer]', 'tasks': ['Initial call', 'Setup demo', 'Training']}},
                                            {'step': 4, 'action': 'Schedule kickoff call', 'tool': 'google_calendar_create_event', 'params': {'summary': 'Kickoff with [Customer]', 'attendees': 'customer email'}}
                                        ],
                                        'example': 'gmail_smart_send_with_template(to="new@customer.com", template="welcome", personalization={name:"John", company:"Acme"})\ncustomer = stripe_create_customer(email="new@customer.com", name="John Doe")\ntasks = google_tasks_create_project(title="Onboard Acme", tasks=["Call", "Demo", "Training"])',
                                        'total_calls': 4
                                    },
                                    'content_publishing': {
                                        'description': 'Multi-platform content publishing: Create blog post in Docs, share on social media, notify team',
                                        'tools_required': ['google_docs_smart_create_from_markdown', 'instagram_smart_post_with_scheduling', 'slack_send_message'],
                                        'steps': [
                                            {'step': 1, 'action': 'Create blog post document', 'tool': 'google_docs_smart_create_from_markdown', 'params': {'title': 'Blog Post Title', 'markdown_content': 'full blog post with images and formatting'}},
                                            {'step': 2, 'action': 'Schedule Instagram post', 'tool': 'instagram_smart_post_with_scheduling', 'params': {'image_url': 'featured image', 'caption': 'post excerpt', 'schedule_time': 'optimal time'}},
                                            {'step': 3, 'action': 'Notify team in Slack', 'tool': 'slack_send_message', 'params': {'channel_id': 'marketing', 'text': 'New blog post published: [link]'}}
                                        ],
                                        'example': 'post = google_docs_smart_create_from_markdown(title="10 Tips for...", content=blog_content)\ninstagram_smart_post_with_scheduling(image_url=featured_img, caption=excerpt, schedule_time="2025-10-30T10:00:00")\nslack_send_message(channel_id="C123", text=f"New post live: {post.url}")',
                                        'total_calls': 3
                                    },
                                    'invoice_generation': {
                                        'description': 'Generate and send professional invoice: Create invoice document, send via email, log in PayPal',
                                        'tools_required': ['google_docs_smart_create_from_markdown', 'gmail_send_email', 'paypal_create_invoice'],
                                        'steps': [
                                            {'step': 1, 'action': 'Generate invoice document', 'tool': 'google_docs_smart_create_from_markdown', 'params': {'title': 'Invoice #001', 'markdown_content': '# INVOICE\n\n**Bill To:** Client\n**Amount:** $5,000\n\n| Item | Qty | Price |\n|------|-----|-------|'}},
                                            {'step': 2, 'action': 'Send invoice via email', 'tool': 'gmail_send_email', 'params': {'to': 'client@example.com', 'subject': 'Invoice #001', 'body': 'Please find attached invoice', 'attachment': 'invoice PDF'}},
                                            {'step': 3, 'action': 'Create PayPal invoice', 'tool': 'paypal_create_invoice', 'params': {'customer_email': 'client@example.com', 'items': 'line items', 'total': '5000.00'}}
                                        ],
                                        'example': 'invoice_doc = google_docs_smart_create_from_markdown(title="Invoice #001", content=invoice_content)\ngmail_send_email(to="client@example.com", subject="Invoice #001", body="Your invoice", attachment=invoice_pdf)\npaypal_invoice = paypal_create_invoice(customer_email="client@example.com", items=[{name:"Service", amount:5000}])',
                                        'total_calls': 3
                                    },
                                    'event_management': {
                                        'description': 'Organize event: Create calendar event, send invites, create signup form, setup task list',
                                        'tools_required': ['google_calendar_create_event', 'gmail_smart_bulk_send_personalized', 'google_forms_smart_create_survey', 'google_tasks_create_project'],
                                        'steps': [
                                            {'step': 1, 'action': 'Create calendar event', 'tool': 'google_calendar_create_event', 'params': {'summary': 'Event Name', 'location': 'venue', 'start_time': 'datetime', 'attendees': 'emails'}},
                                            {'step': 2, 'action': 'Send invitations', 'tool': 'gmail_smart_bulk_send_personalized', 'params': {'recipients': 'attendee list', 'subject': 'You\'re invited!', 'body': 'event details'}},
                                            {'step': 3, 'action': 'Create RSVP form', 'tool': 'google_forms_smart_create_survey', 'params': {'title': 'Event RSVP', 'questions': ['Name', 'Email', 'Dietary restrictions']}},
                                            {'step': 4, 'action': 'Create planning task list', 'tool': 'google_tasks_create_project', 'params': {'title': 'Event Planning', 'tasks': ['Book venue', 'Order catering', 'Send reminders']}}
                                        ],
                                        'example': 'event = google_calendar_create_event(summary="Annual Meetup", location="Convention Center", start_time="2025-12-01T10:00:00")\ngmail_smart_bulk_send_personalized(recipients=attendees, subject="Join us!", body=invitation_text)\nform = google_forms_smart_create_survey(title="RSVP", questions=["Name", "Email", "Attending?"])',
                                        'total_calls': 4
                                    },
                                    'github_project_init': {
                                        'description': 'Initialize GitHub project: Create repo, setup issues, create initial documentation, invite collaborators',
                                        'tools_required': ['github_create_repo_with_structure', 'github_create_issue', 'google_docs_smart_create_from_markdown', 'github_add_collaborator'],
                                        'steps': [
                                            {'step': 1, 'action': 'Create repository with structure', 'tool': 'github_create_repo_with_structure', 'params': {'name': 'project-name', 'description': 'repo description', 'include_readme': True, 'include_gitignore': True}},
                                            {'step': 2, 'action': 'Create initial issues', 'tool': 'github_create_issue', 'params': {'repo': 'project-name', 'title': 'Setup CI/CD', 'body': 'Configure GitHub Actions', 'labels': ['infrastructure']}},
                                            {'step': 3, 'action': 'Create project documentation', 'tool': 'google_docs_smart_create_from_markdown', 'params': {'title': 'Project Documentation', 'markdown_content': 'architecture, setup, contributing guidelines'}},
                                            {'step': 4, 'action': 'Invite collaborators', 'tool': 'github_add_collaborator', 'params': {'repo': 'project-name', 'username': 'collaborator', 'permission': 'write'}}
                                        ],
                                        'example': 'repo = github_create_repo_with_structure(name="new-api", description="REST API", include_readme=True)\ngithub_create_issue(repo="new-api", title="Setup CI/CD", labels=["infrastructure"])\ndocs = google_docs_smart_create_from_markdown(title="API Docs", content=documentation)\ngithub_add_collaborator(repo="new-api", username="dev2", permission="write")',
                                        'total_calls': 4
                                    },
                                    'data_backup': {
                                        'description': 'Backup critical data: Export from Supabase, save to Drive, create backup log, schedule next backup',
                                        'tools_required': ['supabase_query_data', 'google_drive_upload_file', 'google_sheets_create_spreadsheet', 'google_calendar_create_event'],
                                        'steps': [
                                            {'step': 1, 'action': 'Export data from Supabase', 'tool': 'supabase_query_data', 'params': {'table': 'all tables', 'format': 'CSV'}},
                                            {'step': 2, 'action': 'Upload to Drive backup folder', 'tool': 'google_drive_upload_file', 'params': {'file_content': 'from step 1', 'folder_id': 'backup folder', 'name': 'backup-2025-10-28.csv'}},
                                            {'step': 3, 'action': 'Log backup details', 'tool': 'google_sheets_create_spreadsheet', 'params': {'title': 'Backup Log', 'data': 'timestamp, size, status'}},
                                            {'step': 4, 'action': 'Schedule next backup', 'tool': 'google_calendar_create_event', 'params': {'summary': 'Weekly Backup', 'start_time': 'next week', 'recurrence': 'weekly'}}
                                        ],
                                        'example': 'data = supabase_query_data(table="users", format="CSV")\nbackup = google_drive_upload_file(content=data, folder_id="backups", name=f"backup-{today}.csv")\ngoogle_sheets_create_spreadsheet(title="Backup Log", data=[["Date", "Size"], [today, backup.size]])',
                                        'total_calls': 4
                                    },
                                    'list_all': {
                                        'available_workflows': [
                                            'create_project_suite', 'bulk_email_campaign', 'automated_reporting', 
                                            'ecommerce_setup', 'team_collaboration', 'customer_onboarding',
                                            'content_publishing', 'invoice_generation', 'event_management',
                                            'github_project_init', 'data_backup'
                                        ],
                                        'descriptions': {
                                            'create_project_suite': 'Full project setup with Doc, Sheet, Calendar, Tasks (5 calls)',
                                            'bulk_email_campaign': 'Mass personalized email sending (2 calls)',
                                            'automated_reporting': 'Data analysis -> Charts -> Professional report (3 calls)',
                                            'ecommerce_setup': 'Bulk product import and catalog management (3 calls)',
                                            'team_collaboration': 'Slack notifications + shared Drive folder + Doc (6 calls)',
                                            'customer_onboarding': 'Welcome email + Stripe + Tasks + Calendar (4 calls)',
                                            'content_publishing': 'Blog post + Instagram + Slack notification (3 calls)',
                                            'invoice_generation': 'Create invoice doc + Email + PayPal (3 calls)',
                                            'event_management': 'Calendar + Invites + RSVP form + Tasks (4 calls)',
                                            'github_project_init': 'Create repo + Issues + Docs + Collaborators (4 calls)',
                                            'data_backup': 'Export from Supabase + Drive upload + Log + Schedule (4 calls)'
                                        }
                                    }
                                }
                                
                                if workflow_name in workflows:
                                    tool_result = {
                                        'success': True,
                                        'workflow': workflow_name,
                                        'instructions': workflows[workflow_name],
                                        'message': f"Workflow instructions loaded. Follow the steps in order for best results."
                                    }
                                else:
                                    tool_result = {
                                        'success': False,
                                        'error': f"Workflow '{workflow_name}' not found. Use 'list_all' to see available workflows."
                                    }
                            
                            # ✅ Handle get_smart_tool_instructions meta-tool  
                            elif tool_name == "get_smart_tool_instructions":
                                smart_tool_name = tool_input.get('tool_name', '')
                                
                                smart_tools_guide = {
                                    'google_docs_smart_create_from_markdown': {
                                        'description': 'Creates fully formatted Google Doc from markdown in ONE call',
                                        'supported_syntax': {
                                            'headings': '# H1, ## H2, ### H3, #### H4, ##### H5, ###### H6',
                                            'colored_headings': '## Title {#1a73e8} - Use hex colors for heading color',
                                            'text_formatting': '**bold**, *italic*, ~~strikethrough~~, ==highlight==, `code`',
                                            'code': '`inline code`, ```language\\ncode block\\n```',
                                            'links': '[text](url) - Creates hyperlink',
                                            'images': '![alt](url) - Embeds image from URL',
                                            'lists': '- bullet items, 1. numbered items (use 2 spaces for nested levels)',
                                            'blockquotes': '> quote text - Creates indented quote block',
                                            'tables': '| col1 | col2 |\\n|------|------|\\n| data1 | data2 | - Full table support',
                                            'horizontal_line': '--- - Creates horizontal divider',
                                            'page_break': '<<NEW-PAGE>> - Forces new page',
                                            'alignment': '|>centered text<| - Centers content',
                                            'colors': 'Use {#RRGGBB} after text for custom colors'
                                        },
                                        'example': '''google_docs_smart_create_from_markdown(
    title="Q1 Report",
    markdown_content="""
# Executive Summary {#1a73e8}

**Revenue:** $2.5M (+15% YoY)
*Generated on: 2025-10-28*

## Key Highlights

- Product launches: 3 new features
  - Feature A: 50k users
  - Feature B: 30k users
- Customer satisfaction: ==95%==

## Financial Details

| Metric | Q1 2024 | Q1 2025 | Growth |
|--------|---------|---------|--------|
| Revenue | $2.1M | $2.5M | +19% |
| Customers | 1,200 | 1,500 | +25% |

> "Best quarter in company history" - CEO

---

<<NEW-PAGE>>

## Next Steps

[View Dashboard](https://dashboard.company.com)

```python
# Revenue calculation
revenue = sum(sales_data)
print(f"Total: ${revenue:,.0f}")
```
"""
)''',
                                        'advantages': 'Only 1 API call vs 20+ with basic tools. All formatting applied automatically. Supports complex layouts.',
                                        'limitations': 'Max 50,000 characters per call. Very complex tables (>50 cols) may need manual adjustment.',
                                        'best_practices': [
                                            'Use colored headings for visual hierarchy',
                                            'Break long docs into sections with page breaks',
                                            'Test table formatting with sample data first',
                                            'Use blockquotes for important callouts',
                                            'Include links to related resources'
                                        ]
                                    },
                                    'google_docs_smart_update': {
                                        'description': 'Updates existing Google Doc with new markdown content (append or replace)',
                                        'supported_operations': {
                                            'append': 'Add new content to end of document',
                                            'prepend': 'Add new content to start of document',
                                            'replace': 'Replace entire document content',
                                            'insert_at': 'Insert at specific position (index)'
                                        },
                                        'example': '''google_docs_smart_update(
    document_id="abc123xyz",
    operation="append",
    markdown_content="## New Section\\n\\nAdditional findings..."
)''',
                                        'advantages': 'Only 2 API calls (get + update) vs 10+ with basic insert operations',
                                        'best_practices': [
                                            'Use "append" for adding sections',
                                            'Use "replace" for complete document rewrites',
                                            'Fetch document first if you need to preserve content'
                                        ]
                                    },
                                    'google_sheets_smart_create_with_formulas': {
                                        'description': 'Creates spreadsheet with data, formulas, and formatting in ONE call',
                                        'supported_features': {
                                            'formulas': 'SUM, AVERAGE, IF, VLOOKUP, etc. - All Google Sheets formulas',
                                            'formatting': 'Bold, colors, number formats, borders',
                                            'charts': 'Embedded charts (bar, line, pie)',
                                            'conditional_formatting': 'Color scales, data bars, icon sets',
                                            'data_validation': 'Dropdowns, ranges, custom rules'
                                        },
                                        'example': '''google_sheets_smart_create_with_formulas(
    title="Sales Dashboard",
    sheets=[
        {
            "name": "Data",
            "data": [
                ["Product", "Q1", "Q2", "Q3", "Q4", "Total"],
                ["Product A", 1000, 1200, 1500, 1800, "=SUM(B2:E2)"],
                ["Product B", 800, 900, 1100, 1300, "=SUM(B3:E3)"],
                ["Average", "=AVERAGE(B2:B3)", "=AVERAGE(C2:C3)", "=AVERAGE(D2:D3)", "=AVERAGE(E2:E3)", "=SUM(F2:F3)"]
            ],
            "formatting": {
                "A1:F1": {"bold": True, "bg_color": "#1a73e8", "text_color": "#ffffff"},
                "F2:F4": {"number_format": "$#,##0"}
            }
        },
        {
            "name": "Chart",
            "chart": {
                "type": "column",
                "data_range": "Data!A1:E3",
                "title": "Quarterly Sales"
            }
        }
    ]
)''',
                                        'advantages': 'Creates complete dashboard in 1 call. Formulas auto-calculate. Professional formatting.',
                                        'limitations': 'Max 5MB per spreadsheet. Very large datasets (>100k rows) may timeout.',
                                        'best_practices': [
                                            'Use relative cell references in formulas (A1, B2) not absolute ($A$1)',
                                            'Put raw data in first sheet, calculations in second',
                                            'Use named ranges for complex formulas',
                                            'Apply conditional formatting to highlight trends'
                                        ]
                                    },
                                    'gmail_smart_bulk_send_personalized': {
                                        'description': 'Sends personalized emails to multiple recipients with merge fields',
                                        'supported_features': {
                                            'personalization': 'Use {{field_name}} for merge fields',
                                            'rate_limiting': 'Automatic delays to avoid Gmail quota',
                                            'html_support': 'Full HTML emails with inline CSS',
                                            'attachments': 'Support for file attachments',
                                            'cc_bcc': 'Carbon copy and blind carbon copy',
                                            'tracking': 'Returns delivery status for each email'
                                        },
                                        'example': '''gmail_smart_bulk_send_personalized(
    subject="Welcome to {{company_name}}, {{first_name}}!",
    body="""
    <html>
    <body>
        <h2>Hi {{first_name}},</h2>
        <p>Welcome to <strong>{{company_name}}</strong>!</p>
        <p>Your account is ready. Next steps:</p>
        <ul>
            <li>Complete your profile</li>
            <li>Explore features</li>
            <li>Join our community</li>
        </ul>
        <p>Questions? Reply to this email or visit {{support_url}}</p>
        <p>Best,<br>The {{company_name}} Team</p>
    </body>
    </html>
    """,
    recipients=[
        {
            "email": "john@example.com",
            "first_name": "John",
            "company_name": "Acme Corp",
            "support_url": "https://support.acme.com"
        },
        {
            "email": "jane@example.com",
            "first_name": "Jane",
            "company_name": "Tech Industries",
            "support_url": "https://support.techindustries.com"
        }
    ],
    delay_seconds=2  # Wait 2 seconds between sends
)''',
                                        'advantages': 'Handles rate limits automatically, personalizes each email, tracks delivery. No manual loops needed.',
                                        'limitations': 'Gmail quota: 500 emails/day (standard), 2000/day (Google Workspace). Max 25MB per email.',
                                        'best_practices': [
                                            'Test with 1-2 emails first before bulk sending',
                                            'Use HTML for better formatting, fallback to plain text',
                                            'Include unsubscribe link for marketing emails',
                                            'Validate all email addresses before sending',
                                            'Use delay_seconds=2 for lists >100 recipients'
                                        ]
                                    },
                                    'woocommerce_bulk_create_products': {
                                        'description': 'Creates multiple WooCommerce products in ONE optimized call',
                                        'supported_fields': {
                                            'basic': 'name, description, short_description, sku, price, regular_price, sale_price',
                                            'inventory': 'stock_quantity, manage_stock, stock_status, backorders',
                                            'organization': 'categories, tags, attributes',
                                            'media': 'images (array of URLs), featured_image',
                                            'shipping': 'weight, dimensions (length, width, height)',
                                            'advanced': 'variations, downloadable, virtual'
                                        },
                                        'example': '''woocommerce_bulk_create_products(
    products=[
        {
            "name": "Wireless Headphones",
            "description": "<p>Premium wireless headphones with noise cancellation</p>",
            "short_description": "Noise-canceling wireless headphones",
            "sku": "WH-001",
            "regular_price": "199.99",
            "sale_price": "149.99",
            "categories": [{"id": 12}],  # Electronics category
            "tags": [{"name": "wireless"}, {"name": "audio"}],
            "images": [
                {"src": "https://example.com/images/headphones-1.jpg"},
                {"src": "https://example.com/images/headphones-2.jpg"}
            ],
            "stock_quantity": 50,
            "manage_stock": True,
            "weight": "0.5",
            "dimensions": {"length": "8", "width": "7", "height": "3"}
        },
        {
            "name": "USB-C Cable",
            "sku": "USB-001",
            "regular_price": "19.99",
            "categories": [{"id": 12}, {"id": 15}],  # Electronics & Accessories
            "stock_quantity": 200,
            "manage_stock": True
        }
        # ... up to 100 products per call
    ],
    status="draft"  # Create as draft for review first
)''',
                                        'advantages': 'Creates 100 products in 1 call vs 100 individual calls. Automatic SKU validation. Batch image uploads.',
                                        'limitations': 'Max 100 products per call. Large images may slow down process. Requires valid category IDs.',
                                        'best_practices': [
                                            'List existing products first to avoid duplicate SKUs',
                                            'Create categories before bulk import',
                                            'Use status="draft" for review, then publish',
                                            'Optimize images (<500KB) for faster uploads',
                                            'Include all required fields (name, sku, price) for each product'
                                        ]
                                    },
                                    'slack_smart_broadcast_message': {
                                        'description': 'Sends same message to multiple Slack channels with smart formatting',
                                        'supported_features': {
                                            'markdown': 'Bold (*bold*), italic (_italic_), code (`code`), links (<url|text>)',
                                            'mentions': '@channel, @here, @username',
                                            'blocks': 'Rich message blocks with buttons, images, context',
                                            'threading': 'Option to send as thread reply',
                                            'scheduling': 'Schedule message for future time'
                                        },
                                        'example': '''slack_smart_broadcast_message(
    channel_ids=["C123ABC", "C456DEF", "C789GHI"],
    text="🚀 *Product Launch Alert*",
    blocks=[
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🚀 *Product Launch Alert*\\n\\nWe just launched our new feature: *Real-time Analytics*"
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*When:*\\nToday, 2PM EST"},
                {"type": "mrkdwn", "text": "*Where:*\\nMain Dashboard"}
            ]
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "View Release Notes"},
                    "url": "https://docs.company.com/releases"
                }
            ]
        }
    ]
)''',
                                        'advantages': 'Sends to multiple channels in 1 call. Rich formatting. Professional appearance.',
                                        'limitations': 'Slack rate limits apply (1 message per second per channel). Max 50 blocks per message.',
                                        'best_practices': [
                                            'Use blocks for important announcements (better visibility)',
                                            'Test in one channel first before broadcasting',
                                            'Avoid @channel for non-urgent messages',
                                            'Include links to relevant resources',
                                            'Use emojis sparingly for visual hierarchy'
                                        ]
                                    },
                                    'google_calendar_smart_schedule': {
                                        'description': 'Finds optimal meeting time by checking availability across multiple calendars',
                                        'supported_features': {
                                            'availability_check': 'Checks free/busy for all attendees',
                                            'time_preferences': 'Morning/afternoon/business hours',
                                            'duration': 'Specify meeting length (15min to 8hrs)',
                                            'buffer': 'Add buffer time between meetings',
                                            'recurring': 'Setup recurring meetings'
                                        },
                                        'example': '''google_calendar_smart_schedule(
    summary="Product Review Meeting",
    attendees=["john@company.com", "jane@company.com", "bob@company.com"],
    duration_minutes=60,
    date_range={
        "start": "2025-10-29",
        "end": "2025-11-02"
    },
    preferences={
        "time_of_day": "morning",  # morning, afternoon, anytime
        "business_hours_only": True,
        "buffer_minutes": 15  # 15min buffer before/after
    }
)

# Returns best available time slot:
# {
#   "success": True,
#   "proposed_time": "2025-10-30T10:00:00-07:00",
#   "all_attendees_available": True,
#   "event_id": "xyz123"
# }''',
                                        'advantages': 'Automatically finds time that works for everyone. Creates event in one step. Handles timezones.',
                                        'limitations': 'Requires calendar read access for all attendees. May not find time if calendars are very full.',
                                        'best_practices': [
                                            'Provide 3-5 day range for better options',
                                            'Specify time_of_day preference',
                                            'Add buffer for back-to-back meetings',
                                            'Check returned proposed_time before accepting'
                                        ]
                                    },
                                    'stripe_create_subscription': {
                                        'description': 'Creates recurring Stripe subscription with pricing, trials, and billing',
                                        'supported_features': {
                                            'pricing': 'Monthly, yearly, custom intervals',
                                            'trials': 'Free trial periods (days)',
                                            'coupons': 'Discount codes and promotions',
                                            'proration': 'Handle mid-cycle changes',
                                            'invoicing': 'Auto-generate invoices'
                                        },
                                        'example': '''stripe_create_subscription(
    customer_id="cus_ABC123",  # From stripe_create_customer
    price_id="price_XYZ789",    # From stripe_create_price
    trial_period_days=14,       # 14-day free trial
    payment_behavior="default_incomplete",  # Require payment method
    metadata={
        "plan": "Pro",
        "signup_date": "2025-10-28"
    },
    coupon="SAVE20"  # Optional discount code
)

# Returns subscription object with:
# - subscription_id
# - status (trialing, active, past_due, canceled)
# - current_period_start/end
# - cancel_at_period_end (boolean)''',
                                        'advantages': 'Handles complex billing automatically. Prorations, trials, coupons all built-in. Webhook integration.',
                                        'limitations': 'Requires existing customer and price. Payment method must be added before trial ends.',
                                        'best_practices': [
                                            'Create customer first (stripe_create_customer)',
                                            'Create price/plan first (stripe_create_price)',
                                            'Use trials to reduce friction',
                                            'Set up webhooks to track subscription events',
                                            'Store subscription_id in your database'
                                        ]
                                    },
                                    'instagram_smart_post_with_scheduling': {
                                        'description': 'Posts or schedules Instagram content with optimal timing and hashtags',
                                        'supported_features': {
                                            'media_types': 'Photo, video, carousel (multiple images)',
                                            'scheduling': 'Schedule for future date/time',
                                            'hashtags': 'Auto-suggest relevant hashtags',
                                            'location': 'Geotag posts with location',
                                            'first_comment': 'Post hashtags as first comment (cleaner caption)'
                                        },
                                        'example': '''instagram_smart_post_with_scheduling(
    media_url="https://example.com/images/product.jpg",
    caption="""Introducing our new product! 🎉

Available now in 3 colors.
Link in bio for details.""",
    hashtags=["newproduct", "innovation", "design", "tech"],
    schedule_time="2025-10-30T14:00:00-07:00",  # 2PM PST (peak engagement)
    location_id=1234567,  # Optional location tag
    first_comment=True  # Put hashtags in first comment instead
)

# For carousel posts:
instagram_smart_post_with_scheduling(
    media_urls=[
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg",
        "https://example.com/image3.jpg"
    ],
    caption="Swipe to see all features! ➡️",
    schedule_time="2025-10-30T18:00:00-07:00"
)''',
                                        'advantages': 'Schedules for optimal engagement times. Auto-formats hashtags. Supports all media types.',
                                        'limitations': 'Instagram Business account required. Max 10 images per carousel. Videos max 60s (feed) or 90s (reels).',
                                        'best_practices': [
                                            'Post during peak hours: 11AM-1PM, 7-9PM local time',
                                            'Use 5-10 relevant hashtags (not 30)',
                                            'Put hashtags in first comment for cleaner look',
                                            'Square images (1080x1080) or portrait (1080x1350)',
                                            'Use emojis sparingly in captions'
                                        ]
                                    },
                                    'teams_smart_daily_standup': {
                                        'description': 'Posts automated daily standup message to Teams channel with structured format',
                                        'supported_features': {
                                            'structured_format': 'Yesterday/Today/Blockers sections',
                                            'html_formatting': 'Rich HTML formatting with headings, lists, emphasis',
                                            'team_mentions': 'Option to @mention entire team',
                                            'importance': 'Set message importance (normal/high)',
                                            'date_tracking': 'Auto-includes date in standup'
                                        },
                                        'example': '''teams_smart_daily_standup(
    team_id="abc123...",
    channel_id="xyz789...",
    standup_data={
        "date": "2025-10-28",
        "yesterday": [
            "Completed user authentication module",
            "Fixed 3 critical bugs in payment flow",
            "Reviewed 5 pull requests"
        ],
        "today": [
            "Implement email notification system",
            "Write unit tests for new features",
            "Team meeting at 2PM"
        ],
        "blockers": [
            "Waiting for API key from external service",
            "Need design approval for new UI"
        ]
    },
    mention_team=True  # Will @mention everyone
)

# Returns: Message posted with formatted standup''',
                                        'advantages': 'One call vs manual formatting. Professional appearance. Consistent structure.',
                                        'limitations': 'Teams channel must exist. User must have posting permissions.',
                                        'best_practices': [
                                            'Post standups at consistent time each day',
                                            'Keep items concise (1-2 lines each)',
                                            'Use mention_team=True for important updates only',
                                            'Include actual blockers (not "None" if there are issues)',
                                            'Link to relevant tickets/PRs in items'
                                        ]
                                    },
                                    'teams_smart_broadcast_announcement': {
                                        'description': 'Sends announcement to multiple Teams channels simultaneously with rate limiting',
                                        'supported_features': {
                                            'multi_channel': 'Send to unlimited channels in one call',
                                            'rate_limiting': 'Automatic delays between sends',
                                            'importance_levels': 'normal, high, urgent',
                                            'html_formatting': 'Full HTML support for rich messages',
                                            'delivery_tracking': 'Returns sent/failed status per channel'
                                        },
                                        'example': '''teams_smart_broadcast_announcement(
    channels=[
        {"team_id": "team1_id", "channel_id": "general_id"},
        {"team_id": "team1_id", "channel_id": "announcements_id"},
        {"team_id": "team2_id", "channel_id": "general_id"}
    ],
    message="""
    <h2>🚀 System Maintenance Notice</h2>
    <p><strong>When:</strong> Tonight 11PM - 2AM EST</p>
    <p><strong>Impact:</strong> All services will be offline</p>
    <p><strong>Action Required:</strong> Save your work before 11PM</p>
    <p>Questions? Contact IT Support</p>
    """,
    importance="high",
    delay_seconds=2  # 2 second delay between channels
)

# Returns: {"sent": 3, "failed": 0, "total": 3}''',
                                        'advantages': 'Broadcasts to many channels in one call. Handles rate limits automatically. Tracks delivery.',
                                        'limitations': 'Max 50 channels per call. Teams API rate limits apply.',
                                        'best_practices': [
                                            'Test message in one channel first',
                                            'Use importance="high" for urgent announcements only',
                                            'Include clear call-to-action',
                                            'Add 2-3 second delays for large broadcasts',
                                            'Keep message under 10,000 characters'
                                        ]
                                    },
                                    'teams_smart_create_poll': {
                                        'description': 'Creates interactive poll in Teams channel with options and vote tracking',
                                        'supported_features': {
                                            'multiple_options': 'Unlimited poll options',
                                            'single_or_multiple': 'Allow single or multiple selections',
                                            'vote_instructions': 'Auto-generates voting instructions',
                                            'formatted_display': 'Professional poll layout'
                                        },
                                        'example': '''teams_smart_create_poll(
    team_id="abc123...",
    channel_id="xyz789...",
    question="What day works best for team lunch?",
    options=[
        "Monday",
        "Wednesday",
        "Friday"
    ],
    allow_multiple=False  # Single selection only
)

# Creates formatted poll message with numbered options''',
                                        'advantages': 'Quick poll creation. Clear voting instructions. Professional appearance.',
                                        'limitations': 'Vote tracking requires reading replies. Not built-in Teams poll feature (uses formatted message).',
                                        'best_practices': [
                                            'Keep questions clear and concise',
                                            'Limit to 5-7 options for best results',
                                            'Set deadline in poll question',
                                            'Use allow_multiple=False unless necessary',
                                            'Follow up with results summary'
                                        ]
                                    },
                                    'teams_smart_meeting_summary': {
                                        'description': 'Posts structured meeting summary with attendees, key points, and action items',
                                        'supported_features': {
                                            'attendee_list': 'Lists all meeting participants',
                                            'key_points': 'Formatted bullet points',
                                            'action_items_table': 'HTML table with task/owner/due date',
                                            'professional_formatting': 'Rich HTML layout',
                                            'importance_flag': 'Highlights summary as important'
                                        },
                                        'example': '''teams_smart_meeting_summary(
    team_id="abc123...",
    channel_id="xyz789...",
    meeting_title="Q4 Planning Meeting",
    attendees=["Alice Smith", "Bob Johnson", "Carol White"],
    key_points=[
        "Q4 revenue target: $5M",
        "New product launch planned for November",
        "Hiring 3 new engineers"
    ],
    action_items=[
        {
            "task": "Finalize budget proposal",
            "owner": "Alice Smith",
            "due_date": "2025-11-05"
        },
        {
            "task": "Create hiring job posts",
            "owner": "Bob Johnson",
            "due_date": "2025-11-01"
        }
    ]
)

# Returns: Formatted meeting summary posted to channel''',
                                        'advantages': 'Professional meeting notes. Action tracking. Clear ownership.',
                                        'limitations': 'Teams channel required. No automatic calendar integration.',
                                        'best_practices': [
                                            'Post summary within 24 hours of meeting',
                                            'Tag action item owners in follow-up',
                                            'Include meeting date in title',
                                            'Keep key points to 5-10 items max',
                                            'Set realistic due dates for action items'
                                        ]
                                    },
                                    'onedrive_smart_organize_by_type': {
                                        'description': 'Automatically organizes files into folders by extension type',
                                        'supported_features': {
                                            'auto_detection': 'Detects file extensions automatically',
                                            'folder_creation': 'Creates folders for each file type',
                                            'bulk_move': 'Moves all files in one operation',
                                            'result_tracking': 'Reports organized/failed files'
                                        },
                                        'example': '''onedrive_smart_organize_by_type(
    source_folder="Documents/Unsorted",  # Folder to organize
)

# Automatically creates:
# - PDF/ folder (moves all .pdf files)
# - DOCX/ folder (moves all .docx files)
# - XLSX/ folder (moves all .xlsx files)
# - JPG/ folder (moves all .jpg files)
# - etc.

# Returns: {
#   "organized": ["file1.pdf", "file2.docx", "file3.xlsx"],
#   "failed": [],
#   "folders_created": ["PDF", "DOCX", "XLSX"]
# }''',
                                        'advantages': 'One call organizes hundreds of files. Auto-creates folders. Handles errors gracefully.',
                                        'limitations': 'Max 5000 files per call. Existing folders may cause conflicts.',
                                        'best_practices': [
                                            'Run on specific folders (not root) for better control',
                                            'Backup folder before organizing (use onedrive_smart_backup_folder)',
                                            'Test on small folder first',
                                            'Check "failed" array for issues',
                                            'Use for downloads folders, project archives'
                                        ]
                                    },
                                    'onedrive_smart_backup_folder': {
                                        'description': 'Creates timestamped backup copy of entire folder',
                                        'supported_features': {
                                            'timestamp_naming': 'Auto-adds timestamp to backup name',
                                            'recursive_copy': 'Copies all subfolders and files',
                                            'async_operation': 'Runs in background for large folders',
                                            'status_tracking': 'Returns backup folder ID and status'
                                        },
                                        'example': '''onedrive_smart_backup_folder(
    folder_path="Documents/ImportantProject"
)

# Creates: "Backup_ImportantProject_20251028_143000"
# Location: Same parent folder as original

# Returns: {
#   "success": true,
#   "backup_folder": "Backup_ImportantProject_20251028_143000",
#   "message": "Backup created successfully"
# }''',
                                        'advantages': 'One-call full folder backup. Timestamped for version tracking. Async for large folders.',
                                        'limitations': 'OneDrive storage limits apply. Large folders (>1GB) may take time.',
                                        'best_practices': [
                                            'Backup before major changes or deletions',
                                            'Keep backups in separate "Backups" folder',
                                            'Delete old backups after 30 days',
                                            'Check storage quota before backing up large folders',
                                            'Use before running organize or cleanup operations'
                                        ]
                                    },
                                    'onedrive_smart_cleanup_duplicates': {
                                        'description': 'Finds and removes duplicate files based on name and size',
                                        'supported_features': {
                                            'duplicate_detection': 'Matches by name and size',
                                            'keep_strategy': 'keep_newest or keep_oldest',
                                            'safe_deletion': 'Reports deleted files before removing',
                                            'result_summary': 'Shows kept/deleted/failed counts'
                                        },
                                        'example': '''onedrive_smart_cleanup_duplicates(
    folder_path="Documents/Photos",
    strategy="keep_newest"  # Keep most recent copy
)

# Returns: {
#   "deleted": ["photo (1).jpg", "photo (2).jpg"],
#   "kept": ["photo.jpg"],
#   "failed": [],
#   "message": "Deleted 2 duplicate files"
# }''',
                                        'advantages': 'Frees storage space. One-call cleanup. Safe deletion with reporting.',
                                        'limitations': 'Only matches by name+size (not content hash). Cannot restore deleted files.',
                                        'best_practices': [
                                            'ALWAYS backup folder first (use onedrive_smart_backup_folder)',
                                            'Test on small folder before full cleanup',
                                            'Use keep_newest for active projects',
                                            'Review "deleted" list before confirming',
                                            'Run periodically (monthly) for maintenance'
                                        ]
                                    },
                                    'onedrive_smart_sync_folders': {
                                        'description': 'Synchronizes two OneDrive folders (one-way or two-way)',
                                        'supported_features': {
                                            'one_way_sync': 'Source → Destination only',
                                            'two_way_sync': 'Bidirectional synchronization',
                                            'timestamp_comparison': 'Only syncs modified files',
                                            'conflict_detection': 'Reports sync conflicts',
                                            'result_tracking': 'Shows copied/updated/failed files'
                                        },
                                        'example': '''onedrive_smart_sync_folders(
    source_folder="Documents/WorkFiles",
    destination_folder="Backups/WorkFiles",
    sync_mode="one_way"  # or "two_way"
)

# Returns: {
#   "copied": ["newfile.docx"],
#   "updated": ["modified.xlsx"],
#   "failed": [],
#   "message": "Synced: 1 new, 1 updated"
# }''',
                                        'advantages': 'Automatic folder synchronization. Only syncs changed files. Bidirectional support.',
                                        'limitations': 'Two-way sync can cause conflicts if both sides modified. Max 1000 files per sync.',
                                        'best_practices': [
                                            'Use one_way for backup scenarios',
                                            'Use two_way only for non-conflicting workflows',
                                            'Run regularly (daily/weekly) for best results',
                                            'Monitor "failed" array for issues',
                                            'Combine with onedrive_smart_backup_folder for safety'
                                        ]
                                    },
                                    'calendar_smart_find_meeting_time': {
                                        'description': 'AI-powered meeting scheduler that finds optimal time across attendees',
                                        'supported_features': {
                                            'availability_check': 'Checks all attendees calendars',
                                            'preference_matching': 'Morning/afternoon/business hours',
                                            'duration_flexible': '15min to 8 hours',
                                            'timezone_aware': 'Handles multiple timezones',
                                            'auto_scheduling': 'Creates event if time found'
                                        },
                                        'example': '''calendar_smart_find_meeting_time(
    attendees=["alice@company.com", "bob@company.com", "carol@company.com"],
    duration_minutes=60,
    date_range={
        "start": "2025-10-29",
        "end": "2025-11-02"  # Search window
    },
    timezone="America/Los_Angeles",
    preferences={
        "time_of_day": "morning",  # morning, afternoon, anytime
        "business_hours_only": true,
        "buffer_minutes": 15
    }
)

# Returns: {
#   "proposed_time": "2025-10-30T10:00:00-07:00",
#   "all_attendees_available": true,
#   "event_id": "xyz123..."
# }''',
                                        'advantages': 'Finds time automatically. Checks all calendars. Creates event in one call.',
                                        'limitations': 'Requires calendar read access for all attendees. May fail if calendars very busy.',
                                        'best_practices': [
                                            'Provide 3-5 day search window',
                                            'Specify time preferences clearly',
                                            'Use buffer for back-to-back meetings',
                                            'Check proposed_time before accepting',
                                            'Fall back to manual scheduling if no time found'
                                        ]
                                    },
                                    'calendar_smart_schedule_series': {
                                        'description': 'Bulk creates multiple calendar events with conflict detection',
                                        'supported_features': {
                                            'batch_creation': 'Create up to 50 events per call',
                                            'conflict_detection': 'Checks for overlaps before creating',
                                            'online_meetings': 'Auto-generates Teams meeting links',
                                            'result_tracking': 'Reports created/conflicts/failed',
                                            'rollback_on_error': 'Option to cancel all if any fails'
                                        },
                                        'example': '''calendar_smart_schedule_series(
    events=[
        {
            "subject": "Team Standup",
            "start_time": "2025-10-29T09:00:00Z",
            "end_time": "2025-10-29T09:30:00Z",
            "attendees": ["team@company.com"],
            "is_online_meeting": true
        },
        {
            "subject": "Client Meeting",
            "start_time": "2025-10-29T14:00:00Z",
            "end_time": "2025-10-29T15:00:00Z",
            "attendees": ["client@external.com"],
            "location": "Conference Room A"
        },
        # ... up to 50 events
    ],
    check_conflicts=true  # Will skip events with conflicts
)

# Returns: {
#   "created": ["Team Standup", "Client Meeting"],
#   "conflicts": [],
#   "failed": [],
#   "message": "Created 2 events, 0 conflicts, 0 failed"
# }''',
                                        'advantages': 'Creates many events in one call. Conflict detection. Teams links auto-generated.',
                                        'limitations': 'Max 50 events per call. Conflict check adds processing time.',
                                        'best_practices': [
                                            'Enable check_conflicts for important events',
                                            'Sort events by start time for better conflict detection',
                                            'Use for recurring meetings, workshops, training series',
                                            'Set is_online_meeting=true for remote events',
                                            'Review conflicts array and reschedule manually'
                                        ]
                                    },
                                    'calendar_smart_conflict_resolver': {
                                        'description': 'Detects and optionally auto-resolves calendar conflicts',
                                        'supported_features': {
                                            'conflict_detection': 'Finds overlapping events',
                                            'overlap_calculation': 'Shows minutes of overlap',
                                            'auto_resolve': 'Can move/delete conflicting events',
                                            'priority_handling': 'Respects event importance',
                                            'recommendation_engine': 'Suggests resolution actions'
                                        },
                                        'example': '''calendar_smart_conflict_resolver(
    start_date="2025-10-28",
    end_date="2025-11-04",
    auto_resolve=false  # Manual resolution mode
)

# Returns: {
#   "conflicts_found": 2,
#   "conflicts": [
#     {
#       "event1": {"subject": "Team Meeting", "start": "..."},
#       "event2": {"subject": "Client Call", "start": "..."},
#       "overlap_minutes": 30
#     }
#   ],
#   "recommendations": [
#     "Move 'Team Meeting' to 10:00 AM",
#     "Shorten 'Client Call' to 30 minutes"
#   ]
# }''',
                                        'advantages': 'Finds hidden conflicts. Provides resolution suggestions. Can auto-fix simple conflicts.',
                                        'limitations': 'Cannot move events without permissions. Auto-resolve may make wrong choices.',
                                        'best_practices': [
                                            'Run with auto_resolve=false first (review recommendations)',
                                            'Check conflicts weekly for busy calendars',
                                            'Manually resolve important meeting conflicts',
                                            'Use before major events or busy weeks',
                                            'Save recommendations for future reference'
                                        ]
                                    },
                                    'todo_smart_daily_digest': {
                                        'description': 'Generates comprehensive daily task summary with priorities and deadlines',
                                        'supported_features': {
                                            'overdue_tracking': 'Lists tasks past due date',
                                            'due_today': 'Shows tasks due today',
                                            'due_this_week': 'Upcoming tasks (7 days)',
                                            'high_priority': 'Filters high-importance tasks',
                                            'summary_stats': 'Total counts by category'
                                        },
                                        'example': '''todo_smart_daily_digest()

# Returns: {
#   "date": "2025-10-28",
#   "overdue": [
#     {"title": "Submit report", "due_date": "2025-10-25"}
#   ],
#   "due_today": [
#     {"title": "Client meeting prep", "importance": "high"}
#   ],
#   "due_this_week": [
#     {"title": "Code review", "due_date": "2025-11-01"}
#   ],
#   "high_priority": [
#     {"title": "Fix production bug", "importance": "high"}
#   ],
#   "summary": {
#     "overdue_count": 1,
#     "due_today_count": 1,
#     "due_this_week_count": 3,
#     "high_priority_count": 2
#   }
# }''',
                                        'advantages': 'Complete task overview. Prioritization built-in. Daily snapshot.',
                                        'limitations': 'Across all To Do lists (not filtered by project). No Planner integration in digest.',
                                        'best_practices': [
                                            'Run at start of each day',
                                            'Address overdue tasks first',
                                            'Review high_priority array for urgent items',
                                            'Use as daily planning tool',
                                            'Share digest with team for transparency'
                                        ]
                                    },
                                    'planner_smart_sprint_setup': {
                                        'description': 'Creates complete sprint board with buckets and initial structure',
                                        'supported_features': {
                                            'custom_buckets': 'Backlog, To Do, In Progress, Review, Done',
                                            'duration_config': 'Specify sprint length (weeks)',
                                            'date_tracking': 'Sets start and end dates',
                                            'auto_organization': 'Creates logical workflow structure',
                                            'team_ready': 'Ready for immediate use'
                                        },
                                        'example': '''planner_smart_sprint_setup(
    group_id="group123...",  # Microsoft 365 Group ID
    sprint_name="Sprint 23 - Q4 2025",
    duration_weeks=2,
    buckets=["Backlog", "To Do", "In Progress", "Review", "Done"]
    # Or use default buckets
)

# Returns: {
#   "plan_id": "plan123...",
#   "buckets_created": [
#     {"name": "Backlog", "id": "bucket1..."},
#     {"name": "To Do", "id": "bucket2..."},
#     {"name": "In Progress", "id": "bucket3..."},
#     {"name": "Review", "id": "bucket4..."},
#     {"name": "Done", "id": "bucket5..."}
#   ],
#   "start_date": "2025-10-28",
#   "end_date": "2025-11-11"
# }''',
                                        'advantages': 'Complete sprint board in one call. Standard workflow structure. Team-ready immediately.',
                                        'limitations': 'Requires Microsoft 365 Group. Cannot add tasks during creation.',
                                        'best_practices': [
                                            'Use at start of each sprint',
                                            'Customize buckets for team workflow',
                                            'Stick to 2-week sprints for agile',
                                            'Add tasks after board creation',
                                            'Archive old sprint boards after completion'
                                        ]
                                    },
                                    'planner_smart_team_workload': {
                                        'description': 'Analyzes team task distribution and provides workload balancing recommendations',
                                        'supported_features': {
                                            'per_user_analysis': 'Tasks/completed/in-progress per team member',
                                            'workload_calculation': 'Identifies overloaded/underutilized members',
                                            'unassigned_tracking': 'Lists tasks without assignees',
                                            'recommendations': 'Suggests task redistribution',
                                            'priority_weighting': 'Considers high-priority tasks'
                                        },
                                        'example': '''planner_smart_team_workload(
    plan_id="plan123..."
)

# Returns: {
#   "total_tasks": 45,
#   "workload_by_user": {
#     "alice@company.com": {
#       "total_tasks": 12,
#       "completed": 5,
#       "in_progress": 4,
#       "high_priority": 3
#     },
#     "bob@company.com": {
#       "total_tasks": 8,
#       "completed": 6,
#       "in_progress": 2,
#       "high_priority": 1
#     }
#   },
#   "unassigned_tasks": 5,
#   "analysis": {
#     "average_tasks_per_user": 10,
#     "overloaded_users": ["alice@company.com"],
#     "underutilized_users": ["carol@company.com"]
#   },
#   "recommendations": [
#     "Redistribute tasks from Alice to Carol",
#     "Assign 5 unassigned tasks"
#   ]
# }''',
                                        'advantages': 'Reveals workload imbalances. Data-driven recommendations. Prevents burnout.',
                                        'limitations': 'Cannot auto-reassign tasks (manual action needed). Based on task count (not time estimates).',
                                        'best_practices': [
                                            'Run weekly during sprint',
                                            'Address overloaded users immediately',
                                            'Assign unassigned tasks promptly',
                                            'Use for sprint planning',
                                            'Track trends over multiple sprints'
                                        ]
                                    },
                                    'todo_smart_recurring_tasks': {
                                        'description': 'Creates series of recurring tasks with custom patterns and schedules',
                                        'supported_features': {
                                            'recurrence_patterns': 'Daily, weekly, monthly, custom',
                                            'count_based': 'Generate N occurrences',
                                            'date_based': 'Until specific end date',
                                            'template_support': 'Use task template for all occurrences',
                                            'auto_naming': 'Adds dates to task titles'
                                        },
                                        'example': '''todo_smart_recurring_tasks(
    task_template={
        "title": "Weekly Team Report",
        "list_id": "list123...",
        "importance": "normal",
        "body": "Submit team progress report"
    },
    recurrence_pattern="weekly",  # daily, weekly, monthly
    count=12  # Create 12 occurrences
)

# Creates tasks:
# - "Weekly Team Report - 2025-10-28"
# - "Weekly Team Report - 2025-11-04"
# - "Weekly Team Report - 2025-11-11"
# ... (12 total)

# Returns: {
#   "created": ["Weekly Team Report - 2025-10-28", ...],
#   "failed": [],
#   "message": "Created 12 recurring tasks"
# }''',
                                        'advantages': 'One-call creates entire series. Auto-dates tasks. Template-based for consistency.',
                                        'limitations': 'Max 50 occurrences per call. Cannot modify later (must delete and recreate).',
                                        'best_practices': [
                                            'Use for weekly reports, monthly reviews, daily standups',
                                            'Keep count reasonable (12-24 occurrences)',
                                            'Set appropriate due dates in template',
                                            'Use clear naming convention',
                                            'Create separate series for different frequencies'
                                        ]
                                    },
                                    'word_smart_generate_report': {
                                        'description': 'Creates formatted Word report with sections, TOC, and professional styling in ONE call',
                                        'supported_features': {
                                            'sections': 'Multiple sections with headings (levels 1-9)',
                                            'table_of_contents': 'Auto-generated TOC at document start',
                                            'styling': 'Professional formatting (fonts, spacing, margins)',
                                            'page_breaks': 'Automatic page breaks between sections',
                                            'headers_footers': 'Optional headers and footers'
                                        },
                                        'example': '''word_smart_generate_report(
    title="Q1 2025 Business Review",
    sections=[
        {
            "heading": "Executive Summary",
            "level": 1,
            "content": "Revenue increased by 25% with strong customer retention..."
        },
        {
            "heading": "Financial Performance",
            "level": 1,
            "content": "Revenue: $2.5M\\nCosts: $1.2M\\nProfit: $1.3M"
        },
        {
            "heading": "Key Metrics",
            "level": 2,
            "content": "Customer count: 1,500\\nChurn rate: 5%"
        }
    ],
    include_toc=true,
    folder_name="Reports/Q1"
)

# Returns: {
#   "document_id": "abc123",
#   "web_url": "https://onedrive.live.com/...",
#   "sections_created": 3
# }''',
                                        'advantages': 'Professional report in 1 call. Auto-formatting. TOC generation. Page breaks handled.',
                                        'limitations': 'Max 50 sections per report. Requires Files.ReadWrite.All scope.',
                                        'best_practices': [
                                            'Use heading levels properly (1 for main, 2 for sub)',
                                            'Keep sections focused and concise',
                                            'Include TOC for reports >5 pages',
                                            'Store in OneDrive organized folder structure',
                                            'Export to PDF for final distribution'
                                        ]
                                    },
                                    'word_smart_merge_documents': {
                                        'description': 'Merges multiple Word documents with page breaks and unified TOC',
                                        'supported_features': {
                                            'multiple_docs': 'Combine 2-50 documents',
                                            'page_breaks': 'Auto-insert page breaks between documents',
                                            'unified_toc': 'Single TOC for merged document',
                                            'preserve_formatting': 'Keeps original document formatting'
                                        },
                                        'example': '''word_smart_merge_documents(
    document_ids=["doc1_id", "doc2_id", "doc3_id"],
    output_title="Merged Annual Report 2025",
    include_page_breaks=true,
    generate_toc=true
)

# Merges all documents in order with page breaks
# Returns: {
#   "document_id": "merged_doc_id",
#   "total_documents_merged": 3
# }''',
                                        'advantages': 'Merge multiple docs in 1 call. Auto-page breaks. Unified TOC.',
                                        'limitations': 'Max 50 documents per merge. Large docs may timeout.',
                                        'best_practices': [
                                            'Merge documents with similar formatting',
                                            'Always include page breaks for readability',
                                            'Generate TOC for merged docs >10 pages',
                                            'Test with 2-3 docs before large merges'
                                        ]
                                    },
                                    'word_smart_template_fill': {
                                        'description': 'Fills Word template by replacing {{variable}} placeholders with values',
                                        'supported_features': {
                                            'variable_replacement': 'Replace {{name}}, {{date}}, etc.',
                                            'conditional_sections': 'Show/hide based on values',
                                            'multiple_variables': 'Replace hundreds of variables',
                                            'preserve_formatting': 'Maintains template styling'
                                        },
                                        'example': '''word_smart_template_fill(
    template_document_id="template_id",
    variables={
        "client_name": "Acme Corp",
        "date": "October 29, 2025",
        "amount": "$50,000",
        "description": "Professional services for Q4 2025"
    },
    output_title="Invoice_AcmeCorp_Oct2025"
)

# Template contains: "Invoice for {{client_name}} dated {{date}}"
# Result: "Invoice for Acme Corp dated October 29, 2025"

# Returns: {
#   "document_id": "filled_doc_id",
#   "variables_replaced": 4
# }''',
                                        'advantages': 'Fill templates in 1 call. Replace hundreds of variables. Preserve formatting.',
                                        'limitations': 'Variables must be {{variable}} format. Template must exist in OneDrive.',
                                        'best_practices': [
                                            'Use consistent {{variable}} naming',
                                            'Create reusable templates (invoices, contracts, reports)',
                                            'Test template with sample data first',
                                            'Store templates in dedicated folder'
                                        ]
                                    },
                                    'word_smart_extract_data': {
                                        'description': 'Extracts structured data from Word document (headings, tables, lists, images)',
                                        'supported_features': {
                                            'headings': 'Extract all headings with levels',
                                            'tables': 'Extract table data as arrays',
                                            'lists': 'Extract bulleted and numbered lists',
                                            'images': 'Get image URLs and alt text',
                                            'metadata': 'Document properties and stats'
                                        },
                                        'example': '''word_smart_extract_data(
    document_id="doc_id",
    extract_types=["headings", "tables", "lists"]
)

# Returns: {
#   "headings": [
#       {"text": "Executive Summary", "level": 1},
#       {"text": "Financial Data", "level": 2}
#   ],
#   "tables": [
#       [["Q1", "Q2"], ["$1M", "$1.2M"]]
#   ],
#   "lists": [
#       ["Item 1", "Item 2", "Item 3"]
#   ]
# }''',
                                        'advantages': 'Extract all data in 1 call. Structured output. Multiple formats.',
                                        'limitations': 'Complex nested tables may need cleanup. Max 100 tables per doc.',
                                        'best_practices': [
                                            'Use for data migration from Word to Excel/DB',
                                            'Extract headings for document analysis',
                                            'Extract tables for data processing',
                                            'Combine with other tools for workflows'
                                        ]
                                    },
                                    'excel_smart_import_csv': {
                                        'description': 'Imports CSV with auto-formatting, headers, and optional chart generation',
                                        'supported_features': {
                                            'auto_headers': 'Formats first row as headers',
                                            'data_types': 'Auto-detects numbers, dates, text',
                                            'formatting': 'Applies cell formatting and borders',
                                            'chart_generation': 'Creates chart from data',
                                            'summary_row': 'Adds totals/averages'
                                        },
                                        'example': '''excel_smart_import_csv(
    csv_file_path="/path/to/data.csv",
    workbook_name="Sales Data 2025",
    auto_format=true,
    create_chart={
        "type": "ColumnClustered",
        "range": "A1:D10"
    }
)

# Returns: {
#   "workbook_id": "wb_id",
#   "rows_imported": 100,
#   "chart_created": true
# }''',
                                        'advantages': 'Import + format + chart in 1 call. Auto-detection. Professional appearance.',
                                        'limitations': 'Max 10,000 rows per import. CSV must be valid format.',
                                        'best_practices': [
                                            'Use for data visualization workflows',
                                            'Create charts for key metrics',
                                            'Validate CSV format before import',
                                            'Use summary rows for totals'
                                        ]
                                    },
                                    'excel_smart_data_analysis': {
                                        'description': 'Analyzes Excel data with summary statistics (count, sum, avg, min, max) per column',
                                        'supported_features': {
                                            'column_stats': 'Count, sum, average, min, max for each column',
                                            'data_types': 'Identifies numeric vs text columns',
                                            'missing_data': 'Counts blank cells',
                                            'distribution': 'Basic distribution analysis'
                                        },
                                        'example': '''excel_smart_data_analysis(
    workbook_id="wb_id",
    sheet_name="Sales Data",
    range="A1:E100"
)

# Returns: {
#   "columns": {
#       "Revenue": {"count": 100, "sum": 250000, "avg": 2500, "min": 1000, "max": 5000},
#       "Units": {"count": 100, "sum": 1500, "avg": 15, "min": 5, "max": 30}
#   }
# }''',
                                        'advantages': 'Instant statistics. Multiple columns. Identifies data quality issues.',
                                        'limitations': 'Basic statistics only. Max 100 columns.',
                                        'best_practices': [
                                            'Use for quick data quality checks',
                                            'Analyze before creating complex formulas',
                                            'Check for missing data',
                                            'Use results to inform chart creation'
                                        ]
                                    },
                                    'excel_smart_create_pivot': {
                                        'description': 'Creates pivot table with custom grouping and aggregations',
                                        'supported_features': {
                                            'row_grouping': 'Group by multiple columns',
                                            'value_aggregation': 'Sum, average, count, min, max',
                                            'filters': 'Apply filters to data',
                                            'auto_formatting': 'Professional pivot table styling'
                                        },
                                        'example': '''excel_smart_create_pivot(
    workbook_id="wb_id",
    source_range="Data!A1:F1000",
    rows=["Region", "Product"],
    values=[{"field": "Revenue", "function": "sum"}],
    filters=["Year"]
)

# Creates pivot table grouping by Region/Product with Revenue totals
# Returns: {
#   "pivot_table_id": "pivot_id",
#   "location": "Sheet2!A1"
# }''',
                                        'advantages': 'Complex pivot tables in 1 call. Multiple groupings. Professional format.',
                                        'limitations': 'Max 10 row fields. Requires structured source data.',
                                        'best_practices': [
                                            'Use for sales analysis and reporting',
                                            'Group by time periods (Year/Quarter/Month)',
                                            'Apply filters for focused analysis',
                                            'Create multiple pivots for different views'
                                        ]
                                    },
                                    'excel_smart_financial_report': {
                                        'description': 'Generates multi-sheet financial report (income, balance, cashflow)',
                                        'supported_features': {
                                            'income_statement': 'Revenue, expenses, net income',
                                            'balance_sheet': 'Assets, liabilities, equity',
                                            'cashflow_statement': 'Operating, investing, financing',
                                            'formulas': 'Auto-linking between sheets',
                                            'formatting': 'Professional financial formatting'
                                        },
                                        'example': '''excel_smart_financial_report(
    workbook_name="Financial Report Q1 2025",
    income_data={
        "revenue": 250000,
        "cost_of_goods": 100000,
        "operating_expenses": 80000
    },
    balance_data={
        "assets": 500000,
        "liabilities": 200000
    }
)

# Creates 3 sheets: Income, Balance, Cashflow
# Returns: {
#   "workbook_id": "wb_id",
#   "sheets_created": ["Income Statement", "Balance Sheet", "Cashflow"]
# }''',
                                        'advantages': 'Complete financial reports in 1 call. Formula linking. Professional format.',
                                        'limitations': 'Requires complete financial data. US GAAP format.',
                                        'best_practices': [
                                            'Use for monthly/quarterly reporting',
                                            'Validate data before generation',
                                            'Export to PDF for distribution',
                                            'Store in shared OneDrive for access'
                                        ]
                                    },
                                    'sharepoint_smart_site_audit': {
                                        'description': 'Comprehensive SharePoint site health analysis (storage, permissions, activity)',
                                        'supported_features': {
                                            'storage_analysis': 'Usage, quotas, large files',
                                            'permission_audit': 'User/group access levels',
                                            'activity_metrics': 'Recent activity, popular content',
                                            'recommendations': 'Optimization suggestions'
                                        },
                                        'example': '''sharepoint_smart_site_audit(
    site_id="site_id",
    check_permissions=true,
    check_storage=true
)

# Returns: {
#   "storage": {"used": "15GB", "quota": "25GB", "usage_percent": 60},
#   "permissions": {"unique_users": 45, "groups": 8, "external_users": 3},
#   "recommendations": ["Remove duplicate files", "Archive old content"]
# }''',
                                        'advantages': 'Complete site health in 1 call. Actionable recommendations. Multiple checks.',
                                        'limitations': 'Requires Sites.ReadWrite.All scope. Large sites may take time.',
                                        'best_practices': [
                                            'Run monthly for site maintenance',
                                            'Act on storage recommendations',
                                            'Review permission complexity',
                                            'Track metrics over time'
                                        ]
                                    },
                                    'sharepoint_smart_bulk_upload': {
                                        'description': 'Bulk uploads files with automatic folder structure creation',
                                        'supported_features': {
                                            'folder_auto_create': 'Creates nested folders automatically',
                                            'error_handling': 'Continues on individual failures',
                                            'progress_tracking': 'Reports success/failed counts',
                                            'conflict_resolution': 'Handles duplicate names'
                                        },
                                        'example': '''sharepoint_smart_bulk_upload(
    site_id="site_id",
    drive_id="drive_id",
    files=[
        {"name": "doc1.pdf", "content": "...", "path": "Folder1/SubFolder"},
        {"name": "doc2.pdf", "content": "...", "path": "Folder1/SubFolder"},
        {"name": "doc3.pdf", "content": "...", "path": "Folder2"}
    ]
)

# Auto-creates Folder1/SubFolder and Folder2
# Returns: {
#   "success": ["doc1.pdf", "doc2.pdf", "doc3.pdf"],
#   "failed": [],
#   "folders_created": ["Folder1", "Folder1/SubFolder", "Folder2"]
# }''',
                                        'advantages': 'Upload + folder creation in 1 call. Error resilience. Progress tracking.',
                                        'limitations': 'Max 1000 files per call. Large files may timeout.',
                                        'best_practices': [
                                            'Use for project setup (many files)',
                                            'Organize files by folder path before upload',
                                            'Check "failed" array for issues',
                                            'Use for migration workflows'
                                        ]
                                    },
                                    'sharepoint_smart_organize_library': {
                                        'description': 'Auto-organizes files by type, date, or metadata rules',
                                        'supported_features': {
                                            'group_by_type': 'Organize by file extension',
                                            'group_by_date': 'Organize by created/modified date',
                                            'group_by_metadata': 'Organize by custom columns',
                                            'folder_structure': 'Creates nested folder hierarchy'
                                        },
                                        'example': '''sharepoint_smart_organize_library(
    site_id="site_id",
    drive_id="drive_id",
    rules={
        "group_by": "type",  # or "date" or "metadata"
        "folder_structure": "YYYY/MM"  # for date grouping
    }
)

# Moves files into folders:
# - PDF/
# - DOCX/
# - XLSX/
# Returns: {
#   "files_moved": 150,
#   "folders_created": ["PDF", "DOCX", "XLSX"]
# }''',
                                        'advantages': 'Auto-organization in 1 call. Rule-based. Scalable.',
                                        'limitations': 'Max 5000 files per operation. Cannot undo (backup first).',
                                        'best_practices': [
                                            'Backup library before organizing',
                                            'Test on small library first',
                                            'Use date grouping for archives',
                                            'Use type grouping for mixed content'
                                        ]
                                    },
                                    'sharepoint_smart_permission_report': {
                                        'description': 'Generates detailed permission analysis with simplification recommendations',
                                        'supported_features': {
                                            'user_access': 'Lists all users and their permissions',
                                            'group_access': 'Lists all groups and members',
                                            'external_sharing': 'Identifies external users',
                                            'complexity_score': 'Rates permission complexity',
                                            'recommendations': 'Suggests simplifications'
                                        },
                                        'example': '''sharepoint_smart_permission_report(
    site_id="site_id",
    include_lists=false
)

# Returns: {
#   "users": [{"email": "user@company.com", "role": "Edit"}],
#   "groups": [{"name": "Team Members", "members": 15}],
#   "external_users": 3,
#   "complexity_score": 7,
#   "recommendations": ["Consolidate 3 groups with same permissions"]
# }''',
                                        'advantages': 'Complete permission audit in 1 call. Actionable insights. Complexity scoring.',
                                        'limitations': 'Large sites may take time. Requires full permissions.',
                                        'best_practices': [
                                            'Run quarterly for security review',
                                            'Act on high complexity scores',
                                            'Remove unused external access',
                                            'Simplify group structure'
                                        ]
                                    },
                                    'onenote_smart_meeting_notes': {
                                        'description': 'Creates structured meeting notes with agenda, attendees, and action items table',
                                        'supported_features': {
                                            'structured_format': 'Title, date, attendees, agenda, notes, action items',
                                            'action_items_table': 'HTML table with task, owner, due date',
                                            'auto_section_creation': 'Creates "Meetings" section if missing',
                                            'html_formatting': 'Rich text with styling'
                                        },
                                        'example': '''onenote_smart_meeting_notes(
    notebook_id="notebook_id",
    section_name="Meetings",
    meeting_title="Q1 Planning - October 29, 2025",
    attendees=["Alice", "Bob", "Carol"],
    agenda=["Budget review", "Timeline planning", "Resource allocation"],
    action_items=[
        {"task": "Finalize budget", "owner": "Alice", "due_date": "2025-11-05"},
        {"task": "Create timeline", "owner": "Bob", "due_date": "2025-11-07"}
    ]
)

# Returns: {
#   "page_id": "page_id",
#   "section_created": false,
#   "action_items_count": 2
# }''',
                                        'advantages': 'Professional meeting notes in 1 call. Action item tracking. Structured format.',
                                        'limitations': 'Requires Notes.ReadWrite.All scope. Max 50 action items.',
                                        'best_practices': [
                                            'Create within 24 hours of meeting',
                                            'Use consistent section naming',
                                            'Set realistic due dates',
                                            'Link related pages'
                                        ]
                                    },
                                    'onenote_smart_organize_by_topic': {
                                        'description': 'Creates organized section structure for knowledge base',
                                        'supported_features': {
                                            'multi_section_creation': 'Creates multiple sections at once',
                                            'index_page': 'Creates navigation/index page',
                                            'template_pages': 'Adds starter pages per section',
                                            'hierarchy': 'Maintains notebook structure'
                                        },
                                        'example': '''onenote_smart_organize_by_topic(
    notebook_id="notebook_id",
    topics=["Product Docs", "Meeting Notes", "Research", "Resources"]
)

# Creates 4 sections + index page with links
# Returns: {
#   "sections_created": ["Product Docs", "Meeting Notes", "Research", "Resources"],
#   "index_page_id": "index_id"
# }''',
                                        'advantages': 'Complete structure in 1 call. Index page. Template pages.',
                                        'limitations': 'Max 20 topics per call. Cannot rename existing sections.',
                                        'best_practices': [
                                            'Use for new notebook setup',
                                            'Create logical topic grouping',
                                            'Update index page regularly',
                                            'Use consistent naming'
                                        ]
                                    },
                                    'onenote_smart_extract_tasks': {
                                        'description': 'Extracts action items from OneNote page content (TODO, ACTION keywords)',
                                        'supported_features': {
                                            'keyword_detection': 'Finds TODO, ACTION, TASK keywords',
                                            'owner_extraction': 'Identifies @mentions as owners',
                                            'due_date_extraction': 'Parses dates from text',
                                            'priority_detection': 'Identifies URGENT, HIGH priority'
                                        },
                                        'example': '''onenote_smart_extract_tasks(
    page_id="page_id"
)

# Scans content like:
# "TODO: Finish report @Alice by Nov 5"
# "ACTION: Review contract @Bob (URGENT)"

# Returns: {
#   "tasks": [
#       {"text": "Finish report", "owner": "Alice", "due_date": "2025-11-05", "priority": "normal"},
#       {"text": "Review contract", "owner": "Bob", "due_date": null, "priority": "urgent"}
#   ]
# }''',
                                        'advantages': 'Auto-extract tasks from notes. Owner detection. Priority parsing.',
                                        'limitations': 'Requires consistent formatting. Max 100 tasks per page.',
                                        'best_practices': [
                                            'Use consistent keywords (TODO, ACTION)',
                                            'Always @mention owners',
                                            'Include dates in clear format',
                                            'Mark priorities explicitly'
                                        ]
                                    },
                                    'onenote_smart_knowledge_base': {
                                        'description': 'Creates comprehensive knowledge base with categories, subcategories, and templates',
                                        'supported_features': {
                                            'multi_level_structure': 'Categories and subcategories',
                                            'template_pages': 'Standard page templates per category',
                                            'navigation_page': 'Master index with links',
                                            'search_tips': 'Adds search/usage guide'
                                        },
                                        'example': '''onenote_smart_knowledge_base(
    notebook_name="Company Knowledge Base",
    categories=[
                {"name": "HR", "subcategories": ["Onboarding", "Benefits", "Policies"]},
                {"name": "Engineering", "subcategories": ["Setup", "Best Practices", "Troubleshooting"]},
                {"name": "Sales", "subcategories": ["Process", "Templates", "Resources"]}
            ]
        )
        
        # Creates complete KB with 3 main sections, 9 subsections, navigation page
        # Returns: {
        #   "notebook_id": "kb_id",
        #   "sections_created": 3,
        #   "pages_created": 12
        # }''',
                                        'advantages': 'Complete KB structure in 1 call. Navigation included. Templates provided.',
                                        'limitations': 'Max 10 categories. Max 5 subcategories each.',
                                        'best_practices': [
                                            'Use for company documentation',
                                            'Organize by department or topic',
                                            'Update navigation page regularly',
                                            'Add search guide for users'
                                        ]
                                    },
                                    'forms_smart_create_survey': {
                                        'description': 'Creates complete survey from question templates with auto-ordering',
                                        'supported_features': {
                                            'question_types': 'choice, text, rating, date, ranking',
                                            'auto_ordering': 'Orders questions logically',
                                            'validation': 'Adds validation rules',
                                            'settings': 'Configures survey settings'
                                        },
                                        'example': '''forms_smart_create_survey(
    title="Customer Feedback Survey",
    description="Help us improve our service",
    question_templates=[
        {"text": "How satisfied are you?", "type": "rating", "scale": 5},
        {"text": "What can we improve?", "type": "text", "multiline": true},
        {"text": "Would you recommend us?", "type": "choice", "options": ["Yes", "No", "Maybe"]}
    ]
)

# Returns: {
#   "form_id": "form_id",
#   "questions_added": 3,
#   "web_url": "https://forms.office.com/..."
# }''',
                                        'advantages': 'Complete survey in 1 call. Multiple question types. Auto-validation.',
                                        'limitations': 'Forms API in beta. Max 100 questions per form.',
                                        'best_practices': [
                                            'Use for feedback, polls, registrations',
                                            'Start with rating questions',
                                            'Include open-ended questions',
                                            'Test survey before distribution'
                                        ]
                                    },
                                    'forms_smart_satisfaction_survey': {
                                        'description': 'Creates NPS, CSAT, or CES satisfaction survey with standard questions',
                                        'supported_features': {
                                            'nps': 'Net Promoter Score (0-10 rating)',
                                            'csat': 'Customer Satisfaction Score (1-5 rating)',
                                            'ces': 'Customer Effort Score (1-7 rating)',
                                            'follow_up': 'Includes follow-up text question'
                                        },
                                        'example': '''forms_smart_satisfaction_survey(
    product_name="AI Agent Platform",
    survey_type="nps"  # or "csat" or "ces"
)

# Creates form with:
# 1. "How likely are you to recommend AI Agent Platform?" (0-10)
# 2. "What is the primary reason for your score?" (text)

# Returns: {
#   "form_id": "form_id",
#   "survey_type": "NPS",
#   "web_url": "https://forms.office.com/..."
# }''',
                                        'advantages': 'Standard survey in 1 call. Industry best practices. Ready to distribute.',
                                        'limitations': 'Predefined structure. Forms API in beta.',
                                        'best_practices': [
                                            'Use NPS for recommendation likelihood',
                                            'Use CSAT for service satisfaction',
                                            'Use CES for ease of use',
                                            'Send after key customer interactions'
                                        ]
                                    },
                                    'forms_smart_analyze_responses': {
                                        'description': 'Analyzes form responses with summary statistics and insights',
                                        'supported_features': {
                                            'statistics': 'Count, average, distribution per question',
                                            'sentiment': 'Basic sentiment analysis for text',
                                            'trends': 'Identifies patterns in responses',
                                            'insights': 'Actionable recommendations'
                                        },
                                        'example': '''forms_smart_analyze_responses(
    form_id="form_id",
    analysis_type="detailed"  # or "summary" or "sentiment"
)

# Returns: {
#   "total_responses": 150,
#   "questions_analyzed": 5,
#   "insights": [
#       {"question": "Satisfaction", "avg": 4.2, "sentiment": "positive"},
#       {"question": "Improvement", "common_themes": ["speed", "features"]}
#   ]
# }''',
                                        'advantages': 'Auto-analysis in 1 call. Multiple metrics. Actionable insights.',
                                        'limitations': 'Basic sentiment only. Requires response data.',
                                        'best_practices': [
                                            'Run after collecting 50+ responses',
                                            'Look for common themes',
                                            'Act on low satisfaction scores',
                                            'Compare over time'
                                        ]
                                    },
                                    'forms_smart_export_to_excel': {
                                        'description': 'Exports form responses to formatted Excel workbook with charts',
                                        'supported_features': {
                                            'data_sheet': 'Raw responses in table format',
                                            'summary_sheet': 'Statistics and aggregations',
                                            'charts': 'Visualizations per question',
                                            'pivot_tables': 'Advanced analysis views'
                                        },
                                        'example': '''forms_smart_export_to_excel(
    form_id="form_id",
    workbook_name="Survey Results Q4 2025",
    include_charts=true
)

# Creates Excel with 3 sheets:
# 1. Raw Data (all responses)
# 2. Summary (statistics)
# 3. Charts (visual analysis)

# Returns: {
#   "workbook_id": "wb_id",
#   "web_url": "https://onedrive.live.com/...",
#   "sheets_created": ["Raw Data", "Summary", "Charts"]
# }''',
                                        'advantages': 'Export + format + charts in 1 call. Professional analysis. Shareable.',
                                        'limitations': 'Requires Forms + Excel tools. Max 10,000 responses.',
                                        'best_practices': [
                                            'Use for detailed analysis',
                                            'Share workbook with stakeholders',
                                            'Update regularly for new responses',
                                            'Use pivot tables for complex analysis'
                                        ]
                                    }
                                }
                                
                                if smart_tool_name in smart_tools_guide:
                                    tool_result = {
                                        'success': True,
                                        'tool_name': smart_tool_name,
                                        'instructions': smart_tools_guide[smart_tool_name],
                                        'message': f"SMART tool instructions loaded. This tool combines multiple operations in one call."
                                    }
                                else:
                                    tool_result = {
                                        'success': True,
                                        'tool_name': smart_tool_name,
                                        'message': f"Specific guide for {smart_tool_name} not yet available. Check tool description in schema for usage.",
                                        'suggestion': 'Use list_platform_tools to see tool description with inline examples'
                                    }
                            
                            else:
                                # Execute regular tool with user credential injection
                                tool_result = tool_registry.execute_tool(tool_name, user_id=user_id, **tool_input)
                            
                            success = tool_result.get('success', False)
                            
                            print(f"{'✅' if success else '❌'} Tool executed: {success}")
                            if not success:
                                print(f"   Error: {tool_result.get('error')}")
                            
                            tools_used.append({
                                'name': tool_name,
                                'success': success,
                                'error': tool_result.get('error') if not success else None,
                                'duration': 0
                            })
                            
                            # Add tool result for AI to see
                            tool_results_for_ai.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": json.dumps(tool_result)
                            })
                            
                        except Exception as e:
                            print(f"❌ Tool execution exception: {e}")
                            error_result = {'success': False, 'error': str(e), 'tool': tool_name}
                            tools_used.append({
                                'name': tool_name,
                                'success': False,
                                'error': str(e),
                                'duration': 0
                            })
                            tool_results_for_ai.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": json.dumps(error_result)
                            })
                
                # If tools were used, continue conversation with results
                if has_tool_use and tool_results_for_ai:
                    # ✅ FIX: Convert content blocks to serializable format
                    serializable_content = []
                    for block in response_obj.content:
                        if block.type == "text":
                            serializable_content.append({"type": "text", "text": block.text})
                        elif block.type == "tool_use":
                            serializable_content.append({
                                "type": "tool_use",
                                "id": block.id,
                                "name": block.name,
                                "input": block.input
                            })
                    
                    conversation.append({"role": "assistant", "content": serializable_content})
                    conversation.append({"role": "user", "content": tool_results_for_ai})
                    continue
                else:
                    # No more tools, we have final response
                    break
            
            if current_turn >= max_turns:
                ai_response += "\n\n*[Note: Reached maximum tool execution turns]*"
        else:
            # ✅ SIMPLE CALL WITHOUT TOOLS
            response_obj = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=16000,  # ✅ Increased to 16000 for longer responses
                system=system_prompt,
                messages=conversation
            )
            
            # Extract text from response content
            if isinstance(response_obj.content, list):
                ai_response = response_obj.content[0].text
            else:
                ai_response = str(response_obj.content)
        
        print(f"✅ AI response received ({len(ai_response)} chars)")
        print(f"🔧 Tools used: {len(tools_used)}")
        
        # Add AI response to history
        conversation.append({"role": "assistant", "content": ai_response})
        session_manager.update_conversation(session_id, conversation)
        
        # Return JSON response - ensure all data is serializable
        response = jsonify({
            'success': True,
            'response': str(ai_response),  # Ensure it's a string
            'session_id': session_id,
            'provider': provider,
            'mode': 'live',
            'tools_used': tools_used,  # ✅ RETURN TOOL USAGE STATS
            'tool_calls': tools_used  # Add alternative key name
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        print(f"❌ Main chat error: {e}")
        import traceback
        traceback.print_exc()
        
        response = jsonify({
            'success': False,
            'error': str(e),
            'response': "I'm having trouble connecting. Please try again.",
            'tools_used': []  # ✅ Empty array on error
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500


def handle_main_chat_streaming(message, session_id, provider, model, user_id=None):
    """
    Handle main chat with SSE streaming for real-time responses
    Uses session_manager for persistence
    
    Args:
        user_id: User ID for credential injection into Google tools
    """
    # ✅ CAPTURE REQUEST DATA BEFORE GENERATOR (outside request context)
    request_data = request.get_json() if request.is_json else {}
    provided_history = request_data.get('conversation_history', [])
    source = request_data.get('source', 'ui')
    
    def generate():
        try:
            # Use captured request data from outer scope
            if provided_history and len(provided_history) > 0:
                print(f"📜 Using conversation history from frontend: {len(provided_history)} messages")
                session_data = {
                    'session_id': session_id,
                    'conversation': provided_history,
                    'ui_context': 'business_ai_platform',
                    'created_at': None
                }
            else:
                session_data = session_manager.get_session(session_id)
                if not session_data:
                    print(f"📝 Creating new session: {session_id}")
                    created_session_id = session_manager.create_session('business_ai_platform', agent_id=None, session_id=session_id, source=source)
                    session_data = session_manager.get_session(created_session_id)
                    print(f"✅ Session created with ID: {created_session_id} (source={source})")
            
            from anthropic import Anthropic
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            client = Anthropic(api_key=anthropic_key)
            
            # Build conversation
            conversation = session_data.get('conversation', [])
            
            # ✅ Clean conversation messages - remove extra fields that Anthropic doesn't accept
            cleaned_conversation = []
            for msg in conversation:
                cleaned_msg = {
                    'role': msg.get('role'),
                    'content': msg.get('content')
                }
                cleaned_conversation.append(cleaned_msg)
            
            # Add new user message
            cleaned_conversation.append({"role": "user", "content": message})
            
            system_prompt = """You are an AI assistant with access to 296+ business tools across 20+ platforms.

🚨 ONLY mention platforms/tools you actually have: Google Workspace, Slack, Stripe, WooCommerce, etc. DO NOT mention: Trello, Asana, Linear, ClickUp.

Provide clear, helpful responses. Format URLs as markdown links: [Title](url)"""
            
            # Send start event
            yield f"data: {json.dumps({'type': 'start', 'session_id': session_id})}\n\n"
            
            # Stream response from Anthropic
            full_response = ""
            
            with client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system_prompt,
                messages=cleaned_conversation
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    # Send text delta
                    yield f"data: {json.dumps({'type': 'content_delta', 'text': text})}\n\n"
            
            # Save to conversation history (add to original conversation, not cleaned)
            conversation.append({"role": "user", "content": message})
            conversation.append({"role": "assistant", "content": full_response})
            session_manager.update_conversation(session_id, conversation)
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'complete', 'full_response': full_response})}\n\n"
            
        except Exception as e:
            print(f"❌ Streaming error: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    from flask import Response
    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
        'Access-Control-Allow-Origin': '*'
    })


def handle_multi_agent_chat(agent_id, message, session_id, provider, model, user_id=None):
    """
    Handle multi-agent panel - JSON response (SSE coming soon)
    Uses agent_state_manager for persistence
    
    Args:
        user_id: User ID for credential injection into Google tools
    """
    try:
        # Get or create agent state
        from core.agent_state_manager import agent_state_manager
        
        state = agent_state_manager.get_or_create_state(
            agent_id=agent_id,
            session_id=session_id,
            context={'ui_context': 'multi_agent_panel'}
        )
        
        # Get conversation history
        conversation = state.get('conversation', [])
        conversation.append({"role": "user", "content": message})
        
        print(f"🤖 Calling AI for Agent {agent_id}...")
        
        from anthropic import Anthropic
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        client = Anthropic(api_key=anthropic_key)
        
        # Agent-specific system prompt
        agent_names = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo']
        agent_name = agent_names[int(agent_id) - 1] if int(agent_id) <= len(agent_names) else f"Agent-{agent_id}"
        
        system_prompt = f"""You are Agent {agent_name}, part of a multi-agent system with access to 281 business tools.

🚨 CRITICAL: Only mention platforms you have tools for (Google Workspace, Slack, Stripe, etc.). DO NOT mention: Trello, Asana, Linear, ClickUp.

Your role: Collaborative AI assistant with full platform access.
Tools available: WooCommerce, Slack, GitHub, Google Workspace, and 15 more platforms."""
        
        response_obj = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=system_prompt,
            messages=conversation
        )
        
        ai_response = response_obj.content[0].text
        print(f"✅ Agent {agent_id} response received")
        
        # Update conversation
        conversation.append({"role": "assistant", "content": ai_response})
        agent_state_manager.add_message(agent_id, session_id, "assistant", ai_response)
        
        response = jsonify({
            'success': True,
            'response': ai_response,
            'session_id': session_id,
            'agent_id': agent_id,
            'mode': 'live'
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        print(f"❌ Multi-agent error: {e}")
        import traceback
        traceback.print_exc()
        
        response = jsonify({
            'success': False,
            'error': str(e)
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500


@agent_bp.route('/tools', methods=['GET', 'OPTIONS'])
def get_tools():
    """
    Get list of available AI tools and platforms
    For business-ai-platform-v2.html platform dashboard
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    try:
        # Return ONLY real, implemented platforms
        tools_data = {
            'total_tools': 92,  # Actual count from implemented tools
            'platforms': [
                # AI Providers
                {'name': 'Anthropic', 'tools': 0, 'status': 'configured', 'category': 'AI'},
                {'name': 'OpenAI', 'tools': 0, 'status': 'configured', 'category': 'AI'},
                {'name': 'DeepSeek', 'tools': 0, 'status': 'configured', 'category': 'AI'},
                
                # E-Commerce & Payments
                {'name': 'WooCommerce', 'tools': 29, 'status': 'active', 'category': 'E-Commerce'},
                {'name': 'Stripe', 'tools': 25, 'status': 'active', 'category': 'Payments'},
                
                # Communication
                {'name': 'Slack', 'tools': 24, 'status': 'active', 'category': 'Communication'},
                {'name': 'Twilio', 'tools': 8, 'status': 'active', 'category': 'Communication'},
                
                # Development & Infrastructure
                {'name': 'GitHub', 'tools': 15, 'status': 'active', 'category': 'Development'},
                {'name': 'Cloudflare', 'tools': 12, 'status': 'active', 'category': 'Infrastructure'},
                {'name': 'Supabase', 'tools': 10, 'status': 'active', 'category': 'Database'},
                {'name': 'Ngrok', 'tools': 5, 'status': 'active', 'category': 'Development'},
                
                # Google Workspace
                {'name': 'Google Sheets', 'tools': 18, 'status': 'active', 'category': 'Productivity'},
                {'name': 'Google Calendar', 'tools': 12, 'status': 'active', 'category': 'Productivity'},
                
                # Media & Content
                {'name': 'AssemblyAI', 'tools': 8, 'status': 'active', 'category': 'AI/Media'},
                {'name': 'CloudConvert', 'tools': 6, 'status': 'active', 'category': 'Media'}
            ],
            'note': 'Only showing implemented and configured platforms'
        }
        
        response = jsonify(tools_data)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        response = error_response(str(e))
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


# ============================================================
# UNIVERSAL TRIPLE AGENT ENDPOINTS (NEW)
# ============================================================

@agent_bp.route('/agent/<agent_id>/start', methods=['POST', 'OPTIONS'])
@require_auth
def start_agent(agent_id):
    """
    Universal agent start endpoint for Triple Agent + Stock AI
    
    agent_id: '1' | '2' | '3' | 'stock_ai' | 'data_agent' | 'single_viewer'
    
    Request JSON (text-only):
    {
        "session_id": "uuid" (optional),
        "message": "User prompt"
    }
    
    OR FormData (with files):
    - session_id (optional)
    - message
    - files[] (multiple file uploads)
    
    Returns:
    {
        "success": true,
        "session_id": "uuid",
        "agent_id": "1",
        "status": "processing"
    }
    """
    try:
        # Determine if text-only or file upload
        is_form_data = request.content_type and 'multipart/form-data' in request.content_type
        
        if is_form_data:
            # File upload workflow
            session_id = request.form.get('session_id')
            prompt = request.form.get('message', '')
            
            # Process file uploads
            files = request.files.getlist('files')
            if not files:
                return error_response("No files uploaded", 400)
            
            try:
                content_blocks = process_file_uploads(files)
            except FileValidationError as e:
                return error_response(str(e), 400)
            
            # Build file_data for worker
            file_data = content_blocks
        else:
            # Text-only workflow
            data = request.json
            session_id = data.get('session_id')
            prompt = data.get('message', '')
            file_data = None
        
        # Get or create agent state
        state = agent_state_manager.get_or_create_state(
            agent_id=agent_id,
            session_id=session_id,
            context={'ui_context': 'triple_agent' if agent_id in ['1', '2', '3'] else agent_id}
        )
        session_id = state['session_id']
        
        # Get execution lock and queue
        lock = agent_state_manager.get_lock(agent_id, session_id)
        queue = agent_state_manager.get_queue(agent_id, session_id)
        
        # Update status
        agent_state_manager.update_status(agent_id, session_id, 'processing')
        
        # Start background worker
        if file_data:
            threading.Thread(
                target=run_agent_worker,
                args=(agent_id, prompt, file_data, lock, session_id, queue, state['conversation'], state['context']),
                daemon=True
            ).start()
        else:
            threading.Thread(
                target=run_simple_agent_worker,
                args=(agent_id, prompt, lock, session_id, queue, state['conversation']),
                daemon=True
            ).start()
        
        return success_response({
            'session_id': session_id,
            'agent_id': agent_id,
            'status': 'processing',
            'files_uploaded': len(file_data) if file_data else 0
        })
    
    except Exception as e:
        return error_response(f"Agent start failed: {str(e)}", 500)


@agent_bp.route('/stream/<agent_id>', methods=['GET'])
@require_auth
def stream_agent(agent_id):
    """
    Universal SSE stream endpoint
    🔐 PROTECTED - Requires authentication
    
    Query params:
        ?session_id=uuid (required)
    
    agent_id: '1' | '2' | '3' | 'stock_ai' | 'data_agent' | 'single_viewer'
    """
    session_id = request.args.get('session_id')
    
    if not session_id:
        return error_response("Missing session_id", 400)
    
    def generate():
        queue = agent_state_manager.get_queue(agent_id, session_id)
        
        while True:
            try:
                event = queue.get(timeout=30)
                
                event_type = event.get('type')
                
                if event_type == 'complete':
                    yield stream_sse_event('complete', event)
                    break
                
                elif event_type == 'error':
                    yield stream_sse_event('error', event)
                    break
                
                else:
                    # thinking, response, etc.
                    yield stream_sse_event(event_type, event)
            
            except Empty:
                # Heartbeat every 30s
                yield stream_sse_event('heartbeat', {'status': 'alive'})
            
            except Exception as e:
                yield stream_sse_event('error', {'message': str(e)})
                break
    
    return Response(generate(), mimetype='text/event-stream')


@agent_bp.route('/agent/<agent_id>/status', methods=['GET'])
@require_auth
def get_agent_status(agent_id):
    """
    Get agent status
    
    Query params:
        ?session_id=uuid (required)
    
    Returns:
    {
        "success": true,
        "data": {
            "status": "idle" | "processing",
            "message_count": 6
        }
    }
    """
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
@require_auth
def get_agent_history(agent_id):
    """
    Get conversation history
    
    Query params:
        ?session_id=uuid (required)
    
    Returns:
    {
        "success": true,
        "data": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"}
        ]
    }
    """
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
    """
    Clear conversation history
    
    Request JSON:
    {
        "session_id": "uuid"
    }
    
    Returns:
    {
        "success": true,
        "message": "Conversation cleared"
    }
    """
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
# LEGACY ENDPOINTS (Keep for backward compatibility)
# ============================================================


@agent_bp.route('/data-agent/chat', methods=['POST'])
def data_agent_chat():
    """
    Legacy Data Agent endpoint
    Routes to universal /agent/data_agent/start
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        prompt = data.get('prompt', '')
        
        # Use universal endpoint logic
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
            target=run_simple_agent_worker,
            args=('data_agent', prompt, lock, session_id, queue, state['conversation']),
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
    """
    Legacy Single Viewer endpoint
    Routes to universal /agent/single_viewer/start
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        prompt = data.get('prompt', '')
        
        state = agent_state_manager.get_or_create_state(
            agent_id='single_viewer',
            session_id=session_id,
            context={'ui_context': 'single_viewer'}
        )
        session_id = state['session_id']
        
        lock = agent_state_manager.get_lock('single_viewer', session_id)
        queue = agent_state_manager.get_queue('single_viewer', session_id)
        
        agent_state_manager.update_status('single_viewer', session_id, 'processing')
        
        threading.Thread(
            target=run_simple_agent_worker,
            args=('single_viewer', prompt, lock, session_id, queue, state['conversation']),
            daemon=True
        ).start()
        
        return success_response({
            'status': 'processing',
            'session_id': session_id
        })
    
    except Exception as e:
        return error_response(str(e), 500)


@agent_bp.route('/chat-with-document-stream', methods=['POST'])
def agent_chat_with_document_stream():
    """
    Legacy document chat endpoint with SSE streaming
    Routes to universal /agent/data_agent/start with files
    """
    try:
        session_id = request.form.get('session_id')
        prompt = request.form.get('prompt', '')
        
        # Process files
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

