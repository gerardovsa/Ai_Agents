# AI Agent Guide: Internal Docs Tools

**Date:** November 15, 2025  
**For:** AI Agents (Claude, GPT, DeepSeek, etc.)  
**Status:** Production Ready

---

## 🎯 What You Can Do With Internal Docs

As an AI agent, you have **8 powerful tools** to manage internal documents within Synergy sessions:

### **Basic Tools (4)** - Simple Operations
1. `synergy_create_internal_doc` - Create documents
2. `synergy_update_internal_doc` - Update documents
3. `synergy_get_internal_doc` - Read documents
4. `synergy_export_internal_doc` - Export documents

### **Smart Tools (4)** - AI-Powered Operations
5. `synergy_smart_create_document` - Create with templates/AI generation
6. `synergy_smart_update_document` - Intelligent section-aware updates
7. `synergy_smart_analyze_document` - AI analysis and insights
8. `synergy_smart_batch_operations` - Batch processing across multiple docs

---

## 📝 When to Use Each Tool

### Use Basic Tools When:
- ✅ User explicitly provides content to save
- ✅ Simple read/write operations
- ✅ Direct content replacement needed
- ✅ Quick document export

### Use Smart Tools When:
- ✅ User says "create meeting notes" (use template)
- ✅ User says "add a risks section" (section-aware update)
- ✅ User says "summarize this document" (analysis)
- ✅ User says "create project documents" (batch create)
- ✅ User asks "what are the action items?" (extract)
- ✅ You need to generate structured content

---

## 🚀 **SMART TOOL #1: Create Documents**

### Tool: `synergy_smart_create_document`

### When to Use:
- User wants meeting notes, project plans, technical specs, etc.
- User says "create a document for..."
- You need to generate structured content
- Starting a new project with multiple docs

### Available Templates (12):
```
meeting_notes           - Meeting documentation
project_plan            - Project planning with timeline
technical_spec          - Technical specifications
code_review             - Code review template
bug_report              - Bug documentation
feature_request         - Feature proposals
sprint_retrospective    - Sprint reviews
user_story              - User story format
api_documentation       - API docs
training_guide          - Training materials
policy_document         - Policy docs
budget_forecast         - Budget planning
```

### Examples:

**Example 1: User asks for meeting notes**
```
User: "Create meeting notes for today's standup"

YOU CALL:
{
  "name": "synergy_smart_create_document",
  "parameters": {
    "session_id": "sess_20251115_1030_standup",
    "operation": "create_from_template",
    "template": "meeting_notes",
    "title": "Daily Standup - November 15, 2025"
  }
}

RETURNS:
{
  "success": true,
  "doc_id": "int_doc_1731672600000",
  "title": "Daily Standup - November 15, 2025",
  "slug": "daily-standup-november-15-2025",
  "share_url": "/internal-docs/daily-standup-november-15-2025",
  "processing_steps": [
    "Validating operation",
    "Processing create_from_template",
    "Using template: meeting_notes",
    "Generating tags",
    "Creating document in database",
    "Document created successfully"
  ]
}

YOU RESPOND:
"Created meeting notes! I've set up a document with sections for attendees, agenda, discussion, and action items. You can view it at /internal-docs/daily-standup-november-15-2025"
```

**Example 2: User asks for project planning**
```
User: "Start a new microservices migration project"

YOU CALL:
{
  "name": "synergy_smart_create_document",
  "parameters": {
    "session_id": "sess_20251115_1400_migration",
    "operation": "create_from_template",
    "template": "project_plan",
    "title": "Microservices Migration Project"
  }
}

THEN CREATE RELATED DOCS:
{
  "name": "synergy_smart_batch_operations",
  "parameters": {
    "operation": "bulk_create",
    "session_id": "sess_20251115_1400_migration",
    "templates": ["technical_spec", "sprint_retrospective", "bug_report"]
  }
}

YOU RESPOND:
"Started microservices migration project! Created 4 documents:
• Project Plan - Timeline, resources, risks
• Technical Spec - Architecture and design
• Sprint Retrospective - For sprint reviews
• Bug Report - For issue tracking"
```

