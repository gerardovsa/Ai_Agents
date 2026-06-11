# USER INTERACTION TOOLS - QUICK REFERENCE

**Date:** January 2025  
**For:** AI Agents  
**Status:** Production Ready

---

## 🎯 TWO FEATURES - WHEN TO USE

### FEATURE 1: Interaction Bubble (BLOCKING)
**Tool:** `request_user_interaction()`  
**Use BEFORE action** - AI waits for user response

✅ **Use when:**
- Need approval BEFORE expensive operation (>$0.03 or >10k tokens)
- Need approval BEFORE destructive operation (delete, modify)
- Multiple valid approaches exist
- User must choose between options
- Need specific information not provided

❌ **Don't use when:**
- Operation already started
- Trivial operation (<1k tokens)
- Clear single path forward
- User already provided all info

---

### FEATURE 2: Feedback Area (NON-BLOCKING)
**Tools:** `show_feedback_area()`, `fetch_user_instructions()`, `hide_feedback_area()`  
**Use DURING action** - AI continues working, checks periodically

✅ **Use when:**
- AFTER creating content (docs, files, reports)
- AFTER research/data gathering
- Processing >20 items (batch operations)
- Operation takes >30 seconds
- User might want to adjust mid-task

❌ **Don't use when:**
- Quick operations (<30 seconds)
- Single operation (not a loop)
- Not adjustable once started
- Better to ask upfront (use Feature 1)

---

## 📋 MANDATORY USAGE PATTERNS

### Pattern 1: After Creating Content
```python
# Create document
doc = google_docs_create_document(title="Report", content=content)

# IMMEDIATELY show feedback area
show_feedback_area("Document created. Adding formatting...")

# Continue work with polling
for section in remaining_sections:
    add_section(section)
    feedback = fetch_user_instructions()
    if feedback.get('has_instructions'):
        adjust_based_on_feedback()

# ALWAYS hide when done
hide_feedback_area()
```

### Pattern 2: After Research
```python
# Perform research
results = web_search("AI trends 2025")

# IMMEDIATELY show feedback area
show_feedback_area("Analyzed 50 sources. Synthesizing insights...")

# Process with polling
for i, result in enumerate(results):
    process_result(result)
    if i % 10 == 0:
        feedback = fetch_user_instructions()

hide_feedback_area()
```

### Pattern 3: Batch Processing
```python
# ALWAYS show for >20 items
show_feedback_area(f"Processing {len(emails)} emails...")

for i, email in enumerate(emails):
    process_email(email)
    
    # Poll every 5 items
    if i % 5 == 0:
        feedback = fetch_user_instructions()
        if feedback.get('has_instructions'):
            handle_feedback(feedback['instructions'])

hide_feedback_area()
```

### Pattern 4: Combined (Feature 1 + Feature 2)
```python
# 1. Get approval BEFORE (Feature 1)
approval = request_user_interaction(
    message="Read 3 large PDFs?",
    interaction_mode="confirmation",
    estimated_tokens=25000,
    estimated_cost_usd=0.075
)

if approval == "cancel":
    return

# 2. Show feedback DURING (Feature 2)
show_feedback_area("Processing 3 PDFs...")

for i, pdf in enumerate(pdfs):
    process_pdf(pdf)
    if i < len(pdfs) - 1:
        feedback = fetch_user_instructions()

hide_feedback_area()
```

---

## 🔧 FEATURE 1 EXAMPLES

### Example 1: Confirmation with Cost
```python
request_user_interaction(
    message="Should I read the full email with 3 PDF attachments?",
    interaction_mode="confirmation",
    context="Email from john@example.com, 12 MB total",
    options=[
        {"label": "Read Full Content", "value": "confirm"},
        {"label": "Metadata Only", "value": "metadata"},
        {"label": "Cancel", "value": "cancel"}
    ],
    estimated_tokens=25000,
    estimated_cost_usd=0.075,
    level="high"
)
```

### Example 2: Choice Selection
```python
request_user_interaction(
    message="Which email thread should I analyze?",
    interaction_mode="choice",
    options=[
        {"label": "Contract Review (5 messages)", "value": "thread_1"},
        {"label": "Project Discussion (12 messages)", "value": "thread_2"},
        {"label": "Q4 Planning (8 messages)", "value": "thread_3"}
    ]
)
```

### Example 3: Input Request
```python
request_user_interaction(
    message="Which sender should I search for?",
    interaction_mode="input",
    options=[
        {"label": "john@example.com", "value": "john@example.com"},
        {"label": "jane@example.com", "value": "jane@example.com"}
    ]
)
```

### Example 4: Control Buttons
```python
request_user_interaction(
    message="Analyzing 50 emails - this may take time...",
    interaction_mode="control",
    control_type="all"  # Shows Pause/Stop/Explain/Continue
)
```

---

## 💬 FEATURE 2 EXAMPLES

