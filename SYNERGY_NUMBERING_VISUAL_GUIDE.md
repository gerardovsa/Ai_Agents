# Synergy Numbering System - Visual Reference Guide

**Quick Reference:** What users see vs what AI agents use

---

## 📊 DUAL IDENTIFICATION SYSTEM

```
┌─────────────────┬──────────────────┬────────────────────┐
│  UI Display     │  Database ID     │  Who Uses It       │
├─────────────────┼──────────────────┼────────────────────┤
│  D1             │  doc_145         │  Users see D1      │
│  D2             │  doc_146         │  AI uses doc_145   │
│  N1             │  step_200        │  Users see N1      │
│  N1.1           │  step_201        │  AI uses step_200  │
│  C1             │  checklist_100   │  Users see C1      │
│  C1.1           │  checklist_145   │  AI uses check_100 │
└─────────────────┴──────────────────┴────────────────────┘
```

---

## 🎨 VISUAL EXAMPLES

### **1. Synergy Card (Kanban View)**

```
┌─────────────────────────────────────────────────────┐
│ 📄 Customer Onboarding Project              [⋮]    │
├─────────────────────────────────────────────────────┤
│ 📑 Documents (2)                                    │
│                                                     │
│  [D1] 📄 Customer Research Report                  │
│       Google Doc                            [↗]    │
│                                                     │
│  [D2] 📊 Analysis Spreadsheet                      │
│       Google Sheet                          [↗]    │
│                                                     │
├─────────────────────────────────────────────────────┤
│ ✅ Next Steps (2)                                   │
│                                                     │
│  [N1] ☑ Complete initial analysis                  │
│       Due: Nov 20, 2025                            │
│                                                     │
│  [N2] ☐ Prepare presentation                       │
│       Due: Nov 25, 2025                            │
│                                                     │
├─────────────────────────────────────────────────────┤
│ ☑️ Checklist (2/5)                                  │
│                                                     │
│  [C1] ☐ Process Document 1                         │
│    [C1.1] ☑ Step 1 - Extract data (agent-1)       │
│    [C1.2] ☑ Step 2 - Validate (agent-2)           │
│    [C1.3] ☐ Step 3 - Transform                    │
│    [C1.4] ☐ Step 4 - Load                         │
│    [C1.5] ☐ Step 5 - Verify                       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### **2. Edit Modal**

```
┌──────────────────────────────────────────────────────────────┐
│  ✏️ Edit Synergy Session Card                          [✕]  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Title: Customer Onboarding Project                         │
│                                                              │
│  Description: Multi-step project for customer setup         │
│                                                              │
│  📄 Documents                                     [+ Add]    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ [D1] Research Report    https://...    Google Doc [🗑️] │ │
│  │ [D2] Analysis           https://...    Sheet      [🗑️] │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ✅ Next Steps                                    [+ Add]    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ [N1] ☑ Initial analysis   2025-11-20  [+sub] [🗑️]     │ │
│  │   [N1.1] ☑ Extract data                      [✕]       │ │
│  │   [N1.2] ☑ Validate                          [✕]       │ │
│  │ [N2] ☐ Presentation       2025-11-25  [+sub] [🗑️]     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ☑️ Checklist                                     [+ Add]    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ [C1] ☐ Process Document 1            [+sub] [🗑️]      │ │
│  │   [C1.1] ☑ Extract data                      [✕]       │ │
│  │   [C1.2] ☑ Validate                          [✕]       │ │
│  │   [C1.3] ☐ Transform                         [✕]       │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│                                   [Cancel]  [Save Changes]   │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎯 NUMBER BADGE STYLES

