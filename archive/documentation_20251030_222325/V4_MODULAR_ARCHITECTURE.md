# 🏗️ V4 MODULAR ARCHITECTURE PLAN

## 📋 EXECUTIVE SUMMARY

**Goal:** Break V4 monolithic file into small, testable modules with comprehensive logging

**Benefits:**
-  Easy to troubleshoot (logs show exactly which module failed)
-  Easy to test (each module independent)
-  Easy to debug (small files, clear responsibilities)
-  Easy to maintain (update one module without breaking others)
-  Easy to extend (add new modules without touching existing code)

---

## 📁 PROPOSED FOLDER STRUCTURE

```
AI_infrastructure/
├── routes/
│   ├── agent_routes_v4.py          # Main Flask blueprint (200 lines)
│   └── __init__.py
│
├── core/
│   ├── __init__.py
│   ├── tool_executor.py            # ToolExecutor class (150 lines)
│   ├── tool_processor.py           # ToolCallProcessor class (100 lines)
│   ├── conversation_manager.py     # Multi-turn loop logic (200 lines)
│   ├── session_handler.py          # Session loading/saving (100 lines)
│   └── response_serializer.py      # Content serialization (150 lines)
│
├── builders/
│   ├── __init__.py
│   ├── user_profile_builder.py     # Fetch user data from DB (150 lines)
│   ├── system_prompt_builder.py    # Build comprehensive prompt (300 lines)
│   ├── tool_schema_converter.py    # Convert schemas to Anthropic format (100 lines)
│   └── credential_fetcher.py       # Fetch OAuth credentials (100 lines)
│
├── meta_tools/
│   ├── __init__.py
│   ├── platform_tools_lister.py    # list_platform_tools handler (100 lines)
│   ├── platform_guide_provider.py  # get_platform_guide handler (500 lines)
│   ├── workflow_instructor.py      # get_workflow_instructions handler (400 lines)
│   └── smart_tool_instructor.py    # get_smart_tool_instructions handler (300 lines)
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                   # Centralized logging config (100 lines)
│   ├── error_handler.py            # Error recovery logic (150 lines)
│   ├── validators.py               # Input validation (100 lines)
│   └── formatters.py               # Response formatting (100 lines)
│
└── config/
    ├── __init__.py
    ├── logging_config.py           # Logging configuration (50 lines)
    └── constants.py                # Constants (MAX_TURNS, etc.) (50 lines)
```

**Total:** 13 modules + 1 main routes file = 14 files  
**Average size:** 150 lines per module (vs 2000 lines monolithic)

---

## 🎯 MODULE BREAKDOWN

### 1️⃣ **routes/agent_routes_v4.py** (Main Flask Blueprint)
**Size:** ~200 lines  
**Responsibility:** Flask routes only, delegates to modules

```python
"""
V4 Agent Routes - Modular Architecture
Main Flask blueprint that delegates to specialized modules
"""

from flask import Blueprint, request, jsonify
from utils.logger import get_logger
from core.conversation_manager import ConversationManager
from builders.user_profile_builder import UserProfileBuilder
from builders.system_prompt_builder import SystemPromptBuilder

logger = get_logger(__name__)

agent_bp = Blueprint('agent_v4', __name__)

@agent_bp.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint - delegates to ConversationManager"""
    logger.info("📨 Received chat request")
    
    try:
        data = request.get_json()
        message = data.get('message')
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        
        logger.debug(f"Request: message={message[:50]}..., session={session_id}, user={user_id}")
        
        # Delegate to conversation manager
        manager = ConversationManager()
        response = manager.handle_chat(message, session_id, user_id)
        
        logger.info(f" Chat completed: tools_used={len(response.get('tools_used', []))}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f" Chat failed: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@agent_bp.route('/tools', methods=['GET'])
def list_tools():
    """List available tools"""
    # Implementation...

@agent_bp.route('/status', methods=['GET'])
def status():
    """Health check"""
    # Implementation...
```

**Logging Points:**
- Request received
- Request parameters
- Delegation to manager
- Response summary
- Errors with stack trace

---

### 2️⃣ **core/tool_executor.py** (Tool Execution)
**Size:** ~150 lines  
**Responsibility:** Validate and execute tools with credential injection

