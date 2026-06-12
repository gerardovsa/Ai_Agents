# Platform Keyword Detection - Quick Reference

**Created:** November 22, 2025  
**Purpose:** Complete list of platform keywords that trigger explicit tool suggestions  
**System:** Intelligent Discovery Skip Enhancement

---

## Overview

When users mention specific platform names in their queries, the system **overrides their historical preference** and suggests tools from the explicitly-mentioned platform only.

**Example:**
- User typically uses Gmail (85% of email activity)
- User asks: "Search my Outlook for emails from John"
- System detects "Outlook" keyword → **Suggests Microsoft tools only**
- Result: Respects user's explicit platform choice

---

## Supported Platform Keywords

### 📧 Email Platforms

| User Says | Detected Platform | Suggested Tools |
|-----------|------------------|-----------------|
| "gmail", "google mail" | **Google** | gmail_list_messages, gmail_search_messages, gmail_send_email |
| "outlook", "microsoft mail" | **Microsoft** | outlook_list_messages, outlook_search_messages, outlook_send_email |

**Example Queries:**
- ✅ "Check my **Gmail** inbox" → Google tools only
- ✅ "Search **Outlook** for emails from boss" → Microsoft tools only
- ⚪ "Check my emails" → Uses preference (no explicit platform)

---

### 📁 File Storage / Drive

| User Says | Detected Platform | Suggested Tools |
|-----------|------------------|-----------------|
| "google drive", "drive", "gdrive" | **Google** | google_drive_list_files, google_drive_search_files, google_drive_list_recent |
| "onedrive", "one drive", "microsoft drive" | **Microsoft** | onedrive_list_files, onedrive_search_files, onedrive_list_recent |

**Example Queries:**
- ✅ "Search my **Google Drive** for PDFs" → Google tools only
- ✅ "Find files on **OneDrive**" → Microsoft tools only
- ✅ "Recent files on **Drive**" → Google tools (common abbreviation)
- ⚪ "Show my recent files" → Uses preference

---

### 📊 Spreadsheets

| User Says | Detected Platform | Suggested Tools |
|-----------|------------------|-----------------|
| "google sheets", "sheets", "gsheet", "gsheets" | **Google** | google_sheets_list, google_sheets_read, google_sheets_write, google_sheets_create |
| "excel", "microsoft excel", "ms excel" | **Microsoft** | excel_list_workbooks, excel_read_sheet, excel_write_sheet |

**Example Queries:**
- ✅ "Open my **Google Sheets** files" → Google tools only
- ✅ "Find **Excel** files with sales data" → Microsoft tools only
- ✅ "List my **sheets**" → Google tools (common term for Google Sheets)
- ⚪ "Show my spreadsheets" → Uses preference

**Special Note:** "Excel" is a strong Microsoft indicator even without "Microsoft" prefix.

---

### 📝 Documents / Word Processing

| User Says | Detected Platform | Suggested Tools |
|-----------|------------------|-----------------|
| "google docs", "docs", "gdoc", "gdocs" | **Google** | google_docs_list, google_docs_create, google_docs_read, google_docs_append |
| "word", "microsoft word", "ms word" | **Microsoft** | word_list_documents, word_create_document, word_read_document |

**Example Queries:**
- ✅ "Create a **Google Doc** with meeting notes" → Google tools only
- ✅ "Open my **Word** documents" → Microsoft tools only
- ✅ "List my **docs**" → Google tools (common abbreviation)
- ⚪ "Show my documents" → Uses preference

---

### 📅 Calendar

| User Says | Detected Platform | Suggested Tools |
|-----------|------------------|-----------------|
| "google calendar", "gcal" | **Google** | google_calendar_list_events, google_calendar_get_event, google_calendar_create_event |
| "outlook calendar", "microsoft calendar" | **Microsoft** | outlook_calendar_list_events, outlook_calendar_get_event, outlook_calendar_create_event |

**Example Queries:**
- ✅ "Check my **Google Calendar** for tomorrow" → Google tools only
- ✅ "Show **Outlook calendar** events" → Microsoft tools only
- ⚪ "What's on my calendar today?" → Uses preference

---

### 👥 Contacts

| User Says | Detected Platform | Suggested Tools |
|-----------|------------------|-----------------|
| "google contacts" | **Google** | google_contacts_list, google_contacts_search, google_contacts_get |
| "outlook contacts", "microsoft contacts" | **Microsoft** | outlook_contacts_list, outlook_contacts_search, outlook_contacts_get |

