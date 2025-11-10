# 🎨 Visual Architecture Comparison: In_House_SQL vs AI_agents

**Created:** October 30, 2025  
**Companion to:** MIGRATION_GUIDE_INHOUSEPRINT_TO_AI_AGENTS.md

---

## 📊 System Architecture Diagrams

### Current AI_agents Architecture (Synchronous)

```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER CLIENT                          │
│                    (business-ai-platform-v2.html)               │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ HTTP POST /api/agent/chat
                 │ { message: "...", session_id: "..." }
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK APPLICATION                          │
│                     (Single Thread Blocking)                    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  AGENT_ROUTES.PY (handle_main_chat)                      │  │
│  │                                                           │  │
│  │  1. Load ToolRegistry (281 tools)                        │  │
│  │  2. Inject user credentials                              │  │
│  │  3. Build messages array                                 │  │
│  │  4. Call Anthropic API ──────────────────────────┐       │  │
│  │                                                   │       │  │
│  │  5. Parse response blocks ◄──────────────────────┘       │  │
│  │     │                                                     │  │
│  │     ├─ thinking block → yield SSE                        │  │
│  │     ├─ tool_use block → execute_tool() ──┐              │  │
│  │     │                                      │              │  │
│  │     │  ┌────────────────────────────────┐ │              │  │
│  │     │  │ ToolRegistry.execute_tool()    │ │              │  │
│  │     │  │ - Lookup tool implementation   │◄┘              │  │
│  │     │  │ - Inject credentials (user_id) │                │  │
│  │     │  │ - Execute synchronously        │                │  │
│  │     │  │ - Return result                │                │  │
│  │     │  └────────────────────────────────┘                │  │
│  │     │                                                     │  │
│  │     ├─ Add tool_result to messages                       │  │
│  │     ├─ Loop to step 4 (next API call)                    │  │
│  │     └─ text block → yield SSE                            │  │
│  │                                                           │  │
│  │  6. Generator yields SSE events                          │  │
│  │     ├─ data: {"type":"thinking_block","content":"..."}   │  │
│  │     ├─ data: {"type":"tool_use","tool_name":"..."}       │  │
│  │     └─ data: {"type":"text_block","content":"..."}       │  │
│  │                                                           │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ SSE Stream (Generator)
                 │ Direct events, no buffering
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BROWSER EVENT STREAM                         │
│                                                                 │
│  const reader = response.body.getReader();                     │
│  while (true) {                                                 │
│    const {done, value} = await reader.read();                  │
│    // Process JSON events immediately                          │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘

⚠️ LIMITATIONS:
├─ Flask thread BLOCKED until complete (10-120 seconds)
├─ No session persistence (lost on server restart)
├─ No multi-tab support (shared state)
├─ Generator locks up Flask worker
└─ Manual multi-turn loop management
```

---

### Target In_House_SQL Architecture (Asynchronous + Persistent)

