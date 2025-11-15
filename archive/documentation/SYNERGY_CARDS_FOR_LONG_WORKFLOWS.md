# Using Synergy Cards for Long-Running AI Workflows

**Quick Reference Guide**

---

## The Problem

```
Traditional Approach (Fails after 10-15 rounds):
┌────────────────────────────────────────────────┐
│ Conversation History                           │
│                                                │
│ User:  "Analyze 100 emails"                    │
│ AI:    *thinking* "I'll search Gmail..."       │
│ Tool:  gmail_search() → 100 emails (50K tokens)│ ← Stored in conversation
│ AI:    *thinking* "Now I'll categorize..."     │
│ Tool:  categorize() → Results (20K tokens)     │ ← Stored in conversation
│ AI:    *thinking* "Create spreadsheet..."      │
│ Tool:  sheets_create() → Data (30K tokens)     │ ← Stored in conversation
│ ...                                            │
│ Round 10: 💥 ERROR: 231,130 tokens > 200K     │
└────────────────────────────────────────────────┘
```

## The Solution

```
Synergy Card Approach (Unlimited rounds):
┌─────────────────────────┐     ┌────────────────────────────────┐
│  Conversation Thread    │     │  Synergy Session Card          │
│  (Stays small!)         │◄───►│  (Stores everything!)          │
│                         │     │                                │
│ User: "Analyze 100      │     │ session_id: sess_gmail_xyz     │
│        emails"          │     │                                │
│                         │     │ checklist:                     │
│ AI: "Created card.      │     │  ✅ Batch 1-10 (7 pos, 3 neg) │
│      Working on         │     │  ✅ Batch 11-20 (9 pos, 1 neg)│
│      batch 1..."        │     │  ✅ Batch 21-30 (8 pos, 2 neg)│
│                         │     │  ⏳ Batch 31-40 (in progress) │
│ Tool: gmail_search()    │     │  ⬜ Batch 41-50               │
│  → 50K tokens          ├────►│  ... (stored in card)          │
│                         │     │                                │
│ AI: "Batch 1 done.      │     │ documents:                     │
│      7 positive,        │     │  - Analysis Report (doc_123)   │
│      3 negative.        │     │  - Raw Data Sheet (sheet_456)  │
│      Moving to batch 2" │     │                                │
│                         │     │ recent_activity:               │
│ Conversation: 5K tokens │     │  - 50+ tool executions logged  │
│                         │     │  - All results stored          │
│ Can run 100+ rounds! ✅ │     │ Unlimited size! ✅             │
└─────────────────────────┘     └────────────────────────────────┘
```

---

## How It Works

### Step 1: Create Card (Round 1)

```python
# AI uses synergy_create_session tool
{
  "title": "Gmail Analysis - 100 Messages",
  "description": "Analyze customer feedback Q4 2024",
  "platforms_involved": ["gmail", "google_docs", "google_sheets"],
  "thread_ids": ["thread_1762926885059"],
  "checklist": [
    {"text": "Batch 1-10: Categorize", "completed": false},
    {"text": "Batch 11-20: Categorize", "completed": false},
    {"text": "Batch 21-30: Categorize", "completed": false},
    ...
    {"text": "Batch 91-100: Categorize", "completed": false},
    {"text": "Create summary report", "completed": false}
  ]
}
```

**Conversation:** 500 tokens  
**Card:** Stored in database

---

### Step 2: Execute First Batch (Rounds 2-5)

```python
# Round 2: Search Gmail
tool_result = gmail_search_messages(query="customer feedback", max_results=10)
# Result: 15,000 tokens of email data

# AI updates card (NOT conversation!)
synergy_update_session(
  session_id="sess_gmail_xyz",
  session_data={
    "batch_1": {
      "messages": [...],  # All 10 emails
      "positive": 7,
      "negative": 3,
      "neutral": 0
    }
  },
  recent_activity=[
    {"round": 2, "tool": "gmail_search", "found": 10, "tokens": 15000}
  ]
)

# AI response in conversation (small!)
"Batch 1 complete: Analyzed 10 messages. 
 7 positive, 3 negative. 
 Starting batch 2..."
```

**Conversation:** 500 + 150 = 650 tokens  
**Card:** Stores 15,000 tokens of email data  
**Key:** Tool result NOT added to conversation!

---

### Step 3: Continue Batches (Rounds 6-50)

