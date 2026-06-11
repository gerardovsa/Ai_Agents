# 🤖 AI_agents - Universal AI Integration Platform

> **Empowering humans with AI-powered multi-platform orchestration**  
> Connect, automate, and amplify your business workflows across 20+ platforms through intelligent AI agents.

---

## 🎯 What is AI_agents?

**AI_agents** is an enterprise-grade **AI integration hub** that serves as the central nervous system for modern businesses. It bridges the gap between your core productivity platforms (Microsoft 365, Google Workspace) and the dozens of specialized tools your business relies on daily.

### **The Vision: Human Conductors + AI Semi-Conductors**

```
👤 Human = Conductor
   ├─ Strategic thinking
   ├─ Decision making
   └─ Creative direction

🤖 AI Agents = Semi-Conductors
   ├─ Raw processing power
   ├─ Multi-platform data flow
   ├─ Automated execution
   └─ Pattern recognition
```

**Humans conduct the orchestra, AI agents provide the computational muscle.**

---

## 🏗️ Architecture Overview

### **Central Hub Design**

```
┌─────────────────────────────────────────────────────────────────┐
│                       AI_agents Platform                         │
│                  (Universal Integration Hub)                     │
│                                                                   │
│  📊 584 Tools across 20+ Platforms                               │
│  🔐 OAuth Integration (M365 + Google)                            │
│  🧵 Multi-Agent Orchestration                                    │
│  📁 Document Processing (PDFs, Images, Spreadsheets)             │
│  ⚡ Real-time Streaming                                          │
│  💾 Session Persistence                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↕️
        ┌──────────────────────┴──────────────────────┐
        │                                              │
   ┌────▼─────┐                                  ┌────▼─────┐
   │ M365     │                                  │ Google   │
   │ OAuth    │                                  │ OAuth    │
   │          │                                  │          │
   │ • Outlook│                                  │ • Gmail  │
   │ • OneDrive│                                 │ • Drive  │
   │ • Teams  │                                  │ • Calendar│
   │ • ToDo   │                                  │ • Tasks  │
   └────┬─────┘                                  └────┬─────┘
        │                                              │
        └──────────────────┬───────────────────────────┘
                           │
        ┌──────────────────▼──────────────────────┐
        │   User's Daily Work Hub                 │
        │   (Core Productivity Platforms)         │
        └──────────────────┬──────────────────────┘
                           │
        ┌──────────────────▼──────────────────────┐
        │   20+ Integrated Platforms               │
        │                                          │
        │   Communication:                         │
        │   • Slack        • Discord               │
        │   • Microsoft Teams                      │
        │                                          │
        │   Project Management:                    │
        │   • Asana        • Trello                │
        │   • Monday.com   • Jira                  │
        │   • ClickUp      • Notion                │
        │                                          │
        │   Business Operations:                   │
        │   • Salesforce   • HubSpot               │
        │   • QuickBooks   • Xero                  │
        │   • Stripe       • PayPal                │
        │                                          │
        │   Development:                           │
        │   • GitHub       • GitLab                │
        │   • Bitbucket                            │
        │                                          │
        │   Cloud Services:                        │
        │   • AWS          • Azure                 │
        │   • Google Cloud Run                     │
        └──────────────────────────────────────────┘
```

---

## 🌟 Key Features

### **1. Multi-Platform Tool Orchestration**
- **584 tools** across **20+ platforms**
- Intelligent tool selection via AI reasoning
- Cross-platform workflow automation
- Credential injection at runtime

### **2. OAuth-Based Authentication**
- **Microsoft 365** as primary auth provider
- **Google Workspace** as alternative auth provider
- Per-user credential management
- Secure token storage and refresh

### **3. Synergy UI - Task Orchestration Hub** 🎯
The **Synergy UI** is the visual command center that unifies task management across platforms:

```
┌─────────────────────────────────────────────────────────────┐
│                       SYNERGY UI                             │
│         Unified Task Management & Collaboration              │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼─────┐      ┌─────▼──────┐     ┌─────▼──────┐
   │ Kanban   │      │ M365 ToDo  │     │ G Tasks    │
   │ Boards   │      │ Lists      │     │ Lists      │
   └──────────┘      └────────────┘     └────────────┘
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
                ┌───────────▼────────────┐
                │   AI Agents Layer      │
                │   • Task creation      │
                │   • Status sync        │
                │   • Priority updates   │
                │   • Deadline tracking  │
                │   • Cross-platform     │
                │     coordination       │
                └────────────────────────┘
```

