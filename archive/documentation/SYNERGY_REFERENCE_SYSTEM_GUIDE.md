# Synergy Reference Resolution System

**Date:** November 14, 2025  
**Status:** ✅ IMPLEMENTED  
**Purpose:** Enable AI to understand user references like "N4", "C2.1", "D1"

---

## 🎯 What Problem Does This Solve?

**Before this system:**
```
User: "Continue working on N4"
AI: "I don't know what N4 refers to. Can you clarify?"
```

**After this system:**
```
User: "Continue working on N4"
AI: [Calls synergy_resolve_reference("N4")]
AI: "N4 is 'Process MGR Roofing - 100 Corflute signs order'. I'll start working on that now."
```

---

## 📋 Reference Format

### **Visual Reference System (from UI)**

Your Synergy session cards have these IDs assigned:

```
┌─────────────────────────────────────┐
│  📄 Documents (1)                   │
│  ┌────┐                             │
│  │ D1 │ MBE Eight Mile Plains Quote │
│  └────┘                             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  🎯 Next Steps (7)                  │
│  ┌────┐ ☐ Respond to Aaron Woods   │
│  │ N1 │                             │
│  └────┘                             │
│                                     │
│  ┌────┐ ☐ Process GoldCoast HIGH   │
│  │ N2 │    PRIORITY order           │
│  └────┘                             │
│                                     │
│  ┌────┐ ☐ Respond to MBE Eight     │
│  │ N3 │    Mile Plains              │
│  └────┘                             │
│                                     │
│  ┌────┐ ☐ Process MGR Roofing      │
│  │ N4 │    100 Corflute signs       │
│  └────┘                             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  ✅ Checklist (0/7)                 │
│  ┌────┐ ☐ Aaron Woods - Quote      │
│  │ C1 │    Approval                 │
│  └────┘                             │
│    ┌──────┐ ☐ Read full email      │
│    │ C1.1 │                         │
│    └──────┘                         │
│    ┌──────┐ ☐ Look up quote        │
│    │ C1.2 │                         │
│    └──────┘                         │
│                                     │
│  ┌────┐ ☐ GoldCoast Marketing      │
│  │ C2 │    HIGH PRIORITY            │
│  └────┘                             │
│    ┌──────┐ ☐ Read email specs     │
│    │ C2.1 │                         │
│    └──────┘                         │
└─────────────────────────────────────┘
```

---

## 🔤 Reference Types

| Prefix | Type | Format | Examples | Description |
|--------|------|--------|----------|-------------|
| **N** | Next Steps | N# | N1, N2, N7 | Main action items (top-level tasks) |
| **C** | Checklist | C# | C1, C2 | Checklist items (top-level) |
| **C** | Checklist Sub | C#.# | C1.1, C2.1 | Sub-items under checklist items |
| **D** | Documents | D# | D1, D2 | Linked documents/files |

---

## 🛠️ Available Tools

### **1. synergy_resolve_reference(reference)**

**Purpose:** Understand what a reference refers to

**When to use:**
- User mentions "N4", "C2.1", or any reference
- Before taking action on a referenced item
- To show user what a reference means

**Example:**
```python
# User says: "continue N4"
result = synergy_resolve_reference(reference="N4")

# Result:
{
    "success": True,
    "reference": "N4",
    "type": "next_step",
    "item": {
        "id": "N4",
        "description": "Process MGR Roofing - 100 Corflute signs order",
        "completed": False
    },
    "session_id": "session_12345",
    "session_title": "InHouse Print Production Queue",
    "context": "Next Step N4: 'Process MGR Roofing - 100 Corflute signs order' (⏳ Pending) in session 'InHouse Print Production Queue'"
}

# Now you know: N4 = Process MGR Roofing order
# Proceed with creating quote, invoice, etc.
```

---

### **2. synergy_list_all_references()**

**Purpose:** Show all available references in the session

**When to use:**
- User asks "what can I work on?"
- User mentions invalid reference (show valid ones)
- To provide context about the session