```python
"""
Tool Executor - Validates and executes tools with credential injection
"""

from utils.logger import get_logger
from tools.registry_v3 import get_registry

logger = get_logger(__name__)

class ToolExecutor:
    def __init__(self):
        self.registry = get_registry()
        logger.info(f"🔧 ToolExecutor initialized: {len(self.registry.tools)} tools")
    
    def validate_tool_call(self, tool_name, parameters):
        """Validate tool call before execution"""
        logger.debug(f"🔍 Validating: {tool_name} with {len(parameters)} params")
        
        # Validation logic...
        
        logger.debug(f" Validation passed: {tool_name}")
        return True, None
    
    def inject_credentials(self, params, user_id, credentials):
        """Inject user credentials into parameters"""
        logger.debug(f"🔐 Injecting credentials for user {user_id}")
        
        # Injection logic...
        
        logger.debug(f" Credentials injected: _user_id, _injected_credentials")
        return injected_params
    
    def execute_tool(self, tool_name, parameters, user_id, credentials):
        """Execute tool with error handling"""
        logger.info(f"⚙️ Executing: {tool_name}")
        
        try:
            # Validate
            is_valid, error = self.validate_tool_call(tool_name, parameters)
            if not is_valid:
                logger.error(f" Validation failed: {error}")
                raise ValueError(error)
            
            # Inject credentials
            params = self.inject_credentials(parameters, user_id, credentials)
            
            # Get function
            func = self.registry.get_tool_function(tool_name)
            logger.debug(f"📦 Retrieved function: {func.__name__}")
            
            # Execute
            result = func(**params)
            
            logger.info(f" Execution successful: {tool_name}")
            return result
            
        except Exception as e:
            logger.error(f" Execution failed: {tool_name} - {e}", exc_info=True)
            raise
```

**Logging Points:**
- Initialization (tool count)
- Validation start/result
- Credential injection
- Function retrieval
- Execution start/result
- Errors with context

---

### 3️⃣ **core/conversation_manager.py** (Multi-Turn Loop)
**Size:** ~200 lines  
**Responsibility:** Orchestrate multi-turn conversations with Claude

```python
"""
Conversation Manager - Multi-turn conversation orchestration
"""

from utils.logger import get_logger
from core.tool_executor import ToolExecutor
from core.session_handler import SessionHandler
from builders.user_profile_builder import UserProfileBuilder
from builders.system_prompt_builder import SystemPromptBuilder
from config.constants import MAX_TURNS
from anthropic import Anthropic
import os

logger = get_logger(__name__)

class ConversationManager:
    def __init__(self):
        self.tool_executor = ToolExecutor()
        self.session_handler = SessionHandler()
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        logger.info("💬 ConversationManager initialized")
    
    def handle_chat(self, message, session_id, user_id):
        """Main chat handling with multi-turn loop"""
        logger.info(f"🚀 Starting chat: session={session_id}, user={user_id}")
        
        try:
            # Load session
            logger.debug("📂 Loading session...")
            session = self.session_handler.load_session(session_id)
            conversation = session.get('conversation', [])
            logger.debug(f" Session loaded: {len(conversation)} messages")
            
            # Build user profile
            logger.debug("👤 Building user profile...")
            profile = UserProfileBuilder().build(user_id)
            logger.debug(f" Profile built: {profile['name']}, platform={profile['platform']}")
            
            # Build system prompt
            logger.debug("📝 Building system prompt...")
            system_prompt = SystemPromptBuilder().build(profile)
            logger.debug(f" System prompt built: {len(system_prompt)} chars")
            
            # Add user message
            conversation.append({"role": "user", "content": message})
            
            # Multi-turn loop
            logger.info(f"🔄 Starting multi-turn loop (max {MAX_TURNS} turns)")
            ai_response = ""
            tools_used = []
            current_turn = 0
            
            while current_turn < MAX_TURNS:
                current_turn += 1
                logger.info(f"📍 Turn {current_turn}/{MAX_TURNS}")
                
                # Call Claude
                logger.debug("🤖 Calling Claude API...")
                response_obj = self.client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=16000,
                    system=system_prompt,
                    messages=conversation,
                    tools=self.load_tools(),
                    tool_choice={"type": "auto"}
                )
                logger.debug(f" Claude responded: stop_reason={response_obj.stop_reason}")
                
                # Process response
                has_tool_use = False
                for block in response_obj.content:
                    if block.type == "text":
                        ai_response += block.text
                        logger.debug(f"📄 Text block: {len(block.text)} chars")
                    
                    elif block.type == "tool_use":
                        has_tool_use = True
                        logger.info(f"🔧 Tool use: {block.name}")
                        
                        # Execute tool
                        result = self.tool_executor.execute_tool(
                            block.name,
                            block.input,
                            user_id,
                            profile.get('credentials')
                        )
                        
                        tools_used.append({
                            "name": block.name,
                            "success": True
                        })
                        
                        # Add to conversation
                        conversation.append({
                            "role": "assistant",
                            "content": response_obj.content
                        })
                        conversation.append({
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": str(result)
                            }]
                        })
                
                # Check if done
                if not has_tool_use or response_obj.stop_reason != "tool_use":
                    logger.info(f" Conversation complete after {current_turn} turns")
                    break
            
            # Save session
            logger.debug("💾 Saving session...")
            self.session_handler.save_session(session_id, conversation)
            
            logger.info(f"🎉 Chat completed: {len(tools_used)} tools used")
            return {
                "response": ai_response,
                "tools_used": tools_used,
                "turns": current_turn
            }
            
        except Exception as e:
            logger.error(f" Chat failed: {e}", exc_info=True)
            raise
```

