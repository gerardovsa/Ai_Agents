# AI Agents - Tool Integration System

## 🎯 **Purpose**

This folder provides **MCP-compatible tool integrations** for all platforms, allowing AI assistants (GitHub Copilot, Claude, ChatGPT, etc.) to directly interact with your services through structured tool calls.

---

## 🛠️ **Available Platform Tools**

### **1. Supabase Tools** 🗄️
- `supabase_query` - Query database tables
- `supabase_insert` - Insert data into tables
- `supabase_update` - Update existing records
- `supabase_delete` - Delete records
- `supabase_auth` - Manage authentication
- `supabase_storage` - Manage file storage

### **2. CloudConvert Tools** 🔄
- `cloudconvert_convert` - Convert files between formats
- `cloudconvert_optimize` - Optimize images/videos
- `cloudconvert_merge` - Merge multiple files
- `cloudconvert_status` - Check conversion job status

### **3. AssemblyAI Tools** 🎤
- `assemblyai_transcribe` - Transcribe audio/video
- `assemblyai_analyze` - Sentiment/topic analysis
- `assemblyai_speakers` - Speaker diarization
- `assemblyai_status` - Check transcription status

### **4. Ngrok Tools** 🌐
- `ngrok_start_tunnel` - Start HTTP tunnel
- `ngrok_list_tunnels` - List active tunnels
- `ngrok_stop_tunnel` - Stop specific tunnel
- `ngrok_get_public_url` - Get public URL for port

### **5. Cloudflare Tools** ☁️
- `cloudflare_deploy_worker` - Deploy Worker script
- `cloudflare_list_workers` - List all Workers
- `cloudflare_get_worker_logs` - Fetch Worker logs
- `cloudflare_worker_status` - Check Worker health

### **6. WooCommerce Tools** 🛒
- `woocommerce_get_orders` - Retrieve orders
- `woocommerce_create_product` - Create new product
- `woocommerce_update_order` - Update order status
- `woocommerce_get_products` - List products

### **7. GitHub Tools** 📦
- `github_create_repo` - Create repository
- `github_commit_file` - Commit file changes
- `github_create_pr` - Create pull request
- `github_get_issues` - List issues

### **8. Google Sheets Tools** 📊
- `gsheets_read` - Read spreadsheet data
- `gsheets_write` - Write to spreadsheet
- `gsheets_append` - Append rows
- `gsheets_create` - Create new spreadsheet

---

## 📋 **Tool Schema Format**

Each tool follows this structure:

```json
{
  "name": "tool_name",
  "description": "What the tool does",
  "parameters": {
    "param1": {
      "type": "string",
      "description": "Parameter description",
      "required": true
    }
  },
  "returns": {
    "type": "object",
    "description": "Return value description"
  }
}
```

---

## 🚀 **Quick Start**

### **For AI Copilots**

```python
# Example: Using Supabase tool
result = use_tool(
    name="supabase_query",
    parameters={
        "table": "users",
        "select": "*",
        "filters": {"status": "active"}
    }
)
```

### **For Developers**

```python
# Import tool registry
from tools.registry import ToolRegistry

# Initialize
registry = ToolRegistry()

# Execute tool
result = registry.execute_tool(
    "supabase_query",
    table="users",
    select="*"
)
```

---

## 📁 **Folder Structure**

```
tools/
├── __init__.py              # Tool registry
├── registry.py              # Tool execution engine
├── schemas/                 # Tool schemas (MCP format)
│   ├── supabase_tools.json
│   ├── cloudconvert_tools.json
│   ├── assemblyai_tools.json
│   ├── ngrok_tools.json
│   ├── cloudflare_tools.json
│   ├── woocommerce_tools.json
│   ├── github_tools.json
│   └── gsheets_tools.json
├── implementations/         # Tool implementations
│   ├── supabase.py
│   ├── cloudconvert.py
│   ├── assemblyai.py
│   ├── ngrok.py
│   ├── cloudflare.py
│   ├── woocommerce.py
│   ├── github.py
│   └── gsheets.py
└── README.md               # This file
```

---

## 🔧 **Installation**

```bash
cd AI_agents/tools
pip install -r requirements.txt
```

---

## 📚 **Documentation**

- **Tool Registry**: See `TOOL_REGISTRY.md`
- **MCP Format**: See `MCP_SPECIFICATION.md`
- **Examples**: See `examples/` folder
- **Testing**: See `TESTING_GUIDE.md`

---

## ✅ **Status**

| Platform | Tools Created | Status |
|----------|---------------|--------|
| Supabase | 6 tools | ✅ Ready |
| CloudConvert | 4 tools | ✅ Ready |
| AssemblyAI | 4 tools | ✅ Ready |
| Ngrok | 4 tools | ✅ Ready |
| Cloudflare | 4 tools | ✅ Ready |
| WooCommerce | 4 tools | ✅ Ready |
| GitHub | 4 tools | ✅ Ready |
| Google Sheets | 4 tools | ✅ Ready |

**Total: 34 tools across 8 platforms**

---

## 🎯 **Use Cases**

### **For Support AI**
- Query database to troubleshoot user issues
- Check Worker logs when errors occur
- Transcribe support calls automatically
- Convert file formats for customers

### **For Development AI**
- Deploy Workers to production
- Create GitHub PRs with fixes
- Update database schemas
- Test webhook integrations

### **For Operations AI**
- Monitor service health
- Generate reports from databases
- Process bulk file conversions
- Manage e-commerce orders

---

**Ready to empower AI copilots with platform access! 🚀**