**Example 3: Generate from natural language**
```
User: "Create a comprehensive guide for onboarding new engineers"

YOU CALL:
{
  "name": "synergy_smart_create_document",
  "parameters": {
    "session_id": "sess_20251115_1500_onboarding",
    "operation": "create_from_prompt",
    "prompt": "Create a comprehensive onboarding guide for new software engineers. Include setup instructions, team introductions, development workflow, code standards, and first-week tasks."
  }
}

YOU RESPOND:
"Created onboarding guide with structured sections for setup, team intro, workflow, standards, and tasks. The document is ready for you to fill in specific details!"
```

---

## ✏️ **SMART TOOL #2: Update Documents**

### Tool: `synergy_smart_update_document`

### When to Use:
- User says "add X to the document"
- User says "update the risks section"
- User pastes doc_id and asks to modify
- Need to append to specific section
- Merge content from another doc

### Operations:
```
append_content      - Add to end or specific section
replace_section     - Replace specific section by title
insert_at           - Insert at character position
merge_from          - Merge from another document
reformat            - Clean up formatting
update_metadata     - Update tags/description
smart_edit          - AI-powered edits
```

### Examples:

**Example 1: Add to specific section**
```
User: "Add these action items to the meeting notes:
- Review PR #123 (Sarah)
- Deploy to staging (Mike)"

YOU CALL:
{
  "name": "synergy_smart_update_document",
  "parameters": {
    "doc_id": "int_doc_1731672600000",
    "operation": "append_content",
    "section": "Action Items",
    "content": "- [ ] Review PR #123 (Sarah)\n- [ ] Deploy to staging (Mike)"
  }
}

RETURNS:
{
  "success": true,
  "doc_id": "int_doc_1731672600000",
  "version": 2,
  "changes_made": ["Appended content to section: Action Items"],
  "validation_warnings": []
}

YOU RESPOND:
"Added 2 action items to the meeting notes (now version 2)!"
```

**Example 2: Replace entire section**
```
User: "Replace the risks section with this table:
| Risk | Impact | Mitigation |
| API delays | High | Start early |"

YOU CALL:
{
  "name": "synergy_smart_update_document",
  "parameters": {
    "doc_id": "int_doc_1731672600000",
    "operation": "replace_section",
    "section": "Risks",
    "content": "| Risk | Impact | Mitigation |\n|------|--------|------------|\n| API delays | High | Start early |"
  }
}

YOU RESPOND:
"Updated the Risks section with the new table!"
```

**Example 3: Merge from another document**
```
User: "Merge the technical details from int_doc_456 into the project plan"

YOU CALL:
{
  "name": "synergy_smart_update_document",
  "parameters": {
    "doc_id": "int_doc_123",
    "operation": "merge_from",
    "source_doc_id": "int_doc_456"
  }
}

YOU RESPOND:
"Merged technical details into the project plan. Added a new section with the content from the technical spec."
```

---

## 🔍 **SMART TOOL #3: Analyze Documents**

### Tool: `synergy_smart_analyze_document`

### When to Use:
- User says "summarize int_doc_123"
- User asks "what are the action items?"
- User asks "is this document complete?"
- User asks "what's the sentiment?"
- User pastes doc_id and asks questions

### Analysis Types:
```
summary         - Concise overview
key_points      - Main takeaways (bullet points)
action_items    - Extract todos/checkboxes
sentiment       - Tone analysis (positive/negative/neutral)
completeness    - Missing sections check
improvements    - Enhancement suggestions
related_docs    - Find similar documents
qa              - Answer specific question
full_analysis   - Comprehensive analysis
```

### Examples:

**Example 1: Summarize document**
```
User: "Summarize int_doc_1731672600000"

YOU CALL:
{
  "name": "synergy_smart_analyze_document",
  "parameters": {
    "doc_id": "int_doc_1731672600000",
    "analysis_type": "summary"
  }
}

RETURNS:
{
  "success": true,
  "result": {
    "summary": "Daily standup meeting covering team updates, blockers, and next steps..."
  },
  "metadata": {
    "word_count": 250,
    "sections": 5
  }
}

YOU RESPOND:
"Here's a summary of the meeting notes:
Daily standup meeting with 3 attendees. Team discussed feature X progress, API integration status, and UI mockups. One blocker: waiting for API keys. Next steps assigned to John, Sarah, and Mike."
```

**Example 2: Extract action items**
```
User: "What are the action items from the meeting?"

YOU CALL:
{
  "name": "synergy_smart_analyze_document",
  "parameters": {
    "doc_id": "int_doc_1731672600000",
    "analysis_type": "action_items"
  }
}

RETURNS:
{
  "success": true,
  "result": {
    "action_items": [
      "- [ ] John: Test feature X in staging",
      "- [ ] Sarah: Complete API integration",
      "- [ ] Mike: Share mockups in Slack"
    ]
  }
}

YOU RESPOND:
"Found 3 action items from the meeting:
✓ John: Test feature X in staging
✓ Sarah: Complete API integration
✓ Mike: Share mockups in Slack"
```

**Example 3: Check completeness**
```
User: "Is the project plan complete?"

YOU CALL:
{
  "name": "synergy_smart_analyze_document",
  "parameters": {
    "doc_id": "int_doc_123",
    "analysis_type": "completeness"
  }
}

RETURNS:
{
  "success": true,
  "result": {
    "completeness_score": 83.3,
    "missing_sections": ["timeline"]
  }
}

YOU RESPOND:
"The project plan is 83% complete. Missing section: Timeline. I can add that if you'd like!"
```

**Example 4: Sentiment analysis**
```
User: "What's the overall tone of the retrospective?"

YOU CALL:
{
  "name": "synergy_smart_analyze_document",
  "parameters": {
    "doc_id": "int_doc_789",
    "analysis_type": "sentiment"
  }
}

RETURNS:
{
  "success": true,
  "result": {
    "sentiment": "positive",
    "positive_indicators": 12,
    "negative_indicators": 3
  }
}

YOU RESPOND:
"The retrospective has a positive tone overall. Found 12 positive indicators (success, great, improvement) and only 3 negative ones (issue, problem)."
```

---

## 📦 **SMART TOOL #4: Batch Operations**

### Tool: `synergy_smart_batch_operations`

### When to Use:
- User says "create multiple documents"
- User says "update all project docs"
- User says "summarize all documents"
- User wants to perform same action on many docs
- Starting a new project with multiple docs

### Operations:
```
bulk_create          - Create multiple from templates
batch_update         - Apply same update to multiple
mass_export          - Export multiple to same format
bulk_tag             - Apply tags to multiple
archive_multiple     - Archive/delete multiple
generate_summaries   - Create summaries for all
cross_search         - Search across multiple
map_relationships    - Find connections
```

### Examples:

**Example 1: Bulk create project documents**
```
User: "Set up documents for the migration project"

YOU CALL:
{
  "name": "synergy_smart_batch_operations",
  "parameters": {
    "operation": "bulk_create",
    "session_id": "sess_20251115_1400_migration",
    "templates": ["project_plan", "technical_spec", "sprint_retrospective", "bug_report"]
  }
}

RETURNS:
{
  "success": true,
  "operation": "bulk_create",
  "total_docs": 4,
  "processed_docs": 4,
  "successful_operations": 4,
  "processing_time_ms": 450,
  "results": [...]
}

YOU RESPOND:
"Created 4 project documents in 450ms:
✓ Project Plan
✓ Technical Specification
✓ Sprint Retrospective
✓ Bug Report

All ready for your team!"
```

