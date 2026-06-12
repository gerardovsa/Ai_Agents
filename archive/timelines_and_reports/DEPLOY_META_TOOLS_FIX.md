# Deploy Meta-Tools Fix - Quick Checklist

**Date:** January 21, 2026  
**Fix:** System prompt updated to teach AI correct meta-tool usage

---

## ✅ Pre-Deployment Checklist

- [x] System prompt updated (`AI_infrastructure/prompts/tool_usage_system_prompt.md`)
- [x] All examples fixed to use `execute_tool()` wrapper
- [x] Prominent warning section added
- [x] Documentation created

---

## 🚀 Deployment Steps

### Step 1: Restart Flask Server (REQUIRED)
```powershell
# In terminal where Flask is running:
# Press Ctrl+C to stop

# Then restart:
cd AI_infrastructure
python flask_app.py
```

**Wait for:**
```
[OK] Tool Registry loaded - 1076 tools available
[OK] System prompt loaded from tool_usage_system_prompt.md
```

### Step 2: Clear Browser Cache (RECOMMENDED)
- Press `Ctrl+Shift+Delete` in browser
- Clear cached files
- Reload AI agent page

### Step 3: Test Meta-Tool Usage

**Test 1: Search for Tools**
```
Message: "Find tools to read Outlook emails"
Expected: AI discovers microsoft_outlook_read_message tool
```

**Test 2: List Platform Tools**
```
Message: "What Gmail tools are available?"
Expected: AI lists 42+ Gmail tools
```

**Test 3: Get Tool Schema**
```
Message: "What parameters does gmail_send_email need?"
Expected: AI shows to, subject, body, cc, bcc parameters
```

---

## 📊 Success Indicators

### ✅ GOOD (Working Correctly)
```
[TOOLS] Executing: execute_tool with params: {'tool_name': 'search_tools', 'query': 'outlook email'}
[TOOLS] Result: {"success": true, "match_count": 18, "matches": [...]}
AI: "I found 18 Outlook email tools. Here are the main ones..."
```

### ❌ BAD (Still Broken)
```
Tool execution failed: Tool not found: search_tools
AI: "I'm sorry, I cannot search for tools..."
```

---

## 🔧 Troubleshooting

### Problem: Still getting "Tool not found" errors

**Solution 1: Verify server restarted**
```powershell
# Check if Flask process is running with NEW code
Get-Process | Where-Object {$_.ProcessName -eq "python"}

# If still running old code, force kill:
Stop-Process -Name python -Force

# Restart:
cd AI_infrastructure
python flask_app.py
```

**Solution 2: Verify prompt file loaded**
```powershell
# Check Flask logs for:
[UnifiedAIClient] ✅ Loaded system prompt: 95,138 characters

# If you see different character count, prompt didn't load!
```

**Solution 3: Hard refresh browser**
```
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

### Problem: AI still calling meta-tools directly

**Check Flask logs for:**
```
# If you see this, server is using OLD prompt:
[STREAM] System prompt complete: 35,171 characters

# Should see NEW prompt size:
[STREAM] System prompt complete: 95,138 characters (or similar)
```

**Fix:** Server didn't reload prompt file. Restart Flask.

---

## 📝 Verification Test Script

Copy this and send to the AI:

```
Test meta-tool discovery workflow:

1. Search for calendar tools
2. List all Gmail tools
3. Get schema for google_docs_create_document
4. Show me what platforms are available

For each step, tell me which meta-tool you're calling and show the result.
```

**Expected AI Response:**
```
I'll test the meta-tool discovery workflow:

1. **Searching for calendar tools:**
   [Calls: execute_tool(tool_name="search_tools", query="calendar")]
   Found 29 calendar tools across Google Calendar and Microsoft Calendar...

2. **Listing Gmail tools:**
   [Calls: execute_tool(tool_name="list_platform_tools", platform="gmail")]
   Gmail has 42 tools available: gmail_send_email, gmail_list_messages...

3. **Getting schema for google_docs_create_document:**
   [Calls: execute_tool(tool_name="get_tool_schema", tool_name_param="google_docs_create_document")]
   Parameters: title (required), content (optional), folder_id (optional)...

4. **Available platforms:**
   [Calls: execute_tool(tool_name="list_available_platforms")]
   Found 74 platforms: gmail, google_docs, microsoft_outlook...
```

---

## ⏱️ Estimated Time

- **Server Restart:** 30 seconds
- **Browser Cache Clear:** 10 seconds
- **Testing:** 2-3 minutes
- **Total:** ~5 minutes

---

## 🎯 Quick Reference

**The Fix:**
- ❌ OLD: `search_tools("keyword")`
- ✅ NEW: `execute_tool(tool_name="search_tools", query="keyword")`

**What Changed:**
- System prompt now teaches AI to use execute_tool() wrapper for meta-tools
- All examples updated throughout 95KB prompt file
- Prominent warning section added

**What to Watch:**
- No more "Tool not found" errors for meta-tools
- AI successfully discovers tools when asked
- AI can list platforms and get schemas

---

**Ready to Deploy?**
1. Stop Flask server (Ctrl+C)
2. Restart: `python flask_app.py`
3. Test with verification script above
4. 🎉 Meta-tools should work!

---

**Last Updated:** January 21, 2026  
**Created By:** GitHub Copilot  
**Issue Tracking:** META_TOOLS_SYSTEM_PROMPT_FIX_JAN21_2026.md
