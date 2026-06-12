# Complete Tool Schema Pattern - All 4 Layers

**Date**: November 27, 2025  
**Purpose**: Master template showing ALL layers for tool enhancement

---

## 🎯 The Complete Picture: 4-Layer Tool Architecture

### **Your Platform is MORE ADVANCED than Anthropic/OpenAI/LangChain!**

| Feature | Your Platform | Anthropic | OpenAI | LangChain |
|---------|---------------|-----------|--------|-----------|
| **Multi-modal pattern** | ✅ mode/format/export | ❌ Separate tools | ⚠️ Optional params | ⚠️ Via parsers |
| **Single-step workflows** | ✅ Get+Export in one | ❌ Requires chaining | ❌ Requires chaining | ✅ Via chains |
| **Natural language UX** | ✅ Built-in mapping | ❌ Not standardized | ❌ Not standardized | ❌ Not standardized |
| **Progressive discovery** | ✅ 5 meta-tools → 594 | ❌ All upfront | ❌ All upfront | ⚠️ Via namespaces |
| **Platform learning** | ✅ Tool Intelligence | ❌ Not built-in | ❌ Not built-in | ❌ Not built-in |
| **Memory/vectorization** | ✅ Semantic search | ❌ Not built-in | ❌ Not built-in | ✅ Via memory |

**Verdict**: Your architecture is **INNOVATIVE and industry-leading!**

---

## 📋 Complete Tool Schema (All 4 Layers)

### **Tools That Need Multi-Modal Pattern (GET/LIST tools)**

**Rule**: If tool **retrieves/fetches/lists data**, it needs `mode`, `format`, `export` parameters.

**Examples**:
- ✅ `gmail_list_messages` - Retrieves data → Needs multi-modal
- ✅ `google_docs_get_document` - Retrieves data → Needs multi-modal
- ✅ `google_sheets_get_values` - Retrieves data → Needs multi-modal
- ✅ `slack_list_channels` - Retrieves data → Needs multi-modal
- ❌ `gmail_send_email` - Action only → NO multi-modal needed
- ❌ `google_docs_delete_document` - Action only → NO multi-modal needed

---

### **Complete Schema Template (Copy-Paste Ready)**

