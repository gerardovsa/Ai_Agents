# Synergy Reference System - Visual Flow Diagrams

**Date:** November 14, 2025  
**Purpose:** Visual explanation of how reference resolution works

---

## 🎨 Visual Reference System

### **What User Sees in UI:**

```
┌─────────────────────────────────────────────────────────────┐
│  InHouse Print Production Queue            📅 Due: 11/13/25│
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📄 Documents (1)                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [D1] MBE Eight Mile Plains - Formal Quote           │   │
│  │      📝 word_doc                                     │   │
│  │      🔗 https://docs.google.com/document/d/...       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  🎯 Next Steps (7)                                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [N1] ☐ Respond to Aaron Woods with turnaround time  │   │
│  │      for approved quote                              │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [N2] ☐ Process GoldCoast Marketing HIGH PRIORITY    │   │
│  │      order (500 + 1,500 DLs needed tomorrow)        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [N3] ☐ Respond to MBE Eight Mile Plains -           │   │
│  │      Certificates with Silver foil (due Nov 20)     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [N4] ☐ Process MGR Roofing - 100 Corflute signs     │   │  ← USER SEES THIS
│  │      order                                           │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [N5] ☐ Follow up on Phil Leonard - 30 more Ivy      │   │
│  │      corflutes request                               │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [N6] ☐ Confirm Craig Harper letterhead order        │   │
│  │      (10,000 on 80gsm)                               │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [N7] ☐ Verify Jason Rocha delivery dates            │   │
│  │      (Nov 25-26 for vinyl banners)                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ✅ Checklist (0/7)                                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [C1] ☐ Aaron Woods - Quote Approval & Turnaround    │   │
│  │           Time (aom@iceworld.com.au)                │   │
│  │                                                      │   │
│  │      ┌──────────────────────────────────────────┐   │   │
│  │      │ [C1.1] ☐ Read full email thread to get  │   │   │
│  │      │            quote details                 │   │   │
│  │      └──────────────────────────────────────────┘   │   │
│  │      ┌──────────────────────────────────────────┐   │   │
│  │      │ [C1.2] ☐ Look up original quote in      │   │   │
│  │      │            database                      │   │   │
│  │      └──────────────────────────────────────────┘   │   │
│  │      ┌──────────────────────────────────────────┐   │   │
│  │      │ [C1.3] ☐ Check current production       │   │   │
│  │      │            schedule for turnaround time  │   │   │
│  │      └──────────────────────────────────────────┘   │   │
│  │      ┌──────────────────────────────────────────┐   │   │
│  │      │ [C1.4] ☐ Draft response email with      │   │   │
│  │      │            turnaround estimate           │   │   │
│  │      └──────────────────────────────────────────┘   │   │
│  │      ┌──────────────────────────────────────────┐   │   │
│  │      │ [C1.5] ☐ Send email and link to this    │   │   │  ← USER SEES THIS
│  │      │            session                       │   │   │
│  │      └──────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [C2] ☐ GoldCoast Marketing - HIGH PRIORITY DLs for  │   │
│  │           Tomorrow                                   │   │
│  │                                                      │   │
│  │      ┌──────────────────────────────────────────┐   │   │
│  │      │ [C2.1] ☐ Read full email for            │   │   │
│  │      │            specifications (500 + 1,500   │   │   │
│  │      │            Arch DLs)                     │   │   │
│  │      └──────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Flow Diagram

### **User Says "Continue N4"**

```
┌────────────────────────────────────────────────────────────┐
│ 1. USER INPUT                                              │
│    "Continue working on N4"                                │
└────────────┬───────────────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────────────┐
│ 2. AI RECOGNIZES REFERENCE                                 │
│    Pattern detected: "N4" = Synergy reference              │
│    Action: Call synergy_resolve_reference("N4")            │
└────────────┬───────────────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────────────┐
│ 3. REFERENCE RESOLUTION TOOL                               │
│    Function: synergy_resolve_reference(reference="N4")     │
│                                                            │
│    Step 3.1: Parse Reference                               │
│    ┌──────────────────────────────────────────┐           │
│    │ Input: "N4"                               │           │
│    │ Regex: ^N(\d+)$                           │           │
│    │ Match: ✅ type=next_step, index=4         │           │
│    └──────────────────────────────────────────┘           │
│                                                            │
│    Step 3.2: Get Active Session                            │
│    ┌──────────────────────────────────────────┐           │
│    │ GET /api/synergy/list?status=active       │           │
│    │ Result: session_id = "session_12345"      │           │
│    │ Title: "InHouse Print Production Queue"   │           │
│    └──────────────────────────────────────────┘           │
│                                                            │
│    Step 3.3: Fetch Session Data                            │
│    ┌──────────────────────────────────────────┐           │
│    │ GET /api/synergy/session_12345            │           │
│    │ Result: {                                 │           │
│    │   next_steps: [                           │           │
│    │     {description: "Respond to Aaron..."},  │           │
│    │     {description: "Process GoldCoast..."}, │           │
│    │     {description: "Respond to MBE..."},    │           │
│    │     {description: "Process MGR Roofing..."} │          │
│    │   ]                                       │           │
│    │ }                                         │           │
│    └──────────────────────────────────────────┘           │
│                                                            │
│    Step 3.4: Extract Item                                  │
│    ┌──────────────────────────────────────────┐           │
│    │ Index: 4 → Array index: 3 (0-based)       │           │
│    │ Item: next_steps[3]                       │           │
│    │ = {                                       │           │
│    │     description: "Process MGR Roofing -   │           │
│    │                  100 Corflute signs order" │           │
│    │     completed: false                      │           │
│    │   }                                       │           │
│    └──────────────────────────────────────────┘           │
└────────────┬───────────────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────────────┐
│ 4. TOOL RESULT RETURNED TO AI                              │
│    {                                                       │
│      "success": true,                                      │
│      "reference": "N4",                                    │
│      "type": "next_step",                                  │
│      "item": {                                             │
│        "id": "N4",                                         │
│        "description": "Process MGR Roofing - 100          │
│                       Corflute signs order",               │
│        "completed": false                                  │
│      },                                                    │
│      "session_id": "session_12345",                        │
│      "session_title": "InHouse Print Production Queue",    │
│      "context": "Next Step N4: 'Process MGR Roofing -     │
│                 100 Corflute signs order' (⏳ Pending)     │
│                 in session 'InHouse Print Production       │
│                 Queue'"                                    │
│    }                                                       │
└────────────┬───────────────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────────────┐
│ 5. AI UNDERSTANDS CONTEXT                                  │
│    Now knows:                                              │
│    • N4 = "Process MGR Roofing order"                      │
│    • It's a next step (not checklist or document)          │
│    • Status: Not completed                                 │
│    • From session: "InHouse Print Production Queue"        │
│                                                            │
│    AI Decision: Proceed with MGR Roofing order             │
└────────────┬───────────────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────────────┐
│ 6. AI RESPONSE TO USER                                     │
│    "N4 is 'Process MGR Roofing - 100 Corflute signs       │
│    order' from your InHouse Print Production Queue.        │
│                                                            │
│    To proceed with this order, I need to:                  │
│    1. Check if we have an existing quote                   │
│    2. Create an invoice in Xero                            │
│    3. Generate production documents                        │
│                                                            │
│    Would you like me to start by checking for the quote?"  │
└────────────────────────────────────────────────────────────┘
```

---

## 🔤 Reference Type Resolution

### **Next Step (N4)**

```
Input: "N4"
        ↓
