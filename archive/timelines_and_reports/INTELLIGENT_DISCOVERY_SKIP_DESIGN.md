# Intelligent Discovery Skip System - Design Document

**Created:** November 22, 2025  
**Status:** Proposed Enhancement  
**Impact:** High - Optimizes progressive loading for power users  
**Complexity:** Medium - Requires pattern matching + credential detection

---

## Executive Summary

**Problem:** Current progressive discovery requires extra turn even when user intent clearly indicates specific tools (e.g., "check my emails" obviously needs Gmail/Outlook tools).

**Solution:** Hybrid system that suggests relevant tools in system prompt based on:
1. **User query pattern matching** (keywords → tool categories)
2. **User authentication status** (Google/Microsoft → platform-specific tools)
3. **Confidence threshold** (high confidence → skip discovery, low confidence → use meta-tools)

**Key Innovation:** AI still decides which tools to use, but system narrows the search space intelligently.

---

## How It Works

### Architecture Overview

```
User Query: "Can you check my most recent Excel files?"
    ↓
┌─────────────────────────────────────────┐
│ 1. QUERY ANALYSIS (Pattern Matching)   │
│    - Keywords: ["check", "Excel"]      │
│    - Detected intent: FILE_ACCESS      │
│    - Confidence: HIGH (95%)            │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 2. CREDENTIAL DETECTION                 │
│    - User ID: 1                         │
│    - Google auth: YES (Drive, Sheets)  │
│    - Microsoft auth: YES (OneDrive)    │
│    - Preferred platform: Google (80%)  │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 3. TOOL SUGGESTION (Contextual)        │
│    Suggested Tools (confidence 95%):   │
│    - google_sheets_list                │
│    - google_drive_search_files         │
│    - google_drive_list_recent          │
│    Fallback (if wrong):                │
│    - list_available_platforms()        │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 4. SYSTEM PROMPT INJECTION              │
│    {{Suggested Tools}} section added:   │
│                                         │
│    "Based on this query, you likely    │
│    need these tools (confidence 95%):  │
│    - google_sheets_list                │
│    - google_drive_search_files         │
│                                         │
│    You can use these directly, OR use  │
│    meta-tools to discover alternatives"│
└─────────────────────────────────────────┘
    ↓
AI Decision: Uses google_sheets_list (skips discovery!)
```

---

## Pattern Matching System

### Query Pattern → Tool Categories