**Logging Points:**
- Session loading
- Profile building
- System prompt building
- Each turn start
- Claude API call
- Tool execution
- Loop completion
- Session saving
- Final summary

---

### 4️⃣ **builders/user_profile_builder.py** (User Context)
**Size:** ~150 lines  
**Responsibility:** Fetch user data, OAuth status, location

```python
"""
User Profile Builder - Fetch comprehensive user context
"""

from utils.logger import get_logger
import sqlite3
import requests
from pathlib import Path
from datetime import datetime, timezone

logger = get_logger(__name__)

class UserProfileBuilder:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / 'ai_infrastructure.db'
        logger.debug(f"📊 UserProfileBuilder initialized: db={self.db_path}")
    
    def build(self, user_id):
        """Build comprehensive user profile"""
        logger.info(f"👤 Building profile for user {user_id}")
        
        try:
            # Fetch from database
            logger.debug("🔍 Querying database...")
            profile = self._fetch_user_data(user_id)
            logger.debug(f" User data: {profile['username']}, {profile['email']}")
            
            # Fetch OAuth status
            logger.debug("🔐 Checking OAuth status...")
            oauth = self._fetch_oauth_status(user_id)
            profile['google_oauth'] = oauth['google']
            profile['microsoft_oauth'] = oauth['microsoft']
            logger.debug(f" OAuth: Google={oauth['google']}, Microsoft={oauth['microsoft']}")
            
            # Get location
            logger.debug("🌍 Fetching location...")
            location = self._fetch_location(profile.get('ip'))
            profile['location'] = location
            logger.debug(f" Location: {location.get('city')}, {location.get('country')}")
            
            logger.info(f" Profile complete: {profile['username']}")
            return profile
            
        except Exception as e:
            logger.error(f" Profile build failed: {e}", exc_info=True)
            raise
    
    def _fetch_user_data(self, user_id):
        """Fetch user from database"""
        # Implementation...
    
    def _fetch_oauth_status(self, user_id):
        """Check OAuth credentials"""
        # Implementation...
    
    def _fetch_location(self, ip_address):
        """Get location from IP"""
        # Implementation...
```

**Logging Points:**
- Builder initialization
- Database query
- OAuth check
- Location fetch
- Success/failure for each step

---

### 5️⃣ **builders/system_prompt_builder.py** (Comprehensive Prompt)
**Size:** ~300 lines  
**Responsibility:** Build platform-aware system prompt

```python
"""
System Prompt Builder - Build comprehensive AI prompt
"""

from utils.logger import get_logger

logger = get_logger(__name__)

class SystemPromptBuilder:
    def build(self, user_profile):
        """Build comprehensive system prompt"""
        logger.info("📝 Building system prompt")
        
        try:
            sections = []
            
            # User context
            logger.debug("👤 Adding user context section...")
            sections.append(self._build_user_context(user_profile))
            
            # Platform guidance
            logger.debug("🏢 Adding platform guidance...")
            sections.append(self._build_platform_guidance(user_profile))
            
            # Tool usage patterns
            logger.debug("🔧 Adding tool usage patterns...")
            sections.append(self._build_tool_patterns())
            
            # Anti-XML instructions
            logger.debug("⚠️ Adding anti-XML instructions...")
            sections.append(self._build_anti_xml_instructions())
            
            prompt = "\n\n".join(sections)
            logger.info(f" System prompt built: {len(prompt)} chars, {len(sections)} sections")
            return prompt
            
        except Exception as e:
            logger.error(f" Prompt build failed: {e}", exc_info=True)
            raise
    
    def _build_user_context(self, profile):
        """Build user context section"""
        logger.debug(f"Building context for {profile['username']}")
        # Implementation...
    
    def _build_platform_guidance(self, profile):
        """Build platform-specific guidance"""
        platform = profile.get('platform', 'none')
        logger.debug(f"Building guidance for platform: {platform}")
        # Implementation...
    
    def _build_tool_patterns(self):
        """Build tool usage patterns"""
        # Implementation...
    
    def _build_anti_xml_instructions(self):
        """Build explicit anti-XML instructions"""
        # Implementation...
```

