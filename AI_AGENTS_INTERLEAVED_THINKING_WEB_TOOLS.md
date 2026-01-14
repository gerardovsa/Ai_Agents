# AI_Agents: Interleaved Thinking & Web Tools Architecture

**Date:** November 15, 2025  
**Source Project:** https://github.com/gerardovsa/Ai_Agents/tree/v5  
**Purpose:** Complete analysis of how interleaved thinking, web search, web fetch, and streaming are structured

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Interleaved Thinking Architecture](#interleaved-thinking-architecture)
3. [Web Search & Web Fetch (Server Tools)](#web-search--web-fetch-server-tools)
4. [Streaming Agent Architecture](#streaming-agent-architecture)
5. [Tool Execution Flow](#tool-execution-flow)
6. [System Prompt Engineering](#system-prompt-engineering)
7. [Integration with Health_app](#integration-with-health_app)

---

## 📊 Executive Summary

### Key Innovation: Interleaved Thinking

AI_Agents uses **Anthropic's Interleaved Thinking Beta** to enable Claude to:
- **Think between tool calls** (not just at the start)
- **Reason about tool results** before next action
- **Show reasoning process** to users in real-time
- **Self-correct** based on intermediate results

### Architecture Highlights

```
┌─────────────────────────────────────────────────────────────┐
│                    AI_Agents Architecture                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌────────────┐ │
│  │   Extended   │────▶│  Interleaved │────▶│  Streaming │ │
│  │   Thinking   │     │   Thinking   │     │   Worker   │ │
│  │  (10k tokens)│     │    (Beta)    │     │  (Multi-   │ │
│  └──────────────┘     └──────────────┘     │   Round)   │ │
│                                             └────────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              SERVER TOOLS (Anthropic)                │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  • web_search (real-time, 5 uses/conversation)      │  │
│  │  • web_fetch (URLs/PDFs, 10 uses/conversation)      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           CLIENT TOOLS (Registry V3)                 │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  • 584 tools across 20+ platforms                   │  │
│  │  • Google Workspace (307 tools)                     │  │
│  │  • Microsoft 365 (115+ tools)                       │  │
│  │  • Meta-tools (progressive discovery)               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Interleaved Thinking Architecture

### What is Interleaved Thinking?

**Standard Extended Thinking:**
```
[Thinking] → [Tool Use] → [Tool Use] → [Text Response]
   ↑
Only at START
```

**Interleaved Thinking:**
```
[Thinking] → [Tool Use] → [Thinking] → [Tool Use] → [Thinking] → [Text Response]
   ↑                          ↑                         ↑
Thinking BETWEEN actions (analyzes tool results)
```

### API Configuration

**File:** `inhouse_modules/tool_use_agent.py` (Lines 2798-2820)

```python
response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=16000,
    temperature=1.0,
    
    # Extended Thinking with Interleaved Thinking
    thinking={
        "type": "enabled",
        "budget_tokens": 10000  # Up to 10k tokens for reasoning
    },
    
    # CRITICAL: Interleaved thinking beta header
    extra_headers={
        "anthropic-beta": "interleaved-thinking-2025-05-14"
    },
    
    # Tool definitions (client + server)
    tools=self._get_tool_definitions(),
    
    # Tool choice (must be 'auto' or 'none' with thinking)
    tool_choice={"type": "auto"},
    
    system=system_prompt,
    messages=conversation
)
```

### Token Cost Analysis

| Component | Tokens | Cost (per request) |
|-----------|--------|-------------------|
| **Thinking tokens** | 500-10,000 | $0.002-$0.015 |
| **Input tokens** | 5,000-20,000 | $0.015-$0.060 |
| **Output tokens** | 1,000-5,000 | $0.015-$0.075 |
| **TOTAL** | 6,500-35,000 | $0.032-$0.150 |

**Average cost with thinking:** $0.09/request  
**Trade-off:** Higher quality responses with visible reasoning = WORTH IT

### Response Parsing

**File:** `inhouse_modules/tool_use_agent.py` (Lines 2840-3029)

```python
# Process streaming events in real-time
for event in stream:
    
    # THINKING BLOCK
    if event.type == "content_block_start":
        if event.content_block.type == 'thinking':
            assistant_content.append({'type': 'thinking', 'thinking': ''})
    
    # THINKING DELTA (accumulate text)
    elif event.type == "content_block_delta":
        if hasattr(event.delta, 'thinking'):
            # Accumulate thinking text
            accumulated_thinking[content_block_index] += event.delta.thinking
    
    # TEXT BLOCK
    elif event.type == "content_block_start":
        if event.content_block.type == 'text':
            assistant_content.append({'type': 'text', 'text': ''})
    
    # TOOL USE BLOCK
    elif event.type == "content_block_start":
        if event.content_block.type == 'tool_use':
            current_tool_use = {
                'type': 'tool_use',
                'id': event.content_block.id,
                'name': event.content_block.name,
                'input': {}
            }
```

### Thinking Block Storage Strategy

**File:** `docs/archive/THINKING_BLOCK_FIX_COMPLETE.md`

```markdown
## What Gets Stored (BEST PRACTICE)

| Block Type | Real-Time SSE | Stored in DB | Sent to Claude | On Reload UI |
|------------|---------------|--------------|----------------|--------------|
| **thinking** | ✅ Show | ❌ No | ❌ No | ❌ No |
| **text** | ✅ Show | ✅ Yes | ✅ Yes | ✅ Show |
| **tool_use** | ✅ Show | ✅ Yes | ✅ Yes | ✅ Show (collapsed) |
| **tool_result** | ✅ Show | ❌ No | ✅ Yes* | ❌ No |

*Tool results sent to Claude **during active session** but not stored for future sessions

REASON:
- Thinking is for the current turn only
- Claude doesn't need previous thinking for future requests
- Everything important from thinking goes into the text response
- Text response is what provides context for future turns
```

**Code Implementation:**

```python
def prepare_content_for_storage(content: List[Dict]) -> List[Dict]:
    """
    BEST PRACTICE: Keep only text + tool_use blocks
    
    Removes:
    - thinking blocks (causes API errors if stored)
    - tool_result blocks (too verbose, not needed)
    
    Keeps:
    - text blocks (main response)
    - tool_use blocks (transparency - shows what AI requested)
    """
    return [
        block for block in content
        if block.get('type') in ('text', 'tool_use')
    ]
```

### Thinking Block Ordering (API Requirement)

**Anthropic API Rule:** If assistant message contains thinking blocks, **first block MUST be thinking**

**File:** `AI_infrastructure/core/combined_agent_worker.py` (Lines 301-331)

```python
def validate_and_reorder_assistant_content(content_blocks: List[Dict]) -> List[Dict]:
    """
    CRITICAL: Anthropic API requires thinking blocks FIRST
    
    Reorders content blocks to comply with API requirement:
    - All thinking blocks FIRST
    - Then all other blocks (text, tool_use)
    """
    thinking_blocks = [
        b for b in content_blocks 
        if b.get('type') in ('thinking', 'redacted_thinking')
    ]
    
    other_blocks = [
        b for b in content_blocks 
        if b.get('type') not in ('thinking', 'redacted_thinking')
    ]
    
    return thinking_blocks + other_blocks
```

### UI Display of Thinking Blocks

**Real-time streaming shows thinking in amber bubble:**

```javascript
// UI/triple_agent.html (Lines 2594-2616)
if (blockType === 'thinking') {
    // Add separator
    const thinkingHr = document.createElement('hr');
    thinkingHr.style.opacity = '0.3';
    thinkingHr.style.margin = '10px 0';
    currentAIMessages[agentId].appendChild(thinkingHr);
    
    // Add [THINKING] header
    const thinkingHeader = document.createElement('span');
    thinkingHeader.style.color = '#60A5FA'; // Blue
    thinkingHeader.style.fontWeight = 'bold';
    thinkingHeader.textContent = '[THINKING]\n';
    currentAIMessages[agentId].appendChild(thinkingHeader);
}
```

---

## 🌐 Web Search & Web Fetch (Server Tools)

### Server Tool Architecture

**Server tools are executed by Anthropic on their servers** (not in local tool registry)

```
┌─────────────────────────────────────────────────────────┐
│              CLIENT (AI_Agents Application)              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Include server tools in API call:                   │
│     {                                                    │
│       "type": "web_search_20250305",                    │
│       "name": "web_search",                             │
│       "max_uses": 5                                     │
│     }                                                    │
│                                                          │
│  2. Claude decides to use web_search                    │
│     {"type": "tool_use", "name": "web_search", ...}    │
│                                                          │
│  3. Response includes server_tool_use block             │
│     {"type": "server_tool_use", "name": "web_search"}  │
│                                                          │
│  4. Response includes web_search_tool_result            │
│     {"type": "web_search_tool_result",                 │
│      "content": [{url, title, snippet, ...}]}          │
│                                                          │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│           ANTHROPIC API (Server-Side Execution)         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  • Executes web_search on Anthropic's servers          │
│  • Fetches real-time web data                          │
│  • Returns results with encrypted_content (for         │
│    citations in multi-turn conversations)              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### web_search Configuration

**File:** `AI_infrastructure/core/unified_ai_client.py` (Lines 930-961)

```python
# Web Search server tool
if enable_web_search:
    server_tools.append({
        "type": "web_search_20250305",  # Anthropic's tool type
        "name": "web_search",            # Tool name Claude uses
        "user_location": {
            "type": "approximate",
            "city": "Brisbane",
            "region": "Queensland",
            "country": "AU",
            "timezone": "Australia/Brisbane"
        },
        "max_uses": 5  # Limit per conversation
    })
```

### web_fetch Configuration

**File:** `AI_infrastructure/core/unified_ai_client.py` (Lines 961-970)

```python
# Web Fetch server tool (BETA)
if enable_web_fetch:
    server_tools.append({
        "type": "web_fetch_20250910",   # Anthropic's tool type
        "name": "web_fetch",             # Tool name Claude uses
        "max_uses": 10,                  # Limit per conversation
        "citations": {"enabled": True},  # Enable source citations
        "max_content_tokens": 100000     # Max content per fetch
    })
```

### Meta-Tool Guidance for Server Tools

**Problem:** Claude might search for web_search in the tool registry (which doesn't exist there)

**Solution:** `search_tools()` meta-tool detects web search queries and provides guidance

**File:** `tools/implementations/meta_tools.py` (Lines 326-397)

```python
def search_tools(query: str, **kwargs) -> Dict[str, Any]:
    """Search for tools by keyword, platform, or use case"""
    
    # Detect web search queries
    web_search_queries = [
        'websearch', 'web_search', 'web search', 'search web',
        'search internet', 'internet search', 'tavily', 'brave',
        'brave search', 'search engine', 'online search', 'web query'
    ]
    
    if any(q in query.lower() for q in web_search_queries):
        return {
            "success": True,
            "match_count": 1,
            "query": query,
            "guidance": """SERVER TOOL AVAILABLE: web_search

You have a web_search SERVER TOOL that's ALWAYS available.
This tool runs on Anthropic's servers and provides real-time internet access.

HOW TO USE (NO execute_tool NEEDED):
You don't call search_tools() or execute_tool() for this. Just USE IT DIRECTLY in your content blocks.

EXAMPLE:
User: "What's the latest AI news?"

Your response should include:
{
  "type": "tool_use",
  "name": "web_search",
  "input": {
    "query": "latest AI news November 2025"
  }
}

Claude API executes search automatically on server
You receive results with URLs, titles, content, page age
You analyze and respond to user

KEY POINTS:
- Server tool (no client execution)
- Max 5 searches per conversation
- Returns URLs, titles, snippets, page age
- Localized to Brisbane, Queensland, Australia
- Use for: current events, news, trends, recent data

WHEN TO USE:
- Current events, news, trends
- Latest pricing or market data
- Recent technical standards
- Real-time information
- Any info beyond your knowledge cutoff (April 2024)

NEVER say "I need to find a web search tool" - YOU ALREADY HAVE IT!
Just use it directly.""",
            "available_platforms": ["anthropic_server_tools"],
            "tools": [{
                "name": "web_search",
                "description": "Server-side real-time web search (always available)",
                "platform": "anthropic_server_tools",
                "type": "server_tool",
                "usage": "Use directly in content blocks with tool_use type"
            }],
            "critical_note": "This is a SERVER TOOL - it's not in your tools list but you can use it directly."
        }
```

### Server Tool Response Handling

**File:** `AI_infrastructure/core/unified_ai_client.py` (Lines 420-460)

```python
# SERVER TOOL: server_tool_use
elif event.content_block.type == 'server_tool_use':
    print(f"[SERVER TOOL] {event.content_block.name} initiated")
    assistant_message['content'].append({
        'type': 'server_tool_use',
        'id': event.content_block.id,
        'name': event.content_block.name
    })

# SERVER TOOL: web_search_tool_result
elif event.type == 'server_tool_result':
    if hasattr(event, 'tool_result_type'):
        if event.tool_result_type == 'web_search':
            print(f"[SERVER TOOL] web_search returned {len(event.search_results)} results")
            assistant_message['content'].append({
                'type': 'web_search_tool_result',
                'search_results': event.search_results
            })

# SERVER TOOL: web_fetch_tool_result
elif event.type == 'server_tool_result':
    if hasattr(event, 'tool_result_type'):
        if event.tool_result_type == 'web_fetch':
            print(f"[SERVER TOOL] web_fetch retrieved content")
            assistant_message['content'].append({
                'type': 'web_fetch_tool_result',
                'content': event.content
            })
```

### System Prompt: Server Tools Section

**File:** `AI_infrastructure/prompts/tool_usage_system_prompt.md` (Lines 1396-1503)

```markdown
## **SERVER TOOLS: WEB SEARCH & WEB FETCH**

You have real-time internet access via two server tools executed by Anthropic:

**CURRENT CONTEXT:** {{USER_LOCATION}}

### **web_search - Real-Time Web Search**
Searches internet for current information (news, pricing, trends, standards, verification)
- **Returns:** URLs, titles, content snippets, page age, sources
- **Limit:** 5 searches per conversation
- **Localized to:** User's detected location and timezone (from IP)
- **Executed by:** Anthropic servers (not local tools)

**✅ WHEN TO USE web_search:**

1. **User explicitly requests:**
   - "Search online for...", "Look up...", "Find information about...", "Research..."
   - "What's the latest...", "Current price of...", "Check if...", "Is there news about..."

2. **Current/time-sensitive information (after April 2024):**
   - News, events, breaking stories, recent developments
   - Real-time data: weather, stock prices, sports scores, traffic, cryptocurrency
   - Latest versions: software releases, product launches, API updates

3. **Verification needs:**
   - "Is this still true?", "Has this changed?", "Verify...", "Confirm..."
   - Fact-checking recent claims or outdated info

4. **Local/regional information (changes frequently):**
   - Brisbane/Australia-specific: "business hours", "best restaurants", "local events"
   - Regional pricing, services, availability

**DECISION TREE:**

```
User asks question
    ↓
Is this about current/recent events (after April 2024)?
    YES → Use web_search
    NO → Continue
        ↓
    Is this local/regional info that changes frequently?
        YES → Use web_search
        NO → Continue
            ↓
        Am I uncertain and need verification?
            YES → Use web_search
            NO → Continue
                ↓
            User explicitly asked me to search/research?
                YES → Use web_search
                NO → Use my training data
```

### **web_fetch - Fetch & Analyze URLs**
Fetches full content from specific URLs (web pages, PDFs, documents)
- **Returns:** Complete document content with citations enabled
- **Limit:** 10 fetches per conversation
- **Max content:** 100,000 tokens per fetch
- **Executed by:** Anthropic servers (not local tools)

**When to use:**
- Read specific URL: "Analyze this article: https://..."
- Extract from PDF: "Read this report: https://example.com/doc.pdf"
- Follow up on search: Fetch top results after web_search
- Deep dive: Get full content when snippets aren't enough
```

---

## 🌊 Streaming Agent Architecture

### Multi-Round Tool Execution Pattern

**AI_Agents implements recursive continuation pattern** (from InHouse Print ToolUseAgent)

```
Round 1:
  User: "Find latest AI news and email it to John"
  Claude: [Thinking: Need to search first]
  Claude: [Tool Use: web_search]
  API: [Server Tool Result: web_search]
  ↓
  stop_reason = "tool_use" → CONTINUE
  ↓
Round 2:
  Claude: [Thinking: Received search results, analyze them]
  Claude: [Text: "Found 3 articles about AI breakthroughs"]
  Claude: [Tool Use: gmail_smart_compose_and_send]
  Registry: [Execute: gmail_smart_compose_and_send]
  ↓
  stop_reason = "tool_use" → CONTINUE
  ↓
Round 3:
  Claude: [Thinking: Email sent successfully]
  Claude: [Text: "I've emailed John with the latest AI news"]
  ↓
  stop_reason = "end_turn" → COMPLETE
```

### Streaming Worker Implementation

**File:** `AI_infrastructure/core/combined_agent_worker.py` (Lines 932-1100)

```python
def execute_streaming_request(
    session_id: str,
    user_prompt: str,
    conversation_history: List[Dict],
    system_prompt: str,
    tools: List[Dict],
    user_id: Optional[int] = None,
    max_rounds: int = 20,
    current_round: int = 1
) -> Generator[Dict[str, Any], None, None]:
    """
    Execute multi-round streaming request with tool use
    
    Features:
    - Real-time SSE streaming (thinking, text, tool_use, tool_result)
    - Recursive continuation after tool execution
    - Unlimited rounds of tool use (up to max_rounds)
    - Proper conversation history management
    - Credential injection for OAuth tools
    
    Architecture:
    1. Stream thinking blocks → SSE event: "thinking"
    2. Stream text blocks → SSE event: "content_delta"
    3. Stream tool_use blocks → SSE event: "tool_use"
    4. Execute tools → SSE event: "tool_result"
    5. If stop_reason == "tool_use" → RECURSIVE CALL
    6. If stop_reason == "end_turn" → SSE event: "complete"
    """
    
    log_prefix = f"[Round {current_round}]"
    print(f"{log_prefix} Starting streaming request")
    
    # Initialize Anthropic client
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    model = "claude-sonnet-4-5-20250929"
    
    # Build messages array
    messages = []
    for msg in conversation_history:
        # Validate and reorder content blocks (thinking first)
        if msg['role'] == 'assistant' and isinstance(msg['content'], list):
            msg['content'] = validate_and_reorder_assistant_content(msg['content'])
        messages.append(msg)
    
    # Add user prompt (first round only)
    if user_prompt and current_round == 1:
        messages.append({'role': 'user', 'content': user_prompt})
    
    # Track content blocks and stop reason
    stop_reason = None
    assistant_content = []
    
    # Stream API call
    with client.messages.stream(
        model=model,
        max_tokens=16000,
        temperature=1.0,
        
        # Extended Thinking with Interleaved Thinking
        thinking={
            "type": "enabled",
            "budget_tokens": 10000
        },
        extra_headers={
            "anthropic-beta": "interleaved-thinking-2025-05-14"
        },
        
        system=system_prompt,
        messages=messages,
        tools=tools
    ) as stream:
        
        # Track current block for delta accumulation
        current_block_index = -1
        accumulated_text = {}
        accumulated_thinking = {}
        
        for event in stream:
            
            # CONTENT BLOCK START
            if event.type == 'content_block_start':
                current_block_index += 1
                
                # Thinking block
                if event.content_block.type == 'thinking':
                    accumulated_thinking[current_block_index] = ''
                    assistant_content.append({
                        'type': 'thinking',
                        'thinking': ''
                    })
                    yield {
                        'type': 'thinking_start',
                        'block_index': current_block_index
                    }
                
                # Text block
                elif event.content_block.type == 'text':
                    accumulated_text[current_block_index] = ''
                    assistant_content.append({
                        'type': 'text',
                        'text': ''
                    })
                    yield {
                        'type': 'text_start',
                        'block_index': current_block_index
                    }
                
                # Tool use block
                elif event.content_block.type == 'tool_use':
                    tool_data = {
                        'type': 'tool_use',
                        'id': event.content_block.id,
                        'name': event.content_block.name,
                        'input': {}
                    }
                    assistant_content.append(tool_data)
                    yield {
                        'type': 'tool_use_start',
                        'block_index': current_block_index,
                        'tool_name': event.content_block.name,
                        'tool_id': event.content_block.id
                    }
            
            # CONTENT BLOCK DELTA
            elif event.type == 'content_block_delta':
                
                # Thinking delta
                if hasattr(event.delta, 'thinking'):
                    delta = event.delta.thinking
                    accumulated_thinking[current_block_index] += delta
                    assistant_content[current_block_index]['thinking'] = accumulated_thinking[current_block_index]
                    
                    yield {
                        'type': 'thinking_delta',
                        'delta': delta,
                        'block_index': current_block_index
                    }
                
                # Text delta
                elif hasattr(event.delta, 'text'):
                    delta = event.delta.text
                    accumulated_text[current_block_index] += delta
                    assistant_content[current_block_index]['text'] = accumulated_text[current_block_index]
                    
                    yield {
                        'type': 'content_delta',
                        'delta': delta,
                        'block_index': current_block_index
                    }
                
                # Tool input delta (JSON accumulation)
                elif hasattr(event.delta, 'partial_json'):
                    # Accumulate tool input JSON
                    pass
            
            # CONTENT BLOCK STOP
            elif event.type == 'content_block_stop':
                yield {
                    'type': 'content_block_stop',
                    'block_index': current_block_index
                }
            
            # MESSAGE STOP
            elif event.type == 'message_stop':
                stop_reason = stream.get_final_message().stop_reason
                print(f"{log_prefix} stop_reason = {stop_reason}")
    
    # SERIALIZE CONTENT (thinking blocks first)
    serialized_content = validate_and_reorder_assistant_content(assistant_content)
    
    # Add assistant response to history
    conversation_history.append({
        'role': 'assistant',
        'content': serialized_content
    })
    
    # TOOL EXECUTION
    if stop_reason == 'tool_use':
        
        # Extract tool_use blocks
        tool_blocks = [b for b in serialized_content if b['type'] == 'tool_use']
        
        # Execute each tool
        tool_results = []
        for tool_block in tool_blocks:
            tool_name = tool_block['name']
            tool_id = tool_block['id']
            tool_input = tool_block['input']
            
            print(f"{log_prefix} Executing tool: {tool_name}")
            
            # Execute tool with credential injection
            from tools.registry_v3 import get_registry
            registry = get_registry()
            
            result = registry.execute_tool(
                tool_name=tool_name,
                _user_id=user_id,
                _injected_credentials=True,
                **tool_input
            )
            
            # Convert result to string
            result_str = json.dumps(result) if not isinstance(result, str) else result
            
            # Build tool_result content block
            tool_results.append({
                'type': 'tool_result',
                'tool_use_id': tool_id,
                'content': result_str
            })
            
            # Yield tool_result event
            yield {
                'type': 'tool_result',
                'tool_name': tool_name,
                'tool_id': tool_id,
                'result': result_str,
                'success': True
            }
        
        # Add tool results to conversation (as user role)
        conversation_history.append({
            'role': 'user',
            'content': tool_results
        })
        
        # RECURSIVE CALL - Continue conversation
        print(f"{log_prefix} Recursive call to round {current_round + 1}...")
        
        yield from execute_streaming_request(
            session_id=session_id,
            user_prompt="",  # Empty (continuing from tool results)
            conversation_history=conversation_history,
            system_prompt=system_prompt,
            tools=tools,
            user_id=user_id,
            max_rounds=max_rounds,
            current_round=current_round + 1
        )
    
    else:
        # Conversation complete
        yield {
            'type': 'complete',
            'stop_reason': stop_reason
        }
```

### SSE Event Streaming

**File:** `AI_infrastructure/routes/agent_routes_v4.py` (Lines 835-930)

```python
@agent_bp.route('/stream/<agent_id>', methods=['GET'])
def stream_agent(agent_id):
    """
    Universal SSE stream endpoint - MULTI-ROUND STREAMING
    """
    session_id = request.args.get('session_id')
    
    # Get conversation history
    state = agent_state_manager.get_or_create_state(agent_id, session_id, {})
    conversation = state.get('conversation', [])
    
    def generate():
        try:
            # Yield start event
            yield stream_sse_event('start', {'session_id': session_id})
            
            # Execute streaming request with multi-round support
            for event in execute_streaming_request(
                session_id=session_id,
                user_prompt=last_message,
                conversation_history=conversation_without_current,
                system_prompt=system_prompt,
                tools=tools,
                user_id=user_id
            ):
                # Yield SSE event
                event_type = event.get('type', 'unknown')
                yield stream_sse_event(event_type, event)
                
                # AUTO-SAVE: On completion, save thread to database
                if event_type == 'complete':
                    try:
                        final_state = agent_state_manager.get_state(agent_id, session_id)
                        final_conversation = final_state.get('conversation', [])
                        
                        # Save thread with metadata
                        thread_manager.save_thread(
                            session_id=session_id,
                            agent_id=agent_id,
                            user_id=user_id,
                            title=generate_title(final_conversation),
                            conversation=final_conversation,
                            metadata={'auto_saved': True, 'source': 'stream_completion'}
                        )
                    except Exception as e:
                        print(f"⚠️  Auto-save failed: {e}")
        
        except Exception as e:
            print(f"❌ Stream error: {e}")
            yield stream_sse_event('error', {'error': str(e)})
    
    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no'
    })
```

### SSE Event Format

```
event: thinking_start
data: {"block_index": 0}

event: thinking_delta
data: {"delta": "Let me analyze the ", "block_index": 0}

event: thinking_delta
data: {"delta": "user's request...", "block_index": 0}

event: content_block_stop
data: {"block_index": 0}

event: text_start
data: {"block_index": 1}

event: content_delta
data: {"delta": "I'll search for ", "block_index": 1}

event: tool_use_start
data: {"block_index": 2, "tool_name": "web_search", "tool_id": "toolu_123"}

event: tool_result
data: {"tool_name": "web_search", "tool_id": "toolu_123", "result": "{...}", "success": true}

event: complete
data: {"stop_reason": "end_turn"}
```

---

## 🔧 Tool Execution Flow

### Tool Categories

```
┌─────────────────────────────────────────────────────────────┐
│                      TOOL CATEGORIES                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           SERVER TOOLS (Anthropic Execution)           │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  • web_search (5 uses/conversation)                   │ │
│  │  • web_fetch (10 uses/conversation)                   │ │
│  │                                                        │ │
│  │  Execution: Anthropic servers                         │ │
│  │  Response: Included in API response                   │ │
│  │  No local code execution                              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            META TOOLS (Discovery/Navigation)           │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  • list_available_platforms                           │ │
│  │  • list_platform_tools                                │ │
│  │  • get_tool_schema                                    │ │
│  │  • search_tools                                       │ │
│  │  • recommend_tools_for_task                           │ │
│  │  • get_workflow_steps                                 │ │
│  │  • execute_tool (wrapper for registry execution)     │ │
│  │                                                        │ │
│  │  Execution: Local registry                            │ │
│  │  Purpose: Progressive tool discovery                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         CLIENT TOOLS (Local Registry Execution)        │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  • Google Workspace (307 tools)                       │ │
│  │  • Microsoft 365 (115 tools)                          │ │
│  │  • Slack, Stripe, WooCommerce, etc. (162 tools)      │ │
│  │                                                        │ │
│  │  Execution: Local Python functions                    │ │
│  │  Credential Injection: Per-user OAuth tokens          │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Tool Execution Decision Tree

```python
# AI_infrastructure/routes/agent_routes_v4.py (Lines 194-197)
class ToolExecutor:
    """Executes tools with proper credential injection and error handling"""
    
    def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user_id: Optional[int] = None,
        credentials: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Execute tool with credential injection
        
        Decision tree:
        1. Is tool a server tool? → Return error (already executed by Anthropic)
        2. Is tool a meta-tool? → Execute via meta_tools module
        3. Is tool a client tool? → Execute via registry with credential injection
        """
        
        # SERVER TOOLS - Should never reach here (executed by Anthropic)
        if tool_name in ['web_search', 'web_fetch']:
            return {
                'success': False,
                'error': f'{tool_name} is a server tool executed by Anthropic'
            }
        
        # META TOOLS - Execute via meta_tools module
        if tool_name in [
            'list_available_platforms', 'list_platform_tools',
            'get_tool_schema', 'search_tools', 'recommend_tools_for_task',
            'get_workflow_steps', 'execute_tool'
        ]:
            from tools.implementations import meta_tools
            func = getattr(meta_tools, tool_name)
            result = func(**parameters)
            return {'success': True, 'result': result}
        
        # CLIENT TOOLS - Execute via registry with credential injection
        from tools.registry_v3 import get_registry
        registry = get_registry()
        
        result = registry.execute_tool(
            tool_name=tool_name,
            _user_id=user_id,
            _injected_credentials=True,
            **parameters
        )
        
        return result
```

---

## 📝 System Prompt Engineering

### Complete System Prompt Structure

**File:** `AI_infrastructure/prompts/tool_usage_system_prompt.md` (1,503 lines)

```markdown
# AI Agent System Instructions v3 - COMPACT

You are a highly capable AI assistant with access to 584+ tools across 20+ platforms, plus real-time web access.

## **🎯 THREE-METHOD TOOL DISCOVERY SYSTEM**

**METHOD 1: list_platform_tools (FAST - See ALL tool names for platform)**
```json
execute_tool("list_platform_tools", {
  "platforms": ["google_workspace"]
})

Returns: {"gmail_send_email", "gmail_search_messages", "google_docs_create", ...}
```

**METHOD 2: search_tools (FASTEST - Find tools by keyword)**
```json
execute_tool("search_tools", {
  "query": "email"
})

Returns: {"gmail_send_email", "gmail_smart_compose_and_send", ...}
```

**METHOD 3: get_tool_schema (Get ONE tool's parameters)**
```json
execute_tool("get_tool_schema", {
  "tool_name": "gmail_send_email"
})

Returns: {parameters: {to, subject, body}, examples: [...]}
```

## **🌐 SERVER TOOLS: WEB SEARCH & WEB FETCH**

You have real-time internet access via two server tools executed by Anthropic:

### **web_search - Real-Time Web Search**
- **Returns:** URLs, titles, content snippets, page age, sources
- **Limit:** 5 searches per conversation
- **Localized to:** User's detected location and timezone
- **Use for:** Current events, news, pricing, trends, anything after April 2024

### **web_fetch - Fetch & Analyze URLs**
- **Returns:** Complete document content with citations enabled
- **Limit:** 10 fetches per conversation
- **Max content:** 100,000 tokens per fetch
- **Use for:** Analyze URLs, read documents, summarize web content

## **INTERLEAVED THINKING PATTERN**

You have Extended Thinking enabled with interleaved thinking capability.
- Think BETWEEN actions to analyze, plan, and reason
- Think before executing tools to determine best approach
- Think after tool results to assess and adjust strategy

**Example workflow:**
```
[Thinking: User wants latest news. Should use web_search first.]
[Tool Use: web_search("latest AI news")]
[Thinking: Found 5 articles. Most relevant is about GPT-5. Fetch full content.]
[Tool Use: web_fetch("https://example.com/gpt5-article")]
[Thinking: Article confirms GPT-5 launch. Now compose summary.]
[Text: Based on recent sources, GPT-5 was announced...]
```

## **WORKFLOW BEST PRACTICES**

### **Pattern 1: Research → Document → Share**
1. web_search → Find current data
2. google_docs_create → Document findings
3. gmail_send_email → Share with stakeholders

### **Pattern 2: Search → Analyze → Execute**
1. search_tools → Find relevant tools
2. get_tool_schema → Learn parameters
3. execute_tool → Complete task

### **Pattern 3: Multi-Platform Coordination**
1. google_calendar_list_events → Check availability
2. google_meet_create_meeting → Schedule video call
3. gmail_smart_compose_and_send → Send invite

## **USER INTERACTION TOOLS**

### **request_user_confirmation() - Ask Before Acting**
Use when:
- High-cost actions (>1000 tokens, >$0.01)
- Destructive operations (delete, archive)
- Ambiguous requests (multiple interpretations)

### **request_user_choice() - Multiple Options**
Use when:
- Multiple valid approaches
- User needs to pick specific item
- Configuration preferences

## **ERROR HANDLING**

### **Tool Execution Errors:**
- Credential missing? → Guide user to connect platform
- Invalid parameter? → Check schema, adjust, retry
- Rate limit? → Wait or use alternative tool
- API error? → Explain, suggest manual action

### **Server Tool Errors:**
- No web_search results? → Try different keywords
- web_fetch failed? → URL may be invalid or blocked
- Rate limit? → Already used max searches/fetches

## **CRITICAL RULES**

1. **ALWAYS use thinking blocks** - Reason before acting
2. **NEVER execute tools blindly** - Validate parameters first
3. **ALWAYS cite sources** - Include URLs from web_search
4. **NEVER guess credentials** - Use credential injection
5. **ALWAYS confirm destructive actions** - Use request_user_confirmation
6. **NEVER overwhelm with tools** - Use progressive discovery
```

### System Prompt Injection

**File:** `AI_infrastructure/routes/agent_routes_v4.py` (Lines 660-829)

```python
@agent_bp.route('/stream/<agent_id>', methods=['GET'])
def stream_agent(agent_id):
    """SSE stream with system prompt customization"""
    
    # Get user preferences (nickname, auth platform, style)
    user_prefs = get_user_preferences(user_id) if user_id else None
    nickname = user_prefs.get('nickname', '') if user_prefs else ''
    communication_style = user_prefs.get('communication_style', 'professional')
    detail_level = user_prefs.get('detail_level', 'standard')
    
    # Build personalized system prompt
    system_prompt = f"""You are a highly capable AI assistant with access to 584+ tools.

**User Preferences:**
- Nickname: {nickname if nickname else "None set"}
- Communication Style: {communication_style}
- Detail Level: {detail_level}

**Available Tools:**
- Server Tools: web_search (5/conversation), web_fetch (10/conversation)
- Meta Tools: 8 discovery/navigation tools
- Client Tools: 584 tools via Registry V3

**Current Context:**
- Location: Brisbane, Queensland, Australia
- Timezone: Australia/Brisbane
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S AEST')}

**3-STEP WORKFLOW:**

STEP 1: DISCOVER
- list_available_platforms() → See platforms
- search_tools("keyword") → Find tools fast
- list_platform_tools("platform") → See all tool names

STEP 2: LEARN (ONE tool at a time)
- get_tool_schema("tool_name") → Get parameters

STEP 3: EXECUTE
- execute_tool("tool_name", param1="...", param2="...") → Run tool

**Interleaved Thinking:**
Use thinking blocks between actions to analyze results and plan next steps.
Think before executing tools to validate approach.
Think after tool results to assess success and adjust strategy.

**Example:**
[Thinking: User wants latest AI news. Should search first.]
[Tool: web_search("latest AI news")]
[Thinking: Found 5 articles. Fetch most relevant.]
[Tool: web_fetch("https://...")]
[Thinking: Article confirms findings. Compose summary.]
[Text: Based on recent sources...]

Use tools in multiple rounds with interleaved thinking to complete complex tasks."""
    
    # ... rest of streaming logic
```

---

## 🏥 Integration with Health_app

### Recommended Integration Patterns

#### Pattern 1: Medication Reminder with Calendar Integration

```python
# app/services/medication_reminder_service.py

class MedicationReminderService:
    """
    Medication reminder service using AI_Agents calendar integration patterns
    """
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.registry = get_registry()  # Import from tools/registry_v3
    
    def create_medication_reminder(
        self,
        medication_name: str,
        dosage: str,
        time: str,
        frequency: str,
        platform: str = 'google'  # or 'microsoft'
    ):
        """
        Create recurring calendar event for medication reminder
        
        Uses interleaved thinking pattern:
        1. Validate medication details
        2. Build calendar event parameters
        3. Execute calendar tool with credential injection
        4. Log success to health tracking database
        """
        
        # STEP 1: Think about the task
        print(f"[Thinking] Creating {frequency} reminder for {medication_name}")
        
        # STEP 2: Build calendar event
        if platform == 'google':
            tool_name = 'google_calendar_create_event'
            event_params = {
                'summary': f'💊 {medication_name} - {dosage}',
                'description': f'Take {dosage} of {medication_name}',
                'start_time': time,
                'end_time': self._add_15_minutes(time),
                'recurrence': self._build_recurrence(frequency),
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 15},
                        {'method': 'popup', 'minutes': 0}
                    ]
                }
            }
        
        elif platform == 'microsoft':
            tool_name = 'microsoft_calendar_create_event'
            event_params = {
                'subject': f'💊 {medication_name} - {dosage}',
                'body': f'Take {dosage} of {medication_name}',
                'start': time,
                'end': self._add_15_minutes(time),
                'recurrence': self._build_recurrence_ms(frequency),
                'isReminderOn': True,
                'reminderMinutesBeforeStart': 15
            }
        
        # STEP 3: Execute tool with credential injection
        print(f"[Tool Use] {tool_name}")
        result = self.registry.execute_tool(
            tool_name=tool_name,
            _user_id=self.user_id,
            _injected_credentials=True,
            **event_params
        )
        
        # STEP 4: Log result
        if result.get('success'):
            event_id = result.get('event_id')
            print(f"[Success] Calendar event created: {event_id}")
            
            # Save to health tracking database
            self._save_medication_log(
                medication_name=medication_name,
                dosage=dosage,
                calendar_event_id=event_id,
                platform=platform
            )
            
            return {
                'success': True,
                'event_id': event_id,
                'message': f'Medication reminder created on {platform.title()} Calendar'
            }
        else:
            error = result.get('error', 'Unknown error')
            print(f"[Error] Calendar creation failed: {error}")
            return {'success': False, 'error': error}
```

#### Pattern 2: Symptom Analysis with Web Search

```python
# app/services/symptom_analysis_service.py

class SymptomAnalysisService:
    """
    Symptom analysis using web search for latest medical information
    """
    
    def analyze_symptom_with_research(
        self,
        symptom: str,
        user_context: Dict[str, Any]
    ):
        """
        Analyze symptom using interleaved thinking + web search
        
        Pattern:
        1. Check local knowledge (database of common symptoms)
        2. If uncommon or needs current data → web_search
        3. Fetch detailed medical sources via web_fetch
        4. Provide analysis with citations
        """
        
        # STEP 1: Check local knowledge
        print(f"[Thinking] User reported: {symptom}")
        local_match = self._check_symptom_database(symptom)
        
        if local_match and local_match.get('confidence') > 0.8:
            # High confidence local match
            return {
                'source': 'local_database',
                'analysis': local_match['description'],
                'recommendations': local_match['recommendations']
            }
        
        # STEP 2: Need current medical information
        print(f"[Thinking] Low confidence. Searching for current medical info...")
        
        # Use web_search (server tool - no credential injection needed)
        search_query = f"{symptom} causes symptoms treatment medical"
        
        # NOTE: In actual implementation, this would be done via Anthropic API
        # with web_search server tool, not via registry.execute_tool
        # This is just for illustration of the pattern
        
        print(f"[Tool Use] web_search(query='{search_query}')")
        # search_results = api_call_with_web_search(search_query)
        
        # STEP 3: Fetch detailed sources
        # top_url = search_results[0]['url']
        # print(f"[Tool Use] web_fetch(url='{top_url}')")
        # detailed_content = api_call_with_web_fetch(top_url)
        
        # STEP 4: Provide analysis with citations
        return {
            'source': 'web_research',
            'analysis': 'Based on current medical sources...',
            'citations': ['https://example.com/medical-source'],
            'recommendations': ['Consult with healthcare provider', '...']
        }
```

#### Pattern 3: Health Report Generation with AI

```python
# app/services/health_report_service.py

class HealthReportService:
    """
    Generate health reports using Google Docs integration
    """
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.registry = get_registry()
    
    def generate_monthly_report(self, year: int, month: int):
        """
        Generate comprehensive health report using interleaved thinking
        
        Workflow:
        1. Gather data (symptoms, medications, mood)
        2. Analyze patterns with thinking blocks
        3. Create Google Doc report
        4. Generate charts/visualizations
        5. Share report with healthcare provider
        """
        
        # STEP 1: Gather data
        print(f"[Thinking] Generating report for {year}-{month:02d}")
        data = self._gather_health_data(year, month)
        
        # STEP 2: Analyze patterns
        print(f"[Thinking] Found {len(data['symptoms'])} symptom logs")
        patterns = self._analyze_patterns(data)
        
        # STEP 3: Create Google Doc
        print(f"[Tool Use] google_docs_create")
        
        report_content = self._build_report_markdown(data, patterns)
        
        result = self.registry.execute_tool(
            tool_name='google_docs_smart_create_from_markdown',
            _user_id=self.user_id,
            _injected_credentials=True,
            title=f'Health Report - {year}-{month:02d}',
            markdown_content=report_content
        )
        
        if result.get('success'):
            document_id = result.get('document_id')
            document_url = result.get('document_url')
            
            # STEP 4: Generate charts (optional)
            # self._add_charts_to_doc(document_id, data)
            
            # STEP 5: Share with healthcare provider
            # self._share_document(document_id, provider_email)
            
            return {
                'success': True,
                'document_id': document_id,
                'document_url': document_url,
                'message': 'Health report generated successfully'
            }
        else:
            return {'success': False, 'error': result.get('error')}
```

### Minimal Integration Setup

```python
# app/__init__.py

from tools.registry_v3 import get_registry

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize tool registry for AI integrations
    registry = get_registry()
    app.config['TOOL_REGISTRY'] = registry
    
    # Initialize Anthropic client for interleaved thinking
    from anthropic import Anthropic
    anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    app.config['ANTHROPIC_CLIENT'] = anthropic_client
    
    return app
```

---

## 📚 Key Files Reference

### Core Files

| File | Purpose | Lines |
|------|---------|-------|
| `inhouse_modules/tool_use_agent.py` | Complete interleaved thinking implementation | 3,000+ |
| `AI_infrastructure/core/combined_agent_worker.py` | Streaming agent with multi-round tool use | 1,100+ |
| `AI_infrastructure/core/unified_ai_client.py` | Unified client with server tools | 1,200+ |
| `tools/registry_v3.py` | Central tool registry (584 tools) | 450+ |
| `tools/implementations/meta_tools.py` | Progressive discovery (8 meta-tools) | 610+ |
| `AI_infrastructure/prompts/tool_usage_system_prompt.md` | Complete system prompt | 1,503 |

### Documentation Files

| File | Purpose | Lines |
|------|---------|-------|
| `docs/archive/THINKING_BLOCK_FIX_COMPLETE.md` | Thinking block storage strategy | 643 |
| `docs/archive/EXTENDED_THINKING_FIX_COMPLETE_ANALYSIS.md` | Extended thinking implementation analysis | 400+ |
| `docs/archive/WEB_SEARCH_SERVER_TOOL_FIX.md` | Server tools implementation guide | 728 |
| `docs/archive/SERVER_TOOLS_COMPLETE_GUIDE.md` | Complete server tools documentation | 200+ |

---

## 🎯 Summary: What Makes This Architecture Unique

### 1. Interleaved Thinking Between Tool Calls

**Unlike standard agentic systems** that think only at the start:
- AI_Agents enables **thinking between every tool call**
- Claude analyzes tool results before next action
- Self-correction based on intermediate results
- More accurate multi-step workflows

### 2. Server Tools Integration

**Seamless integration of server-side tools**:
- `web_search` and `web_fetch` executed by Anthropic
- No local API keys required (Brave, Tavily, etc.)
- Automatic location detection
- Citations support for multi-turn conversations

### 3. Progressive Tool Discovery

**Prevents tool overwhelm** (600+ tools):
- Meta-tools enable discovery on-demand
- AI learns schemas only when needed
- 97.5% token reduction vs. upfront loading
- Scalable to infinite tools

### 4. Multi-Round Streaming

**Recursive continuation pattern**:
- Unlimited rounds of tool use (up to max_rounds)
- Real-time SSE streaming of all events
- Proper conversation history management
- Tool results automatically fed back to Claude

### 5. Credential Injection

**Per-user OAuth without exposing tokens**:
- Database-backed token storage
- Auto-refresh expired credentials
- `_user_id` parameter injected automatically
- Supports Google + Microsoft OAuth

---

## 🚀 Next Steps for Health_app

1. **Copy core files** from AI_Agents:
   - `tools/registry_v3.py` → `app/tools/registry.py`
   - `tools/implementations/meta_tools.py` → `app/tools/meta_tools.py`
   - `AI_infrastructure/auth/credential_injector.py` → `app/auth/credential_injector.py`

2. **Add interleaved thinking** to Health_app AI features:
   - Configure Anthropic client with thinking enabled
   - Add beta header for interleaved thinking
   - Implement thinking block display in UI

3. **Integrate server tools** for symptom research:
   - Add web_search to Anthropic API calls
   - Add web_fetch for detailed medical sources
   - Implement citation display in health reports

4. **Implement medication reminders**:
   - Copy calendar integration code
   - Set up OAuth for Google/Microsoft calendars
   - Create recurring events with credential injection

5. **Build health report generation**:
   - Use Google Docs tools for report creation
   - Implement markdown → Google Doc conversion
   - Add chart generation with Google Sheets

---

**Document Version:** 1.0  
**Last Updated:** November 15, 2025  
**Author:** GitHub Copilot (Analysis of AI_Agents v5)
