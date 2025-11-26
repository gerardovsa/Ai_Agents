# InHousePrint Production Workflow - Integration Guide

**Version:** 1.0.0  
**Date:** November 3, 2025  
**Status:** Ready for Deployment

---

## Quick Start

### 1. Verify Files Created

All module files have been created in the correct locations:

**Module Files:**
```
✅ UI/external/modules/inhouse-kanban/manifest.json
✅ UI/external/modules/inhouse-kanban/inhouse-kanban.js
✅ UI/external/modules/inhouse-kanban/inhouse-kanban.css
✅ UI/external/modules/inhouse-kanban/README.md
```

**Backend Files:**
```
✅ AI_infrastructure/routes/inhouse_kanban_routes.py
```

**Integration Files:**
```
✅ AI_infrastructure/flask_app.py (updated)
✅ UI/external/modules/manifest.json (updated)
```

### 2. Restart Flask Server

**Stop current server:**
- Press `Ctrl+C` in the terminal running BISTART

**Start server:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

### 3. Verify Backend

**Test health endpoint:**
```powershell
curl http://localhost:5001/api/inhouse-kanban/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "active_jobs": 45,
  "server": "3.25.76.138\\INHPSQLSERVER",
  "database_name": "In HousePrint"
}
```

### 4. Access Module

1. Open browser: `http://localhost:5001`
2. Look for **"Production Workflow"** icon in sidebar (factory icon)
3. Click to open module
4. Verify jobs load correctly

---

## Validation Checklist

Run through this checklist to ensure everything works:

- [ ] **Flask Blueprint Registration**
  - Check Flask logs for: `✅ InHousePrint Kanban routes registered`
  - No errors during blueprint registration

- [ ] **Health Endpoint**
  - `curl http://localhost:5001/api/inhouse-kanban/health` returns 200 OK
  - Response shows database connected

- [ ] **Module Validation**
  - `python scripts\maintenance\validate_modules.py` shows ✅ for inhouse-kanban
  - No naming convention errors

- [ ] **Frontend Loading**
  - Module icon appears in sidebar
  - Clicking icon loads Kanban board
  - No JavaScript errors in console (F12)

- [ ] **Data Loading**
  - Jobs appear in Kanban columns
  - Metrics row shows correct counts
  - Filters work (timeframe, priority, search)

- [ ] **Job Details**
  - Clicking "View Details" opens modal
  - All job fields display correctly
  - Modal closes properly

- [ ] **Responsive Design**
  - Test on desktop (works)
  - Test on tablet/mobile (responsive)

---

## Troubleshooting

### Module Not Appearing

**Check 1: Module registered in main manifest?**
```powershell
# Verify entry exists
cat UI\external\modules\manifest.json | Select-String "inhouse-kanban"
```

**Check 2: JavaScript loading?**
- Open browser console (F12)
- Look for errors
- Check Network tab for 404s

**Check 3: Blueprint registered?**
- Check Flask logs on startup
- Should see blueprint registration message

### Database Connection Errors

**Error: `pyodbc.InterfaceError`**
- **Solution:** Install ODBC Driver 17 for SQL Server
- **Download:** https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

**Error: `Login failed`**
- **Solution:** Ensure Windows Authentication is enabled
- **Fix:** Run Flask app with correct Windows user

**Error: `Unable to connect to server`**
- **Solution:** Check server is accessible: `3.25.76.138\INHPSQLSERVER`
- **Fix:** Test with SQL Server Management Studio first

### No Jobs Displayed

**Check 1: Database has active jobs?**
```sql
SELECT COUNT(*) FROM JobTickets WHERE InternalInvoiceComplete = 0
```

**Check 2: Timeframe filter too restrictive?**
- Try "Last 12 months" instead of "Last 6 months"

**Check 3: API returning data?**
```powershell
curl "http://localhost:5001/api/inhouse-kanban/jobs?timeframe_months=-12&limit=10"
```