Parse Regex: ^N(\d+)$
        ↓
Match: ✅
Type: next_step
Index: 4
        ↓
Fetch: session.next_steps[3]
        ↓
Return:
{
    "id": "N4",
    "description": "Process MGR Roofing - 100 Corflute signs order",
    "completed": false
}
```

### **Checklist Item (C2)**

```
Input: "C2"
        ↓
Parse Regex: ^C(\d+)$
        ↓
Match: ✅
Type: checklist
Index: 2
        ↓
Fetch: session.checklist[1]
        ↓
Return:
{
    "id": "C2",
    "description": "GoldCoast Marketing - HIGH PRIORITY DLs for Tomorrow",
    "completed": false,
    "sub_items": [...]
}
```

### **Checklist Sub-Item (C2.1)**

```
Input: "C2.1"
        ↓
Parse Regex: ^C(\d+)\.(\d+)$
        ↓
Match: ✅
Type: checklist
Main Index: 2
Sub Index: 1
        ↓
Fetch: session.checklist[1].sub_items[0]
        ↓
Return:
{
    "id": "C2.1",
    "parent_id": "C2",
    "description": "Read full email for specifications (500 + 1,500 Arch DLs)",
    "completed": false
}
```

### **Document (D1)**

```
Input: "D1"
        ↓