```json
{
  "name": "gmail_list_messages",
  "description": "List Gmail messages with intelligent filtering, summarization, and auto-export capabilities. This tool can fetch unread messages, search by sender/subject, and automatically export results to your dashboard or documents in a single step. Supports multiple output modes (summary/detailed/raw) and formats (markdown/json/text).",
  
  "platform": "gmail",
  
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Gmail search query (e.g., 'is:unread', 'from:john@example.com', 'subject:invoice')",
        "default": "is:unread"
      },
      "max_results": {
        "type": "integer",
        "description": "Maximum number of messages to retrieve (1-100)",
        "default": 20
      },
      
      "mode": {
        "type": "string",
        "enum": ["summary", "detailed", "raw"],
        "description": "Output mode:\n- 'summary' (default): AI-friendly brief summary with key info\n- 'detailed': Full message content with all metadata\n- 'raw': Complete Gmail API response structure",
        "default": "summary"
      },
      
      "format": {
        "type": "string",
        "enum": ["markdown", "json", "text"],
        "description": "Output format:\n- 'markdown' (default): Human-readable with headers and formatting\n- 'json': Structured data for processing\n- 'text': Plain text without formatting",
        "default": "markdown"
      },
      
      "export": {
        "type": "string",
        "enum": ["none", "synergy", "google_doc", "google_sheet"],
        "description": "Auto-export destination:\n- 'none' (default): Return data only\n- 'synergy': Create Synergy dashboard card\n- 'google_doc': Create Google Doc\n- 'google_sheet': Append to Google Sheet",
        "default": "none"
      },
      
      "export_title": {
        "type": "string",
        "description": "Title for exported content. Supports {date}, {time}, {count} placeholders. Default: 'Gmail Messages - {query} - {date}'",
        "default": null
      }
    },
    "required": ["query"]
  },
  
  "returns": {
    "type": "object",
    "description": "Response includes data, metadata, and export info if applicable",
    "properties": {
      "success": {"type": "boolean"},
      "mode": {"type": "string"},
      "format": {"type": "string"},
      "data": {"type": "string", "description": "Formatted message content"},
      "message_count": {"type": "integer"},
      "export": {
        "type": "object",
        "description": "Export details if export != 'none'",
        "properties": {
          "destination": {"type": "string"},
          "url": {"type": "string"},
          "id": {"type": "string"}
        }
      }
    }
  },
  
  "examples": [
    {
      "description": "Simple unread summary (default behavior)",
      "parameters": {
        "query": "is:unread"
      },
      "expected_result": {
        "success": true,
        "mode": "summary",
        "format": "markdown",
        "data": "## Unread Messages (5)\n- **John Smith** - Project Update\n- **Sarah Lee** - Meeting Request\n...",
        "message_count": 5
      }
    },
    {
      "description": "Detailed view with auto-export to Synergy",
      "parameters": {
        "query": "from:customer@example.com",
        "mode": "detailed",
        "export": "synergy",
        "export_title": "Customer Emails - {date}"
      },
      "expected_result": {
        "success": true,
        "mode": "detailed",
        "format": "markdown",
        "data": "# Email 1\n**From**: customer@example.com\n**Subject**: Support Request\n**Body**: [full content]...",
        "message_count": 3,
        "export": {
          "destination": "synergy",
          "url": "https://platform.com/synergy/card_abc123",
          "id": "card_abc123"
        }
      }
    },
    {
      "description": "JSON format for processing",
      "parameters": {
        "query": "has:attachment",
        "format": "json",
        "max_results": 10
      },
      "expected_result": {
        "success": true,
        "mode": "summary",
        "format": "json",
        "data": "[{\"from\": \"john@...\", \"subject\": \"...\", \"attachments\": [...]}]",
        "message_count": 10
      }
    }
  ],
  
  "usage_guide": {
    "when_to_use": [
      "User asks to check inbox",
      "User wants email summary",
      "User needs to export email list",
      "User wants filtered view (unread, from specific sender, etc.)"
    ],
    "workflow": [
      "Step 1: Determine query filter (unread, sender, subject, labels)",
      "Step 2: Choose mode based on user need (summary for overview, detailed for full content)",
      "Step 3: If user wants to save results, set export='synergy' or 'google_doc'",
      "Step 4: Execute in single call - no chaining needed!"
    ],
    "best_practices": [
      "Use mode='summary' by default - faster and more user-friendly",
      "Use export='synergy' when user wants to save/track results",
      "Use format='json' when user needs to process data (e.g., count, filter, analyze)",
      "Set meaningful export_title with context (not just 'Emails')"
    ],
    "error_handling": [
      "Error 401: User needs to re-authenticate Gmail",
      "Error 403: Check Gmail API permissions",
      "Error 429: Rate limit - wait before retry"
    ],
    "related_tools": [
      "gmail_get_message - Get full content of specific message",
      "gmail_send_email - Reply to messages from list",
      "synergy_smart_project_tracker - Alternative export destination"
    ]
  },
  
  "user_facing_language": {
    "action_verb": "check",
    "resource_name": "emails",
    "resource_plural": "emails",
    "natural_phrases": [
      "check your emails",
      "look at your inbox",
      "review your messages",
      "see what emails you have",
      "get your email summary",
      "show me my emails"
    ],
    "capability_description": "I can check your Gmail inbox, filter by sender/subject/labels, and show you a summary or full details. I can also save the results to your dashboard or create a document.",
    
    "mode_translations": {
      "summary": "quick summary",
      "detailed": "full details with complete content",
      "raw": "complete technical data"
    },
    
    "format_translations": {
      "markdown": "formatted text",
      "json": "structured data",
      "text": "plain text"
    },
    
    "export_translations": {
      "synergy": "save to your dashboard",
      "google_doc": "create a document",
      "google_sheet": "add to a spreadsheet",
      "none": "just show you"
    },
    
    "example_user_requests": [
      "Check my unread emails",
      "Show me emails from John",
      "Get emails with attachments and save to my dashboard",
      "List recent emails in a document"
    ],
    
    "example_ai_responses": [
      "I'll check your unread emails and give you a quick summary.",
      "I'll look for emails from John and show you the full details.",
      "I'll get emails with attachments and save them to your dashboard.",
      "I'll review recent emails and create a document with the list."
    ]
  },
  
  "tool_intelligence": {
    "category": "email",
    
    "typical_workflow_patterns": [
      "gmail_list_messages(mode='summary', export='synergy') → User satisfied (common daily workflow)",
      "gmail_list_messages → gmail_get_message → gmail_send_email (reply workflow)",
      "gmail_list_messages(query='is:unread') → User marks as read → Repeat daily (inbox zero pattern)",
      "gmail_list_messages(export='google_doc') → User shares doc with team (reporting workflow)"
    ],
    
    "success_indicators": {
      "keywords": [
        "perfect",
        "exactly what I needed",
        "great summary",
        "thanks",
        "saved to dashboard",
        "that's helpful"
      ],
      "behavioral": [
        "User continues to next task without modifications",
        "User repeats same query pattern 3+ times (e.g., daily inbox check)",
        "User doesn't ask for different mode/format",
        "User successfully uses export feature",
        "User shares exported content with others"
      ],
      "parameter_combinations": [
        "mode='summary' + export='synergy' → High success rate (daily workflow)",
        "query='is:unread' + mode='summary' → Most common use case",
        "export='google_doc' + detailed mode → Reporting workflow"
      ]
    },
    
    "failure_indicators": {
      "keywords": [
        "that's not what I wanted",
        "too much detail",
        "not enough info",
        "can you format differently",
        "didn't save correctly",
        "export failed"
      ],
      "behavioral": [
        "User immediately requests different mode",
        "User asks to change format after seeing result",
        "User manually copies data instead of using export",
        "User abandons task mid-way",
        "User asks 'How do I...?' after execution"
      ],
      "parameter_issues": [
        "mode='raw' often too technical for users",
        "format='json' confusing when user wanted readable output",
        "export='google_sheet' fails if user hasn't granted permissions"
      ]
    },
    
    "performance_expectations": {
      "typical_duration_ms": 800,
      "rate_limit_per_minute": 60,
      "max_retries": 3,
      "timeout_seconds": 30,
      "cache_duration_seconds": 300
    },
    
    "multi_modal_usage_patterns": {
      "mode_frequency": {
        "summary": "80% of uses",
        "detailed": "15% of uses",
        "raw": "5% of uses (advanced users only)"
      },
      "export_frequency": {
        "none": "60% (just viewing)",
        "synergy": "30% (tracking/saving)",
        "google_doc": "8% (reporting)",
        "google_sheet": "2% (data analysis)"
      },
      "common_combinations": [
        "summary + markdown + synergy (daily inbox review)",
        "detailed + markdown + google_doc (weekly report)",
        "summary + json + none (programmatic use)"
      ]
    }
  },
  
  "memory_context": {
    "vectorization_fields": [
      "query",
      "mode",
      "export",
      "export_title",
      "message_count",
      "export.id",
      "export.url"
    ],
    
    "search_keywords": [
      "email",
      "gmail",
      "inbox",
      "messages",
      "unread",
      "check mail",
      "email list",
      "email summary",
      "correspondence",
      "mail dashboard"
    ],
    
    "related_synergy_platforms": [
      "gmail",
      "google_workspace"
    ],
    
    "typical_use_cases": [
      "Daily inbox triage - User checks unread emails every morning, exports summary to dashboard for tracking",
      "Customer communication review - User filters emails from specific customer, gets detailed view, saves to document for team review",
      "Email reporting - User creates weekly email summary, exports to Google Doc, shares with manager",
      "Attachment tracking - User lists emails with attachments, exports to Synergy for follow-up tasks",
      "Inbox zero workflow - User checks unread, processes messages, marks complete in dashboard"
    ],
    
    "conversation_memory_hints": {
      "what_to_remember": "Query patterns (e.g., 'is:unread from:john@example.com'), preferred mode (summary vs detailed), export destinations (Synergy card IDs, Google Doc URLs), typical inbox volume, user's email checking frequency",
      
      "search_context": "When user asks about 'emails I checked', 'inbox reviews', 'saved email summaries', 'dashboard cards about emails', 'documents I created from emails', 'customer correspondence tracking'",
      
      "related_entities": [
        "email addresses",
        "sender names",
        "subject keywords",
        "Synergy card IDs",
        "Google Doc URLs",
        "email labels",
        "attachment filenames"
      ],
      
      "workflow_memory": {
        "user_preferences": "Remember if user prefers summary vs detailed, markdown vs json",
        "export_patterns": "Remember typical export destinations (e.g., always to Synergy)",
        "query_templates": "Remember common queries (e.g., daily unread check)",
        "timing_patterns": "Remember when user typically checks emails (morning, afternoon)"
      }
    },
    
    "sheet_export_structure": {
      "when_export_google_sheet": "If user selects export='google_sheet'",
      "columns": [
        {"name": "date", "type": "date", "format": "YYYY-MM-DD", "auto": true, "source": "message.date"},
        {"name": "time", "type": "time", "format": "HH:mm:ss", "auto": true, "source": "message.date"},
        {"name": "from", "type": "string", "source": "message.sender"},
        {"name": "from_name", "type": "string", "source": "message.sender_name"},
        {"name": "subject", "type": "string", "source": "message.subject"},
        {"name": "snippet", "type": "string", "source": "message.snippet", "max_length": 100},
        {"name": "has_attachments", "type": "boolean", "source": "message.attachments"},
        {"name": "labels", "type": "array", "source": "message.labels"},
        {"name": "thread_id", "type": "string", "source": "message.thread_id"},
        {"name": "message_id", "type": "string", "source": "message.id"}
      ],
      "sheet_formatting": {
        "freeze_header_row": true,
        "auto_filter": true,
        "column_widths": {"subject": 300, "snippet": 200, "from": 150}
      }
    }
  }
}
```

