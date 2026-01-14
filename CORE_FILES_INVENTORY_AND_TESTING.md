# Core Files Inventory & Testing Plan
**Date**: November 20, 2025  
**Total Files**: 20  
**Status**: Analysis Complete

---

## 📊 Usage Analysis Summary

**HIGH USAGE** (10+ imports): 4 files  
**MEDIUM USAGE** (2-9 imports): 4 files  
**LOW USAGE** (1 import): 4 files  
**NO IMPORTS FOUND**: 8 files (needs verification)

---

## 🔥 HIGH PRIORITY - Actively Used (8 files)

### 1. unified_session_manager.py ⭐⭐⭐⭐⭐
**Status**: ✅ CRITICAL - Core Infrastructure  
**Imports**: 11 locations (flask_app.py, verify_setup.py, core/__init__.py)  
**Purpose**: Single source of truth for ALL session data  
**Features**:
- SQLite/Supabase dual-mode persistence
- In-memory cache for active sessions
- SSE queue management
- Thread-safe execution locks

**Testing Required**:
- [x] Session creation
- [x] Session loading
- [ ] Multi-turn conversation persistence
- [ ] SSE queue management
- [ ] Lock contention handling

**Used By**:
- flask_app.py (global session_manager)
- verify_setup.py (verification script)
- core/__init__.py (module export)

---

### 2. combined_agent_worker.py ⭐⭐⭐⭐⭐
**Status**: ✅ CRITICAL - Production Streaming  
**Imports**: 10 locations (agent_routes_v4.py primary)  
**Purpose**: Streaming agent worker with Claude API  
**Features**:
- SSE event streaming
- Tool execution
- Multi-turn conversations
- Thinking block handling

**Testing Required**:
- [x] Basic streaming
- [x] Tool execution
- [ ] Multi-turn with history
- [ ] Error handling
- [ ] Token limit handling
- [ ] Thinking blocks preservation

**Used By**:
- agent_routes_v4.py (5 imports: run_agent_worker, execute_streaming_request, agent_worker, prune_conversation_for_context_limit)

---

### 3. agent_state_manager.py ⭐⭐⭐⭐
**Status**: ✅ ACTIVE - State Management  
**Imports**: 18 locations (agent_routes_v4.py, thread_routes.py)  
**Purpose**: Centralized agent execution state  
**Features**:
- Isolated queues for SSE streaming
- Execution locks for thread safety
- Conversation history per agent
- Triple Agent state coordination

**Testing Required**:
- [ ] State creation per agent
- [ ] Queue isolation
- [ ] Lock thread safety
- [ ] State cleanup
- [ ] Triple Agent coordination

**Used By**:
- agent_routes_v4.py (state retrieval)
- thread_routes.py (thread listing, cleanup)

**⚠️ OVERLAP**: Functions may overlap with unified_session_manager.py (needs review)

---

### 4. unified_ai_client.py ⭐⭐⭐⭐
**Status**: ✅ ACTIVE - AI Provider Abstraction  
**Imports**: 20+ locations (agent_routes_v4.py, flask_app.py)  
**Purpose**: Universal AI client (Claude, OpenAI, DeepSeek)  
**Features**:
- Multi-provider support
- Automatic failover
- API key rotation
- Rate limit handling

**Testing Required**:
- [ ] Claude API calls
- [ ] OpenAI fallback
- [ ] DeepSeek fallback
- [ ] Key rotation
- [ ] Rate limit handling
- [ ] Error recovery

**Used By**:
- agent_routes_v4.py (initialize_ai_client - 6 locations)
- flask_app.py (global ai_client)

---

### 5. prompt_injection_manager.py ⭐⭐⭐
**Status**: ✅ ACTIVE - Security  
**Imports**: agent_routes_v4.py (line 1076)  
**Purpose**: Detect and prevent prompt injection attacks  
**Features**:
- Prompt injection detection
- Jailbreak attempt blocking
- Security logging

**Testing Required**:
- [ ] Basic injection detection
- [ ] Jailbreak attempts
- [ ] False positive rate
- [ ] Performance impact

**Used By**:
- agent_routes_v4.py (get_prompt_manager)

---

### 6. ip_location.py ⭐⭐
**Status**: ✅ ACTIVE - Context Enhancement  
**Imports**: agent_routes_v4.py (line 867)  
**Purpose**: Geographic context for AI  
**Features**:
- IP to location mapping
- Timezone detection
- Location-aware responses

**Testing Required**:
- [ ] Location detection
- [ ] Timezone accuracy
- [ ] Privacy compliance

**Used By**:
- agent_routes_v4.py (get_location_dict)

---

### 7. tool_executor.py ⭐⭐
**Status**: ✅ ACTIVE - V4 Modular (kept for future)  
**Imports**: conversation_manager.py (archived), tool_processor.py  
**Purpose**: Tool execution with credential injection  
**Features**:
- Validates tool calls
- Injects user credentials
- Comprehensive logging

