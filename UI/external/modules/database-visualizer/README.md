# Database Visualizer Module

**Version:** 1.0.0  
**Module ID:** `database-visualizer`  
**Author:** InHouse Print  
**Last Updated:** November 3, 2025

---

## Overview

The Database Visualizer module provides a powerful interface for exploring SQLite databases within the AI Agents Platform. View schemas, browse tables, and analyze data with an intuitive tabbed interface.

### Key Features

- **📂 Database Browser** - View all available SQLite databases
- **🗂️ Schema Explorer** - Examine table structures, columns, and relationships
- **📊 Data Viewer** - Browse table data with Tabulator integration
- **🎨 Dark Theme** - Custom dark-themed UI for comfortable viewing

---

## File Structure

```
database-visualizer/
├── manifest.json                          # Module configuration
├── database-visualizer.js                 # Main module code (952 lines)
└── database-visualizer-dark-tags.css      # Dark theme styles
```

---

## Installation

### 1. Module is Pre-installed
This module is already included in the AI Agents Platform at:
```
C:\Users\gpoli\GIT\AI_agents\UI\external\modules\database-visualizer\
```

### 2. Enable Module (if disabled)
Edit `UI/external/modules/manifest.json`:
```json
{
  "modules": [
    {
      "id": "database-visualizer",
      "name": "Database Visualizer",
      "enabled": true  ← Set to true
    }
  ]
}
```

### 3. Reload Browser
Refresh the AI Agents Platform dashboard to load the module.

---

## Usage

### Tab 1: Databases
- View all available SQLite databases in the system
- Select a database to explore
- See database metadata (size, tables, etc.)

### Tab 2: Schema Explorer
- View all tables in selected database
- Examine column definitions
- See data types and constraints
- Understand table relationships

### Tab 3: Data Viewer
- Browse table data with pagination
- Sort and filter columns
- Export data (via Tabulator features)
- Full-featured table interface

---

## Technical Details

### Dependencies

**External Libraries:**
- **Tabulator 5.5.0** - Advanced table rendering
  - CSS: `https://unpkg.com/tabulator-tables@5.5.0/dist/css/tabulator.min.css`
  - JS: `https://unpkg.com/tabulator-tables@5.5.0/dist/js/tabulator.min.js`

**Platform Components:**
- `base-module.js` - BaseModule class
- `tabulator-enhancements.css` - Custom Tabulator styling
- `tabulator-functions.js` - Helper functions

### Module Structure

**Class:** `DatabaseVisualizerModule extends BaseModule`

**Key Methods:**
```javascript
initialize()           // Module setup and UI initialization
loadDatabases()        // Fetch available databases
loadSchema()           // Load table schemas
renderDataView()       // Display table data with Tabulator
applyModuleColors()    // Apply purple theme colors
```

**State Management:**
```javascript
this.databases         // List of available databases
this.selectedDb        // Currently selected database
this.selectedTable     // Currently selected table
this.schema            // Database schema cache
this.tabulatorTable    // Data viewer table instance
```

### Color Scheme

```javascript
{
  "primary": "#8b5cf6",      // Purple
  "secondary": "#c4b5fd",    // Light purple
  "hover": "#7c3aed"         // Dark purple
}
```

---

## API Integration

### Backend Endpoints

The module connects to Flask backend routes:

```
GET /api/database/list              - Get available databases
GET /api/database/schema?db=<name>  - Get database schema
GET /api/database/table?db=<name>&table=<name> - Get table data
```

**Note:** Ensure Flask backend is running on `http://localhost:5001`

---

## Design Decisions

### Dark Theme CSS
The module uses `database-visualizer-dark-tags.css` instead of the standard `database-visualizer.css` naming convention. This is **intentional** and reflects:

1. **Purpose:** Dark theme-optimized styling for database viewing
2. **Explicit Reference:** Listed in manifest.json dependencies array
3. **Visual Consistency:** Matches dark-themed data exploration UX

This naming is validated by the module validation script when CSS files are explicitly referenced in manifest.json.

---

## Development

### Modifying the Module

1. **Edit JavaScript:** `database-visualizer.js`
2. **Edit Styles:** `database-visualizer-dark-tags.css`
3. **Update Config:** `manifest.json` (if adding features/tabs)
4. **Test:** Reload browser and test all three tabs
5. **Validate:** Run `python scripts/maintenance/validate_modules.py`

### Adding New Tabs

Edit `manifest.json`:
```json
{
  "tabs": [
    ...existing tabs...,
    {
      "id": "new-feature",
      "label": "New Feature",
      "icon": "fas fa-star"
    }
  ]
}
```

Then implement in `database-visualizer.js`:
```javascript
renderNewFeatureTab() {
  // Tab content here
}
```

---

## Troubleshooting

### Module Not Loading
- Check `UI/external/modules/manifest.json` - ensure `"enabled": true`
- Verify folder name is `database-visualizer` (matches module ID)
- Check browser console for JavaScript errors

### Databases Not Showing
- Ensure Flask backend is running (`BISTART`)
- Verify `/api/database/list` endpoint is accessible
- Check database file paths in backend configuration

### Tabulator Not Working
- Ensure external CDN dependencies are loaded
- Check network tab for 404 errors on Tabulator CDN
- Verify internet connection for CDN access

### Styling Issues
- Clear browser cache (Ctrl + F5)
- Check `database-visualizer-dark-tags.css` is loaded
- Verify CSS is listed in manifest.json dependencies

---

## Future Enhancements

Potential features for future versions:

- [ ] **Query Builder** - Visual SQL query construction
- [ ] **Export Options** - CSV, JSON, Excel export
- [ ] **Schema Visualization** - ER diagram generation
- [ ] **Data Editing** - Inline table editing
- [ ] **Search** - Full-text search across tables
- [ ] **Bookmarks** - Save favorite queries/views
- [ ] **History** - Track recent database views

---

## Related Documentation

- **Module Development Guide:** `UI/module_development/Instructions.md`
- **Module Best Practices:** `UI/module_development/MODULE_BEST_PRACTICES.md`
- **Validation Script:** `scripts/maintenance/validate_modules.py`
- **Architecture Overview:** `ARCHITECTURE.md`

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review module validation output
3. Check Flask backend logs
4. Verify all dependencies are loaded

---

## Changelog

### Version 1.0.0 (Current)
- Initial release
- Three-tab interface (Databases, Schema, Data)
- Tabulator integration for data viewing
- Dark theme styling
- SQLite database support

---

**Module Status:** ✅ Production Ready
