# Tool System - Usage Guide

## 🚀 **Quick Start**

### **For AI Copilots (GitHub Copilot, Claude, ChatGPT)**

The tool system is designed to be used directly by AI assistants through the Tool Registry:

```python
from tools import ToolRegistry

# Initialize
registry = ToolRegistry()

# Execute any tool
result = registry.execute_tool(
    "supabase_query",
    table="users",
    select="*",
    filters={"status": "active"},
    limit=10
)

if result['success']:
    data = result['result']
    print(f"Found {data['count']} users")
else:
    print(f"Error: {result['error']}")
```

---

## 📋 **Available Tools by Platform**

### **Supabase** 🗄️
```python
# Query database
registry.execute_tool("supabase_query", 
    table="users", 
    select="*", 
    filters={"status": "active"}
)

# Insert data
registry.execute_tool("supabase_insert",
    table="users",
    data={"name": "John", "email": "john@example.com"}
)

# Update records
registry.execute_tool("supabase_update",
    table="users",
    data={"status": "inactive"},
    filters={"id": 123}
)

# Delete records
registry.execute_tool("supabase_delete",
    table="users",
    filters={"id": 123}
)
```

### **CloudConvert** 🔄
```python
# Convert file
registry.execute_tool("cloudconvert_convert",
    input_file="/path/to/document.docx",
    input_format="docx",
    output_format="pdf",
    output_file="/path/to/document.pdf"
)

# Optimize image
registry.execute_tool("cloudconvert_optimize",
    input_file="/path/to/image.jpg",
    file_type="image",
    quality=85
)

# Merge PDFs
registry.execute_tool("cloudconvert_merge",
    input_files=["/path/to/doc1.pdf", "/path/to/doc2.pdf"],
    output_format="pdf"
)
```

### **AssemblyAI** 🎤
```python
# Transcribe audio
registry.execute_tool("assemblyai_transcribe",
    audio_file="/path/to/meeting.mp3",
    language="en",
    speaker_labels=True
)

# Analyze sentiment
registry.execute_tool("assemblyai_analyze",
    audio_file="/path/to/call.wav",
    sentiment_analysis=True,
    entity_detection=True
)

# Identify speakers
registry.execute_tool("assemblyai_speakers",
    audio_file="/path/to/interview.mp3",
    speakers_expected=2
)
```

### **Ngrok** 🌐
```python
# Start tunnel
registry.execute_tool("ngrok_start_tunnel",
    port=3000,
    protocol="http"
)

# List tunnels
registry.execute_tool("ngrok_list_tunnels")

# Get public URL
registry.execute_tool("ngrok_get_public_url",
    port=8080
)
```

### **Cloudflare** ☁️
```python
# Deploy Worker
registry.execute_tool("cloudflare_deploy_worker",
    worker_name="api-handler",
    script_path="/path/to/worker.js",
    routes=["api.example.com/*"]
)

# List Workers
registry.execute_tool("cloudflare_list_workers")

# Get logs
registry.execute_tool("cloudflare_get_worker_logs",
    worker_name="api-handler",
    limit=100
)
```

### **WooCommerce** 🛒
```python
# Get orders
registry.execute_tool("woocommerce_get_orders",
    status="processing",
    limit=20
)

# Create product
registry.execute_tool("woocommerce_create_product",
    name="New Product",
    price=29.99,
    description="Product description",
    stock_quantity=100
)

# Update order
registry.execute_tool("woocommerce_update_order",
    order_id=12345,
    status="completed",
    note="Order fulfilled"
)
```

### **GitHub** 📦
```python
# Create repository
registry.execute_tool("github_create_repo",
    name="my-new-repo",
    description="Repository description",
    private=False
)

# Commit file
registry.execute_tool("github_commit_file",
    repo="owner/repo-name",
    file_path="README.md",
    content="# My Project",
    message="Update README"
)

# Create pull request
registry.execute_tool("github_create_pr",
    repo="owner/repo-name",
    title="Add new feature",
    head="feature-branch",
    base="main",
    body="PR description"
)

# Get issues
registry.execute_tool("github_get_issues",
    repo="owner/repo-name",
    state="open",
    limit=30
)
```

