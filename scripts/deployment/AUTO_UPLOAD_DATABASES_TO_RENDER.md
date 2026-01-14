# Automated Database Upload to Render - Complete Guide

## Your Render Configuration

- **API Key:** `rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu`
- **Service ID:** `srv-d4b2723uibrs73ff02t0`
- **Service Name:** `ai-agents-backend-singapore`
- **Service URL:** `https://ai-agents-backend-singapore.onrender.com`
- **Dashboard:** `https://dashboard.render.com/web/srv-d4b2723uibrs73ff02t0`
- **Google Drive Folder:** `https://drive.google.com/drive/folders/1UwmYADDh6vuNKlMOlcjFog4SSwnThE-O`

---

## 🚀 FASTEST METHOD: Copy-Paste Shell Commands

### Step 1: Get Google Drive File IDs

For each database file in your Google Drive folder:

1. Right-click file → **Get link**
2. Set to: **Anyone with the link can view**
3. Copy the FILE_ID from the link:
   ```
   https://drive.google.com/file/d/FILE_ID_HERE/view
   ```

You need FILE_IDs for:
- `ai_infrastructure.db` (638 KB)
- `sessions.db` (733 KB)
- `synergy_sessions.db` (225 KB)
- `kanban_analytics.db` (655 KB)
- `stock_data.db` (8.8 MB)

### Step 2: Go to Render Shell

Open: https://dashboard.render.com/web/srv-d4b2723uibrs73ff02t0/shell

### Step 3: Run These Commands (Replace FILE_IDs)

```bash
# Go to data folder
cd /data

# Backup existing databases
echo "Creating backup..."
mkdir -p backup_$(date +%Y%m%d_%H%M%S)
cp *.db backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo "No existing databases"

# Download ai_infrastructure.db (CRITICAL - HAS OAuth COLUMNS)
echo "Downloading ai_infrastructure.db..."
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=PASTE_FILE_ID_HERE' -O ai_infrastructure.db

# Download sessions.db
echo "Downloading sessions.db..."
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=PASTE_FILE_ID_HERE' -O sessions.db

# Download synergy_sessions.db
echo "Downloading synergy_sessions.db..."
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=PASTE_FILE_ID_HERE' -O synergy_sessions.db

# Download kanban_analytics.db
echo "Downloading kanban_analytics.db..."
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=PASTE_FILE_ID_HERE' -O kanban_analytics.db

# Download stock_data.db (LARGE FILE)
echo "Downloading stock_data.db (8.8MB)..."
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=PASTE_FILE_ID_HERE' -O stock_data.db

# Verify downloads
echo ""
echo "===== VERIFICATION ====="
ls -lh *.db

# CRITICAL CHECK: Verify users table has OAuth columns
echo ""
echo "===== CHECKING OAuth COLUMNS ====="
sqlite3 ai_infrastructure.db "SELECT name FROM pragma_table_info('users') WHERE name LIKE '%oauth%';"

# Should show:
# has_google_oauth
# has_microsoft_oauth

echo ""
echo "===== COMPLETE! ====="
echo "Next step: Restart the service from Render dashboard"
```

### Step 4: Restart Render Service

After databases are uploaded:

1. Go to: https://dashboard.render.com/web/srv-d4b2723uibrs73ff02t0
2. Click: **Manual Deploy** → **Clear build cache & deploy**
3. Wait 2-3 minutes for rebuild

### Step 5: Test OAuth Login

Visit: https://ai-agents-backend-singapore.onrender.com

Try **Login with Microsoft** - should work without `"no such column: has_microsoft_oauth"` error!

---

## Alternative: One-Command Upload (All 5 Databases)

If you want to paste all FILE_IDs at once, use this single command block:

