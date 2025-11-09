# Supabase Migration Toolkit

Complete toolkit for migrating AI Agents from SQLite to Supabase PostgreSQL.

## 📁 Files

| File | Purpose |
|------|---------|
| `migrate_to_supabase.py` | Main migration script (SQLite → PostgreSQL) |
| `SUPABASE_SETUP_GUIDE.md` | Complete step-by-step guide |
| `README.md` | This file |

## 🚀 Quick Start (5 steps)

### 1. Create Supabase Project
- Go to https://supabase.com/dashboard
- Create project: "ai-agents-production"
- Region: Singapore
- Save credentials (URL, Anon Key, Database URL)

### 2. Install Dependencies
```powershell
pip install psycopg2-binary
```

### 3. Run Migration
```powershell
python migrate_to_supabase.py
```

### 4. Add Environment Variables
```powershell
cd ../Render_backend
python add_supabase_env_vars.py
```

### 5. Deploy
```powershell
cd ..
git add .
git commit -m "Migrate to Supabase"
git push origin v3
```

## 📊 What Gets Migrated

| Database | Tables | Purpose |
|----------|--------|---------|
| `ai_infrastructure.db` | 15 | Users, OAuth tokens, credentials |
| `sessions.db` | 3 | Flask sessions, JWT tokens |
| `synergy_sessions.db` | 5 | Synergy feature data |
| `kanban_analytics.db` | 3 | Analytics data |
| `stock_data.db` | 2 | Stock management |

**Total:** ~28 tables, ~5,000+ rows

## ✅ Benefits

1. **Visual Dashboard** - See and edit data in browser
2. **No Deployment Issues** - No more file copying errors
3. **Better Performance** - Proper database engine
4. **Automatic Backups** - Daily backups included
5. **Cost Savings** - $2.50/month less than Render persistent disk

## 🆘 Need Help?

See `SUPABASE_SETUP_GUIDE.md` for:
- Detailed instructions
- Troubleshooting
- Cost comparison
- Testing procedures

## 📈 Migration Process

```
Phase 1: Analyze SQLite databases (2 min)
    ↓
Phase 2: Create PostgreSQL schemas (3 min)
    ↓
Phase 3: Migrate all data (8 min)
    ↓
Phase 4: Verify row counts (2 min)
    ↓
Total: ~15 minutes
```

## 🎯 Success Criteria

✅ All tables created in PostgreSQL  
✅ Row counts match source databases  
✅ No data loss or corruption  
✅ Application connects successfully  
✅ Render deployment succeeds  

---

**Created:** November 9, 2025  
**Status:** Production Ready  
**Tested:** Yes (with 5 SQLite databases)