```python
# Round 11: Batch 2
tool_result = gmail_search_messages(offset=10, max_results=10)
# Another 15,000 tokens

# Update card
synergy_update_session(
  session_id="sess_gmail_xyz",
  session_data={
    "batch_1": {...},
    "batch_2": {...}  # Add batch 2 data
  },
  checklist=[
    {"text": "Batch 1-10: Categorize", "completed": true},
    {"text": "Batch 11-20: Categorize", "completed": true},
    ...
  ]
)

# AI response
"Batch 2 complete: 9 positive, 1 negative.
 Total so far: 16 positive, 4 negative.
 Starting batch 3..."
```

**Conversation:** 650 + 150 = 800 tokens  
**Card:** Stores 30,000 tokens (batch 1 + batch 2)  
**Repeat:** 50 times if needed!

---

### Step 4: Create Summary (Rounds 51-55)

```python
# AI reads card to get full data
card = synergy_get_session("sess_gmail_xyz")

# All 100 emails available in card.session_data
# AI generates summary from card data (NOT conversation!)

# Create Google Doc
doc_id = google_docs_create_document(
  title="Customer Feedback Analysis Q4 2024",
  content="Summary of 100 emails analyzed..."
)

# Update card with document link
synergy_update_session(
  session_id="sess_gmail_xyz",
  documents=[
    {"type": "google_doc", "id": doc_id, "title": "Analysis Report"}
  ],
  status="completed",
  kanban_column="done"
)

# Final response
"Analysis complete! Created summary report.
 Total: 67 positive, 28 negative, 5 neutral.
 Document: [link to Google Doc]"
```

**Conversation:** 800 + 200 = 1,000 tokens  
**Card:** Stores 150,000+ tokens (all 100 emails + analysis)  
**Result:** 55 rounds completed successfully! ✅

---

## Comparison

### Without Synergy Cards (Traditional)

| Round | Action | Conv Tokens | Status |
|-------|--------|-------------|--------|
| 1 | User message | 100 | ✅ |
| 2 | Gmail search (10 emails) | 15,100 | ✅ |
| 3 | Analyze batch 1 | 20,200 | ✅ |
| 5 | Gmail search (10 more) | 35,300 | ✅ |
| 8 | Create spreadsheet | 60,500 | ✅ |
| 10 | Continue analysis | 90,800 | ✅ |
| 12 | More data | 125,400 | ✅ |
| 15 | **💥 Token limit exceeded** | **231,130** | ❌ **FAILS** |

**Max rounds:** 10-15  
**Reason:** Tool results accumulate in conversation

### With Synergy Cards (New Approach)

| Round | Action | Conv Tokens | Card Data | Status |
|-------|--------|-------------|-----------|--------|
| 1 | Create card | 500 | 0 | ✅ |
| 2 | Batch 1 (10 emails) | 650 | 15K | ✅ |
| 11 | Batch 2 (10 emails) | 800 | 30K | ✅ |
| 21 | Batch 3 (10 emails) | 950 | 45K | ✅ |
| 31 | Batch 4 (10 emails) | 1,100 | 60K | ✅ |
| 41 | Batch 5 (10 emails) | 1,250 | 75K | ✅ |
| 51 | Create summary | 1,400 | 150K | ✅ |
| 55 | Final review | 1,500 | 150K | ✅ **SUCCESS** |
| 100+ | **Can continue!** | ~2,000 | Unlimited | ✅ |

**Max rounds:** UNLIMITED  
**Reason:** Tool results stored in card (database), not conversation

---

## Multi-Agent Collaboration Example

```
One Big Task = Multiple Agents Working Together

┌─────────────────────────────────────────────────────────────┐
│                  Synergy Session Card                       │
│                                                             │
│  session_id: "sess_quarterly_report"                       │
│  title: "Q4 2024 Business Report"                          │
│  assigned_agents: ["data_agent", "writer_agent",           │
│                    "designer_agent"]                        │
│                                                             │
│  thread_ids: ["thread_abc", "thread_def", "thread_ghi"]   │
└─────────────────────────────────────────────────────────────┘
         │                    │                      │
         ▼                    ▼                      ▼
┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ Thread 1        │ │ Thread 2         │ │ Thread 3        │
│ Data Agent      │ │ Writer Agent     │ │ Designer Agent  │
│                 │ │                  │ │                 │
│ Round 1-15:     │ │ Round 1-12:      │ │ Round 1-8:      │
│ - Collect Gmail │ │ - Read card data │ │ - Read report   │
│ - Analyze sales │ │ - Write intro    │ │ - Create charts │
│ - Generate      │ │ - Write analysis │ │ - Format doc    │
│   charts        │ │ - Write summary  │ │ - Export PDF    │
│                 │ │                  │ │                 │
│ Stores data in  │ │ Stores draft in  │ │ Stores design   │
│ card.session_   │ │ card.documents   │ │ in card.links   │
│ data            │ │                  │ │                 │
└─────────────────┘ └──────────────────┘ └─────────────────┘
```

