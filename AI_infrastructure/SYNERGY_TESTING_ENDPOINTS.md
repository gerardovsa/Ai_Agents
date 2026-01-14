# Synergy Testing Endpoints Documentation

**Created:** December 31, 2024  
**Purpose:** Comprehensive testing infrastructure for Synergy Dashboard API  
**Location:** AI_infrastructure/routes/synergy_routes.py

## Overview

Added 5 new testing endpoints to enable automated smoke tests, compile validation, database health checks, and endpoint verification. These endpoints are designed for:

1. **Development:** Quick validation during coding
2. **Deployment:** Pre-production health checks
3. **Monitoring:** Production uptime and performance tracking
4. **CI/CD:** Automated testing in deployment pipelines

---

## Endpoints

### 1. Smoke Test (`/api/synergy/test/smoke`)

**Method:** GET  
**Purpose:** Quick system health check  
**Use Case:** First line of defense - verify basic functionality is working

#### Tests Performed:
- ✅ Database connection establishment
- ✅ Core table existence (synergy_sessions, milestones, tasks, subtasks)
- ✅ Basic query execution (SELECT COUNT(*))
- ✅ JSON serialization/deserialization

#### Response Format:
```json
{
  "success": true,
  "summary": "4/4 tests passed",
  "duration_ms": 45.23,
  "timestamp": "2024-12-31T10:30:00",
  "tests": {
    "database_connection": {
      "status": "PASS",
      "duration_ms": 12.34
    },
    "table_existence": {
      "status": "PASS",
      "found_tables": ["synergy_sessions", "milestones", "tasks", "subtasks"],
      "missing_tables": [],
      "duration_ms": 8.76
    },
    "query_execution": {
      "status": "PASS",
      "session_count": 42,
      "duration_ms": 5.12
    },
    "json_serialization": {
      "status": "PASS",
      "duration_ms": 0.01
    }
  }
}
```

#### Usage Example:
```bash
# Command line
curl http://localhost:5000/api/synergy/test/smoke

# PowerShell
Invoke-RestMethod -Uri "http://localhost:5000/api/synergy/test/smoke"

# Python
import requests
response = requests.get("http://localhost:5000/api/synergy/test/smoke")
print(response.json())
```

#### When to Use:
- ✅ After server restart
- ✅ Before deployment
- ✅ In CI/CD pipeline health checks
- ✅ When debugging "server not responding" issues

---

### 2. Endpoints List (`/api/synergy/test/endpoints`)

**Method:** GET  
**Purpose:** Discover all available API endpoints  
**Use Case:** API documentation, integration testing, endpoint inventory

#### Response Format:
```json
{
  "success": true,
  "endpoint_count": 28,
  "timestamp": "2024-12-31T10:30:00",
  "endpoints": [
    {
      "name": "list_sessions",
      "path": "/api/synergy/list",
      "methods": ["GET"],
      "tested": true
    },
    {
      "name": "create_session",
      "path": "/api/synergy/create",
      "methods": ["POST"],
      "tested": true
    },
    ...
  ]
}
```

#### Usage Example:
```bash
# Command line
curl http://localhost:5000/api/synergy/test/endpoints

# PowerShell
$endpoints = Invoke-RestMethod -Uri "http://localhost:5000/api/synergy/test/endpoints"
$endpoints.endpoints | Format-Table name, path, methods

# Python
import requests
response = requests.get("http://localhost:5000/api/synergy/test/endpoints")
for endpoint in response.json()['endpoints']:
    print(f"{endpoint['path']} - {endpoint['methods']}")
```

#### When to Use:
- ✅ Generating API documentation
- ✅ Building integration test suites
- ✅ Verifying endpoint registration after code changes
- ✅ Creating OpenAPI/Swagger specs

---

### 3. Database Test (`/api/synergy/test/database`)

**Method:** GET  
**Purpose:** Comprehensive database functionality verification  
**Use Case:** Database migration validation, performance monitoring, connection pooling tests

#### Tests Performed:
- ✅ Connection pool stress test (5 concurrent connections)
- ✅ Transaction rollback verification (ACID compliance)
- ✅ Query performance benchmarking (simple vs complex queries)

