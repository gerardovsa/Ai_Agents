# Pre-Flight Checklist Before Testing AI Agent

## ✅ Smoke Test Results
- [x] Module Plugin Loader - Discovered 7 calculator tools
- [x] Module Blueprint Loader - Registered 11 Flask routes  
- [x] Registry V3 Integration - 607 total tools loaded
- [x] Tool Accessibility - All calculator tools accessible

## 🚀 Server Startup

### Step 1: Kill any existing Python processes
```powershell
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
```

### Step 2: Start Flask app
```powershell
BISTART
```

Expected output:
```
✅ Loaded 607 tools across platforms
✅ Loaded 1 module blueprints from UI/external/modules
✅ Flask app running on port 5001
```

### Step 3: Verify server is running
```powershell
curl http://localhost:5001/api/quote-calculator/health
```

Expected response:
```json
{
  "status": "healthy",
  "module": "quote-calculator",
  "endpoints": [...]
}
```

## 🤖 AI Agent Test Commands

After server is running, test AI agent with:

```bash
CHAT "Calculate a quote for 1000 business cards, double-sided, premium stock"
```

Expected behavior:
1. AI discovers `calculate_business_cards` tool
2. AI calls tool with parameters
3. AI returns quote result

### Alternative test commands:
```bash
CHAT "What paper stocks do we have available?"
CHAT "I need a quote for 5000 A4 flyers on 150GSM Gloss"
CHAT "Calculate the cost of a 16-page booklet, 500 copies"
```

## 📊 What's Being Tested

### Module Plugin System (AI Tools)
- Module discovery: `UI/external/modules/quote-calculator/schema/`
- Tool loading: 7 calculator tools automatically loaded
- Registry integration: Tools appear in Registry V3 alongside 600 other tools

### Module Blueprint System (Flask Routes)
- Blueprint discovery: `UI/external/modules/quote-calculator/routes/`
- Route registration: 11 endpoints automatically registered
- Flask integration: Routes available at `/api/quote-calculator/*`

### End-to-End Flow
```
User: "Calculate quote for 1000 business cards"
  ↓
AI Agent (Claude)
  ↓
Registry V3 (discovers calculate_business_cards tool)
  ↓
Flask Route: /api/tools/execute
  ↓
Module Blueprint: quote_calculator.calculate_business_cards_route()
  ↓
calculator_wrapper.py: calculate_business_cards()
  ↓
Database calculation
  ↓
Return: Quote result to user
```

## ⚠️ Known Issues

### ImportError: No module named 'inhouse_modules.calculators'
- This is expected if G_Folder is not connected
- Tool wrappers will return errors gracefully
- AI can still discover and attempt to use tools
- Once `inhouse_modules` is properly configured, calculations will work

### Workaround for testing without G_Folder:
The tools are discoverable, but will return errors when executed. This is fine for testing:
1. AI can discover tools ✅
2. AI can describe tool capabilities ✅
3. Tool execution will gracefully fail ⚠️

## 📝 Test Workflow

1. **Server startup** (you will do this)
2. **Verify health check** (confirm server is running)
3. **AI agent test** (verify AI can discover and call tools)
4. **Check logs** (verify module loading messages)

## 🎯 Success Criteria

✅ Server starts without errors  
✅ Smoke test shows 607 tools (594 + 7 + 6 others)  
✅ Module blueprints registered (11 routes)  
✅ AI agent discovers calculator tools  
✅ AI can describe tool parameters  
✅ Tools appear in available tools list  

## 🔍 Debugging Commands

### Check if module tools are loaded:
```powershell
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print([t for t in r.tools.keys() if 'calculate_business' in t])"
```

### Check Flask routes:
```powershell
curl http://localhost:5001/api/quote-calculator/health
```

### Check module discovery:
```powershell
python tools/plugins/module_plugin_loader.py
```

---

**Ready to start server? Run:**
```powershell
BISTART
```

**Once running, test AI with:**
```powershell
CHAT "Calculate quote for 1000 business cards"
```
