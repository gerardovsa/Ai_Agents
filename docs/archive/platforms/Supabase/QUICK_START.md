# Supabase Integration - Quick Start Guide

**Get connected in 5 minutes!**

---

## ⚡ Step 1: Get Your Credentials (2 minutes)

1. Go to **https://supabase.com/dashboard**
2. Select your project (or create new)
3. Click **Settings** (gear icon) → **API**
4. Copy two things:
   - **Project URL:** `https://xxxxx.supabase.co`
   - **anon public key:** Long string starting with `eyJ...`

---

## ⚡ Step 2: Set Environment Variables (1 minute)

**Windows PowerShell:**
```powershell
$env:SUPABASE_URL = "https://your-project.supabase.co"
$env:SUPABASE_KEY = "your-anon-key-here"
```

**Linux/Mac:**
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key-here"
```

**Or create `.env` file:**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## ⚡ Step 3: Test Connection (1 minute)

```bash
python test_supabase_connection.py
```

Expected output:
```
✅ SUPABASE_URL: https://xxxxx.supabase.co
✅ SUPABASE_KEY: eyJhbGciOiJIUzI1Ni...
✅ Client initialized successfully
✅ Status: healthy
✅ Supabase client is working!
```

---

## ⚡ Step 4: Create Test Table (1 minute)

Go to **Supabase Dashboard → SQL Editor** and run:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all" ON users
    FOR ALL USING (true) WITH CHECK (true);

INSERT INTO users (name, email) VALUES
    ('Test User', 'test@example.com');
```

---

## ⚡ Step 5: Try It Out!

**List data:**
```bash
python supabase_client.py list users
```

**Insert data:**
```python
from supabase_client import SupabaseClient

client = SupabaseClient()
client.insert('users', {'name': 'John', 'email': 'john@example.com'})
```

**Query data:**
```python
users = client.query('users').select('*').eq('name', 'John').execute()
print(users)
```

---

## 🎉 You're Done!

**Now you can:**
- ✅ Query your Supabase database
- ✅ Insert, update, delete data
- ✅ Authenticate users
- ✅ Upload/download files
- ✅ Call PostgreSQL functions

---

## 📚 Next Steps

- Read **[README.md](README.md)** for complete documentation
- Check **[SUPABASE_API_DOCS.md](SUPABASE_API_DOCS.md)** for advanced features
- Explore example scripts in this folder

---

## 🆘 Need Help?

**Connection Issues?**
```bash
# Check if credentials are set
echo $env:SUPABASE_URL
echo $env:SUPABASE_KEY

# Test manually
curl https://your-project.supabase.co
```

**Table Not Found?**
- Make sure table name is exact (case-sensitive)
- Check table exists in SQL Editor
- Verify RLS policies are set

**Permission Denied?**
- Enable Row Level Security
- Create policy: `CREATE POLICY "Allow all" ON your_table FOR ALL USING (true);`

---

**Last Updated:** October 23, 2025