#### Response Format:
```json
{
  "success": true,
  "timestamp": "2024-12-31T10:30:00",
  "tests": {
    "connection_pool": {
      "status": "PASS",
      "connections_created": 5,
      "duration_ms": 120.45
    },
    "transaction_rollback": {
      "status": "PASS",
      "duration_ms": 15.23
    },
    "query_performance": {
      "status": "PASS",
      "simple_query_ms": 2.34,
      "complex_query_ms": 8.76,
      "duration_ms": 11.10
    }
  }
}
```

#### Usage Example:
```bash
# Command line
curl http://localhost:5000/api/synergy/test/database

# PowerShell
$dbTest = Invoke-RestMethod -Uri "http://localhost:5000/api/synergy/test/database"
$dbTest.tests | ConvertTo-Json -Depth 3

# Python
import requests
response = requests.get("http://localhost:5000/api/synergy/test/database")
for test_name, result in response.json()['tests'].items():
    print(f"{test_name}: {result['status']} ({result['duration_ms']}ms)")
```

#### When to Use:
- ✅ After database migrations
- ✅ When debugging slow queries
- ✅ Before production deployment
- ✅ Monitoring connection pool health

---

### 4. Compile Test (`/api/synergy/test/compile`)

**Method:** GET  
**Purpose:** Python syntax validation  
**Use Case:** Pre-deployment syntax checks, CI/CD validation

#### Tests Performed:
- ✅ Python bytecode compilation of synergy_routes.py
- ✅ Syntax error detection
- ✅ Import resolution verification

#### Response Format:
```json
{
  "success": true,
  "timestamp": "2024-12-31T10:30:00",
  "files_tested": [
    {
      "file": "synergy_routes.py",
      "status": "PASS",
      "size_bytes": 187432
    }
  ]
}
```

#### Usage Example:
```bash
# Command line
curl http://localhost:5000/api/synergy/test/compile

# PowerShell
Invoke-RestMethod -Uri "http://localhost:5000/api/synergy/test/compile"

# Python
import requests
response = requests.get("http://localhost:5000/api/synergy/test/compile")
if response.json()['success']:
    print("✅ Code compiles successfully")
else:
    print("❌ Compilation errors detected")
```

#### When to Use:
- ✅ In pre-commit hooks
- ✅ CI/CD pipeline validation
- ✅ After code refactoring
- ✅ Before merging pull requests

---

### 5. Health Check (`/api/synergy/test/health`)

**Method:** GET  
**Purpose:** System-level health monitoring  
**Use Case:** Production monitoring, uptime checks, resource tracking

#### Metrics Collected:
- ✅ Platform information (OS, Python version)
- ✅ CPU usage (percent, core count)
- ✅ Memory usage (percent)
- ✅ Disk usage (percent)
- ✅ Database connection status

#### Response Format:
```json
{
  "status": "healthy",
  "timestamp": "2024-12-31T10:30:00",
  "system": {
    "platform": "Windows",
    "python_version": "3.11.0",
    "cpu_count": 8,
    "cpu_percent": 45.2,
    "memory_percent": 62.1,
    "disk_percent": 78.5
  },
  "database": {
    "status": "connected"
  }
}
```

#### Usage Example:
```bash
# Command line
curl http://localhost:5000/api/synergy/test/health

# PowerShell (continuous monitoring)
while ($true) {
    $health = Invoke-RestMethod -Uri "http://localhost:5000/api/synergy/test/health"
    Write-Host "$(Get-Date) - Status: $($health.status) - CPU: $($health.system.cpu_percent)%"
    Start-Sleep -Seconds 10
}

# Python (alert on high resource usage)
import requests
import time

while True:
    response = requests.get("http://localhost:5000/api/synergy/test/health")
    health = response.json()
    
    if health['system']['cpu_percent'] > 80:
        print("⚠️ HIGH CPU USAGE DETECTED!")
    if health['system']['memory_percent'] > 90:
        print("⚠️ HIGH MEMORY USAGE DETECTED!")
    
    time.sleep(30)
```

#### When to Use:
- ✅ Production uptime monitoring
- ✅ Resource usage tracking
- ✅ Load balancer health checks
- ✅ Alerting on high resource usage

---

## Testing Strategy

### Local Development
```bash
# Quick smoke test before committing
curl http://localhost:5000/api/synergy/test/smoke

# Verify compilation
curl http://localhost:5000/api/synergy/test/compile
```

### Pre-Deployment
```bash
# Run all tests
python AI_infrastructure/test_synergy_endpoints.py

# Check health
curl http://localhost:5000/api/synergy/test/health
```