**Logging Points:**
- Prompt building start
- Each section addition
- Final prompt stats
- Errors

---

### 6️⃣ **utils/logger.py** (Centralized Logging)
**Size:** ~100 lines  
**Responsibility:** Configure logging for all modules

```python
"""
Centralized Logging Configuration
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
LOG_FILE = LOGS_DIR / f'v4_agent_{datetime.now().strftime("%Y%m%d")}.log'
DEBUG_FILE = LOGS_DIR / f'v4_debug_{datetime.now().strftime("%Y%m%d")}.log'

# Format
LOG_FORMAT = '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def get_logger(name):
    """Get a configured logger instance"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Console handler (INFO level)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        logger.addHandler(console_handler)
        
        # File handler (INFO level)
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        logger.addHandler(file_handler)
        
        # Debug file handler (DEBUG level)
        debug_handler = logging.FileHandler(DEBUG_FILE, encoding='utf-8')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        logger.addHandler(debug_handler)
        
        logger.propagate = False
    
    return logger

# Export convenience function
__all__ = ['get_logger']
```

**Features:**
-  Console output (INFO level)
-  Daily log files (INFO level)
-  Daily debug files (DEBUG level)
-  UTF-8 encoding
-  Timestamp, module, function, line number
-  Easy to use: `logger = get_logger(__name__)`

---

## 📊 LOGGING LEVELS STRATEGY

### INFO Level (Always On)
-  Request received
-  Major steps (session loaded, profile built, prompt built)
-  Tool execution started/completed
-  Turn progress
-  Final result summary
-  Errors

**Example Log:**
```
[2025-10-30 10:15:23] INFO [agent_routes_v4.chat:15] 📨 Received chat request
[2025-10-30 10:15:23] INFO [conversation_manager.handle_chat:25] 🚀 Starting chat: session=abc123, user=1
[2025-10-30 10:15:23] INFO [user_profile_builder.build:20] 👤 Building profile for user 1
[2025-10-30 10:15:24] INFO [conversation_manager.handle_chat:55] 🔄 Starting multi-turn loop (max 20 turns)
[2025-10-30 10:15:24] INFO [conversation_manager.handle_chat:60] 📍 Turn 1/20
[2025-10-30 10:15:25] INFO [tool_executor.execute_tool:45] ⚙️ Executing: gmail_list_messages
[2025-10-30 10:15:26] INFO [tool_executor.execute_tool:65]  Execution successful: gmail_list_messages
[2025-10-30 10:15:26] INFO [conversation_manager.handle_chat:95]  Conversation complete after 1 turns
[2025-10-30 10:15:26] INFO [conversation_manager.handle_chat:102] 🎉 Chat completed: 1 tools used
```

### DEBUG Level (Debug File Only)
- 🔍 Request parameters
- 🔍 Database queries
- 🔍 API call details
- 🔍 Tool validation details
- 🔍 Credential injection
- 🔍 Response processing
- 🔍 Session data

**Example Debug Log:**
```
[2025-10-30 10:15:23] DEBUG [agent_routes_v4.chat:20] Request: message=List my Gmail messages, session=abc123, user=1
[2025-10-30 10:15:23] DEBUG [session_handler.load_session:15] Query: SELECT * FROM sessions WHERE id='abc123'
[2025-10-30 10:15:23] DEBUG [session_handler.load_session:20]  Session loaded: 5 messages
[2025-10-30 10:15:24] DEBUG [user_profile_builder._fetch_user_data:40] Query: SELECT * FROM users WHERE id=1
[2025-10-30 10:15:24] DEBUG [user_profile_builder.build:30]  User data: john@example.com
[2025-10-30 10:15:25] DEBUG [tool_executor.validate_tool_call:18] 🔍 Validating: gmail_list_messages with 2 params
[2025-10-30 10:15:25] DEBUG [tool_executor.inject_credentials:28] 🔐 Injecting credentials for user 1
```

### ERROR Level (All Outputs)
-  All exceptions with stack traces
-  Validation failures
-  Tool execution failures
-  Database errors
-  API errors

---

## 🧪 TESTING STRATEGY FOR MODULES

### Test Each Module Independently