```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER CLIENT                          │
│                    (single_agent_viewer.html)                   │
└────────────┬────────────────────────────────┬───────────────────┘
             │                                │
             │ 1. Start Agent                 │ 2. Stream Events
             │ POST /api/agent/1/start        │ GET /stream/1?session_id=...
             │                                │
             ▼                                ▼
┌────────────────────────────────────────────────────────────────┐
│                      FLASK APPLICATION                         │
│                   (Non-Blocking Architecture)                  │
│                                                                │
│  ┌──────────────────────────────────┐  ┌───────────────────┐ │
│  │  AGENT_ROUTES.PY                 │  │  SSE ENDPOINT     │ │
│  │  (start_agent)                   │  │  (stream_agent)   │ │
│  │                                  │  │                   │ │
│  │  1. Parse request (JSON/Form)    │  │  1. Get queue     │ │
│  │  2. Load session from SQLite ──┐ │  │  2. Read events   │ │
│  │     (conversation history)      │ │  │  3. Yield SSE     │ │
│  │  3. Get lock + queue            │ │  │  4. Exit on       │ │
│  │  4. Spawn background thread ──┐ │ │  │     complete      │ │
│  │  5. Return 200 immediately    │ │ │  │                   │ │
│  │     (non-blocking!)            │ │ │  │  ┌────────────┐  │ │
│  │                                │ │ │  │  │ Queue.get  │  │ │
│  └────────────────────────────────┘ │ │  │  │ (blocking, │  │ │
│                                     │ │ │  │  timeout=30)│  │ │
│                                     │ │ │  └─────┬──────┘  │ │
│                                     │ │ └────────┼─────────┘ │
│                                     │ │          │           │
│                                     ▼ │          │           │
│  ┌──────────────────────────────────────────────┼─────────┐ │
│  │  BACKGROUND THREAD (agent_worker.py)         │         │ │
│  │                                               │         │ │
│  │  ┌────────────────────────────────────────────────┐   │ │
│  │  │ 1. Build content blocks from files          │   │   │ │
│  │  │    - Base64 encode PDFs/images              │   │   │ │
│  │  │    - Determine document vs image type       │   │   │ │
│  │  │                                              │   │   │ │
│  │  │ 2. Initialize multi-turn loop (max 10)      │   │   │ │
│  │  │    messages = conversation_history + user   │   │   │ │
│  │  │                                              │   │   │ │
│  │  │ 3. FOR turn in range(10):                   │   │   │ │
│  │  │    │                                         │   │   │ │
│  │  │    ├─ Call Anthropic API ────────────────┐  │   │   │ │
│  │  │    │  - Extended thinking (10k tokens)   │  │   │   │ │
│  │  │    │  - Interleaved thinking beta header │  │   │   │ │
│  │  │    │  - Tools: ToolRegistry schemas      │  │   │   │ │
│  │  │    │                                      │  │   │   │ │
│  │  │    ├─ Parse response ◄──────────────────┘  │   │   │ │
│  │  │    │  │                                     │   │   │ │
│  │  │    │  ├─ thinking block ───────┐           │   │   │ │
│  │  │    │  │                         │           │   │   │ │
│  │  │    │  ├─ tool_use block ────┐  │           │   │   │ │
│  │  │    │  │                      │  │           │   │   │ │
│  │  │    │  │  ┌──────────────────▼──▼───────┐   │   │   │ │
│  │  │    │  │  │ Queue.put()               │   │   │   │ │
│  │  │    │  │  │ - thinking_block          │───┼───┼───┼─┼┐│
│  │  │    │  │  │ - tool_use                │   │   │   │ │││
│  │  │    │  │  │ - tool_result             │   │   │   │ │││
│  │  │    │  │  │ - text_block              │   │   │   │ │││
│  │  │    │  │  │ - complete                │   │   │   │ │││
│  │  │    │  │  └───────────────────────────┘   │   │   │ │││
│  │  │    │  │                      │            │   │   │ │││
│  │  │    │  │  ┌──────────────────▼──────────┐ │   │   │ │││
│  │  │    │  │  │ ToolRegistry.execute_tool() │ │   │   │ │││
│  │  │    │  │  │ - user_id for credentials   │ │   │   │ │││
│  │  │    │  │  │ - Execute tool              │ │   │   │ │││
│  │  │    │  │  │ - Return result             │ │   │   │ │││
│  │  │    │  │  └──────────────┬──────────────┘ │   │   │ │││
│  │  │    │  │                 │                 │   │   │ │││
│  │  │    │  ├─ Add tool_result to messages     │   │   │ │││
│  │  │    │  └─ Loop to next turn               │   │   │ │││
│  │  │    │                                      │   │   │ │││
│  │  │    └─ BREAK if no tool_use blocks        │   │   │ │││
│  │  │                                           │   │   │ │││
│  │  │ 4. Save conversation to SQLite ───────┐  │   │   │ │││
│  │  │                                        │  │   │   │ │││
│  │  │ 5. Queue.put({'type': 'complete'}) ───┼──┼───┼───┼─┼┤│
│  │  │                                        │  │   │   │ │││
│  │  │ 6. Release lock                        │  │   │   │ │││
│  │  └────────────────────────────────────────┼──┘   │   │ │││
│  │                                            │      │   │ │││
│  └────────────────────────────────────────────┼──────┘   │ │││
│                                               │          │ │││
│  ┌────────────────────────────────────────────▼────────┐ │ │││
│  │  UNIFIED SESSION MANAGER                            │ │ │││
│  │  ├─ SQLite: sessions.db (persistence)               │ │ │││
│  │  ├─ In-memory cache (active sessions)               │ │ │││
│  │  ├─ Queue management (SSE events)                   │ │ │││
│  │  └─ Lock management (thread safety)                 │ │ │││
│  └─────────────────────────────────────────────────────┘ │ │││
│                                                           │ │││
└───────────────────────────────────────────────────────────┼─┼┼┘
                                                            │ │││
                  ┌─────────────────────────────────────────┼─┼┼┐
                  │         IN-MEMORY QUEUE                 │ │││
                  │  [                                      │ │││
                  │   {type:'thinking',content:'...'},  ◄───┘ │││
                  │   {type:'tool_use',tool_name:'...'},  ◄───┼┘│
                  │   {type:'tool_result',output:'...'},  ◄───┼─┘
                  │   {type:'text_block',content:'...'},  ◄───┘
                  │   {type:'complete',result:'...'}
                  │  ]
                  └─────────────────┬─────────────────────────┘
                                    │
                                    │ queue.get(timeout=30)
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BROWSER EVENT STREAM                         │
│                                                                 │
│  const eventSource = new EventSource('/stream/1?session_id=...');│
│  eventSource.onmessage = (event) => {                          │
│    const data = JSON.parse(event.data);                        │
│    // Process events as they arrive from queue                 │
│  };                                                             │
└─────────────────────────────────────────────────────────────────┘

BENEFITS:
├─ Flask thread NEVER blocked (returns 200 immediately)
├─ Session persistence (survives restart, loads conversation)
├─ Multi-tab support (separate queues per session_id)
├─ Queue-based buffering (events don't get lost)
├─ Automatic multi-turn loop (up to 10 turns)
├─ Interleaved thinking (visible between tool uses)
└─ File upload support (PDFs, images via base64)
```