**Testing Required**:
- [ ] Tool validation
- [ ] Credential injection
- [ ] Error handling
- [ ] Streaming results

**Used By**:
- tool_processor.py (V4 architecture)
- conversation_manager.py (archived)

**Note**: Clean patterns, may be integrated into combined_agent_worker.py

---

### 8. tool_processor.py ⭐⭐
**Status**: ✅ ACTIVE - V4 Modular (kept for future)  
**Imports**: conversation_manager.py (archived)  
**Purpose**: Processes tool_use blocks from Claude  
**Features**:
- Parses tool_use blocks
- Builds tool_result blocks
- Handles multiple tool calls

**Testing Required**:
- [ ] Tool call extraction
- [ ] Batch execution
- [ ] Result formatting

**Used By**:
- conversation_manager.py (archived)

**Note**: May be merged into combined_agent_worker.py

---

## ⚠️ MEDIUM PRIORITY - Specialized Features (4 files)

### 9. confirmation_manager.py ⚠️
**Status**: 🔍 NO IMPORTS FOUND (needs verification)  
**Purpose**: Universal confirmation system for expensive operations  
**Features**:
- Declarative confirmation requirements
- Token/cost estimation
- Risk level assessment
- Multi-turn confirmation flow

**Testing Required**:
- [ ] Confirmation request creation
- [ ] User approval flow
- [ ] Cost estimation
- [ ] Risk assessment

**Potential Users**: Email tools, file operations, bulk operations

---

### 10. context_aware_ai.py ⚠️
**Status**: 🔍 NO IMPORTS FOUND (needs verification)  
**Purpose**: Integrates all context systems for AI  
**Features**:
- User profiles (who)
- Temporal context (when)
- Geographic context (where)
- Memory & history
- Event triggers

**Testing Required**:
- [ ] Context collection
- [ ] System prompt enhancement
- [ ] Performance impact

**Potential Enhancement**: Could enhance agent_routes_v4.py prompts

---

### 11. context_engine.py ⚠️
**Status**: 🔍 NO IMPORTS FOUND (needs verification)  
**Purpose**: Context aggregation and management  
**Features**:
- User profile loading
- Temporal context
- Geographic context
- Memory retrieval

**Testing Required**:
- [ ] Context retrieval
- [ ] Cache performance
- [ ] Data freshness

---

### 12. event_triggers.py ⚠️
**Status**: 🔍 NO IMPORTS FOUND (needs verification)  
**Purpose**: Proactive AI activation based on events  
**Features**:
- Time-based triggers
- Event detection
- Proactive suggestions

**Testing Required**:
- [ ] Trigger detection
- [ ] Event processing
- [ ] Performance impact

---

## 📋 SPECIALIZED - Domain-Specific (4 files)

### 13. sync_manager.py 📊
**Status**: ✅ ACTIVE - Kanban Sync  
**Imports**: 2 locations (session_database import)  
**Purpose**: Bidirectional sync between Kanban ↔ Google Tasks ↔ Calendar  
**Features**:
- sessions.db as source of truth
- Google Tasks mobile access
- Calendar event generation
- Conflict resolution

**Testing Required**:
- [ ] Kanban → Google Tasks sync
- [ ] Google Tasks → Kanban sync
- [ ] Calendar event creation
- [ ] Conflict resolution

**Used By**: Kanban board feature

---

### 14. task_card_manager.py 📊
**Status**: ✅ ACTIVE - Task Cards  
**Imports**: 2 locations (session_database import)  
**Purpose**: Task card management for Kanban  
**Features**:
- Create task cards
- Update task status
- Link to sessions

**Testing Required**:
- [ ] Card creation
- [ ] Status updates
- [ ] Session linking

**Used By**: Kanban board feature

---

### 15. email_parser.py 📧
**Status**: 🔍 NO IMPORTS FOUND  
**Purpose**: Email parsing and structure extraction  
**Features**:
- Email header parsing
- Body extraction
- Attachment handling

**Testing Required**:
- [ ] Header parsing
- [ ] Body extraction
- [ ] Attachment detection

**Potential Users**: Gmail tools, email processing

---

### 16. email_to_pdf_converter.py 📧
**Status**: 🔍 NO IMPORTS FOUND  
**Purpose**: Convert emails to PDF format  
**Features**:
- HTML to PDF conversion
- Attachment embedding
- Formatting preservation

**Testing Required**:
- [ ] HTML conversion
- [ ] Attachment handling
- [ ] Output quality

**Potential Users**: Email archiving, document generation

---

## 🔧 UTILITY - Support Functions (4 files)

### 17. unified_anthropic_client.py 🤖
**Status**: ✅ ACTIVE - Claude API  
**Imports**: Multiple (tests, verify_setup.py, core/__init__.py)  
**Purpose**: Anthropic Claude API client  
**Features**:
- Claude API integration
- Extended thinking support
- Tool use handling