**1. Test tool_executor.py:**
```python
# test_tool_executor.py
from core.tool_executor import ToolExecutor

executor = ToolExecutor()

# Test validation
is_valid, error = executor.validate_tool_call("gmail_send_email", {
    "to": "test@example.com",
    "subject": "Test",
    "body": "Body"
})
assert is_valid, f"Validation failed: {error}"

# Test credential injection
params = executor.inject_credentials(
    {"to": "test@example.com"},
    user_id=1,
    credentials={"access_token": "abc123"}
)
assert "_user_id" in params
assert "_injected_credentials" in params
```

**2. Test user_profile_builder.py:**
```python
# test_user_profile_builder.py
from builders.user_profile_builder import UserProfileBuilder

builder = UserProfileBuilder()
profile = builder.build(user_id=1)

assert profile['username']
assert profile['email']
assert 'google_oauth' in profile
assert 'location' in profile
```

**3. Test system_prompt_builder.py:**
```python
# test_system_prompt_builder.py
from builders.system_prompt_builder import SystemPromptBuilder

builder = SystemPromptBuilder()
prompt = builder.build({
    "username": "John",
    "platform": "google",
    "google_oauth": True
})

assert len(prompt) > 100
assert "John" in prompt
assert "Google" in prompt or "Gmail" in prompt
```

---

## 🚀 IMPLEMENTATION STAGES

### Stage 1: Create Folder Structure (5 min)
```powershell
cd AI_infrastructure
mkdir core, builders, meta_tools, utils, config
```

### Stage 2: Implement Logger First (10 min)
- Create `utils/logger.py`
- Test logging works
- All other modules will use this

### Stage 3: Extract ToolExecutor (15 min)
- Move from agent_routes_v4.py to `core/tool_executor.py`
- Add logging throughout
- Test independently

### Stage 4: Extract Other Core Modules (20 min)
- `core/tool_processor.py`
- `core/session_handler.py`
- `core/response_serializer.py`

### Stage 5: Create Builder Modules (30 min)
- `builders/user_profile_builder.py`
- `builders/system_prompt_builder.py`
- `builders/tool_schema_converter.py`
- `builders/credential_fetcher.py`

### Stage 6: Create ConversationManager (20 min)
- `core/conversation_manager.py`
- Orchestrates all other modules
- Multi-turn loop logic

### Stage 7: Implement Meta-Tools (40 min)
- `meta_tools/platform_tools_lister.py`
- `meta_tools/platform_guide_provider.py`
- `meta_tools/workflow_instructor.py`
- `meta_tools/smart_tool_instructor.py`

### Stage 8: Simplify Main Routes (10 min)
- `routes/agent_routes_v4.py` becomes just Flask routes
- Delegates to ConversationManager

**Total: ~150 minutes (2.5 hours)**

---

##  BENEFITS OF MODULAR ARCHITECTURE

### 1. **Easy Troubleshooting**
```
Error occurs → Check logs → See which module failed → Fix that module
```

**Example:**
```
[ERROR] [user_profile_builder.build:30]  Profile build failed: table not found
```
→ Clear: Issue is in user_profile_builder, database table missing

### 2. **Easy Testing**
```
Test 1 module → Fix issues → Test next module → Fix issues → etc.
```

**Example:**
```python
# Test just the tool executor
pytest tests/test_tool_executor.py -v
```

### 3. **Easy Debugging**
```
Small files → Easy to read → Easy to understand → Easy to fix
```

**Example:**
- Old: Find bug in 4815-line file (needle in haystack)
- New: Find bug in 150-line module (easy to spot)

### 4. **Easy Maintenance**
```
Update 1 module → Other modules unaffected → Safe changes
```

**Example:**
- Update system prompt builder → Doesn't touch tool executor
- Add new meta-tool → Doesn't affect conversation manager

### 5. **Easy Extension**
```
Add new module → Import where needed → Done
```

**Example:**
- Add `builders/context_enhancer.py` → Import in conversation_manager → Works

---

## 📋 SUMMARY

**Proposal:**
-  Break V4 into 13 small modules (~150 lines each)
-  Add comprehensive logging (INFO + DEBUG levels)
-  Organize in folders by responsibility
-  Each module independently testable
-  Main routes file becomes simple (200 lines)

**Timeline:**
- 2.5 hours to create all modules
- Test as we go (easier than testing monolith)
- Deploy when all modules pass tests

**Benefits:**
- Easy to troubleshoot (logs show exact module)
- Easy to test (small, independent modules)
- Easy to maintain (update one module safely)
- Easy to extend (add new modules)
- Professional architecture (industry standard)

---

## 🎯 READY TO START?

**Next Steps:**
1. Create folder structure
2. Implement logger first
3. Extract modules one by one
4. Test each module
5. Integrate into main routes

**Shall I begin implementing the modular architecture?**