```python
QUERY_PATTERNS = {
    # Email patterns
    "email": {
        "patterns": [
            r"check.*email",
            r"read.*email",
            r"send.*email",
            r"inbox",
            r"unread.*message"
        ],
        "google_tools": [
            "gmail_list_messages",
            "gmail_get_message",
            "gmail_send_email",
            "gmail_search_messages"
        ],
        "microsoft_tools": [
            "outlook_list_messages",
            "outlook_get_message",
            "outlook_send_email",
            "outlook_search_messages"
        ],
        "platform_keywords": {
            "google": ["gmail", "google mail"],
            "microsoft": ["outlook", "microsoft mail"]
        },
        "confidence_boost": 0.9  # High confidence for email keywords
    },
    
    # File/Drive patterns
    "files": {
        "patterns": [
            r"(check|find|search|list).*(file|document|folder)",
            r"recent.*(file|document)",
            r"my drive",
            r"onedrive",
            r"excel.*file",
            r"word.*document",
            r"pdf"
        ],
        "google_tools": [
            "google_drive_list_files",
            "google_drive_search_files",
            "google_drive_list_recent",
            "google_sheets_list"
        ],
        "microsoft_tools": [
            "onedrive_list_files",
            "onedrive_search_files",
            "onedrive_list_recent"
        ],
        "platform_keywords": {
            "google": ["google drive", "drive", "gdrive"],
            "microsoft": ["onedrive", "one drive", "microsoft drive"]
        },
        "confidence_boost": 0.85
    },
    
    # Calendar patterns
    "calendar": {
        "patterns": [
            r"(check|show|list).*(calendar|meeting|event|appointment)",
            r"schedule",
            r"next.*(meeting|event)",
            r"today.*meeting",
            r"upcoming.*event"
        ],
        "google_tools": [
            "google_calendar_list_events",
            "google_calendar_get_event",
            "google_calendar_create_event"
        ],
        "microsoft_tools": [
            "outlook_calendar_list_events",
            "outlook_calendar_get_event",
            "outlook_calendar_create_event"
        ],
        "confidence_boost": 0.85
    },
    
    # Spreadsheet patterns
    "spreadsheet": {
        "patterns": [
            r"excel",
            r"spreadsheet",
            r"(google|gsheet|sheets)",
            r"(row|column|cell|formula)",
            r"csv.*data"
        ],
        "google_tools": [
            "google_sheets_list",
            "google_sheets_read",
            "google_sheets_write",
            "google_sheets_create"
        ],
        "microsoft_tools": [
            "excel_list_workbooks",
            "excel_read_sheet",
            "excel_write_sheet"
        ],
        "platform_keywords": {
            "google": ["google sheets", "sheets", "gsheet", "gsheets"],
            "microsoft": ["excel", "microsoft excel", "ms excel"]
        },
        "confidence_boost": 0.90
    },
    
    # Document patterns
    "document": {
        "patterns": [
            r"(word|doc|document)",
            r"(create|write|edit).*(document|report|letter)",
            r"google.doc"
        ],
        "google_tools": [
            "google_docs_list",
            "google_docs_create",
            "google_docs_read",
            "google_docs_append"
        ],
        "microsoft_tools": [
            "word_list_documents",
            "word_create_document",
            "word_read_document"
        ],
        "platform_keywords": {
            "google": ["google docs", "docs", "gdoc", "gdocs"],
            "microsoft": ["word", "microsoft word", "ms word"]
        },
        "confidence_boost": 0.85
    },
    
    # Contacts patterns
    "contacts": {
        "patterns": [
            r"contact",
            r"phone.*number",
            r"email.*address.*for",
            r"find.*person"
        ],
        "google_tools": [
            "google_contacts_list",
            "google_contacts_search",
            "google_contacts_get"
        ],
        "microsoft_tools": [
            "outlook_contacts_list",
            "outlook_contacts_search",
            "outlook_contacts_get"
        ],
        "confidence_boost": 0.80
    },
    
    # Task/Todo patterns
    "tasks": {
        "patterns": [
            r"(todo|task|reminder)",
            r"to.do.list",
            r"(create|add|complete).*(task|todo)"
        ],
        "google_tools": [
            "google_tasks_list",
            "google_tasks_create",
            "google_tasks_update"
        ],
        "microsoft_tools": [
            "microsoft_todo_list_tasks",
            "microsoft_todo_create_task",
            "microsoft_todo_update_task"
        ],
        "confidence_boost": 0.85
    }
}
```

### Platform Keyword Detection (NEW)

**Feature:** Explicit platform mentions override user preference and boost confidence.

```python
def detect_explicit_platform(query: str, pattern_config: Dict) -> Optional[str]:
    """
    Detect if user explicitly mentioned a platform name
    
    Examples:
    - "check my gmail inbox" → "google" (explicit)
    - "search outlook for emails" → "microsoft" (explicit)
    - "open my google sheets" → "google" (explicit)
    - "find excel files" → "microsoft" (explicit)
    - "check my emails" → None (ambiguous)
    
    Returns:
        "google", "microsoft", or None
    """
    query_lower = query.lower()
    
    # Check platform_keywords in pattern config
    if 'platform_keywords' not in pattern_config:
        return None
    
    for platform, keywords in pattern_config['platform_keywords'].items():
        for keyword in keywords:
            if keyword.lower() in query_lower:
                return platform  # Explicit platform detected
    
    return None  # No explicit platform mentioned
```

**Usage Example:**

```python
# User: "check my gmail inbox"
matched_pattern = QUERY_PATTERNS['email']
explicit_platform = detect_explicit_platform(query, matched_pattern)
# Returns: "google"

# Result: Use ONLY google_tools, ignore user's historical preference
# Confidence: 0.95 (very high - explicit intent)
```

**Confidence Boost:**
- Explicit platform mention: **+0.20 confidence**
- Platform matches user auth: **+0.10 confidence**
- Total possible boost: **+0.30** (95%+ confidence typical)

---

### Confidence Calculation