**Synergy UI Capabilities:**
- **Unified View**: See tasks from Kanban, M365 ToDo, and Google Tasks in one place
- **AI-Powered Sync**: AI agents automatically sync task status across platforms
- **Intelligent Routing**: Create tasks in the right platform based on context
- **Collaboration Bridge**: Share tasks between M365 and Google users seamlessly
- **Workflow Automation**: "When Asana task completes → update M365 ToDo → notify in Slack"

**Example Workflow:**
```
User: "Create a task for next week's client presentation"

AI Agent (via Synergy UI):
1. Analyzes user's primary platform (M365 or Google)
2. Creates task in native platform (M365 ToDo or Google Tasks)
3. Syncs to Kanban board for team visibility
4. Adds to Google Calendar for scheduling
5. Posts reminder in Slack channel
6. Updates Salesforce opportunity stage
```


### **4. Multiple AI Agents**
- **Data Processing Agents**: Handle document analysis, extraction, transformation
- **Workflow Automation Agents**: Execute multi-step cross-platform workflows
- **Integration Agents**: Sync data between platforms in real-time
- **Analysis Agents**: Generate insights from cross-platform data

### **5. Document Processing**
- **PDF Parsing**: Extract structured data from invoices, contracts, reports
- **Image Analysis**: OCR, receipt processing, diagram understanding
- **Spreadsheet Processing**: Data transformation, validation, enrichment
- **Document Generation**: Create reports, summaries, presentations

### **6. Real-Time Streaming (SSE)**
- Live progress updates for long-running workflows
- Multi-turn conversation streaming
- Tool execution visibility
- Error notifications

### **7. Session Persistence**
- Resume workflows after disconnection
- Multi-day conversation history
- Audit trail for compliance
- Team collaboration on sessions

---

## � Getting Started

### **Prerequisites**
- Python 3.9+
- Microsoft 365 account (for OAuth)
- Google Workspace account (optional, alternative OAuth)
- Platform API keys (Slack, Asana, etc.)

### **Installation**

```powershell
# Clone repository
git clone https://github.com/yourusername/AI_agents.git
cd AI_agents

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config.example.py config.py
# Edit config.py with your API keys

# Initialize database
python scripts/setup/setup_master_account.py
```

### **Start the Platform**

```powershell
# Start Flask backend (port 5001)
BISTART

# Or manually
cd AI_infrastructure
python flask_app.py
```

### **Test with CLI**

```powershell
# Talk to AI agent from any directory
CHAT List my Gmail messages
CHAT Create a task in Microsoft ToDo
CHAT "Sync Asana tasks to Google Calendar"
```

---

## 📊 Real-World Use Cases

### **Use Case 1: Multi-Platform Data Sync**
**Scenario**: Marketing team needs to sync campaign data across platforms

```
User Request: "Sync all new leads from Salesforce to Google Sheets, 
               create tasks in Asana, notify team in Slack"

AI Agent Workflow:
1. Query Salesforce for new leads (salesforce_query_records)
2. Transform data and append to Google Sheets (google_sheets_append_rows)
3. Create Asana task for each lead (asana_create_task)
4. Post summary to Slack channel (slack_post_message)
5. Update M365 ToDo with follow-up tasks (microsoft_todo_create_task)

Result: 47 leads synced, 47 tasks created, team notified
Time: 3 minutes (vs 2+ hours manual)
```

### **Use Case 2: Invoice Processing Pipeline**
**Scenario**: Accounting team processes vendor invoices

```
User Upload: 20 invoice PDFs

AI Agent Workflow:
1. Extract data from PDFs using vision (Claude 4.5 vision)
2. Validate against Salesforce records (salesforce_query)
3. Create QuickBooks invoices (quickbooks_create_invoice)
4. Generate summary in Google Sheets (google_sheets_create_spreadsheet)
5. Email report via Outlook (microsoft_mail_send)
6. Archive PDFs to OneDrive (microsoft_onedrive_upload)

Result: 20 invoices processed, categorized, archived
Time: 10 minutes (vs 4+ hours manual)
Accuracy: 98% (with AI review)
```

### **Use Case 3: Customer Support Automation**
**Scenario**: Support team handles 100+ daily tickets

