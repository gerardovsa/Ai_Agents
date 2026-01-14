# Use AI Agent's Render Tools to Fix Database

## We Have 8 Render Tools Available:

1. `render_list_services` - Find your service ID
2. `render_get_service_logs` - Check current logs for errors
3. `render_deploy_service` - Trigger new deployment
4. `render_restart_service` - Restart after database upload
5. `render_get_deploys` - Check deployment history
6. `render_get_service_metrics` - Monitor performance
7. `render_scale_service` - Scale if needed
8. `render_postgres_backup` - Backup databases

## Quick Fix Using AI Agent Chat:

### Option 1: Use CHAT Command (Easiest)

```powershell
# From any directory
CHAT "Use render_get_service_logs to check ai-agents-backend for the 'no such column' error"

CHAT "Use render_get_deploys to show recent deployments for ai-agents-backend"

# After you upload database manually via Google Drive
CHAT "Use render_restart_service to restart ai-agents-backend"
```

### Option 2: Direct Tool Execution (If you have Render API key)

Set your Render API key:
```powershell
$env:RENDER_API_KEY = "your_render_api_key_here"
```

Then use Python:
```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

# List all services
services = registry.execute_tool('render_list_services')
print(services)

# Get logs (find the service_id from list_services)
logs = registry.execute_tool(
    'render_get_service_logs',
    service_id='srv-XXXXX',  # Replace with actual ID
    tail=100,
    filter='no such column'
)
print(logs)

# Restart after database upload
result = registry.execute_tool(
    'render_restart_service',
    service_id='srv-XXXXX',  # Replace with actual ID
    wait=True
)
print(result)
```

## The Problem & Solution:

**Problem:** Render database is OLD, missing columns
- ❌ `has_microsoft_oauth` column doesn't exist
- ❌ `has_google_oauth` column doesn't exist

**Solution:** Upload working database from Google Drive

### Step-by-Step:

1. **Get Service ID:**
   ```powershell
   CHAT "List all my Render services"
   ```
   
2. **Check Current Logs:**
   ```powershell
   CHAT "Get the last 50 error logs from ai-agents-backend"
   ```

3. **Upload Database Manually:**
   - Go to: https://drive.google.com/drive/folders/1UwmYADDh6vuNKlMOlcjFog4SSwnThE-O
   - Get shareable link for `ai_infrastructure.db`
   - Extract FILE_ID from link
   - Go to Render Shell: https://dashboard.render.com → ai-agents-backend → Shell
   - Run:
   ```bash
   cd /data
   wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=FILE_ID' -O ai_infrastructure.db
   ```

4. **Restart Service Using Tool:**
   ```powershell
   CHAT "Restart ai-agents-backend service on Render"
   ```

5. **Verify It Worked:**
   ```powershell
   CHAT "Get the latest logs from ai-agents-backend and check for OAuth errors"
   ```

## Why Use AI Agent Tools Instead of Manual?

✅ **Faster** - One command instead of clicking through dashboard  
✅ **Automated** - Can script the entire process  
✅ **Better logging** - All actions logged in conversation  
✅ **Error checking** - Tools validate responses  
✅ **Repeatable** - Save commands for future use  

## Example Full Workflow:

```powershell
# 1. Start AI Agent
BISTART

# 2. Check service status
CHAT "List all Render services and show their status"

# 3. Check for errors
CHAT "Get logs from ai-agents-backend filtering for 'no such column' errors"

# 4. (Upload database manually via Google Drive + Render Shell)

# 5. Restart service
CHAT "Restart ai-agents-backend and wait for it to complete"

# 6. Verify fix
CHAT "Get the latest 20 logs from ai-agents-backend to confirm OAuth is working"
```

## Get Your Render API Key:

1. Go to: https://dashboard.render.com/u/settings/api-keys
2. Create new API key
3. Copy it
4. Set environment variable:
   ```powershell
   $env:RENDER_API_KEY = "rnd_XXXXXXXXXXXX"
   ```

## Current Status:

- ✅ Render tools loaded (8 tools available)
- ✅ Google Drive folder ready with working databases
- ✅ Migration script deployed (commit f797fe3)
- ⏳ Waiting for database upload
- ⏳ Waiting for service restart

## Next Action:

**Simplest approach:**
1. Upload `ai_infrastructure.db` via Google Drive + Render Shell (5 minutes)
2. Use Render tool to restart: `CHAT "Restart ai-agents-backend"`
3. Test OAuth login

OR

**Wait for migration:**
- Migration is deployed
- Should run automatically on next restart
- But Render database might be too old for migration to work

**Recommended: Upload database (guaranteed to work)**

---

**See also:**
- `RENDER_DATABASE_RESTORE_COMPLETE.md` - Full upload guide
- `render_tools.json` - Complete tool documentation