### Production Monitoring
```bash
# Set up cron job (Linux) or Scheduled Task (Windows) to run every 5 minutes
*/5 * * * * curl -f http://your-domain.com/api/synergy/test/health || echo "Health check failed"
```

### CI/CD Integration
```yaml
# Example GitHub Actions workflow
- name: Run Synergy Tests
  run: |
    python AI_infrastructure/test_synergy_endpoints.py
    if [ $? -ne 0 ]; then
      echo "Tests failed - blocking deployment"
      exit 1
    fi
```

---

## Response Codes

| Code | Meaning | When It Occurs |
|------|---------|---------------|
| 200 | Success | All tests passed |
| 500 | Server Error | Tests failed or exception occurred |
| 503 | Service Unavailable | Health check failed (unhealthy system) |

---

## Troubleshooting

### Smoke Test Failing

**Symptom:** `database_connection` test fails  
**Solution:** Check database credentials in `.env` file

**Symptom:** `table_existence` test fails  
**Solution:** Run database migrations or check schema

**Symptom:** `query_execution` test fails  
**Solution:** Verify database permissions and table structure

### Database Test Failing

**Symptom:** `connection_pool` test fails  
**Solution:** Check connection pool settings in database_utils.py

**Symptom:** `transaction_rollback` test fails  
**Solution:** Verify database supports transactions (PostgreSQL required)

**Symptom:** `query_performance` test slow (>100ms)  
**Solution:** Check database indexes, consider adding indexes to frequently queried columns

### Compile Test Failing

**Symptom:** `py_compile.PyCompileError`  
**Solution:** Fix syntax errors in synergy_routes.py

### Health Check Failing

**Symptom:** High CPU/memory usage  
**Solution:** Check for memory leaks, optimize queries, scale resources

**Symptom:** Database connection error  
**Solution:** Verify database is running and accessible

---

## Performance Benchmarks

**Expected Response Times:**
- Smoke Test: < 100ms
- Endpoints List: < 50ms
- Database Test: < 200ms
- Compile Test: < 500ms (depends on file size)
- Health Check: < 100ms

**Acceptable Resource Usage:**
- CPU: < 80%
- Memory: < 85%
- Disk: < 90%

---

## Integration with Existing System

### Files Modified:
- `AI_infrastructure/routes/synergy_routes.py` - Added 5 new endpoints (lines 2619-2878)

### Files Created:
- `AI_infrastructure/test_synergy_endpoints.py` - Test verification script
- `AI_infrastructure/SYNERGY_TESTING_ENDPOINTS.md` - This documentation

### Dependencies:
- `psutil` - System metrics (already in requirements.txt)
- `py_compile` - Python compilation (built-in)
- All existing synergy_routes.py dependencies

### No Breaking Changes:
- ✅ All existing endpoints continue to work
- ✅ No database schema changes
- ✅ No configuration changes required
- ✅ Backward compatible

---

## Future Enhancements

### Planned Features:
1. **Load Testing Endpoint** - Simulate high traffic scenarios
2. **Integration Test Suite** - Full end-to-end workflow testing
3. **Performance Profiling** - Detailed query analysis and optimization suggestions
4. **Automated Alerting** - Webhook notifications for failed health checks
5. **Historical Metrics** - Store test results over time for trend analysis

### Potential Improvements:
- Add authentication to test endpoints (prevent unauthorized access)
- Create Prometheus/Grafana integration for metrics visualization
- Add custom test configurations via query parameters
- Implement test result caching to reduce database load

---

## Best Practices

### DO:
- ✅ Run smoke test after every server restart
- ✅ Include health check in production monitoring
- ✅ Add test endpoints to CI/CD pipelines
- ✅ Monitor query performance trends over time

### DON'T:
- ❌ Expose test endpoints to public internet without authentication
- ❌ Run database stress tests in production
- ❌ Ignore failing health checks
- ❌ Skip testing before deployment

---

## Contact & Support

**Questions:** Refer to AI_agent_instructions.md  
**Issues:** Check Flask logs at `AI_infrastructure/flask_app.log`  
**Updates:** This system follows the nested context manager pattern documented in synergy_routes.py header

---

**Last Updated:** December 31, 2024  
**Version:** 1.0  
**Status:** Production Ready ✅
