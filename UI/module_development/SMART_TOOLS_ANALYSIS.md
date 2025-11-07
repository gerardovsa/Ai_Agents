# 🔧 Smart Tools Architecture Analysis

**Created:** October 30, 2025  
**Analysis Date:** October 30, 2025  
**Status:** Complete Understanding

---

## 🎯 Current Smart Tools Structure

### Tool Hierarchy

```
Tools System
├── Granular API Tools (Basic Operations)
│   ├── Single API call tools
│   ├── CRUD operations (Create, Read, Update, Delete)
│   └── Direct 1:1 mapping to platform APIs
│
└── Smart Tools (Multi-Operation Bundled)
    ├── Smart Bundled Tools (Multiple API calls → 1 tool call)
    ├── Smart Analysis Tools (Data processing + recommendations)
    └── AI-Powered Smart Tools (AI generation + API execution)
```

---

## 📋 Tool Type Breakdown

### 1. **Granular API Tools** (Basic Operations)

**Purpose:** Direct 1:1 mapping to platform APIs

**Characteristics:**
- Single API call per tool
- CRUD operations
- No orchestration
- Minimal logic

**Example:** Google Tasks Basic Tools

```json
{
  "name": "google_tasks_create_task",
  "description": "Create a single task",
  "platform": "google_tasks",
  "parameters": {
    "title": {"type": "string", "required": true},
    "notes": {"type": "string", "required": false},
    "due": {"type": "string", "required": false}
  }
}
```

**Tool Count:** ~10-15 per platform
- `create_*`
- `get_*`
- `list_*`
- `update_*`
- `delete_*`
- `complete_*` (for tasks)
- `share_*` (for documents)

---

### 2. **Smart Bundled Tools** (Multi-Operation)

**Purpose:** Combine multiple API calls into single tool call

**Characteristics:**
- Multiple API calls orchestrated
- Efficiency focus (95% reduction in calls)
- Common workflow patterns
- Category: `"smart_bundled"`

**Example:** Google Tasks Smart Project Creation

```json
{
  "name": "google_tasks_smart_create_project",
  "description": "🤖 SMART TOOL: Create a complete project with parent task and multiple subtasks in ONE call",
  "platform": "google_tasks",
  "category": "smart_bundled",
  "parameters": {
    "project_name": {"type": "string", "required": true},
    "tasks_list": {"type": "array", "required": true},
    "task_list_id": {"type": "string", "required": false},
    "due_date": {"type": "string", "required": false}
  },
  "efficiency": "95% reduction (15 API calls → 1 call for 15-task project)"
}
```

**Implementation Pattern:**

```python
def google_tasks_smart_create_project(project_name, tasks_list, task_list_id='@default', due_date=None):
    """
    Creates project with parent task + subtasks in ONE call
    """
    # 1. Create parent task (1 API call)
    parent_result = google_tasks_create_task(
        title=project_name,
        notes=f"Project with {len(tasks_list)} subtasks",
        due=due_date
    )
    
    parent_id = parent_result['task_id']
    subtasks = []
    
    # 2. Create each subtask (N API calls)
    for task_data in tasks_list:
        subtask_result = google_tasks_create_task(
            title=task_data.get('title'),
            notes=task_data.get('notes'),
            due=task_data.get('due'),
            parent=parent_id  # Link to parent
        )
        subtasks.append(subtask_result)
    
    # 3. Return consolidated result
    return {
        'project_task_id': parent_id,
        'project_name': project_name,
        'subtasks_created': len(subtasks),
        'subtasks': subtasks
    }
```

**Use Cases:**
- Create project with 15 subtasks → 1 call instead of 16
- Complete 10 tasks → 1 call instead of 10
- Upload 50 files → 1 call instead of 50

---

### 3. **Smart Analysis Tools** (Data Processing)

**Purpose:** Analyze data + provide recommendations

**Characteristics:**
- Fetches data from multiple sources
- Processes and analyzes
- Returns insights and recommendations
- Category: `"SMART Tools"`

**Example:** SharePoint Site Audit

```json
{
  "name": "sharepoint_smart_site_audit",
  "category": "SMART Tools",
  "description": "SMART: Comprehensive site health and usage analysis",
  "parameters": {
    "site_id": {"type": "string", "required": true},
    "check_permissions": {"type": "boolean", "default": true},
    "check_storage": {"type": "boolean", "default": true}
  },
  "returns": "Dict with comprehensive audit report (storage, permissions, activity, recommendations)"
}
```

**Implementation Pattern:**