**Example 2: Batch update multiple docs**
```
User: "Add status update to all project documents: Sprint 3 completed"

YOU CALL:
{
  "name": "synergy_smart_batch_operations",
  "parameters": {
    "operation": "batch_update",
    "doc_ids": ["int_doc_123", "int_doc_456", "int_doc_789"],
    "update_content": "## Status Update - November 15\n\nSprint 3 completed on schedule. All features deployed to staging."
  }
}

RETURNS:
{
  "success": true,
  "total_docs": 3,
  "successful_operations": 3,
  "summary": "Processed 3 documents in 250ms. 0 errors."
}

YOU RESPOND:
"Updated 3 documents with the status. All now show Sprint 3 completion!"
```

**Example 3: Generate summaries for all docs**
```
User: "Give me a summary of all project documents"

YOU CALL:
{
  "name": "synergy_smart_batch_operations",
  "parameters": {
    "operation": "generate_summaries",
    "doc_ids": ["int_doc_123", "int_doc_456", "int_doc_789", "int_doc_101"]
  }
}

RETURNS:
{
  "success": true,
  "summaries": [
    {"doc_id": "int_doc_123", "title": "Project Plan", "summary": "..."},
    {"doc_id": "int_doc_456", "title": "Technical Spec", "summary": "..."},
    {"doc_id": "int_doc_789", "title": "Sprint Retro", "summary": "..."},
    {"doc_id": "int_doc_101", "title": "Bug Report", "summary": "..."}
  ]
}

YOU RESPOND:
"Here's a summary of all 4 project documents:

📋 Project Plan: Migration timeline with 4 phases, estimated 6 months...
📝 Technical Spec: Microservices architecture with API gateway...
🔄 Sprint Retro: Team velocity increased 20%, 3 improvements identified...
🐛 Bug Report: 2 critical issues open, 5 resolved this sprint..."
```

---

## 🎯 **AI Agent Decision Tree**

### User Request → Your Decision

```
User says: "Create meeting notes"
→ USE: synergy_smart_create_document
→ PARAMETERS: operation="create_from_template", template="meeting_notes"

User says: "Add X to document"
→ USE: synergy_smart_update_document
→ PARAMETERS: operation="append_content"

User says: "Summarize int_doc_123"
→ USE: synergy_smart_analyze_document
→ PARAMETERS: analysis_type="summary"

User says: "What are the action items?"
→ USE: synergy_smart_analyze_document
→ PARAMETERS: analysis_type="action_items"

User says: "Create project documents"
→ USE: synergy_smart_batch_operations
→ PARAMETERS: operation="bulk_create", templates=[...]

User says: "Update all project docs with status"
→ USE: synergy_smart_batch_operations
→ PARAMETERS: operation="batch_update"

User says: "Read int_doc_123"
→ USE: synergy_get_internal_doc (basic tool)

User says: "Export as markdown"
→ USE: synergy_export_internal_doc (basic tool)
```

---

## ⚠️ **Important Notes for AI Agents**

### 1. Always Get Session ID First
Before creating documents, you MUST have a session_id. If user doesn't provide it:
```
YOU ASK: "Which Synergy session should I create this in? Or should I create a new session?"
```

### 2. Section Names Must Match
When using `append_content` or `replace_section`, the section name must match EXACTLY:
```
✅ CORRECT: section="Action Items"    (matches ## Action Items)
❌ WRONG:   section="action items"    (case mismatch)
❌ WRONG:   section="Actions"         (name mismatch)
```

### 3. Progressive Processing
Smart tools return `processing_steps` array. You can tell the user:
```
YOU RESPOND: "Creating document... (validated operation, using template, generating tags, creating in database... Done!)"
```

### 4. Auto-Generated Metadata
Smart create tool auto-generates:
- **Tags** from title (unless you provide)
- **Slug** from title (for sharing)
- **Share URL** (friendly URL)