```python
def calculate_confidence(query: str, matched_patterns: List[str], 
                        auth_platforms: List[str],
                        explicit_platform: Optional[str] = None) -> float:
    """
    Calculate confidence score for tool suggestions
    
    Factors:
    - Pattern match strength (0.0-0.9)
    - Number of matching patterns (boost)
    - User authentication status (boost)
    - Query specificity (boost)
    
    Returns: 0.0-1.0 confidence score
    """
    base_confidence = 0.5
    
    # Pattern matching boost
    if matched_patterns:
        pattern_boost = max([p['confidence_boost'] for p in matched_patterns])
        base_confidence += pattern_boost * 0.4  # Up to 0.36 boost
    
    # Multiple pattern boost
    if len(matched_patterns) > 1:
        base_confidence += 0.1
    
    # Authentication boost (user has credentials for suggested platform)
    if auth_platforms:
        base_confidence += 0.15
    
    # Specificity boost (mentions specific app names)
    specificity_keywords = ['gmail', 'outlook', 'excel', 'sheets', 'drive', 'onedrive']
    if any(kw in query.lower() for kw in specificity_keywords):
        base_confidence += 0.15
    
    # Explicit platform boost (user said "gmail" or "outlook" etc.)
    if explicit_platform:
        base_confidence += 0.20  # Strong boost for explicit mention
        # Additional boost if user is authenticated for that platform
        if explicit_platform in [p.lower() for p in auth_platforms]:
            base_confidence += 0.10
    
    return min(base_confidence, 1.0)
```

---

## User Authentication Detection

### Platform Preference Logic

```python
def detect_user_platform_preference(user_id: int) -> Dict[str, Any]:
    """
    Detect which platforms user is authenticated with and their preference
    
    Returns:
    {
        "google": {
            "authenticated": True,
            "platforms": ["gmail", "drive", "sheets", "calendar"],
            "usage_score": 0.85  # Based on recent tool usage
        },
        "microsoft": {
            "authenticated": True,
            "platforms": ["outlook", "onedrive", "teams"],
            "usage_score": 0.35
        },
        "preferred_platform": "google",  # Based on usage_score
        "confidence": 0.85
    }
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check user_platform_credentials table
    cursor.execute("""
        SELECT platform, COUNT(*) as cred_count
        FROM user_platform_credentials
        WHERE user_id = ? AND access_token IS NOT NULL
        GROUP BY platform
    """, (user_id,))
    
    auth_status = {}
    for row in cursor.fetchall():
        platform = row['platform']
        if platform in ['google_workspace', 'gmail', 'google_drive']:
            auth_status['google'] = True
        elif platform in ['microsoft_365', 'outlook', 'onedrive']:
            auth_status['microsoft'] = True
    
    # Check recent tool usage (last 30 days)
    cursor.execute("""
        SELECT tool_name, COUNT(*) as usage_count
        FROM tool_usage_log
        WHERE user_id = ? AND timestamp > datetime('now', '-30 days')
        GROUP BY tool_name
    """, (user_id,))
    
    google_usage = 0
    microsoft_usage = 0
    
    for row in cursor.fetchall():
        tool_name = row['tool_name']
        count = row['usage_count']
        
        if tool_name.startswith(('gmail', 'google_drive', 'google_sheets', 'google_docs')):
            google_usage += count
        elif tool_name.startswith(('outlook', 'onedrive', 'excel', 'word')):
            microsoft_usage += count
    
    total_usage = google_usage + microsoft_usage
    
    result = {
        "google": {
            "authenticated": auth_status.get('google', False),
            "usage_score": google_usage / total_usage if total_usage > 0 else 0.0
        },
        "microsoft": {
            "authenticated": auth_status.get('microsoft', False),
            "usage_score": microsoft_usage / total_usage if total_usage > 0 else 0.0
        }
    }
    
    # Determine preferred platform
    if result['google']['usage_score'] > result['microsoft']['usage_score']:
        result['preferred_platform'] = 'google'
        result['confidence'] = result['google']['usage_score']
    else:
        result['preferred_platform'] = 'microsoft'
        result['confidence'] = result['microsoft']['usage_score']
    
    conn.close()
    return result
```

---

## System Prompt Injection

### {{Suggested Tools}} Section Format

