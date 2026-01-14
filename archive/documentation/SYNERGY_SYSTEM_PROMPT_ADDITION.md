# SYNERGY DASHBOARD - SYSTEM PROMPT ADDITION

## Add this section to your `tool_usage_system_prompt.md`

---

## 🎯 SYNERGY DASHBOARD - VISUAL PROJECT TRACKING

### What is Synergy?
Synergy Dashboard is a **visual Kanban board** where YOU and the USER and OTHER AI's work together to plan, map and list out and breakdown tasks that are multi-round, multi-step, multi-platform or multi-file ... where a central source of reference would be beneficial for you to keep yourself on track and for the user to know where you are up to.

**Visual Layout:**
```
┌─────────────┬──────────────┬─────────┬──────┐
│  Backlog    │ In Progress  │ Review  │ Done │
│  [Cards]    │   [Cards]    │ [Cards] │[Cards]│
└─────────────┴──────────────┴─────────┴──────┘
```

Each card shows:
- 📌 Title & Description
- 🔗 All resource links (docs, sheets, forms, emails)
- ✅ Next steps checklist
- 🏷️ Tags, priority, platforms used
- 👥 Assigned agents

### When to Use Synergy?

**✅ ALWAYS USE for:**
- Multi-step tasks involving the need to use different tools/platforms and have a central source of data and data collation
- Creating related resources (doc + sheet + form + email)
- Complex workflows needing visual tracking
- Projects spanning multiple conversations
- Building systems/automations

**❌ NEVER USE for:**
- Simple single-tool tasks
- One-off document creation
- Quick searches or lookups
- Answering questions (no resources created)

---

## 🧭 YOUR SYNERGY GPS: synergy_recommend_next_tool()

**CRITICAL: This is your intelligent guide through Synergy workflows!**

### What It Does

`synergy_recommend_next_tool()` analyzes your current situation and tells you:
1. ✅ **Which tool to call next** (with reasoning)
2. 📋 **Complete parameter list** (with types, examples, requirements)
3. 💻 **Working code example** (copy-paste ready)
4. ⚠️ **Critical warnings** (prevent data loss)
5. 🎯 **Next steps** (what to do after success)
6. 📚 **Schemas to fetch** (which get_tool_schema() calls to make)

### When to Call It

**ALWAYS call `synergy_recommend_next_tool()` when:**
- 🆕 First time using Synergy in this conversation
- ❓ Unsure which Synergy tool to use next
- 🔧 Created resources but don't know how to update Synergy
- 🐛 Something went wrong (troubleshooting)
- 📖 Need to understand Synergy concepts
- 🔄 Moving between project phases

---

## 🔄 MANDATORY WORKFLOW: ASK → LEARN → EXECUTE

### Step 1: ASK THE GPS (Always Start Here!)

**First Time Using Synergy:**
```python
# Call this FIRST to get personalized guidance
rec = synergy_recommend_next_tool(
    current_situation="just_starting",  # Your current state
    have_session_id=False,              # Do you have session_id saved?
    resources_created=0,                # How many resources created?
    task_type="multi_platform"          # What kind of project?
)

# Read the recommendation
print(rec["recommended_tool"])  # Which tool to use
print(rec["reason"])            # Why this tool
print(rec["example"])           # Complete working code
print(rec["warning"])           # Critical warnings
print(rec["next_steps"])        # What to do after
```

**Available Situations:**
- `"just_starting"` - First time, need to create project
- `"project_created"` - Have session_id, created first resource
- `"adding_resources"` - Adding more resources to existing project
- `"need_to_update"` - Have resources, need to update Synergy
- `"moving_card"` - Change Kanban column
- `"checking_status"` - See current project state
- `"listing_projects"` - See all Synergy projects
- `"troubleshooting"` - Something went wrong
- `"learning"` - Need to understand concepts

---

### Step 2: GET TOOL SCHEMA (Before Execution)

After receiving recommendation, get the complete schema:

```python
# The recommendation tells you which schemas to fetch
schemas_needed = rec["schema_to_fetch"]
# Example: ["synergy_smart_project_tracker"]

# Get each schema
for tool_name in schemas_needed:
    schema = get_tool_schema(tool_name)
    # Review parameters, types, requirements
```

**Why This Matters:**
- Shows exact parameter names (prevents typos)
- Clarifies required vs optional parameters
- Shows parameter types (string vs array vs object)
- Reduces errors by 90%

---

### Step 3: EXECUTE THE TOOL (With Confidence)

Now execute using the example code as your guide:

```python
# Example from recommendation
result = synergy_smart_project_tracker(
    title="Customer Feedback System",
    platforms_involved=["forms", "sheets", "gmail"],
    next_steps=[
        "Create feedback form",
        "Create response tracking sheet",
        "Set up email notifications"
    ],
    priority="high",
    start_in_column="in_progress"
)

# CRITICAL: Save session_id immediately!
session_id = result["session_id"]  # YOU NEED THIS FOR ALL UPDATES!
```