```python
def sharepoint_smart_site_audit(site_id, check_permissions=True, check_storage=True):
    """
    Multi-step analysis with recommendations
    """
    audit_report = {
        'site_id': site_id,
        'timestamp': datetime.now().isoformat(),
        'issues': [],
        'recommendations': []
    }
    
    # 1. Get site info
    site_info = sharepoint_get_site(site_id)
    
    # 2. Analyze storage if requested
    if check_storage:
        storage = sharepoint_get_storage_usage(site_id)
        if storage['used_percentage'] > 80:
            audit_report['issues'].append('Storage usage critical (>80%)')
            audit_report['recommendations'].append('Archive old files or increase quota')
    
    # 3. Analyze permissions if requested
    if check_permissions:
        permissions = sharepoint_list_permissions(site_id)
        # Check for overly permissive settings
        for perm in permissions:
            if perm['role'] == 'owner' and perm['type'] == 'everyone':
                audit_report['issues'].append('Everyone has owner access - security risk')
    
    # 4. Return comprehensive report
    return audit_report
```

**Use Cases:**
- Site health check
- Permission audit
- Storage optimization
- Activity analysis

---

### 4. **AI-Powered Smart Tools** (AI + API)

**Purpose:** AI generates content → API executes

**Characteristics:**
- Uses AI (Claude/GPT) for content generation
- Executes API calls with generated content
- Natural language input
- Category: `"smart_bundled"`

**Example:** Google Docs AI Document Generation

```json
{
  "name": "google_docs_ai_smart_generate_document",
  "description": "🤖 SMART TOOL: AI-powered document generation from natural language in ONE call",
  "platform": "google_docs",
  "category": "smart_bundled",
  "parameters": {
    "prompt": {
      "type": "string",
      "description": "Natural language description. Example: 'Create a product requirements document for a mobile fitness app'",
      "required": true
    },
    "tone": {"type": "string", "default": "professional"},
    "share_with": {"type": "array", "required": false},
    "folder_id": {"type": "string", "required": false}
  },
  "efficiency": "99% faster than manual writing (2 hours → 10 seconds)"
}
```

**Implementation Pattern:**

```python
def google_docs_ai_smart_generate_document(prompt, tone='professional', share_with=None, folder_id=None):
    """
    AI generates content → Creates formatted doc
    """
    # 1. Call AI to generate document content
    ai_response = call_ai_api({
        'model': 'claude-3-5-sonnet',
        'messages': [{
            'role': 'user',
            'content': f"Generate a {tone} document based on this prompt: {prompt}. Output as markdown."
        }]
    })
    
    markdown_content = ai_response['content']
    
    # 2. Extract title from content (first heading)
    title = extract_title_from_markdown(markdown_content)
    
    # 3. Create Google Doc with AI-generated content
    doc_result = google_docs_smart_create_from_markdown(
        title=title,
        markdown_content=markdown_content
    )
    
    # 4. Share if requested
    if share_with:
        for email in share_with:
            google_docs_share(doc_result['document_id'], email)
    
    # 5. Move to folder if requested
    if folder_id:
        google_drive_move_to_folder(doc_result['document_id'], folder_id)
    
    return {
        'document_id': doc_result['document_id'],
        'document_url': doc_result['url'],
        'title': title,
        'generated_content': markdown_content,
        'word_count': len(markdown_content.split())
    }
```

**Use Cases:**
- Generate PRD from brief
- Create meeting minutes template
- Write technical specifications
- Generate policy documents

---

## 📊 Smart Tool Categories

### Current Category System

```json
{
  "categories": {
    "smart_bundled": "Multiple operations bundled into one call",
    "SMART Tools": "Analysis and recommendations",
    "smart_analysis": "Data processing with insights",
    "smart_ai_powered": "AI generation + API execution"
  }
}
```

### Category Usage by Platform

| Platform | Granular Tools | Smart Bundled | Smart Analysis | AI Powered |
|----------|---------------|---------------|----------------|------------|
| Google Tasks | 10 | 3 | 0 | 0 |
| Google Docs | 15 | 3 | 0 | 2 |
| SharePoint | 20 | 4 | 4 | 0 |
| Google Forms | 12 | 4 | 0 | 0 |
| OneNote | 15 | 4 | 0 | 0 |
| Outlook | 18 | 5+ | 0 | 0 |

---

## 🏗️ Tool Schema Structure

### Standard Tool Schema

```json
{
  "name": "tool_name",
  "description": "What the tool does",
  "platform": "platform_name",
  "category": "category_name (optional)",
  "parameters": {
    "param_name": {
      "type": "string|integer|boolean|array|object",
      "description": "Parameter description",
      "required": true|false,
      "default": "default_value (optional)",
      "enum": ["option1", "option2"] (optional)
    }
  },
  "returns": {
    "type": "object",
    "description": "What is returned"
  },
  "use_cases": [
    "Use case 1",
    "Use case 2"
  ],
  "efficiency": "Efficiency gain description (for smart tools)"
}
```