```
User Request: "Process today's support tickets from Gmail, 
               categorize, assign to team, update Salesforce"

AI Agent Workflow:
1. List unread Gmail messages in support inbox (gmail_list_messages)
2. Analyze content for category/priority (AI reasoning)
3. Create Asana tasks with assignments (asana_create_task)
4. Update Salesforce cases (salesforce_update_record)
5. Post to Slack for urgent issues (slack_post_message)
6. Sync to M365 ToDo for assigned users (microsoft_todo_create_task)

Result: 127 tickets processed, 127 tasks created, 23 urgent flagged
Time: 5 minutes (vs 3+ hours manual)
Team Capacity: Increased 80%
```

### **Use Case 4: Project Status Reporting**
**Scenario**: Weekly project status report across multiple platforms

```
User Request: "Generate weekly project status report"

AI Agent Workflow:
1. Gather data from Asana (task completion %)
2. Pull GitHub commits and PRs (github_list_commits)
3. Query Salesforce opportunities (salesforce_query)
4. Analyze Google Sheets budget (google_sheets_get_values)
5. Generate summary document (AI synthesis)
6. Create Google Slides presentation (google_slides_create)
7. Email to stakeholders via Outlook (microsoft_mail_send)
8. Post to Teams channel (microsoft_teams_post_message)

Result: Comprehensive report across 4 platforms
Time: 8 minutes (vs 6+ hours manual)
Insights: AI-identified 3 blockers, 2 risks, 5 wins
```

---

## 🔧 Architecture Details

### **V4 Modular System**

The platform is built on a **modular architecture** with 21 components:

```
AI_infrastructure/
├── routes/
│   └── agent_routes_v4.py          # Flask endpoints (sync + async)
│
├── core/  (10 modules)
│   ├── tool_executor.py            # Execute 584 tools
│   ├── tool_processor.py           # Process tool_use blocks
│   ├── conversation_manager.py     # Orchestrate multi-turn
│   ├── session_handler.py          # Session CRUD
│   ├── response_serializer.py      # Format responses
│   ├── unified_session_manager.py  # SQLite + cache
│   ├── agent_state_manager.py      # Queue + locks
│   ├── agent_worker.py             # Background threads
│   ├── session_persistence.py      # Load/save conversations
│   └── unified_ai_client.py        # Anthropic API wrapper
│
├── builders/  (4 modules)
│   ├── user_profile_builder.py     # Fetch user context
│   ├── system_prompt_builder.py    # Build AI prompt
│   ├── tool_schema_converter.py    # Format tool schemas
│   └── credential_fetcher.py       # OAuth credentials
│
├── meta_tools/  (4 modules)
│   ├── platform_tools_lister.py    # Discover tools
│   ├── platform_guide_provider.py  # Platform guides
│   ├── workflow_instructor.py      # Workflow patterns
│   └── smart_tool_instructor.py    # Smart tool usage
│
└── utils/  (7 modules)
    ├── logger.py                   # Comprehensive logging
    ├── error_handler.py            # Error recovery
    ├── validators.py               # Input validation
    ├── formatters.py               # Response formatting
    ├── file_encoding.py            # Base64, file validation
    └── response_helpers.py         # HTTP response helpers
```

### **Dual-Mode Operation**

**Synchronous Mode**: Fast, direct response
```
POST /api/agent/v4/chat
{
  "message": "List my Gmail messages",
  "user_id": 1
}

Response (10-30 seconds):
{
  "response": "You have 15 unread messages...",
  "tools_used": ["gmail_list_messages"],
  "session_id": "abc123"
}
```

**Asynchronous Mode**: Background processing + streaming
```
POST /api/agent/v4/chat/async/start
FormData: 
  - message: "Process these invoices"
  - files: [invoice1.pdf, invoice2.pdf, ...]
  - user_id: 1

Response (50ms):
{
  "success": true,
  "session_id": "def456",
  "status": "processing"
}

GET /api/agent/v4/chat/async/stream/def456
SSE Stream:
  data: {"type": "thinking", "content": "Analyzing invoice 1..."}
  data: {"type": "tool_use", "tool_name": "quickbooks_create_invoice"}
  data: {"type": "tool_result", "success": true, "output": {...}}
  data: {"type": "complete", "result": "20 invoices processed"}
```

---