**Total rounds:** 15 + 12 + 8 = 35 rounds  
**Each thread:** Stays under 200K limit  
**Coordination:** Session card ties everything together

---

## Real-World Use Cases

### 1. Email Campaign Manager (50+ rounds)

```
Task: Send personalized quotes to 20 clients
Synergy Card:
  ├─ Checklist: 20 clients
  ├─ Session Data: {client_1: {email, quote, status}, ...}
  ├─ Documents: [quote_pdfs]
  └─ Recent Activity: [emails_sent, quotes_generated]

Round 1-5:   Calculate quote for client 1 → Store in card
Round 6-10:  Calculate quote for client 2 → Store in card
Round 11-15: Calculate quote for client 3 → Store in card
... (repeat for all 20 clients)
Round 96-100: Send summary email to manager

Conversation: ~2,000 tokens throughout
Card: Stores all 20 quotes + emails + PDFs
```

### 2. Multi-Platform Sync (40+ rounds)

```
Task: Sync data between Gmail, Google Sheets, Slack, and Stripe
Synergy Card:
  ├─ Platforms: [gmail, sheets, slack, stripe]
  ├─ Session Data: {sync_status, errors, records}
  └─ Recent Activity: [tool executions, API calls]

Round 1-10:  Read Gmail (50 emails) → Store in card
Round 11-20: Update Sheets (100 rows) → Store in card
Round 21-30: Post to Slack (10 channels) → Store in card
Round 31-40: Create Stripe invoices (25 customers) → Store in card

Conversation: ~1,500 tokens
Card: Stores all sync data + error logs
```

### 3. Research & Report Generation (60+ rounds)

```
Task: Research 10 topics and create comprehensive report
Synergy Card:
  ├─ Checklist: 10 topics
  ├─ Documents: [research_notes, final_report]
  └─ Session Data: {topic_1: {findings, sources}, ...}

Round 1-5:   Research topic 1 (web search) → Store in card
Round 6-10:  Research topic 2 (web search) → Store in card
... (repeat for all 10 topics)
Round 51-55: Compile findings → Read from card
Round 56-60: Create Google Doc report → Link in card

Conversation: ~2,500 tokens
Card: Stores 10 research summaries + sources
```

---

## Quick Start Checklist

✅ **Already Available - No Setup Needed!**

Your system already has:
- ✅ Synergy database (`data/synergy_sessions.db`)
- ✅ Synergy tools (`synergy_create_session`, `synergy_update_session`, etc.)
- ✅ Synergy routes (`/api/synergy/*`)
- ✅ UI Dashboard (Synergy Kanban board)

**To start using:**

1. **AI creates card at workflow start:**
   ```
   "I'll create a Synergy card to track this project..."
   [calls synergy_create_session]
   ```

2. **AI updates card after each major step:**
   ```
   "Batch 1 complete. Updating card..."
   [calls synergy_update_session with results]
   ```

3. **AI reads card when needed:**
   ```
   "Let me check the card for all previous results..."
   [calls synergy_get_session]
   ```

**That's it!** The AI handles everything automatically.

---

## Monitoring

Watch logs for:
```
✅ Card created: sess_xyz
✅ Card updated: 10 new items in session_data
✅ Checklist progress: 7/10 complete
✅ Conversation: 1,234 tokens (still safe!)
✅ Card storage: 87,456 tokens (unlimited!)
```

---

## Summary

**The Magic:**
- 🎯 **Conversation:** Decisions only (~2K tokens)
- 💾 **Card:** Everything else (unlimited storage)
- 🔄 **Unlimited rounds:** No token limit concerns
- 🤝 **Multi-agent:** Multiple AIs collaborate via card
- ⏸️  **Resumable:** Pause/continue anytime
- 📊 **Trackable:** Kanban board shows progress

**Bottom Line:** You already have Phase 3 (External Working Memory) implemented. Start using it today!

---

**Next:** Read `LONG_RUNNING_AGENT_STRATEGY.md` for complete strategy
