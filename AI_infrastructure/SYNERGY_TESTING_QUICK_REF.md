# Synergy Testing Endpoints - Quick Reference

## 🚀 Quick Start

```bash
# Test everything at once
python AI_infrastructure/test_synergy_endpoints.py

# Individual tests
curl http://localhost:5000/api/synergy/test/smoke       # Quick health check
curl http://localhost:5000/api/synergy/test/endpoints   # List all endpoints
curl http://localhost:5000/api/synergy/test/database    # Database tests
curl http://localhost:5000/api/synergy/test/compile     # Syntax check
curl http://localhost:5000/api/synergy/test/health      # System metrics
```

## 📋 Endpoints Summary

| Endpoint | Purpose | Response Time | Use When |
|----------|---------|---------------|----------|
| `/test/smoke` | Basic health check | < 100ms | After restart, before deploy |
| `/test/endpoints` | List all APIs | < 50ms | API documentation, integration |
| `/test/database` | DB functionality | < 200ms | After migrations, slow queries |
| `/test/compile` | Syntax validation | < 500ms | Pre-commit, CI/CD |
| `/test/health` | System metrics | < 100ms | Production monitoring |

## 🎯 Common Use Cases

### Pre-Deployment Check
```bash
# Run all tests
python AI_infrastructure/test_synergy_endpoints.py

# Expected output:
# ✅ Smoke Test
# ✅ Endpoints List
# ✅ Database Test
# ✅ Compile Test
# ✅ Health Check
# Total: 5/5 tests passed
```

### Production Monitoring (PowerShell)
```powershell
# Continuous health monitoring
while ($true) {
    $health = Invoke-RestMethod "http://localhost:5000/api/synergy/test/health"
    Write-Host "$(Get-Date) - $($health.status) - CPU: $($health.system.cpu_percent)%"
    Start-Sleep 10
}
```

### CI/CD Pipeline
```yaml
# GitHub Actions
- name: Synergy Tests
  run: python AI_infrastructure/test_synergy_endpoints.py
```

## 🔍 Troubleshooting

| Error | Solution |
|-------|----------|
| Connection refused | Start Flask server: `python AI_infrastructure/flask_app.py` |
| Database connection failed | Check `.env` credentials |
| Table not found | Run database migrations |
| High CPU/memory | Check for memory leaks, optimize queries |

## 📊 Response Examples

### Smoke Test (200 OK)
```json
{
  "success": true,
  "summary": "4/4 tests passed",
  "duration_ms": 45.23,
  "tests": {
    "database_connection": {"status": "PASS", "duration_ms": 12.34},
    "table_existence": {"status": "PASS", "found_tables": [...], "duration_ms": 8.76},
    "query_execution": {"status": "PASS", "session_count": 42, "duration_ms": 5.12},
    "json_serialization": {"status": "PASS", "duration_ms": 0.01}
  }
}
```

### Health Check (200 OK)
```json
{
  "status": "healthy",
  "system": {
    "cpu_percent": 45.2,
    "memory_percent": 62.1,
    "disk_percent": 78.5
  },
  "database": {"status": "connected"}
}
```

## 🚨 HTTP Status Codes

- **200** - All tests passed ✅
- **500** - Tests failed or exception ❌
- **503** - System unhealthy ⚠️

## 📁 Files Added

1. **synergy_routes.py** (lines 2619-2878) - 5 new endpoints
2. **test_synergy_endpoints.py** - Automated test script
3. **SYNERGY_TESTING_ENDPOINTS.md** - Full documentation
4. **SYNERGY_TESTING_QUICK_REF.md** - This file

## 🔗 Related Documentation

- **Full Docs:** `AI_infrastructure/SYNERGY_TESTING_ENDPOINTS.md`
- **Architecture:** `AI_infrastructure/routes/synergy_routes.py` (header comments)
- **Main Instructions:** `.github/copilot-instructions.md`

---

**Version:** 1.0  
**Last Updated:** December 31, 2024  
**Status:** Production Ready ✅
