# System Prompt Updates - December 12, 2025

## Changes Applied to `tool_usage_system_prompt.md`

### ✅ 1. Tool Ecosystem Architecture (Lines 192-245)

**Replaced:** "TOOL FRAMEWORK" with "TOOL ECOSYSTEM"

**Added:** Comprehensive 4-layer architecture explanation:

**LAYER 1: NAVIGATION TOOLS** - Find what exists
- `list_platform_tools()` - List tools by platform
- `search_tools()` - Search 646 tools by keyword
- `inhouse_get_domain_guide()` - Navigate InHouse domains

**LAYER 2: GUIDANCE TOOLS** - Learn how platforms work
- `platform_guide()` - Platform overviews
- `inhouse_calculator_guide()` - Calculator workflows
- `inhouse_query_guide()` - SQL query patterns
- `inhouse_database_guide()` - Database schemas
- `synergy_guide()` - Project tracking system
- `visualization_guide()` - Chart library syntax

**LAYER 3: SPECIFICATION TOOLS** - Get exact requirements
- `get_tool_schema()` - Parameters, types, required fields

**LAYER 4: EXECUTION TOOLS** - Take action
- `execute_tool()` - Run any tool
- Platform tools (Gmail, Google Docs, Outlook, etc.)
- InHouse tools (calculators, SQL, stock)
- `python_exec()` - Secure Python sandbox

**Key Principles:**
- Progressive Discovery: Discover tools as needed
- Just-In-Time Learning: Get instructions before execution
- Meta-Navigation: Tools help navigate other tools
- Intelligent Discovery: System learns patterns over time

---

### ✅ 2. Python Execution Security Model (Lines 455-522)

**Added:** Complete security documentation for Python execution sandbox

**Security Features:**
- ✅ RestrictedPython sandbox (safe execution)
- ✅ Limited libraries: pandas, numpy, matplotlib, seaborn
- ✅ No file system access (except workspace)
- ✅ No network access (no requests, urllib)
- ✅ No subprocess execution (no system commands)
- ✅ 30-second timeout protection

**Available Tools:**
```python
python_exec(code)
python_exec_with_dataframe(code, dataframe)
python_exec_analysis(code, data_file)
```

**What CAN Be Executed:**
- Data transformation (df operations)
- Statistical analysis (numpy, correlations)
- Visualizations (matplotlib, saved to workspace)

**What CANNOT Be Executed:**
- File system access (open, read, write)
- Network requests (requests, urllib)
- System commands (os.system, subprocess)
- Dangerous operations (exec, eval)

**Use Cases:**
- Analyze InHouse database query results
- Transform data from Google Sheets/Excel
- Generate charts from business metrics
- Calculate complex statistical models
- Clean and format data for reports

---

### ✅ 3. Renamed Tool: synergy_agent_instructions → synergy_guide

**Changed in 4 locations:**
- Line 567: Discovery example
- Line 580: First time workflow (1st occurrence)
- Line 581: First time workflow (2nd occurrence)
- Line 598: Decision flowchart

**Reason:** Consistency with other guide tools (_guide suffix)

---

### ✅ 4. Enhanced InHouse Print System Description (Lines 903-920)

**Old:** Generic system description
**New:** Business-focused context

**Business Context:**
"This tool ecosystem serves the staff at InHouse Print (a printing business) to perform daily workflows, tactical decisions, and leadership analytics."

**Primary Use Cases:**
- 📧 **Email Processing:** Read emails → Extract specs → Create quotes → Draft replies
- 🖨️ **Quote Creation:** Calculate printing costs → Create Xero invoices
- 🗄️ **Database Access:** Lookup printing history, client records via "Fred" database
- 📊 **Business Intelligence:** SQL query library for leadership reports and KPIs
- 🎨 **Visual Rendering:** Generate reports with logos, layouts, charts

**Database Alias:**
"Fred" = In House SQL database (use interchangeably, staff prefer "Fred")

---

### ✅ 5. Removed Section: Outlook Email Filtering

**Reason:** Filtering parameters are documented in tool schemas

**Removed ~180 lines covering:**
- max_results parameter usage
- unread_only filtering
- search parameter examples
- filter OData queries
- date range filtering
- Performance impact examples

**Why removed:** 
- Tool schemas already document all parameters
- get_tool_schema("microsoft_outlook_list_messages") provides this
- Reduces redundancy (per user request: "remove repetitions")
- Keeps prompt focused on ecosystem navigation

---

## Impact Summary

**File:** `tool_usage_system_prompt.md`
**Total Lines:** 1,082 (after updates)

**Additions:**
- +53 lines: Tool Ecosystem architecture
- +67 lines: Python execution security model
- +17 lines: Enhanced InHouse Print context

**Removals:**
- -180 lines: Outlook filtering (now in schemas)

**Renames:**
- 4 occurrences: synergy_agent_instructions → synergy_guide

**Net Change:** -43 lines (cleaner, more focused)

---

## Verification

```powershell
# Key sections verified:
✅ Line 192: TOOL ECOSYSTEM ARCHITECTURE
✅ Line 455: PYTHON EXECUTION - SECURE DATA ANALYSIS  
✅ Line 567: synergy_guide(topic="overview")
✅ Line 580-581: synergy_guide references
✅ Line 598: synergy_guide in flowchart
✅ Line 903: INHOUSE PRINT SYSTEM - BUSINESS OPERATIONS SUITE
```

---

## Next Steps

1. ✅ All updates applied successfully
2. ⏳ User review required
3. ⏸ Commit changes after approval
4. ⏸ Update schema files if needed (synergy_agent_instructions → synergy_guide)

---

## User Feedback Addressed

✅ **"What is the best word for tools structure?"**  
→ Changed to "Tool Ecosystem" (living, interconnected, adaptive system)

✅ **"Add Python execution security model"**  
→ Added comprehensive security section with examples

✅ **"Rename synergy_agent_instructions to synergy_guide"**  
→ Renamed in 4 locations for consistency

✅ **"Explain InHouse Print business context"**  
→ Enhanced with workflows: email processing, quote creation, database lookups, BI reports, visual rendering

✅ **"Remove Outlook filtering (in schemas)"**  
→ Removed ~180 lines of parameter documentation

✅ **"Remove repetitions"**  
→ Net reduction of 43 lines while adding critical context