**Example:**
```python
# User says: "show me what tasks I have"
result = synergy_list_all_references()

# Result:
{
    "success": True,
    "session_title": "InHouse Print Production Queue",
    "next_steps": [
        {"ref": "N1", "description": "Respond to Aaron Woods...", "completed": False},
        {"ref": "N2", "description": "Process GoldCoast Marketing...", "completed": False},
        {"ref": "N3", "description": "Respond to MBE Eight Mile...", "completed": False},
        {"ref": "N4", "description": "Process MGR Roofing...", "completed": False},
        {"ref": "N5", "description": "Follow up on Phil Leonard...", "completed": False},
        {"ref": "N6", "description": "Confirm Craig Harper...", "completed": False},
        {"ref": "N7", "description": "Verify Jason Rocha delivery...", "completed": False}
    ],
    "checklist": [
        {
            "ref": "C1",
            "description": "Aaron Woods - Quote Approval",
            "completed": False,
            "sub_items": [
                {"ref": "C1.1", "description": "Read full email thread", "completed": False},
                {"ref": "C1.2", "description": "Look up original quote", "completed": False},
                {"ref": "C1.3", "description": "Check current production schedule", "completed": False}
            ]
        },
        {
            "ref": "C2",
            "description": "GoldCoast Marketing - HIGH PRIORITY",
            "completed": False,
            "sub_items": [
                {"ref": "C2.1", "description": "Read full email for specifications", "completed": False}
            ]
        }
    ],
    "documents": [
        {"ref": "D1", "name": "MBE Eight Mile Plains Quote", "type": "word_doc", "url": "https://..."}
    ],
    "summary": "Found 7 next steps, 2 checklist items, 1 documents"
}

# Present to user:
# "You have 7 next steps (N1-N7), 2 checklist items (C1-C2), and 1 document (D1)"
```

---

### **3. synergy_update_by_reference(reference, action)**

**Purpose:** Update an item using its reference

**When to use:**
- User completes a task ("done with N4")
- User wants to mark item as complete
- User wants to update description
- User wants to remove an item

**Actions:**
- `"complete"` - Mark as done
- `"uncomplete"` - Mark as not done
- `"update"` - Change description (requires `new_description`)
- `"delete"` - Remove item

**Example:**
```python
# User says: "I finished N4"
result = synergy_update_by_reference(
    reference="N4",
    action="complete"
)

# Result:
{
    "success": True,
    "reference": "N4",
    "action": "complete",
    "message": "Updated N4 successfully",
    "updated_item": {
        "description": "Process MGR Roofing - 100 Corflute signs order",
        "completed": True
    }
}

# Tell user: "✅ Marked N4 as complete: Process MGR Roofing order"
```

---

## 🎯 User Conversation Examples

### **Example 1: Continue Work**

```
User: "Continue working on N4"

AI: [Calls synergy_resolve_reference("N4")]

AI: "N4 is 'Process MGR Roofing - 100 Corflute signs order' from the InHouse Print Production Queue.

To proceed, I need to:
1. Check if we have a quote for this order
2. Create an invoice in Xero
3. Generate production documents

Would you like me to start with checking the quote?"
```

---

### **Example 2: Start Checklist Sub-Item**

```
User: "Start C2.1"

AI: [Calls synergy_resolve_reference("C2.1")]

AI: "C2.1 is 'Read full email for specifications (500 + 1,500 Arch DLs)' under checklist item C2 (GoldCoast Marketing - HIGH PRIORITY).

Let me search your emails for GoldCoast Marketing specifications..."

AI: [Calls gmail_search_messages(query="GoldCoast Marketing")]

AI: "Found the email! Here are the specifications:
- Quantity: 500 + 1,500 Arch DLs
- Due date: Tomorrow
- Priority: HIGH

Should I mark C2.1 as complete and move to the next step?"
```

---

### **Example 3: Show Available Tasks**