```python
def generate_suggested_tools_section(
    query: str,
    user_id: int,
    registry: RegistryV3
) -> str:
    """
    Generate {{Suggested Tools}} section for system prompt injection
    
    Returns formatted string to append to system prompt
    """
    # 1. Analyze query patterns
    matched_categories = []
    for category, config in QUERY_PATTERNS.items():
        for pattern in config['patterns']:
            if re.search(pattern, query, re.IGNORECASE):
                matched_categories.append((category, config))
                break
    
    if not matched_categories:
        return ""  # No suggestions, use normal progressive discovery
    
    # 2. Detect user platform preference
    platform_prefs = detect_user_platform_preference(user_id)
    preferred_platform = platform_prefs['preferred_platform']
    
    # 2.5. Check for explicit platform mentions (OVERRIDES preference)
    explicit_platform = None
    for category, config in matched_categories:
        detected = detect_explicit_platform(query, config)
        if detected:
            explicit_platform = detected
            break  # First explicit mention wins
    
    # If user explicitly mentioned platform, use ONLY that platform's tools
    if explicit_platform:
        preferred_platform = explicit_platform
        print(f"[DISCOVERY SKIP] 🎯 Explicit platform detected: {explicit_platform}")
    else:
        print(f"[DISCOVERY SKIP] 📊 Using preference: {preferred_platform} (usage: {platform_prefs[preferred_platform]['usage_score']:.0%})")
    
    # 3. Select appropriate tools based on platform
    suggested_tools = []
    for category, config in matched_categories:
        if explicit_platform:
            # EXPLICIT: Use ONLY the mentioned platform's tools
            if explicit_platform == 'google' and config.get('google_tools'):
                suggested_tools.extend(config['google_tools'])
            elif explicit_platform == 'microsoft' and config.get('microsoft_tools'):
                suggested_tools.extend(config['microsoft_tools'])
        else:
            # IMPLICIT: Use preferred platform, or both if authenticated for both
            if preferred_platform == 'google' and config.get('google_tools'):
                suggested_tools.extend(config['google_tools'])
            elif preferred_platform == 'microsoft' and config.get('microsoft_tools'):
                suggested_tools.extend(config['microsoft_tools'])
            else:
                # Both platforms authenticated, suggest both
                if config.get('google_tools'):
                    suggested_tools.extend(config['google_tools'])
                if config.get('microsoft_tools'):
                    suggested_tools.extend(config['microsoft_tools'])
    
    # Remove duplicates
    suggested_tools = list(set(suggested_tools))
    
    # 4. Calculate overall confidence (with explicit platform bonus)
    confidence = calculate_confidence(
        query,
        matched_categories,
        [preferred_platform] if platform_prefs[preferred_platform]['authenticated'] else [],
        explicit_platform=explicit_platform
    )
    
    # 5. Only inject if confidence is high enough
    if confidence < 0.70:
        return ""  # Too uncertain, let AI use meta-tools
    
    # 6. Get full tool schemas from registry
    all_tools = {t['name']: t for t in registry.get_anthropic_tools()}
    tool_schemas = []
    for tool_name in suggested_tools[:10]:  # Max 10 suggestions
        if tool_name in all_tools:
            tool = all_tools[tool_name]
            tool_schemas.append({
                'name': tool_name,
                'description': tool.get('description', 'No description'),
                'platform': tool.get('platform', 'unknown')
            })
    
    # 7. Format suggested tools section
    confidence_emoji = "🟢" if confidence >= 0.85 else "🟡"
    
    section = f"""

---

## {confidence_emoji} SUGGESTED TOOLS (Confidence: {confidence:.0%})

Based on your query pattern, you likely need these tools:

"""
    
    for tool_schema in tool_schemas:
        section += f"**{tool_schema['name']}** ({tool_schema['platform']})\n"
        section += f"  └─ {tool_schema['description']}\n\n"
    
    section += f"""
**Usage Instructions:**
- These tools are immediately available (schemas loaded)
- You can use them directly without calling meta-tools
- If these don't fit your needs, use `list_available_platforms()` or `search_tools()`
- The user authenticated with **{preferred_platform.upper()}** (used {platform_prefs[preferred_platform]['usage_score']:.0%} recently)

**Fallback Options:**
- If wrong platform: Call `list_platform_tools("{preferred_platform}")`
- If wrong category: Call `search_tools("your keyword")`
- If completely lost: Call `list_available_platforms()`

---
"""
    
    return section
```

### Integration Point