## 🎛️ Configuration

### **Environment Variables**

```bash
# AI Provider Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-secret
MICROSOFT_TENANT_ID=common

# Google OAuth (uses service account)
# Place service-account.json in project root

# Database
# Automatically created in AI_infrastructure/data/
```

### **User Setup**

```powershell
# Add your user account
python scripts/setup/setup_master_account.py

# Link Microsoft 365
python scripts/setup/setup_microsoft_login.py

# Verify credentials
python check_users_and_credentials.py
```

---

## 📡 API Reference

### **Endpoints**

#### **Synchronous Chat**
```http
POST /api/agent/v4/chat
Content-Type: application/json

{
  "message": "Your request",
  "session_id": "uuid (optional)",
  "user_id": 1
}
```

#### **Async Chat Start**
```http
POST /api/agent/v4/chat/async/start
Content-Type: application/json OR multipart/form-data

# Text only:
{
  "message": "Your request",
  "user_id": 1
}

# With files:
FormData:
  - message: "Process these"
  - user_id: 1
  - files[]: file1.pdf
  - files[]: file2.pdf
```

#### **Async Chat Stream**
```http
GET /api/agent/v4/chat/async/stream/<session_id>

Response: text/event-stream
  - thinking_block
  - tool_use
  - tool_result
  - text_block
  - complete
  - error
```

#### **Session Retrieval**
```http
GET /api/agent/v4/session/<session_id>

Response:
{
  "success": true,
  "session": {
    "session_id": "...",
    "conversation": [...],
    "created_at": "...",
    "updated_at": "..."
  }
}
```

---

## 🧪 Testing

### **Run Tests**

```powershell
# Test tool registry
python -c "from tools.registry import ToolRegistry; r = ToolRegistry(); print(f'{len(r.tools)} tools')"

# Test V3 system
python test_v3_request.py

# Test specific module
pytest tests/test_tool_executor.py -v
```

### **CLI Testing**

```powershell
# Start server
BISTART

# Wait for startup (10-15 seconds)
Start-Sleep -Seconds 12

# Test chat
CHAT List my Gmail messages
CHAT "Create a Google Doc titled 'Test Document'"
CHAT Send an email to john@example.com
```

---

## � Performance & Scalability

### **Current Metrics**
- **Tools**: 584 across 20+ platforms
- **Concurrent Users**: 50+ supported
- **Request Latency**: 
  - Sync: 10-120 seconds (blocking)
  - Async: <100ms (non-blocking)
- **Session Persistence**: SQLite + in-memory cache
- **Tool Execution**: ~2-5 seconds per tool
- **Multi-turn Loops**: Max 20 turns per conversation

### **Production Deployment**
- **Render.com**: Automatic deployment via GitHub
- **Docker**: Container support for local testing
- **Database**: SQLite (development), PostgreSQL (production option)
- **Logging**: Comprehensive logging to files + console
- **Monitoring**: Health check endpoints

---

## 🛠️ Development

### **Project Structure**

```
AI_agents/
├── AI_infrastructure/         # Flask backend
│   ├── routes/               # API endpoints
│   ├── core/                 # Business logic
│   ├── builders/             # Data preparation
│   ├── meta_tools/           # Tool discovery
│   └── utils/                # Utilities
│
├── tools/                    # Tool implementations
│   ├── schemas/              # Tool definitions (JSON)
│   └── implementations/      # Python implementations
│
├── google_workspace/         # Google API integrations
├── Microsoft_365_Connection/ # M365 API integrations
│
├── scripts/                  # Utility scripts
│   ├── startup/              # BISTART, CHAT
│   ├── setup/                # Setup scripts
│   ├── testing/              # Test scripts
│   └── maintenance/          # Cleanup scripts
│
├── docs/                     # Documentation
├── logs/                     # Application logs
└── data/                     # SQLite databases
```

### **Adding New Tools**

1. **Create Tool Schema** (`tools/schemas/my_platform_tools.json`):
```json
{
  "tools": [
    {
      "name": "my_platform_action",
      "description": "What this tool does",
      "parameters": {
        "type": "object",
        "properties": {
          "param1": {
            "type": "string",
            "description": "Parameter description"
          }
        },
        "required": ["param1"]
      }
    }
  ]
}
```