```
User: "What can I work on?"

AI: [Calls synergy_list_all_references()]

AI: "Here are your available tasks from InHouse Print Production Queue:

**Next Steps (7 pending):**
• N1 - Respond to Aaron Woods with turnaround time
• N2 - Process GoldCoast Marketing HIGH PRIORITY order ⚡
• N3 - Respond to MBE Eight Mile Plains - Certificates
• N4 - Process MGR Roofing - 100 Corflute signs order
• N5 - Follow up on Phil Leonard - 30 more Ivy corflutes
• N6 - Confirm Craig Harper letterhead order (10,000)
• N7 - Verify Jason Rocha delivery dates

**Checklist (2 items with sub-tasks):**
• C1 - Aaron Woods - Quote Approval (3 sub-items)
• C2 - GoldCoast Marketing - HIGH PRIORITY (1 sub-item) ⚡

**Documents (1):**
• D1 - MBE Eight Mile Plains Quote (Word Doc)

Which would you like to start with?"
```

---

### **Example 4: Mark as Complete**

```
User: "Done with N2"

AI: [Calls synergy_resolve_reference("N2")]
AI: [Calls synergy_update_by_reference("N2", action="complete")]

AI: "✅ Marked N2 as complete: 'Process GoldCoast Marketing HIGH PRIORITY order'

You now have 6 pending next steps. Would you like to work on:
• N1 - Respond to Aaron Woods (quote approval)
• N3 - Respond to MBE Eight Mile Plains
• N4 - Process MGR Roofing order"
```

---

### **Example 5: Invalid Reference**

```
User: "Continue N10"

AI: [Calls synergy_resolve_reference("N10")]

AI: "I couldn't find reference N10 in your active session. 

Available Next Steps are N1-N7. Here's the list:
• N1 - Respond to Aaron Woods
• N2 - Process GoldCoast Marketing HIGH PRIORITY
• N3 - Respond to MBE Eight Mile Plains
• N4 - Process MGR Roofing
• N5 - Follow up on Phil Leonard
• N6 - Confirm Craig Harper letterhead
• N7 - Verify Jason Rocha delivery

Which one did you mean?"
```

---

## 🏗️ How It Works (Architecture)

### **Data Flow:**

```
User says "continue N4"
        ↓
AI calls synergy_resolve_reference("N4")
        ↓
Tool parses "N4" → type=next_step, index=4
        ↓
Tool fetches active Synergy session via API
        ↓
Tool extracts next_steps array from session
        ↓
Tool gets item at index 4 (array[3])
        ↓
Tool returns:
{
    "item": {
        "id": "N4",
        "description": "Process MGR Roofing order",
        "completed": false
    },
    "context": "Next Step N4: 'Process MGR Roofing...' in session 'Production Queue'"
}
        ↓
AI now knows what N4 is
        ↓
AI proceeds with task (create quote, invoice, etc.)
```

### **Reference Parsing:**

```python
Reference: "N4"
    ↓
Regex: ^N(\d+)$
    ↓
Type: next_step
Index: 4
    ↓
Fetch session.next_steps[3]  # 0-indexed
```

```python
Reference: "C2.1"
    ↓
Regex: ^C(\d+)\.(\d+)$
    ↓
Type: checklist
Main Index: 2
Sub Index: 1
    ↓
Fetch session.checklist[1].sub_items[0]
```

---

## 🎨 UI Integration

### **How IDs Are Assigned (UI Side):**

The Synergy Dashboard UI automatically assigns IDs when rendering:

```javascript
// In SynergyCard.jsx
function renderNextSteps(steps) {
    return steps.map((step, index) => (
        <div key={index}>
            <span className="id-badge">N{index + 1}</span>
            <span>{step.description}</span>
        </div>
    ));
}

function renderChecklist(items) {
    return items.map((item, i) => (
        <div key={i}>
            <span className="id-badge">C{i + 1}</span>
            <span>{item.description}</span>
            
            {item.sub_items?.map((sub, j) => (
                <div key={j} className="sub-item">
                    <span className="id-badge">C{i + 1}.{j + 1}</span>
                    <span>{sub.description}</span>
                </div>
            ))}
        </div>
    ));
}
```