---

## 🔄 Message Flow Comparison

### AI_agents: Direct SSE Streaming

```
USER MESSAGE
    │
    ▼
┌───────────────────────────────────────┐
│ handle_main_chat()                    │
│ ├─ Build messages array               │
│ ├─ for turn in range(MAX_TURNS):      │
│ │  ├─ Call Anthropic                  │
│ │  ├─ Parse blocks                    │
│ │  │  ├─ thinking → yield SSE         │ ───► BROWSER
│ │  │  ├─ tool_use → execute           │
│ │  │  └─ text → yield SSE             │ ───► BROWSER
│ │  └─ Add tool_result to messages     │
│ └─ Return                              │
└───────────────────────────────────────┘

Timeline:
0s ────────── 30s ────────── 60s ────────── 90s ────────── 120s
│              │              │              │              │
Start          Tool 1         Tool 2         Tool 3         Done
│              │              │              │              │
└─────────────────── Flask Thread BLOCKED ──────────────────┘
                    (Cannot serve other requests)
```

### In_House_SQL: Queue-Based Streaming

```
USER MESSAGE
    │
    ▼
┌─────────────────────────┐
│ start_agent()           │
│ ├─ Load session         │
│ ├─ Spawn thread ──────┐ │
│ └─ Return 200 (50ms)   │ │
└─────────────────────────┘ │
         │                  │
         │ (non-blocking)   │ (background)
         │                  │
         ▼                  ▼
    ┌─────────┐    ┌──────────────────────┐
    │ BROWSER │    │ run_agent_worker()   │
    │ /stream │    │ ├─ Call Anthropic    │
    │         │    │ ├─ Parse blocks      │
    │         │    │ │  ├─ thinking       │ ───► Queue
    │         │    │ │  ├─ tool_use       │ ───► Queue
    │         │◄───┼─┤  └─ text           │ ───► Queue
    │         │    │ ├─ Execute tools     │
    │         │    │ └─ Save conversation │
    └─────────┘    └──────────────────────┘
         │                      │
         │ queue.get()          │ queue.put()
         │                      │
         ▼                      ▼
    ┌──────────────────────────────┐
    │     IN-MEMORY QUEUE          │
    │  [event1, event2, event3...] │
    └──────────────────────────────┘

Timeline:
0s ────────── 30s ────────── 60s ────────── 90s ────────── 120s
│              │              │              │              │
Start          Tool 1         Tool 2         Tool 3         Done
│ Return 200   │              │              │              │
│ (50ms)       └──────────────┴──────────────┴──────────────┘
│                     Background Thread (non-blocking)
│
└─ Flask thread FREE (can serve other requests immediately)
```