### Example 1: Email Processing
```python
show_feedback_area("Analyzing 50 emails...")

processed = []
for i, email in enumerate(emails):
    category = categorize_email(email)
    processed.append({"email": email, "category": category})
    
    if i % 5 == 0:
        feedback = fetch_user_instructions()
        
        if feedback.get('has_instructions'):
            instruction = feedback['instructions'].lower()
            
            if "legal" in instruction:
                emails = filter_legal(emails)
            if "skip archived" in instruction:
                emails = [e for e in emails if not e.archived]
            if "stop" in instruction:
                hide_feedback_area()
                return partial_results(i)

hide_feedback_area()
present_results(processed)
```

### Example 2: Document Generation
```python
show_feedback_area("Generating 30-page report...")

for section in sections:
    write_section(section)
    
    feedback = fetch_user_instructions()
    if feedback.get('has_instructions'):
        instruction = feedback['instructions'].lower()
        
        if "technical" in instruction:
            increase_technical_detail()
        if "examples" in instruction:
            add_more_examples()

hide_feedback_area()
present_report()
```

### Example 3: Data Migration
```python
show_feedback_area("Migrating 500 records...")

for i, record in enumerate(records):
    migrate_record(record)
    
    if i % 50 == 0:
        feedback = fetch_user_instructions()
        if feedback.get('has_instructions'):
            if "stop" in feedback['instructions'].lower():
                hide_feedback_area()
                return partial_results(i)

hide_feedback_area()
return complete_results()
```

---

## 🎯 COMMON USER INSTRUCTIONS

When user provides feedback, handle these patterns:

### Filtering
```python
instruction = feedback['instructions'].lower()

if "focus on" in instruction:
    # "focus on legal emails" → filter to legal
    subject = extract_focus(instruction)
    items = filter_by_subject(items, subject)

if "skip" in instruction:
    # "skip archived" → exclude archived
    skip_type = extract_skip(instruction)
    items = exclude_items(items, skip_type)

if "only" in instruction:
    # "only unread" → filter to unread only
    filter_type = extract_only(instruction)
    items = include_only(items, filter_type)
```

### Detail Level
```python
if "more detail" in instruction or "detailed" in instruction:
    increase_detail_level()

if "less detail" in instruction or "summary" in instruction:
    decrease_detail_level()

if "technical" in instruction:
    increase_technical_depth()

if "simple" in instruction or "basic" in instruction:
    simplify_explanation()
```

### Control
```python
if "pause" in instruction:
    request_user_interaction(
        message=f"Paused. Completed {i} items.",
        interaction_mode="control",
        control_type="continue"
    )

if "stop" in instruction:
    hide_feedback_area()
    return partial_results()

if "explain" in instruction:
    provide_progress_update()
```

---

## 🚨 CRITICAL RULES

### Rule 1: Always Hide Feedback Area
```python
try:
    show_feedback_area("Working...")
    do_work()
finally:
    hide_feedback_area()  # ALWAYS hide, even on error
```

### Rule 2: Always Check has_instructions
```python
feedback = fetch_user_instructions()
if feedback.get('has_instructions'):  # REQUIRED CHECK
    handle_instructions(feedback['instructions'])
```

### Rule 3: Poll Frequency
- Fast operations (30s-1min): Every 3-5 items
- Medium operations (1-5min): Every 10 items
- Long operations (5min+): Every 20 items

### Rule 4: After Content Creation
```python
# Create something
result = create_content()

# IMMEDIATELY show feedback area
show_feedback_area("Content created. Continuing...")
```

### Rule 5: Lifecycle Pattern
```python
# 1. SHOW
show_feedback_area("Starting...")

# 2. WORK + POLL
for i, item in enumerate(items):
    process(item)
    if i % 5 == 0:
        feedback = fetch_user_instructions()

# 3. HIDE (always)
hide_feedback_area()
```

---

## 📊 DECISION TREE

```
Is operation started yet?
├─ NO → Need decision before?
│  ├─ YES → Use Feature 1 (request_user_interaction)
│  └─ NO → Start operation
│
└─ YES (operation started)
   ├─ Operation >30 seconds OR >20 items?
   │  ├─ YES → Use Feature 2 (show_feedback_area + polling)
   │  └─ NO → Continue without feedback area
   │
   ├─ Just created content?
   │  └─ YES → IMMEDIATELY show_feedback_area()
   │
   └─ Just finished research?
      └─ YES → IMMEDIATELY show_feedback_area()
```

---

## ✅ CHECKLIST

Before you finish ANY task, check:

- [ ] Did I create content? → Used show_feedback_area()?
- [ ] Did I do research? → Used show_feedback_area()?
- [ ] Did I process >20 items? → Used show_feedback_area()?
- [ ] Did operation take >30s? → Used show_feedback_area()?
- [ ] If I showed feedback area, did I hide it?
- [ ] Did I poll periodically during work?
- [ ] Did I check has_instructions before acting?

---

**Last Updated:** January 2025  
**Version:** 2.0  
**Status:** Production Ready