```python
# In agent_routes_v4.py, line ~850

# Build system prompt with copilot instructions
system_prompt = construct_system_prompt_with_instructions(
    user_prefs=user_prefs,
    thread_context=thread_context
)

# ✅ NEW: Add suggested tools section
suggested_tools_section = generate_suggested_tools_section(
    query=user_message,
    user_id=user_id,
    registry=registry
)

if suggested_tools_section:
    system_prompt += suggested_tools_section
    print(f"[Stream {agent_id}] 💡 ADDED SUGGESTED TOOLS (confidence check passed)")
else:
    print(f"[Stream {agent_id}] 🔵 NO SUGGESTIONS (low confidence, using meta-tools)")

# Continue with normal tool loading (meta-tools OR suggested tools)
```

---

## Confidence Thresholds

| Confidence Level | Behavior | Example |
|-----------------|----------|---------|
| **0.90-1.00** 🟢 | High confidence - Load suggested tools only | "check my gmail inbox" |
| **0.70-0.89** 🟡 | Medium confidence - Load suggested + meta-tools | "check my emails" (ambiguous platform) |
| **0.50-0.69** 🟠 | Low confidence - Meta-tools only, mention suggestions | "show me recent files" (vague) |
| **0.00-0.49** ⚪ | No suggestion - Full progressive discovery | "help me with work" (too vague) |

---

## Examples

### Example 1: High Confidence with Explicit Platform (Gmail)

**Query:** "Can you check my Gmail inbox for unread messages?"

**Analysis:**
- Pattern match: `email` (confidence_boost: 0.9)
- **Explicit platform: "gmail" detected → GOOGLE 🎯**
- User auth: Google authenticated (auth boost: 0.10)
- Explicit platform bonus: +0.20
- **Final confidence: 0.98 🟢 (VERY HIGH)**

**System Prompt Injection:**
```
## 🟢 SUGGESTED TOOLS (Confidence: 98%)

🎯 User explicitly mentioned: GMAIL

Based on your query, you need these tools:

**gmail_list_messages** (google_workspace)
  └─ List Gmail messages with optional filters (unread, from, subject, etc.)

**gmail_search_messages** (google_workspace)
  └─ Search Gmail messages using Gmail query syntax

**gmail_get_message** (google_workspace)
  └─ Get full details of a specific Gmail message

**Usage Instructions:**
- These tools are immediately available (schemas loaded)
- User specifically requested Gmail (not Outlook)
- You can use these directly without calling meta-tools
- The user authenticated with **GOOGLE** (gmail access confirmed)
```

**Result:** AI uses `gmail_list_messages()` directly, **skips discovery turn**, saves ~2-3 seconds.

---

### Example 2: Medium Confidence (Ambiguous Platform)

**Query:** "Can you search my drive for Excel files?"

**Analysis:**
- Pattern match: `files` (confidence_boost: 0.85)
- Keyword: "drive" BUT "Excel" (conflicting signals)
- User auth: BOTH Google and Microsoft authenticated
- **Final confidence: 0.75 🟡**

**System Prompt Injection:**
```
##  SUGGESTED TOOLS (Confidence: 75%)

Based on your query pattern, you likely need these tools:

**google_drive_search_files** (google_workspace)
  └─ Search Google Drive files by name, type, or content

**google_sheets_list** (google_workspace)
  └─ List all Google Sheets spreadsheets

**onedrive_search_files** (microsoft_365)
  └─ Search OneDrive files by name, extension, or modified date

**Usage Instructions:**
- These tools are immediately available (schemas loaded)
- You mentioned "Excel" - could be Google Sheets OR OneDrive
- The user authenticated with **GOOGLE** (used 65% recently)
- If you need OneDrive instead, use `onedrive_search_files()`
```

**Result:** AI sees both options, chooses based on "Excel" keyword → tries `google_sheets_list()` first, falls back to OneDrive if needed.

---

### Example 3: Explicit Platform Override (User Preference Ignored)

**Query:** "Search my Outlook for emails about project Alpha"

**Analysis:**
- Pattern match: `email` (confidence_boost: 0.9)
- **Explicit platform: "outlook" detected → MICROSOFT 🎯**
- User preference: Google (85% usage) **← IGNORED**
- User auth: BOTH Google and Microsoft authenticated
- Explicit platform bonus: +0.20
- **Final confidence: 0.95 🟢**