---

## 🗄️ Session Persistence Architecture

### AI_agents: No Persistence

```
┌─────────────────────────────────────┐
│  FLASK APP (In-Memory Only)        │
│                                     │
│  sessions = {}  ← Transient state   │
│  {                                  │
│    "session_123": {                 │
│      messages: [...],               │
│      tools_used: [...],             │
│      context: {...}                 │
│    }                                │
│  }                                  │
│                                     │
│  ⚠️ Lost on server restart          │
│  ⚠️ Not shared across processes     │
└─────────────────────────────────────┘
```

### In_House_SQL: SQLite Persistence

```
┌──────────────────────────────────────────────────────────┐
│  UNIFIED SESSION MANAGER (Dual Storage)                  │
│                                                           │
│  ┌─────────────────────┐     ┌──────────────────────┐   │
│  │  IN-MEMORY CACHE    │     │  SQLite: sessions.db │   │
│  │  (Fast Access)      │◄───►│  (Persistence)       │   │
│  │                     │     │                      │   │
│  │  sessions = {       │     │  CREATE TABLE sessions(│
│  │    "uuid": {        │     │    session_id TEXT,  │   │
│  │      conversation,  │     │    ui_context TEXT,  │   │
│  │      metadata,      │     │    agent_id TEXT,    │   │
│  │      created_at,    │     │    conversation TEXT,│   │
│  │      last_active    │     │    metadata TEXT,    │   │
│  │    }                │     │    created_at,       │   │
│  │  }                  │     │    last_active       │   │
│  │                     │     │  )                   │   │
│  └─────────────────────┘     └──────────────────────┘   │
│           │                            │                 │
│           │ Cache miss                 │                 │
│           └────────► Load ────────────►│                 │
│                      from DB                             │
│                                                           │
│  Survives server restart                              │
│  Shared across processes (via SQLite)                 │
│  Multi-tab support (unique session_id per tab)        │
└──────────────────────────────────────────────────────────┘

Example Session Data:
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "ui_context": "triple_agent",
  "agent_id": "1",
  "conversation": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ],
  "metadata": {
    "user_id": 1,
    "tool_calls": 3,
    "thinking_tokens": 5420
  },
  "created_at": "2025-10-30T10:00:00Z",
  "last_active": "2025-10-30T10:05:23Z"
}
```

---

## 🔧 Tool Execution Comparison

### AI_agents: Synchronous in Route

