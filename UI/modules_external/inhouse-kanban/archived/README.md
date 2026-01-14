# InHousePrint Production Workflow Module

**Version:** 1.0.0  
**Module ID:** `inhouse-kanban`  
**Author:** InHouse Print  
**Last Updated:** November 3, 2025  
**Status:** ✅ Production Ready

---

## Overview

The **InHousePrint Production Workflow** module provides a comprehensive Kanban-style dashboard for real-time production job tracking. It connects directly to the InHousePrint SQL Server database and displays active jobs across multiple production stages with AI-powered priority scoring.

### Key Features

- 🎯 **AI Priority Scoring** - Intelligent 0-999 score based on due date, value, and customer tier
- 👥 **Customer Tier Badges** - VIP, Premium, Regular, and New customer identification
- ⏱️ **WIP Status Tracking** - DELAYED, AT_RISK, and ON_TRACK indicators
- 📊 **Multi-Stage Workflow** - Visual Kanban board with all production stages
- 🔍 **Advanced Filtering** - Filter by timeframe, priority, and search
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🔄 **Auto-Refresh** - Automatic data refresh every 5 minutes
- 💼 **Detailed Job View** - Complete job specifications in modal dialogs

---

## Installation

### Prerequisites

- AI_agents platform running on port 5001
- SQL Server connection to InHousePrint database
- ODBC Driver 17 for SQL Server installed

### Setup Steps

1. **Module files already created in:**
   ```
   UI/external/modules/inhouse-kanban/
   ```

2. **Backend route created at:**
   ```
   AI_infrastructure/routes/inhouse_kanban_routes.py
   ```

3. **Register the backend blueprint** in `AI_infrastructure/flask_app.py`:
   ```python
   from routes.inhouse_kanban_routes import inhouse_kanban_bp
   app.register_blueprint(inhouse_kanban_bp)
   ```

4. **Add module to main manifest** in `UI/external/modules/manifest.json`:
   ```json
   {
     "id": "inhouse-kanban",
     "name": "Production Workflow",
     "icon": "fas fa-industry",
     "color": "#00509E",
     "manifestPath": "external/modules/inhouse-kanban/manifest.json",
     "scriptPath": "external/modules/inhouse-kanban/inhouse-kanban.js",
     "enabled": true
   }
   ```

5. **Restart Flask server:**
   ```powershell
   BISTART
   ```

6. **Access the module:**
   - Open http://localhost:5001
   - Click "Production Workflow" icon in sidebar

---

## Usage

### Dashboard Overview

The main Kanban board displays:

1. **Top Metrics Row:**
   - Total Active Jobs
   - Pipeline Value
   - Overdue Jobs
   - Average Days in System