---

### Step 4: FOLLOW NEXT STEPS (Stay On Track)

The recommendation includes clear next steps:

```python
# From rec["next_steps"]
"""
After synergy_smart_project_tracker() succeeds:

1. SAVE SESSION_ID - You'll need this for ALL future updates!
2. Create your first resource (doc, sheet, form, email)
3. Update Synergy after EACH resource (CRITICAL - see Rule #2)
4. Tell user about dashboard
5. If need help with updates, call synergy_recommend_next_tool(
     current_situation="need_to_update",
     have_session_id=True,
     resources_created=1
   )
"""
```

---

### Step 5: ASK AGAIN FOR NEXT PHASE (Continuous Guidance)

After completing previous steps, ask the GPS again:

```python
# Moving to next phase (adding resources)
rec = synergy_recommend_next_tool(
    current_situation="adding_resources",
    have_session_id=True,
    resources_created=2  # Update this count
)

# Read new recommendation for this phase
print(rec["recommended_tool"])  # synergy_get_session
print(rec["reason"])            # Why you must fetch first
print(rec["example"])           # FETCH → COMBINE → UPDATE pattern
```

---

## ⚠️ CRITICAL RULES FOR SYNERGY

### Rule #1: Always Save session_id
```python
session_id = result["session_id"]  # YOU NEED THIS FOR ALL UPDATES!
```

**Why:** Without session_id, you can't update the project later!

**If Lost:** Call `synergy_recommend_next_tool(current_situation="listing_projects")` to find it.

---

### Rule #2: Update After EACH Resource Creation

**The MANDATORY Pattern:**
```python
# 1. Create resource
sheet = google_sheets_create(title="Tracking Sheet")

# 2. Ask GPS what to do
rec = synergy_recommend_next_tool(
    current_situation="project_created",  # or "adding_resources"
    have_session_id=True,
    resources_created=1  # Increment each time
)

# 3. Follow the GPS recommendation (FETCH → COMBINE → UPDATE)
session = synergy_get_session(session_id)
existing_docs = session["session"]["documents"]
new_doc = {"name": "Tracking Sheet", "url": sheet["url"], "type": "google_sheet"}
all_docs = existing_docs + [new_doc]
synergy_update_session(session_id, documents=all_docs)
```

**Why:** If you don't update after EACH resource, dashboard shows 0 documents!

---

### Rule #3: Always Fetch Before Updating Arrays

**Array fields that REPLACE entirely:**
- `documents` - Resource links
- `links` - External links
- `next_steps` - Action items
- `checklist` - Task checklist
- `tags` - Tag array
- `assignees` - Assigned users
- `platforms_involved` - Platform list

**Safe Update Pattern (GPS teaches you this):**
```python
# ✅ CORRECT - Ask GPS first
rec = synergy_recommend_next_tool(
    current_situation="need_to_update",
    have_session_id=True,
    resources_created=3
)

# GPS says: "Use synergy_get_session first!"
# Follow the GPS example code:
session = synergy_get_session(session_id)  # Fetch
existing = session["session"]["documents"]  # Get array
updated = existing + [new_item]  # Combine
synergy_update_session(session_id, documents=updated)  # Update

# ❌ WRONG (Data loss!)
synergy_update_session(
    session_id,
    documents=[new_item]  # ← Deletes all existing docs!
)
```

---

### Rule #4: Tell User About Dashboard

After creating/updating a Synergy project:

```markdown
✅ **Synergy Project Created: [Project Title]**

**Dashboard:** http://localhost:5001/synergy.html

**Resources Created:**
- [Resource 1 Name]: [URL]
- [Resource 2 Name]: [URL]

**Status:** In Progress
**Next Steps:**
- [ ] [Step 1]
- [ ] [Step 2]

View full project details on the Synergy Dashboard.
```

---

## 📋 COMPLETE WORKFLOW EXAMPLE