```
┌──────────────────────────────────────────────────────────┐
│  AGENT_ROUTES.PY (handle_main_chat)                      │
│                                                           │
│  for block in response.content:                          │
│    if block.type == "tool_use":                          │
│                                                           │
│      ┌────────────────────────────────────────────┐     │
│      │ tool_registry.execute_tool()                │     │
│      │ ├─ Lookup tool implementation               │     │
│      │ ├─ Inject credentials (user_id=1)           │     │
│      │ ├─ Execute SYNCHRONOUSLY ◄────────────────  │     │
│      │ │  (Flask thread blocked)                   │     │
│      │ └─ Return result                            │     │
│      └────────────────────────────────────────────┘     │
│                                                           │
│      yield SSE event (tool_use)                          │
│      yield SSE event (tool_result)                       │
│                                                           │
│  ⚠️ Flask thread blocked during tool execution           │
│  ⚠️ Other requests wait in queue                         │
└──────────────────────────────────────────────────────────┘
```

### In_House_SQL: Asynchronous in Background

```
┌──────────────────────────────────────────────────────────┐
│  BACKGROUND THREAD (agent_worker.py)                     │
│                                                           │
│  for block in response.content:                          │
│    if block.type == "tool_use":                          │
│                                                           │
│      ┌────────────────────────────────────────────┐     │
│      │ tool_registry.execute_tool()                │     │
│      │ ├─ Lookup tool implementation               │     │
│      │ ├─ Inject credentials (user_id=1)           │     │
│      │ ├─ Execute in BACKGROUND ◄────────────────  │     │
│      │ │  (Flask thread free)                      │     │
│      │ └─ Return result                            │     │
│      └────────────────────────────────────────────┘     │
│                                                           │
│      queue.put({'type': 'tool_use', ...})                │
│      queue.put({'type': 'tool_result', ...})             │
│                │                                          │
│                └─────► Queue ────► SSE Endpoint          │
│                                                           │
│  Flask thread never blocked                           │
│  Other requests served immediately                    │
└──────────────────────────────────────────────────────────┘
```

---

## 📦 File Upload Flow

### AI_agents: Basic Support

```
BROWSER: FormData
  ├─ message: "Analyze this"
  └─ file: invoice.pdf (binary)
      │
      ▼
FLASK: request.files.getlist('files')
  ├─ file.read() → bytes
  ├─ base64.b64encode(bytes)
  └─ Build content block
      │
      ▼
ANTHROPIC API: content blocks
  [
    {
      "type": "document",
      "source": {
        "type": "base64",
        "media_type": "application/pdf",
        "data": "JVBERi0xLjQKJ..."
      }
    },
    {
      "type": "text",
      "text": "Analyze this"
    }
  ]
```

### In_House_SQL: Full Support with Validation

```
BROWSER: FormData
  ├─ session_id: "uuid"
  ├─ message: "Analyze this"
  └─ files[]: [invoice.pdf, receipt.jpg]
      │
      ▼
FLASK: agent_routes.py
  ├─ request.form.get('session_id')
  ├─ request.form.get('message')
  └─ request.files.getlist('files')
      │
      ▼
FILE_ENCODING.PY: process_file_uploads()
  ├─ FOR each file:
  │  ├─ Validate size (< 32MB)
  │  ├─ Guess media type (PDF/JPEG/PNG/GIF/WEBP)
  │  ├─ Determine block type (document vs image)
  │  ├─ Base64 encode
  │  └─ Build content block
  └─ Return: List[content_block]
      │
      ▼
BACKGROUND THREAD: agent_worker.py
  ├─ Receive: file_data (List[Dict])
  ├─ Build content blocks
  ├─ Add to messages array
  └─ Send to Anthropic API
      │
      ▼
ANTHROPIC API: Process files
  ├─ PDFs: Extract text + analyze layout
  ├─ Images: Computer vision analysis
  └─ Multi-file: Compare/analyze together

File validation (size, type)
Media type detection (PDF vs image)
Multi-file support (batch uploads)
Error handling (invalid files)
```

---

## 🧠 Thinking Display Comparison

### AI_agents: Extended Thinking Only