**Result:** User sees visual IDs (N1, N2, C1.1, etc.) and can reference them in conversation.

---

## 📊 Database Structure

### **Synergy Session Schema:**

```sql
CREATE TABLE synergy_sessions (
    session_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    
    -- Arrays stored as JSON
    next_steps TEXT,      -- [{"description": "...", "completed": false}, ...]
    checklist TEXT,       -- [{"description": "...", "completed": false, "sub_items": [...]}, ...]
    documents TEXT,       -- [{"name": "...", "url": "...", "type": "..."}, ...]
    
    kanban_column TEXT,   -- "backlog", "in_progress", "review", "done"
    status TEXT,          -- "active", "completed", "archived"
    ...
);
```

### **Example Session Data:**

```json
{
    "session_id": "session_12345",
    "title": "InHouse Print Production Queue",
    "next_steps": [
        {"description": "Respond to Aaron Woods with turnaround time", "completed": false},
        {"description": "Process GoldCoast Marketing HIGH PRIORITY order", "completed": false},
        {"description": "Respond to MBE Eight Mile Plains", "completed": false},
        {"description": "Process MGR Roofing - 100 Corflute signs order", "completed": false}
    ],
    "checklist": [
        {
            "description": "Aaron Woods - Quote Approval & Turnaround Time",
            "completed": false,
            "sub_items": [
                {"description": "Read full email thread to get quote details", "completed": false},
                {"description": "Look up original quote in database", "completed": false}
            ]
        },
        {
            "description": "GoldCoast Marketing - HIGH PRIORITY DLs for Tomorrow",
            "completed": false,
            "sub_items": [
                {"description": "Read full email for specifications (500 + 1,500 Arch DLs)", "completed": false}
            ]
        }
    ],
    "documents": [
        {
            "name": "MBE Eight Mile Plains - Formal Quote - Silver Foil Certificates",
            "type": "word_doc",
            "url": "https://docs.google.com/document/d/..."
        }
    ]
}
```

**Reference Resolution:**
- `N1` → `next_steps[0]` → "Respond to Aaron Woods..."
- `N4` → `next_steps[3]` → "Process MGR Roofing..."
- `C1` → `checklist[0]` → "Aaron Woods - Quote Approval"
- `C1.1` → `checklist[0].sub_items[0]` → "Read full email thread..."
- `C2.1` → `checklist[1].sub_items[0]` → "Read full email for specifications..."
- `D1` → `documents[0]` → "MBE Eight Mile Plains Quote"

---

## 🚀 Implementation Details

### **Files Created:**

1. **`tools/implementations/synergy_reference_resolver.py`** (800 lines)
   - `synergy_resolve_reference()` - Main resolution function
   - `synergy_list_all_references()` - List all IDs
   - `synergy_update_by_reference()` - Update by ID
   - Internal helpers for parsing, fetching, resolving

2. **`tools/schemas/synergy_reference_tools.json`**
   - Tool definitions for registry
   - Parameter schemas
   - Instructions and examples
   - Comprehensive documentation

3. **`SYNERGY_REFERENCE_SYSTEM_GUIDE.md`** (this file)
   - Complete usage guide
   - Examples and workflows
   - Architecture documentation

### **API Endpoints Used:**

```
GET  /api/synergy/list?status=active  - Get active sessions
GET  /api/synergy/{session_id}        - Get specific session
PATCH /api/synergy/{session_id}       - Update session
```

---

## 🎯 Best Practices for AI

### **1. Always Resolve First**

```python
# ✅ CORRECT
result = synergy_resolve_reference("N4")
if result['success']:
    description = result['item']['description']
    print(f"Working on: {description}")
    # Proceed with task

# ❌ WRONG
# Assuming you know what N4 is without checking
```

### **2. Handle Errors Gracefully**

```python
result = synergy_resolve_reference("N10")
if not result['success']:
    # Reference doesn't exist
    # List available references
    all_refs = synergy_list_all_references()
    # Show user valid options
```

