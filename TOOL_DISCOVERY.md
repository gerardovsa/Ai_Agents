# Tool Discovery - Registry and Semantic Search System

> **📋 Consolidated Documentation** - This file consolidates 20+ scattered tool discovery documentation files. See [AI_DOCUMENTATION_CONSOLIDATION_INSTRUCTIONS.md](.github/AI_DOCUMENTATION_CONSOLIDATION_INSTRUCTIONS.md) for consolidation process.

---

## Overview

### What is the Tool Discovery System?

The Tool Discovery system provides **intelligent, progressive discovery of 594 tools** across 20+ platforms without overwhelming the AI with massive token payloads. Instead of sending all tool schemas upfront, the system uses a **4-tier progressive discovery architecture** that enables Just-In-Time (JIT) learning.

**Key Components:**
- **RegistryV3** - Auto-loads and manages 594 tools from modular plugin system
- **Module Plugin Loader** - Discovers tools from `UI/modules_external/*/tools/*.json`
- **Meta-Tools** - 6 discovery tools (search_tools, get_tool_schema, list_platform_tools, etc.)
- **Semantic Search** - PersistentSemanticToolSearch with embeddings cached in Supabase
- **Intelligent Discovery** - Hybrid scoring combining semantic + keyword + platform filtering

**The Problem It Solves:**

**❌ Naive Approach:**
```json
{
  "tools": [
    {"name": "gmail_send_email", ...},
    {"name": "gmail_get_message", ...},
    // ... 592 more tools ...
  ]
}
```
- Token explosion: 594 tools × 500 tokens = **297,000 tokens**
- Exceeds Claude 200K context limit
- Massive API costs on every request
- AI overwhelmed with irrelevant tools