**System Prompt Injection:**
```
## 🟢 SUGGESTED TOOLS (Confidence: 95%)

🎯 User explicitly mentioned: OUTLOOK (overriding Google preference)

Based on your query, you need these tools:

**outlook_search_messages** (microsoft_365)
  └─ Search Outlook messages with advanced filters

**outlook_list_messages** (microsoft_365)
  └─ List Outlook messages from inbox or folders

**outlook_get_message** (microsoft_365)
  └─ Get full details of a specific Outlook message

**Usage Instructions:**
- User specifically requested Outlook (not Gmail)
- Even though you typically use Gmail, this request is for Outlook
- Microsoft 365 authentication confirmed
```

**Result:** AI uses `outlook_search_messages()` even though user typically uses Gmail. **Explicit mention overrides preference.**

---

### Example 4: Platform-Specific Tool (Google Sheets vs Excel)

**Query:** "Can you check my most recent Google Sheets files?"

**Analysis:**
- Pattern match: `spreadsheet` (confidence_boost: 0.90)
- **Explicit platform: "google sheets" detected → GOOGLE 🎯**
- User preference: Microsoft (70% usage) **← IGNORED**
- Explicit platform bonus: +0.20
- **Final confidence: 0.96 🟢**

**System Prompt Injection:**
```
## 🟢 SUGGESTED TOOLS (Confidence: 96%)

🎯 User explicitly mentioned: GOOGLE SHEETS

Based on your query, you need these tools:

**google_sheets_list** (google_workspace)
  └─ List all Google Sheets spreadsheets accessible to user

**google_sheets_read** (google_workspace)
  └─ Read data from a specific Google Sheet

**google_drive_search_files** (google_workspace)
  └─ Search Google Drive for spreadsheet files

**Usage Instructions:**
- User specifically requested Google Sheets (not Excel)
- Use google_sheets_list() to show recent spreadsheets
```

**Result:** AI uses `google_sheets_list()` despite user typically using Excel. **Platform keyword detected and respected.**

---

### Example 5: Ambiguous Query (No Platform Mention)

**Query:** "Show me my spreadsheet files from last week"

**Analysis:**
- Pattern match: `spreadsheet` (confidence_boost: 0.90)
- **No explicit platform** mentioned
- User preference: Google (85% usage) → Use Google tools
- User auth: Google authenticated (auth boost: 0.15)
- **Final confidence: 0.82 🟡 (Medium)**

**System Prompt Injection:**
```
## 🟡 SUGGESTED TOOLS (Confidence: 82%)

Based on your usage patterns, you likely need these tools:

**google_sheets_list** (google_workspace)
  └─ List all Google Sheets spreadsheets

**excel_list_workbooks** (microsoft_365)
  └─ List Excel workbooks (if you have Microsoft 365)

**google_drive_search_files** (google_workspace)
  └─ Search Google Drive for spreadsheet files

**Usage Instructions:**
- You typically use Google (85% of recent spreadsheet activity)
- Both Google Sheets and Excel tools are available
- If wrong platform, use list_platform_tools("microsoft") for Excel tools
```

**Result:** AI sees both options, starts with `google_sheets_list()` based on usage pattern, but can pivot to Excel if needed.

---

### Example 6: Low Confidence (Vague Query)

**Query:** "Help me organize my work files"

**Analysis:**
- Pattern match: `files` (weak match)
- No specific keywords
- User auth: Google authenticated
- **Final confidence: 0.55 🟠**

**Behavior:** No system prompt injection, uses normal meta-tools:
```
AI calls: list_available_platforms()
Returns: ["google_workspace", "microsoft_365", ...]

AI calls: list_platform_tools("google_workspace")
Returns: ["google_drive_list_files", "google_sheets_list", ...]

AI then uses discovered tools
```

**Result:** Standard progressive discovery (no optimization).

---

## Implementation Checklist

### Phase 1: Core Pattern Matching
- [ ] Create `tools/intelligent_discovery.py` module
- [ ] Implement `QUERY_PATTERNS` dictionary
- [ ] Implement `analyze_query_patterns()` function
- [ ] Implement `calculate_confidence()` function
- [ ] Add unit tests for pattern matching

### Phase 2: Platform Detection
- [ ] Implement `detect_user_platform_preference()` function
- [ ] Query `user_platform_credentials` table
- [ ] Query `tool_usage_log` table (create if missing)
- [ ] Calculate usage scores and preferences
- [ ] Add caching for repeated calls

