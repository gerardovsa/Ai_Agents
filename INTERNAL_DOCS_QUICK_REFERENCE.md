# Internal Docs AI Tools - Quick Reference

**Date:** November 15, 2025

## All Available Tools (8 Total)

### Basic Tools (4)
```
✅ synergy_create_internal_doc       - Create document
✅ synergy_update_internal_doc       - Update document
✅ synergy_get_internal_doc          - Read document
✅ synergy_export_internal_doc       - Export document
```

### Smart Tools (4)
```
✅ synergy_smart_create_document     - AI creation with templates
✅ synergy_smart_update_document     - Intelligent updates
✅ synergy_smart_analyze_document    - AI analysis
✅ synergy_smart_batch_operations    - Batch processing
```

---

## Quick Examples

### Create from Template
```javascript
synergy_smart_create_document({
  session_id: "sess_20251115_1030_project",
  operation: "create_from_template",
  template: "meeting_notes"  // or project_plan, technical_spec, etc.
})
```

### Update Section
```javascript
synergy_smart_update_document({
  doc_id: "int_doc_123",
  operation: "append_content",
  section: "Action Items",
  content: "- [ ] New task"
})
```

### Analyze Document
```javascript
synergy_smart_analyze_document({
  doc_id: "int_doc_123",
  analysis_type: "summary"  // or key_points, action_items, sentiment, etc.
})
```

### Batch Create
```javascript
synergy_smart_batch_operations({
  operation: "bulk_create",
  session_id: "sess_20251115_1030_project",
  templates: ["meeting_notes", "project_plan", "technical_spec"]
})
```

---

## Templates Available (12)

```
1.  meeting_notes           - Meeting documentation
2.  project_plan            - Project planning with timeline
3.  technical_spec          - Technical specifications
4.  code_review             - Code review template
5.  bug_report              - Bug documentation
6.  feature_request         - Feature proposals
7.  sprint_retrospective    - Sprint reviews
8.  user_story              - User story format
9.  api_documentation       - API docs
10. training_guide          - Training materials
11. policy_document         - Policy docs
12. budget_forecast         - Budget planning
```

---

## Smart Operations

### Create Operations (6)
```
create_from_template         - Use predefined template
create_from_prompt           - Generate from natural language
create_multiple              - Create several related docs
create_structured            - Build with specific structure
create_spreadsheet_advanced  - Advanced spreadsheets
create_with_analysis         - Create with AI insights
```

### Update Operations (7)
```
append_content      - Add to end or specific section
replace_section     - Replace specific section
insert_at           - Insert at character position
merge_from          - Merge content from another doc
reformat            - Clean up formatting
update_metadata     - Update tags/description
smart_edit          - AI-powered edits
```

### Analysis Types (9)
```
summary         - Concise overview
key_points      - Main takeaways
action_items    - Extract todos
sentiment       - Tone analysis
completeness    - Missing sections check
improvements    - Enhancement suggestions
related_docs    - Find similar documents
qa              - Answer specific questions
full_analysis   - Comprehensive analysis
```

### Batch Operations (8)
```
bulk_create          - Create multiple from templates
batch_update         - Apply same update to multiple
mass_export          - Export multiple to same format
bulk_tag             - Apply tags to multiple
archive_multiple     - Archive/delete multiple
generate_summaries   - Create summaries for all
cross_search         - Search across multiple
map_relationships    - Find connections between docs
```

---

## Function Signatures

### synergy_smart_create_document
```python
synergy_smart_create_document(
    session_id: str,              # Required
    operation: str,               # Required
    template: str = None,         # Required for create_from_template
    prompt: str = None,           # Required for create_from_prompt
    title: str = None,            # Optional (auto-generated)
    context: Dict = None,         # Optional
    doc_type: str = "richtext",   # Optional
    auto_tags: bool = True,       # Optional
    auto_link: bool = True        # Optional
)
```