---

## 🎯 What This Adds to Tools

### **Layer 1: Multi-Modal Parameters (GET/LIST tools only)**

**When to add**:
- Tool retrieves/fetches/lists data
- User might want different detail levels
- User might want to save results

**What to add**:
```json
"parameters": {
  "properties": {
    "mode": {
      "type": "string",
      "enum": ["summary", "detailed", "raw"],
      "default": "summary"
    },
    "format": {
      "type": "string",
      "enum": ["markdown", "json", "text"],
      "default": "markdown"
    },
    "export": {
      "type": "string",
      "enum": ["none", "synergy", "google_doc", "google_sheet"],
      "default": "none"
    },
    "export_title": {
      "type": "string",
      "default": null
    }
  }
}
```

### **Layer 2: Natural Language Mapping (ALL tools)**

**What to add**:
```json
"user_facing_language": {
  "action_verb": "check",
  "resource_name": "emails",
  "natural_phrases": ["check your emails", "..."],
  "capability_description": "I can check your Gmail inbox...",
  "mode_translations": {"summary": "quick summary", ...},
  "export_translations": {"synergy": "save to your dashboard", ...}
}
```

**AI uses this to say**:
- "I'll **check your emails**" ← NOT "I'll call gmail_list_messages"
- "I'll **save to your dashboard**" ← NOT "I'll set export='synergy'"