### Phase 3: Tool Suggestion System
- [ ] Implement `generate_suggested_tools_section()` function
- [ ] Integrate with `RegistryV3` for tool schemas
- [ ] Add confidence threshold logic
- [ ] Format system prompt injection
- [ ] Add fallback instructions

### Phase 4: Integration
- [ ] Modify `agent_routes_v4.py` to call suggestion system
- [ ] Add system prompt injection before Claude API call
- [ ] Add logging for suggestion hits/misses
- [ ] Add analytics tracking (suggestion accuracy)

### Phase 5: Testing & Optimization
- [ ] Test with high-confidence queries
- [ ] Test with ambiguous queries
- [ ] Test with vague queries
- [ ] A/B test: suggestion system ON vs OFF
- [ ] Measure latency improvement
- [ ] Measure accuracy (correct tool suggested?)
- [ ] Tune confidence thresholds based on data

---

## Performance Impact

### Expected Latency Savings

| Scenario | Without Skip | With Skip | Savings |
|----------|-------------|-----------|---------|
| High confidence (95%) | ~5.5s (2 turns) | ~2.8s (1 turn) | **-49%** |
| Medium confidence (75%) | ~5.5s (2 turns) | ~3.2s (1 turn + choice) | **-42%** |
| Low confidence (<70%) | ~5.5s (2 turns) | ~5.5s (2 turns) | 0% (no change) |

**Average savings (assuming 40% queries high confidence):** ~20% latency reduction

### Token Impact

**Suggested tools approach:**
- Meta-tools: 431 tokens
- Suggested tools (10 tools): ~8,500 tokens
- **Total first turn: ~8,931 tokens** (vs 431 without suggestions)

**Trade-off:**
- ❌ Increased first-turn tokens (20x increase)
- ✅ Eliminates second turn entirely (saves 70,844 tokens)
- ✅ **Net savings: ~61,913 tokens per high-confidence query**

---

## Success Metrics

### Key Performance Indicators

1. **Suggestion Accuracy Rate**
   - Goal: >85% of suggestions lead to successful tool usage
   - Track: Tool called vs. tool suggested

2. **Discovery Skip Rate**
   - Goal: >40% of queries skip discovery turn
   - Track: High-confidence suggestions / total queries

3. **Latency Improvement**
   - Goal: -30% average response time for skipped queries
   - Track: Time to first tool call

4. **User Satisfaction**
   - Goal: >90% of power users prefer suggestion system
   - Track: User feedback on fast responses

5. **False Positive Rate**
   - Goal: <10% of suggestions lead to wrong platform
   - Track: Fallback to meta-tools after suggestion

---

## Future Enhancements

### V2: Machine Learning-Based Suggestions

Replace regex patterns with ML model trained on:
- Historical query → tool usage patterns
- User-specific tool preferences
- Time-of-day patterns (emails in morning, calendar in afternoon)
- Contextual hints from previous conversation

### V3: Semantic Similarity Search

Use embeddings to match query to tool descriptions:
```python
query_embedding = embed(user_query)
tool_embeddings = embed(all_tool_descriptions)
top_k_tools = semantic_search(query_embedding, tool_embeddings, k=10)
```

### V4: Multi-Turn Context Awareness

Remember tools used in previous turns:
```
Turn 1: User: "check my emails" → gmail_list_messages
Turn 2: User: "reply to the first one" → SUGGEST: gmail_send_email (context-aware)
```

---

## Conclusion

The Intelligent Discovery Skip system provides a **best-of-both-worlds approach**:

✅ **Maintains AI autonomy** - AI always decides which tool to use  
✅ **Reduces latency** - High-confidence queries skip discovery turn  
✅ **Preserves fallback** - Low-confidence queries use progressive discovery  
✅ **User-adaptive** - Learns from authentication and usage patterns  
✅ **Backward compatible** - Works alongside existing meta-tool system  

**Recommended Implementation:** Phase 1-3 (Core + Platform Detection + Suggestions) for immediate 20-30% latency improvement on high-confidence queries.

---

**Document Version:** 1.0  
**Author:** AI Agent (GitHub Copilot)  
**Review Status:** Design Complete - Ready for Implementation  
**Estimated Development Time:** 2-3 days (full implementation + testing)