**Testing Required**:
- [ ] Basic API calls
- [ ] Streaming responses
- [ ] Tool use
- [ ] Extended thinking

**Used By**:
- Test files
- verify_setup.py
- core/__init__.py

---

### 18. tool_result_limits.py 🔧
**Status**: 🔍 NO IMPORTS FOUND  
**Purpose**: Limit tool result sizes for context window  
**Features**:
- Result truncation
- Smart summarization
- Token counting

**Testing Required**:
- [ ] Truncation logic
- [ ] Summarization quality
- [ ] Token accuracy

**Potential Users**: Tool execution, API calls

---

### 19. module_blueprint_loader.py 🔧
**Status**: 🔍 NO IMPORTS FOUND  
**Purpose**: Dynamic Flask blueprint loading  
**Features**:
- Auto-discover blueprints
- Dynamic route registration
- Module hot-reload

**Testing Required**:
- [ ] Blueprint discovery
- [ ] Route registration
- [ ] Hot reload

**Used By**: Flask app initialization

---

### 20. session_orchestrator.py 📊
**Status**: ✅ ACTIVE - Google Tasks Integration  
**Purpose**: Google Tasks synchronization (niche but active)  
**Features**:
- Create/update Google Tasks from sessions
- Load sessions from Google Tasks
- Kanban column mapping

**Testing Required**:
- [ ] Google Tasks API
- [ ] Session sync
- [ ] Kanban mapping

**Used By**: Kanban + Google Tasks feature

---

## 🎯 Testing Priority Matrix

### P0 - CRITICAL (Must Test Immediately)
1. **unified_session_manager.py** - Session persistence broken
2. **combined_agent_worker.py** - Multi-turn conversations broken
3. **agent_state_manager.py** - State management conflicts

### P1 - HIGH (Test This Week)
4. **unified_ai_client.py** - AI provider switching
5. **prompt_injection_manager.py** - Security
6. **unified_anthropic_client.py** - Claude API

### P2 - MEDIUM (Test This Month)
7. **confirmation_manager.py** - Verify if used
8. **context_aware_ai.py** - Verify if used
9. **sync_manager.py** - Kanban sync
10. **task_card_manager.py** - Task cards

### P3 - LOW (Test When Needed)
11-20. Specialized/utility files

---

## 📝 Test Script Template

```python
# test_core_file.py
"""
Test [FILE_NAME]
Purpose: [DESCRIPTION]
Priority: [P0/P1/P2/P3]
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

def test_basic_functionality():
    """Test basic operations"""
    # Import module
    from core.[module_name] import [class_or_function]
    
    # Test creation
    instance = [class_name]()
    assert instance is not None
    
    # Test core function
    result = instance.[method]()
    assert result is not None
    print(f"✅ Basic test passed: {result}")

def test_edge_cases():
    """Test edge cases and errors"""
    # Test error handling
    # Test boundary conditions
    # Test concurrent access
    pass

if __name__ == '__main__':
    print("🧪 Testing [FILE_NAME]...")
    test_basic_functionality()
    test_edge_cases()
    print("✅ All tests passed!")
```

---

## 🔍 Files Needing Verification

These files had **NO IMPORTS FOUND** but may still be used:

1. **confirmation_manager.py** - Check tool implementations
2. **context_aware_ai.py** - Check system prompt builders
3. **context_engine.py** - Check context_aware_ai.py
4. **event_triggers.py** - Check context_aware_ai.py
5. **email_parser.py** - Check Gmail tools
6. **email_to_pdf_converter.py** - Check email tools
7. **tool_result_limits.py** - Check tool executors
8. **module_blueprint_loader.py** - Check flask_app.py

**Action**: Grep search each file's functions to find indirect usage

---

## ⚠️ Overlap Analysis

### agent_state_manager.py vs unified_session_manager.py

Both manage state but may have different scopes:

**agent_state_manager.py**:
- Agent-specific state (Triple Agent coordination)
- SSE queues per agent
- Execution locks per agent
- Used by agent_routes_v4.py

**unified_session_manager.py**:
- Global session storage
- Database persistence
- SSE queues per session
- Used by flask_app.py

**Action Required**: Analyze if they can be merged or if separation is intentional

---

## 📊 Quick Stats

**Total Lines**: ~8,000+ lines across 20 files  
**Critical Files**: 3 (unified_session_manager, combined_agent_worker, agent_state_manager)  
**Active Files**: 11 (55%)  
**Unverified Files**: 8 (40%)  
**Test Coverage**: ~10% (needs improvement)

---

## 🚀 Next Steps

1. **Immediate**: Test P0 critical files (unified_session_manager, combined_agent_worker)
2. **This Week**: Verify "no imports found" files
3. **This Month**: Create test suite for all active files
4. **Ongoing**: Monitor imports with automated tools

---

**Created**: November 20, 2025  
**Last Updated**: November 20, 2025  
**Status**: Initial Analysis Complete