**✅ Progressive Discovery:**
```
Round 1: AI gets 6 meta-tools (discovery layer)
Round 2: AI discovers relevant platform tools (gmail_*)
Round 3: AI gets schema for specific tool (gmail_send_email)
Round 4: AI executes tool
```
- Initial payload: ~3,000 tokens (6 tools)
- Only loads what's needed, when it's needed
- 95% accuracy with semantic search

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    TOOL DISCOVERY SYSTEM                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  1. REGISTRY V3 (tools/registry_v3.py)             │    │
│  │     - Auto-loads 594 tools at server startup       │    │
│  │     - Module plugin system (UI/modules_external/)  │    │
│  │     - Converts to Anthropic-compatible format      │    │
│  │     - Redis caching (1-hour TTL, 50x faster)       │    │
│  │     - Thread-local user_id storage                 │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  2. MODULE PLUGIN LOADER                           │    │
│  │     (tools/plugins/module_plugin_loader.py)        │    │
│  │     - Scans UI/modules_external/*/tools/*.json     │    │
│  │     - Loads tool definitions dynamically           │    │
│  │     - Links to implementations/*_wrapper.py        │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  3. META-TOOLS (tools/implementations/)            │    │
│  │     - list_available_platforms()                   │    │
│  │     - list_platform_tools(platform)                │    │
│  │     - search_tools(query)                          │    │
│  │     - get_tool_schema(tool_name)                   │    │
│  │     - execute_tool(tool_name, **params)            │    │
│  │     - recommend_tools_for_task(task)               │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  4. SEMANTIC SEARCH (persistent_semantic_search.py)│    │
│  │     - Sentence transformers (all-MiniLM-L6-v2)     │    │
│  │     - 384-dim embeddings cached in Supabase        │    │
│  │     - Version hash checks (regenerate only on      │    │
│  │       tool changes)                                │    │
│  │     - Cosine similarity search (<10ms)             │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  5. INTELLIGENT DISCOVERY (intelligent_discovery.py)│   │
│  │     - Hybrid scoring (semantic + keyword + context)│    │
│  │     - Platform filtering (OAuth-based)             │    │
│  │     - Conversation context awareness               │    │
│  │     - 95% accuracy                                 │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### The 4-Tier Progressive Discovery Model

```
TIER 1: NAVIGATION TOOLS (Always Available)
├── list_available_platforms() - "What platforms exist?"
├── search_tools(query) - "Find tools matching keyword"
└── recommend_tools_for_task(task) - "What tools do I need for X?"

TIER 2: PLATFORM DISCOVERY
├── list_platform_tools("gmail") - "What Gmail tools exist?"
├── list_platform_tools("microsoft_word") - "What Word tools?"
└── Platform aliases: "google" → all google_* tools

TIER 3: SCHEMA RETRIEVAL
├── get_tool_schema("gmail_send_email") - "How do I use this tool?"
└── Returns: Full parameter schema, examples, required fields

TIER 4: EXECUTION
├── execute_tool("gmail_send_email", to="john@example.com", ...)
└── Direct tool calls: gmail_send_email(to="...", subject="...", ...)
```

**Data Flow Example:**

```
User: "Send an email to john@example.com"
           │
           ▼
┌─────────────────────────────────────┐
│  AI Agent (Claude)                  │
│  Initial Tools: 6 meta-tools        │
└──────────────┬──────────────────────┘
               │
               │ TIER 1: Discovery
               ▼
┌─────────────────────────────────────┐
│  list_available_platforms()         │
│  Returns: ["gmail", "google_sheets",│
│            "microsoft_outlook", ...] │
└──────────────┬──────────────────────┘
               │
               │ TIER 2: Platform Selection
               ▼
┌─────────────────────────────────────┐
│  list_platform_tools("gmail")       │
│  Returns: [                         │
│    "gmail_send_email",              │
│    "gmail_get_message",             │
│    "gmail_list_messages"            │
│  ]                                  │
└──────────────┬──────────────────────┘
               │
               │ TIER 3: Schema Fetch
               ▼
┌─────────────────────────────────────┐
│  get_tool_schema("gmail_send_email")│
│  Returns: {                         │
│    parameters: {                    │
│      to: {type: "string"},          │
│      subject: {type: "string"},     │
│      body: {type: "string"}         │
│    }                                │
│  }                                  │
└──────────────┬──────────────────────┘
               │
               │ TIER 4: Execution
               ▼
┌─────────────────────────────────────┐
│  execute_tool("gmail_send_email",   │
│    to="john@example.com",           │
│    subject="Hello",                 │
│    body="Meeting tomorrow?"         │
│  )                                  │
└─────────────────────────────────────┘
```

---

## Core Modules

### RegistryV3

**File:** `tools/registry_v3.py` (1,075 lines)

**Responsibilities:**
1. Auto-load tool schemas from `tools/schemas/*.json`
2. Load module plugins from `UI/modules_external/*/tools/*.json`
3. Convert tool definitions to Anthropic-compatible format
4. Provide meta-tools for discovery
5. Execute tools with credential injection
6. Cache loaded tools in Redis (1-hour TTL)
7. Track tool usage with ToolIntelligenceLogger

**Initialization Flow:**

```python
class RegistryV3:
    def __init__(self):
        # 1. Try loading from Redis cache (50x faster on hit)
        if self._load_from_cache():
            return  # Cache hit!
        
        # 2. Cache miss - load from disk
        self._load_schemas()  # Load tools/schemas/*.json
        self._load_implementations()  # Link to Python functions
        self._load_module_plugins()  # Load UI/modules_external/
        
        # 3. Save to cache for next startup
        self._save_to_cache()
```

**Key Methods:**

```python
def get_tool_schema(self, tool_name: str) -> Dict:
    """Get complete schema for a specific tool"""
    return self.tools.get(tool_name)

def execute_tool(self, tool_name: str, **kwargs) -> Any:
    """
    Execute tool with automatic credential injection.
    
    Injects:
    - _user_id: From thread-local storage or Flask g context
    - _injected_credentials: OAuth tokens for Google/Microsoft
    """
    # Get user_id from thread-local storage (worker threads)
    user_id = self._thread_local.user_id if hasattr(self._thread_local, 'user_id') else None
    
    # Inject credentials
    if user_id:
        kwargs['_user_id'] = user_id
        kwargs['_injected_credentials'] = self._get_credentials(user_id)
    
    # Execute implementation function
    impl_func = self.implementations[tool_name]
    return impl_func(**kwargs)

def set_thread_user_id(self, user_id: int):
    """Store user_id in thread-local storage for worker threads"""
    self._thread_local.user_id = user_id

def get_thread_user_id(self) -> Optional[int]:
    """Retrieve user_id from thread-local storage"""
    return getattr(self._thread_local, 'user_id', None)
```

**Redis Caching:**

```python
def _load_from_cache(self) -> bool:
    """Load tools from Redis cache (1-hour TTL)"""
    if not self.redis_manager or not self.redis_manager.connected:
        return False
    
    cached = self.redis_manager.get_with_ttl('tool_registry:v3:tools')
    if cached and isinstance(cached, dict):
        self.tools = cached
        return True
    return False

def _save_to_cache(self):
    """Save tools to Redis with 1-hour TTL"""
    if self.redis_manager and self.redis_manager.connected:
        self.redis_manager.set_with_ttl(
            'tool_registry:v3:tools',
            self.tools,
            ttl=3600  # 1 hour
        )
```

**Tool Intelligence Logging:**

```python
# Track tool usage patterns for AI learning
if self.intelligence_logger:
    self.intelligence_logger.log_tool_call(
        tool_name=tool_name,
        user_id=user_id,
        parameters=kwargs,
        success=True,
        duration_ms=duration
    )
```

---

### Module Plugin Loader

**File:** `tools/plugins/module_plugin_loader.py`

**Purpose:** Automatically discover and load tool definitions from modular plugin directories.

**Directory Structure:**
```
UI/modules_external/
├── quote-calculator/
│   ├── tools/
│   │   ├── calculator_tools.json       # Tool definitions
│   │   └── calculator_guide.json       # Guide tool
│   └── implementations/
│       └── calculator_wrapper.py       # Python implementations
├── shopify/
│   ├── tools/
│   │   └── shopify_tools.json
│   └── implementations/
│       └── shopify_wrapper.py
├── xero/
│   ├── tools/
│   │   └── xero_tools.json
│   └── implementations/
│       └── xero_wrapper.py
└── inhouse-print/
    ├── tools/
    │   └── inhouse_tools.json
    └── implementations/
        └── inhouse_wrapper.py
```

**Loading Process:**

```python
def load_module_plugins() -> Dict[str, Any]:
    """
    Scan UI/modules_external/ for plugin modules.
    
    Returns:
        {
            "tools": {...},  # All discovered tool schemas
            "implementations": {...},  # All @tool_executor functions
            "modules_loaded": 15
        }
    """
    modules_dir = Path("UI/modules_external")
    
    for module_dir in modules_dir.iterdir():
        if not module_dir.is_dir():
            continue
        
        # Load tool definitions from tools/*.json
        tools_dir = module_dir / "tools"
        if tools_dir.exists():
            for json_file in tools_dir.glob("*.json"):
                with open(json_file, encoding='utf-8') as f:
                    tools = json.load(f)
                    # Merge into registry
        
        # Load implementations from implementations/*_wrapper.py
        impl_dir = module_dir / "implementations"
        if impl_dir.exists():
            for py_file in impl_dir.glob("*_wrapper.py"):
                # Import module and extract @tool_executor functions
                module = importlib.import_module(f"UI.modules_external.{module_dir.name}.implementations.{py_file.stem}")
                # Register functions
```

**@tool_executor Decorator:**

```python
# In calculator_wrapper.py
from tools.registry_v3 import tool_executor

@tool_executor()
def calculate_booklets(quantity: int, pages: int, **kwargs):
    """
    Calculate quote for saddle-stitched booklets.
    
    Args:
        quantity: Number of booklets
        pages: Number of pages per booklet
    
    Returns:
        {
            "success": True,
            "price": 1250.00,
            "breakdown": {...}
        }
    """
    # Implementation
    return {"success": True, "price": calculate_price(...)}
```

---

### Meta-Tools

**File:** `tools/implementations/meta_tools.py` (1,027 lines)

**The 6 Discovery Tools:**

#### 1. list_available_platforms()

**Purpose:** List all platforms that have tools available.

**Returns:**
```json
{
  "success": true,
  "platforms": [
    "gmail",
    "google_sheets",
    "google_docs",
    "microsoft_outlook",
    "microsoft_word",
    "quote_calculator",
    "xero",
    "shopify"
  ],
  "platform_count": 20,
  "tool_counts": {
    "gmail": 15,
    "quote_calculator": 80,
    "xero": 39
  },
  "total_tools": 594
}
```

#### 2. list_platform_tools(platform)

**Purpose:** List all tools for a specific platform (names + descriptions only, NO parameter schemas).

**Platform Aliases:**
```python
platform_aliases = {
    'microsoft': ['microsoft_'],  # All microsoft_* tools
    'm365': ['microsoft_'],
    'office': ['microsoft_outlook', 'microsoft_word', 'microsoft_excel'],
    'outlook': ['microsoft_outlook_'],
    'google': ['google_', 'gmail_'],  # All Google tools
    'gmail': ['gmail_'],
    'sheets': ['google_sheets_'],
    'synergy': ['synergy_'],
    'agent': ['assign_and_activate', 'request_update', 'respond_to']
}
```

**Example:**
```python
list_platform_tools("gmail")

# Returns:
{
  "success": true,
  "platform": "gmail",
  "tools": [
    {
      "name": "gmail_send_email",
      "short_description": "Send email via Gmail"
    },
    {
      "name": "gmail_get_message",
      "short_description": "Retrieve specific email by ID"
    },
    {
      "name": "gmail_list_messages",
      "short_description": "List emails with filters"
    }
  ],
  "tool_count": 15
}
```

#### 3. search_tools(query)

**Purpose:** Keyword search across all tools (name, description, platform).

**Features:**
- Case-insensitive matching
- Searches tool name, description, short_description, platform
- Returns relevance-sorted results
- Supports multi-word queries

**Example:**
```python
search_tools("send email")

# Returns:
{
  "success": true,
  "query": "send email",
  "tools": [
    {
      "name": "gmail_send_email",
      "platform": "gmail",
      "short_description": "Send email via Gmail",
      "relevance_score": 2  # Matches both "send" and "email"
    },
    {
      "name": "microsoft_outlook_send_email",
      "platform": "microsoft_outlook",
      "short_description": "Send email via Outlook",
      "relevance_score": 2
    }
  ],
  "result_count": 8
}
```

#### 4. get_tool_schema(tool_name)

**Purpose:** Get complete parameter schema for a specific tool.

**Returns:**
```json
{
  "success": true,
  "tool_name": "gmail_send_email",
  "schema": {
    "name": "gmail_send_email",
    "description": "Send an email using Gmail API...",
    "parameters": {
      "type": "object",
      "properties": {
        "to": {
          "type": "string",
          "description": "Recipient email address"
        },
        "subject": {
          "type": "string",
          "description": "Email subject line"
        },
        "body": {
          "type": "string",
          "description": "Email body (plain text or HTML)"
        },
        "cc": {
          "type": "array",
          "items": {"type": "string"},
          "description": "CC recipients (optional)"
        }
      },
      "required": ["to", "subject", "body"]
    },
    "platform": "gmail"
  }
}
```

#### 5. execute_tool(tool_name, **params)

**Purpose:** Execute a tool with automatic credential injection.

**Features:**
- Injects `_user_id` from thread-local storage
- Injects `_injected_credentials` (OAuth tokens)
- Validates parameters against schema
- Returns tool result

**Example:**
```python
execute_tool(
    "gmail_send_email",
    to="john@example.com",
    subject="Meeting Tomorrow",
    body="Can we meet at 2pm?"
)

# Returns:
{
  "success": true,
  "message_id": "msg_abc123",
  "thread_id": "thread_xyz789"
}
```

#### 6. recommend_tools_for_task(task)

**Purpose:** Intelligent task-based tool recommendations with workflow steps.

**Features:**
- Intent detection (email, calendar, document creation, data analysis, quote calculation)
- Multi-step workflow guidance
- Parameter extraction from task description
- Platform preference hints

**Example:**
```python
recommend_tools_for_task("Generate quote for 500 booklets with 24 pages")

# Returns:
{
  "success": true,
  "task": "Generate quote for 500 booklets with 24 pages",
  "intent": "quote_calculation",
  "confidence": 0.95,
  "recommended_tools": [
    {
      "name": "inhouse_get_domain_guide",
      "step": 1,
      "reason": "REQUIRED: Get context about InHouse Print quote calculator domains",
      "priority": "required"
    },
    {
      "name": "calculate_booklets",
      "step": 2,
      "reason": "Calculate quote for saddle-stitched booklets",
      "priority": "primary",
      "suggested_params": {
        "quantity": 500,
        "pages": 24
      }
    }
  ],
  "workflow_steps": [
    "Call inhouse_get_domain_guide() to understand calculator structure",
    "Call calculate_booklets(quantity=500, pages=24, ...)",
    "Return calculated quote with price breakdown"
  ]
}
```

---

### Persistent Semantic Search

**File:** `tools/persistent_semantic_search.py` (443 lines)

**Purpose:** Fast semantic tool search using sentence transformers with Supabase-backed persistence.

**Technology:**
- **Model:** sentence-transformers `all-MiniLM-L6-v2`
- **Embedding Dimensions:** 384
- **Storage:** Supabase PostgreSQL with pgvector extension
- **Search Algorithm:** Cosine similarity
- **Performance:** <10ms per search (cached embeddings)

**Database Schema:**

```sql
-- Tool embeddings storage
CREATE TABLE ai_infrastructure.tool_embeddings (
    tool_name TEXT PRIMARY KEY,
    embedding vector(384),  -- pgvector type
    tool_metadata JSONB,
    version_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cache metadata
CREATE TABLE ai_infrastructure.tool_embedding_cache (
    cache_key TEXT PRIMARY KEY,
    version_hash TEXT,
    total_tools INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast similarity search
CREATE INDEX ON ai_infrastructure.tool_embeddings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);
```

**Initialization Strategy:**

```python
class PersistentSemanticToolSearch:
    def __init__(self, registry, force_regenerate=False):
        # 1. Load sentence-transformers model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 2. Calculate version hash (checksum of all tool definitions)
        self.version_hash = self._calculate_version_hash()
        
        # 3. Try loading from Supabase
        if not force_regenerate:
            if self._load_from_supabase():
                print(f"✅ Loaded {len(self.tool_embeddings)} from Supabase")
                return
        
        # 4. Generate embeddings (cache miss or forced regenerate)
        self._generate_embeddings()
        
        # 5. Store in Supabase for next startup
        self._store_to_supabase()
```

**Version Hash Check:**

```python
def _calculate_version_hash(self) -> str:
    """
    Calculate SHA256 hash of all tool definitions.
    Used to detect when tools have changed.
    """
    tool_data = []
    for tool_name in sorted(self.registry.tools.keys()):
        tool = self.registry.tools[tool_name]
        tool_data.append(json.dumps({
            'name': tool_name,
            'description': tool.get('description', ''),
            'platform': tool.get('platform', ''),
            'short_description': tool.get('short_description', '')
        }, sort_keys=True))
    
    combined = '||'.join(tool_data)
    return hashlib.sha256(combined.encode()).hexdigest()
```

**Loading from Supabase:**

```python
def _load_from_supabase(self) -> bool:
    """Load embeddings from Supabase if up-to-date"""
    from AI_infrastructure.shared.database_utils import execute_query
    
    # Check cache metadata
    cache_info = execute_query(
        """SELECT version_hash, total_tools FROM ai_infrastructure.tool_embedding_cache
           WHERE cache_key = 'semantic_tool_search'""",
        fetch_mode='one'
    )
    
    if not cache_info or cache_info['version_hash'] != self.version_hash:
        return False  # Cache outdated
    
    # Load embeddings
    rows = execute_query(
        """SELECT tool_name, embedding, tool_metadata 
           FROM ai_infrastructure.tool_embeddings""",
        fetch_mode='all'
    )
    
    for row in rows:
        self.tool_embeddings[row['tool_name']] = np.array(row['embedding'])
        self.tool_metadata[row['tool_name']] = row['tool_metadata']
    
    return True
```

**Semantic Search:**

```python
def search_tools(self, query_text: str, top_k: int = 8, min_similarity: float = 0.3) -> List[Dict]:
    """
    Semantic search for tools using cosine similarity.
    
    Args:
        query_text: User's natural language query
        top_k: Number of results to return
        min_similarity: Minimum cosine similarity threshold (0.0-1.0)
    
    Returns:
        List of tools sorted by relevance with similarity scores
    """
    if not self.available:
        return []
    
    # Generate query embedding
    query_embedding = self.model.encode(query_text, convert_to_numpy=True)
    
    # Calculate cosine similarity with all tools
    similarities = {}
    for tool_name, tool_embedding in self.tool_embeddings.items():
        similarity = np.dot(query_embedding, tool_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(tool_embedding)
        )
        if similarity >= min_similarity:
            similarities[tool_name] = similarity
    
    # Sort by similarity and return top_k
    sorted_tools = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    results = []
    for tool_name, similarity in sorted_tools:
        metadata = self.tool_metadata[tool_name]
        results.append({
            'tool_name': tool_name,
            'similarity': similarity,
            'platform': metadata.get('platform'),
            'short_description': metadata.get('short_description'),
            'description': metadata.get('description')
        })
    
    return results
```

**Performance:**
- First run: ~500ms (generate 594 embeddings)
- Subsequent runs: <10ms (load from Supabase)
- Search: <10ms (cosine similarity with 594 vectors)

---

### Intelligent Discovery

**File:** `tools/intelligent_discovery.py`

**Purpose:** Hybrid tool discovery combining semantic search, keyword matching, and platform filtering.

**Features:**
1. **Semantic Search** - sentence-transformers embeddings
2. **Keyword Matching** - Pattern matching in tool names/descriptions
3. **Platform Filtering** - OAuth-based (Google vs Microsoft)
4. **Conversation Context** - Analyze previous messages
5. **Hybrid Scoring** - Combine multiple signals

**Scoring Algorithm:**

```python
def calculate_hybrid_score(
    tool_name: str,
    semantic_score: float,
    keyword_matches: int,
    platform_match: bool,
    context_relevance: float
) -> float:
    """
    Hybrid scoring combining multiple signals.
    
    Weights:
    - Semantic similarity: 40%
    - Keyword matches: 30%
    - Platform match: 20%
    - Context relevance: 10%
    """
    score = (
        semantic_score * 40.0 +
        min(keyword_matches, 3) * 10.0 +
        (20.0 if platform_match else 0.0) +
        context_relevance * 10.0
    )
    return score
```

**Platform Filtering:**

```python
def filter_by_platform(tools: List[Dict], user_id: int) -> List[Dict]:
    """
    Filter tools based on user's OAuth platform.
    
    If user authenticated with Google:
    - Include: gmail_, google_*
    - Exclude: microsoft_*
    
    If user authenticated with Microsoft:
    - Include: microsoft_*
    - Exclude: gmail_, google_*
    """
    from AI_infrastructure.shared.database_utils import execute_query
    
    # Get user's connected platforms
    platforms = execute_query(
        """SELECT platform FROM user_oauth_tokens WHERE user_id = %s""",
        (user_id,),
        fetch_mode='all'
    )
    
    connected_platforms = [p['platform'] for p in platforms]
    
    filtered_tools = []
    for tool in tools:
        platform = tool.get('platform', '')
        
        # Check if platform is accessible
        if 'google' in connected_platforms and platform.startswith(('gmail', 'google_')):
            filtered_tools.append(tool)
        elif 'microsoft' in connected_platforms and platform.startswith('microsoft_'):
            filtered_tools.append(tool)
        elif platform not in ['gmail', 'google_sheets', 'microsoft_outlook']:
            # Platform-agnostic tool (e.g., quote_calculator, xero)
            filtered_tools.append(tool)
    
    return filtered_tools
```

**Usage in Agent Routes:**

```python
# agent_routes_v4.py line ~1050

from tools.persistent_semantic_search import PersistentSemanticToolSearch

# Get semantic search instance (cached globally)
semantic_search = get_semantic_search(registry)

if semantic_search:
    # Search for relevant tools
    suggested_tools = semantic_search.search_tools(
        query_text=user_message,
        top_k=8,
        min_similarity=0.3
    )
    
    # Filter by user's auth platform
    if auth_platform == 'microsoft':
        suggested_tools = [
            tool for tool in suggested_tools 
            if tool['platform'] not in google_platforms
        ]
    elif auth_platform == 'google':
        suggested_tools = [
            tool for tool in suggested_tools 
            if tool['platform'] not in microsoft_platforms
        ]
    
    # Inject into system prompt
    intelligent_tool_suggestions = build_suggestions_block(suggested_tools)
    system_prompt += intelligent_tool_suggestions
```

**Suggestion Block Format:**

```
═══════════════════════════════════════════════════════════════
🎯 INTELLIGENT TOOL SUGGESTIONS (Pre-searched for this query)
═══════════════════════════════════════════════════════════════

Based on semantic analysis, these tools are most relevant:

1. calculate_booklets [quote_calculator] 🔥
   Calculate quote for saddle-stitched booklets
   Similarity: 87%
   ⚠️  MUST call first: inhouse_get_domain_guide() → inhouse_calculator_guide()

2. calculate_perfect_bound [quote_calculator] ✅
   Calculate quote for perfect-bound books
   Similarity: 72%

3. calculate_flyers [quote_calculator] ✅
   Calculate quote for flyers and posters
   Similarity: 65%

How to Use These Suggestions:
- Similarity scores are suggestions, not certainty
- 🔥 ≥70% = High confidence (still verify with get_tool_schema)
- ✅ ≥50% = Medium confidence (validate carefully)
- 💡 <50% = Low confidence (consider manual search_tools())
- Always call GUIDE tools FIRST before using suggested tools
═══════════════════════════════════════════════════════════════
```

---

## Implementation Details

### Tool Schema Format

**Anthropic-Compatible Schema:**

```json
{
  "name": "gmail_send_email",
  "description": "Send an email using Gmail API. Supports HTML formatting, attachments, CC/BCC recipients, and threading. Uses OAuth credentials from user's connected Google account.",
  "input_schema": {
    "type": "object",
    "properties": {
      "to": {
        "type": "string",
        "description": "Recipient email address (required)"
      },
      "subject": {
        "type": "string",
        "description": "Email subject line"
      },
      "body": {
        "type": "string",
        "description": "Email body (supports plain text or HTML)"
      },
      "cc": {
        "type": "array",
        "items": {"type": "string"},
        "description": "CC recipients (optional)"
      },
      "bcc": {
        "type": "array",
        "items": {"type": "string"},
        "description": "BCC recipients (optional)"
      },
      "attachments": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "filename": {"type": "string"},
            "content": {"type": "string"},
            "mimetype": {"type": "string"}
          }
        },
        "description": "File attachments (optional)"
      }
    },
    "required": ["to", "subject", "body"]
  },
  "platform": "gmail",
  "short_description": "Send email via Gmail"
}
```

**Extended Metadata (for semantic search):**

```json
{
  "name": "calculate_booklets",
  "description": "...",
  "platform": "quote_calculator",
  "short_description": "Calculate quote for saddle-stitched booklets",
  "tags": ["printing", "booklets", "saddle-stitch", "quote", "pricing"],
  "category": "Quote Calculation",
  "domain": "booklets_and_magazines",
  "requires_guide": true,
  "guide_tools": ["inhouse_get_domain_guide", "inhouse_calculator_guide"],
  "examples": [
    {
      "description": "500 x 24-page booklets",
      "parameters": {
        "quantity": 500,
        "pages": 24,
        "stock_type": "satin_350gsm",
        "sides": 2
      }
    }
  ]
}
```

---

### Credential Injection

**Problem:** OAuth tokens should never be in tool parameters (security risk, token exposure).

**Solution:** Automatic credential injection via Registry.

**Flow:**

```python
# User calls tool (NO credentials in params)
execute_tool("gmail_send_email", to="john@example.com", subject="Hi", body="Hello")

# Registry injects credentials automatically
def execute_tool(self, tool_name: str, **kwargs) -> Any:
    # Get user_id from thread-local storage
    user_id = self.get_thread_user_id()
    
    # Fetch OAuth tokens from database
    credentials = self._get_credentials(user_id)
    
    # Inject into kwargs (hidden from AI)
    kwargs['_user_id'] = user_id
    kwargs['_injected_credentials'] = credentials
    
    # Execute implementation
    return self.implementations[tool_name](**kwargs)

# Implementation receives credentials
@tool_executor()
def gmail_send_email(to: str, subject: str, body: str, _injected_credentials=None, **kwargs):
    # Use _injected_credentials to authenticate with Gmail API
    service = build_gmail_service(_injected_credentials['google'])
    service.users().messages().send(...)
```

**Thread-Local Storage (Worker Threads):**

```python
# Flask g context doesn't transfer to worker threads
# Solution: Thread-local storage

class RegistryV3:
    _thread_local = threading.local()
    
    def set_thread_user_id(self, user_id: int):
        """Store user_id in thread-local storage"""
        self._thread_local.user_id = user_id
    
    def get_thread_user_id(self) -> Optional[int]:
        """Retrieve user_id from thread-local storage"""
        return getattr(self._thread_local, 'user_id', None)

# In agent worker thread
from tools.registry_v3 import get_registry
registry = get_registry()
registry.set_thread_user_id(user_id)  # Set once per request

# All subsequent tool calls have access to user_id
execute_tool("gmail_send_email", ...)  # user_id injected automatically
```

---

### Platform Detection & Email Rules

**InHouse Print Staff Detection:**

**Rule:** If user's email contains `_@inhouseprint.com.au`, prioritize InHouse tools.

**Implementation:**

```python
# In agent_routes_v4.py system prompt construction

if email_address and "_@inhouseprint.com.au" in email_address:
    system_prompt += """
    
    ═══════════════════════════════════════════════════════════════
    🏢 INHOUSE PRINT STAFF DETECTED
    ═══════════════════════════════════════════════════════════════
    
    The user is an InHouse Print employee. ALWAYS:
    
    1. PRIORITIZE InHouse tools FIRST:
       - inhouse_get_domain_guide()
       - inhouse_calculator_guide()
       - inhouse_execute_sql()
       - calculate_* tools (booklets, flyers, business cards, etc.)
    
    2. REQUIRED WORKFLOW for quote calculations:
       Step 1: Call inhouse_get_domain_guide() to list all domains
       Step 2: Call inhouse_calculator_guide(domain) for specific calculator
       Step 3: Call calculate_[product](...) with parameters
    
    3. For database queries:
       - Use inhouse_execute_sql(query) for Fred database
       - SQL Server syntax (TOP instead of LIMIT)
       - Tables: JobTickets, Customers, Products, etc.
    
    ═══════════════════════════════════════════════════════════════
    """
```

**Microsoft vs Google Detection:**

```python
# Check user's OAuth platform
auth_platform = user_prefs.get('preferred_platform', 'auto')

if auth_platform == 'microsoft':
    system_prompt += """
    
    MANDATORY PLATFORM: Microsoft 365 Suite
    - Use microsoft_outlook_* for emails
    - Use microsoft_word_* for documents
    - Use microsoft_excel_* for spreadsheets
    - Use microsoft_teams_* for collaboration
    
    DO NOT use Google tools (gmail_, google_docs_, etc.)
    """

elif auth_platform == 'google':
    system_prompt += """
    
    MANDATORY PLATFORM: Google Workspace
    - Use gmail_* for emails
    - Use google_docs_* for documents
    - Use google_sheets_* for spreadsheets
    - Use google_drive_* for file storage
    
    DO NOT use Microsoft tools (microsoft_outlook_, etc.)
    """
```

---

## Configuration

### Environment Variables

```bash
# Semantic search
SEMANTIC_SEARCH_ENABLED=true
SENTENCE_TRANSFORMERS_HOME=/app/.cache/torch

# Redis caching (optional)
REDIS_URL=redis://localhost:6379
REDIS_ENABLED=true

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### Registry Initialization

**Flask App Startup:**

```python
# flask_app.py

from tools.registry_v3 import get_registry

# Initialize registry at startup (loads all tools)
registry = get_registry()
print(f"[OK] Registry initialized: {len(registry.tools)} tools loaded")

# Initialize semantic search (cached globally)
from tools.persistent_semantic_search import PersistentSemanticToolSearch
semantic_search = PersistentSemanticToolSearch(registry)
```

**Global Singleton Pattern:**

```python
# tools/registry_v3.py

_global_registry = None

def get_registry() -> RegistryV3:
    """Get global registry instance (singleton)"""
    global _global_registry
    if _global_registry is None:
        _global_registry = RegistryV3()
    return _global_registry
```

---

## Critical Fixes

### Fix 1: Thread-Local User ID Storage (Jan 13, 2026)

**Problem:** Flask `g` context doesn't transfer to worker threads, causing `_user_id` injection to fail.

**Root Cause:** Background threads (agent workers) don't have access to Flask request context.

**Solution:**

```python
class RegistryV3:
    # Thread-local storage for user_id
    _thread_local = threading.local()
    
    def set_thread_user_id(self, user_id: int):
        """Store user_id in thread-local storage for this worker thread"""
        self._thread_local.user_id = user_id
    
    def get_thread_user_id(self) -> Optional[int]:
        """Retrieve user_id from thread-local storage"""
        return getattr(self._thread_local, 'user_id', None)
```

**Usage in Worker:**

```python
# agent_worker.py

def agent_worker(thread_id, user_id, message, ...):
    from tools.registry_v3 import get_registry
    
    registry = get_registry()
    registry.set_thread_user_id(user_id)  # Set once per request
    
    # All tool calls now have access to user_id
    # ...
```

**Status:** ✅ COMPLETE

---

### Fix 2: Redis Caching Performance (Dec 17, 2025)

**Problem:** Loading 594 tool schemas from disk takes ~500ms on every server restart.

**Solution:** Cache loaded tools in Redis with 1-hour TTL.

**Implementation:**

```python
def __init__(self):
    # Try loading from Redis cache
    if self._load_from_cache():
        logger.info("[CACHE] Loaded from Redis (50x faster)")
        return
    
    # Cache miss - load from disk
    self._load_schemas()
    self._load_implementations()
    self._load_module_plugins()
    
    # Save to cache
    self._save_to_cache()

def _load_from_cache(self) -> bool:
    """Load tools from Redis (1-hour TTL)"""
    if not self.redis_manager:
        return False
    
    cached = self.redis_manager.get_with_ttl('tool_registry:v3:tools')
    if cached:
        self.tools = cached
        return True
    return False
```

**Performance:**
- Before: ~500ms to load 594 tools
- After: ~10ms on cache hit (50x faster)

**Status:** ✅ COMPLETE

---

### Fix 3: Persistent Semantic Embeddings (Jan 2, 2026)

**Problem:** Regenerating 594 tool embeddings on every server restart takes ~500ms.

**Solution:** Store embeddings in Supabase with version hash checking.

**Implementation:**

```python
def __init__(self, registry):
    # Calculate version hash (checksum of all tools)
    self.version_hash = self._calculate_version_hash()
    
    # Try loading from Supabase
    if self._load_from_supabase():
        print("✅ Loaded embeddings from Supabase")
        return
    
    # Regenerate if cache miss or version mismatch
    self._generate_embeddings()
    self._store_to_supabase()
```

**Performance:**
- First run: ~500ms (generate + store)
- Subsequent runs: <10ms (load from Supabase)
- Only regenerates when tools change (version hash mismatch)

**Status:** ✅ COMPLETE

---

### Fix 4: Module Plugin UTF-8 Encoding (Nov 2025)

**Problem:** Tool JSON files with emoji characters causing `UnicodeDecodeError`.

**Root Cause:** JSON files opened without explicit UTF-8 encoding.

**Solution:**

```python
# Before (BROKEN):
with open(json_file) as f:
    tools = json.load(f)

# After (FIXED):
with open(json_file, encoding='utf-8') as f:
    tools = json.load(f)
```

**Status:** ✅ COMPLETE

---

### Fix 5: Microsoft Tool Instance Detection (Date Unknown)

**Problem:** Microsoft tools failing with "object has no attribute" errors.

**Root Cause:** Tool implementations expecting class instance, but receiving module.

**Solution:**

```python
def execute_tool(self, tool_name: str, **kwargs):
    impl = self.implementations[tool_name]
    
    # Detect if impl is a class instance method
    if hasattr(impl, '__self__'):
        # It's a bound method, call directly
        return impl(**kwargs)
    
    # Check for global class instances
    module = sys.modules.get(impl.__module__)
    if module:
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if hasattr(attr, tool_name):
                # Found class instance with this method
                method = getattr(attr, tool_name)
                return method(**kwargs)
    
    # Fallback: call as function
    return impl(**kwargs)
```

**Status:** ✅ COMPLETE

---

## Testing

### Manual Testing Checklist

**Meta-Tool Discovery:**
- [ ] `list_available_platforms()` returns 20+ platforms
- [ ] `list_platform_tools("gmail")` returns 15+ Gmail tools
- [ ] `list_platform_tools("microsoft")` returns all microsoft_* tools
- [ ] `search_tools("send email")` finds gmail_send_email and microsoft_outlook_send_email
- [ ] `get_tool_schema("gmail_send_email")` returns complete parameter schema
- [ ] `execute_tool("gmail_send_email", ...)` successfully sends email

**Semantic Search:**
- [ ] First server startup generates embeddings and stores in Supabase
- [ ] Second server startup loads from Supabase (fast)
- [ ] `search_tools("quote for booklets")` returns calculate_booklets with high similarity
- [ ] Platform filtering excludes Google tools for Microsoft users
- [ ] Version hash changes trigger regeneration

**Module Plugin Loading:**
- [ ] Quote calculator tools loaded (80 tools)
- [ ] Shopify tools loaded
- [ ] Xero tools loaded (39 tools)
- [ ] InHouse Print tools loaded
- [ ] Tool implementations callable via @tool_executor

**Credential Injection:**
- [ ] `_user_id` injected from thread-local storage
- [ ] `_injected_credentials` contains OAuth tokens
- [ ] Google tools receive Google OAuth credentials
- [ ] Microsoft tools receive Microsoft OAuth credentials

---

### Automated Tests

**Registry Tests:**

```python
def test_registry_initialization():
    from tools.registry_v3 import get_registry
    
    registry = get_registry()
    
    # Verify tool count
    assert len(registry.tools) >= 594
    
    # Verify platforms loaded
    platforms = {tool.get('platform') for tool in registry.tools.values()}
    assert 'gmail' in platforms
    assert 'quote_calculator' in platforms
    assert 'xero' in platforms

def test_tool_schema_retrieval():
    registry = get_registry()
    
    schema = registry.get_tool_schema('gmail_send_email')
    
    assert schema is not None
    assert schema['name'] == 'gmail_send_email'
    assert 'input_schema' in schema
    assert 'to' in schema['input_schema']['properties']

def test_credential_injection():
    registry = get_registry()
    
    # Set user_id in thread-local storage
    registry.set_thread_user_id(1)
    
    # Execute tool (should inject credentials)
    # Mock implementation to verify credentials passed
    result = registry.execute_tool('gmail_send_email', to='test@example.com', ...)
    
    assert '_user_id' in result  # Verify injection occurred
```

**Semantic Search Tests:**

```python
def test_semantic_search_initialization():
    from tools.persistent_semantic_search import PersistentSemanticToolSearch
    from tools.registry_v3 import get_registry
    
    registry = get_registry()
    search = PersistentSemanticToolSearch(registry)
    
    assert search.available is True
    assert len(search.tool_embeddings) >= 594

def test_semantic_search_results():
    search = PersistentSemanticToolSearch(get_registry())
    
    results = search.search_tools("send email", top_k=5)
    
    assert len(results) <= 5
    assert any('email' in r['tool_name'] for r in results)
    assert all(r['similarity'] >= 0.3 for r in results)

def test_version_hash_check():
    search1 = PersistentSemanticToolSearch(get_registry())
    hash1 = search1.version_hash
    
    # No tools changed
    search2 = PersistentSemanticToolSearch(get_registry())
    hash2 = search2.version_hash
    
    assert hash1 == hash2  # Should match
```

---

## Deployment

### Production Configuration

**Render Deployment:**

```yaml
# render.yaml

services:
  - type: web
    name: ai-agents-platform
    env: python
    buildCommand: |
      pip install -r requirements.txt
      python -c "from tools.registry_v3 import get_registry; get_registry()"
      python -c "from tools.persistent_semantic_search import PersistentSemanticToolSearch; from tools.registry_v3 import get_registry; PersistentSemanticToolSearch(get_registry())"
    startCommand: gunicorn AI_infrastructure.flask_app:app
    envVars:
      - key: SEMANTIC_SEARCH_ENABLED
        value: true
      - key: REDIS_URL
        fromService:
          name: redis
          type: redis
          property: connectionString
```

**Pre-Deployment Checklist:**

```bash
# 1. Verify tool count
python -c "from tools.registry_v3 import get_registry; r = get_registry(); print(f'Tools: {len(r.tools)}')"

# 2. Test semantic search initialization
python -c "from tools.persistent_semantic_search import PersistentSemanticToolSearch; from tools.registry_v3 import get_registry; s = PersistentSemanticToolSearch(get_registry()); print(f'Embeddings: {len(s.tool_embeddings)}')"

# 3. Verify Supabase connection
python -c "from AI_infrastructure.shared.database_utils import execute_query; print(execute_query('SELECT version()', fetch_mode='value'))"

# 4. Test meta-tools
python -c "from tools.implementations.meta_tools import list_available_platforms; print(list_available_platforms())"
```

---

### Performance Optimization

**Redis Caching:**
- Enable Redis caching for 50x faster startup
- Set TTL to 1 hour (tools rarely change during production)

**Supabase Embeddings:**
- Use pgvector extension for fast similarity search
- Create IVFFlat index for <10ms searches
- Regenerate only when tools change (version hash)

**Module Plugin Loading:**
- Load once at server startup
- Cache in global registry singleton
- Avoid reloading on every request

**Thread-Local Storage:**
- Set user_id once per request
- Avoid repeated database lookups
- Reuse across all tool calls in request

---

## Known Issues

### Issue 1: Semantic Search Accuracy Varies

**Problem:** Semantic search sometimes suggests irrelevant tools (similarity threshold too low).

**Status:** ⚠️ KNOWN LIMITATION - Embeddings are probabilistic.

**Workaround:**
- Use `min_similarity=0.5` for higher precision
- Always verify with `get_tool_schema` before execution
- Combine with keyword search for better results

**Tuning:**
```python
# Current threshold: 0.3 (30% similarity)
# Recommended: 0.5 for high precision, 0.3 for high recall
search.search_tools(query, min_similarity=0.5)
```

---

### Issue 2: Platform Aliases Not Exhaustive

**Problem:** Some platform aliases missing (e.g., "shopify" doesn't expand to shopify_*).

**Status:** ⚠️ ENHANCEMENT NEEDED

**Workaround:** Use full platform name (`list_platform_tools("shopify")` instead of `"shop"`).

**Potential Fix:** Add more aliases to `platform_aliases` dict in meta_tools.py.

---

### Issue 3: Tool Intelligence Logging Performance

**Problem:** Logging every tool call adds ~5ms overhead.

**Status:** ⚠️ MINOR - Acceptable for learning value.

**Workaround:** Disable if performance critical:
```python
self.intelligence_logger = None  # Disable logging
```

---

### Issue 4: Redis Cache Invalidation

**Problem:** Cached tools don't update when new tools added until TTL expires (1 hour).

**Status:** ⚠️ BY DESIGN - Trade-off for performance.

**Workaround:**
```python
# Force cache invalidation
redis_manager.delete('tool_registry:v3:tools')

# Restart server to reload tools
```

---

## Related Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Overall system architecture
- **[AI_AGENTS.md](AI_AGENTS.md)** - Multi-agent system using tool discovery
- **[MODULES.md](MODULES.md)** - Module plugin system architecture
- **[SUPABASE_DATABASE.md](SUPABASE_DATABASE.md)** - Database schema for embeddings

---

## Changelog

**Jan 18, 2026** - Consolidated 20+ tool discovery files into TOOL_DISCOVERY.md
**Jan 13, 2026** - Added thread-local user_id storage for worker threads
**Jan 2, 2026** - Implemented persistent semantic search with Supabase
**Dec 17, 2025** - Added Redis caching for 50x faster startup
**Nov 2025** - Fixed UTF-8 encoding for module plugin JSON files
**Earlier** - Progressive discovery architecture implemented

---

## Files Consolidated

This document consolidates the following 20+ files:

### Root Tool Discovery Files (6 files):
- AI_TOOL_DISCOVERY_PATH_MAP.md
- PROGRESSIVE_TOOL_DISCOVERY_ARCHITECTURE.md
- TOOL_DISCOVERY_SYSTEMS_SUMMARY.md
- TOOL_DISCOVERY_IMPLEMENTATION_TASKS.md
- TOOL_DISCOVERY_IMPLEMENTATION_CHECKLIST.md
- TOOL_DISCOVERY_EXECUTIVE_SUMMARY.md

### Registry Files (8 files):
- THREAD_CARD_REGISTRY_IMPLEMENTATION_COMPLETE.md
- THREAD_CARD_MODULE_REGISTRY_ARCHITECTURE.md
- docs/archive/CRITICAL_REGISTRY_ISSUES.md
- docs/archive/REGISTRY_AUDIT_REPORT.md
- docs/archive/REGISTRY_FIXES_COMPLETE.md
- docs/archive/REGISTRY_DIAGNOSTIC_COMPLETE.md
- docs/archive/MICROSOFT_TOOLS_REGISTRY_FIX_COMPLETE.md
- docs/archive/ai_infrastructure/TOOL_REGISTRY_INTEGRATION_COMPLETE.md

### Archive Files (6+ files):
- archive/documentation/XERO_SMART_TOOLS_AND_DISCOVERY_COMPLETE.md
- archive/documentation/TOOL_DISCOVERY_FLOW_DIAGRAM.md

**Total:** 20+ files consolidated → 1 comprehensive document