### Performance Issues

**Symptom: Slow loading**
- Reduce timeframe (e.g., 1-3 months)
- Check SQL Server performance
- Verify network connectivity

**Symptom: High memory usage**
- Clear browser cache
- Reduce limit parameter
- Check for memory leaks in DevTools

---

## Testing Endpoints

### 1. Health Check
```powershell
curl http://localhost:5001/api/inhouse-kanban/health
```

### 2. Get Jobs (Last 6 months)
```powershell
curl "http://localhost:5001/api/inhouse-kanban/jobs?timeframe_months=-6&limit=20"
```

### 3. Get Stages Summary
```powershell
curl "http://localhost:5001/api/inhouse-kanban/stages?timeframe_months=-6"
```

### 4. Get Dashboard Metrics
```powershell
curl "http://localhost:5001/api/inhouse-kanban/metrics?timeframe_months=-6"
```

### 5. Get Single Job Details
```powershell
curl "http://localhost:5001/api/inhouse-kanban/jobs/12345"
```
*(Replace 12345 with actual TicketID)*

---

## Database Schema Reference

### Tables Used

**JobTickets:**
- `TicketID` - Primary key
- `OrderID` - Foreign key to Orders
- `StageID` - Current production stage
- `ShortJobDesc` - Job description
- `QTY` - Quantity
- `Cost` - Job cost
- `Paper`, `GSM`, `JobSize`, `Pages`, `Binding` - Specifications
- `Cello`, `Folding`, `Stitching` - Finishing options
- `TicketNotes` - Production notes
- `InternalInvoiceComplete` - 0 for active jobs

**Orders:**
- `OrderID` - Primary key
- `ClientName` - Customer name
- `OrderDate` - Order date
- `DateRequired` - Due date
- `TotalCost` - Order total

**JobStages:**
- `StageID` - Primary key
- `Desc` - Stage description

---

## Configuration

### Module Settings

Located in `UI/external/modules/inhouse-kanban/manifest.json`:

```json
{
  "settings": {
    "api_endpoint": "/api/inhouse-kanban",
    "backend_url": "http://localhost:5001",
    "default_timeframe": -6,
    "refresh_interval": 300
  }
}
```

**Adjustable Settings:**
- `default_timeframe` - Default months to show (-6 = last 6 months)
- `refresh_interval` - Auto-refresh seconds (300 = 5 minutes)

### Backend Configuration

Located in `AI_infrastructure/routes/inhouse_kanban_routes.py`:

```python
DB_CONFIG = {
    'server': '3.25.76.138\\INHPSQLSERVER',
    'database': 'In HousePrint',
    'driver': '{ODBC Driver 17 for SQL Server}',
    'trusted_connection': 'yes'
}
```

---

## Deployment Steps

### Development Environment

1. ✅ Files created
2. ✅ Validation passed
3. ⏳ Restart Flask server
4. ⏳ Test all endpoints
5. ⏳ Verify frontend loads

### Production Environment

1. Commit changes to repository
2. Pull changes on production server
3. Restart Flask service
4. Run validation script
5. Test health endpoint
6. Verify module loads
7. Monitor logs for errors

---

## Support

For issues or questions:

1. Check Flask logs in terminal
2. Check browser console (F12)
3. Review `README.md` for usage instructions
4. Test backend endpoints directly with curl
5. Verify database connectivity

---

## Success Criteria

The module is successfully integrated when:

✅ Validation script shows: `✅ inhouse-kanban: VALID`  
✅ Health endpoint returns: `{"status": "healthy", "database": "connected"}`  
✅ Module appears in sidebar with factory icon  
✅ Jobs load and display in Kanban columns  
✅ Filters work correctly  
✅ Job detail modals open and display data  
✅ No console errors in browser  
✅ Responsive design works on all devices  

---

**Ready to deploy!** Follow the Quick Start steps above to launch the module.