```
ANTHROPIC API CALL:
{
  "model": "claude-3-7-sonnet-20250219",
  "max_tokens": 16000,
  "thinking": {
    "type": "enabled",
    "budget_tokens": 10000
  },
  //  NO interleaved thinking header
  "tools": [...],
  "tool_choice": {"type": "auto"}  // ← Blocks extended thinking!
}

RESPONSE:
{
  "content": [
    {"type": "thinking", "thinking": "Initial analysis..."},
    //  No more thinking blocks after tools
    {"type": "tool_use", "name": "search"},
    {"type": "text", "text": "Based on results..."}
  ]
}

LIMITATION:
├─ tool_choice=auto BLOCKS extended thinking
├─ Thinking only appears at START of response
└─ No reasoning visible during tool execution
```

### In_House_SQL: Interleaved Thinking (Beta)

```
ANTHROPIC API CALL:
{
  "model": "claude-3-7-sonnet-20250219",
  "max_tokens": 16000,
  "thinking": {
    "type": "enabled",
    "budget_tokens": 10000
  },
  // INTERLEAVED THINKING BETA HEADER
  "extra_headers": {
    "anthropic-beta": "interleaved-thinking-2025-05-14"
  },
  "tools": [...],
  "tool_choice": {"type": "auto"}  // ← Works with thinking!
}

RESPONSE:
{
  "content": [
    {"type": "thinking", "thinking": "Initial analysis..."},
    {"type": "tool_use", "name": "search"},
    {"type": "thinking", "thinking": "Based on search results..."},
    {"type": "tool_use", "name": "calculate"},
    {"type": "thinking", "thinking": "Finalizing answer..."},
    {"type": "text", "text": "The result is..."}
  ]
}

BENEFITS:
├─ Thinking visible THROUGHOUT response
├─ Shows reasoning between tool uses
├─ Better debugging (see AI decision-making)
└─ Improved UX (shows AI is "thinking")

BROWSER DISPLAY:
┌──────────────────────────────────────┐
│ 💭 THINKING: Initial analysis...     │ ← Dark blue background
├──────────────────────────────────────┤
│ 🔧 TOOL: search_google               │ ← Green text
│    {"query": "..."}                  │
├──────────────────────────────────────┤
│ 💭 THINKING: Based on search...      │ ← Dark blue background
├──────────────────────────────────────┤
│ 🔧 TOOL: calculate_quote             │ ← Green text
│    {"quantity": 1000}                │
├──────────────────────────────────────┤
│ 💭 THINKING: Finalizing answer...    │ ← Dark blue background
├──────────────────────────────────────┤
│ The result is $2,847.50              │ ← White text (response)
└──────────────────────────────────────┘
```

---

## 🔐 Credential Injection Flow

### AI_agents: Route-Based Injection

```
┌─────────────────────────────────────┐
│ BROWSER                             │
│ POST /api/agent/chat                │
│ Headers:                            │
│   Authorization: Bearer <jwt_token> │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ AUTH MIDDLEWARE                     │
│ ├─ Decode JWT token                 │
│ ├─ Extract user_id: 1               │
│ └─ Add to request.user              │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ AGENT_ROUTES.PY                     │
│ user_id = request.user.get('id')    │
│                                     │
│ tool_result = tool_registry.execute_tool(│
│   tool_name="gmail_send_email",     │
│   user_id=user_id,  ← Inject here   │
│   to="user@example.com",            │
│   subject="Test"                    │
│ )                                   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ CREDENTIAL_INJECTOR                 │
│ def get_credentials(user_id):       │
│   ├─ Query: user_platform_credentials│
│   ├─ WHERE user_id=1                │
│   └─ Return: {                      │
│       access_token: "...",          │
│       refresh_token: "..."          │
│     }                               │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ TOOL IMPLEMENTATION                 │
│ def gmail_send_email(**kwargs):     │
│   user_id = kwargs.get('_user_id')  │
│   creds = kwargs.get('_injected_credentials')│
│   # Use creds to call Gmail API     │
└─────────────────────────────────────┘
```

### In_House_SQL: Worker Thread Injection

