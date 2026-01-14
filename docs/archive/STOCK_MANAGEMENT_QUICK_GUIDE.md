# Stock Management - Quick Reference Guide

## 🚀 How to Use

### Start the Backend
```powershell
cd C:\Users\gpoli\GIT\In_House_SQL\G_Folder\AI_infrastructure
python flask_app.py
```

### Access the Module
1. Open browser: `http://localhost:5001`
2. Click "Stock Management" module
3. Navigate through sub-tabs

---

## 📑 Sub-Tab Guide

### 1. Invoice Processing
**What it does:** Upload invoices (PDF/images) for AI extraction

**How to use:**
1. Drag & drop invoice file OR click to browse
2. AI extracts supplier, items, amounts
3. Review extraction results
4. Click "Clear" to process another

**Backend:** POST `/api/stock/invoice-process`

---

### 2. Usage Analytics
**What it does:** Shows stock consumption trends over time

**How to use:**
1. Select time period (30/90/180/365 days)
2. View summary stats (Total Stocks, Sheets, Fast/Slow Movers)
3. Analyze consumption chart (by product type)
4. Click "Refresh" to reload data

**Backend:** GET `/api/stock/usage-analytics?days=90&group_by=month`

**Chart:** Line chart showing usage trends by product category

---

### 3. Reorder Dashboard
**What it does:** Lists all stocks with reorder alerts

**How to use:**
1. View summary (Critical, Low, Adequate, Total)
2. Browse stock table with status indicators
3. Use checkboxes for bulk selection
4. Tag rows (Green=Ordered, Orange=Review, Red=Urgent)
5. Click "Refresh" to reload data

**Backend:** GET `/api/stock/list-unified?is_active=true&limit=100`

**Status Logic:**
- 🔴 CRITICAL: stock = 0 OR stock < (reorder_point * 0.5)
- 🟡 LOW: stock < reorder_point
- 🟢 OK: stock >= reorder_point

---

### 4. Profit Analysis
**What it does:** Shows profitability by stock type

**How to use:**
1. Select time period (30/90/180/365 days)
2. View summary (Revenue, Cost, Margin, Jobs)
3. Browse profit table sorted by margin
4. Identify high/low margin stocks
5. Click "Refresh" to reload data

**Backend:** GET `/api/stock/profit-analysis?days=90`

**Calculations:**
```
Profit = Revenue - Cost
Margin % = (Profit / Revenue) * 100

Color Coding:
  Green: Margin > 30%
  Yellow: Margin 15-30%
  Red: Margin < 15%
```

---

### 5. SQL Viewer
**What it does:** Direct database queries (coming soon)

**Status:** Placeholder - Future implementation

---

### 6. AI Analytics
**What it does:** AI extraction quality metrics

**How to use:**
1. View extraction statistics
2. Success rate percentage
3. Average confidence scores
4. Click "Refresh" to reload

**Backend:** GET `/api/stock/ai-extraction-stats`

---

## 🔄 Refresh System

### Global Refresh
- Click main "Refresh" button in module header
- Refreshes currently active sub-tab only

### Per-Tab Refresh
- Each tab has its own refresh button
- Only reloads data for that specific tab
- Faster than global refresh

---

## 🎨 Features

### Tagging System
- Select rows with checkboxes
- Apply color tags: Green/Orange/Red
- Tags persist across sessions
- Use for workflow management

### Sorting & Filtering
- Click column headers to sort
- Search box filters all columns
- Multi-column sorting (hold Shift)

### Export Options
- Copy to clipboard
- Export to CSV
- Print view

---

## 🧪 Testing

### Test Backend APIs
```powershell
cd C:\Users\gpoli\GIT\AI_agents
python test_stock_management_apis.py
```

Expected output:
```
✅ PASS - health
✅ PASS - usage_analytics
✅ PASS - list_unified
✅ PASS - profit_analysis
✅ PASS - ai_extraction_stats

📊 Results: 5/5 tests passed (100%)
🎉 All tests passed! Stock Management module is ready.
```

---

## 🐛 Troubleshooting

### "Loading..." Never Finishes
**Problem:** Backend not running  
**Solution:** Start Flask backend (see above)

### "Failed to load data"
**Problem:** Database not accessible  
**Solution:** Check `stock_data.db` exists in `G_Folder/`

### "HTTP 404" Error
**Problem:** Endpoint not found  
**Solution:** Verify Flask routes are registered

### Empty Tables
**Problem:** No data in database  
**Solution:** Run data extraction/import scripts first

### Chart Not Rendering
**Problem:** Chart.js not loaded  
**Solution:** Check browser console for errors

---

## 📊 Database Schema

### Tables Used
- `unified_stocks` - Master stock inventory
- `extracted_jobs` - Job history with stock usage
- `extraction_logs` - AI extraction audit trail (optional)

### Key Fields

**unified_stocks:**
- `stock_id` - Primary key
- `stock_type_name` - Stock name
- `current_stock` - Current quantity
- `reorder_level` - Reorder threshold
- `supplier_name` - Supplier info
- `cost_per_thousand` - Cost data

**extracted_jobs:**
- `ticket_id` - Job ticket ID
- `stock_id` - Links to unified_stocks
- `order_date` - Job date
- `quantity` - Stock used
- `total_revenue` - Revenue data
- `total_cost` - Cost data

---

## 🔐 Permissions

### Required Access
- Read: `unified_stocks`, `extracted_jobs`
- Write: None (read-only queries)

### API Authentication
- Backend: No auth required (localhost)
- Production: Implement JWT/OAuth

---

## 📈 Performance

### Loading Times
- Usage Analytics: ~1-2 seconds (90 days)
- Reorder Dashboard: ~0.5 seconds (100 stocks)
- Profit Analysis: ~1-2 seconds (90 days)

### Optimization Tips
1. Limit date ranges for faster queries
2. Use pagination for large datasets
3. Cache frequently accessed data
4. Index database columns (stock_id, order_date)

---

## 🎯 Key Metrics

### Usage Analytics
- **Tracks:** Stock consumption patterns
- **Time Range:** 30-365 days
- **Grouping:** Day/Week/Month
- **Output:** Chart + Statistics

### Reorder Dashboard
- **Tracks:** Stock levels vs reorder points
- **Filtering:** Active stocks only
- **Limit:** 100 stocks (configurable)
- **Output:** Status table

### Profit Analysis
- **Tracks:** Revenue, cost, margins
- **Time Range:** 30-365 days
- **Calculations:** Profit = Revenue - Cost
- **Output:** Profitability table

---

## 🔧 Configuration

### Backend URL
```javascript
this.backendUrl = 'http://localhost:5001';
```

### API Endpoint Base
```javascript
this.apiEndpoint = '/api/stock';
```

### Time Period Defaults
```javascript
this.currentPeriod = 90; // days
```

---

## 📞 Support

**Documentation:**
- Main Guide: `STOCK_MANAGEMENT_SQL_FIX_COMPLETE.md`
- Backend Routes: `stock_routes.py`, `stock_analytics_routes.py`

**Issues:**
- GitHub: `gerardovsa/AI_agents`
- Branch: `V2_clean`

---

## ✅ Checklist

Before using Stock Management module:

- [ ] Backend Flask server is running (port 5001)
- [ ] Database `stock_data.db` exists and has data
- [ ] Browser console shows no JavaScript errors
- [ ] Test script passes all API tests
- [ ] Chart.js library is loaded
- [ ] Module registered in `ModuleRegistry`

---

**Last Updated:** November 3, 2025  
**Version:** 2.0 (SQL Integration Complete)  
**Status:** Production Ready ✅