### **Primary Badge (Edit Modal)**
```
┌──────┐
│  D1  │  ← Gradient purple/blue, bold, 40px min-width
└──────┘
```
**CSS:** `.item-number-badge`  
**Color:** Linear gradient (#667eea → #764ba2)  
**Used in:** Edit modal input fields

---

### **Inline Badge (Card View)**
```
┌────┐
│ N1 │  ← Light blue bg, compact, 32px min-width
└────┘
```
**CSS:** `.item-number`  
**Color:** Light blue (#e3f2fd) with dark blue text (#1976d2)  
**Used in:** Kanban cards, list views

---

### **Sub-Item Badge (Nested)**
```
┌──────┐
│ C1.1 │  ← Monospace font, gray border, 50px min-width
└──────┘
```
**CSS:** `.sub-number`  
**Color:** Light gray (#fafafa) with dark text  
**Font:** Courier New (monospace)  
**Used in:** Subtasks, nested items

---

## 🔄 DYNAMIC RENUMBERING

### **Scenario 1: Adding Items**
```
Before:
[C1] Task A
[C2] Task B

After adding "Task C":
[C1] Task A
[C2] Task B
[C3] Task C  ← Auto-numbered
```

---

### **Scenario 2: Deleting Items**
```
Before:
[C1] Task A
[C2] Task B
[C3] Task C

After deleting Task B:
[C1] Task A
[C2] Task C  ← Auto-renumbered from C3
```

---

### **Scenario 3: Reordering**
```
Before:
[C1] Task A (DB: check_100)
[C2] Task B (DB: check_101)
[C3] Task C (DB: check_102)

After dragging C3 to top:
[C1] Task C (DB: check_102)  ← Display changed, DB ID stable
[C2] Task A (DB: check_100)
[C3] Task B (DB: check_101)
```

---

## 🤖 AI AGENT SYSTEM PROMPT

### **What AI Agents See:**

```markdown
SYNERGY SESSION CONTEXT

Session: "Customer Onboarding Project"

Documents:
- D1: Customer Research Report [DB: doc_145]
  → AI uses: synergy_get_document("doc_145")
  
- D2: Analysis Spreadsheet [DB: doc_146]
  → AI uses: synergy_get_document("doc_146")

Next Steps:
- N1: Complete initial analysis [DB: step_200]
  → AI uses: synergy_update_next_step("step_200", ...)
  
  - N1.1: Extract data [DB: step_201]
    → AI uses: synergy_update_next_step("step_201", ...)
    
  - N1.2: Validate findings [DB: step_202]
    → AI uses: synergy_update_next_step("step_202", ...)

Checklist:
- C1: Process Document 1 (2/5 completed) [DB: check_100]
  → AI uses: synergy_update_checklist("check_100", ...)
  
  - C1.1: ✓ Extract data (completed by agent-1) [DB: check_145]
  - C1.2: ✓ Validate (completed by agent-2) [DB: check_146]
  - C1.3: Transform (PENDING) [DB: check_147]
    → AI uses: synergy_update_checklist("check_147", "completed")

IMPORTANT:
- Users see display numbers (D1, N1, C1)
- You MUST use database IDs (doc_145, step_200, check_100)
- Display numbers may change if items reordered
- Database IDs NEVER change
```

---

## 📐 HIERARCHY RULES

### **Single Level:**
```
D1, D2, D3        → Documents
N1, N2, N3        → Next Steps
C1, C2, C3        → Checklist
```

### **Two Levels:**
```
N1                → Parent next step
├─ N1.1          → Sub-task 1
├─ N1.2          → Sub-task 2
└─ N1.3          → Sub-task 3

C1                → Parent checklist item
├─ C1.1          → Sub-checklist 1
├─ C1.2          → Sub-checklist 2
└─ C1.3          → Sub-checklist 3
```

### **Maximum Depth: 2 Levels**
```
✅ Allowed:
  C1 → C1.1 → ✓

❌ Not Allowed:
  C1 → C1.1 → C1.1.1 → ✗
```

---

## 🎯 PREFIX MEANINGS

| Prefix | Type | Example | Description |
|--------|------|---------|-------------|
| **D** | Document | D1, D2 | Files, reports, sheets |
| **N** | Next Step | N1, N2 | Action items, tasks |
| **C** | Checklist | C1, C2 | Todo items, subtasks |

---

## 🔍 QUICK REFERENCE TABLE

| Display Number | Database ID | Item Type | Level |
|----------------|-------------|-----------|-------|
| D1 | doc_145 | Document | Top-level |
| D2 | doc_146 | Document | Top-level |
| N1 | step_200 | Next Step | Top-level |
| N1.1 | step_201 | Next Step | Sub-item |
| N1.2 | step_202 | Next Step | Sub-item |
| C1 | check_100 | Checklist | Top-level |
| C1.1 | check_145 | Checklist | Sub-item |
| C1.2 | check_146 | Checklist | Sub-item |

---

## ✅ TESTING CHECKLIST

- [ ] Numbers appear in Kanban cards
- [ ] Numbers appear in edit modal
- [ ] Badges styled correctly (gradient, colors)
- [ ] Sub-items show nested numbers (1.1, 1.2)
- [ ] Adding item increments number
- [ ] Deleting item renumbers remaining items
- [ ] Reordering updates display numbers only
- [ ] Database IDs remain stable after reorder

---

## 🚀 STATUS

**Implementation:** ✅ Complete  
**Visual Design:** ✅ Complete  
**Documentation:** ✅ Complete  
**Ready for Testing:** ✅ Yes

---

**Last Updated:** November 14, 2025
