# Render Database Upload Instructions

## 5 Databases to Upload

| Database | Size | Purpose |
|----------|------|---------|
| ai_infrastructure.db | 624 KB | Users, OAuth tokens, credentials |
| sessions.db | 716 KB | Flask sessions, JWT tokens |
| synergy_sessions.db | 220 KB | Synergy feature data |
| kanban_analytics.db | 640 KB | Kanban board analytics |
| stock_data.db | 8.8 MB | Stock management (LARGE!) |

## Upload Methods

### Option 1: Use Render Shell (RECOMMENDED - All 5 databases)

**Step 1: Go to Render Dashboard**
- https://dashboard.render.com
- Click on `ai-agents-backend` service
- Click `Shell` tab

**Step 2: Upload using wget/curl**

You need to host the databases temporarily. Two options:

#### A) Use Google Drive (Easiest):
1. Upload all 5 `.db` files to Google Drive
2. Get shareable links (Anyone with link can view)
3. In Render Shell:

```bash
cd /data

# Get the file ID from share link (https://drive.google.com/file/d/FILE_ID/view)
# Then download each:

# ai_infrastructure.db
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=FILE_ID' -O ai_infrastructure.db

# sessions.db
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=FILE_ID' -O sessions.db

# synergy_sessions.db
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=FILE_ID' -O synergy_sessions.db

# kanban_analytics.db
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=FILE_ID' -O kanban_analytics.db

# stock_data.db (LARGE - 8.8MB)
wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=FILE_ID' -O stock_data.db
```

#### B) Use Dropbox:
1. Upload all 5 `.db` files to Dropbox
2. Get shareable links
3. Replace `www.dropbox.com` with `dl.dropboxusercontent.com` in the link
4. In Render Shell:

```bash
cd /data
wget 'YOUR_DROPBOX_LINK' -O ai_infrastructure.db
wget 'YOUR_DROPBOX_LINK' -O sessions.db
wget 'YOUR_DROPBOX_LINK' -O synergy_sessions.db
wget 'YOUR_DROPBOX_LINK' -O kanban_analytics.db
wget 'YOUR_DROPBOX_LINK' -O stock_data.db
```

**Step 3: Verify Upload**

```bash
ls -lh /data/*.db
sqlite3 /data/ai_infrastructure.db "SELECT COUNT(*) FROM users"
sqlite3 /data/sessions.db "SELECT COUNT(*) FROM sessions"
```

### Option 2: Base64 Paste (ONLY for small databases)

**For ai_infrastructure.db, sessions.db, synergy_sessions.db, kanban_analytics.db ONLY:**

1. Open the `.b64` file in Notepad:
   - `data\ai_infrastructure.db.b64`
   - `data\sessions.db.b64`
   - `data\synergy_sessions.db.b64`
   - `data\kanban_analytics.db.b64`

2. Copy ALL content (Ctrl+A, Ctrl+C)

3. In Render Shell:
```bash
cd /data
cat > ai_infrastructure.db.b64 << 'EOF'
[PASTE BASE64 CONTENT HERE]
EOF
base64 -d ai_infrastructure.db.b64 > ai_infrastructure.db
rm ai_infrastructure.db.b64
```

4. Repeat for each database

**DO NOT use this method for stock_data.db** (12 MB - too large!)

### Option 3: Use the Local Upload Server

1. Run on your PC:
```powershell
cd C:\Users\gpoli\GIT\AI_agents
python scripts/deployment/create_db_download_endpoint.py
```

2. Expose with ngrok:
```bash
ngrok http 8888
```

3. Copy the ngrok URL and in Render Shell:
```bash
cd /data
wget 'YOUR_NGROK_URL/download-db?token=TOKEN' -O ai_infrastructure.db
```

## What Render Needs

**All 5 databases must be in `/data/` folder:**

```
/data/
├── ai_infrastructure.db
├── sessions.db
├── synergy_sessions.db
├── kanban_analytics.db
└── stock_data.db
```

## After Upload

1. **Restart Render service** to pick up new databases
2. **Check logs** for successful initialization
3. **Test OAuth login** - should work now!

## Quick Test Commands (Render Shell)

```bash
# Check all databases exist
ls -lh /data/*.db

# Check record counts
sqlite3 /data/ai_infrastructure.db "SELECT COUNT(*) FROM users"
sqlite3 /data/ai_infrastructure.db "SELECT COUNT(*) FROM oauth_tokens"
sqlite3 /data/sessions.db "SELECT COUNT(*) FROM sessions"
sqlite3 /data/synergy_sessions.db "SELECT COUNT(*) FROM synergy_sessions"
sqlite3 /data/kanban_analytics.db "SELECT name FROM sqlite_master WHERE type='table'"
sqlite3 /data/stock_data.db "SELECT COUNT(*) FROM stock_items"
```

## Troubleshooting

**Error: "database is locked"**
- Suspend the Render service first
- Upload databases
- Resume service

**Error: "no such table"**
- Database file is corrupt or wrong version
- Re-upload the database

**OAuth still failing?**
- Check that migration ran: Look for "✅ [MIGRATION] Added X columns" in logs
- Verify oauth_tokens has scope column: `sqlite3 /data/ai_infrastructure.db "PRAGMA table_info(oauth_tokens)"`
