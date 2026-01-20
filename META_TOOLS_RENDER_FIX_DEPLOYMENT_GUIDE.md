# META-TOOLS FIX FOR RENDER PRODUCTION - January 21, 2026

## 🎯 QUICK FIX DEPLOYMENT

**What you need to do RIGHT NOW:**

1. **Set Admin API Key in Render Environment Variables**
2. **Push changes to deploy admin routes**
3. **Call cache invalidation endpoint**  
4. **Restart Render service**
5. **Verify meta-tools are available**

---

## Step 1: Set Admin API Key (Render Dashboard)

Go to: https://dashboard.render.com → Your Service → Environment

Add this environment variable:
```
ADMIN_API_KEY=your_secret_key_here_make_it_strong
```

**Example strong key:**
```
ADMIN_API_KEY=AIa-prod-cache-2026-b8f3d9e1c4a7
```

**Important:** This key protects admin endpoints from unauthorized access. Keep it secret!

---

## Step 2: Deploy Admin Routes to Render

### Option A: Push to gerardo remote (RECOMMENDED)
```powershell
# From your local AI_agents directory
cd c:\Users\gpoli\GIT\AI_Agents_V11\AI_agents

# Check current status
git status

# Add changes
git add AI_infrastructure/routes/admin_routes.py
git add AI_infrastructure/flask_app.py

# Commit
git commit -m "feat(admin): Add cache invalidation endpoints for meta-tools fix"

# Push to BOTH remotes (backup + production)
git push origin v11
git push gerardo v11:v11
```

**Render will auto-deploy in ~2-5 minutes**

### Option B: Manual Deploy on Render Dashboard
1. Go to: https://dashboard.render.com → Your Service
2. Click "Manual Deploy" → "Deploy latest commit"
3. Wait for build to complete (~2-5 minutes)

---

## Step 3: Invalidate Stale Redis Cache

Once deployment is complete, call the cache invalidation endpoint:

### Method A: Using curl (PowerShell)
```powershell
# Replace with your actual ADMIN_API_KEY and Render URL
$AdminKey = "AIa-prod-cache-2026-b8f3d9e1c4a7"
$RenderURL = "https://ai-agents-inhouse-v11-backend.onrender.com"

# Invalidate cache
curl -X POST "$RenderURL/api/admin/cache/invalidate" `
     -H "X-Admin-Key: $AdminKey"
```

### Method B: Using browser (with query param)
Open this URL in your browser (replace placeholders):
```
https://ai-agents-inhouse-v11-backend.onrender.com/api/admin/cache/invalidate?admin_key=AIa-prod-cache-2026-b8f3d9e1c4a7
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Tool registry cache invalidated",
  "action_required": "Restart Flask server to reload fresh tools"
}
```

---

## Step 4: Restart Render Service

**Go to Render Dashboard:**
1. https://dashboard.render.com → Your Service
2. Click "Manual Deploy" → "Clear build cache & deploy"  
   OR  
   Click "Settings" → "Manual Restart"

**Wait 30-60 seconds for server to restart**

---

## Step 5: Verify Meta-Tools Are Available

### Test 1: Check Cache Status
```powershell
$AdminKey = "AIa-prod-cache-2026-b8f3d9e1c4a7"
$RenderURL = "https://ai-agents-inhouse-v11-backend.onrender.com"

curl "$RenderURL/api/admin/cache/status" `
     -H "X-Admin-Key: $AdminKey"
```

**Expected Output:**
```json
{
  "success": true,
  "total_tools": 1076,
  "meta_tools": {
    "search_tools": true,
    "list_platform_tools": true,
    "list_available_platforms": true,
    "get_tool_schema": true,
    "execute_tool": true
  },
  "meta_tools_available": true,
  "redis_enabled": true
}
```

### Test 2: Use AI to Discover Tools
1. Open your Render production frontend
2. Start a conversation with any agent
3. Ask: "Find tools to read Outlook emails"
4. **Expected:** AI calls `execute_tool(tool_name="search_tools", query="outlook email")`
5. **Expected:** AI discovers `microsoft_outlook_read_message` tool
6. **NOT Expected:** "Tool not found: search_tools" error