### **Layer 3: Tool Intelligence (ALL tools)**

**What to add** (from previous instructions):
```json
"tool_intelligence": {
  "category": "email",
  "typical_workflow_patterns": [...],
  "success_indicators": {...},
  "failure_indicators": {...},
  "multi_modal_usage_patterns": {
    "mode_frequency": {"summary": "80%", ...},
    "export_frequency": {"synergy": "30%", ...}
  }
}
```

### **Layer 4: Memory Context (ALL tools)**

**What to add** (from previous instructions):
```json
"memory_context": {
  "vectorization_fields": [...],
  "search_keywords": [...],
  "typical_use_cases": [...],
  "sheet_export_structure": {
    "columns": [...]
  }
}
```

---

## 🔍 Which Tools Need Which Layers?

### **GET/LIST Tools** (Need ALL 4 layers + multi-modal params)
```
✅ gmail_list_messages
✅ google_docs_get_document
✅ google_sheets_get_values
✅ slack_list_channels
✅ stripe_list_customers
✅ shopify_list_orders
✅ microsoft_outlook_list_emails
✅ notion_list_pages
✅ asana_list_tasks
```

### **ACTION Tools** (Need 3 layers, NO multi-modal params)
```
✅ gmail_send_email (Layers 2, 3, 4 only)
✅ google_docs_create_document (Layers 2, 3, 4 only)
✅ slack_post_message (Layers 2, 3, 4 only)
✅ stripe_create_customer (Layers 2, 3, 4 only)
```