2. **Filters Bar:**
   - Timeframe selector (1-12 months)
   - Priority filter (All/Critical/High/Urgent/Normal/Low)
   - Search box (client name, job description, ticket #)
   - Last refresh time

3. **Kanban Columns:**
   - One column per production stage
   - Job count and total value per stage
   - Drag-and-drop capability (coming soon)

4. **Job Cards:**
   - Priority badge (color-coded)
   - Customer tier badge
   - Client name
   - Job description
   - Ticket ID, quantity, cost
   - Job specifications (paper, GSM, size, binding)
   - Due date (color-coded by urgency)
   - WIP status (days in system)
   - "View Details" button

### Viewing Job Details

Click the "View Details" button on any job card to see:

- **Client Information:** Client name, order ID, order date, business division
- **Job Specifications:** Full description, quantity, cost, paper, GSM, size, pages, binding
- **Finishing Options:** Cello, folding, stitching
- **Production Notes:** Internal notes and instructions
- **Status Information:** Current stage, due date, days in system, urgency level
- **Shipping:** Shipping instructions (if applicable)

### Filtering Jobs

**By Timeframe:**
- Select from 1-12 months lookback period
- Default: Last 6 months

**By Priority:**
- All Priorities (default)
- Critical Only (score 800-999)
- High Priority (score 600-799)
- Urgent (score 400-599)
- Normal (score 200-399)
- Low Priority (score 0-199)

**By Search:**
- Type client name, job description, or ticket number
- Search applies in real-time (500ms debounce)

### Understanding Priority Scores

The AI Priority Score (0-999) is calculated based on:

1. **Days Until Due Date** (most critical):
   - Overdue: +300 points
   - Due today/tomorrow: +250 points
   - Due within 3 days: +200 points
   - Due this week: +150 points
   - Future jobs: -5 points per week

2. **Job Value**:
   - $5,000+: +200 points
   - $2,000-$4,999: +150 points
   - $1,000-$1,999: +100 points
   - $500-$999: +50 points

3. **Customer Tier**:
   - VIP (20+ orders or $50K+ total): +100 points
   - Premium (10+ orders or $20K+ total): +75 points
   - Regular (5+ orders): +50 points

4. **Stage Urgency**:
   - Bindery, Guillotine, Dispatch: +50 points

### Customer Tiers

- **VIP** (Purple): 20+ orders OR $50,000+ lifetime value
- **Premium** (Blue): 10+ orders OR $20,000+ lifetime value
- **Regular** (Green): 5+ orders
- **New** (Gray): Less than 5 orders

### WIP Status

- **ON_TRACK** (Green): 0-6 days in system
- **AT_RISK** (Orange): 7-13 days in system
- **DELAYED** (Red): 14+ days in system

---

## Technical Details

### Database Connection

**SQL Server Details:**
- Server: `3.25.76.138\INHPSQLSERVER`
- Database: `In HousePrint`
- Authentication: Windows Authentication (Trusted Connection)

**Tables Used:**
- `JobTickets` - Active job tickets
- `Orders` - Order information
- `JobStages` - Stage descriptions
- `ClientList` - Customer metrics (calculated on-the-fly)

### API Endpoints

**Base URL:** `http://localhost:5001/api/inhouse-kanban`

**Endpoints:**
- `GET /jobs` - List active jobs (with filters)
- `GET /jobs/:id` - Get single job details
- `GET /stages` - Get stage summary
- `GET /metrics` - Get dashboard metrics
- `GET /health` - Health check

**Query Parameters:**
- `timeframe_months` - Lookback period (default: -6)
- `priority_filter` - Filter by priority level
- `stage_id` - Filter by specific stage
- `limit` - Max results (default: 100)

### Module Configuration

**manifest.json settings:**
```json
{
  "id": "inhouse-kanban",
  "colors": {
    "primary": "#00509E",
    "secondary": "#7FB3D5",
    "hover": "#003D7A"
  },
  "settings": {
    "api_endpoint": "/api/inhouse-kanban",
    "backend_url": "http://localhost:5001",
    "default_timeframe": -6,
    "refresh_interval": 300
  }
}
```

---

## Troubleshooting

### Module Not Appearing

1. Check Flask logs for blueprint registration errors
2. Verify database connection:
   ```powershell
   curl http://localhost:5001/api/inhouse-kanban/health
   ```
3. Check browser console for JavaScript errors
4. Run validation script:
   ```powershell
   python scripts/maintenance/validate_modules.py
   ```

### No Jobs Displayed

1. Check SQL Server connection (ODBC Driver installed?)
2. Verify InternalInvoiceComplete filter is correct
3. Check timeframe filter (try "Last 12 months")
4. View Network tab in browser DevTools for API errors

### Database Connection Errors

**Error:** `pyodbc.InterfaceError: ('IM002', ...)`
- **Fix:** Install ODBC Driver 17 for SQL Server

**Error:** `Login failed for user`
- **Fix:** Ensure Windows Authentication is configured
- **Fix:** Run Flask app with correct Windows user permissions

### Performance Issues

1. **Slow loading:**
   - Reduce timeframe filter (e.g., 1-3 months)
   - Check SQL Server performance
   - Verify network connectivity

2. **High memory usage:**
   - Clear browser cache
   - Reduce limit parameter in API calls

---

## Roadmap

### Version 1.1 (Planned)
- [ ] Drag-and-drop job stage updates
- [ ] Export to CSV/Excel
- [ ] Email notifications for overdue jobs
- [ ] Custom stage workflows

### Version 1.2 (Planned)
- [ ] Analytics dashboard (bottleneck detection)
- [ ] Stage efficiency metrics
- [ ] Customer performance trends
- [ ] Priority distribution charts

### Version 2.0 (Future)
- [ ] AI-powered scheduling recommendations
- [ ] Predictive completion dates
- [ ] Resource allocation optimization
- [ ] Integration with production equipment

---

## Support

### Documentation
- Complete technical guide: `IMPLEMENTATION_COMPLETE.md`
- Integration instructions: `INTEGRATION_GUIDE.md`
- Module best practices: `UI/module_development/MODULE_BEST_PRACTICES.md`

### Health Check
```bash
curl http://localhost:5001/api/inhouse-kanban/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "active_jobs": 45,
  "server": "3.25.76.138\\INHPSQLSERVER",
  "database_name": "In HousePrint"
}
```

---

## Changelog

### Version 1.0.0 - November 3, 2025
- ✨ Initial release
- ✅ AI priority scoring (0-999)
- ✅ Customer tier badges (VIP/Premium/Regular/New)
- ✅ WIP status indicators
- ✅ Multi-stage Kanban board
- ✅ Advanced filtering and search
- ✅ Responsive design
- ✅ Job detail modals
- ✅ Auto-refresh (5 minutes)
- ✅ Top metrics dashboard

---

**For additional support, refer to the AI_agents platform documentation or contact the development team.**