**Example Queries:**
- ✅ "Find John's email in **Google Contacts**" → Google tools only
- ✅ "Search **Outlook contacts** for Sarah" → Microsoft tools only
- ⚪ "Find contact info for Mike" → Uses preference

---

### ✅ Tasks / Todo Lists

| User Says | Detected Platform | Suggested Tools |
|-----------|------------------|-----------------|
| "google tasks", "gtasks" | **Google** | google_tasks_list, google_tasks_create, google_tasks_update |
| "microsoft todo", "ms todo", "outlook tasks" | **Microsoft** | microsoft_todo_list_tasks, microsoft_todo_create_task, microsoft_todo_update_task |

**Example Queries:**
- ✅ "Add task to **Google Tasks**" → Google tools only
- ✅ "Show my **Microsoft To Do** list" → Microsoft tools only
- ⚪ "Create a new task" → Uses preference

---

## Confidence Scoring Impact

### Without Explicit Platform (Preference-Based)

```
Base confidence: 0.50
+ Pattern match (email): 0.36
+ User authenticated: 0.15
+ Specificity keywords: 0.00
= Total: 0.76 🟡 (Medium confidence)
```

### With Explicit Platform Mention

```
Base confidence: 0.50
+ Pattern match (email): 0.36
+ User authenticated: 0.15
+ Explicit platform: 0.20  ← NEW BOOST
+ Platform auth match: 0.10  ← ADDITIONAL BOOST
= Total: 0.96 🟢 (Very high confidence)
```

**Impact:** Explicit platform mention adds **+0.30 confidence** (from 76% → 96%)

---

## How Detection Works (Technical)

### Step 1: Pattern Matching

```python
# User query: "Check my Gmail inbox"
query_lower = "check my gmail inbox"

# Email pattern matched
pattern_config = QUERY_PATTERNS['email']
```

### Step 2: Platform Keyword Scan

```python
platform_keywords = {
    "google": ["gmail", "google mail"],
    "microsoft": ["outlook", "microsoft mail"]
}

# Check each keyword
for platform, keywords in platform_keywords.items():
    for keyword in keywords:
        if keyword in query_lower:  # "gmail" found!
            return "google"  # Explicit platform detected
```

### Step 3: Tool Selection Override

```python
if explicit_platform == "google":
    # Use ONLY Google tools (ignore user's preference)
    suggested_tools = [
        "gmail_list_messages",
        "gmail_search_messages",
        "gmail_get_message"
    ]
    confidence = 0.96  # Very high
```

### Step 4: System Prompt Injection

```markdown
## 🟢 SUGGESTED TOOLS (Confidence: 96%)

🎯 User explicitly mentioned: GMAIL

**gmail_list_messages** (google_workspace)
  └─ List Gmail messages with optional filters

(User can use these directly without meta-tool discovery)
```

---

## Common Scenarios

### Scenario 1: Platform Match

**Query:** "Check my Gmail inbox"  
**User Preference:** Google (85% usage)  
**Detection:** "gmail" → Google  
**Result:** ✅ Match! High confidence (96%)  
**Behavior:** Load Gmail tools immediately

---

### Scenario 2: Platform Override

**Query:** "Search Outlook for emails"  
**User Preference:** Google (85% usage)  
**Detection:** "outlook" → Microsoft  
**Result:** ⚠️ Override preference! High confidence (95%)  
**Behavior:** Load Outlook tools (ignore Gmail preference)

---

### Scenario 3: No Platform Mentioned

**Query:** "Check my emails"  
**User Preference:** Google (85% usage)  
**Detection:** None (no keyword)  
**Result:** 📊 Use preference (medium confidence 76%)  
**Behavior:** Load Gmail tools based on usage history

---

### Scenario 4: Multiple Platforms (Authenticated Both)

**Query:** "Find spreadsheet files"  
**User Preference:** Microsoft (60% usage)  
**Detection:** None  
**Result:** 📊 Use preference + suggest alternatives  
**Behavior:** Load Excel tools (primary) + Google Sheets (secondary)

---

### Scenario 5: Platform Conflict

**Query:** "Open my Google Sheets in Excel"  
**User Preference:** Google (70% usage)  
**Detection:** "google sheets" → Google  
**Result:** ⚠️ Conflicting keywords detected  
**Behavior:** AI receives BOTH tool sets, explains conversion needed

---

## Integration with Existing Meta-Tools

### Current System (Progressive Discovery)