### Smart Tool Enhanced Schema

```json
{
  "name": "google_tasks_smart_create_project",
  "description": "🤖 SMART TOOL: Create a complete project with parent task and multiple subtasks in ONE call",
  "platform": "google_tasks",
  "category": "smart_bundled",
  "parameters": {
    "project_name": {
      "type": "string",
      "description": "Name of the project (becomes parent task)",
      "required": true
    },
    "tasks_list": {
      "type": "array",
      "description": "Array of task objects with 'title', 'notes', 'due'",
      "required": true
    }
  },
  "returns": {
    "type": "object",
    "description": "Project created with parent task ID, subtask count, and subtask details"
  },
  "use_cases": [
    "Create software sprint with 10 user stories",
    "Plan event with setup, execution, and cleanup tasks"
  ],
  "efficiency": "95% reduction (15 API calls → 1 call for 15-task project)"
}
```

**Key Additions for Smart Tools:**
1. **🤖 Emoji prefix** in description
2. **`category`** field (smart_bundled, SMART Tools, etc.)
3. **`use_cases`** array with real-world examples
4. **`efficiency`** metric showing reduction

---

## 💡 Smart Tool Design Patterns

### Pattern 1: Batch Operations

**Problem:** Need to perform same operation on multiple items

**Solution:** Bundle into single smart tool call

**Example:** Bulk Complete Tasks

```python
def smart_bulk_complete(task_ids):
    """
    Instead of:
        complete_task(id1)
        complete_task(id2)
        complete_task(id3)
        ... (10 calls)
    
    Use:
        smart_bulk_complete([id1, id2, id3, ...])  # 1 call
    """
    results = []
    for task_id in task_ids:
        result = complete_task(task_id)
        results.append(result)
    return {'completed': len(results), 'results': results}
```

### Pattern 2: Hierarchical Creation

**Problem:** Need to create parent + children in logical structure

**Solution:** Smart tool creates hierarchy

**Example:** Project with Subtasks

```python
def smart_create_project(project_name, subtasks):
    """
    Instead of:
        parent = create_task(project_name)
        create_task(task1, parent=parent.id)
        create_task(task2, parent=parent.id)
        ... (16 calls)
    
    Use:
        smart_create_project("Project", [task1, task2, ...])  # 1 call
    """
    parent = create_task(project_name)
    children = [create_task(t, parent=parent.id) for t in subtasks]
    return {'parent': parent, 'children': children}
```

### Pattern 3: Analysis + Recommendations

**Problem:** Need to fetch data, analyze, and provide insights

**Solution:** Smart analysis tool

**Example:** Site Audit

```python
def smart_site_audit(site_id):
    """
    Instead of:
        site = get_site(site_id)
        storage = get_storage(site_id)
        perms = get_permissions(site_id)
        # Manually analyze each...
    
    Use:
        smart_site_audit(site_id)  # Returns full report
    """
    site = get_site(site_id)
    storage = get_storage(site_id)
    perms = get_permissions(site_id)
    
    issues = []
    recommendations = []
    
    # Automated analysis
    if storage['used'] > 0.8:
        issues.append('Storage critical')
        recommendations.append('Archive old files')
    
    return {'issues': issues, 'recommendations': recommendations}
```

### Pattern 4: AI + API Execution

**Problem:** Need AI to generate content then execute API

**Solution:** AI-powered smart tool

**Example:** AI Document Generation

```python
def ai_smart_generate_document(prompt):
    """
    Instead of:
        # User manually writes content
        # User formats in Google Docs
        # User shares with team
    
    Use:
        ai_smart_generate_document("Create PRD for mobile app")
    """
    # 1. AI generates content
    content = call_ai_api(f"Generate document: {prompt}")
    
    # 2. Create formatted doc
    doc = create_doc_from_markdown(content)
    
    # 3. Return result
    return {'doc_id': doc.id, 'content': content}
```

---

## 🔗 Tool Orchestration

### Smart Tool Internal Flow

```
User Call: smart_create_project("Launch", [task1, task2, task3])
    ↓
Smart Tool Function
    ↓
    ├─→ Call: create_task("Launch")  [Granular Tool #1]
    │   └─→ Returns: parent_task_id
    │
    ├─→ Call: create_task("task1", parent=parent_id)  [Granular Tool #2]
    │   └─→ Returns: subtask_1_id
    │
    ├─→ Call: create_task("task2", parent=parent_id)  [Granular Tool #3]
    │   └─→ Returns: subtask_2_id
    │
    └─→ Call: create_task("task3", parent=parent_id)  [Granular Tool #4]
        └─→ Returns: subtask_3_id
    ↓
Consolidate Results
    ↓
Return: {
    'project_id': parent_task_id,
    'subtasks_created': 3,
    'subtasks': [subtask_1, subtask_2, subtask_3]
}
```