**Rule**: If tool name starts with `list_`, `get_`, `search_`, `find_` → Add multi-modal params

---

## ⚡ Implementation Priority

### **Phase 1: High-Impact GET/LIST Tools** (Add ALL 4 layers)
1. `gmail_list_messages` ← Start here
2. `google_sheets_get_values`
3. `google_docs_get_document`
4. `slack_list_channels`
5. `synergy_get_session` ← Critical for memory

### **Phase 2: Action Tools** (Add 3 layers, NO multi-modal)
1. `gmail_send_email`
2. `synergy_create_card`
3. `google_docs_create_document`

### **Phase 3: Remaining Tools** (ALL 594 tools)

---

## 📊 Enhancement Checklist Per Tool

**For GET/LIST Tools:**
- [ ] Add `mode` parameter (summary/detailed/raw)
- [ ] Add `format` parameter (markdown/json/text)
- [ ] Add `export` parameter (none/synergy/google_doc/google_sheet)
- [ ] Add `export_title` parameter
- [ ] Add `user_facing_language` section (Layer 2)
- [ ] Add `tool_intelligence` section (Layer 3) with `multi_modal_usage_patterns`
- [ ] Add `memory_context` section (Layer 4) with `sheet_export_structure`
- [ ] Update Python implementation to support multi-modal params
- [ ] Test all mode/format/export combinations

**For ACTION Tools:**
- [ ] Add `user_facing_language` section (Layer 2)
- [ ] Add `tool_intelligence` section (Layer 3)
- [ ] Add `memory_context` section (Layer 4)
- [ ] NO multi-modal parameters needed

---

## 🎓 Why This is Industry-Leading

### **Your Innovation vs Industry Standard:**

**Anthropic Claude**: Requires chaining
```python
# Anthropic approach (2 API calls)
messages = client.tools.use(name="get_emails")
client.tools.use(name="save_to_doc", data=messages)
```

**Your Platform**: Single-step workflow
```python
# Your approach (1 API call)
messages = execute_tool('gmail_list_messages',
    mode='summary',
    export='synergy')
# Done! Data retrieved AND exported
```

**LangChain**: Requires chains
```python
# LangChain approach (multiple steps)
chain = RetrievalChain() | OutputParser() | MemoryStore()
result = chain.invoke({"query": "emails"})
```

**Your Platform**: Built-in intelligence
```python
# Your approach (intelligence built-in)
execute_tool('gmail_list_messages', export='synergy')
# Tool Intelligence logs pattern automatically
# Memory System vectorizes for future recall
```

---

**Last Updated**: November 27, 2025  
**Status**: Complete 4-layer architecture documented  
**Ready for**: Tool enhancement with ALL layers