### **Google Sheets** 📊
```python
# Read spreadsheet
registry.execute_tool("gsheets_read",
    spreadsheet_id="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    range="Sheet1!A1:D10"
)

# Write data
registry.execute_tool("gsheets_write",
    spreadsheet_id="spreadsheet_id_here",
    range="Sheet1!A1:B2",
    values=[["Name", "Email"], ["John", "john@example.com"]]
)

# Append rows
registry.execute_tool("gsheets_append",
    spreadsheet_id="spreadsheet_id_here",
    range="Sheet1!A:D",
    values=[["Row 1 data"], ["Row 2 data"]]
)

# Create spreadsheet
registry.execute_tool("gsheets_create",
    title="New Spreadsheet",
    sheets=["Sheet1", "Sheet2", "Sheet3"]
)
```

---

## 🔧 **Advanced Usage**

### **List Available Tools**
```python
# List all tools
tools = registry.list_tools()
print(f"Total tools: {len(tools)}")

# List tools for specific platform
supabase_tools = registry.list_tools(platform="supabase")
for tool in supabase_tools:
    print(f"{tool['name']}: {tool['description']}")

# Get all platforms
platforms = registry.get_all_platforms()
print(f"Platforms: {', '.join(platforms)}")
```

### **Get Tool Information**
```python
# Get tool schema
schema = registry.get_tool_schema("supabase_query")
print(f"Description: {schema['description']}")
print(f"Parameters: {list(schema['parameters'].keys())}")

# Validate parameters before execution
valid, error = registry.validate_parameters(
    "supabase_query",
    {"table": "users", "select": "*"}
)
if not valid:
    print(f"Invalid parameters: {error}")
```

### **Error Handling**
```python
result = registry.execute_tool("supabase_query", table="users")

if result['success']:
    # Tool executed successfully
    data = result['result']
    print(f"Query returned {data['count']} rows")
else:
    # Tool failed
    print(f"Error: {result['error']}")
    
    # Check if tool exists
    if 'available_tools' in result:
        print(f"Available tools: {result['available_tools']}")
```

---

## 🎯 **Use Cases**

### **Support AI - Troubleshoot User Issue**
```python
# 1. Check user in database
user_result = registry.execute_tool("supabase_query",
    table="users",
    filters={"email": "customer@example.com"}
)

# 2. Check their orders
orders = registry.execute_tool("woocommerce_get_orders",
    email="customer@example.com"
)

# 3. Transcribe their support call
transcript = registry.execute_tool("assemblyai_transcribe",
    audio_file="support_call_123.mp3",
    sentiment_analysis=True
)

# 4. Log issue to GitHub
issue = registry.execute_tool("github_create_issue",
    repo="company/support-tracker",
    title=f"Customer issue: {user_result['result']['data'][0]['name']}",
    body=f"Transcript: {transcript['result']['text']}"
)
```

### **Development AI - Deploy Fix**
```python
# 1. Commit fix to GitHub
commit = registry.execute_tool("github_commit_file",
    repo="owner/repo",
    file_path="src/bug-fix.js",
    content=fixed_code,
    message="Fix: Resolve user login issue"
)

# 2. Create PR
pr = registry.execute_tool("github_create_pr",
    repo="owner/repo",
    title="Fix user login issue",
    head="fix-branch",
    base="main"
)

# 3. Deploy Worker
deploy = registry.execute_tool("cloudflare_deploy_worker",
    worker_name="api-handler",
    script_path="dist/worker.js"
)

# 4. Test webhook
tunnel = registry.execute_tool("ngrok_start_tunnel", port=3000)
print(f"Test at: {tunnel['result']['public_url']}")
```

### **Operations AI - Generate Report**
```python
# 1. Query database for metrics
users = registry.execute_tool("supabase_query",
    table="users",
    filters={"created_at": ">= '2025-01-01'"}
)

# 2. Get order statistics
orders = registry.execute_tool("woocommerce_get_orders",
    limit=1000
)

# 3. Create report in Google Sheets
sheet = registry.execute_tool("gsheets_create",
    title="Monthly Report - October 2025"
)

# 4. Write data
registry.execute_tool("gsheets_write",
    spreadsheet_id=sheet['result']['id'],
    range="A1:B10",
    values=report_data
)
```

---

## 🧪 **Testing**

```bash
# Test all tools
python tools/test_tools.py

# Test specific platform
python tools/test_tools.py --platform supabase

# Test specific tool
python tools/test_tools.py --tool supabase_query
```

---

## 📚 **Documentation**

- **Tool Schemas**: See `tools/schemas/*.json` for complete tool definitions
- **Implementations**: See `tools/implementations/*.py` for source code
- **Examples**: See `examples/` folder for complete workflows

---

**Total: 34 tools across 8 platforms - Ready for AI copilot integration! 🚀**
