"""
Unified AI Client - Multi-Provider Support
Supports: Anthropic Claude, DeepSeek, OpenAI GPT, MiniMax

This client wraps all AI providers with a unified interface
so routes can switch providers without code changes.

MiniMax is exposed via an Anthropic-compatible endpoint
(https://api.minimax.io/anthropic), so we re-use the Anthropic SDK
with a custom base_url.  This gives us thinking blocks, tool use, and
the same content-block shape as Claude with no extra translation layer.
"""

import httpx
from anthropic import Anthropic
import openai
import requests
import json
from typing import Dict, List, Optional, Callable, Any, Literal
from pathlib import Path
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Quote_Calculator', 'AI_Quote_Agent', 'core'))

# TODO: Uncomment when tool_use_agent is available
# from tool_use_agent import ToolUseAgent

# REAL Tool Execution using Registry_V3
class ToolUseAgent:
    """
    Real tool execution agent using Registry_V3
    Executes tools from the 584-tool registry
    """
    def __init__(self, config_path=None):
        self.config_path = config_path
        
        # Import and initialize registry
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))
        from registry_v3 import get_registry
        self.registry = get_registry()
        self.tools = list(self.registry.tools.keys())
        
        print(f"[ToolUseAgent] Initialized with {len(self.tools)} tools from registry_v3")
    
    def _get_tool_definitions(self):
        """Get tool definitions in Anthropic format"""
        return self.registry.get_anthropic_tools()
    
    def execute_tool(self, tool_name, tool_input):
        """Execute a tool from the registry"""
        try:
            print(f"[ToolUseAgent] Executing tool: {tool_name}")
            print(f"[ToolUseAgent] Input: {json.dumps(tool_input, indent=2)}")
            
            result = self.registry.execute_tool(tool_name=tool_name, **tool_input)
            
            print(f"[ToolUseAgent] Result: {str(result)[:200]}...")
            return result
            
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            print(f"[ToolUseAgent] ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            return {"error": error_msg, "tool": tool_name}


class UnifiedAIClient:
    """
    Multi-provider AI client with unified interface

    Supported Providers:
    - Anthropic (Claude Sonnet, Haiku)
    - DeepSeek (deepseek-chat, deepseek-reasoner)
    - OpenAI (GPT-4o, GPT-4o-mini)
    - MiniMax (MiniMax-M3, MiniMax-M2.7, MiniMax-M2.5, MiniMax-M2.1, MiniMax-M2, M2-her)

    Features:
    - Single interface for all providers
    - SSE streaming for all providers
    - System prompt routing by UI context
    - Server-side tool execution
    - Same SSE event format (NO UI CHANGES)
    """

    def __init__(self, config_path: str):
        """
        Initialize multi-provider AI client

        Args:
            config_path: Path to database-config.json
        """
        # Load config (handle UTF-8 BOM)
        with open(config_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            if not content or len(content) == 0:
                raise ValueError(f"Config file is empty: {config_path}")
            self.config = json.loads(content)

        # Initialize all providers
        self._init_anthropic()
        self._init_deepseek()
        self._init_openai()
        self._init_MiniMax()

        # Initialize tool use agent (server-side tools)
        self.tool_agent = ToolUseAgent(config_path)

        print(f"[UnifiedAIClient] Initialized with providers:")
        print(f"  - Anthropic: {self.anthropic_model}")
        print(f"  - DeepSeek: {self.deepseek_model}")
        print(f"  - OpenAI: {self.openai_model}")
        print(f"  - MiniMax: {self.MiniMax_model}")
    
    def _get_api_key_from_supabase(self, platform='anthropic', user_id=1):
        """
        Fetch API key from Supabase user_platform_credentials table
        
        Args:
            platform: 'anthropic', 'openai', 'deepseek', etc.
            user_id: User ID (default 1 for system account)
        
        Returns:
            API key string or None if not found
        """
        try:
            # Only attempt Supabase query on Render deployment
            supabase_url = os.environ.get('SUPABASE_DB_URL_POOLER')
            if not supabase_url:
                return None  # Local development - use environment variables
            
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            conn = psycopg2.connect(supabase_url, cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            
            query = """
                SELECT credential_value, credentials
                FROM ai_infrastructure.user_platform_credentials
                WHERE user_id = %s AND platform = %s AND is_active = true
                ORDER BY updated_at DESC
                LIMIT 1
            """
            cursor.execute(query, (user_id, platform))
            row = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if row:
                print(f"[UnifiedAIClient] ✅ Fetched {platform} API key from Supabase for user {user_id}")
                return row['credential_value']
            else:
                print(f"[UnifiedAIClient] ⚠️  No {platform} credentials found in Supabase for user {user_id}")
                return None
                
        except Exception as e:
            print(f"[UnifiedAIClient] ⚠️  Failed to fetch {platform} key from Supabase: {e}")
            return None
    
    def _init_anthropic(self):
        """Initialize Anthropic Claude client with increased timeout"""
        # Priority: Supabase → Environment Variable → Config File
        api_key_supabase = self._get_api_key_from_supabase('anthropic')
        api_key_env = os.environ.get('ANTHROPIC_API_KEY')
        api_key_config = self.config.get('AI', {}).get('AnthropicAPIKey', '')
        
        # Use first available key
        api_key = api_key_supabase or api_key_env or api_key_config
        
        # Log which source was used (show first 20 and last 8 chars for verification)
        if api_key:
            key_display = f"{api_key[:20]}...{api_key[-8:]}" if len(api_key) > 28 else api_key
            if api_key == api_key_supabase:
                print(f"[UnifiedAIClient] 🔐 Using Anthropic key from SUPABASE (key: {key_display})")
            elif api_key == api_key_env:
                print(f"[UnifiedAIClient] 🔐 Using Anthropic key from ENVIRONMENT (key: {key_display})")
            else:
                print(f"[UnifiedAIClient] 🔐 Using Anthropic key from CONFIG FILE (key: {key_display})")
            
            # Use granular httpx.Timeout: short connect, long read for extended-thinking responses
            # Anthropic recommends ≥600 s read timeout for long requests with thinking enabled
            _anthropic_timeout = httpx.Timeout(connect=30.0, read=600.0, write=60.0, pool=10.0)
            self.anthropic_client = Anthropic(
                api_key=api_key,
                timeout=_anthropic_timeout,
                max_retries=3   # Retry up to 3 times on network errors
            )
            print("[UnifiedAIClient] Anthropic client initialized with 600s read timeout, 3 max retries")
        else:
            self.anthropic_client = None
            print("⚠️  Warning: No Anthropic API key found. Check Supabase credentials or set ANTHROPIC_API_KEY.")
        self.anthropic_model = self.config.get('AI', {}).get('Model', 'claude-sonnet-4-5-20250929')
    
    def _init_deepseek(self):
        """Initialize DeepSeek client"""
        # Try environment variable first, then config file
        self.deepseek_api_key = os.environ.get('DEEPSEEK_API_KEY') or self.config.get('AI', {}).get('DeepSeekAPIKey', '')
        self.deepseek_model = self.config.get('AI', {}).get('DeepSeekModel', 'deepseek-chat')
        self.deepseek_base_url = "https://api.deepseek.com/v1"
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        # Try environment variable first, then config file
        openai_key = os.environ.get('OPENAI_API_KEY') or self.config.get('AI', {}).get('OpenAIAPIKey', '')
        if openai_key:
            openai.api_key = openai_key
        self.openai_model = self.config.get('AI', {}).get('OpenAIModel', 'gpt-4o-mini')

    def _init_MiniMax(self):
        """Initialize MiniMax client (uses Anthropic SDK with custom base_url).

        MiniMax exposes an Anthropic-compatible endpoint at
        https://api.minimax.io/anthropic, so we re-use the Anthropic SDK
        pointing at that base URL.  This gives us native support for
        thinking blocks, tool use, and the same content-block shape as Claude
        without any translation layer.
        """
        # Priority: Supabase → Environment Variable → Config File
        api_key_supabase = self._get_api_key_from_supabase('MiniMax')
        api_key_env = os.environ.get('MINIMAX_API_KEY')
        api_key_config = self.config.get('AI', {}).get('MiniMaxAPIKey', '')

        api_key = api_key_supabase or api_key_env or api_key_config

        # Default base URL (Anthropic-compatible recommended path)
        self.MiniMax_base_url = (
            os.environ.get('MINIMAX_BASE_URL')
            or self.config.get('AI', {}).get('MiniMaxBaseURL', '')
            or 'https://api.minimax.io/anthropic'
        )

        if api_key:
            key_display = f"{api_key[:20]}...{api_key[-8:]}" if len(api_key) > 28 else api_key
            if api_key == api_key_supabase:
                print(f"[UnifiedAIClient] 🔐 Using MiniMax key from SUPABASE (key: {key_display})")
            elif api_key == api_key_env:
                print(f"[UnifiedAIClient] 🔐 Using MiniMax key from ENVIRONMENT (key: {key_display})")
            else:
                print(f"[UnifiedAIClient] 🔐 Using MiniMax key from CONFIG FILE (key: {key_display})")

            # Re-use the Anthropic SDK pointing at MiniMax's Anthropic-compatible
            # endpoint.  M3 supports thinking + tool use natively.
            _MiniMax_timeout = httpx.Timeout(connect=30.0, read=600.0, write=60.0, pool=10.0)
            self.MiniMax_client = Anthropic(
                api_key=api_key,
                base_url=self.MiniMax_base_url,
                timeout=_MiniMax_timeout,
                max_retries=3,
            )
            print(f"[UnifiedAIClient] MiniMax client initialized (base_url={self.MiniMax_base_url})")
        else:
            self.MiniMax_client = None
            print("⚠️  Warning: No MiniMax API key found. Check Supabase credentials or set MINIMAX_API_KEY.")
        self.MiniMax_model = self.config.get('AI', {}).get('MiniMaxModel', 'MiniMax-M3')
    
    def _get_tool_usage_instructions(self) -> str:
        """Load tool usage instructions from prompt file"""
        try:
            prompt_path = Path(__file__).parent.parent / 'prompts' / 'tool_usage_system_prompt.md'
            if prompt_path.exists():
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Warning: Could not load tool usage prompt: {e}")
        
        # Fallback instructions with server tools documentation
        return """You have access to 584+ tools across multiple platforms including Google Workspace, Microsoft 365, and business tools. ALWAYS use these tools to complete user requests. Never say you cannot do something - use the available tools.

CRITICAL - NATURAL LANGUAGE COMMUNICATION:
When communicating with users about tools, ALWAYS use natural, conversational language. NEVER mention internal tool names or technical function names.

FORBIDDEN PHRASES (Never say these):
❌ "I'll call gmail_list_messages"
❌ "I'll execute the tool"
❌ "Running gmail_send_email function"
❌ "Using google_docs_create_document"

REQUIRED PHRASES (Always say these instead):
✅ "I'll check your emails"
✅ "I'll send that email"
✅ "I'll create that document"
✅ "I'll look at your calendar"

NATURAL ACTION VERBS BY CATEGORY:
• Email: "check", "send", "reply to", "forward", "archive", "delete"
• Documents: "create", "update", "review", "edit", "share"
• Calendar: "check", "schedule", "add", "update", "cancel"
• Data: "get", "retrieve", "fetch", "analyze", "calculate"
• Communication: "post", "message", "notify", "call"

EXPORT TRANSLATIONS (When using mode/format/export parameters):
• export="synergy" → "save to your dashboard"
• export="google_doc" → "create a document"
• export="google_sheet" → "add to a spreadsheet"
• mode="summary" → "quick summary"
• mode="detailed" → "detailed breakdown"
• format="markdown" → (don't mention - it's the default)

EXAMPLES OF CORRECT COMMUNICATION:
User: "Check my inbox"
You: "I'll check your emails" (NOT "I'll call gmail_list_messages")

User: "Send an email to john@example.com"
You: "I'll send that email" (NOT "I'll execute gmail_send_email")

User: "Get my calendar for today"
You: "I'll check your calendar" (NOT "I'll use google_calendar_list_events")

User: "Create a doc with my email summary"
You: "I'll check your emails and create a document with the summary" (NOT "I'll call gmail_list_messages with export='google_doc'")

SERVER TOOLS (Always Available):
- **web_search**: Real-time web search to find current information, news, pricing, standards, or any up-to-date data. Returns search results with URLs, titles, and content snippets. Use this when you need current information not in your knowledge cutoff.
- **web_fetch**: Fetch and analyze content from specific URLs. Retrieves full document content including PDFs and web pages with citations enabled. Use this when you need to read a specific document or webpage.

WHEN TO USE SERVER TOOLS:
✅ Use web_search when user asks about:
   - Current events, news, trends
   - Latest pricing or market data
   - Technical standards or specifications
   - "What's the latest..." or "Find information about..."
   
✅ Use web_fetch when user asks to:
   - Analyze a specific URL or document
   - Read content from a webpage
   - Extract information from a PDF link
   - "Analyze this article at..." or "What does this page say..."

IMPORTANT: You can use both server tools AND client tools in the same conversation. For example:
1. Use web_search to find current information
2. Use gmail_send_email to send that information to someone
3. Use google_docs_create_document to save the findings

Always explain what you're doing when using these tools so the user understands your process - but use natural language, not technical tool names."""
    
    def get_system_prompt(self, ui_context: str, agent_id: Optional[str] = None) -> str:
        """
        Get system prompt for UI context
        
        Args:
            ui_context: 'stock_chat' | 'data_agent_chat' | 'single_viewer' | 'triple_agent'
            agent_id: For triple_agent: '1', '2', '3'
        
        Returns:
            System prompt string
        """
        # Load tool usage instructions
        tool_usage_prompt = self._get_tool_usage_instructions()
        
        if ui_context == 'stock_chat':
            return tool_usage_prompt + "\n\n" + self._get_stock_chat_prompt()
        
        elif ui_context == 'data_agent_chat':
            return tool_usage_prompt + "\n\n" + self._get_data_agent_prompt()
        
        elif ui_context == 'single_viewer':
            return tool_usage_prompt + "\n\n" + self._get_single_viewer_prompt()
        
        elif ui_context == 'triple_agent':
            return tool_usage_prompt + "\n\n" + self._get_triple_agent_prompt(agent_id)
        
        # Default fallback
        return tool_usage_prompt + "\n\nYou are a helpful AI assistant with access to database and business tools."
    
    def process_streaming(
        self,
        session_id: str,
        session_data: Dict,
        prompt: str,
        files: Optional[List] = None,
        provider: Literal['anthropic', 'deepseek', 'openai', 'MiniMax'] = 'anthropic',
        sse_callback: Optional[Callable] = None,
        user_id: Optional[int] = None,
        org_model: Optional[str] = None,
        org_max_tokens: Optional[int] = None,
    ) -> List[Dict]:
        """
        Process AI request with streaming (unified interface for all providers)

        Args:
            session_id: Session identifier
            session_data: Session data from UnifiedSessionManager
            prompt: User message
            files: Optional files (for Claude Vision)
            provider: AI provider to use
            sse_callback: Callback for SSE events (lambda event: queue.put(event))
            user_id: Requesting user — used for per-org key + model resolution (GAP-M3)
            org_model: Per-org model override (GAP-M3) — None falls back to startup default
            org_max_tokens: Per-org max_tokens override (GAP-M3)

        Returns:
            Updated conversation history
        """
        # Route to appropriate provider
        if provider == 'anthropic':
            return self._process_anthropic(session_id, session_data, prompt, files, sse_callback,
                                           user_id=user_id, org_model=org_model, org_max_tokens=org_max_tokens)

        elif provider == 'deepseek':
            return self._process_deepseek(session_id, session_data, prompt, sse_callback,
                                          user_id=user_id, org_model=org_model, org_max_tokens=org_max_tokens)

        elif provider == 'openai':
            return self._process_openai(session_id, session_data, prompt, sse_callback,
                                        user_id=user_id, org_model=org_model, org_max_tokens=org_max_tokens)

        elif provider == 'MiniMax':
            return self._process_MiniMax(session_id, session_data, prompt, files, sse_callback,
                                          user_id=user_id, org_model=org_model, org_max_tokens=org_max_tokens)

        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _process_anthropic(
        self,
        session_id: str,
        session_data: Dict,
        prompt: str,
        files: Optional[List],
        sse_callback: Optional[Callable],
        user_id: Optional[int] = None,
        org_model: Optional[str] = None,
        org_max_tokens: Optional[int] = None,
    ) -> List[Dict]:
        """Process with Anthropic Claude (streaming with tools)"""
        # GAP-C3 FIX: Resolve API key per-request so each org uses its own key.
        # Falls back to the startup-initialised client when no user context is available.
        anthropic_client = self.anthropic_client
        try:
            if user_id:
                from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
                per_request_key = resolve_api_key(user_id, 'anthropic')
                if per_request_key:
                    from anthropic import Anthropic as _Anthropic
                    anthropic_client = _Anthropic(
                        api_key=per_request_key,
                        timeout=httpx.Timeout(connect=30.0, read=600.0, write=60.0, pool=10.0),
                        max_retries=3,
                    )
        except Exception as _key_err:
            import logging as _log
            _log.getLogger(__name__).warning(
                f"[UnifiedAIClient] Per-request key resolution failed, using startup key: {_key_err}"
            )
        
        # Get system prompt
        system_prompt = self.get_system_prompt(
            session_data['ui_context'],
            session_data.get('agent_id')
        )
        
        # Build conversation
        conversation = session_data.get('conversation', [])
        
        # Build user message
        user_message = {'role': 'user', 'content': []}
        
        # Add files if present (Claude Vision)
        if files:
            for file_data in files:
                user_message['content'].append({
                    'type': 'image' if file_data['media_type'].startswith('image/') else 'document',
                    'source': {
                        'type': 'base64',
                        'media_type': file_data['media_type'],
                        'data': file_data['data']
                    }
                })
        
        # Add text
        user_message['content'].append({'type': 'text', 'text': prompt})
        
        # Add to conversation
        conversation.append(user_message)
        
        # Get tool definitions from registry_v3
        from tools import registry_v3
        registry = registry_v3.get_registry()
        client_tools = registry.get_anthropic_tools()
        
        # Add ToolUseAgent tools if available
        try:
            tool_agent_tools = self.tool_agent._get_tool_definitions()
            print(f"[UnifiedAIClient] Loaded {len(tool_agent_tools)} ToolUseAgent tools")
            client_tools.extend(tool_agent_tools)
        except:
            pass
        
        # Validate and fix client tools
        validated_tools = []
        invalid_count = 0
        
        for idx, tool in enumerate(client_tools):
            is_valid, errors = self._validate_tool_schema(tool, idx)
            
            if not is_valid:
                # Try to fix
                fixed_tool = self._fix_tool_schema(tool)
                is_fixed, remaining_errors = self._validate_tool_schema(fixed_tool, idx)
                
                if is_fixed:
                    validated_tools.append(fixed_tool)
                else:
                    invalid_count += 1
            else:
                validated_tools.append(tool)
        
        if invalid_count > 0:
            print(f"⚠️  [UnifiedAIClient] Skipped {invalid_count} invalid tools in streaming mode")
        
        # Add server tools
        server_tools = []
        
        # Web Search server tool
        server_tools.append({
            "type": "web_search_20250305",
            "name": "web_search",
            "user_location": {
                "type": "approximate",
                "city": "Brisbane",
                "region": "Queensland",
                "country": "AU",
                "timezone": "Australia/Brisbane"
            },
            "max_uses": 5
        })
        
        # Web Fetch server tool (BETA) - enabled by default
        enable_web_fetch = session_data.get('enable_web_fetch', True)
        if enable_web_fetch:
            server_tools.append({
                "type": "web_fetch_20250910",
                "name": "web_fetch",
                "max_uses": 10,
                "citations": {"enabled": True},
                "max_content_tokens": 100000
            })
        
        all_tools = validated_tools + server_tools
        print(f"[UnifiedAIClient] Total tools: {len(all_tools)} ({len(validated_tools)} client + {len(server_tools)} server)")
        
        # ✅ FIX F2 (Jul 26, 2026): Interleaved-aware reorder.
        # ─────────────────────────────────────────────────────────────────────
        # WHY THIS REPLACES THE OLD CODE
        #   The previous code unconditionally moved every thinking block to
        #   the front of each assistant message. That breaks the
        #   `interleaved-thinking-2025-05-14` beta contract when the model
        #   emits a thinking block *after* a tool_use (the reasoning that
        #   justifies the tool call). The Anthropic API requires the
        #   original order to be preserved in that case.
        #
        # WHAT IT DOES
        #   Walks each assistant message and detects whether the message is
        #   "interleaved" (i.e. a thinking block appears after a tool_use).
        #   - Non-interleaved messages: safe to reorder — thinking stays
        #     first (the original rule).
        #   - Interleaved messages: order is left untouched, exactly as the
        #     model produced it. A log line marks the bypass for traceability.
        #
        # SAFETY
        #   - Operates only on assistant messages with structured content.
        #   - Does not drop or duplicate blocks; only reorders.
        #   - Mirrors the helper in `combined_agent_worker.py:
        #     validate_and_reorder_assistant_content` so the two paths
        #     agree on the contract.
        # ─────────────────────────────────────────────────────────────────────
        _THINKING_TYPES = ('thinking', 'redacted_thinking')
        _TOOL_TYPES = ('tool_use', 'server_tool_use')

        def _is_interleaved(blocks: list) -> bool:
            seen_tool_use = False
            for b in blocks:
                if not isinstance(b, dict):
                    continue
                t = b.get('type')
                if t in _TOOL_TYPES:
                    seen_tool_use = True
                elif t in _THINKING_TYPES and seen_tool_use:
                    return True
            return False

        for msg in conversation:
            if msg['role'] == 'assistant' and isinstance(msg.get('content'), list):
                content = msg['content']
                if not content:
                    continue
                has_thinking = any(
                    isinstance(b, dict) and b.get('type') in _THINKING_TYPES
                    for b in content
                )
                if not has_thinking:
                    continue
                # First block is already thinking — nothing to do.
                if isinstance(content[0], dict) and content[0].get('type') in _THINKING_TYPES:
                    continue
                # Interleaved pattern — DO NOT reorder.
                if _is_interleaved(content):
                    print(
                        f"[UnifiedAIClient] ℹ️  Interleaved thinking detected "
                        f"({len(content)} blocks); preserving original order"
                    )
                    continue
                # Non-interleaved: move thinking blocks to the front.
                thinking_blocks = [b for b in content if isinstance(b, dict) and b.get('type') in _THINKING_TYPES]
                other_blocks = [b for b in content if not (isinstance(b, dict) and b.get('type') in _THINKING_TYPES)]
                msg['content'] = thinking_blocks + other_blocks
                print(
                    f"[UnifiedAIClient] ✅ Reordered: {len(thinking_blocks)} thinking + "
                    f"{len(other_blocks)} other blocks"
                )
        
        # ✅ EXPLICIT CHECK: Validate final assistant message when thinking is enabled
        thinking_enabled = session_data.get('enable_thinking', True)
        if thinking_enabled and conversation:
            # Find last assistant message
            last_assistant_idx = None
            for i in range(len(conversation) - 1, -1, -1):
                if conversation[i].get('role') == 'assistant':
                    last_assistant_idx = i
                    break
            
            if last_assistant_idx is not None:
                last_assistant = conversation[last_assistant_idx]
                content = last_assistant.get('content', [])
                
                if isinstance(content, list) and content:
                    has_thinking = any(block.get('type') == 'thinking' for block in content)
                    first_is_thinking = content[0].get('type') == 'thinking'
                    
                    if has_thinking and not first_is_thinking:
                        # Already reordered above, this shouldn't happen
                        print(f"⚠️  [UnifiedAIClient] WARNING: Final assistant message has thinking blocks but first block is not thinking!")
                    elif not has_thinking:
                        # No thinking blocks in final assistant message - this is OK when thinking param is present
                        print(f"[UnifiedAIClient] ℹ️  Final assistant message has no thinking blocks (API will generate thinking in response)")
                    else:
                        print(f"[UnifiedAIClient] ✅ Final assistant message properly starts with thinking block")
        
        # Stream with Anthropic (WITH Extended Thinking + Interleaved Thinking + Server Tools)
        assistant_message = {'role': 'assistant', 'content': []}
        
        # Beta headers
        # ✅ FIX 4A (Jul 26, 2026): Send the `interleaved-thinking-…` header
        # ONLY when thinking is enabled. Advertising the beta while not using
        # it is a contract violation and Anthropic may reject the request in
        # the future. (Provider routing itself is already conditional — the
        # MiniMax code path omits these headers entirely.)
        beta_headers = []
        if thinking_enabled:
            beta_headers.append("interleaved-thinking-2025-05-14")
        if enable_web_fetch:
            beta_headers.append("web-fetch-2025-09-10")
        
        # CRITICAL: When thinking is enabled, temperature MUST be 1.0 (Anthropic API requirement)
        # Get custom temperature from session_data or use default
        custom_temperature = session_data.get('temperature', 1.0)
        thinking_enabled = session_data.get('enable_thinking', True)
        
        if thinking_enabled:
            final_temperature = 1.0
            if custom_temperature != 1.0:
                print(f"[UnifiedAIClient] ⚙️  Temperature overridden: {custom_temperature} → 1.0 (required when thinking enabled)")
        else:
            final_temperature = custom_temperature
            print(f"[UnifiedAIClient] ⚙️  Temperature set to {final_temperature} (thinking disabled)")
        
        with anthropic_client.messages.stream(
            model=org_model or self.anthropic_model,
            max_tokens=org_max_tokens or 12000,
            temperature=final_temperature,
            system=system_prompt,
            messages=conversation,
            tools=all_tools,
            # ✅ Extended Thinking: Internal reasoning blocks
            # ─────────────────────────────────────────────────────────────────
            # ✅ FIX 4B (Jul 26, 2026): The Anthropic `thinking` param shape
            # is `{"type": "enabled", "budget_tokens": N}`. MiniMax-M3 uses the
            # SAME shape (documented in MiniMax API as Anthropic-compatible
            # thinking param), so no shape switch is needed at this point —
            # but if MiniMax ever introduces `{"type": "adaptive"}` or
            # `{"type": "disabled"}` without `budget_tokens`, branch here.
            # The block CONTENT divergence (redacted_thinking) is handled in
            # `validate_messages_for_api` (F3 denylist) and the per-provider
            # strip helper in 4C.
            # ─────────────────────────────────────────────────────────────────
            thinking={
                "type": "enabled",
                "budget_tokens": session_data.get('thinking_budget', 5000)
            },
            # ✅ Beta headers: Interleaved Thinking + Web Fetch
            extra_headers={
                "anthropic-beta": ",".join(beta_headers)
            }
        ) as stream:
            for event in stream:
                # Convert to SSE format
                sse_event = self._convert_anthropic_event_to_sse(event)
                
                if sse_event and sse_callback:
                    sse_callback(sse_event)
                
                # Build assistant message
                if event.type == 'content_block_start':
                    # Handle thinking blocks
                    if event.content_block.type == 'thinking':
                        assistant_message['content'].append({'type': 'thinking', 'thinking': ''})
                    
                    # Handle text blocks
                    elif event.content_block.type == 'text':
                        assistant_message['content'].append({'type': 'text', 'text': ''})
                    
                    # Handle CLIENT tool_use
                    elif event.content_block.type == 'tool_use':
                        assistant_message['content'].append({
                            'type': 'tool_use',
                            'id': event.content_block.id,
                            'name': event.content_block.name,
                            'input': {}
                        })
                    
                    # SERVER TOOL: server_tool_use
                    elif event.content_block.type == 'server_tool_use':
                        assistant_message['content'].append({
                            'type': 'server_tool_use',
                            'id': event.content_block.id,
                            'name': event.content_block.name,
                            'input': {}
                        })
                        print(f"[SERVER TOOL] {event.content_block.name} initiated")
                    
                    # SERVER TOOL: web_search_tool_result
                    elif event.content_block.type == 'web_search_tool_result':
                        result_block = {
                            'type': 'web_search_tool_result',
                            'tool_use_id': event.content_block.tool_use_id,
                            'content': []
                        }
                        # Preserve search results with encrypted content
                        if hasattr(event.content_block, 'content'):
                            for result in event.content_block.content:
                                result_block['content'].append({
                                    'type': 'web_search_result',
                                    'url': result.url,
                                    'title': result.title,
                                    'encrypted_content': result.encrypted_content,
                                    'page_age': getattr(result, 'page_age', None)
                                })
                        assistant_message['content'].append(result_block)
                        print(f"[SERVER TOOL] web_search returned {len(result_block['content'])} results")
                    
                    # SERVER TOOL: web_fetch_tool_result
                    elif event.content_block.type == 'web_fetch_tool_result':
                        result_block = {
                            'type': 'web_fetch_tool_result',
                            'tool_use_id': event.content_block.tool_use_id,
                            'content': {}
                        }
                        # Preserve fetch results with content
                        if hasattr(event.content_block, 'content'):
                            content = event.content_block.content
                            result_block['content'] = {
                                'type': 'web_fetch_result',
                                'url': content.url,
                                'content': {
                                    'type': 'document',
                                    'source': content.content.source,
                                    'title': getattr(content.content, 'title', None),
                                    'citations': getattr(content.content, 'citations', None)
                                },
                                'retrieved_at': content.retrieved_at
                            }
                        assistant_message['content'].append(result_block)
                        print(f"[SERVER TOOL] web_fetch returned content from {result_block['content'].get('url', 'unknown')}")
                
                elif event.type == 'content_block_delta':
                    if event.delta.type == 'thinking_delta':
                        # Accumulate thinking content
                        assistant_message['content'][-1]['thinking'] += event.delta.thinking

                    elif event.delta.type == 'text_delta':
                        assistant_message['content'][-1]['text'] += event.delta.text

                    elif event.delta.type == 'input_json_delta':
                        # Accumulate tool input (client and server)
                        if assistant_message['content']:
                            last_block = assistant_message['content'][-1]
                            if last_block['type'] in ['tool_use', 'server_tool_use']:
                                # Parse JSON delta and merge into input
                                try:
                                    import json
                                    partial_input = json.loads(event.delta.partial_json)
                                    last_block['input'].update(partial_input)
                                except:
                                    pass  # Partial JSON, wait for more chunks

                    # ✅ FIX F1-A (Jul 26, 2026): Capture signature_delta for thinking blocks.
                    # ─────────────────────────────────────────────────────────────────────
                    # WHY THIS EXISTS
                    #   Anthropic streams a final `signature_delta` event for every
                    #   thinking block. The signature is a cryptographic token that
                    #   the API uses to verify the block was produced by Anthropic.
                    #   Without it, the next round-trip rejects the assistant message
                    #   with `400 invalid_request_error: thinking block must be
                    #   signed`. This was the root cause of the orphaned thinking
                    #   blocks in the "Tool Test Rd 5" thread (commit bd5841ed).
                    #
                    # WHAT IT DOES
                    #   Stamps the signature onto the last thinking block in the
                    #   in-memory `assistant_message` so it round-trips correctly
                    #   on the next API call AND is persisted to the DB with the
                    #   signature field populated.
                    #
                    # SAFETY
                    #   - Only touches the last block (the one currently streaming).
                    #   - Only assigns when the last block is a thinking block
                    #     (extras like tool_use or text are skipped).
                    #   - Writes nothing if the SDK never sends a signature_delta
                    #     (the API then returns an error itself with a clear
                    #     message); we never fabricate a signature.
                    # ─────────────────────────────────────────────────────────────────────
                    elif event.delta.type == 'signature_delta':
                        if assistant_message['content']:
                            last_block = assistant_message['content'][-1]
                            if last_block.get('type') == 'thinking':
                                last_block['signature'] = event.delta.signature
                            else:
                                print(f"[UnifiedAIClient] ⚠️  signature_delta for non-thinking block (type={last_block.get('type')}); ignored")

                    # Handle citations in text blocks
                    elif hasattr(event.delta, 'citations') and event.delta.citations:
                        if assistant_message['content']:
                            last_block = assistant_message['content'][-1]
                            if last_block['type'] == 'text':
                                if 'citations' not in last_block:
                                    last_block['citations'] = []
                                last_block['citations'].extend(event.delta.citations)
        
        # Handle CLIENT tool use (server tools are already executed by Anthropic API)
        server_tools = ['web_search', 'web_fetch']
        
        # Only handle CLIENT tools (not server tools)
        client_tool_blocks = [
            block for block in assistant_message['content']
            if block['type'] == 'tool_use' and block.get('name') not in server_tools
        ]
        
        if client_tool_blocks:
            assistant_message = self._handle_tool_use(assistant_message, sse_callback)
        
        # Log server tool execution
        server_tool_blocks = [
            block for block in assistant_message['content']
            if block['type'] == 'server_tool_use'
        ]
        if server_tool_blocks:
            tool_names = [block['name'] for block in server_tool_blocks]
            print(f"[SERVER TOOLS] {len(server_tool_blocks)} server tools executed: {', '.join(tool_names)}")
        
        # Add to conversation
        conversation.append(assistant_message)
        
        return conversation
    
    def _process_deepseek(
        self,
        session_id: str,
        session_data: Dict,
        prompt: str,
        sse_callback: Optional[Callable],
        user_id: Optional[int] = None,
        org_model: Optional[str] = None,
        org_max_tokens: Optional[int] = None,
    ) -> List[Dict]:
        """Process with DeepSeek (streaming)"""
        # GAP-C3/L5 FIX: Resolve DeepSeek key per-request from org vault.
        deepseek_api_key = self.deepseek_api_key
        try:
            if user_id:
                from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
                per_request_key = resolve_api_key(user_id, 'deepseek')
                if per_request_key:
                    deepseek_api_key = per_request_key
        except Exception:
            pass
        
        # Get system prompt
        system_prompt = self.get_system_prompt(
            session_data['ui_context'],
            session_data.get('agent_id')
        )
        
        # Build conversation
        conversation = session_data.get('conversation', [])
        
        # Convert to OpenAI format (DeepSeek uses OpenAI-compatible API)
        messages = [{'role': 'system', 'content': system_prompt}]
        
        for msg in conversation:
            # Convert Anthropic format to OpenAI format
            if msg['role'] == 'user':
                text_content = ''
                for block in msg['content']:
                    if block['type'] == 'text':
                        text_content += block['text']
                messages.append({'role': 'user', 'content': text_content})
            
            elif msg['role'] == 'assistant':
                text_content = ''
                for block in msg['content']:
                    if block['type'] == 'text':
                        text_content += block['text']
                messages.append({'role': 'assistant', 'content': text_content})
        
        # Add new user message
        messages.append({'role': 'user', 'content': prompt})
        
        # Call DeepSeek API (streaming)
        headers = {
            'Authorization': f'Bearer {deepseek_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': org_model or self.deepseek_model,
            'messages': messages,
            'stream': True,
            'max_tokens': org_max_tokens or 8000
        }
        
        response = requests.post(
            f'{self.deepseek_base_url}/chat/completions',
            headers=headers,
            json=payload,
            stream=True
        )
        
        assistant_text = ''
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    
                    try:
                        chunk = json.loads(data)
                        delta = chunk['choices'][0]['delta']
                        
                        if 'content' in delta:
                            text = delta['content']
                            assistant_text += text
                            
                            # Emit SSE event
                            if sse_callback:
                                sse_callback({
                                    'type': 'text_delta',
                                    'text': text,
                                    'index': 0
                                })
                    except:
                        pass
        
        #  Add to conversation (Anthropic format for consistency)
        # DeepSeek doesn't support thinking blocks, but we preserve the format
        conversation.append({'role': 'user', 'content': [{'type': 'text', 'text': prompt}]})
        # NOTE: DeepSeek responses are text-only (no thinking/tool_use support)
        conversation.append({'role': 'assistant', 'content': [{'type': 'text', 'text': assistant_text}]})
        
        return conversation
    
    def _process_openai(
        self,
        session_id: str,
        session_data: Dict,
        prompt: str,
        sse_callback: Optional[Callable],
        user_id: Optional[int] = None,
        org_model: Optional[str] = None,
        org_max_tokens: Optional[int] = None,
    ) -> List[Dict]:
        """Process with OpenAI GPT (streaming)"""
        # GAP-C3 FIX: Resolve OpenAI key per-request from org vault.
        openai_key = getattr(openai, 'api_key', None) or os.environ.get('OPENAI_API_KEY', '')
        try:
            if user_id:
                from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
                per_request_key = resolve_api_key(user_id, 'openai')
                if per_request_key:
                    openai_key = per_request_key
        except Exception:
            pass
        
        # Get system prompt
        system_prompt = self.get_system_prompt(
            session_data['ui_context'],
            session_data.get('agent_id')
        )
        
        # Build conversation
        conversation = session_data.get('conversation', [])
        
        # Convert to OpenAI format
        messages = [{'role': 'system', 'content': system_prompt}]
        
        for msg in conversation:
            if msg['role'] == 'user':
                text_content = ''
                for block in msg['content']:
                    if block['type'] == 'text':
                        text_content += block['text']
                messages.append({'role': 'user', 'content': text_content})
            
            elif msg['role'] == 'assistant':
                text_content = ''
                for block in msg['content']:
                    if block['type'] == 'text':
                        text_content += block['text']
                messages.append({'role': 'assistant', 'content': text_content})
        
        # Add new user message
        messages.append({'role': 'user', 'content': prompt})
        
        # Call OpenAI API (streaming) — use per-request key via openai.OpenAI() client
        import openai as _openai_mod
        _openai_client = _openai_mod.OpenAI(api_key=openai_key)
        response = _openai_client.chat.completions.create(
            model=org_model or self.openai_model,
            messages=messages,
            stream=True,
            max_tokens=org_max_tokens or 8000
        )
        
        assistant_text = ''
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                assistant_text += text
                
                # Emit SSE event
                if sse_callback:
                    sse_callback({
                        'type': 'text_delta',
                        'text': text,
                        'index': 0
                    })
        
        #  Add to conversation (Anthropic format for consistency)
        # OpenAI doesn't support thinking blocks, but we preserve the format
        conversation.append({'role': 'user', 'content': [{'type': 'text', 'text': prompt}]})
        # NOTE: OpenAI responses are text-only (no thinking/tool_use support)
        conversation.append({'role': 'assistant', 'content': [{'type': 'text', 'text': assistant_text}]})

        return conversation

    def _process_MiniMax(
        self,
        session_id: str,
        session_data: Dict,
        prompt: str,
        files: Optional[List],
        sse_callback: Optional[Callable],
        user_id: Optional[int] = None,
        org_model: Optional[str] = None,
        org_max_tokens: Optional[int] = None,
    ) -> List[Dict]:
        """Process with MiniMax (streaming, Anthropic-compatible).

        MiniMax exposes an Anthropic-compatible endpoint, so this implementation
        is structurally identical to _process_anthropic — same content blocks,
        same tool_use / thinking handling.  We swap the client (base_url points
        at api.minimax.io/anthropic) and the model id ('MiniMax-M3' etc.).

        Per MiniMax docs: M3 supports thinking + interleaved-thinking + tool use
        with the same Anthropic headers.  Other M-series models (M2.7, M2.5,
        M2.1, M2) support tool use but not thinking.
        """
        # Resolve per-request API key from the org vault
        MiniMax_client = self.MiniMax_client
        try:
            if user_id:
                from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
                per_request_key = resolve_api_key(user_id, 'MiniMax')
                if per_request_key:
                    from anthropic import Anthropic as _Anthropic
                    MiniMax_client = _Anthropic(
                        api_key=per_request_key,
                        base_url=self.MiniMax_base_url,
                        timeout=httpx.Timeout(connect=30.0, read=600.0, write=60.0, pool=10.0),
                        max_retries=3,
                    )
        except Exception as _key_err:
            import logging as _log
            _log.getLogger(__name__).warning(
                f"[UnifiedAIClient] Per-request MiniMax key resolution failed, using startup key: {_key_err}"
            )

        if MiniMax_client is None:
            raise ValueError("MiniMax client not initialized. Set MINIMAX_API_KEY.")

        # System prompt
        system_prompt = self.get_system_prompt(
            session_data['ui_context'],
            session_data.get('agent_id')
        )

        # Build conversation
        conversation = session_data.get('conversation', [])

        # Build user message
        user_message = {'role': 'user', 'content': []}

        # Add files if present (vision / multimodal)
        if files:
            for file_data in files:
                user_message['content'].append({
                    'type': 'image' if file_data['media_type'].startswith('image/') else 'document',
                    'source': {
                        'type': 'base64',
                        'media_type': file_data['media_type'],
                        'data': file_data['data']
                    }
                })

        # Add text
        user_message['content'].append({'type': 'text', 'text': prompt})

        # Add to conversation
        conversation.append(user_message)

        # Resolve tool definitions from registry_v3
        from tools import registry_v3
        registry = registry_v3.get_registry()
        client_tools = registry.get_anthropic_tools()

        # Add ToolUseAgent tools if available
        try:
            tool_agent_tools = self.tool_agent._get_tool_definitions()
            print(f"[UnifiedAIClient] Loaded {len(tool_agent_tools)} ToolUseAgent tools (MiniMax)")
            client_tools.extend(tool_agent_tools)
        except Exception:
            pass

        # Validate and fix client tools (same logic as Anthropic path)
        validated_tools = []
        invalid_count = 0

        for idx, tool in enumerate(client_tools):
            is_valid, errors = self._validate_tool_schema(tool, idx)
            if not is_valid:
                fixed_tool = self._fix_tool_schema(tool)
                is_fixed, _ = self._validate_tool_schema(fixed_tool, idx)
                if is_fixed:
                    validated_tools.append(fixed_tool)
                else:
                    invalid_count += 1
            else:
                validated_tools.append(tool)

        if invalid_count > 0:
            print(f"⚠️  [UnifiedAIClient/MiniMax] Skipped {invalid_count} invalid tools in streaming mode")

        # MiniMax does NOT have Anthropic server tools (no web_search/web_fetch).
        # Tool use is handled locally by the registered client tools.
        all_tools = validated_tools
        print(f"[UnifiedAIClient/MiniMax] Total tools: {len(all_tools)} (client only — no server tools)")

        # Reorder assistant message content blocks so any thinking block is first
        # ─────────────────────────────────────────────────────────────────────
        # ✅ FIX 4C (Jul 26, 2026): Strip `redacted_thinking` blocks before send.
        # WHY
        #   Anthropic uses `redacted_thinking` for encrypted thinking payloads
        #   (e.g. when a safety classifier intercepts internal reasoning).
        #   MiniMax-M3 does not support this block type — sending it produces
        #   a 400 from the upstream provider. Earlier rounds of the
        #   conversation may have been answered by Anthropic and persisted
        #   with `redacted_thinking`; the next MiniMax round-trip needs them
        #   removed without disturbing the regular `thinking` blocks.
        #
        # WHAT IT DOES
        #   Walks every assistant message, removes only `redacted_thinking`
        #   blocks, and logs a count. Then reorders the remaining
        #   `thinking` blocks to the front (same shape as Anthropic path).
        #
        # SAFETY
        #   - Operates on a copy-safe iteration; does not mutate the
        #     conversation reference shared with the rest of the app.
        #   - Only the redacted variant is removed; `thinking` and
        #     `text` blocks pass through untouched.
        # ─────────────────────────────────────────────────────────────────────
        _stripped_redacted = 0
        for msg in conversation:
            if msg['role'] != 'assistant' or not isinstance(msg.get('content'), list):
                continue
            new_content = []
            for b in msg['content']:
                if isinstance(b, dict) and b.get('type') == 'redacted_thinking':
                    _stripped_redacted += 1
                    continue
                new_content.append(b)
            msg['content'] = new_content
        if _stripped_redacted:
            print(
                f"[UnifiedAIClient/MiniMax] 🧹 Stripped {_stripped_redacted} redacted_thinking "
                f"block(s) — MiniMax does not support them"
            )

        for msg in conversation:
            if msg['role'] == 'assistant' and isinstance(msg.get('content'), list):
                has_thinking = any(block.get('type') == 'thinking' for block in msg['content'])
                if has_thinking and msg['content'] and msg['content'][0].get('type') != 'thinking':
                    thinking_blocks = [b for b in msg['content'] if b.get('type') == 'thinking']
                    other_blocks   = [b for b in msg['content'] if b.get('type') != 'thinking']
                    msg['content'] = thinking_blocks + other_blocks

        # Thinking is only supported on M3.
        # The MiniMax docs treat thinking as opt-in via the same Anthropic param
        # shape, so we follow the user toggle the same way as the Claude path.
        model_id = org_model or self.MiniMax_model
        thinking_enabled = session_data.get('enable_thinking', True) and model_id == 'MiniMax-M3'

        if thinking_enabled:
            final_temperature = 1.0
        else:
            final_temperature = session_data.get('temperature', 1.0)

        assistant_message = {'role': 'assistant', 'content': []}

        # Build stream params
        stream_params = {
            'model': model_id,
            'max_tokens': org_max_tokens or 12000,
            'temperature': final_temperature,
            'system': system_prompt,
            'messages': conversation,
            'tools': all_tools,
        }

        # MiniMax accepts the same `thinking` block as Anthropic; only M3 supports it.
        # ─────────────────────────────────────────────────────────────────
        # ✅ FIX 4B/C (Jul 26, 2026): Param shape is intentionally identical
        # to the Anthropic path ({"type": "enabled", "budget_tokens": N}).
        # The only provider divergence is the BLOCK CONTENT — MiniMax-M3
        # does not support `redacted_thinking` blocks; the strip helper
        # added below removes them from the conversation before send.
        # ─────────────────────────────────────────────────────────────────
        if thinking_enabled:
            stream_params['thinking'] = {
                'type': 'enabled',
                'budget_tokens': session_data.get('thinking_budget', 5000),
            }

        # The MiniMax docs do not require the `anthropic-beta` headers, so we
        # omit them by default.  Callers that need interleaved-thinking on M3
        # get it for free through the Anthropic SDK's `thinking` param.

        with MiniMax_client.messages.stream(**stream_params) as stream:
            for event in stream:
                sse_event = self._convert_anthropic_event_to_sse(event)
                if sse_event and sse_callback:
                    sse_callback(sse_event)

                if event.type == 'content_block_start':
                    block = event.content_block
                    if block.type == 'thinking':
                        assistant_message['content'].append({'type': 'thinking', 'thinking': ''})
                    elif block.type == 'text':
                        assistant_message['content'].append({'type': 'text', 'text': ''})
                    elif block.type == 'tool_use':
                        assistant_message['content'].append({
                            'type': 'tool_use',
                            'id': block.id,
                            'name': block.name,
                            'input': {},
                        })

                elif event.type == 'content_block_delta':
                    if event.delta.type == 'thinking_delta':
                        assistant_message['content'][-1]['thinking'] += event.delta.thinking
                    elif event.delta.type == 'text_delta':
                        assistant_message['content'][-1]['text'] += event.delta.text
                    elif event.delta.type == 'input_json_delta':
                        if assistant_message['content']:
                            last_block = assistant_message['content'][-1]
                            if last_block['type'] == 'tool_use':
                                try:
                                    import json as _json
                                    partial_input = _json.loads(event.delta.partial_json)
                                    last_block['input'].update(partial_input)
                                except Exception:
                                    pass  # Partial JSON
                    # ✅ FIX F1-B (Jul 26, 2026): Capture signature_delta for MiniMax.
                    # Mirror of F1-A. MiniMax-M3 emits signatures on the same
                    # `signature_delta` event through the Anthropic SDK; without
                    # this, thinking blocks break on the next round-trip exactly
                    # as they do for Anthropic (see F1-A comment for full context).
                    elif event.delta.type == 'signature_delta':
                        if assistant_message['content']:
                            last_block = assistant_message['content'][-1]
                            if last_block.get('type') == 'thinking':
                                last_block['signature'] = event.delta.signature
                            else:
                                print(f"[UnifiedAIClient:MiniMax] ⚠️  signature_delta for non-thinking block (type={last_block.get('type')}); ignored")

        # Handle CLIENT tool use (MiniMax has no server tools)
        client_tool_blocks = [
            block for block in assistant_message['content']
            if block['type'] == 'tool_use'
        ]

        if client_tool_blocks:
            assistant_message = self._handle_tool_use(assistant_message, sse_callback)

        conversation.append(assistant_message)
        return conversation

    def _convert_anthropic_event_to_sse(self, event) -> Optional[Dict]:
        """
        Convert Anthropic event to SSE format

        Handles:
        - text_delta: Regular text content
        - thinking_delta: Extended thinking content
        - signature_delta: Signature for thinking blocks (interleaved-thinking)
        - server_tool_use: Web search/fetch requests
        - web_search_tool_result: Web search results
        - web_fetch_tool_result: Web fetch results
        """

        # ─────────────────────────────────────────────────────────────────
        # Content-block deltas (text / thinking / signature / input_json).
        # ─────────────────────────────────────────────────────────────────
        # All four delta kinds are delivered by the SDK as
        # `event.type == 'content_block_delta'` with `event.delta.type` set
        # to one of `text_delta | thinking_delta | signature_delta |
        # input_json_delta`. The previous version of this function put
        # text_delta in the first `if` branch and the other three in an
        # `elif hasattr(event, 'delta')` branch — but that elif was
        # unreachable for any `content_block_delta` event, so the
        # thinking_delta / signature_delta paths never fired. The smoke
        # test in `tests/test_tool_system_robustness_fixes.py` exposed
        # this; the corrected structure collapses all four into one
        # branch.
        if event.type == 'content_block_delta':
            d = event.delta
            if d.type == 'text_delta':
                return {
                    'type': 'text_delta',
                    'text': d.text,
                    'index': event.index,
                }
            if d.type == 'thinking_delta':
                return {
                    'type': 'thinking_delta',
                    'text': d.thinking,
                    'index': event.index,
                }
            # ✅ FIX F1-C (Jul 26, 2026): Forward signature_delta to the browser.
            # The signature is the cryptographic token that proves the
            # thinking block was produced by Anthropic (or MiniMax-M3).
            # Without it, the client-side cache can never reconstruct a
            # valid round-trip. Used together with F1-A/F1-B, this
            # ensures the signature reaches the UI as soon as the SDK
            # delivers it.
            if d.type == 'signature_delta':
                return {
                    'type': 'signature_delta',
                    'signature': d.signature,
                    'index': event.index,
                }
            if d.type == 'input_json_delta':
                return {
                    'type': 'input_json_delta',
                    'partial_json': d.partial_json,
                    'index': event.index,
                }
            # Unknown delta type — surface for visibility rather than
            # silently dropping on the floor.
            return {
                'type': 'unknown_delta',
                'delta_type': d.type,
                'index': event.index,
            }

        # Server tool use (web_search, web_fetch) — only delivered by
        # the Anthropic provider, not MiniMax.
        if event.type == 'content_block_start':
            if hasattr(event, 'content_block'):
                block = event.content_block

                # Server tool use
                if block.type == 'server_tool_use':
                    return {
                        'type': 'server_tool_use',
                        'id': block.id,
                        'name': block.name,
                        'input': getattr(block, 'input', {}),
                        'index': event.index
                    }

                # Web search results
                elif block.type == 'web_search_tool_result':
                    return {
                        'type': 'web_search_tool_result',
                        'tool_use_id': block.tool_use_id,
                        'content': getattr(block, 'content', []),
                        'index': event.index
                    }

                # Web fetch results
                elif block.type == 'web_fetch_tool_result':
                    return {
                        'type': 'web_fetch_tool_result',
                        'tool_use_id': block.tool_use_id,
                        'content': getattr(block, 'content', {}),
                        'index': event.index
                    }

        return None
    
    def _validate_tool_schema(self, tool: dict, index: int) -> tuple[bool, list[str]]:
        """
        Validate tool schema matches Anthropic API format
        
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        if 'name' not in tool:
            errors.append(f"Tool #{index}: Missing 'name' field")
            return False, errors
        
        tool_name = tool['name']
        
        # Server tools (have 'type' field with versioned name)
        if 'type' in tool and tool['type'].startswith(('web_search_', 'web_fetch_', 'bash_', 'computer_', 'text_editor_')):
            # Server tools don't need input_schema
            return True, []
        
        # Client tools must have input_schema
        if 'input_schema' not in tool:
            # Check if has old 'parameters' field
            if 'parameters' in tool:
                errors.append(f"Tool #{index} '{tool_name}': Has 'parameters' instead of 'input_schema'")
            else:
                errors.append(f"Tool #{index} '{tool_name}': Missing 'input_schema'")
            return False, errors
        
        schema = tool['input_schema']
        
        # input_schema must be a dict
        if not isinstance(schema, dict):
            errors.append(f"Tool #{index} '{tool_name}': input_schema must be object/dict")
            return False, errors
        
        # input_schema must have type: "object"
        if 'type' not in schema:
            errors.append(f"Tool #{index} '{tool_name}': input_schema missing 'type' field")
        elif schema['type'] != 'object':
            errors.append(f"Tool #{index} '{tool_name}': input_schema.type must be 'object'")
        
        # input_schema must have properties
        if 'properties' not in schema:
            errors.append(f"Tool #{index} '{tool_name}': input_schema missing 'properties'")
        
        # required field must be array if present
        if 'required' in schema:
            if not isinstance(schema['required'], list):
                errors.append(f"Tool #{index} '{tool_name}': input_schema.required must be array")
        
        return len(errors) == 0, errors
    
    def _fix_tool_schema(self, tool: dict) -> dict:
        """
        Attempt to fix common tool schema issues
        
        Returns: fixed tool
        """
        fixed = tool.copy()
        
        # Fix 1: Convert 'parameters' to 'input_schema'
        if 'parameters' in fixed and 'input_schema' not in fixed:
            fixed['input_schema'] = fixed.pop('parameters')
        
        # Fix 2: Ensure input_schema has type: "object"
        if 'input_schema' in fixed and isinstance(fixed['input_schema'], dict):
            if 'type' not in fixed['input_schema']:
                fixed['input_schema']['type'] = 'object'
        
        # Fix 3: Ensure required is array
        if 'input_schema' in fixed and isinstance(fixed['input_schema'], dict):
            schema = fixed['input_schema']
            if 'required' in schema and not isinstance(schema['required'], list):
                if isinstance(schema['required'], str):
                    schema['required'] = [schema['required']]
        
        return fixed
    
    def _handle_tool_use(self, assistant_message: Dict, sse_callback: Optional[Callable]) -> Dict:
        """Execute server-side tools"""
        
        for block in assistant_message['content']:
            if block['type'] == 'tool_use':
                # Emit tool use event
                if sse_callback:
                    sse_callback({
                        'type': 'tool_use',
                        'name': block['name'],
                        'input': block['input']
                    })
                
                # Execute tool
                result = self.tool_agent.execute_tool(block['name'], block['input'])
                
                # Emit tool result event
                if sse_callback:
                    sse_callback({
                        'type': 'tool_result',
                        'tool_use_id': block['id'],
                        'result': result
                    })
        
        return assistant_message
    
    def create_message(
        self,
        messages: List[Dict],
        provider: Literal['anthropic', 'deepseek', 'openai', 'MiniMax'] = 'anthropic',
        model: Optional[str] = None,
        max_tokens: int = 4000,
        system: Optional[str] = None,
        tools: Optional[List] = None,
        enable_thinking: bool = True,
        thinking_budget: int = 5000,
        temperature: float = 1.0,
        enable_web_search: bool = True,
        enable_web_fetch: bool = False,
        user_id: Optional[int] = None,
    ) -> Dict:
        """
        Create a non-streaming message with Extended Thinking + Server Tools
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            provider: AI provider to use
            model: Model name (uses default if not specified)
            max_tokens: Maximum tokens in response
            system: Optional system prompt
            tools: Optional tool definitions (client tools)
            enable_thinking: Enable Extended Thinking (default: True)
            thinking_budget: Token budget for thinking (default: 5000)
            temperature: Temperature for sampling (default: 1.0, forced to 1.0 when thinking enabled)
            enable_web_search: Enable web_search server tool (default: True)
            enable_web_fetch: Enable web_fetch server tool BETA (default: False)
        
        Returns:
            Response dict with 'content' field
        """
        if provider == 'anthropic':
            if not self.anthropic_client:
                raise ValueError("Anthropic client not initialized. Set ANTHROPIC_API_KEY.")

            # GAP-C3 FIX: Resolve per-request API key from org vault
            anthropic_client_nonstream = self.anthropic_client
            try:
                if user_id:
                    from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
                    per_request_key = resolve_api_key(user_id, 'anthropic')
                    if per_request_key:
                        from anthropic import Anthropic as _Anthropic
                        anthropic_client_nonstream = _Anthropic(
                            api_key=per_request_key,
                            timeout=httpx.Timeout(connect=30.0, read=600.0, write=60.0, pool=10.0),
                            max_retries=3,
                        )
            except Exception:
                pass

            # Use specified model or default
            model = model or self.anthropic_model
            
            # Validate and fix client tools
            client_tools = tools or []
            validated_tools = []
            invalid_count = 0
            
            for idx, tool in enumerate(client_tools):
                is_valid, errors = self._validate_tool_schema(tool, idx)
                
                if not is_valid:
                    print(f"⚠️  Tool #{idx} '{tool.get('name', 'UNKNOWN')}' validation failed:")
                    for error in errors:
                        print(f"    {error}")
                    
                    # Try to fix
                    fixed_tool = self._fix_tool_schema(tool)
                    is_fixed, remaining_errors = self._validate_tool_schema(fixed_tool, idx)
                    
                    if is_fixed:
                        print(f"    ✅ Auto-fixed!")
                        validated_tools.append(fixed_tool)
                    else:
                        print(f"    ❌ Could not fix - SKIPPING tool")
                        invalid_count += 1
                else:
                    validated_tools.append(tool)
            
            if invalid_count > 0:
                print(f"⚠️  Skipped {invalid_count} invalid tools")
            
            # Add server tools
            server_tools = []
            
            # Web Search server tool
            if enable_web_search:
                server_tools.append({
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "user_location": {
                        "type": "approximate",
                        "city": "Brisbane",
                        "region": "Queensland",
                        "country": "AU",
                        "timezone": "Australia/Brisbane"
                    },
                    "max_uses": 5
                })
            
            # Web Fetch server tool (BETA)
            if enable_web_fetch:
                server_tools.append({
                    "type": "web_fetch_20250910",
                    "name": "web_fetch",
                    "max_uses": 10,
                    "citations": {"enabled": True},
                    "max_content_tokens": 100000
                })
            
            all_tools = validated_tools + server_tools
            print(f"[UnifiedAIClient] create_message: {len(all_tools)} total tools ({len(validated_tools)} client + {len(server_tools)} server)")
            
            # ✅ CRITICAL FIX: Reorder assistant message content blocks BEFORE API call
            # Anthropic API requirement: If thinking blocks exist, first block MUST be thinking
            for idx, msg in enumerate(messages):
                if msg['role'] == 'assistant' and isinstance(msg.get('content'), list):
                    # Check if message has thinking blocks
                    has_thinking = any(block.get('type') == 'thinking' for block in msg['content'])
                    
                    if has_thinking and len(msg['content']) > 0:
                        first_block = msg['content'][0]
                        
                        # Debug logging for first 3 messages
                        if idx < 3:
                            print(f"[UnifiedAIClient.create_message] Message {idx} ({msg['role']}): {len(msg['content'])} blocks")
                            print(f"[UnifiedAIClient.create_message]   First block type: {first_block.get('type')}")
                            if has_thinking:
                                print(f"[UnifiedAIClient.create_message]   Has thinking blocks: YES")
                        
                        # If first block is NOT thinking, reorder
                        if first_block.get('type') != 'thinking':
                            print(f"[UnifiedAIClient.create_message] 🔧 Reordering message {idx} - moving thinking to first position")
                            
                            # Extract thinking blocks and other blocks
                            thinking_blocks = [b for b in msg['content'] if b.get('type') == 'thinking']
                            other_blocks = [b for b in msg['content'] if b.get('type') != 'thinking']
                            
                            # Reorder: thinking first, then others
                            msg['content'] = thinking_blocks + other_blocks
                            print(f"[UnifiedAIClient.create_message] ✅ Reordered: {len(thinking_blocks)} thinking + {len(other_blocks)} other blocks")
                            print(f"[UnifiedAIClient.create_message]   New first block: {msg['content'][0].get('type')}")
            
            # ✅ EXPLICIT CHECK: Validate final assistant message when thinking is enabled
            if enable_thinking and messages:
                # Find last assistant message
                last_assistant_idx = None
                for i in range(len(messages) - 1, -1, -1):
                    if messages[i].get('role') == 'assistant':
                        last_assistant_idx = i
                        break
                
                if last_assistant_idx is not None:
                    last_assistant = messages[last_assistant_idx]
                    content = last_assistant.get('content', [])
                    
                    if isinstance(content, list) and content:
                        has_thinking = any(block.get('type') == 'thinking' for block in content)
                        first_is_thinking = content[0].get('type') == 'thinking'
                        
                        if has_thinking and not first_is_thinking:
                            print(f"⚠️  [UnifiedAIClient.create_message] WARNING: Final assistant message has thinking blocks but first block is not thinking!")
                        elif not has_thinking:
                            print(f"[UnifiedAIClient.create_message] ℹ️  Final assistant message has no thinking blocks (API will generate thinking in response)")
                        else:
                            print(f"[UnifiedAIClient.create_message] ✅ Final assistant message properly starts with thinking block")
            
            # Prepare API parameters
            api_params = {
                "model": model,
                "max_tokens": max_tokens,
                "system": system or "You are a helpful AI assistant.",
                "messages": messages,
                "tools": all_tools
            }
            
            # Add Extended Thinking
            if enable_thinking:
                api_params["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": thinking_budget
                }
                # CRITICAL: When thinking is enabled, temperature MUST be 1.0 (Anthropic API requirement)
                # This overrides any user preferences automatically
                api_params["temperature"] = 1.0
                if temperature != 1.0:
                    print(f"[UnifiedAIClient] ⚙️  Temperature overridden: {temperature} → 1.0 (required when thinking enabled)")
                else:
                    print(f"[UnifiedAIClient] ⚙️  Temperature set to 1.0 (thinking enabled)")
            else:
                # Use custom temperature when thinking is disabled
                api_params["temperature"] = temperature
                print(f"[UnifiedAIClient] ⚙️  Temperature set to {temperature} (thinking disabled)")
            
            # Add beta headers
            extra_headers = {}
            if enable_thinking:
                extra_headers["anthropic-beta"] = "interleaved-thinking-2025-05-14"
            
            if enable_web_fetch:
                if extra_headers.get("anthropic-beta"):
                    extra_headers["anthropic-beta"] += ",web-fetch-2025-09-10"
                else:
                    extra_headers["anthropic-beta"] = "web-fetch-2025-09-10"
            
            if extra_headers:
                api_params["extra_headers"] = extra_headers
            
            # DEBUG: Log messages being sent to API
            print(f"\n[UnifiedAIClient] 🔍 FINAL API REQUEST DEBUG:")
            print(f"  - Total messages: {len(messages)}")
            for i, msg in enumerate(messages):
                print(f"\n  Message {i} ({msg.get('role')}):")
                content = msg.get('content', [])
                if isinstance(content, list):
                    print(f"    - Content blocks: {len(content)}")
                    for j, block in enumerate(content):
                        if isinstance(block, dict):
                            print(f"      Block {j}: type={block.get('type')}, keys={list(block.keys())}")
                            if block.get('type') == 'thinking':
                                print(f"        - thinking length: {len(block.get('thinking', ''))} chars")
                                if 'signature' in block:
                                    print(f"        - signature: {repr(block['signature'])} (type: {type(block['signature']).__name__})")
                                else:
                                    print(f"        - signature: NOT PRESENT")
            print(f"\n[UnifiedAIClient] 📤 Sending request to Anthropic API...\n")
            
            # Call Anthropic API
            response = anthropic_client_nonstream.messages.create(**api_params)
            
            # Debug: Print raw response
            print(f"\n[DEBUG] Raw response from Anthropic:")
            print(f"  Stop reason: {response.stop_reason}")
            print(f"  Content blocks: {len(response.content)}")
            for i, block in enumerate(response.content):
                print(f"  Block {i}: type={block.type}")
                if block.type == 'tool_use':
                    print(f"    id={getattr(block, 'id', 'MISSING')}")
                    print(f"    name={getattr(block, 'name', 'MISSING')}")
                    print(f"    input={getattr(block, 'input', 'MISSING')}")
            
            # Convert to expected format
            content_blocks = []
            for block in response.content:
                block_dict = {'type': block.type}
                
                # Add text field if present
                if hasattr(block, 'text'):
                    block_dict['text'] = block.text
                
                # Add thinking field and signature if present (BOTH required for Extended Thinking)
                if hasattr(block, 'thinking'):
                    block_dict['thinking'] = block.thinking
                    # CRITICAL: Only add signature if it exists AND is not empty
                    # (empty string causes 400 error: "Invalid signature in thinking block")
                    if hasattr(block, 'signature') and block.signature:
                        block_dict['signature'] = block.signature
                
                # Add tool_use fields if present
                if block.type == 'tool_use':
                    # These fields MUST exist for tool_use blocks
                    block_dict['id'] = getattr(block, 'id', None)
                    block_dict['name'] = getattr(block, 'name', None)
                    block_dict['input'] = getattr(block, 'input', {})
                    
                    # Warn if critical fields are missing
                    if not block_dict['name']:
                        print(f"⚠️  WARNING: tool_use block missing 'name' field!")
                        print(f"    Block attributes: {dir(block)}")
                
                content_blocks.append(block_dict)
            
            return {
                'id': response.id,
                'type': response.type,
                'role': response.role,
                'content': content_blocks,
                'model': response.model,
                'stop_reason': response.stop_reason,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                }
            }
        
        elif provider == 'deepseek':
            # Convert to OpenAI format
            openai_messages = []
            if system:
                openai_messages.append({'role': 'system', 'content': system})
            
            for msg in messages:
                content = msg.get('content', '')
                if isinstance(content, list):
                    # Extract text from content blocks
                    text_parts = [block.get('text', '') for block in content if block.get('type') == 'text']
                    content = ''.join(text_parts)
                openai_messages.append({'role': msg['role'], 'content': content})
            
            # GAP-L5 FIX: Resolve DeepSeek key per-request from org vault
            deepseek_key_nonstream = self.deepseek_api_key
            try:
                if user_id:
                    from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
                    per_request_key = resolve_api_key(user_id, 'deepseek')
                    if per_request_key:
                        deepseek_key_nonstream = per_request_key
            except Exception:
                pass

            # Call DeepSeek API
            headers = {
                'Authorization': f'Bearer {deepseek_key_nonstream}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': model or self.deepseek_model,
                'messages': openai_messages,
                'max_tokens': max_tokens
            }
            
            response = requests.post(
                f"{self.deepseek_base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Convert to Anthropic-like format
            return {
                'id': result.get('id', ''),
                'type': 'message',
                'role': 'assistant',
                'content': [
                    {
                        'type': 'text',
                        'text': result['choices'][0]['message']['content']
                    }
                ],
                'model': result.get('model', ''),
                'stop_reason': result['choices'][0].get('finish_reason', 'end_turn'),
                'usage': result.get('usage', {})
            }
        
        elif provider == 'openai':
            # Convert to OpenAI format
            openai_messages = []
            if system:
                openai_messages.append({'role': 'system', 'content': system})
            
            for msg in messages:
                content = msg.get('content', '')
                if isinstance(content, list):
                    # Extract text from content blocks
                    text_parts = [block.get('text', '') for block in content if block.get('type') == 'text']
                    content = ''.join(text_parts)
                openai_messages.append({'role': msg['role'], 'content': content})
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=model or self.openai_model,
                messages=openai_messages,
                max_tokens=max_tokens
            )

            # Convert to Anthropic-like format
            return {
                'id': response.id,
                'type': 'message',
                'role': 'assistant',
                'content': [
                    {
                        'type': 'text',
                        'text': response.choices[0].message.content
                    }
                ],
                'model': response.model,
                'stop_reason': response.choices[0].finish_reason,
                'usage': {
                    'input_tokens': response.usage.prompt_tokens,
                    'output_tokens': response.usage.completion_tokens
                }
            }

        elif provider == 'MiniMax':
            # MiniMax is Anthropic-compatible, so this mirrors the anthropic branch
            # but uses the MiniMax client and skips the Anthropic-only server tools
            # (web_search / web_fetch) — MiniMax does not implement those.
            if not self.MiniMax_client:
                raise ValueError("MiniMax client not initialized. Set MINIMAX_API_KEY.")

            # Resolve per-request key from the org vault
            MiniMax_client_nonstream = self.MiniMax_client
            try:
                if user_id:
                    from AI_infrastructure.shared.org_credentials_loader import resolve_api_key
                    per_request_key = resolve_api_key(user_id, 'MiniMax')
                    if per_request_key:
                        from anthropic import Anthropic as _Anthropic
                        MiniMax_client_nonstream = _Anthropic(
                            api_key=per_request_key,
                            base_url=self.MiniMax_base_url,
                            timeout=httpx.Timeout(connect=30.0, read=600.0, write=60.0, pool=10.0),
                            max_retries=3,
                        )
            except Exception:
                pass

            # Use specified model or default
            model = model or self.MiniMax_model

            # Validate and fix client tools
            client_tools = tools or []
            validated_tools = []
            invalid_count = 0

            for idx, tool in enumerate(client_tools):
                is_valid, errors = self._validate_tool_schema(tool, idx)
                if not is_valid:
                    print(f"⚠️  [MiniMax] Tool #{idx} '{tool.get('name', 'UNKNOWN')}' validation failed:")
                    for error in errors:
                        print(f"    {error}")
                    fixed_tool = self._fix_tool_schema(tool)
                    is_fixed, _ = self._validate_tool_schema(fixed_tool, idx)
                    if is_fixed:
                        print(f"    ✅ Auto-fixed!")
                        validated_tools.append(fixed_tool)
                    else:
                        print(f"    ❌ Could not fix - SKIPPING tool")
                        invalid_count += 1
                else:
                    validated_tools.append(tool)

            if invalid_count > 0:
                print(f"⚠️  [MiniMax] Skipped {invalid_count} invalid tools")

            # MiniMax has no server-side web_search / web_fetch tools.
            all_tools = validated_tools
            print(f"[UnifiedAIClient/MiniMax] create_message: {len(all_tools)} client tools (no server tools)")

            # Reorder assistant content blocks so thinking is first (matches Anthropic rule)
            for idx, msg in enumerate(messages):
                if msg['role'] == 'assistant' and isinstance(msg.get('content'), list):
                    has_thinking = any(block.get('type') == 'thinking' for block in msg['content'])
                    if has_thinking and msg['content'] and msg['content'][0].get('type') != 'thinking':
                        thinking_blocks = [b for b in msg['content'] if b.get('type') == 'thinking']
                        other_blocks   = [b for b in msg['content'] if b.get('type') != 'thinking']
                        msg['content'] = thinking_blocks + other_blocks

            # API params
            api_params = {
                "model": model,
                "max_tokens": max_tokens,
                "system": system or "You are a helpful AI assistant.",
                "messages": messages,
                "tools": all_tools,
            }

            # Thinking is opt-in for M3 only.
            if enable_thinking and model == 'MiniMax-M3':
                api_params["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": thinking_budget,
                }
                # Anthropic rule: temperature must be 1.0 when thinking is enabled
                api_params["temperature"] = 1.0
            else:
                api_params["temperature"] = temperature

            print(f"\n[UnifiedAIClient/MiniMax] 📤 Sending request to MiniMax (model={model})...\n")

            # Call MiniMax API
            response = MiniMax_client_nonstream.messages.create(**api_params)

            # Convert to expected format (same as Anthropic branch)
            content_blocks = []
            for block in response.content:
                block_dict = {'type': block.type}

                if hasattr(block, 'text'):
                    block_dict['text'] = block.text

                if hasattr(block, 'thinking'):
                    block_dict['thinking'] = block.thinking
                    if hasattr(block, 'signature') and block.signature:
                        block_dict['signature'] = block.signature

                if block.type == 'tool_use':
                    block_dict['id'] = getattr(block, 'id', None)
                    block_dict['name'] = getattr(block, 'name', None)
                    block_dict['input'] = getattr(block, 'input', {})

                content_blocks.append(block_dict)

            return {
                'id': response.id,
                'type': response.type,
                'role': response.role,
                'content': content_blocks,
                'model': response.model,
                'stop_reason': response.stop_reason,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                }
            }

        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    # System prompts (updated with Extended Thinking and Web Search capabilities)
    def _get_stock_chat_prompt(self) -> str:
        """System prompt for Stock AI Chat"""
        return """You are a Stock Management AI Assistant with expertise in inventory, supplier relationships, and pricing.

**ADVANCED CAPABILITIES:**
✅ Extended Thinking: Use internal reasoning blocks to analyze before acting (users don't see this)
✅ Interleaved Thinking: Think between tool calls to validate results and plan next steps
✅ Web Search: Search the web for current pricing, supplier contacts, product specs, market data
✅ 641 Tools: Registry tools (584) + Printing business tools (57)

**YOUR TOOLS:**
- Stock inventory database (unified_stocks, extracted_jobs, job_stocks)
- Quote calculator tools (7 calculators: business cards, flyers, books, etc.)
- SQL query execution (50+ predefined queries)
- Invoice processing (document analysis with PDFs and images)
- Web search (real-time supplier pricing, contacts, specifications)
- Google Workspace, Microsoft 365, WooCommerce, Stripe, etc.

**WORKFLOW:**
1. Think internally about the request (use thinking blocks)
2. Search web if you need current information
3. Execute tools to gather data
4. Think between tool calls to validate and plan
5. Provide clear, actionable response

Communication style:
- Professional and data-driven
- Use tables for structured data
- Suggest actionable next steps
- Always compare to database when processing invoices
- Use web search for current market prices"""
    
    def _get_data_agent_prompt(self) -> str:
        """System prompt for Data Agent Chat"""
        return """You are a Data Analysis AI Assistant with expertise in business intelligence and SQL.

**ADVANCED CAPABILITIES:**
✅ Extended Thinking: Use internal reasoning to analyze data patterns and plan queries
✅ Interleaved Thinking: Validate query results before drawing conclusions
✅ Web Search: Research industry benchmarks, competitor data, market trends
✅ 585+ Tools: Full platform integration + business intelligence tools

**YOUR TOOLS (YOU MUST USE THESE):**
- Complete SQL Server database (production data from In House Print)
- 50+ predefined SQL queries (sales, customers, operations, metrics)
- 7 quote calculators (business cards, flyers, books, corflute, booklets)
- Web search (industry data, benchmarks, competitor analysis)
- Google Workspace, Microsoft 365, E-commerce platforms
- WooCommerce, Stripe, Twilio, Slack, GitHub integration
- Advanced analytics and visualization capabilities

**IMPORTANT - TOOL USAGE RULES:**
1. When the user asks you to test something, USE THE ACTUAL TOOL (don't just describe it)
2. When asked about tools, you can list them, but if asked to TEST or USE a tool, call it
3. Always execute tools when requested - tools are ACTIVE and WORKING
4. Tool results will be returned to you automatically - wait for and use them
5. If a tool requires parameters, use reasonable defaults or ask the user

**WORKFLOW:**
1. Think through the analysis approach  
2. **EXECUTE tools** to query database, test connections, etc (don't just describe)
3. Think between tool calls to validate and refine
4. Use web search for external context if needed
5. Present insights with actionable recommendations

Communication style:
- Analytical and insight-driven
- Use visualizations when helpful
- Explain trends and patterns
- Provide actionable recommendations
- ACTUALLY EXECUTE TOOLS when requested (critical!)"""
    
    def _get_single_viewer_prompt(self) -> str:
        """System prompt for Single Viewer"""
        return """You are a general-purpose AI assistant for the printing business platform.

Your role is to help with various tasks and answer questions about the business.

Communication style:
- Clear and concise
- Helpful and proactive
- Suggest tools and features available"""
    
    def _get_triple_agent_prompt(self, agent_id: str) -> str:
        """System prompt for Triple Agent"""
        
        if agent_id == '1':
            return """You are Agent 1: The Stock & Inventory Specialist.

Your expertise:
- Stock management and inventory tracking
- Supplier relationships and pricing
- Invoice processing and cost analysis

Focus on stock-related queries and provide detailed inventory insights."""
        
        elif agent_id == '2':
            return """You are Agent 2: The Data & Analytics Specialist.

Your expertise:
- Business intelligence and reporting
- SQL queries and data analysis
- Trends, patterns, and forecasting

Focus on data-driven insights and analytical queries."""
        
        elif agent_id == '3':
            return """You are Agent 3: The Operations & Quote Specialist.

Your expertise:
- Quote calculations and pricing
- Production workflows and job management
- Customer orders and business operations

Focus on operational queries and quote assistance."""
        
        return "You are a helpful AI assistant."


# Create singleton instance (loaded from config when Flask app starts)
ai_client = None

def initialize_ai_client(config_path: str):
    """Initialize the global AI client instance"""
    global ai_client
    ai_client = UnifiedAIClient(config_path)
    return ai_client