You can mention this:
```
YOU RESPOND: "Created document! Share it with your team at /internal-docs/daily-standup-november-15"
```

### 5. Version Tracking
Every update increments version. Mention this:
```
YOU RESPOND: "Updated document (now version 3)"
```

### 6. Validation Warnings
If update returns `validation_warnings`, tell the user:
```
RETURNS: { "validation_warnings": ["Unmatched code fence (```)"] }
YOU RESPOND: "Updated! Note: Found an unmatched code fence in the markdown - you may want to check that."
```

---

## 📚 **Common User Requests & Your Responses**

### Request: "Create meeting notes for standup"
```javascript
CALL: synergy_smart_create_document({
  session_id: "sess_...",
  operation: "create_from_template",
  template: "meeting_notes",
  title: "Daily Standup - [Date]"
})

RESPOND: "Created meeting notes with sections for attendees, agenda, discussion, and action items!"
```

### Request: "Add a risks section to the project plan"
```javascript
CALL: synergy_smart_update_document({
  doc_id: "int_doc_...",
  operation: "append_content",
  section: "Risks",  // Will create if doesn't exist
  content: "| Risk | Probability | Impact | Mitigation |\n|------|-------------|--------|------------|\n| | | | |"
})

RESPOND: "Added Risks section with a table template!"
```

### Request: "What are we working on? Check int_doc_123"
```javascript
CALL: synergy_smart_analyze_document({
  doc_id: "int_doc_123",
  analysis_type: "key_points"
})

RESPOND: "Here are the key points from the document:
• Feature X development (80% complete)
• API integration in progress
• UI mockups ready for review
• Sprint 3 deadline: Nov 20"
```

### Request: "Set up a new project for API redesign"
```javascript
CALL: synergy_smart_batch_operations({
  operation: "bulk_create",
  session_id: "sess_...",
  templates: ["project_plan", "technical_spec", "api_documentation"]
})

RESPOND: "Set up API redesign project with 3 documents:
📋 Project Plan - For timeline and resources
📝 Technical Spec - For architecture design
📚 API Documentation - For endpoint specs"
```

---

## 🎓 **Best Practices for AI Agents**

### DO:
✅ Use smart tools for structured content generation  
✅ Use templates when user asks for specific doc types  
✅ Check completeness before declaring "done"  
✅ Mention share URLs so users can access docs  
✅ Use batch operations for multiple docs  
✅ Validate doc_id format before using  
✅ Provide context in your responses  

### DON'T:
❌ Create documents without session_id  
❌ Use basic tools when smart tools fit better  
❌ Forget to increment version mentions  
❌ Ignore validation warnings  
❌ Use wrong section names  
❌ Hardcode content when templates exist  

---

## 🚀 **Advanced Patterns**

### Pattern 1: Progressive Project Setup
```
1. Call synergy_smart_create_document (project_plan template)
2. Call synergy_smart_batch_operations (bulk_create related docs)
3. Call synergy_smart_update_document (add initial timeline)
4. Respond with summary and links
```

### Pattern 2: Document Analysis Workflow
```
1. Call synergy_smart_analyze_document (completeness check)
2. If missing sections, call synergy_smart_update_document (add them)
3. Call synergy_smart_analyze_document (full_analysis)
4. Respond with comprehensive insights
```

### Pattern 3: Batch Document Management
```
1. Call synergy_smart_batch_operations (generate_summaries)
2. Analyze summaries for patterns
3. Call synergy_smart_batch_operations (batch_update with findings)
4. Respond with consolidated report
```

---

## ✅ **Status: Ready to Use**

All 8 tools are:
- ✅ Loaded in tool registry
- ✅ Schemas validated
- ✅ Implementations tested
- ✅ Documentation complete
- ✅ Ready for production

**You can start using these tools NOW in conversations!**

---

**Last Updated:** November 15, 2025  
**For AI Agents:** Claude, GPT-4, DeepSeek, Gemini  
**Version:** 1.0.0
