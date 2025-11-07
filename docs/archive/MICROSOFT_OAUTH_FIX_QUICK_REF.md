# Microsoft OAuth Fix - Quick Reference

## 🔴 The Problem
```
ERROR: no such column: email
Endpoint: /api/auth/microsoft/status
```

## ✅ The Solution
Added 4 columns to `oauth_tokens` table:
- `email` TEXT
- `profile_name` TEXT  
- `error_count` INTEGER DEFAULT 0
- `last_error` TEXT

## 🎯 What You Need to Do

### Step 1: Re-authenticate Microsoft Account
```
Visit: http://localhost:5001/api/auth/microsoft/login
Click: "Authorize"
```

### Step 2: Verify It Works
```
Visit: http://localhost:5001/api/auth/microsoft/status

Should return:
{
  "connected": true,
  "email": "gerardo@minivetguide.onmicrosoft.com",
  "profile_name": "Gerardo Politis",
  "is_valid": true
}
```

## 🔒 Google Authentication
✅ **COMPLETELY UNAFFECTED**
- Google uses `metadata` JSON field for profile data
- Google doesn't use the new columns (they're NULL)
- All Google tools work exactly as before

## 📝 What Changed

### Database Schema
```sql
-- Before: 24 columns
-- After: 28 columns (added email, profile_name, error_count, last_error)
```

### Microsoft Callback Route
```python
# Now populates email and profile_name columns on authentication
INSERT INTO oauth_tokens (..., email, profile_name, ...)
VALUES (..., 'gerardo@...', 'Gerardo Politis', ...)
```

## 🧪 Verification Commands

### Check columns exist:
```bash
python verify_migration.py
```

### Check Google unaffected:
```sql
SELECT email, profile_name FROM oauth_tokens WHERE platform = 'google';
-- Result: email=NULL, profile_name=NULL (✅ Expected)
```

### Check Microsoft needs re-auth:
```sql
SELECT email, profile_name FROM oauth_tokens WHERE platform = 'microsoft';
-- Before re-auth: email=NULL, profile_name=NULL
-- After re-auth: email='gerardo@...', profile_name='Gerardo Politis'
```

## 📂 Files Changed
- ✅ `data/ai_infrastructure.db` - Database schema
- ✅ `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py` - INSERT statement

## ⚡ Quick Test
```powershell
# 1. Check migration worked
python verify_migration.py

# 2. Re-authenticate
# Visit: http://localhost:5001/api/auth/microsoft/login

# 3. Test status endpoint
# Visit: http://localhost:5001/api/auth/microsoft/status
```

## 🎉 Success Criteria
- [x] Migration script ran successfully
- [x] Verification script shows all columns present
- [x] Google tokens unaffected (email=NULL)
- [x] Microsoft callback route updated
- [ ] **USER ACTION REQUIRED:** Re-authenticate Microsoft account
- [ ] Status endpoint returns email and profile_name

---

**See `MICROSOFT_OAUTH_COLUMNS_MIGRATION_COMPLETE.md` for full details.**
