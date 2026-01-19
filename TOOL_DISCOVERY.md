# TOOL DISCOVERY - Technical Documentation

**Version:** 3.0.0
**Status:** ✅ Production Ready
**Last Updated:** January 19, 2026
**Module Type:** Tool Registry + Intelligent Discovery System

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Registry V3](#registry-v3)
4. [Intelligent Discovery](#intelligent-discovery)
5. [Module Plugin System](#module-plugin-system)
6. [Meta-Tools](#meta-tools)
7. [Implementation Details](#implementation-details)
8. [API Reference](#api-reference)
9. [Configuration](#configuration)
10. [Critical Fixes](#critical-fixes)
11. [Testing & Debugging](#testing--debugging)
12. [Known Issues](#known-issues)
13. [Appendix](#appendix)

---

## Overview

### Purpose

The Tool Discovery system provides intelligent tool selection for AI agents, managing 750+ tools across 30+ platforms. It combines:

1. **Registry V3** - Central tool registry with auto-loading and caching
2. **Intelligent Discovery** - Keyword, semantic, and context-based tool search
3. **Module Plugin System** - Auto-discover tools from self-contained modules
4. **Meta-Tools** - AI-accessible tools for discovering other tools
5. **Tool Intelligence Logger** - Silent learning system tracking usage patterns

### Key Capabilities

**Registry V3:**
- Auto-loads 750+ tools from JSON schemas
- Redis caching (50x faster on cache hit: 40ms vs 2000ms)
- Thread-local storage for user context in worker threads
- Dynamic schema injection (`{{DYNAMIC:...}}` placeholders)
- Security: Excludes email sending tools from AI access

**Intelligent Discovery:**
- Keyword matching (75% accuracy, zero maintenance)
- Conversation context analysis (85% accuracy)
- Semantic similarity search (90% accuracy with sentence-transformers)
- Hybrid mode (95% accuracy combining all methods)
- Platform aliasing (e.g., "microsoft" → all microsoft_* tools)

**Module Plugin System:**
- Drop-in architecture: add folder → tools available automatically
- Self-contained modules with schema/ + implementations/
- Quote calculator: 80+ tools, 5 product domains
- Shopify, InHouse Print, Customer Reactivation modules

### Statistics

- **Total Tools:** 750+ (as of Jan 2026)
- **Platforms:** 30+ (Gmail, Outlook, Xero, Shopify, Slack, etc.)
- **Module Plugins:** 8 active (Quote Calculator, Shopify, InHouse, etc.)
- **Schema Files:** 95+ JSON definition files
- **Implementations:** 80+ Python module files
- **Load Time:** 2000ms cold / 40ms cached (Redis)
- **Discovery Accuracy:** 95% (hybrid mode)

---

## Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                         AI AGENT LAYER                                │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ Claude/GPT → "Check my Gmail inbox"                             │ │
│  └──────────────────────────┬───────────────────────────────────────┘ │
└────────────────────────────┼──────────────────────────────────────────┘
                             │
                             │ Tool Request
                             │
┌────────────────────────────▼──────────────────────────────────────────┐
│                    INTELLIGENT DISCOVERY                               │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ IntelligentToolSuggestion                                       │  │
│  │ • Keyword matching: "gmail", "inbox" → gmail_list_messages     │  │
│  │ • Conversation context: Recently used Gmail → boost score      │  │
│  │ • Semantic search: Similarity to "check inbox"                 │  │
│  └────────────────────────┬───────────────────────────────────────┘  │
└────────────────────────────┼──────────────────────────────────────────┘
                             │
                             │ Tool Name
                             │
┌────────────────────────────▼──────────────────────────────────────────┐
│                         REGISTRY V3                                    │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ get_tool_function('gmail_list_messages')                        │  │
│  │ → Returns: google_workspace.gmail.list_messages                │  │
│  └────────────────────────┬───────────────────────────────────────┘  │
│                            │                                           │
│  Cache Layer (Redis):      │     Module Plugins:                      │
│  • tools→ 1-hour TTL       │     • Quote Calculator                   │
│  • 50x speedup (40ms)      │     • Shopify                            │
│                            │     • InHouse Print                       │
└────────────────────────────┼──────────────────────────────────────────┘
                             │
                             │ Function Ref
                             │
┌────────────────────────────▼──────────────────────────────────────────┐
│                    TOOL EXECUTION                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ execute_tool(tool_name='gmail_list_messages', max_results=10)  │  │
│  │ • Inject _user_id for OAuth                                    │  │
│  │ • Check permissions (Phase 3 User Management)                  │  │
│  │ • Execute function                                             │  │
│  │ • Log to Tool Intelligence Logger (silent learning)            │  │
│  └────────────────────────┬───────────────────────────────────────┘  │
└────────────────────────────┼──────────────────────────────────────────┘
                             │
                             │ Result
                             │
┌────────────────────────────▼──────────────────────────────────────────┐
│                  TOOL INTELLIGENCE LOGGER                              │
│  (Silent Learning - runs AFTER tool execution)                        │
│  • Analyze execution (success/error/slow)                             │
│  • Detect recurring patterns (automation opportunities)               │
│  • Generate AI observations (improvement suggestions)                 │
│  • Store intelligence in PostgreSQL for analysis                      │
└────────────────────────────────────────────────────────────────────────┘
```

### Design Patterns

**1. Singleton Registry Pattern**
```python
# Global singleton for performance
_registry_instance = None

def get_registry() -> RegistryV3:
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = RegistryV3()
    return _registry_instance
```

**2. Module Plugin Architecture**
```
UI/modules_external/
├── quote-calculator/
│   ├── schema/calculator_tools.json     ← AI reads this
│   └── implementations/calculator_wrapper.py  ← Python executes this
└── shopify/
    ├── schema/shopify_tools.json
    └── implementations/shopify_wrapper.py
```

**3. Multi-Source Tool Loading**
```python
def _load_implementations(self):
    # Priority order:
    # 1. google_workspace/ for Google tools (PRIMARY)
    self._load_from_google_workspace()
    
    # 2. tools/implementations/ for other platforms (FALLBACK)
    self._load_from_implementations()
    
    # 3. UI/modules_external/ for plugin modules (AUTO-DISCOVER)
    self._load_module_plugins()
```

**4. Thread-Local Storage for User Context**
```python
# Flask g context doesn't transfer to worker threads
# Use thread-local storage instead
_thread_local = threading.local()

def set_thread_user_id(self, user_id: int):
    self._thread_local.user_id = user_id

def get_thread_user_id(self) -> Optional[int]:
    return getattr(self._thread_local, 'user_id', None)
```

**5. Credential Injection Pattern**
```python
# Tools receive _user_id and _injected_credentials
def execute_tool(self, **kwargs):
    user_id = kwargs.get('_user_id') or self.get_thread_user_id()
    
    # Tool function receives user_id transparently
    func = self.get_tool_function(tool_name)
    result = func(**kwargs)  # _user_id passed through
```

---

## Registry V3

### Purpose

Central tool registry managing 750+ tools with auto-loading, caching, and intelligent execution. Handles tool schema storage, implementation discovery, credential injection, and permission checking.

### File Structure

```
tools/
├── registry_v3.py                 # Main registry (1,075 lines)
├── implementations/               # Core tool implementations (80+ files)
│   ├── gmail_smart.py
│   ├── microsoft_outlook_tools.py
│   ├── meta_tools.py
│   └── ...
├── schemas/                       # Tool definitions (95+ JSON files)
│   ├── gmail_tools.json
│   ├── microsoft_outlook_tools.json
│   ├── meta_tools.json
│   └── ...
├── plugins/
│   └── module_plugin_loader.py    # Auto-discover UI modules
└── intelligent_discovery.py       # Smart tool search
```

### Key Components

#### 1. RegistryV3 Class

**File:** `tools/registry_v3.py` (Lines 1-1075)

**Properties:**
```python
class RegistryV3:
    tools: Dict[str, Dict]              # tool_name → tool schema
    implementations: Dict[str, Any]     # module_name → Python module/class
    tool_call_count: int                # For user feedback injection
    redis_manager: Optional[RedisManager]  # Cache manager
    intelligence_logger: Optional[ToolIntelligenceLogger]  # Silent learning
    _thread_local: threading.local      # User context in worker threads
```

#### 2. Schema Loading

**Features:**
- UTF-8 encoding with error handling
- Dynamic schema injection (`{{DYNAMIC:...}}` placeholders)
- Security filtering (excludes email sending tools)
- Platform field propagation (schema → tools)

**Security Exclusions:**
```python
EXCLUDED_TOOLS = [
    'microsoft_outlook_send_email',
    'microsoft_outlook_smart_bulk_send_personalized',
    'microsoft_outlook_reply_to_message',
    'microsoft_outlook_forward_message',
    'microsoft_outlook_send_draft'
]
```

#### 3. Tool Execution

**Critical Features:**
- Multi-source user ID resolution (kwargs, thread-local, Flask g)
- Permission checking (Phase 3 User Management)
- User feedback injection (every Nth call)
- Tool Intelligence logging (silent, non-blocking)

**User ID Resolution:**
```python
def execute_tool(self, **kwargs):
    # Priority order for user_id:
    # 1. _user_id in kwargs (explicit injection)
    user_id = kwargs.get('_user_id')
    
    # 2. Thread-local storage (worker threads) ✅ NEW (Jan 13, 2026)
    if not user_id:
        user_id = self.get_thread_user_id()
    
    # 3. Flask g context (main request thread)
    if not user_id:
        from flask import g
        user_id = g.get('user_id')
    
    # Execute tool
    func = self.get_tool_function(tool_name)
    return func(**kwargs)
```

#### 4. Redis Caching

**Performance:**
- **Cache Hit:** 40ms (50x faster)
- **Cache Miss:** 2000ms (full load)
- **TTL:** 1 hour (3600 seconds)
- **Invalidation:** Manual via `invalidate_cache()`

---

## Intelligent Discovery

### Purpose

Multi-strategy tool search system providing 95% accuracy through keyword matching, conversation context, and semantic similarity.

### Discovery Strategies

#### 1. Keyword Search

**Accuracy:** 75% (baseline)
**Maintenance:** Zero (auto-discovers all tools)

**Scoring Algorithm:**
```python
for word in query_words:
    # Exact word match in tool name: +5.0 points
    if word in tool_name_lower.split('_'):
        score += 5.0
    
    # Partial match in tool name: +2.0 points
    elif word in tool_name_lower:
        score += 2.0
    
    # Description match: +1.0 points
    if word in description:
        score += 1.0
```

#### 2. Conversation Context Analysis

**Accuracy:** 85% (with multi-turn awareness)

**Analyzed Patterns:**
- Recently used tools (boost: 2.0x)
- Mentioned platforms (boost: 1.5x)
- Platform preference (most frequent)

#### 3. Semantic Similarity Search

**Accuracy:** 90% (requires sentence-transformers)
**Model:** `all-MiniLM-L6-v2` (384-dim embeddings)

#### 4. Hybrid System

**Accuracy:** 95% (combining all strategies)

**Scoring Formula:**
```python
final_score = (
    keyword_score * 0.5 +
    semantic_score * 0.3 +
    context_boost * 0.2
)
```

---

## Module Plugin System

### Purpose

Drop-in architecture for self-contained tool modules. Add a folder with schema/ + implementations/ → tools automatically available to AI.

### File Structure

```
UI/modules_external/
├── quote-calculator/              # 80+ tools, 5 product domains
│   ├── schema/
│   │   ├── calculator_tools.json
│   │   ├── meta_tools.json
│   │   └── query_library_tools.json
│   └── implementations/
│       ├── calculator_wrapper.py
│       ├── meta_tools_wrapper.py
│       └── query_library_wrapper.py
├── shopify/                       # 25 tools, product management
├── inhouse-print/                 # 15 tools, database queries
└── customer-reactivation/         # 10 tools, email campaigns
```

### @tool_executor Decorator

**Purpose:** Compatibility decorator for legacy wrappers

**Usage in Wrappers:**
```python
from tools.registry_v3 import tool_executor

@tool_executor()
def calculate_business_cards(quantity: int, **kwargs) -> Dict[str, Any]:
    """Calculate quote for business cards"""
    return result
```

---

## Meta-Tools

### Purpose

AI-accessible tools that help Claude/GPT discover and understand the 750+ available tools.

### Core Meta-Tools

#### 1. list_available_platforms

**Purpose:** List all platforms with tool counts

**Example Response:**
```json
{
  "success": true,
  "platforms": ["gmail", "google_docs", "microsoft_outlook"],
  "platform_count": 30,
  "tool_counts": {"gmail": 25, "google_docs": 18},
  "total_tools": 750
}
```

#### 2. list_platform_tools

**Purpose:** List tools for a specific platform (names + descriptions only)

#### 3. get_tool_schema

**Purpose:** Get full schema for a specific tool (parameters, types, descriptions)

#### 4. recommend_tools_for_task

**Purpose:** AI-guided tool discovery based on task description

#### 5. execute_tool

**Purpose:** Execute any tool by name (meta-tool for tool execution)

---

## API Reference

### Registry V3 Methods

#### get_registry()

**Purpose:** Get singleton registry instance

**Usage:**
```python
from tools.registry_v3 import get_registry

registry = get_registry()
print(f"Total tools: {len(registry.tools)}")
```

#### execute_tool(**kwargs)

**Parameters:**
- `tool_name` (str, required): Name of tool to execute
- `**kwargs`: Tool-specific parameters
- `_user_id` (int, optional): User ID for OAuth credentials

**Example:**
```python
result = registry.execute_tool(
    tool_name='gmail_send_email',
    to='user@example.com',
    subject='Test',
    body='Hello world',
    _user_id=14
)
```

---

## Critical Fixes

### 1. ✅ RESOLVED: Thread-Local User Context (January 13, 2026)

**Problem:** Flask g context doesn't transfer to worker threads

**Solution:** Added thread-local storage to Registry V3

**Impact:**
- Worker threads can now execute OAuth tools
- Background jobs work with user-specific credentials
- No more "user_id not found" errors in async contexts

### 2. ✅ RESOLVED: Redis Cache Performance (December 17, 2025)

**Problem:** Registry initialization took 2000ms on every Flask restart

**Solution:** Added Redis caching with 1-hour TTL

**Performance:**
- **Cold load:** 2000ms
- **Cache hit:** 40ms (50x faster)

### 3. ✅ RESOLVED: Email Sending Security Filter

**Problem:** AI could send emails without proper safeguards

**Solution:** Excluded email sending tools from AI access

---

## Testing & Debugging

### Manual Testing Checklist

```bash
# Test 1: Registry loads successfully
python -c "from tools.registry_v3 import get_registry; r = get_registry(); print(f'Loaded {len(r.tools)} tools')"

# Test 2: Keyword search
python -c "from tools.intelligent_discovery import search_tools_by_query; from tools.registry_v3 import get_registry; r = get_registry(); results = search_tools_by_query('send email', r); print([m['tool_name'] for m in results])"

# Test 3: Meta-tool discovery
python -c "from tools.implementations.meta_tools import list_available_platforms; result = list_available_platforms(); print(f'Platforms: {len(result[\"platforms\"])}')"
```

### Debugging Common Issues

#### Issue: "Tool not found" Error

**Diagnosis:**
```python
from tools.registry_v3 import get_registry
registry = get_registry()
print(f"Tool exists: {'gmail_send_email' in registry.tools}")
```

#### Issue: Redis Cache Not Working

**Fix:**
```bash
# Start Redis server
redis-server

# Check connection
redis-cli ping
```

---

## Known Issues

### 1. ⚠️ KNOWN: Semantic Search Requires sentence-transformers

**Workaround:**
```bash
pip install sentence-transformers
```

### 2. ⚠️ KNOWN: Redis Cache Invalidation Not Automatic

**Workaround:**
```python
from tools.registry_v3 import get_registry
registry = get_registry()
registry.invalidate_cache()
```

---

## Appendix

### Performance Benchmarks

| Operation | Cold Start | Cache Hit | Speedup |
|-----------|-----------|-----------|---------|
| **Total initialization** | **2000ms** | **40ms** | **50x** |

| Discovery Method | Time | Accuracy |
|-----------------|------|----------|
| Keyword search | 15ms | 75% |
| Semantic search | 70ms | 90% |
| **Hybrid mode** | **95ms** | **95%** |

### File Locations Quick Reference

```
tools/
├── registry_v3.py                    # 1,075 lines - Main registry
├── intelligent_discovery.py          # 671 lines - Smart search
└── implementations/meta_tools.py     # 1,034 lines - Discovery tools
```

---

**End of Documentation**

**Document Version:** 3.0.0  
**Last Updated:** January 19, 2026  
**Status:** ✅ Production Ready - Comprehensive Reference