```
Turn 1: User: "Check my emails"
  → Claude receives 5 meta-tools
  → Claude calls: list_available_platforms()
  → Returns: ["google_workspace", "microsoft_365", ...]

Turn 2: Claude receives 594 tools
  → Claude calls: gmail_list_messages()
  → Result: Email list
```

### Enhanced System (Intelligent Skip with Keywords)

```
Turn 1: User: "Check my Gmail inbox"
  → System detects "gmail" keyword
  → System injects suggested tools in prompt
  → Claude receives 5 meta-tools + 10 Gmail tools
  → Claude calls: gmail_list_messages() immediately
  → Result: Email list (no discovery turn needed!)
```

**Latency Savings:** 2-3 seconds per high-confidence query

---

## False Positive Handling

### Potential Conflicts

**Query:** "Compare Gmail and Outlook"  
**Detection:** BOTH "gmail" AND "outlook"  
**Behavior:** Load tools for BOTH platforms, let AI decide

**Query:** "Does Outlook work like Gmail?"  
**Detection:** BOTH platforms  
**Behavior:** Load info/comparison tools, not action tools

**Query:** "I migrated from Gmail to Outlook"  
**Detection:** BOTH platforms  
**Behavior:** Check user preference date, use Outlook (more recent context)

### Resolution Strategy

```python
if multiple_platforms_detected:
    if query_indicates_comparison:
        # Load meta-tools only
        confidence = 0.60  # Lower confidence
        suggested_tools = []  # Let AI discover
    else:
        # Load tools for ALL detected platforms
        suggested_tools = google_tools + microsoft_tools
        confidence = 0.75  # Medium confidence
```

---

## Implementation Checklist

- [ ] Add `platform_keywords` to all QUERY_PATTERNS entries
- [ ] Implement `detect_explicit_platform()` function
- [ ] Update `calculate_confidence()` to accept `explicit_platform` parameter
- [ ] Modify `generate_suggested_tools_section()` to check explicit platform
- [ ] Add logging for platform detection (debug purposes)
- [ ] Test all keyword combinations
- [ ] Test platform override scenarios
- [ ] Test multi-platform detection handling
- [ ] Measure accuracy (correct platform selected?)
- [ ] A/B test: with/without keyword detection

---

## Testing Examples

### Test Case 1: Gmail Explicit

```python
query = "check my gmail inbox"
result = detect_explicit_platform(query, QUERY_PATTERNS['email'])
assert result == "google"
assert confidence > 0.90
```

### Test Case 2: Outlook Explicit

```python
query = "search outlook for emails from john"
result = detect_explicit_platform(query, QUERY_PATTERNS['email'])
assert result == "microsoft"
assert confidence > 0.90
```

### Test Case 3: No Platform

```python
query = "check my emails"
result = detect_explicit_platform(query, QUERY_PATTERNS['email'])
assert result is None
assert confidence < 0.85  # Falls back to preference
```

### Test Case 4: Google Sheets vs Excel

```python
query = "open my google sheets file"
result = detect_explicit_platform(query, QUERY_PATTERNS['spreadsheet'])
assert result == "google"
assert "google_sheets_list" in suggested_tools
assert "excel_list_workbooks" not in suggested_tools  # Excluded!
```

---

## Success Metrics

### Key Performance Indicators

1. **Platform Detection Accuracy**
   - Goal: >95% correct platform identified
   - Track: Detected platform vs. tool actually used

2. **Confidence Boost Effectiveness**
   - Goal: >90% of explicit mentions result in confidence > 0.90
   - Track: Average confidence with/without explicit platform

3. **Override Correctness**
   - Goal: >85% of overrides match user intent
   - Track: User corrects platform choice (indicates wrong detection)

4. **Latency Improvement**
   - Goal: 40% of queries skip discovery turn
   - Track: Single-turn completions vs. multi-turn

---

## Future Enhancements

### V2: Fuzzy Matching

Handle typos and variations:
- "gogle drive" → Google Drive
- "outlok" → Outlook
- "excell" → Excel

### V3: Multi-Language Support

Detect platform names in other languages:
- "mi correo de gmail" (Spanish) → Gmail
- "mon outlook" (French) → Outlook

### V4: Context-Aware Detection

Remember previous messages in thread:
- Turn 1: "Open Gmail"
- Turn 2: "Send an email to John" → Still use Gmail (context)

---

**Document Version:** 1.0  
**Last Updated:** November 22, 2025  
**Status:** Design Complete - Ready for Implementation  
**Estimated Development Time:** 1 day (keyword detection + confidence boost)
