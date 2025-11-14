# Render Database Restore - Complete Guide

## Problem
Render database is OLD and missing critical columns causing OAuth failures:
- `"no such column: has_microsoft_oauth"`
- `"no such column: has_google_oauth"`

## Solution
Upload your WORKING databases from Google Drive to Render.

---

## Google Drive Folder
**Location:** https://drive.google.com/drive/folders/1UwmYADDh6vuNKlMOlcjFog4SSwnThE-O

**Contents:**
- `ai_infrastructure.db` (638 KB) - ✅ Users, OAuth tokens, credentials
- `sessions.db` (733 KB) - ✅ Flask sessions, JWT tokens  
- `synergy_sessions.db` (225 KB) - ✅ Synergy feature data
- `kanban_analytics.db` (655 KB) - ✅ Kanban board analytics
- `stock_data.db` (8.8 MB) - ✅ Stock management

---

## Step 1: Get File IDs from Google Drive

### For Each Database File:

1. Go to: https://drive.google.com/drive/folders/1UwmYADDh6vuNKlMOlcjFog4SSwnThE-O

2. **Right-click** on `ai_infrastructure.db` → **Get link**

3. Make sure it's set to: **Anyone with the link can view**

4. Copy the link - it looks like:
   ```
   https://drive.google.com/file/d/1ABC123XYZ456/view?usp=sharing
   ```

5. Extract the **FILE_ID** (the part between `/d/` and `/view`):
   ```
   FILE_ID = 1ABC123XYZ456
   ```

6. **Repeat for all 5 databases**

---

## Step 2: Create Download Script

**OPTION A: Manual Method (Safer)**

1. Go to Render Dashboard: https://dashboard.render.com
2. Click: **ai-agents-backend** service
3. Click: **Shell** tab
4. Run these commands **ONE BY ONE**:

```bash
# Go to data folder
cd /data

# Backup existing databases
mkdir -p backup_old
cp *.db backup_old/ 2>/dev/null || echo "No backup needed"

# Download ai_infrastructure.db (REPLACE FILE_ID)
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=FILE_ID_HERE' -O ai_infrastructure.db

# Download sessions.db (REPLACE FILE_ID)
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=FILE_ID_HERE' -O sessions.db

# Download synergy_sessions.db (REPLACE FILE_ID)
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=FILE_ID_HERE' -O synergy_sessions.db

# Download kanban_analytics.db (REPLACE FILE_ID)
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=FILE_ID_HERE' -O kanban_analytics.db

# Download stock_data.db (REPLACE FILE_ID)
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=FILE_ID_HERE' -O stock_data.db

# Verify downloads
ls -lh *.db

# Check users table has OAuth columns
sqlite3 ai_infrastructure.db "SELECT name FROM pragma_table_info('users') WHERE name LIKE '%oauth%';"
```

**Expected output from last command:**
```
has_google_oauth
has_microsoft_oauth
```

---

**OPTION B: Automated Script (Faster)**

1. Get all 5 FILE_IDs from Google Drive

2. Edit `scripts/deployment/download_databases_from_google_drive.sh`:
   - Replace each `REPLACE_WITH_FILE_ID_FROM_DRIVE` with actual FILE_IDs

3. In Render Shell, run:
```bash
cd /data
# Copy the script content and paste it into the shell
# OR upload the script file first
```

---

## Step 3: Restart Render Service

### Method 1: Dashboard
1. Go to: https://dashboard.render.com
2. Click: **ai-agents-backend**
3. Click: **Manual Deploy** → **Clear build cache & deploy**

### Method 2: Shell
```bash
# In Render Shell
supervisorctl restart all
```

---

## Step 4: Verify It Worked

### Check Logs
1. Go to Render Dashboard → **ai-agents-backend** → **Logs**

2. Look for:
```
✅ User authentication tables initialized at /data/ai_infrastructure.db
✅ Database tables verified: users, oauth_tokens, ...
✅ Users OAuth columns migration complete (0 columns added)
```

### Test OAuth Login
1. Go to: https://your-render-url.onrender.com
2. Click **Login with Microsoft**
3. Should work WITHOUT "no such column" error

### Verify Database Schema
In Render Shell:
```bash
sqlite3 /data/ai_infrastructure.db "PRAGMA table_info(users);" | grep -E "has_(google|microsoft)_oauth"
```

Should show:
```
12|has_google_oauth|BOOLEAN|0||0
13|has_microsoft_oauth|BOOLEAN|0||0
```

---

## Troubleshooting

### Issue: wget fails with "403 Forbidden"
**Solution:** Make sure Google Drive link is set to "Anyone with the link can view"

### Issue: File size is wrong
**Solution:** Use the direct download link format:
```bash
https://drive.google.com/uc?export=download&id=FILE_ID
```

### Issue: Database is locked
**Solution:** Stop the Flask app first:
```bash
supervisorctl stop all
# Then download databases
# Then restart
supervisorctl start all
```

### Issue: Still getting "no such column" error
**Solution:** Verify you downloaded the correct file:
```bash
sqlite3 /data/ai_infrastructure.db "SELECT COUNT(*) FROM pragma_table_info('users');"
```
Should return: **24** (your local database has 24 columns)

---

## Quick Reference: File IDs Template

Copy this and fill in your FILE_IDs:

```bash
# ai_infrastructure.db
FILE_ID_AI_INFRA="PASTE_HERE"

# sessions.db
FILE_ID_SESSIONS="PASTE_HERE"

# synergy_sessions.db
FILE_ID_SYNERGY="PASTE_HERE"

# kanban_analytics.db
FILE_ID_KANBAN="PASTE_HERE"

# stock_data.db
FILE_ID_STOCK="PASTE_HERE"
```

---

## Expected Results

### Before:
- ❌ OAuth login fails: "no such column: has_microsoft_oauth"
- ❌ Render database: ~15 columns in users table
- ❌ Missing: has_google_oauth, has_microsoft_oauth, is_active

### After:
- ✅ OAuth login works perfectly
- ✅ Render database: 24 columns in users table
- ✅ All OAuth columns present
- ✅ All 5 databases synced with local

---

## Why This Works

Your **local databases** already have the correct schema:
- `users` table: 24 columns (including OAuth columns)
- `oauth_tokens` table: 30 columns (complete schema)

Render's **old databases** are missing these columns because they were created before the migrations.

**Uploading your working databases** gives Render the complete, up-to-date schema.

---

## Post-Deployment Checklist

- [ ] All 5 databases downloaded successfully
- [ ] File sizes match (638KB, 733KB, 225KB, 655KB, 8.8MB)
- [ ] `has_google_oauth` column exists in users table
- [ ] `has_microsoft_oauth` column exists in users table
- [ ] Render service restarted
- [ ] Microsoft OAuth login tested - WORKS
- [ ] Google OAuth login tested - WORKS
- [ ] No "no such column" errors in logs

---

**Status:** Ready for deployment  
**Google Drive Folder:** https://drive.google.com/drive/folders/1UwmYADDh6vuNKlMOlcjFog4SSwnThE-O  
**Last Updated:** November 15, 2025
