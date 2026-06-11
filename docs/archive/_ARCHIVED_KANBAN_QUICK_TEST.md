# InHousePrint Kanban - Quick Testing Guide

## ✅ BACKEND STATUS: ALL ENDPOINTS WORKING

### Test These URLs in Your Browser

#### 1. Platform Dashboard
```
http://localhost:8080/business-ai-platform-v2.html
```
**Look for:** Production Workflow icon (factory symbol) → Click to open Kanban board

#### 2. Health Check API
```
http://localhost:5001/api/inhouse-kanban/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "active_jobs": 43009
}
```

#### 3. Jobs Endpoint (First 5 jobs)
```
http://localhost:5001/api/inhouse-kanban/jobs?timeframe_months=-6&limit=5
```
**Expected:** Array with job objects including:
- `TicketID`, `OrderID`, `ClientName`
- `ShortJobDesc`, `StageDescription`
- `AIPriorityScore` (0-999)
- `PaperType`, `GSM`, `PaperSize`
- `DaysUntilDue`, `CustomerOrderCount`

#### 4. Stages Endpoint
```
http://localhost:5001/api/inhouse-kanban/stages?timeframe_months=-6
```
**Expected:** 13 stages with job counts:
- ArtOnly (1 job)
- OnHold (15 jobs)
- Digital - 9110 (4 jobs)
- Digital - Other (1 job)
- Digital - OutSource (11 jobs)
- ... etc (13 total)

#### 5. Metrics Endpoint
```
http://localhost:5001/api/inhouse-kanban/metrics?timeframe_months=-6
```
**Expected Response:**
```json
{
  "success": true,
  "metrics": {
    "total_jobs": 109,
    "pipeline_value": 130358.27,
    "overdue_jobs": 64,
    "avg_days_in_system": 14.0
  }
}
```

---

## Frontend Testing Checklist

### Module Initialization
- [ ] Platform UI loads without errors
- [ ] "Production Workflow" icon visible
- [ ] Clicking icon opens Kanban board
- [ ] Console shows: "✅ InHouse Print Production Workflow module ready"

### Kanban Board Display
- [ ] 13 production stages visible as columns
- [ ] Job cards display in appropriate stages
- [ ] Cards show: Job description, client name, priority badge
- [ ] Colors applied from Synergy Dashboard theme

### Job Cards
- [ ] Display job description
- [ ] Show customer tier badge (💎 VIP, ⭐ Premium, etc.)
- [ ] Display priority level (🚨 CRITICAL, ⚠️ HIGH, etc.)
- [ ] Show days until due date
- [ ] Display QTY and cost

### Filters
- [ ] Timeframe dropdown works (all time, 1 month, 6 months, 12 months)
- [ ] Priority filter functional
- [ ] Stage filter works
- [ ] Search by job description works

### Interactions
- [ ] Auto-refresh timer running (5-minute interval)
- [ ] Manual refresh button works
- [ ] Modal opens on job card click (if implemented)
- [ ] Drag-and-drop between stages (if implemented)

---

## Data Verification

### Total Numbers to Expect
- **Total Jobs:** 109 (in last 6 months)
- **Active Jobs Across Platform:** 43,009
- **Overdue Jobs:** 64
- **Pipeline Value:** €130,358.27
- **Average Days in System:** 14 days
- **Production Stages:** 13

### Sample Jobs to Look For
```
TicketID: 70398
Client: Gerardo Poli
Desc: "Emergency VG - (INVOICED FOR 1000)"
Stage: Digital - OutSource
Priority Score: 800
Days Until Due: -168 (OVERDUE!)
```

---

## Performance Benchmarks

| Endpoint | Response Time | Status |
|----------|---------------|--------|
| Health | <100ms | ✅ Working |
| Jobs (5 items) | 200-300ms | ✅ Working |
| Stages (13) | 150-200ms | ✅ Working |
| Metrics | 100-150ms | ✅ Working |
| **Average** | **150-200ms** | ✅ Excellent |

---

## If Something Doesn't Work

### Flask Server Down
```powershell
# Restart Flask
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

### Database Connection Error
```powershell
# Test connection
Test-NetConnection -ComputerName 3.25.76.138 -Port 1433
```

### Module Not Loading
```javascript
// Check in browser console
console.log(window.BaseModule) // Should exist
console.log(window.InhouseKanbanModule) // Should exist
```

### Check Flask Logs
```powershell
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
Get-Content flask_app.log -Tail 50
```

---

## What to Look For in Browser

### Console Messages (F12 → Console)
```javascript
// Good: Should see these
"🔧 Initializing InHouse Print Production Workflow module..."
"✅ InHouse Print Production Workflow module ready"
"📊 Loaded 109 jobs from backend"
"📊 Dashboard refreshing in 300 seconds..."

// Bad: Should NOT see these
"ERROR:"
"undefined is not an object"
"Failed to load"
```

### Network Tab (F12 → Network)
```
✅ GET /api/inhouse-kanban/health → 200 OK
✅ GET /api/inhouse-kanban/jobs → 200 OK
✅ GET /api/inhouse-kanban/stages → 200 OK
✅ GET /api/inhouse-kanban/metrics → 200 OK
```

---

## URL Parameters Reference

### Jobs Endpoint
```
GET /api/inhouse-kanban/jobs
  ?timeframe_months=-6     # Default: Last 6 months
  &priority_filter=all     # all/critical/high/urgent/normal/low
  &stage_id=3             # Filter by stage (optional)
  &limit=100              # Max results (default: 100)
```

### Stages Endpoint
```
GET /api/inhouse-kanban/stages
  ?timeframe_months=-6    # Default: Last 6 months
```

### Metrics Endpoint
```
GET /api/inhouse-kanban/metrics
  ?timeframe_months=-6    # Default: Last 6 months
```

---

## Success Criteria

✅ **Phase 1 - Backend (COMPLETE)**
- [x] Database connection works
- [x] All SQL queries execute without errors
- [x] Endpoints return correct data structure
- [x] Sample data loads successfully

✅ **Phase 2 - Frontend (IN PROGRESS)**
- [ ] Module initializes without errors
- [ ] Kanban board renders correctly
- [ ] All 13 stages visible
- [ ] Job cards display with correct data
- [ ] Filters work as expected
- [ ] Auto-refresh works every 5 minutes

⏳ **Phase 3 - Polish (PENDING)**
- [ ] Job details modal implemented
- [ ] Drag-and-drop stage transitions
- [ ] Export to PDF functionality
- [ ] Email notification integration

---

## Contact & Support

**Questions?** Check the logs:
```powershell
Get-Content C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\flask_app.log -Tail 100
```

**Module Files:**
- Backend: `AI_infrastructure/routes/inhouse_kanban_routes.py`
- Frontend: `UI/external/modules/inhouse-kanban/`
- Manifest: `UI/external/modules/inhouse-kanban/manifest.json`

---

**Last Updated:** 2025-11-03  
**Status:** Ready for Frontend Testing ✅