**Efficiency:**
- User made: **1 tool call**
- System made: **4 API calls** (internally)
- Without smart tool: User would make **4 tool calls**
- **Reduction: 75%**

---

## 📦 Module Tool Integration Requirements

### What WooCommerce Module Needs

Based on smart tools analysis, WooCommerce module should have:

#### 1. **Granular API Tools** (10-15 tools)

```
modules/woocommerce/tools/
├── products.json           # Product CRUD
├── orders.json             # Order management
├── customers.json          # Customer management
└── analytics.json          # Basic analytics
```

**Products Tools:**
- `woocommerce_get_products` - List/search products
- `woocommerce_get_product` - Get single product
- `woocommerce_create_product` - Create product
- `woocommerce_update_product` - Update product
- `woocommerce_delete_product` - Delete product
- `woocommerce_update_stock` - Update stock level

**Orders Tools:**
- `woocommerce_get_orders` - List/search orders
- `woocommerce_get_order` - Get single order
- `woocommerce_update_order_status` - Update status
- `woocommerce_refund_order` - Process refund

**Customers Tools:**
- `woocommerce_get_customers` - List customers
- `woocommerce_get_customer` - Get single customer
- `woocommerce_create_customer` - Create customer
- `woocommerce_update_customer` - Update customer

#### 2. **Smart Bundled Tools** (3-5 tools)

```
modules/woocommerce/tools/smart-tools.json
```

**Tools:**

```json
{
  "name": "woocommerce_smart_bulk_update_prices",
  "description": "🤖 SMART TOOL: Update prices for multiple products in ONE call",
  "category": "smart_bundled",
  "efficiency": "90% reduction (10 updates → 1 call)"
}
```

```json
{
  "name": "woocommerce_smart_inventory_report",
  "description": "🤖 SMART TOOL: Generate inventory report with low stock alerts",
  "category": "SMART Tools",
  "efficiency": "Analyzes 1000+ products + generates recommendations in seconds"
}
```

```json
{
  "name": "woocommerce_smart_process_bulk_orders",
  "description": "🤖 SMART TOOL: Process multiple orders (status updates, invoices, emails)",
  "category": "smart_bundled",
  "efficiency": "95% reduction (20 orders → 1 call)"
}
```

#### 3. **Dashboard Export Tool**

```json
{
  "name": "woocommerce_export_dashboard_data",
  "description": "Export current dashboard view as JSON for AI consumption",
  "parameters": {
    "subtab": {
      "type": "string",
      "enum": ["products", "orders", "customers", "analytics", "all"],
      "default": "all"
    }
  }
}
```

---

##  Key Takeaways for Module Implementation

### 1. **Tool Granularity**
- **Granular tools** = 1 API call per tool (basic CRUD)
- **Smart tools** = N API calls bundled into 1 tool call
- Ratio: ~10-15 granular tools : 3-5 smart tools per platform

### 2. **Smart Tool Indicators**
- 🤖 Emoji in description
- `category: "smart_bundled"` or `"SMART Tools"`
- `efficiency` metric in schema
- `use_cases` array with examples

### 3. **Implementation Pattern**
Smart tools internally call granular tools:

```python
def smart_tool():
    # Orchestrate granular tools
    result1 = granular_tool_1()
    result2 = granular_tool_2()
    result3 = granular_tool_3()
    
    # Consolidate results
    return consolidated_result
```

### 4. **Tool Categories**
- `smart_bundled` - Multiple operations → 1 call
- `SMART Tools` - Analysis + recommendations
- `smart_ai_powered` - AI + API execution

### 5. **Module Structure**
```
modules/[module-id]/tools/
├── manifest.json           # Tool registry
├── [category].json         # Granular tools by category
└── smart-tools.json        # Smart bundled tools
```

---

## 🎯 Next Step: Apply to WooCommerce

Now that we understand the structure, we can:

1.  Extract WooCommerce from HTML
2.  Create granular tool schemas (products, orders, customers)
3.  Create smart tool schemas (bulk operations, reports)
4.  Implement tool functions in module class
5.  Test AI can call tools

**Ready to proceed with WooCommerce extraction?**

---

**Last Updated:** October 30, 2025  
**Version:** 1.0.0  
**Status:**  Complete Understanding
