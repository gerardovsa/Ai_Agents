# 🚀 Tool Embeddings - Smart Caching System

## What's Happening

Your system generates **semantic embeddings** for all 1118 tools at startup to enable intelligent tool discovery. This process:

1. **Loads all tool definitions** from the registry
2. **Generates 384-dimensional vector embeddings** using sentence-transformers
3. **Stores embeddings in Supabase** for persistence
4. **Loads from cache on subsequent startups** (if tools haven't changed)

## Current Behavior

The system is **regenerating every startup** because:
- The version hash keeps changing (tools being modified)
- OR the cache doesn't exist in Supabase yet
- OR there's a mismatch between current tools and cached tools

## The Solution

### ✅ **Already Implemented** - Smart Caching

The system **already has smart caching**! It:
- Calculates a SHA256 hash of all tool definitions
- Compares with cached version in Supabase
- Only regenerates if tools changed
- Falls back to in-memory if database unavailable

### 🔍 **New Tools for You**

#### 1. **Debug Version Hash** (Find what's changing)
```powershell
python tools/debug_version_hash.py
```

This shows:
- Current version hash vs cached version
- Which tools were added/removed/modified
- Why regeneration is triggered

#### 2. **Force Regenerate** (Manual control)
```powershell
python tools/force_regenerate_embeddings.py
```

Use this when:
- You've added new tools
- You want to refresh the cache
- Cache is corrupted

#### 3. **Check Cache Status**
```powershell
python tools/manage_semantic_cache.py status
```

Shows cache health, version, and tool count.

## VS Code Tasks

You now have **VS Code tasks** for easy access:

1. Press `Ctrl+Shift+P`
2. Type "Run Task"
3. Choose from:
   - 🔍 **Debug Version Hash** - Find what's changing
   - 🔄 **Force Regenerate Embeddings** - Manual regeneration
   - 📊 **Check Semantic Cache Status** - Cache health check
   - 🗑️ **Invalidate Semantic Cache** - Clear cache
   - 📈 **Semantic Cache Stats** - Detailed statistics

## Expected Behavior

### **First Startup** (No cache)
```
[Persistent Semantic] 📭 No cache found in database - will generate fresh embeddings
[Persistent Semantic] 🔄 Generating embeddings for 1118 tools...
[Persistent Semantic] Stored batch 1/12
[Persistent Semantic] Stored batch 2/12
...
[Persistent Semantic] 💾 Stored 1118 embeddings to Supabase
```
**Time:** ~30-60 seconds

### **Subsequent Startups** (Cache hit)
```
[Persistent Semantic] Tool registry version: a3f8b9c2...
[Persistent Semantic] ✅ Cache is VALID! Loading 1118 embeddings from Supabase...
[Persistent Semantic] ✅ Loaded 1118 embeddings from Supabase
```
**Time:** <3 seconds ⚡

### **After Tool Changes** (Cache miss)
```
[Persistent Semantic] 🔄 Cache outdated - tools have changed!
[Persistent Semantic]    Expected: a3f8b9c2e5d7f1a4...
[Persistent Semantic]    Found:    8f9d2c1b4a6e3f5d...
[Persistent Semantic]    🔄 Will regenerate embeddings for 1118 tools
```
**Time:** ~30-60 seconds (only when needed)

## Why Is It Regenerating Every Time?

Run the debug script to find out:
```powershell
python tools/debug_version_hash.py
```

Common reasons:
1. **Tools being modified** - Registry changes on every startup
2. **No cache exists** - First run or cache was cleared
3. **Tool definitions changing** - Descriptions/platforms updated

## How to Fix

### **If tools haven't actually changed:**

1. **Check what's different:**
   ```powershell
   python tools/debug_version_hash.py
   ```

2. **Force regenerate once:**
   ```powershell
   python tools/force_regenerate_embeddings.py
   ```

3. **Restart Flask:**
   ```powershell
   cd AI_infrastructure
   python flask_app.py
   ```

4. **Verify it loads from cache:**
   Look for: `✅ Loaded 1118 embeddings from Supabase`

### **If tools ARE changing:**

This is expected! The system is doing exactly what it should - keeping embeddings up-to-date with your tool registry.

## Performance Impact

| Scenario | Time | Database Queries |
|----------|------|------------------|
| **Cache Hit** (ideal) | <3s | 2 reads |
| **Cache Miss** (regenerate) | 30-60s | 1200+ writes |

**Goal:** Cache hit rate >95%

## Database Schema

```sql
-- Tool embeddings storage
CREATE TABLE ai_infrastructure.tool_embeddings (
    tool_name TEXT PRIMARY KEY,
    embedding vector(384),        -- Sentence-transformers embedding
    tool_metadata JSONB,          -- Tool description, platform, etc.
    version_hash TEXT,            -- SHA256 of tool definitions
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cache metadata
CREATE TABLE ai_infrastructure.tool_embedding_cache (
    cache_key TEXT PRIMARY KEY,
    version_hash TEXT,            -- Current version hash
    total_tools INTEGER,          -- Tool count
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Troubleshooting

### **"Database storage failed, using in-memory only"**
- Connection to Supabase failed
- Embeddings generated but not persisted
- Will regenerate on next startup
- Check `SUPABASE_DB_URL` in `.env`

### **"Cache outdated - tools have changed"**
- This is **NORMAL** when you add/modify tools
- Embeddings will regenerate automatically
- Run `debug_version_hash.py` to see what changed

### **"No cache found in database"**
- First startup or cache was cleared
- Will generate and store embeddings
- Subsequent startups will be fast

## Best Practices

1. **Don't clear the cache unnecessarily** - It takes time to regenerate
2. **Run debug script before force regenerating** - Understand what's changing
3. **Monitor startup logs** - Look for "Cache is VALID!" message
4. **Use VS Code tasks** - Easier than typing commands

## Files Reference

| File | Purpose |
|------|---------|
| `tools/persistent_semantic_search.py` | Main caching system |
| `tools/debug_version_hash.py` | Debug tool changes |
| `tools/force_regenerate_embeddings.py` | Manual regeneration |
| `tools/manage_semantic_cache.py` | Cache management CLI |
| `.vscode/tasks.json` | VS Code task definitions |

## Next Steps

1. **Run the debug script** to see why it's regenerating:
   ```powershell
   python tools/debug_version_hash.py
   ```

2. **Check the output** - It will tell you exactly what's changing

3. **If no real changes**, force regenerate once:
   ```powershell
   python tools/force_regenerate_embeddings.py
   ```

4. **Restart Flask and verify** - Should load from cache now

---

**Questions?** Check the improved logging in Flask startup - it now shows detailed reasons for cache hits/misses.