Parse Regex: ^D(\d+)$
        ↓
Match: ✅
Type: document
Index: 1
        ↓
Fetch: session.documents[0]
        ↓
Return:
{
    "id": "D1",
    "name": "MBE Eight Mile Plains - Formal Quote - Silver Foil Certificates",
    "type": "word_doc",
    "url": "https://docs.google.com/document/d/..."
}
```

---

## 🔄 Update Flow Diagram

### **User Says "Done with N4"**

```
┌────────────────────────────────────────────────────────────┐
│ 1. USER INPUT                                              │
│    "I finished N4" or "Done with N4" or "Mark N4 complete" │
└────────────┬───────────────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────────────┐
│ 2. AI RECOGNIZES COMPLETION REQUEST                        │
│    Reference: "N4"                                         │
│    Intent: Mark as complete                                │
│    Action: Call synergy_update_by_reference()              │
└────────────┬───────────────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────────────┐
│ 3. RESOLVE REFERENCE FIRST                                 │
│    synergy_resolve_reference("N4")                         │
│    → Returns: "Process MGR Roofing order"                  │
│                                                            │
│    AI Confirms:                                            │
│    "I'll mark N4 as complete:                              │
│     'Process MGR Roofing - 100 Corflute signs order'"      │
└────────────┬───────────────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────────────┐
│ 4. UPDATE REFERENCE                                        │
│    synergy_update_by_reference(                            │
│        reference="N4",                                     │
│        action="complete"                                   │
│    )                                                       │
│                                                            │
│    Internal Steps:                                         │
│    1. Get session data                                     │
│    2. Find next_steps[3]                                   │
│    3. Set item.completed = true                            │
│    4. PATCH /api/synergy/session_12345                     │
│       {next_steps: updated_array}                          │
└────────────┬───────────────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────────────┐
│ 5. CONFIRMATION TO USER                                    │
│    "✅ Marked N4 as complete:                              │
│        'Process MGR Roofing - 100 Corflute signs order'    │
│                                                            │
│    You now have 6 pending next steps. Would you like to    │
│    work on:                                                │
│    • N1 - Respond to Aaron Woods                           │
│    • N2 - Process GoldCoast Marketing (HIGH PRIORITY)      │
│    • N3 - Respond to MBE Eight Mile Plains"                │
└────────────────────────────────────────────────────────────┘
```

---

## 📊 List All References Flow

### **User Says "What can I work on?"**

```
┌────────────────────────────────────────────────────────────┐
│ 1. USER INPUT                                              │
│    "What can I work on?" or "Show me my tasks"             │
└────────────┬───────────────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────────────┐
│ 2. AI CALLS LIST TOOL                                      │
│    synergy_list_all_references()                           │
└────────────┬───────────────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────────────┐
│ 3. TOOL PROCESSES SESSION                                  │
│    Gets active session                                     │
│    Extracts all items                                      │
│    Assigns IDs (N1-N7, C1-C2, C1.1-C1.5, D1)              │
│    Filters completed items (optional)                      │
└────────────┬───────────────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────────────┐
│ 4. RETURNS CATEGORIZED LIST                                │
│    {                                                       │
│      "next_steps": [                                       │
│        {"ref": "N1", "description": "...", "completed": false}, │
│        {"ref": "N2", "description": "...", "completed": false}, │
│        ... (N1-N7)                                         │
│      ],                                                    │
│      "checklist": [                                        │
│        {"ref": "C1", "description": "...",                 │
│         "sub_items": [                                     │
│           {"ref": "C1.1", "description": "..."},           │
│           {"ref": "C1.2", "description": "..."},           │
│           ... (C1.1-C1.5)                                  │
│         ]},                                                │
│        {"ref": "C2", "description": "...",                 │
│         "sub_items": [                                     │
│           {"ref": "C2.1", "description": "..."}            │
│         ]}                                                 │
│      ],                                                    │
│      "documents": [                                        │
│        {"ref": "D1", "name": "...", "url": "..."}          │
│      ]                                                     │
│    }                                                       │
└────────────┬───────────────────────────────────────────────┘
             │
             ↓