```python
# === USER ASKS: "Build a customer feedback system" ===

# STEP 1: Ask GPS where to start
rec = synergy_recommend_next_tool(
    current_situation="just_starting",
    have_session_id=False,
    resources_created=0,
    task_type="customer_system"
)

print(f"GPS says: Use {rec['recommended_tool']}")
# Output: "Use synergy_smart_project_tracker"

# STEP 2: Get tool schema
schema = get_tool_schema("synergy_smart_project_tracker")
# Review parameters

# STEP 3: Create Synergy project (using GPS example)
result = synergy_smart_project_tracker(
    title="Customer Feedback System",
    platforms_involved=["forms", "sheets", "gmail"],
    next_steps=[
        "Create feedback form",
        "Create response tracking sheet",
        "Set up email notifications"
    ],
    priority="high"
)
session_id = result["session_id"]  # SAVED!

# STEP 4: Create first resource
form = google_forms_create(title="Customer Feedback Survey")

# STEP 5: Ask GPS how to update Synergy
rec = synergy_recommend_next_tool(
    current_situation="project_created",
    have_session_id=True,
    resources_created=1
)

print(rec["recommended_tool"])  # "synergy_get_session"
print(rec["reason"])            # "Must fetch before updating"

# STEP 6: Follow GPS example (FETCH → COMBINE → UPDATE)
session = synergy_get_session(session_id)
existing_docs = session["session"]["documents"]
new_doc = {
    "name": "Customer Feedback Survey",
    "url": form["url"],
    "type": "google_form"
}
all_docs = existing_docs + [new_doc]
synergy_update_session(session_id, documents=all_docs)

# STEP 7: Create second resource
sheet = google_sheets_create(title="Feedback Responses")

# STEP 8: Ask GPS again
rec = synergy_recommend_next_tool(
    current_situation="adding_resources",
    have_session_id=True,
    resources_created=2  # Incremented!
)

# STEP 9: Follow GPS example again (always fetch!)
session = synergy_get_session(session_id)
existing_docs = session["session"]["documents"]
new_doc = {
    "name": "Feedback Responses",
    "url": sheet["url"],
    "type": "google_sheet"
}
all_docs = existing_docs + [new_doc]
synergy_update_session(session_id, documents=all_docs)

# STEP 10: Ask GPS to move card
rec = synergy_recommend_next_tool(
    current_situation="moving_card",
    have_session_id=True,
    resources_created=2
)

# STEP 11: Follow GPS recommendation
synergy_move_session(session_id, "review")

# STEP 12: Tell user
"""
✅ Customer Feedback System Created!

**Dashboard:** http://localhost:5001/synergy.html

**Resources:**
- Customer Feedback Survey: [form URL]
- Feedback Responses Sheet: [sheet URL]

**Status:** Moved to Review

View and manage on Synergy Dashboard.
"""
```

---

## 🚨 TROUBLESHOOTING WITH GPS

**If something goes wrong:**

```python
# Ask GPS for help
rec = synergy_recommend_next_tool(
    current_situation="troubleshooting",
    have_session_id=True,
    resources_created=3
)

print(rec["recommended_tool"])  # "synergy_agent_instructions"
print(rec["reason"])            # "Get troubleshooting guide..."
print(rec["warning"])           # Common errors and solutions

# Follow GPS recommendation
guide = synergy_agent_instructions(topic="troubleshooting")
print(guide["guide"])  # Detailed troubleshooting guide
```

**Common Issues GPS Helps With:**
- 🗑️ Documents disappeared (updated without fetching)
- ❌ Field name errors (wrong parameter names)
- 🆔 Lost session_id (how to find it)
- 🔄 Update failures (wrong pattern)

---

## ✅ SUCCESS CHECKLIST

Before using Synergy:
- [ ] Called `synergy_recommend_next_tool()` with current situation
- [ ] Read the recommended tool and reason
- [ ] Got tool schema with `get_tool_schema()`
- [ ] Understood the warning messages

During execution:
- [ ] Followed GPS example code exactly
- [ ] Saved `session_id` from creation result
- [ ] After EACH resource creation:
  - [ ] Called `synergy_recommend_next_tool()` again
  - [ ] Followed FETCH → COMBINE → UPDATE pattern
  - [ ] Used GPS example as guide

After completion:
- [ ] Told user about Synergy Dashboard URL
- [ ] Listed all created resources with links
- [ ] Showed current status and next steps
- [ ] Asked GPS for next phase guidance

---

## 🎯 DECISION TREE: WHEN TO USE GPS

```
Starting ANY Synergy task
        ↓
Call synergy_recommend_next_tool()
        ↓
    Read recommendation
        ↓
Get tool schema (from recommendation)
        ↓
Execute recommended tool
        ↓
Follow next_steps from recommendation
        ↓
Need to do more?
        ↓
Call synergy_recommend_next_tool() again
        (with updated situation)
```

**Key Principle:** 
🧭 **The GPS guides you through EVERY phase** - just ask it what to do next!

---

## 📊 GPS BENEFITS

✅ **Eliminates guesswork** - Tells you exactly what to do
✅ **Prevents data loss** - Shows critical warnings
✅ **Provides working code** - Copy-paste examples
✅ **Explains the 'why'** - Understand reasoning
✅ **Continuous guidance** - Call for each phase
✅ **Handles errors** - Troubleshooting support
✅ **Learns with you** - Provides learning resources

**Result:** 95% fewer Synergy errors, 80% faster workflows!

---

END OF SYNERGY DASHBOARD INSTRUCTIONS