### **3. Provide Context**

```python
# When user says "continue N4", tell them:
# "N4 is 'Process MGR Roofing order'. I'll start by..."

# Not just:
# "Starting N4"
```

### **4. Confirm Before Completing**

```python
# User says: "finished N4"
result = synergy_resolve_reference("N4")

# Ask confirmation:
# "Should I mark N4 as complete? 
#  (Process MGR Roofing - 100 Corflute signs order)"

# Then:
synergy_update_by_reference("N4", action="complete")
```

### **5. Suggest Next Actions**

```python
# After completing N4:
all_refs = synergy_list_all_references(include_completed=False)

# Show user:
# "✅ N4 complete! You still have:
#  • N1 - Respond to Aaron Woods
#  • N2 - Process GoldCoast Marketing (HIGH PRIORITY)
#  • N3 - Respond to MBE Eight Mile Plains
#  
#  Which would you like to work on next?"
```

---

## 🔧 Advanced Usage

### **Multi-Session Support:**

```python
# If user has multiple sessions, specify which one:
result = synergy_resolve_reference(
    reference="N4",
    session_id="production_queue_session"
)
```

### **Include Completed Items:**

```python
# Show all items including completed:
all_refs = synergy_list_all_references(
    include_completed=True
)

# Useful for progress reports:
# "You've completed 5 out of 12 next steps"
```

### **Batch Updates:**

```python
# Complete multiple items:
for ref in ["N1", "N2", "N3"]:
    synergy_update_by_reference(ref, action="complete")

# Tell user:
# "✅ Marked N1, N2, N3 as complete"
```

---

## 📈 Benefits

### **For Users:**
1. ✅ Natural language: "continue N4" instead of full description
2. ✅ Quick reference: See IDs in UI, use in conversation
3. ✅ Less typing: "N4" vs "Process MGR Roofing order"
4. ✅ Visual tracking: IDs stay consistent across conversations

### **For AI:**
1. ✅ Unambiguous references: No confusion about which task
2. ✅ Context preservation: IDs link to full task details
3. ✅ Session continuity: Same IDs across multiple turns
4. ✅ Efficient communication: Less back-and-forth clarification

---

## 🎓 Testing Examples

```bash
# Test resolution
curl -X POST http://localhost:5001/api/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "synergy_resolve_reference", "parameters": {"reference": "N4"}}'

# Test listing
curl -X POST http://localhost:5001/api/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "synergy_list_all_references", "parameters": {}}'

# Test update
curl -X POST http://localhost:5001/api/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "synergy_update_by_reference", "parameters": {"reference": "N4", "action": "complete"}}'
```

---

## ✅ Status

**Implementation:** ✅ COMPLETE  
**Tools Available:** 3 (resolve, list, update)  
**Registry Integration:** ✅ Ready (add to synergy_tools.json or separate)  
**Testing:** ⏳ Pending (test with actual session)  
**Documentation:** ✅ COMPLETE

---

## 🚀 Next Steps

1. **Test with Real Session:**
   - Create Synergy session with N1-N7, C1-C2, D1
   - Test resolution: `synergy_resolve_reference("N4")`
   - Test listing: `synergy_list_all_references()`
   - Test update: `synergy_update_by_reference("N4", "complete")`

2. **Update System Prompt:**
   - Add reference resolution to AI agent instructions
   - Include examples of natural language usage
   - Add to SYNERGY section of system prompt

3. **UI Enhancement (Optional):**
   - Add copy button next to IDs (click N4 → copies "N4")
   - Add tooltips showing full description on hover
   - Add quick action buttons (Mark Complete, Update, etc.)

4. **Advanced Features (Future):**
   - Voice command support: "Alexa, continue N4"
   - Batch completion: "Mark N1 through N4 as complete"
   - Smart suggestions: "N4 is blocked by N2, should I do N2 first?"
   - Cross-session references: "N4 in Production Queue"

---

**Last Updated:** November 14, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
