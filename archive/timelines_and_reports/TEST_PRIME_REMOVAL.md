# Quick Test Commands - Prime-Loaded Removal
# Run these after migration to verify changes

# 1. CHECK DATABASE
# ============================================================
# Should return 0 rows (no prime-loaded threads remain)
SELECT COUNT(*) FROM sessions.threads WHERE location = 'prime-loaded';

# Should show 'prime', 'agent-N', 'unassigned' (NO 'prime-loaded')
SELECT location, COUNT(*) as count 
FROM sessions.threads 
GROUP BY location 
ORDER BY location;

# Check constraint (should NOT include 'prime-loaded')
SELECT conname, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conname = 'chk_location_valid';


# 2. CHECK BROWSER CONSOLE
# ============================================================
# After hard refresh (Ctrl+Shift+R), should see:
# 🔍 [DEBUG] Thread 1: {thread.location: 'prime', currentLocation: 'prime'}
# 🔍 [DEBUG] Final re-computed badge: {agentBadge.name: 'Prime'}


# 3. CHECK BACKEND LOGS
# ============================================================
# Should see (after assigning thread to Prime):
# ✅ Updated thread location to prime (NOT prime-loaded)
# ✅ [Interactions] Thread assigned to prime


# 4. VISUAL CHECK
# ============================================================
# Thread History sidebar:
# - Badge should show "Prime" ⭐ (gold star, gold border)
# - NOT "Prime-Loaded" or "prime-loaded"


# 5. GREP SEARCH (Optional - verify no prime-loaded in active code)
# ============================================================
# Run in PowerShell:
Get-ChildItem -Path "UI/modules_internal" -Filter "*.js" -Recurse | Select-String -Pattern "prime-loaded" | Select-Object -First 10

# Should find ONLY:
# - Debug logging code (✅ OK - these are temporary)
# - No assignment statements like: location = 'prime-loaded' (❌ BAD)
