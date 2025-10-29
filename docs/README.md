# 📚 AI Agents Platform - Documentation Index

**Last Updated:** October 29, 2025  
**Version:** 2.0.0  
**Status:** ✅ Active Development

---

## 🎯 Overview

The AI Agents Platform is a comprehensive multi-agent AI system with 281+ tools across 19+ platforms, integrated with Google Workspace, Microsoft 365, WooCommerce, and more.

**Core Capabilities:**
- Multi-agent conversation orchestration
- Real-time tool execution across platforms
- Kanban-based task management
- User authentication & account linking
- Thread persistence & session management

---

## 📖 Documentation Structure

### 🔧 Feature Documentation
Complete guides for each major system component:

1. **[Agent System](features/AGENT_SYSTEM_COMPLETE.md)** - AI agent orchestration, streaming, lifecycle
2. **[Tool Platform](features/TOOL_PLATFORM_COMPLETE.md)** - 281+ tools across 19+ platforms
3. **[Kanban Integration](features/KANBAN_INTEGRATION_COMPLETE.md)** - Task management with AI agents
4. **[Flask Routes](features/FLASK_ROUTES_COMPLETE.md)** - API architecture & endpoints
5. **[UI Interfaces](features/UI_INTERFACES_COMPLETE.md)** - Frontend components & integration

### 🔌 API Documentation
API references and integration guides:

- **[API Reference](api/API_REFERENCE.md)** - Complete endpoint documentation
- **[Authentication Guide](api/AUTHENTICATION.md)** - OAuth, user auth, account linking
- **[WebSocket Protocol](api/WEBSOCKET.md)** - Real-time communication

### 📦 Archive
Historical implementation notes and deprecated code:

- **[Archive Index](archive/README.md)** - Legacy documentation reference

---

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.11+
python --version

# Install dependencies
pip install -r requirements.txt
```

### Start the Platform
```powershell
# Start Flask server (port 4000)
cd C:\Users\gpoli\GIT\AI_agents
BISTART

# Wait 10-15 seconds for tools to load
Start-Sleep -Seconds 12

# Test with CHAT command (from any directory)
CHAT What tools are available?
```

### Verify Setup
```bash
# Check health
curl http://localhost:4000/health

# List available tools
curl http://localhost:4000/api/agent/tools
```

---

## 📊 Platform Statistics

| Metric | Count |
|--------|-------|
| **Total Tools** | 281+ |
| **Platforms** | 19+ |
| **API Endpoints** | 50+ |
| **UI Interfaces** | 6 |
| **Core Modules** | 12 |

**Supported Platforms:**
- **AI Models:** OpenAI, Anthropic, DeepSeek
- **Communication:** Gmail, Slack, Twilio, Microsoft Outlook
- **E-Commerce:** WooCommerce, Stripe, PayPal
- **Google Workspace:** Docs, Sheets, Forms, Drive, Calendar, Tasks, Slides, Meet
- **Microsoft 365:** Word, Excel, OneDrive, Teams, Outlook, OneNote, SharePoint
- **Infrastructure:** Supabase, GitHub, CloudFlare

---

## 🏗️ Architecture Overview

```
AI_agents/
├── AI_infrastructure/         # Core Flask backend
│   ├── flask_app.py          # Main Flask application
│   ├── core/                 # Core managers & clients
│   ├── routes/               # API blueprint routes
│   └── utils/                # Shared utilities
├── tools/                    # 281+ platform tools
│   ├── registry.py           # Tool discovery system
│   └── implementations/      # Platform-specific tools
├── UI/                       # Frontend interfaces
│   ├── business-ai-platform-v2.html
│   ├── triple_agent.html
│   └── visualisation_engine/
├── data/                     # Databases & storage
└── docs/                     # This documentation
```

---

## 🔑 Key Concepts

### 1. **Agent System**
Multi-agent orchestration with streaming responses, tool execution, and state management.

### 2. **Tool Registry**
Centralized discovery and execution of 281+ tools across platforms.

### 3. **Session Management**
Persistent conversation threads with SQLite storage.

### 4. **Kanban Integration**
Bridge between task management and AI agent execution.

### 5. **Authentication**
Multi-provider OAuth (Google, Microsoft) + user session management.

---

## 📝 Documentation Standards

### Update Guidelines

When implementing features or fixes:

1. **Read existing `_COMPLETE.md` first**
2. **Update relevant sections** (don't create new files)
3. **Follow the template structure** (see any `_COMPLETE.md`)
4. **Update version & date** at bottom of file
5. **Test code examples** before documenting

### Version Increment Rules
- **Major (X.0.0)**: Breaking changes, architectural rewrites
- **Minor (x.X.0)**: New features, non-breaking additions
- **Patch (x.x.X)**: Bug fixes, documentation updates

---

## 🆘 Troubleshooting

### Common Issues

**Server won't start:**
```powershell
# Check if port 4000 is in use
netstat -ano | findstr :4000

# Kill process if needed
taskkill /F /PID <process_id>

# Restart
BISTART
```

**Tools not loading:**
```python
# Check tool registry
from tools.registry import ToolRegistry
registry = ToolRegistry()
print(f"Loaded {len(registry.tools)} tools")
```

**Database errors:**
```bash
# Check database schema
python check_db_schema.py

# Run migrations if needed
python run_migration.py
```

---

## 🤝 Contributing

### Making Changes

1. **Update code** in appropriate module
2. **Update documentation** in `docs/features/`
3. **Test thoroughly** with relevant UI
4. **Update version numbers**
5. **Document in CHANGELOG.md** (root level)

### Code Standards

- Follow existing patterns in codebase
- Use type hints where applicable
- Add docstrings to all functions
- Include logging with emoji prefixes (🔧, ✅, ❌)

---

## 📞 Support

For issues or questions:
1. Check relevant `_COMPLETE.md` file
2. Review troubleshooting sections
3. Check terminal output for errors
4. Review Flask logs in console

---

## 🗺️ Roadmap

**Current Focus (v2.0):**
- [ ] Documentation consolidation
- [ ] Code cleanup (remove test/temp functions)
- [ ] Folder reorganization
- [ ] API standardization

**Upcoming (v2.1):**
- [ ] WebSocket real-time updates
- [ ] Enhanced visualization engine
- [ ] Performance optimizations
- [ ] Extended test coverage

**Future (v3.0):**
- [ ] Multi-user deployment
- [ ] Role-based permissions
- [ ] API rate limiting
- [ ] Monitoring & analytics

---

**Documentation maintained by:** Development Team  
**Last reviewed:** October 29, 2025  
**Next review:** November 15, 2025