```
┌─────────────────────────────────────┐
│ BROWSER                             │
│ POST /api/agent/1/start             │
│ Headers:                            │
│   Authorization: Bearer <jwt_token> │
│ Body:                               │
│   {"message": "...", "user_id": 1}  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ AGENT_ROUTES.PY (start_agent)       │
│ user_id = request.json.get('user_id')│
│ # Validate user_id matches JWT      │
│                                     │
│ threading.Thread(                   │
│   target=run_agent_worker,          │
│   args=(                            │
│     agent_id,                       │
│     prompt,                         │
│     file_data,                      │
│     lock,                           │
│     session_id,                     │
│     queue,                          │
│     conversation,                   │
│     context,                        │
│     ai_client,                      │
│     user_id  ← Pass to worker       │
│   )                                 │
│ ).start()                           │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ BACKGROUND THREAD (agent_worker.py) │
│ def run_agent_worker(..., user_id): │
│                                     │
│   tool_result = tool_registry.execute_tool(│
│     tool_name="gmail_send_email",   │
│     user_id=user_id,  ← Use here    │
│     to="user@example.com",          │
│     subject="Test"                  │
│   )                                 │
│                                     │
│   # Same credential injection flow  │
│   # as AI_agents from here          │
└─────────────────────────────────────┘

user_id validated in route (before thread spawn)
Passed securely to background thread
Same credential_injector.py used
```

---

## 📈 Performance Metrics

### Request Handling Capacity

```
AI_AGENTS (Synchronous):
┌─────────────────────────────────────────────────────────┐
│ Time:  0s ───── 30s ───── 60s ───── 90s ───── 120s     │
│        │        │        │        │        │            │
│ Req 1: [█████████████████████████████████████] (120s)  │
│ Req 2:                                        [waiting] │
│ Req 3:                                        [waiting] │
│ Req 4:                                        [waiting] │
│                                                          │
│ Throughput: 1 request per 120s = 0.5 req/min            │
│ Max concurrent: 1 (blocking)                            │
└─────────────────────────────────────────────────────────┘

IN_HOUSE_SQL (Asynchronous):
┌─────────────────────────────────────────────────────────┐
│ Time:  0s ───── 30s ───── 60s ───── 90s ───── 120s     │
│        │        │        │        │        │            │
│ Req 1: [█] (50ms) Background: [──────────────────────]  │
│ Req 2:    [█] (50ms) Background: [─────────────────]    │
│ Req 3:       [█] (50ms) Background: [──────────────]    │
│ Req 4:          [█] (50ms) Background: [───────────]    │
│                                                          │
│ Throughput: 4 requests in 0.2s = 1200 req/min           │
│ Max concurrent: Limited by background threads (50+)     │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Migration Priority Matrix

```
┌──────────────────────────────────────────────────────────┐
│                    PRIORITY MATRIX                       │
│                                                          │
│  High Impact,  │ 1. Background Worker                   │
│  High Effort   │ 2. Session Persistence                 │
│                │ 3. Queue-based SSE                     │
│  ──────────────┼──────────────────────────────────────  │
│  High Impact,  │ 4. File Upload Handling                │
│  Low Effort    │ 5. Interleaved Thinking                │
│                │                                        │
│  ──────────────┼──────────────────────────────────────  │
│  Low Impact,   │ 6. Response Helpers                    │
│  Low Effort    │ 7. Error Messages                      │
│                                                          │
└──────────────────────────────────────────────────────────┘

IMPLEMENTATION ORDER:
1️⃣ Copy core files (session manager, file encoding)
2️⃣ Create agent_worker.py (background execution)
3️⃣ Update agent_routes_v4.py (split endpoints)
4️⃣ Test SSE streaming (queue-based)
5️⃣ Enable interleaved thinking (beta header)
6️⃣ Deploy and monitor
```

---

**END OF VISUAL COMPARISON**

See also: MIGRATION_GUIDE_INHOUSEPRINT_TO_AI_AGENTS.md