2. **Create Implementation** (`tools/implementations/my_platform.py`):
```python
class MyPlatformTools:
    def __init__(self, **kwargs):
        self.credentials = None
        
    def my_platform_action(self, param1, **kwargs):
        """Execute action on My Platform"""
        access_token = kwargs.get('access_token')
        # Implementation...
        return {"success": True, "result": "..."}
```

3. **Restart Server** - Tools auto-load on startup

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### **Key Areas for Contribution**
- New platform integrations
- Tool improvements
- Documentation
- Bug fixes
- Performance optimization

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic** - Claude 4.5 Sonnet AI model
- **Microsoft** - Microsoft 365 APIs
- **Google** - Google Workspace APIs
- **Open Source Community** - For countless libraries and tools

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/AI_agents/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/AI_agents/discussions)
- **Email**: support@yourdomain.com

---

## 🗺️ Roadmap

### **Q1 2025**
- V4 Modular Architecture
- Dual-mode operation (sync + async)
- 584 tools across 20+ platforms
- 🔄 Synergy UI (in progress)

### **Q2 2025**
- [ ] Web dashboard for users
- [ ] Team collaboration features
- [ ] Advanced analytics
- [ ] Mobile app (iOS/Android)

### **Q3 2025**
- [ ] Enterprise SSO
- [ ] Custom workflow builder
- [ ] Webhook integrations
- [ ] API rate limit optimization

### **Q4 2025**
- [ ] AI agent marketplace
- [ ] Custom AI model training
- [ ] Advanced security features
- [ ] Compliance certifications

---

## 💡 Philosophy

**"Humans conduct, AI executes."**

AI_agents doesn't replace human intelligence—it amplifies it. By handling the computational heavy lifting of multi-platform integration, data processing, and workflow automation, we free humans to focus on what they do best: strategic thinking, creative problem-solving, and meaningful work.

---

**Built with ❤️ by humans, powered by 🤖 AI**

        
    def analyze_with_ai(self, content):
        # Use AI for analysis
        pass
```

### **Pattern 3: Multi-Provider Support**
```python
from config import get_available_models

class MultiProviderClient:
    def list_models(self):
        return get_available_models('anthropic')
        # Returns: ['claude-sonnet-4-5-20250929', ...]
```

---

## 📚 **Documentation**

- **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)** - Complete guide for creating new integrations
- **[ASSESSMENT_SUMMARY.md](./ASSESSMENT_SUMMARY.md)** - Assessment of root-level scripts
- **Platform-specific READMEs** - In each platform folder

---

## 🧪 **Testing**

Each integration provides test scripts:

```bash
# Test Supabase connection
cd Supabase
python test_supabase_connection.py

# Test Render API
cd Render_backend
python test_render_connection.py

# Test Microsoft 365
cd Microsoft_365_Connection
python test_email_integration.py
```

---

## 🛠️ **Common Operations**

### **Add New API Key**
```bash
# 1. Add to .env
echo "NEW_API_KEY=sk-abc123..." >> .env

# 2. Reference in code
api_key = os.getenv('NEW_API_KEY')
```

### **Switch AI Model**
```python
from config import AI_PROVIDERS

# Change default model
os.environ['AI_MODEL'] = 'claude-sonnet-4-5-20250929'
```

### **Check Model Capabilities**
```python
from config import get_models_by_capability

# Find all models with web search
models = get_models_by_capability('web_search')
print(models)
# {'anthropic': ['claude-sonnet-4-5-20250929', 'claude-3-7-sonnet-20250219', ...]}
```

---

## ⚠️ **Known Issues**

1. **Fixed**: `auth.py` import issue resolved
2. **Fixed**: Supabase client now uses `config.py`
3. ⚠️ **Todo**: Update `.env` with actual Supabase credentials (currently placeholders)

---

## 🚀 **Next Steps**

1. **Review** existing integrations for patterns
2. **Read** [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for creating new integrations
3. **Test** existing integrations with your credentials
4. **Create** new integration following the template

---

## 📞 **Support**

- Check platform-specific README files for detailed usage
- See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for best practices
- Review [ASSESSMENT_SUMMARY.md](./ASSESSMENT_SUMMARY.md) for architecture details

---

**Last Updated**: January 2025  
**Maintained By**: Gerardo Poli  
**Total Integrations**: 8 platforms + shared utilities  
**New Services**: AssemblyAI, CloudConvert, Ngrok (Oct 2025)
