# Supabase Connection Modes - Configuration Guide

**Last Updated:** November 21, 2025  
**Status:** ✅ Production Ready

---

## Overview

Flask backend now supports **dual connection mode** with automatic fallback for Supabase database connections.

### Connection Modes

| Mode | Port | Use Case | Behavior | Priority |
|------|------|----------|----------|----------|
| **Transaction** | 6543 | Flask apps, serverless | Auto-closes after transaction | PRIMARY ✅ |
| **Session** | 5432 | Persistent connections | Keeps connection open | FALLBACK |

---

## Configuration

### Environment Variables (.env)

```env
# PRIMARY: Transaction Mode Pooler (port 6543) - RECOMMENDED
SUPABASE_DB_URL_POOLER=postgresql://postgres.PROJECT:PASSWORD@aws-1-REGION.pooler.supabase.com:6543/postgres

# FALLBACK: Session Mode Pooler (port 5432)
SUPABASE_DB_URL_SESSION=postgresql://postgres.PROJECT:PASSWORD@aws-1-REGION.pooler.supabase.com:5432/postgres
```

### Logic Flow

```python
1. Try SUPABASE_DB_URL_POOLER (port 6543) - Transaction Mode
   └─ If not set → Try SUPABASE_DB_URL_SESSION (port 5432) - Session Mode
      └─ If not set → Raise ValueError with helpful message
```

---

## Why Transaction Mode for Flask?

### Supabase Free Tier (Nano) Limits:
- **Max Database Connections:** 60
- **Max Pooler Clients:** 200

### Problem with Session Mode (5432):
```
Flask Request 1 → Opens connection → Keeps open → Uses 1 slot
Flask Request 2 → Opens connection → Keeps open → Uses 1 slot
...
Flask Request 60 → Opens connection → Keeps open → Uses 1 slot
Flask Request 61 → ❌ CONNECTION POOL EXHAUSTED
```

### Solution with Transaction Mode (6543):
```
Flask Request 1 → Opens connection → Transaction → Auto-closes → Frees slot ✅
Flask Request 2 → Opens connection → Transaction → Auto-closes → Frees slot ✅
Flask Request 100 → Opens connection → Transaction → Auto-closes → Frees slot ✅
```

---

## Connection Pool Configuration

### Current Settings:
```python
ThreadedConnectionPool(
    minconn=1,         # Minimum connections per schema
    maxconn=2,         # Maximum connections per schema (reduced from 3)
    connect_timeout=30,
    keepalives=1,
    keepalives_idle=30
)
```

### Pool Size Math:
- **5 schemas** (sessions, ai_infrastructure, stock_data, synergy_sessions, kanban_analytics)
- **2 max connections per schema**
- **Total potential:** 10 connections (well under 60 limit ✅)

---

## Testing

### Test Connection:
```powershell
python test_connection_modes.py
```

**Expected Output:**
```
SUPABASE CONNECTION MODE TEST
Configured URLs:
  POOLER (6543): ✅ SET
  SESSION (5432): ✅ SET

Testing connection...
 [POOL] Using Transaction Mode (port 6543) for 'sessions'
✅ CONNECTION SUCCESSFUL
PASSED - Ready for production
```

### Verify Pool Usage:
```powershell
python check_threads_messages.py
```

---

## Troubleshooting

### Error: "connection pool exhausted"

**Cause:** Using Session Mode (port 5432) with Flask  
**Solution:** Ensure `SUPABASE_DB_URL_POOLER` is set with port 6543

### Error: "SUPABASE_DB_URL not set"

**Cause:** Old environment variable name  
**Solution:** Update to use `SUPABASE_DB_URL_POOLER` and `SUPABASE_DB_URL_SESSION`

### Warning: "Using Session Mode (port 5432) - FALLBACK"

**Cause:** Transaction pooler URL not configured  
**Solution:** Add `SUPABASE_DB_URL_POOLER` to .env

---

## Migration from Old Config

### Old (Single URL):
```env
SUPABASE_DB_URL=postgresql://...pooler.supabase.com:5432/postgres
```

### New (Dual URL):
```env
# Primary (recommended)
SUPABASE_DB_URL_POOLER=postgresql://...pooler.supabase.com:6543/postgres

# Fallback
SUPABASE_DB_URL_SESSION=postgresql://...pooler.supabase.com:5432/postgres
```

---

## Production Deployment

### Render.com:
```yaml
# render.yaml
envVars:
  - key: SUPABASE_DB_URL_POOLER
    value: postgresql://postgres.PROJECT:PASSWORD@aws-1-REGION.pooler.supabase.com:6543/postgres
  
  - key: SUPABASE_DB_URL_SESSION
    value: postgresql://postgres.PROJECT:PASSWORD@aws-1-REGION.pooler.supabase.com:5432/postgres
```

### Docker:
```dockerfile
ENV SUPABASE_DB_URL_POOLER=postgresql://...pooler.supabase.com:6543/postgres
ENV SUPABASE_DB_URL_SESSION=postgresql://...pooler.supabase.com:5432/postgres
```

---

## Performance Monitoring

### Check Active Connections:
```sql
-- In Supabase SQL Editor
SELECT count(*) as active_connections
FROM pg_stat_activity
WHERE datname = 'postgres';
```

### Check Pool Stats:
```python
from AI_infrastructure.shared.database_utils import _pool_stats
print(_pool_stats)
# {'pools_created': 5, 'pool_hits': 120, 'pool_misses': 5}
```

---

## Files Modified

| File | Change |
|------|--------|
| `AI_infrastructure/shared/database_utils.py` | Added dual-URL logic with fallback |
| `.env` | Added `SUPABASE_DB_URL_POOLER` and `SUPABASE_DB_URL_SESSION` |
| `test_connection_modes.py` | New test script |
| `SUPABASE_CONNECTION_MODES.md` | This documentation |

---

## References

- [Supabase Connection Pooling Docs](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Supabase Free Tier Limits](https://supabase.com/docs/guides/platform/compute-and-disk)
- [Transaction vs Session Mode](https://supabase.com/docs/guides/database/connection-management)

---

**Status:** ✅ **Production Ready** - All tests passing, dual-URL fallback working correctly.