┌────────────────────────────────────────────────────────────┐
│ 5. AI PRESENTS TO USER                                     │
│    "Here are your available tasks from InHouse Print       │
│    Production Queue:                                       │
│                                                            │
│    **Next Steps (7 pending):**                             │
│    • N1 - Respond to Aaron Woods with turnaround time      │
│    • N2 - Process GoldCoast Marketing HIGH PRIORITY ⚡     │
│    • N3 - Respond to MBE Eight Mile Plains                 │
│    • N4 - Process MGR Roofing - 100 Corflute signs         │
│    • N5 - Follow up on Phil Leonard - 30 more Ivy corflutes│
│    • N6 - Confirm Craig Harper letterhead order            │
│    • N7 - Verify Jason Rocha delivery dates                │
│                                                            │
│    **Checklist (2 items with sub-tasks):**                 │
│    • C1 - Aaron Woods - Quote Approval (5 sub-items)       │
│    • C2 - GoldCoast Marketing - HIGH PRIORITY (1 sub-item)│
│                                                            │
│    **Documents (1):**                                      │
│    • D1 - MBE Eight Mile Plains Quote (Word Doc)           │
│                                                            │
│    Which would you like to start with?"                    │
└────────────────────────────────────────────────────────────┘
```

---

## 🎯 Error Handling Flow

### **Invalid Reference (N10)**

```
User: "Continue N10"
        ↓
AI: synergy_resolve_reference("N10")
        ↓
Tool: Parse "N10" → type=next_step, index=10
        ↓
Tool: Fetch session.next_steps[9]
        ↓
Tool: ❌ Index out of range (only 7 items)
        ↓
Tool Returns:
{
    "success": false,
    "error": "Reference 'N10' not found in session 'InHouse Print Production Queue'",
    "reference": "N10"
}
        ↓
AI: synergy_list_all_references()
        ↓
AI: "I couldn't find reference N10 in your active session.
     
     Available Next Steps are N1-N7:
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

## 🔗 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                          │
│  Synergy Dashboard - Shows visual IDs (N1-N7, C1-C2, D1)   │
└────────────┬────────────────────────────────────────────────┘
             │ User sees IDs
             ↓
┌─────────────────────────────────────────────────────────────┐
│                    USER CONVERSATION                         │
│  User: "Continue N4" or "Show tasks" or "Done with N4"      │
└────────────┬────────────────────────────────────────────────┘
             │ Natural language
             ↓
┌─────────────────────────────────────────────────────────────┐
│                      AI AGENT                                │
│  Recognizes reference → Calls appropriate tool               │
└────────────┬────────────────────────────────────────────────┘
             │ Tool execution
             ↓
┌─────────────────────────────────────────────────────────────┐
│            REFERENCE RESOLUTION TOOLS                        │
│  • synergy_resolve_reference(reference)                      │
│  • synergy_list_all_references()                             │
│  • synergy_update_by_reference(reference, action)            │
└────────────┬────────────────────────────────────────────────┘
             │ API calls
             ↓
┌─────────────────────────────────────────────────────────────┐
│                   SYNERGY API                                │
│  GET  /api/synergy/list?status=active                        │
│  GET  /api/synergy/{session_id}                              │
│  PATCH /api/synergy/{session_id}                             │
└────────────┬────────────────────────────────────────────────┘
             │ Database access
             ↓
┌─────────────────────────────────────────────────────────────┐
│               SYNERGY DATABASE                               │
│  synergy_sessions.db                                         │
│  Table: synergy_sessions                                     │
│  Fields: next_steps (JSON), checklist (JSON), documents      │
└─────────────────────────────────────────────────────────────┘
```

---

**Last Updated:** November 14, 2025 12:39 AM  
**Purpose:** Visual documentation of reference resolution system  
**See Also:** `SYNERGY_REFERENCE_SYSTEM_GUIDE.md` for complete documentation