---

## 🚨 If Meta-Tools STILL Don't Work After All Steps

### Emergency Option: Force Reload Tools from Disk

This bypasses cache and reloads directly from files:

```powershell
$AdminKey = "AIa-prod-cache-2026-b8f3d9e1c4a7"
$RenderURL = "https://ai-agents-inhouse-v11-backend.onrender.com"

curl -X POST "$RenderURL/api/admin/tools/reload" `
     -H "X-Admin-Key: $AdminKey"
```

**This will:**
1. Invalidate cache
2. Reload schemas from disk
3. Reload implementations
4. Rebuild cache with fresh data

**Expected Response:**
```json
{
  "success": true,
  "message": "Tools reloaded from disk",
  "total_tools": 1076,
  "meta_tools": {
    "search_tools": true,
    "list_platform_tools": true,
    "list_available_platforms": true,
    "get_tool_schema": true,
    "execute_tool": true
  },
  "meta_tools_available": true
}
```

---

## 📊 What Was the Root Cause?

**The Problem:**
- Render production uses Redis caching for tool registry (1-hour TTL)
- When you deployed system prompt fixes and restarted server, it loaded tools from **stale Redis cache**
- Cache contained OLD tool definitions WITHOUT meta-tools
- Local development doesn't use Redis, so it always loads fresh from files ✅

**Why Local Worked But Render Didn't:**
```
LOCAL DEV:
[REDIS] Connection failed: localhost:6379 not available
[REDIS] Falling back to in-memory storage
→ Loads fresh from tools/schemas/meta_tools.json ✅

RENDER PRODUCTION:
[CACHE] Tool registry loaded from cache in 40ms (1011 tools)
→ Loads stale 1-hour-old cache WITHOUT meta-tools ❌
```

**The Fix:**
1. Admin routes added for cache management
2. Invalidate cache API endpoint
3. Force reload from disk if needed
4. Fresh tools loaded after restart

---

## 🎯 Success Criteria

**All good if:**
1. ✅ `/api/admin/cache/status` shows `"meta_tools_available": true`
2. ✅ AI can call `execute_tool(tool_name="search_tools", ...)`
3. ✅ No more "Tool not found: search_tools" errors
4. ✅ Total tools = 1076 (not 1011 or 65)
5. ✅ System prompt shows: "Loaded system prompt: 94817 characters"

---

## 🔧 Admin Endpoints Reference

### 1. Cache Status
```
GET /api/admin/cache/status
Header: X-Admin-Key: your_secret_key
```

Returns: Tool count, meta-tools availability, Redis status

### 2. Invalidate Cache
```
POST /api/admin/cache/invalidate
Header: X-Admin-Key: your_secret_key
```

Returns: Success message, requires server restart

### 3. Reload Tools
```
POST /api/admin/tools/reload
Header: X-Admin-Key: your_secret_key
```

Returns: Tool count after reload, meta-tools status

---

## 📝 Files Modified

### New Files:
- `AI_infrastructure/routes/admin_routes.py` - Admin endpoints for cache management

### Modified Files:
- `AI_infrastructure/flask_app.py` - Added admin_bp registration

### Environment Variables:
- `ADMIN_API_KEY` - Required for admin endpoint access

---

## ✅ Testing Checklist

- [ ] ADMIN_API_KEY set in Render environment
- [ ] Admin routes deployed to Render (check logs for "admin_bp")
- [ ] Cache invalidation endpoint returns success
- [ ] Render service restarted
- [ ] Cache status shows `"meta_tools_available": true`
- [ ] AI can discover tools using meta-tools
- [ ] No more "Tool not found" errors in production

---

**Date:** January 21, 2026  
**Issue:** Meta-tools work locally but fail on Render  
**Root Cause:** Stale Redis cache with 1-hour TTL  
**Solution:** Admin endpoints for cache invalidation + force reload