```bash
cd /data && \
mkdir -p backup_$(date +%Y%m%d_%H%M%S) && \
cp *.db backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null && \
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=AI_INFRA_FILE_ID' -O ai_infrastructure.db && \
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=SESSIONS_FILE_ID' -O sessions.db && \
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=SYNERGY_FILE_ID' -O synergy_sessions.db && \
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=KANBAN_FILE_ID' -O kanban_analytics.db && \
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=STOCK_FILE_ID' -O stock_data.db && \
ls -lh *.db && \
sqlite3 ai_infrastructure.db "SELECT name FROM pragma_table_info('users') WHERE name LIKE '%oauth%';"
```

**Replace:**
- `AI_INFRA_FILE_ID` with ai_infrastructure.db FILE_ID
- `SESSIONS_FILE_ID` with sessions.db FILE_ID
- `SYNERGY_FILE_ID` with synergy_sessions.db FILE_ID
- `KANBAN_FILE_ID` with kanban_analytics.db FILE_ID
- `STOCK_FILE_ID` with stock_data.db FILE_ID

---

## Troubleshooting

### Issue: wget fails with "403 Forbidden"

**Solution:** Make sure Google Drive links are set to "Anyone with the link can view"

1. Right-click file in Drive → Share
2. Change to: "Anyone with the link"
3. Click "Copy link"

### Issue: Wrong file size

**Check expected sizes:**
```bash
# Expected sizes:
# ai_infrastructure.db: 638 KB
# sessions.db: 733 KB
# synergy_sessions.db: 225 KB
# kanban_analytics.db: 655 KB
# stock_data.db: 8.8 MB
```

If sizes are wrong, the FILE_ID is incorrect or link isn't public.

### Issue: Database is locked

**Solution:** Stop the service first:
```bash
# In Render Shell:
supervisorctl stop all
# Upload databases
# Then restart:
supervisorctl start all
```

### Issue: Still getting "no such column" error

**Verify column exists:**
```bash
sqlite3 /data/ai_infrastructure.db "PRAGMA table_info(users);" | grep -E "has_(google|microsoft)_oauth"
```

Should show:
```
12|has_google_oauth|BOOLEAN|0||0
13|has_microsoft_oauth|BOOLEAN|0||0
```

If not, the wrong database was uploaded.

---

## Expected Results

### Before Upload:
- ❌ OAuth login fails: `"no such column: has_microsoft_oauth"`
- ❌ Render has OLD database schema (~15 columns in users table)
- ❌ Migration can't add columns because base structure is wrong

### After Upload:
- ✅ OAuth login works perfectly (Microsoft + Google)
- ✅ Render has COMPLETE database schema (24 columns in users table)
- ✅ All columns present: `has_google_oauth`, `has_microsoft_oauth`, `is_active`
- ✅ No more "no such column" errors

---

## Quick Verification Commands

### Check Database File Sizes
```bash
ls -lh /data/*.db
```

### Check Users Table Schema
```bash
sqlite3 /data/ai_infrastructure.db "SELECT COUNT(*) FROM pragma_table_info('users');"
```
Should return: **24** (your local has 24 columns)

### Check OAuth Columns Exist
```bash
sqlite3 /data/ai_infrastructure.db "SELECT name FROM pragma_table_info('users') WHERE name LIKE '%oauth%';"
```
Should show: `has_google_oauth` and `has_microsoft_oauth`

### Check Service Status
```bash
curl https://ai-agents-backend-singapore.onrender.com/health
```

---

## Why This Works

Your **local databases** already have the complete, correct schema with all OAuth columns. The migration approach failed because Render's database was so old that it was missing base columns needed for migrations to work.

By **uploading your working databases**, you're giving Render the exact same schema as your local environment where OAuth works perfectly.

---

## Post-Upload Checklist

- [ ] All 5 databases downloaded successfully in Render Shell
- [ ] File sizes match expected values
- [ ] `has_google_oauth` column exists (verified with sqlite3)
- [ ] `has_microsoft_oauth` column exists (verified with sqlite3)
- [ ] Render service restarted via dashboard
- [ ] Microsoft OAuth login tested - WORKS
- [ ] Google OAuth login tested - WORKS
- [ ] No "no such column" errors in logs

---

**Status:** Ready to execute  
**Time Required:** 5-10 minutes  
**Last Updated:** November 15, 2025