### synergy_smart_update_document
```python
synergy_smart_update_document(
    doc_id: str,                      # Required
    operation: str,                   # Required
    content: str = None,              # Required for most operations
    section: str = None,              # Optional
    position: int = None,             # Optional (for insert_at)
    source_doc_id: str = None,        # Optional (for merge_from)
    preserve_formatting: bool = True, # Optional
    validate: bool = True             # Optional
)
```

### synergy_smart_analyze_document
```python
synergy_smart_analyze_document(
    doc_id: str,           # Required
    analysis_type: str,    # Required
    question: str = None,  # Required for qa
    context: Dict = None   # Optional
)
```

### synergy_smart_batch_operations
```python
synergy_smart_batch_operations(
    operation: str,              # Required
    session_id: str = None,      # Required for bulk_create
    doc_ids: List[str] = None,   # Required for most operations
    templates: List[str] = None, # Required for bulk_create
    update_content: str = None,  # Required for batch_update
    export_format: str = None,   # Required for mass_export
    tags: str = None,            # Required for bulk_tag
    search_query: str = None,    # Required for cross_search
    parallel: bool = True        # Optional
)
```

---

## Common Patterns

### Pattern 1: Start New Project
```javascript
// Create project documents
synergy_smart_batch_operations({
  operation: "bulk_create",
  session_id: "sess_project",
  templates: ["project_plan", "technical_spec", "sprint_retrospective"]
})
```

### Pattern 2: Update All Docs
```javascript
// Add status update to all documents
synergy_smart_batch_operations({
  operation: "batch_update",
  doc_ids: ["int_doc_123", "int_doc_456"],
  update_content: "## Status\n\nCompleted on schedule."
})
```

### Pattern 3: Analyze All Docs
```javascript
// Generate summaries for all documents
synergy_smart_batch_operations({
  operation: "generate_summaries",
  doc_ids: ["int_doc_123", "int_doc_456", "int_doc_789"]
})
```

### Pattern 4: Smart Section Update
```javascript
// Add content to specific section
synergy_smart_update_document({
  doc_id: "int_doc_123",
  operation: "append_content",
  section: "Risks",
  content: "| Risk | Impact | Mitigation |\n|------|--------|------------|\n| New risk | High | Plan here |"
})
```

---

## Return Values

### Create Returns
```javascript
{
  success: true,
  doc_id: "int_doc_...",
  title: "Document Title",
  slug: "document-title",
  share_url: "/internal-docs/document-title",
  processing_steps: [...],
  ai_generated_content: true,
  metadata: { tags: "...", doc_type: "..." }
}
```

### Update Returns
```javascript
{
  success: true,
  doc_id: "int_doc_...",
  version: 2,
  operation: "append_content",
  changes_made: ["Appended content to section: Action Items"],
  validation_warnings: [],
  updated_at: "2025-11-15T11:30:00"
}
```

### Analysis Returns
```javascript
{
  success: true,
  doc_id: "int_doc_...",
  title: "Document Title",
  analysis_type: "summary",
  result: { summary: "..." },
  metadata: { word_count: 250, sections: 5, version: 2 }
}
```

### Batch Returns
```javascript
{
  success: true,
  operation: "bulk_create",
  total_docs: 3,
  processed_docs: 3,
  successful_operations: 3,
  failed_operations: 0,
  results: [...],
  errors: [],
  processing_time_ms: 450,
  summary: "Processed 3 documents in 450ms. 0 errors."
}
```

---

## Error Handling

### Common Errors
```javascript
// Invalid operation
{ success: false, error: "Invalid operation: xyz" }

// Missing required parameter
{ success: false, error: "template parameter required for create_from_template" }

// Document not found
{ success: false, error: "Document not found: int_doc_123" }

// Section not found
{ success: false, error: "Section not found: Risks" }

// Unknown template
{ success: false, error: "Unknown template: xyz. Available: meeting_notes, ..." }
```

---

## Status

**Core Tools:** ✅ Production Ready  
**Smart Tools:** ✅ Production Ready  
**Templates:** ✅ 12 Available  
**Operations:** ✅ 30 Total

**Last Updated:** November 15, 2025
